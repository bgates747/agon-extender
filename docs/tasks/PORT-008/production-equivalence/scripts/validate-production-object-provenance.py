#!/usr/bin/env python3
"""Validate and compare genuine PORT-008 target-object provenance.

Unlike the retained schema-v1 similarity checker, this gate consumes records
emitted around the target processes that actually ran.  A tracked policy owns
the complete unit, role, tool, and symbol sets.  Evidence cannot select a
smaller claim.  The gate executes only Git and policy-pinned inspection tools;
it never executes a command selected by an evidence record.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence

import yaml


POLICY_KIND = "port-008-production-object-policy"
BUILD_KIND = "port-008-production-object-build"
BUILD_SCHEMA = 1
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
ROOT_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
ROOTED_PATH_RE = re.compile(r"^\$\{([A-Z][A-Z0-9_]*)\}(?:/(.*))?$")
RESERVED_ROOT_PLACEHOLDER = re.compile(r"\$\{[A-Z][A-Z0-9_]*\}")
BUILD_ID_RE = re.compile(
    r"^(?P<identity>[a-z][a-z0-9]*(?:-[a-z0-9]+)*-v\d+\.\d+\.\d+)"
    r"-b(?P<timestamp>\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2})Z$"
)
ARCHITECTURE_RE = re.compile(r"^architecture:\s*([^,\r\n]+)", re.MULTILINE)
DISASSEMBLY_HEADER = re.compile(r"^\s*([0-9a-fA-F]+)\s+<([^>]+)>:\s*$")
DISASSEMBLY_LINE = re.compile(r"^\s*([0-9a-fA-F]+):\s*(\S.*?)\s*$")
RELOCATION_TARGET = re.compile(r"^([^+\s]+)(?:\+0x([0-9a-fA-F]+))?$")
SECTION_TABLE_ROW = re.compile(
    r"^\s*\d+\s+(\S+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+"
    r"[0-9a-fA-F]+\s+[0-9a-fA-F]+\s+\S+\s*$"
)
SECTION_CONTENT_ROW = re.compile(
    # Pinned GNU objdump renders sixteen bytes in a fixed 36-column field.
    # Using that field boundary avoids mistaking an all-hex ASCII column for
    # evidence bytes and also handles unaligned ranges split into five groups.
    r"^\s*([0-9a-fA-F]+)\s+(.{36})\s.*$"
)
RELOCATION_SECTION_HEADER = re.compile(r"^RELOCATION RECORDS FOR \[(\S+)\]:$")
RELOCATION_TABLE_ROW = re.compile(
    r"^\s*([0-9a-fA-F]+)\s+(r_[A-Za-z0-9_]+)\s+(\S.*?)\s*$"
)
MAP_CONTRIBUTION = re.compile(
    r"^\s*(?:(\.[^\s]+)\s+)?(0x[0-9A-Fa-f]+)\s+"
    r"(0x[0-9A-Fa-f]+)\s+(.+?)\s*$"
)
MAP_SYMBOL = re.compile(r"^\s*0x[0-9A-Fa-f]+\s+(.+?)\s*$")
FORBIDDEN_ENVIRONMENT = re.compile(
    r"(?:TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIAL|PRIVATE|COOKIE|AUTH|KEY)$",
    re.IGNORECASE,
)
NONALLOCATED_SECTION_PREFIXES = (
    ".comment",
    ".debug",
    ".note",
    ".riscv.attributes",
    ".gnu.attributes",
    ".eh_frame",
)
SHELL_CONTROL_TOKENS = {";", "&&", "||", "|", "&", ">", ">>", "<", "<<"}
P4_UNQUOTED_SHELL_META = frozenset(" \t\n\r\v\f\\'\"`$&;|<>()*?[#~")
P4_DOUBLE_QUOTE_ESCAPABLE = frozenset('\\\\"$`')
P4_CANONICAL_MAP_PREFIX = "-Wl,-Map="
P4_MAP_OPTION_PREFIXES = ("-Wl,-Map", "-Wl,--Map", "-Map", "--Map")
P4_COMPILE_VALUE_OPTIONS = frozenset(
    {
        "-D",
        "-I",
        "-MF",
        "-MQ",
        "-MT",
        "-U",
        "-idirafter",
        "-imacros",
        "-include",
        "-iprefix",
        "-iquote",
        "-isystem",
        "-iwithprefix",
        "-iwithprefixbefore",
        "-o",
    }
)
P4_UNPROVED_NESTED_TOOL_OPTIONS = (
    "-B",
    "-flto",
    "-fplugin",
    "-fuse-ld",
    "-specs",
    "--specs",
    "-wrapper",
)


class GateError(ValueError):
    """Evidence failed a structural or integrity condition."""


@dataclass(frozen=True)
class RootBinding:
    name: str
    lexical: Path
    resolved: Path
    allow_symlink: bool


@dataclass(frozen=True)
class StepView:
    record_path: Path
    record_sha256: str
    document: dict[str, Any]
    source_path: Path
    output_path: Path
    command: tuple[str, ...]
    dependencies: tuple[dict[str, Any], ...]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_generator_text_input(path: Path, label: str) -> str:
    """Reproduce zds2gas's UTF-8/universal-newline input digest exactly.

    Prepared-source metadata separately authenticates the file's raw bytes.
    The generator manifest describes the decoded text consumed by Path.read_text,
    which normalizes CRLF and CR line endings before zds2gas re-encodes the text
    for its semantic-input digest.
    """

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise GateError(
            f"cannot decode {label} as generator UTF-8 input: {error}"
        ) from error
    return sha256_bytes(text.encode("utf-8"))


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "utf-8"
    )


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise GateError(f"{label} must be an object")
    return value


def require_exact_keys(
    value: Mapping[str, Any], expected: Iterable[str], label: str
) -> None:
    expected_set = set(expected)
    actual = set(value)
    missing = sorted(expected_set - actual)
    unknown = sorted(actual - expected_set)
    if missing or unknown:
        raise GateError(f"{label} fields differ: missing={missing}, unknown={unknown}")


def require_sha256(value: Any, label: str) -> str:
    if not isinstance(value, str) or SHA256_RE.fullmatch(value) is None:
        raise GateError(f"{label} is not a lowercase SHA-256 digest")
    return value


def require_exact_integer(
    value: Any, label: str, *, minimum: int | None = None
) -> int:
    """Accept JSON integers without treating booleans as numeric evidence."""

    if type(value) is not int or (minimum is not None and value < minimum):
        boundary = f" at least {minimum}" if minimum is not None else ""
        raise GateError(f"{label} must be an integer{boundary}")
    return value


def build_id_matches_source(value: Any, source_identity: Any) -> bool:
    """Require the exact source prefix and a real UTC calendar timestamp."""

    match = BUILD_ID_RE.fullmatch(value) if isinstance(value, str) else None
    if match is None or match.group("identity") != source_identity:
        return False
    try:
        datetime.strptime(match.group("timestamp"), "%Y-%m-%d-%H-%M-%S")
    except ValueError:
        return False
    return True


def identity_registry_artifacts(value: Any) -> dict[str, dict[str, Any]]:
    """Index only after the registry's artifact-ID set is unambiguous."""

    registry = require_object(value, "identity registry")
    records = registry.get("artifacts")
    if not isinstance(records, list):
        raise GateError("identity registry artifacts must be an array")
    artifacts: dict[str, dict[str, Any]] = {}
    for index, record_value in enumerate(records):
        record = require_object(
            record_value, f"identity registry artifact {index}"
        )
        artifact_id = record.get("artifact_id")
        if not isinstance(artifact_id, str) or not artifact_id:
            raise GateError(
                f"identity registry artifact {index} lacks a nonempty artifact_id"
            )
        if artifact_id in artifacts:
            raise GateError(
                f"identity registry contains duplicate artifact_id {artifact_id!r}"
            )
        artifacts[artifact_id] = record
    return artifacts


def safe_relative(value: Any, label: str) -> PurePosixPath:
    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise GateError(f"{label} must be a nonempty POSIX relative path")
    relative = PurePosixPath(value)
    if (
        relative.is_absolute()
        or not relative.parts
        or value != relative.as_posix()
        or any(part in ("", ".", "..") for part in relative.parts)
    ):
        raise GateError(f"{label} is not a normalized relative path: {value!r}")
    return relative


def safe_slash_prefixed_relative(value: Any, label: str) -> PurePosixPath:
    """Validate a policy suffix spelled as one slash plus a relative path."""

    if not isinstance(value, str) or not value.startswith("/"):
        raise GateError(f"{label} must start with exactly one slash")
    relative = safe_relative(value[1:], label)
    if value != "/" + relative.as_posix():
        raise GateError(f"{label} is not a canonical slash-prefixed path")
    return relative


def load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise GateError(f"cannot read {label} {path}: {error}") from error


def no_symlink_components(path: Path, root: Path, label: str) -> None:
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise GateError(f"{label} is outside its root: {path}") from error
    cursor = root
    for part in relative.parts:
        cursor /= part
        try:
            metadata = cursor.lstat()
        except FileNotFoundError as error:
            raise GateError(f"{label} does not exist: {cursor}") from error
        if stat.S_ISLNK(metadata.st_mode):
            raise GateError(f"{label} traverses a symbolic link: {cursor}")


def no_absolute_symlink_components(
    path: Path, label: str, *, allow_leaf_symlink: bool = False
) -> None:
    """Reject symlinks from the filesystem anchor through an absolute path."""

    lexical = Path(os.path.abspath(os.fspath(path)))
    if not lexical.is_absolute():
        raise GateError(f"{label} is not absolute")
    cursor = Path(lexical.anchor)
    for part in lexical.parts[1:]:
        cursor /= part
        try:
            metadata = cursor.lstat()
        except FileNotFoundError as error:
            raise GateError(f"{label} does not exist: {cursor}") from error
        if stat.S_ISLNK(metadata.st_mode) and not (
            allow_leaf_symlink and cursor == lexical
        ):
            raise GateError(f"{label} traverses a symbolic link: {cursor}")


def regular_file(path: Path, label: str, *, root: Path | None = None) -> Path:
    lexical = Path(os.path.abspath(os.fspath(path)))
    if root is not None:
        no_symlink_components(lexical, root, label)
    try:
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError(f"{label} is unavailable: {lexical}: {error}") from error
    if not resolved.is_file():
        raise GateError(f"{label} is not a regular file: {lexical}")
    return resolved


def evidence_file(root: Path, value: str, label: str) -> Path:
    relative = safe_relative(value, label)
    lexical = root.joinpath(*relative.parts)
    return regular_file(lexical, label, root=root)


def parse_root_arguments(
    values: Sequence[str], target_policy: dict[str, Any]
) -> dict[str, RootBinding]:
    required = target_policy["required_roots"]
    if not isinstance(required, list) or not all(
        isinstance(item, str) and ROOT_RE.fullmatch(item) for item in required
    ):
        raise GateError("policy required_roots is malformed")
    root_policy = require_object(target_policy["root_policy"], "policy root_policy")
    if set(root_policy) != set(required):
        raise GateError("policy root_policy does not exactly cover required_roots")
    raw: dict[str, Path] = {}
    for item in values:
        if "=" not in item:
            raise GateError(f"root must use NAME=PATH: {item!r}")
        name, path_text = item.split("=", 1)
        if ROOT_RE.fullmatch(name) is None or name in raw or not path_text:
            raise GateError(f"invalid or duplicate root binding: {item!r}")
        if not Path(path_text).is_absolute():
            raise GateError(f"root binding path must be absolute: {item!r}")
        raw[name] = Path(os.path.abspath(path_text))
    if set(raw) != set(required):
        raise GateError(
            "root bindings differ from policy: "
            f"missing={sorted(set(required) - set(raw))}, "
            f"unknown={sorted(set(raw) - set(required))}"
        )
    bindings: dict[str, RootBinding] = {}
    seen_lexical: set[Path] = set()
    seen_resolved: set[Path] = set()
    for name in required:
        rule = require_object(root_policy[name], f"root policy {name}")
        require_exact_keys(rule, ("allow_symlink",), f"root policy {name}")
        allow_symlink = rule["allow_symlink"]
        if not isinstance(allow_symlink, bool):
            raise GateError(f"root policy {name}.allow_symlink must be boolean")
        lexical = raw[name]
        no_absolute_symlink_components(
            lexical,
            f"root {name}",
            allow_leaf_symlink=allow_symlink,
        )
        try:
            resolved = lexical.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise GateError(f"root {name} is unavailable: {lexical}: {error}") from error
        if not resolved.is_dir():
            raise GateError(f"root {name} is not a directory: {lexical}")
        if lexical in seen_lexical or resolved in seen_resolved:
            raise GateError(f"root {name} aliases another declared root")
        seen_lexical.add(lexical)
        seen_resolved.add(resolved)
        bindings[name] = RootBinding(name, lexical, resolved, allow_symlink)
    return bindings


def require_stable_root(root: RootBinding, label: str) -> None:
    """Reject a declared root whose lexical leaf was retargeted after binding."""

    try:
        current = root.lexical.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError(f"{label} declared root is unavailable: {error}") from error
    if current != root.resolved:
        raise GateError(f"{label} declared root changed after binding")


def resolve_rooted_existing_path(
    value: str, roots: Mapping[str, RootBinding], label: str
) -> Path:
    if not isinstance(value, str):
        raise GateError(f"{label} path must be a string")
    match = ROOTED_PATH_RE.fullmatch(value)
    if match is None or match.group(1) not in roots:
        raise GateError(f"{label} does not use a declared root: {value!r}")
    root = roots[match.group(1)]
    require_stable_root(root, label)
    suffix = match.group(2)
    parts: tuple[str, ...] = ()
    if suffix is not None:
        relative = safe_relative(suffix, f"{label} rooted-path suffix")
        parts = relative.parts
    lexical = root.lexical.joinpath(*parts)
    # parse_root_arguments() applies allow_symlink only to the declared root's
    # own leaf.  It never authorizes a descendant symlink or an escape through
    # one, so inspect every component below the root for both root classes.
    no_symlink_components(lexical, root.lexical, label)
    try:
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError(f"{label} is unavailable: {lexical}: {error}") from error
    if resolved != root.resolved and not resolved.is_relative_to(root.resolved):
        raise GateError(f"{label} escapes its declared root: {value!r}")
    return resolved


def resolve_rooted_path(
    value: str, roots: Mapping[str, RootBinding], label: str
) -> Path:
    path = resolve_rooted_existing_path(value, roots, label)
    if not path.is_file():
        raise GateError(f"{label} is not a regular file: {path}")
    return path


def verify_file_record(
    value: Any, roots: Mapping[str, RootBinding], label: str
) -> Path:
    record = require_object(value, label)
    require_exact_keys(record, ("path", "sha256", "size"), label)
    path = resolve_rooted_path(record["path"], roots, label)
    expected = require_sha256(record["sha256"], f"{label}.sha256")
    if sha256_file(path) != expected:
        raise GateError(f"{label} SHA-256 mismatch")
    if type(record["size"]) is not int or record["size"] < 0:
        raise GateError(f"{label}.size must be a nonnegative integer")
    if path.stat().st_size != record["size"]:
        raise GateError(f"{label} size mismatch")
    return path


def canonical_file_paths_match(left: Path, right: Path, label: str) -> bool:
    """Match one resolved pathname, rejecting a distinct hardlink spelling."""

    if left == right:
        return True
    try:
        hardlink_alias = left.samefile(right)
    except OSError as error:
        raise GateError(f"cannot compare {label} file identities: {error}") from error
    if hardlink_alias:
        raise GateError(f"{label} uses a distinct hardlink alias")
    return False


def register_unique_file_path(path: Path, seen: set[Path], label: str) -> None:
    """Reject repeated resolved paths and distinct hardlink aliases in one set."""

    for previous in seen:
        if canonical_file_paths_match(path, previous, label):
            raise GateError(f"{label} contains a duplicate resolved file")
    seen.add(path)


def require_predeclared_file_record(
    record: Mapping[str, Any],
    path: Path,
    declared_by_path: Mapping[Path, Mapping[str, Any]],
    label: str,
) -> None:
    """Bind a record to one canonical declaration, rejecting hardlink aliases."""

    declared = declared_by_path.get(path)
    if declared is None:
        for declared_path in declared_by_path:
            canonical_file_paths_match(path, declared_path, label)
        raise GateError(f"{label} was not predeclared")
    if any(record[field] != declared[field] for field in ("sha256", "size")):
        raise GateError(f"{label} differs from its predeclared file")


def file_records_same_identity(
    left: Any,
    right: Any,
    roots: Mapping[str, RootBinding],
    label: str,
) -> bool:
    """Compare authenticated file identity independently of rooted spelling."""

    left_record = require_object(left, f"{label} left record")
    right_record = require_object(right, f"{label} right record")
    left_path = verify_file_record(left_record, roots, f"{label} left record")
    right_path = verify_file_record(right_record, roots, f"{label} right record")
    return (
        canonical_file_paths_match(left_path, right_path, label)
        and left_record["sha256"] == right_record["sha256"]
        and left_record["size"] == right_record["size"]
    )


def verify_evidence_reference(value: Any, root: Path, label: str) -> Path:
    record = require_object(value, label)
    require_exact_keys(record, ("path", "sha256"), label)
    path = evidence_file(root, record["path"], label)
    if sha256_file(path) != require_sha256(record["sha256"], f"{label}.sha256"):
        raise GateError(f"{label} SHA-256 mismatch")
    return path


def run_checked(
    argv: Sequence[str],
    *,
    cwd: Path | None = None,
    timeout: int = 30,
    environment: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[bytes]:
    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=(
                dict(environment)
                if environment is not None
                else {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "LC_ALL": "C"}
            ),
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise GateError(f"command failed to execute: {argv[0]}: {error}") from error
    if completed.returncode != 0:
        detail = os.fsdecode(completed.stderr).strip()
        raise GateError(
            f"command exited {completed.returncode}: {' '.join(argv)}: {detail}"
        )
    return completed


def git_output(root: Path, arguments: Sequence[str]) -> bytes:
    return run_checked(("git", "-C", os.fspath(root), *arguments)).stdout


def verify_repository(
    item: dict[str, Any], expected: dict[str, Any], roots: Mapping[str, RootBinding]
) -> dict[str, Any]:
    require_exact_keys(item, ("id", "root", "commit", "dirty"), "repository record")
    if item["id"] != expected["id"] or item["root"] != expected["root"]:
        raise GateError(f"repository record does not match policy: {item.get('id')!r}")
    commit = item["commit"]
    if not isinstance(commit, str) or COMMIT_RE.fullmatch(commit) is None:
        raise GateError(f"repository {item['id']} lacks an exact commit")
    if item["dirty"] is not False:
        raise GateError(f"repository {item['id']} does not attest dirty: false")
    root = roots[item["root"]].resolved
    reported = Path(os.fsdecode(git_output(root, ("rev-parse", "--show-toplevel"))).strip()).resolve()
    if reported != root:
        raise GateError(f"repository {item['id']} root mismatch: {reported} != {root}")
    observed = os.fsdecode(git_output(root, ("rev-parse", "--verify", "HEAD^{commit}"))).strip()
    if observed != commit:
        raise GateError(f"repository {item['id']} HEAD mismatch: {observed} != {commit}")
    status = git_output(
        root,
        (
            "status",
            "--porcelain=v1",
            "--untracked-files=all",
            "--ignore-submodules=none",
            "--",
        ),
    )
    if status:
        raise GateError(f"repository {item['id']} is dirty")
    return {"id": item["id"], "root": item["root"], "commit": commit, "dirty": False}


def verify_tracked_file(repository: Path, path: Path, label: str) -> str:
    try:
        relative = path.relative_to(repository).as_posix()
    except ValueError as error:
        raise GateError(f"{label} is outside its authority repository") from error
    git_output(repository, ("ls-files", "--error-unmatch", "--", relative))
    committed = git_output(repository, ("show", f"HEAD:{relative}"))
    current = path.read_bytes()
    if committed != current:
        raise GateError(f"{label} differs from its committed Git blob")
    return relative


def validate_policy(document: Any) -> dict[str, Any]:
    policy = require_object(document, "policy")
    require_exact_keys(
        policy,
        (
            "schema_version",
            "evidence_kind",
            "identity_registry",
            "targets",
            "known_open_boundaries",
        ),
        "policy",
    )
    if (
        require_exact_integer(policy["schema_version"], "policy schema_version") != 1
        or policy["evidence_kind"] != POLICY_KIND
    ):
        raise GateError("unsupported production-object policy")
    registry_policy = require_object(policy["identity_registry"], "identity registry policy")
    require_exact_keys(
        registry_policy,
        ("root", "path", "eligible_statuses"),
        "identity registry policy",
    )
    if (
        registry_policy["root"] != "AUTHORITY"
        or safe_relative(registry_policy["path"], "identity registry path").as_posix()
        != registry_policy["path"]
        or registry_policy["eligible_statuses"] != ["candidate", "qualified", "released"]
    ):
        raise GateError("identity registry policy is not the exact eligible authority")
    boundaries = policy["known_open_boundaries"]
    if not isinstance(boundaries, list):
        raise GateError("known_open_boundaries must be an array")
    boundary_ids: list[str] = []
    for boundary in boundaries:
        boundary = require_object(boundary, "known provenance boundary")
        require_exact_keys(boundary, ("id", "status", "summary"), "known provenance boundary")
        if not all(isinstance(boundary[field], str) and boundary[field] for field in boundary):
            raise GateError("known provenance boundary is malformed")
        boundary_ids.append(boundary["id"])
    if boundary_ids != [
        "PORT008-PROV-P023",
        "PORT008-PROV-P024",
        "PORT008-PROV-P025",
        "PORT008-PROV-P026",
        "PORT008-PROV-P027",
        "PORT008-PROV-P028",
        "PORT008-PROV-P029",
        "PORT008-PROV-P030",
        "PORT008-PROV-P031",
    ]:
        raise GateError("known provenance boundary set/order differs from policy")
    targets = require_object(policy["targets"], "policy targets")
    if set(targets) != {"emos", "p4"}:
        raise GateError("policy must own exactly the emos and p4 targets")
    for target_name, target in targets.items():
        target = require_object(target, f"policy target {target_name}")
        common_target_fields = {
            "artifact_id",
            "artifact_kind",
            "variant",
            "capture_format",
            "capture_evidence_kind",
            "object_architecture",
            "final_image_suffix",
            "link_map_suffix",
            "required_roots",
            "root_policy",
            "repositories",
            "environment_policy",
            "tools",
            "release_consumer",
            "units",
            "roles",
            "command_normalization",
            "command_policy_status",
            "equality_compile_commands_must_match",
        }
        target_specific_fields = (
            {
                "prepared_source",
                "recorder",
                "build_relative",
                "final_linker_script",
            }
            if target_name == "emos"
            else {
                "target_machine",
                "assembler_selector_arguments",
                "project_relative",
                "venv_relative",
                "pio_packages_relative",
                "toolchain_package_relative",
                "capture_boundary_files",
                "external_project_compile_prefixes",
                "capture_runtime_policy",
            }
        )
        require_exact_keys(
            target,
            common_target_fields | target_specific_fields,
            f"policy target {target_name}",
        )
        for field in (
            "artifact_id",
            "artifact_kind",
            "variant",
            "capture_format",
            "capture_evidence_kind",
            "object_architecture",
            "final_image_suffix",
            "link_map_suffix",
            "required_roots",
            "root_policy",
            "repositories",
            "environment_policy",
            "tools",
            "release_consumer",
            "units",
            "roles",
            "command_normalization",
            "command_policy_status",
            "equality_compile_commands_must_match",
        ):
            if field not in target:
                raise GateError(f"policy target {target_name} lacks {field}")
        for field in ("final_image_suffix", "link_map_suffix"):
            safe_slash_prefixed_relative(
                target[field], f"policy target {target_name} {field}"
            )
        if target_name == "p4":
            safe_relative(target.get("project_relative"), "p4 project_relative")
            safe_relative(target.get("venv_relative"), "p4 venv_relative")
            safe_relative(
                target.get("pio_packages_relative"), "p4 pio_packages_relative"
            )
            safe_relative(
                target.get("toolchain_package_relative"),
                "p4 toolchain_package_relative",
            )
            for field in (
                "target_machine",
                "assembler_selector_arguments",
                "capture_boundary_files",
                "external_project_compile_prefixes",
                "capture_runtime_policy",
            ):
                if field not in target:
                    raise GateError(f"policy target p4 lacks {field}")
            if not {
                "PROJECT",
                "VENV_RUNTIME",
                "PIO_PACKAGES",
                "PYTHON_RUNTIME",
            } <= set(target["required_roots"]):
                raise GateError("P4 policy lacks separate project/runtime authority roots")
            external_prefixes = target["external_project_compile_prefixes"]
            if not isinstance(external_prefixes, list) or not external_prefixes:
                raise GateError("P4 policy has no explicit external compile prefixes")
            normalized_prefixes = [
                safe_relative(value, "P4 external compile prefix").as_posix()
                for value in external_prefixes
            ]
            if normalized_prefixes != external_prefixes or len(normalized_prefixes) != len(
                set(normalized_prefixes)
            ):
                raise GateError("P4 external compile prefixes are not canonical/unique")
            selector_arguments = target["assembler_selector_arguments"]
            if (
                not isinstance(selector_arguments, list)
                or not selector_arguments
                or len(selector_arguments) != len(set(selector_arguments))
                or any(
                    not isinstance(value, str)
                    or not value.startswith(("-march=", "-mespv-spec="))
                    for value in selector_arguments
                )
            ):
                raise GateError("P4 assembler selector policy is malformed")
        else:
            safe_relative(target["build_relative"], "EMOS build_relative")
            safe_relative(target["final_linker_script"], "EMOS final_linker_script")
        if not isinstance(target["artifact_id"], str) or not target["artifact_id"]:
            raise GateError(f"policy target {target_name} has invalid artifact_id")
        if target["artifact_kind"] != "firmware":
            raise GateError(f"policy target {target_name} must identify firmware")
        if not isinstance(target["variant"], str) or not target["variant"]:
            raise GateError(f"policy target {target_name} has invalid variant")
        if target["command_normalization"] != "root-paths-and-build-identity-defines-v1":
            raise GateError(f"policy target {target_name} has an unsupported command normalization")
        if target["command_policy_status"] not in {
            "awaiting-clean-rehearsal",
            "frozen",
        }:
            raise GateError(f"policy target {target_name} has an invalid command-policy status")
        require_object(target["environment_policy"], f"{target_name} environment policy")
        release_consumer = require_object(
            target["release_consumer"], f"{target_name} release consumer"
        )
        require_exact_keys(
            release_consumer, ("status", "note"), f"{target_name} release consumer"
        )
        if release_consumer["status"] not in {
            "ordinary-composition-present",
            "absent",
        }:
            raise GateError(f"{target_name} release consumer status is unsupported")
        units = target.get("units")
        roles = target.get("roles")
        if not isinstance(units, list) or not units:
            raise GateError(f"policy target {target_name} has no units")
        if not isinstance(roles, dict) or set(roles) != {"qualification", "release"}:
            raise GateError(f"policy target {target_name} has incomplete roles")
        by_id: dict[str, dict[str, Any]] = {}
        symbol_owners: dict[str, str] = {}
        for unit in units:
            unit = require_object(unit, f"{target_name} unit")
            unit_id = unit.get("id")
            if not isinstance(unit_id, str) or unit_id in by_id:
                raise GateError(f"{target_name} unit has duplicate/invalid id {unit_id!r}")
            if unit.get("classification") not in {
                "equality",
                "composition-dependent",
                "qualification-only",
                "release-only",
            }:
                raise GateError(f"{target_name} unit {unit_id} has invalid classification")
            safe_relative(unit.get("source"), f"{target_name} unit {unit_id} source")
            if unit.get("source_root") not in target["required_roots"]:
                raise GateError(f"{target_name} unit {unit_id} source root is unknown")
            safe_slash_prefixed_relative(
                unit.get("object_suffix"),
                f"{target_name} unit {unit_id} object suffix",
            )
            if not isinstance(unit.get("producer_kind"), str) or not isinstance(
                unit.get("producer_tool"), str
            ):
                raise GateError(f"{target_name} unit {unit_id} producer is incomplete")
            if unit["producer_tool"] not in target["tools"]:
                raise GateError(f"{target_name} unit {unit_id} names an unknown tool")
            dependency_delta_field = (
                ("expected_dependency_delta",)
                if unit["classification"] == "composition-dependent"
                else ()
            )
            generator = unit.get("generator")
            if unit["producer_kind"] == "wrapped-assembly":
                require_exact_keys(
                    unit,
                    (
                        "id",
                        "classification",
                        "source_root",
                        "source",
                        "maintained_source_root",
                        "maintained_source",
                        "object_suffix",
                        "producer_kind",
                        "producer_tool",
                        "generator",
                        "symbols",
                    )
                    + dependency_delta_field,
                    f"{target_name} unit {unit_id}",
                )
                generator = require_object(generator, f"{unit_id} generator")
                require_exact_keys(
                    generator,
                    (
                        "manifest_root",
                        "manifest",
                        "manifest_schema",
                        "tool_root",
                        "tool",
                        "wrapper_root",
                        "wrapper",
                    ),
                    f"{unit_id} generator",
                )
                require_exact_integer(
                    generator["manifest_schema"],
                    f"{unit_id} generator manifest_schema",
                    minimum=1,
                )
                if unit.get("maintained_source_root") not in target["required_roots"]:
                    raise GateError(f"{unit_id} maintained-source root is unknown")
                safe_relative(unit.get("maintained_source"), f"{unit_id} maintained source")
                safe_relative(generator["manifest"], f"{unit_id} generator manifest")
                safe_relative(generator["tool"], f"{unit_id} generator tool")
                safe_relative(generator["wrapper"], f"{unit_id} assembly wrapper")
            elif generator is not None:
                raise GateError(f"{unit_id} has a generator but is not wrapped assembly")
            else:
                require_exact_keys(
                    unit,
                    (
                        "id",
                        "classification",
                        "source_root",
                        "source",
                        "object_suffix",
                        "producer_kind",
                        "producer_tool",
                        "symbols",
                    )
                    + dependency_delta_field,
                    f"{target_name} unit {unit_id}",
                )
            if dependency_delta_field:
                dependency_delta = require_object(
                    unit["expected_dependency_delta"],
                    f"{target_name} unit {unit_id} expected dependency delta",
                )
                require_exact_keys(
                    dependency_delta,
                    ("qualification_only", "release_only"),
                    f"{target_name} unit {unit_id} expected dependency delta",
                )
                normalized_delta_paths: dict[str, list[str]] = {}
                for role_key in ("qualification_only", "release_only"):
                    paths = dependency_delta[role_key]
                    if (
                        not isinstance(paths, list)
                        or len(paths) != len(set(paths))
                        or any(not isinstance(path, str) for path in paths)
                    ):
                        raise GateError(
                            f"{target_name} unit {unit_id} {role_key} dependency delta is malformed"
                        )
                    normalized: list[str] = []
                    for path in paths:
                        match = ROOTED_PATH_RE.fullmatch(path)
                        if (
                            match is None
                            or match.group(1) not in target["required_roots"]
                            or match.group(2) is None
                        ):
                            raise GateError(
                                f"{target_name} unit {unit_id} {role_key} dependency is not policy-rooted"
                            )
                        relative = safe_relative(
                            match.group(2),
                            f"{target_name} unit {unit_id} {role_key} dependency",
                        )
                        canonical = "${" + match.group(1) + "}/" + relative.as_posix()
                        if path != canonical:
                            raise GateError(
                                f"{target_name} unit {unit_id} {role_key} dependency is not canonical"
                            )
                        normalized.append(canonical)
                    normalized_delta_paths[role_key] = normalized
                if set(normalized_delta_paths["qualification_only"]) & set(
                    normalized_delta_paths["release_only"]
                ):
                    raise GateError(
                        f"{target_name} unit {unit_id} dependency delta overlaps roles"
                    )
            symbols = unit.get("symbols")
            if not isinstance(symbols, list) or not symbols:
                raise GateError(f"{target_name} unit {unit_id} has no owned symbols")
            for symbol in symbols:
                symbol = require_object(symbol, f"{unit_id} symbol")
                require_exact_keys(symbol, ("name", "map_name", "types"), f"{unit_id} symbol")
                name = symbol["name"]
                if not isinstance(name, str) or not name or name in symbol_owners:
                    raise GateError(f"duplicate/invalid policy symbol {name!r}")
                if not isinstance(symbol["map_name"], str) or not symbol["map_name"]:
                    raise GateError(f"{unit_id} symbol lacks map_name")
                types = symbol["types"]
                if not isinstance(types, list) or not types or any(
                    not isinstance(item, str) or len(item) != 1 for item in types
                ):
                    raise GateError(f"{unit_id} symbol {name} has invalid types")
                symbol_owners[name] = unit_id
            by_id[unit_id] = unit
        role_sets: dict[str, set[str]] = {}
        for role_name, role in roles.items():
            role = require_object(role, f"{target_name} role {role_name}")
            require_exact_keys(
                role,
                (
                    "required_units",
                    "forbidden_units",
                    "forbidden_symbols",
                    "requires_separate_composition_identity",
                    "expected_composition_artifact_id",
                    "expected_composition_artifact_kind",
                    "source_selection",
                    "unit_command_sha256",
                    "final_link_command_sha256",
                ),
                f"{target_name} role {role_name}",
            )
            required = role.get("required_units")
            if not isinstance(required, list) or len(required) != len(set(required)):
                raise GateError(f"{target_name} {role_name} unit set is malformed")
            unknown = set(required) - set(by_id)
            if unknown:
                raise GateError(f"{target_name} {role_name} names unknown units {sorted(unknown)}")
            forbidden_units = role["forbidden_units"]
            if (
                not isinstance(forbidden_units, list)
                or len(forbidden_units) != len(set(forbidden_units))
                or not set(forbidden_units) <= set(by_id)
                or set(forbidden_units) & set(required)
            ):
                raise GateError(f"{target_name} {role_name} forbidden-unit set is malformed")
            forbidden_symbols = role["forbidden_symbols"]
            if (
                not isinstance(forbidden_symbols, list)
                or len(forbidden_symbols) != len(set(forbidden_symbols))
                or any(not isinstance(item, str) or not item for item in forbidden_symbols)
            ):
                raise GateError(f"{target_name} {role_name} forbidden symbols are malformed")
            requires_composition = role["requires_separate_composition_identity"]
            if not isinstance(requires_composition, bool):
                raise GateError(f"{target_name} {role_name} composition rule is malformed")
            expected_composition = role["expected_composition_artifact_id"]
            expected_kind = role["expected_composition_artifact_kind"]
            if requires_composition:
                if not isinstance(expected_composition, str) or not isinstance(expected_kind, str):
                    raise GateError(f"{target_name} {role_name} composition authority is absent")
            elif expected_composition is not None or expected_kind is not None:
                raise GateError(f"{target_name} {role_name} has an unexpected composition authority")
            if role["source_selection"] is not None:
                safe_relative(role["source_selection"], f"{target_name} {role_name} selection")
            command_digests = require_object(
                role["unit_command_sha256"],
                f"{target_name} {role_name} command fingerprints",
            )
            if set(command_digests) != set(required):
                raise GateError(
                    f"{target_name} {role_name} command-fingerprint unit set differs from role"
                )
            fingerprint_values = [
                *command_digests.values(), role["final_link_command_sha256"]
            ]
            for digest in fingerprint_values:
                if digest is not None:
                    require_sha256(
                        digest,
                        f"{target_name} {role_name} command fingerprint",
                    )
            if target["command_policy_status"] == "frozen" and any(
                digest is None for digest in fingerprint_values
            ):
                raise GateError(
                    f"{target_name} frozen command policy contains an unset fingerprint"
                )
            role_sets[role_name] = set(required)
        for unit_id, unit in by_id.items():
            classification = unit["classification"]
            in_qualification = unit_id in role_sets["qualification"]
            in_release = unit_id in role_sets["release"]
            expected_presence = {
                "equality": (True, True),
                "composition-dependent": (True, True),
                "qualification-only": (True, False),
                "release-only": (False, True),
            }[classification]
            if (in_qualification, in_release) != expected_presence:
                raise GateError(
                    f"{target_name} unit {unit_id} role presence contradicts {classification}"
                )
    return policy


def verify_policy_authority(
    policy_path: Path, roots: Mapping[str, RootBinding]
) -> str:
    authority = roots["AUTHORITY"].resolved
    path = regular_file(policy_path, "policy")
    verify_tracked_file(authority, path, "policy")
    return sha256_file(path)


def verify_prepared_source(
    target_policy: dict[str, Any],
    repositories: Mapping[str, dict[str, Any]],
    roots: Mapping[str, RootBinding],
    python: Path | None,
) -> dict[str, Any] | None:
    specification = target_policy.get("prepared_source")
    if specification is None:
        return None
    if python is None:
        raise GateError("prepared-source checker lacks a policy-pinned Python")
    specification = require_object(specification, "prepared_source policy")
    prepared = roots[specification["root"]].resolved
    metadata_path = regular_file(
        prepared / specification["metadata"],
        "prepared-source metadata",
        root=prepared,
    )
    metadata = require_object(load_json(metadata_path, "prepared-source metadata"), "prepared metadata")
    if require_exact_integer(metadata.get("schema"), "prepared metadata schema") != 1:
        raise GateError("prepared-source metadata has unsupported schema")
    source_record = require_object(metadata.get("source"), "prepared metadata source")
    if source_record.get("tracked_dirty") is not False:
        raise GateError("prepared source was derived from tracked-dirty input")
    source_repo_id = specification["source_repository"]
    if source_record.get("head") != repositories[source_repo_id]["commit"]:
        raise GateError("prepared-source commit does not match product source")
    files = metadata.get("files")
    if not isinstance(files, list) or not files:
        raise GateError("prepared-source metadata has no files")
    expected_names = {specification["metadata"]}
    for entry in files:
        entry = require_object(entry, "prepared file")
        require_exact_keys(entry, ("path", "sha256", "executable_bits"), "prepared file")
        relative = PurePosixPath(entry["path"])
        if relative.is_absolute() or any(part in ("", ".", "..") for part in relative.parts):
            raise GateError(f"unsafe prepared-source path {entry['path']!r}")
        if entry["path"] in expected_names:
            raise GateError(f"duplicate prepared-source path {entry['path']!r}")
        expected_names.add(entry["path"])
        path = regular_file(prepared.joinpath(*relative.parts), "prepared file", root=prepared)
        if sha256_file(path) != require_sha256(entry["sha256"], "prepared file digest"):
            raise GateError(f"prepared-source digest mismatch: {entry['path']}")
        observed_mode = f"{stat.S_IMODE(path.stat().st_mode) & 0o111:03o}"
        if observed_mode != entry["executable_bits"]:
            raise GateError(f"prepared-source executable mode mismatch: {entry['path']}")
    observed_names: set[str] = set()
    for path in prepared.rglob("*"):
        metadata_bits = path.lstat().st_mode
        if stat.S_ISLNK(metadata_bits):
            raise GateError(f"prepared source contains a symbolic link: {path}")
        if stat.S_ISREG(metadata_bits):
            observed_names.add(path.relative_to(prepared).as_posix())
        elif not stat.S_ISDIR(metadata_bits):
            raise GateError(f"prepared source contains a non-file entry: {path}")
    if observed_names != expected_names:
        raise GateError(
            "prepared-source file set differs from metadata: "
            f"missing={sorted(expected_names - observed_names)}, "
            f"extra={sorted(observed_names - expected_names)}"
        )
    checker_repo_id = specification["checker_repository"]
    checker_root = roots[
        next(
            item["root"]
            for item in target_policy["repositories"]
            if item["id"] == checker_repo_id
        )
    ].resolved
    checker = regular_file(checker_root / specification["checker"], "prepared-source checker", root=checker_root)
    verify_tracked_file(checker_root, checker, "prepared-source checker")
    source_root = roots[
        next(
            item["root"]
            for item in target_policy["repositories"]
            if item["id"] == source_repo_id
        )
    ].resolved
    run_checked(
        (
            os.fspath(python),
            "-B",
            os.fspath(checker),
            "--repo-root",
            os.fspath(checker_root),
            "--upstream",
            os.fspath(source_root),
            "--destination",
            os.fspath(prepared),
            "--check",
        ),
        timeout=120,
    )
    return {
        "metadata_sha256": sha256_file(metadata_path),
        "source_commit": source_record["head"],
        "file_count": len(files),
        "checker_commit": repositories[checker_repo_id]["commit"],
    }


def verify_tool(
    name: str, specification: dict[str, Any], roots: Mapping[str, RootBinding]
) -> dict[str, Any]:
    require_exact_keys(specification, ("path", "sha256"), f"tool policy {name}")
    path = resolve_rooted_path(specification["path"], roots, f"policy tool {name}")
    digest = sha256_file(path)
    if digest != require_sha256(specification["sha256"], f"tool policy {name}.sha256"):
        raise GateError(f"policy tool {name} executable digest mismatch")
    completed = run_checked((os.fspath(path), "--version"))
    version = normalize_external_text(
        (completed.stdout + completed.stderr).decode("utf-8", errors="replace").strip(),
        roots,
    ).encode("utf-8")
    return {
        "name": name,
        "path": specification["path"],
        "sha256": digest,
        "size": path.stat().st_size,
        "version_output_sha256": sha256_bytes(version),
        "resolved": path,
    }


def expanded_policy_location(
    value: str, roots: Mapping[str, RootBinding], label: str
) -> Path:
    if not isinstance(value, str):
        raise GateError(f"{label} must be a rooted path string")
    match = ROOTED_PATH_RE.fullmatch(value)
    if match is None or match.group(1) not in roots:
        raise GateError(f"{label} does not use a declared root")
    suffix = match.group(2)
    parts: tuple[str, ...] = ()
    if suffix is not None:
        parts = safe_relative(suffix, f"{label} rooted-path suffix").parts
    return roots[match.group(1)].resolved.joinpath(*parts)


def validate_environment(
    value: Any,
    specification: Any,
    roots: Mapping[str, RootBinding],
    label: str,
) -> dict[str, Any]:
    environment = require_object(value, label)
    policy = require_object(specification, f"{label} policy")
    require_exact_keys(
        environment,
        ("policy", "variables", "cleared_variables", "source_date_epoch"),
        label,
    )
    if environment["policy"] != policy.get("policy") or environment[
        "policy"
    ] != "sanitized-deterministic-v1":
        raise GateError(f"{label} does not match the policy environment class")
    variables = environment["variables"]
    cleared = environment["cleared_variables"]
    epoch = require_object(environment["source_date_epoch"], f"{label}.source_date_epoch")
    if not isinstance(variables, dict) or any(
        not isinstance(name, str) or not isinstance(value, str)
        for name, value in variables.items()
    ):
        raise GateError(f"{label}.variables must be a string mapping")
    if any(FORBIDDEN_ENVIRONMENT.search(name) for name in variables):
        raise GateError(f"{label} records a secret-bearing environment name")
    if not isinstance(cleared, list) or len(cleared) != len(set(cleared)) or any(
        not isinstance(name, str) or not name for name in cleared
    ):
        raise GateError(f"{label}.cleared_variables is malformed")
    if set(variables) & set(cleared):
        raise GateError(f"{label} both sets and clears an environment variable")
    if cleared != policy.get("exact_cleared_variables"):
        raise GateError(f"{label}.cleared_variables differs from tracked policy")
    if "exact_variables" in policy:
        require_exact_keys(
            policy,
            (
                "policy",
                "exact_variables",
                "exact_cleared_variables",
                "source_date_epoch",
            ),
            f"{label} policy",
        )
        if variables != policy["exact_variables"]:
            raise GateError(f"{label}.variables differs from tracked policy")
    else:
        require_exact_keys(
            policy,
            (
                "policy",
                "exact_variable_names",
                "exact_values",
                "path_allowed_roots",
                "path_allowed_system_directories",
                "path_required_directory",
                "exact_cleared_variables",
                "source_date_epoch",
            ),
            f"{label} policy",
        )
        names = policy["exact_variable_names"]
        if not isinstance(names, list) or set(variables) != set(names) or len(names) != len(set(names)):
            raise GateError(f"{label}.variables has the wrong exact name set")
        for name, expected in require_object(
            policy["exact_values"], f"{label} exact values"
        ).items():
            if isinstance(expected, str) and ROOTED_PATH_RE.fullmatch(expected):
                expected_value = os.fspath(
                    expanded_policy_location(expected, roots, f"{label}.{name}")
                )
            else:
                expected_value = expected
            if variables.get(name) != expected_value:
                raise GateError(f"{label}.{name} differs from tracked policy")
        path_value = variables.get("PATH")
        if not isinstance(path_value, str):
            raise GateError(f"{label}.PATH is absent")
        entries = path_value.split(os.pathsep)
        if not entries or any(not item or not Path(item).is_absolute() for item in entries):
            raise GateError(f"{label}.PATH contains an empty or relative directory")
        if len(entries) != len(set(entries)):
            raise GateError(f"{label}.PATH contains a duplicate directory")
        allowed_system = set(policy["path_allowed_system_directories"])
        allowed_roots = [roots[name].resolved for name in policy["path_allowed_roots"]]
        observed_resolved: set[Path] = set()
        for entry in entries:
            try:
                resolved = Path(entry).resolve(strict=True)
            except (OSError, RuntimeError) as error:
                raise GateError(f"{label}.PATH entry is unavailable: {entry}: {error}") from error
            if not resolved.is_dir():
                raise GateError(f"{label}.PATH entry is not a directory: {entry}")
            if resolved in observed_resolved:
                raise GateError(f"{label}.PATH contains aliased directories")
            observed_resolved.add(resolved)
            if entry in allowed_system:
                continue
            if not any(
                resolved == allowed or resolved.is_relative_to(allowed)
                for allowed in allowed_roots
            ):
                raise GateError(f"{label}.PATH entry is outside policy roots: {entry}")
        required_directory = expanded_policy_location(
            policy["path_required_directory"], roots, f"{label}.PATH required directory"
        ).resolve(strict=True)
        if required_directory not in observed_resolved:
            raise GateError(f"{label}.PATH omits the policy toolchain directory")
    require_exact_keys(epoch, ("disposition", "value"), f"{label}.source_date_epoch")
    if epoch != policy.get("source_date_epoch"):
        raise GateError(f"{label}.source_date_epoch differs from tracked policy")
    if epoch["disposition"] == "cleared":
        if epoch["value"] is not None or "SOURCE_DATE_EPOCH" not in cleared:
            raise GateError(f"{label} has inconsistent cleared SOURCE_DATE_EPOCH")
    elif epoch["disposition"] == "fixed":
        if not isinstance(epoch["value"], str) or not epoch["value"].isdigit():
            raise GateError(f"{label} has invalid fixed SOURCE_DATE_EPOCH")
        if variables.get("SOURCE_DATE_EPOCH") != epoch["value"]:
            raise GateError(f"{label} fixed SOURCE_DATE_EPOCH is not in variables")
    else:
        raise GateError(f"{label} has unsupported SOURCE_DATE_EPOCH disposition")
    return environment


def validate_executable_record(
    value: Any,
    roots: Mapping[str, RootBinding],
    environment: Mapping[str, str],
    label: str,
) -> dict[str, Any]:
    record = require_object(value, label)
    require_exact_keys(
        record,
        (
            "path",
            "sha256",
            "size",
            "version_command",
            "version_output_sha256",
            "version_output",
        ),
        label,
    )
    path = verify_file_record(
        {key: record[key] for key in ("path", "sha256", "size")}, roots, label
    )
    version_command = record["version_command"]
    if version_command != [record["path"], "--version"]:
        raise GateError(f"{label} version command is not canonical")
    completed = run_checked(
        (os.fspath(path), "--version"), environment=environment
    )
    observed = normalize_external_text(
        (completed.stdout + completed.stderr).decode("utf-8", errors="replace").strip(),
        roots,
    )
    if record["version_output"] != observed or sha256_bytes(observed.encode("utf-8")) != require_sha256(
        record["version_output_sha256"], f"{label}.version_output_sha256"
    ):
        raise GateError(f"{label} version output digest mismatch")
    if not isinstance(record["version_output"], str) or "\x00" in record["version_output"]:
        raise GateError(f"{label}.version_output is malformed")
    return record


RAW_STEP_FIELDS = {
    "schema_version",
    "evidence_kind",
    "step_kind",
    "input_stability",
    "working_directory",
    "command",
    "executables",
    "source",
    "declared_inputs",
    "declared_inputs_sha256",
    "dependencies",
    "depfile",
    "output",
    "secondary_outputs",
    "captured_stdout",
    "ordered_link_inputs",
    "producer_records",
    "recorder",
    "session",
    "environment",
    "response_files",
    "driver_selection",
}


def load_mos_step(
    reference: Any,
    evidence_root: Path,
    roots: Mapping[str, RootBinding],
    expected_kind: str,
    environment_policy: dict[str, Any],
    label: str,
) -> StepView:
    path = verify_evidence_reference(reference, evidence_root, label)
    document = require_object(load_json(path, label), label)
    require_exact_keys(document, RAW_STEP_FIELDS, label)
    if (
        require_exact_integer(document["schema_version"], f"{label}.schema_version")
        != 1
        or document["evidence_kind"] != expected_kind
    ):
        raise GateError(f"{label} has unsupported raw-step schema/kind")
    if document["input_stability"] != "verified-before-and-after":
        raise GateError(f"{label} lacks verified input stability")
    if not isinstance(document["working_directory"], str):
        raise GateError(f"{label} working_directory is malformed")
    working = document["working_directory"]
    match = ROOTED_PATH_RE.fullmatch(working)
    if match is None or match.group(1) not in roots:
        raise GateError(f"{label} working_directory is outside declared roots")
    command = document["command"]
    if not isinstance(command, list) or not command or any(
        not isinstance(item, str) or not item or "\x00" in item for item in command
    ):
        raise GateError(f"{label} command must be a nonempty argv array")
    environment = validate_environment(
        document["environment"], environment_policy, roots, f"{label}.environment"
    )
    response_files = document["response_files"]
    if not isinstance(response_files, list):
        raise GateError(f"{label}.response_files must be an array")
    response_paths: list[str] = []
    response_records: list[tuple[Path, dict[str, Any]]] = []
    response_identities: set[Path] = set()
    for index, response in enumerate(response_files):
        response_path = verify_file_record(
            response, roots, f"{label}.response_files[{index}]"
        )
        register_unique_file_path(
            response_path, response_identities, f"{label}.response_files"
        )
        if b"@" in response_path.read_bytes():
            raise GateError(
                f"{label}.response_files[{index}] contains unsupported nested-response syntax"
            )
        response_paths.append(response["path"])
        response_records.append((response_path, response))
    command_responses = [
        item[1:] for item in command if item.startswith("@") and len(item) > 1
    ]
    if command_responses != response_paths:
        raise GateError(
            f"{label} response-file records differ from command references: "
            f"command={sorted(command_responses)}, records={sorted(response_paths)}"
        )
    executables = document["executables"]
    if not isinstance(executables, list) or not executables:
        raise GateError(f"{label} has no executable records")
    executable_paths: set[Path] = set()
    for index, executable in enumerate(executables):
        validate_executable_record(
            executable,
            roots,
            environment["variables"],
            f"{label}.executables[{index}]",
        )
        executable_path = resolve_rooted_path(
            executable["path"], roots, f"{label}.executables[{index}]"
        )
        register_unique_file_path(
            executable_path, executable_paths, f"{label} executable records"
        )
    if command[0] != executables[0]["path"]:
        raise GateError(f"{label} command does not start with its primary executable")
    source = verify_file_record(document["source"], roots, f"{label}.source")
    declared = document["declared_inputs"]
    dependencies = document["dependencies"]
    if not isinstance(declared, list) or not declared:
        raise GateError(f"{label} has no declared inputs")
    if not isinstance(dependencies, list) or not dependencies:
        raise GateError(f"{label} has no dependencies")
    declared_by_path: dict[Path, dict[str, Any]] = {}
    declared_paths: set[Path] = set()
    for index, record in enumerate(declared):
        declared_path = verify_file_record(
            record, roots, f"{label}.declared_inputs[{index}]"
        )
        register_unique_file_path(
            declared_path, declared_paths, f"{label} declared inputs"
        )
        declared_by_path[declared_path] = record
    normalized_declared = sorted(declared, key=lambda item: item["path"])
    if sha256_bytes(canonical_bytes(normalized_declared)) != require_sha256(
        document["declared_inputs_sha256"], f"{label}.declared_inputs_sha256"
    ):
        raise GateError(f"{label} declared-input aggregate digest mismatch")
    dependency_paths: set[Path] = set()
    for index, record in enumerate(dependencies):
        dependency_path = verify_file_record(
            record, roots, f"{label}.dependencies[{index}]"
        )
        register_unique_file_path(
            dependency_path, dependency_paths, f"{label} dependencies"
        )
        require_predeclared_file_record(
            record,
            dependency_path,
            declared_by_path,
            f"{label} dependency",
        )
    if source not in dependency_paths:
        for dependency_path in dependency_paths:
            canonical_file_paths_match(source, dependency_path, f"{label} source dependency")
        raise GateError(f"{label} dependencies omit the primary source")
    for response_path, response in response_records:
        require_predeclared_file_record(
            response,
            response_path,
            declared_by_path,
            f"{label} response file",
        )
    depfile = verify_file_record(document["depfile"], roots, f"{label}.depfile")
    output = verify_file_record(document["output"], roots, f"{label}.output")
    secondary = document["secondary_outputs"]
    if not isinstance(secondary, list):
        raise GateError(f"{label}.secondary_outputs must be an array")
    secondary_paths: set[Path] = set()
    for index, record in enumerate(secondary):
        secondary_path = verify_file_record(
            record, roots, f"{label}.secondary_outputs[{index}]"
        )
        register_unique_file_path(
            secondary_path, secondary_paths, f"{label} secondary outputs"
        )
    stdout_path: Path | None = None
    if document["captured_stdout"] is not None:
        stdout_path = verify_file_record(
            document["captured_stdout"], roots, f"{label}.captured_stdout"
        )
    ordered = document["ordered_link_inputs"]
    if not isinstance(ordered, list):
        raise GateError(f"{label}.ordered_link_inputs must be an array")
    ordered_paths: set[Path] = set()
    for index, record in enumerate(ordered):
        ordered_path = verify_file_record(
            record, roots, f"{label}.ordered_link_inputs[{index}]"
        )
        register_unique_file_path(
            ordered_path, ordered_paths, f"{label} ordered link inputs"
        )
        require_predeclared_file_record(
            record,
            ordered_path,
            declared_by_path,
            f"{label} ordered link input",
        )
        if ordered_path not in dependency_paths:
            for dependency_path in dependency_paths:
                canonical_file_paths_match(
                    ordered_path, dependency_path, f"{label} ordered dependency"
                )
            raise GateError(f"{label} dependency file omits an ordered link input")
    producers = document["producer_records"]
    if not isinstance(producers, list):
        raise GateError(f"{label}.producer_records must be an array")
    producer_inputs: set[Path] = set()
    producer_records: set[Path] = set()
    for index, producer in enumerate(producers):
        producer = require_object(producer, f"{label}.producer_records[{index}]")
        require_exact_keys(
            producer,
            ("input", "record", "record_sha256", "output_sha256"),
            f"{label}.producer_records[{index}]",
        )
        require_sha256(producer["record_sha256"], "producer record digest")
        require_sha256(producer["output_sha256"], "producer output digest")
        input_path = resolve_rooted_path(producer["input"], roots, "producer input")
        record_path = resolve_rooted_path(producer["record"], roots, "producer record")
        if sha256_file(input_path) != producer["output_sha256"]:
            raise GateError(f"{label} producer output digest is stale")
        if sha256_file(record_path) != producer["record_sha256"]:
            raise GateError(f"{label} producer record digest is stale")
        register_unique_file_path(
            input_path, producer_inputs, f"{label} producer inputs"
        )
        register_unique_file_path(
            record_path, producer_records, f"{label} producer records"
        )
        if input_path not in ordered_paths:
            for ordered_path in ordered_paths:
                canonical_file_paths_match(
                    input_path, ordered_path, f"{label} producer input"
                )
            raise GateError(f"{label} producer input is not an ordered link input")
        if not producer["record"].startswith("${PROVENANCE}/"):
            raise GateError(f"{label} producer record is not actual-step evidence")
    recorder = verify_file_record(document["recorder"], roots, f"{label}.recorder")
    session = verify_file_record(document["session"], roots, f"{label}.session")
    for name, record, record_path in (
        ("recorder", document["recorder"], recorder),
        ("session", document["session"], session),
    ):
        require_predeclared_file_record(
            record, record_path, declared_by_path, f"{label} {name}"
        )
    output_records = [
        ("output", output),
        ("depfile", depfile),
        *(("secondary output", item) for item in secondary_paths),
    ]
    if stdout_path is not None:
        output_records.append(("captured stdout", stdout_path))
    output_paths: set[Path] = set()
    for output_name, output_path in output_records:
        register_unique_file_path(
            output_path, output_paths, f"{label} {output_name} paths"
        )
    return StepView(
        record_path=path,
        record_sha256=sha256_file(path),
        document=document,
        source_path=source,
        output_path=output,
        command=tuple(command),
        dependencies=tuple(dependencies),
    )


def executables_match_tools(
    step: StepView,
    tools: Mapping[str, dict[str, Any]],
    expected_names: Sequence[str],
    label: str,
) -> None:
    records = step.document["executables"]
    if len(records) != len(expected_names):
        raise GateError(f"{label} executable set differs from tracked policy")
    for index, name in enumerate(expected_names):
        record = records[index]
        tool = tools[name]
        for field in ("path", "sha256", "size", "version_output_sha256"):
            if record[field] != tool[field]:
                raise GateError(f"{label} executable {index} is not policy tool {name}")


def denormalize_token(value: str, roots: Mapping[str, RootBinding], label: str) -> str:
    result = value
    for name, root in sorted(roots.items(), key=lambda item: len(item[0]), reverse=True):
        result = result.replace("${" + name + "}", os.fspath(root.lexical))
    if "${" in result:
        raise GateError(f"{label} contains an undeclared root placeholder")
    return result


def reject_reserved_root_placeholder(value: str, label: str) -> None:
    if RESERVED_ROOT_PLACEHOLDER.search(value):
        raise GateError(f"{label} contains a literal reserved root placeholder")


def normalize_external_text(value: str, roots: Mapping[str, RootBinding]) -> str:
    candidates: list[tuple[str, str]] = []
    for name, root in roots.items():
        replacement = "${" + name + "}"
        candidates.extend(
            (candidate, replacement)
            for candidate in {os.fspath(root.lexical), os.fspath(root.resolved)}
        )
    result = value
    for candidate, replacement in sorted(candidates, key=lambda item: len(item[0]), reverse=True):
        result = re.sub(
            re.escape(candidate) + r"(?=$|/|[\s\"'`,;:\]\)])",
            replacement,
            result,
        )
    return result


def normalize_external_value(value: Any, roots: Mapping[str, RootBinding]) -> Any:
    """Recursively root-normalize every string without JSON delimiter ambiguity."""

    if isinstance(value, str):
        return normalize_external_text(value, roots)
    if isinstance(value, list):
        return [normalize_external_value(item, roots) for item in value]
    if isinstance(value, dict):
        return {
            key: normalize_external_value(item, roots)
            for key, item in value.items()
        }
    return value


def normalize_policy_command(
    arguments: Sequence[str],
    roots: Mapping[str, RootBinding],
    identity_binding: Mapping[str, Any],
) -> list[str]:
    """Normalize only declared roots and exact per-build identity values.

    Arbitrary flags, ordering, quoting, macro names, and non-identity values
    remain byte-significant.  This intentionally does not provide a generic
    redact/ignore facility.
    """

    identity_definitions = {
        "EMOS_SOURCE_IDENTITY": (
            identity_binding.get("source_identity"),
            "${BUILD_IDENTITY:source_identity}",
        ),
        "EMOS_BUILD_ID": (
            identity_binding.get("build_id"),
            "${BUILD_IDENTITY:build_id}",
        ),
        "EMOS_ARTIFACT_STATUS": (
            identity_binding.get("lifecycle_status"),
            "${BUILD_IDENTITY:lifecycle_status}",
        ),
        "EMOS_QUALIFICATION_COMPOSITION_IDENTITY": (
            identity_binding.get("captured_composition_identity"),
            "${BUILD_IDENTITY:composition_identity}",
        ),
    }

    def normalize_definition(definition: str) -> str:
        name, separator, raw_value = definition.partition("=")
        if not separator or name not in identity_definitions:
            return definition
        expected, placeholder = identity_definitions[name]
        if not isinstance(expected, str) or not expected:
            return definition
        quote = ""
        decoded = raw_value
        if len(raw_value) >= 2 and raw_value[0] == raw_value[-1] == '"':
            quote = '"'
            decoded = raw_value[1:-1]
        if decoded != expected:
            # Identity validation owns the semantic error.  Retaining the
            # unexpected bytes here ensures a fingerprint cannot hide it.
            return definition
        return f"{name}={quote}{placeholder}{quote}"

    normalized: list[str] = []
    index = 0
    while index < len(arguments):
        argument = normalize_external_text(arguments[index], roots)
        if argument == "-D" and index + 1 < len(arguments):
            normalized.append(argument)
            normalized.append(
                normalize_definition(
                    normalize_external_text(arguments[index + 1], roots)
                )
            )
            index += 2
            continue
        if argument.startswith("-D") and len(argument) > 2:
            argument = "-D" + normalize_definition(argument[2:])
        normalized.append(argument)
        index += 1
    return normalized


def command_policy_material(
    *,
    actual_arguments: Sequence[str],
    expanded_arguments: Sequence[str],
    response_files: Sequence[Mapping[str, Any]],
    roots: Mapping[str, RootBinding],
    identity_binding: Mapping[str, Any],
    tool_selection: Any = None,
) -> dict[str, Any]:
    responses: list[dict[str, Any]] = []
    for response in response_files:
        responses.append(
            {
                "reference": normalize_external_text(response["reference"], roots),
                "path": normalize_external_text(response["path"], roots),
                "sha256": response["sha256"],
                "size": response["size"],
            }
        )
    normalized_tool_selection = normalize_external_value(tool_selection, roots)
    return {
        "actual_argument_vector": normalize_policy_command(
            actual_arguments, roots, identity_binding
        ),
        "response_files": responses,
        "expanded_argument_vector": normalize_policy_command(
            expanded_arguments, roots, identity_binding
        ),
        "tool_selection": normalized_tool_selection,
    }


def normalized_mos_driver_selection(
    value: Any,
    roots: Mapping[str, RootBinding],
    identity_binding: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Retain the authenticated effective Clang selection without raw IDs.

    The full probe transcript is independently replayed before this summary is
    built.  Only argv-shaped fields receive the narrow protected-definition
    normalization; unrelated text such as lifecycle words in paths is never
    globally redacted.
    """

    if not isinstance(value, list):
        raise GateError("EMOS driver selection is not an array")
    result: list[dict[str, Any]] = []
    for index, record in enumerate(value):
        record = require_object(record, f"EMOS driver selection {index}")
        probe_command = normalize_policy_command(
            record["probe_command"], roots, identity_binding
        )
        selected_invocation = normalize_policy_command(
            record["selected_invocation"], roots, identity_binding
        )
        probe_output = record["probe_output"]
        if not isinstance(probe_output, str):
            raise GateError(f"EMOS driver selection {index} probe output is not text")
        probe_transcript: list[dict[str, Any]] = []
        for line_number, line in enumerate(probe_output.splitlines(), 1):
            if line.lstrip().startswith('"'):
                try:
                    invocation = shlex.split(line, posix=True)
                except ValueError as error:
                    raise GateError(
                        f"EMOS driver selection {index} probe line {line_number} is malformed"
                    ) from error
                if not invocation:
                    raise GateError(
                        f"EMOS driver selection {index} has an empty probe invocation"
                    )
                probe_transcript.append(
                    {
                        "kind": "invocation",
                        "argv": normalize_policy_command(
                            invocation, roots, identity_binding
                        ),
                    }
                )
            else:
                probe_transcript.append(
                    {
                        "kind": "text",
                        "text": normalize_external_text(line, roots),
                    }
                )
        result.append(
            {
                "driver": normalize_external_text(record["driver"], roots),
                "selected_executable": normalize_external_text(
                    record["selected_executable"], roots
                ),
                "selected_executable_sha256": record[
                    "selected_executable_sha256"
                ],
                "probe_command": probe_command,
                "probe_transcript": probe_transcript,
                "selected_invocation": selected_invocation,
                "normalized_probe_and_selection_sha256": command_fingerprint(
                    {
                        "probe_command": probe_command,
                        "probe_transcript": probe_transcript,
                        "selected_invocation": selected_invocation,
                    }
                ),
            }
        )
    return result


def command_fingerprint(material: object) -> str:
    return sha256_bytes(canonical_bytes(material))


def evaluate_command_policy(
    target_policy: dict[str, Any], role: str, capture: dict[str, Any]
) -> tuple[bool, list[str], dict[str, Any]]:
    """Compare actual normalized argv with tracked role-owned fingerprints."""

    role_policy = target_policy["roles"][role]
    candidates = {
        "normalization": target_policy["command_normalization"],
        "unit_commands": {
            unit_id: capture["units"][unit_id]["command_policy_material"]
            for unit_id in role_policy["required_units"]
        },
        "unit_command_sha256": {
            unit_id: capture["units"][unit_id]["command_sha256"]
            for unit_id in role_policy["required_units"]
        },
        "final_link_command": capture["final_link_command_policy_material"],
        "final_link_command_sha256": capture["final_link_command_sha256"],
    }
    configured_units = role_policy["unit_command_sha256"]
    missing = [
        f"unit {unit_id}"
        for unit_id in role_policy["required_units"]
        if configured_units[unit_id] is None
    ]
    if role_policy["final_link_command_sha256"] is None:
        missing.append("final link")
    if missing:
        return (
            False,
            [
                "tracked intended-command fingerprints await a clean reviewed rehearsal: "
                + ", ".join(missing)
            ],
            candidates,
        )
    for unit_id, observed in candidates["unit_command_sha256"].items():
        if configured_units[unit_id] != observed:
            raise GateError(
                f"{role} unit {unit_id} normalized command differs from tracked policy"
            )
    if (
        role_policy["final_link_command_sha256"]
        != candidates["final_link_command_sha256"]
    ):
        raise GateError(f"{role} normalized final-link command differs from tracked policy")
    if target_policy["command_policy_status"] != "frozen":
        return (
            False,
            ["tracked intended-command fingerprints are populated but not frozen"],
            candidates,
        )
    return True, [], candidates


def run_combined(
    argv: Sequence[str], *, cwd: Path, environment: Mapping[str, str]
) -> bytes:
    try:
        completed = subprocess.run(
            list(argv),
            cwd=cwd,
            env=dict(environment),
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise GateError(f"driver-selection probe failed to execute: {error}") from error
    if completed.returncode != 0:
        raise GateError(f"driver-selection probe exited {completed.returncode}")
    return completed.stdout


def validate_mos_driver_selection(
    step: StepView,
    roots: Mapping[str, RootBinding],
    required: bool,
    label: str,
) -> None:
    selection = step.document["driver_selection"]
    if not isinstance(selection, list):
        raise GateError(f"{label}.driver_selection must be an array")
    if not required:
        if selection:
            raise GateError(f"{label} unexpectedly claims compiler-driver selection")
        return
    if len(selection) != 1 or len(step.document["executables"]) != 2:
        raise GateError(f"{label} lacks exactly one compiler-selected assembler")
    record = require_object(selection[0], f"{label}.driver_selection[0]")
    require_exact_keys(
        record,
        (
            "driver",
            "selected_executable",
            "selected_executable_sha256",
            "probe_command",
            "probe_output",
            "probe_output_sha256",
            "probe_output_size",
            "selected_invocation",
        ),
        f"{label}.driver_selection[0]",
    )
    driver = step.document["executables"][0]
    assembler = step.document["executables"][1]
    if (
        record["driver"] != driver["path"]
        or record["selected_executable"] != assembler["path"]
        or record["selected_executable_sha256"] != assembler["sha256"]
    ):
        raise GateError(f"{label} compiler-selected assembler is not the policy assembler")
    expected_probe = [step.command[0], "-###", "-save-temps=obj", *step.command[1:]]
    if record["probe_command"] != expected_probe:
        raise GateError(f"{label} driver-selection probe is not derived from actual argv")
    selected_invocation = record["selected_invocation"]
    if not isinstance(selected_invocation, list) or not selected_invocation or any(
        not isinstance(item, str) or not item for item in selected_invocation
    ):
        raise GateError(f"{label} selected invocation is malformed")
    working = normalized_working_directory(step.document["working_directory"], roots, label)
    probe_argv = [
        denormalize_token(item, roots, f"{label} probe") for item in record["probe_command"]
    ]
    observed = run_combined(
        probe_argv,
        cwd=working,
        environment=step.document["environment"]["variables"],
    )
    normalized_observed = normalize_external_text(
        observed.decode("utf-8", errors="replace"), roots
    )
    normalized_bytes = normalized_observed.encode("utf-8")
    require_exact_integer(
        record["probe_output_size"], f"{label} probe output size", minimum=0
    )
    if (
        record["probe_output"] != normalized_observed
        or len(normalized_bytes) != record["probe_output_size"]
        or sha256_bytes(normalized_bytes) != require_sha256(
        record["probe_output_sha256"], f"{label} probe output"
        )
    ):
        raise GateError(f"{label} driver-selection probe is not reproducible")
    expected_invocation = [
        denormalize_token(item, roots, f"{label} selected invocation")
        for item in selected_invocation
    ]
    selected_path = resolve_rooted_path(
        record["selected_executable"], roots, f"{label} selected assembler"
    )
    observed_invocations: list[list[str]] = []
    for line in normalized_observed.splitlines():
        candidate = line.lstrip()
        if not candidate.startswith('"'):
            continue
        try:
            invocation = shlex.split(candidate, posix=True)
        except ValueError as error:
            raise GateError(f"{label} probe emitted an unparseable invocation") from error
        if not invocation:
            continue
        invoked_token = denormalize_token(invocation[0], roots, label)
        invoked = command_token_path(invoked_token, roots, working, label)
        if invoked == selected_path:
            observed_invocations.append(
                [denormalize_token(item, roots, label) for item in invocation]
            )
    if observed_invocations != [expected_invocation]:
        raise GateError(f"{label} compiler-selected assembler invocation is ambiguous")


def require_command_pair(
    command: Sequence[str], option: str, value: str, label: str
) -> None:
    positions = [index for index, item in enumerate(command) if item == option]
    if len(positions) != 1 or positions[0] + 1 >= len(command):
        raise GateError(f"{label} does not contain exactly one {option}")
    if command[positions[0] + 1] != value:
        raise GateError(f"{label} {option} value does not match its raw record")


def command_token_path(
    token: str,
    roots: Mapping[str, RootBinding],
    working_directory: Path,
    label: str,
) -> Path | None:
    if ROOTED_PATH_RE.fullmatch(token):
        return resolve_rooted_path(token, roots, label)
    candidate = Path(token)
    if not candidate.is_absolute():
        candidate = working_directory / candidate
    try:
        resolved = candidate.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    return resolved if resolved.is_file() else None


def require_command_path_pair(
    command: Sequence[str],
    option: str,
    rooted_value: str,
    roots: Mapping[str, RootBinding],
    working_directory: Path,
    label: str,
) -> None:
    positions = [index for index, item in enumerate(command) if item == option]
    if len(positions) != 1 or positions[0] + 1 >= len(command):
        raise GateError(f"{label} does not contain exactly one {option}")
    expected = resolve_rooted_path(rooted_value, roots, f"{label} {option} record")
    observed = command_token_path(
        command[positions[0] + 1], roots, working_directory, f"{label} {option}"
    )
    if observed != expected:
        raise GateError(f"{label} {option} path does not match its raw record")


def command_path_positions(
    command: Sequence[str],
    rooted_value: str,
    roots: Mapping[str, RootBinding],
    working_directory: Path,
    label: str,
) -> list[int]:
    expected = resolve_rooted_path(rooted_value, roots, f"{label} expected path")
    positions: list[int] = []
    for index, token in enumerate(command):
        rooted_match = ROOTED_PATH_RE.fullmatch(token)
        if token.startswith("${") and rooted_match is None:
            raise GateError(f"{label} contains a malformed root placeholder")
        if rooted_match is not None:
            candidate = resolve_rooted_existing_path(token, roots, label)
            if candidate.is_dir():
                continue
            if not candidate.is_file():
                raise GateError(f"{label} token is not a regular file: {candidate}")
        else:
            candidate = command_token_path(token, roots, working_directory, label)
        if candidate is not None and canonical_file_paths_match(
            candidate, expected, label
        ):
            positions.append(index)
    return positions


def validate_mos_command(
    step: StepView,
    unit: dict[str, Any],
    roots: Mapping[str, RootBinding],
    label: str,
) -> None:
    command = list(step.command)
    working = normalized_working_directory(
        step.document["working_directory"], roots, label
    )
    source = step.document["source"]["path"]
    output = step.document["output"]["path"]
    depfile = step.document["depfile"]["path"]
    if unit["producer_kind"] == "c-compile":
        if command.count("-c") != 1 or len(
            command_path_positions(command, source, roots, working, f"{label} source")
        ) != 1:
            raise GateError(f"{label} is not an exact single-source compile")
        require_command_path_pair(command, "-o", output, roots, working, label)
        require_command_path_pair(command, "-MF", depfile, roots, working, label)
    elif unit["producer_kind"] == "wrapped-assembly":
        generator = unit["generator"]
        wrapper = "${" + generator["wrapper_root"] + "}/" + generator["wrapper"]
        manifest = "${" + generator["manifest_root"] + "}/" + generator["manifest"]
        assembler = step.document["executables"][1]["path"]
        if command[:2] != [step.document["executables"][0]["path"], "-B"] or len(command) < 3:
            raise GateError(f"{label} does not invoke the tracked assembly wrapper")
        if command_token_path(command[2], roots, working, f"{label} wrapper") != resolve_rooted_path(
            wrapper, roots, f"{label} wrapper record"
        ):
            raise GateError(f"{label} does not invoke the tracked assembly wrapper")
        require_command_path_pair(command, "--manifest", manifest, roots, working, label)
        require_command_path_pair(command, "--source", source, roots, working, label)
        require_command_path_pair(command, "--assembler", assembler, roots, working, label)
        require_command_path_pair(command, "--MD", depfile, roots, working, label)
        require_command_path_pair(command, "-o", output, roots, working, label)
        if command.count("--") != 1:
            raise GateError(f"{label} has an ambiguous wrapper/assembler boundary")
    else:
        raise GateError(f"{label} has an unsupported producer kind")


def command_defines(command: Sequence[str], label: str) -> dict[str, str]:
    definitions: dict[str, str] = {}
    index = 0
    while index < len(command):
        token = command[index]
        if token == "-D":
            if index + 1 >= len(command):
                raise GateError(f"{label} ends with a bare -D")
            definition = command[index + 1]
            index += 2
        elif token.startswith("-D") and len(token) > 2:
            definition = token[2:]
            index += 1
        else:
            index += 1
            continue
        name, separator, raw_value = definition.partition("=")
        if not name or name in definitions:
            raise GateError(f"{label} has an ambiguous definition {definition!r}")
        if not separator:
            raw_value = "1"
        if len(raw_value) >= 2 and raw_value[0] == raw_value[-1] == '"':
            raw_value = raw_value[1:-1]
        definitions[name] = raw_value
    return definitions


def command_undefines(command: Sequence[str], label: str) -> set[str]:
    """Return explicit compiler undefines, rejecting ambiguous spellings."""

    names: set[str] = set()
    index = 0
    while index < len(command):
        token = command[index]
        if token == "-U":
            if index + 1 >= len(command):
                raise GateError(f"{label} ends with a bare -U")
            name = command[index + 1]
            index += 2
        elif token.startswith("-U") and len(token) > 2:
            name = token[2:]
            index += 1
        else:
            index += 1
            continue
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name) or name in names:
            raise GateError(f"{label} has an ambiguous undefine {name!r}")
        names.add(name)
    return names


def require_no_response_indirection(step: StepView, label: str) -> None:
    """Apply the current product policy: no response indirection is admitted."""

    if step.document["response_files"] != []:
        raise GateError(f"{label} uses a response file outside current product policy")
    if any("@" in argument for argument in step.command):
        raise GateError(f"{label} command contains unproved response indirection")


def validate_mos_identity_binding(
    build: dict[str, Any],
    steps: Mapping[str, StepView],
    elf_path: Path,
) -> dict[str, Any]:
    unversioned = "UNVERSIONED-DO-NOT-DEPLOY"
    expected = {
        "EMOS_SOURCE_IDENTITY": build["identity"]["source_identity"] or unversioned,
        "EMOS_BUILD_ID": build["identity"]["build_id"] or unversioned,
        "EMOS_ARTIFACT_STATUS": build["identity"]["lifecycle_status"] or unversioned,
    }
    if any(not isinstance(value, str) or not value for value in expected.values()):
        raise GateError("EMOS build identity is absent from the build record")
    owner_id = "emos-mode-coordinator"
    if owner_id not in steps:
        raise GateError("EMOS identity-owning composition unit is absent")
    owner_defines = command_defines(steps[owner_id].command, "EMOS identity owner")
    for name, value in expected.items():
        if owner_defines.get(name) != value:
            raise GateError(f"EMOS identity owner does not compile exact {name}")
    composition_name = "EMOS_QUALIFICATION_COMPOSITION_IDENTITY"
    qualification_role_name = "EMOS_PARALLEL_FIXED_QUALIFICATION"
    protected_names = set(expected) | {composition_name, qualification_role_name}
    for unit_id, step in steps.items():
        undefined = protected_names & command_undefines(
            step.command, f"EMOS unit {unit_id}"
        )
        if undefined:
            raise GateError(
                "EMOS command undefines a protected identity/role macro: "
                f"{unit_id}: {sorted(undefined)}"
            )
    composition_identity = build["identity"]["composition_identity"]
    if build["role"] == "qualification":
        captured_composition = (
            composition_identity
            if isinstance(composition_identity, str) and composition_identity
            else "UNVERSIONED-PORT008-FORWARD-QUALIFICATION-DO-NOT-DEPLOY"
        )
        if owner_defines.get(composition_name) != captured_composition:
            raise GateError("EMOS identity owner does not compile the exact qualification composition")
        if owner_defines.get(qualification_role_name) != "1":
            raise GateError("EMOS qualification owner lacks exact fixed-qualification role")
    elif (
        composition_name in owner_defines
        or qualification_role_name in owner_defines
    ):
        raise GateError("EMOS release identity owner carries a qualification-only role")
    for unit_id, step in steps.items():
        if unit_id == owner_id:
            continue
        definitions = command_defines(step.command, f"unit {unit_id}")
        leaked = sorted(
            protected_names & set(definitions)
        )
        if leaked:
            raise GateError(
                f"EMOS identity definitions leaked outside the composition owner: {unit_id}: {leaked}"
            )
    image = elf_path.read_bytes()
    unversioned_present = b"UNVERSIONED" in image
    for name, value in expected.items():
        try:
            encoded = value.encode("ascii", errors="strict")
        except UnicodeError as error:
            raise GateError(f"EMOS build identity {name} is not ASCII") from error
        # A source identity is necessarily a prefix of its immutable build ID.
        # Require the independently terminated C string so the longer build-ID
        # literal cannot falsely satisfy the source-identity binding.
        if encoded + b"\0" not in image:
            raise GateError(
                f"EMOS final image does not contain independently terminated {name}"
            )
    if build["role"] == "qualification":
        try:
            composition_bytes = captured_composition.encode("ascii")
        except UnicodeError as error:
            raise GateError("EMOS qualification composition identity is not ASCII") from error
        if composition_bytes + b"\0" not in image:
            raise GateError(
                "EMOS final image does not contain its independently terminated "
                "qualification composition identity"
            )
    return {
        "owner_unit": owner_id,
        "source_identity": expected["EMOS_SOURCE_IDENTITY"],
        "build_id": expected["EMOS_BUILD_ID"],
        "lifecycle_status": expected["EMOS_ARTIFACT_STATUS"],
        "composition_identity": composition_identity,
        "captured_composition_identity": (
            captured_composition if build["role"] == "qualification" else None
        ),
        "fixed_qualification_role_bound": build["role"] == "qualification",
        "unversioned_marker_absent": not unversioned_present,
        "identity_values_bound": not unversioned_present and all(
            isinstance(build["identity"][field], str) and build["identity"][field]
            for field in ("source_identity", "build_id", "lifecycle_status")
        ) and (
            build["role"] == "release"
            or isinstance(composition_identity, str) and bool(composition_identity)
        ),
    }


def normalized_dependencies(step: StepView) -> list[dict[str, Any]]:
    return sorted(
        (
            {"path": item["path"], "sha256": item["sha256"], "size": item["size"]}
            for item in step.dependencies
        ),
        key=lambda item: item["path"],
    )


def normalized_declared_inputs(step: StepView) -> list[dict[str, Any]]:
    session_path = step.document["session"]["path"]
    return sorted(
        (
            {"path": item["path"], "sha256": item["sha256"], "size": item["size"]}
            for item in step.document["declared_inputs"]
            # The per-invocation nonce marker is authenticated above and must
            # differ between independently captured roles.  It is procedural,
            # not a compiler/link semantic input.  No other declaration is
            # excluded from equality.
            if item["path"] != session_path
        ),
        key=lambda item: item["path"],
    )


def rooted_policy_record(
    root_name: str,
    relative_name: str,
    roots: Mapping[str, RootBinding],
    label: str,
) -> dict[str, Any]:
    relative = safe_relative(relative_name, label)
    rooted_name = "${" + root_name + "}/" + relative.as_posix()
    path = resolve_rooted_path(
        rooted_name,
        roots,
        label,
    )
    return {
        "path": rooted_name,
        "sha256": sha256_file(path),
        "size": path.stat().st_size,
    }


def require_unique_declared_policy_file(
    declared: Sequence[dict[str, Any]],
    expected: dict[str, Any],
    roots: Mapping[str, RootBinding],
    label: str,
) -> dict[str, Any]:
    expected_path = resolve_rooted_path(expected["path"], roots, f"{label} policy file")
    matches: list[dict[str, Any]] = []
    for index, record in enumerate(declared):
        observed_path = verify_file_record(
            record, roots, f"{label} declared input {index}"
        )
        if canonical_file_paths_match(observed_path, expected_path, label):
            matches.append(record)
    if not matches:
        raise GateError(f"{label} is not predeclared")
    if len(matches) != 1:
        raise GateError(f"{label} has duplicate rooted aliases in declared inputs")
    observed = matches[0]
    if any(observed[field] != expected[field] for field in ("sha256", "size")):
        raise GateError(f"{label} declared input differs from its policy file")
    return observed


def validate_wrapped_assembly(
    step: StepView,
    unit: dict[str, Any],
    roots: Mapping[str, RootBinding],
    prepared: dict[str, Any],
    tools: Mapping[str, dict[str, Any]],
    replayed_manifests: dict[str, str],
    label: str,
) -> dict[str, Any]:
    generator = unit["generator"]
    expected_records = {
        "manifest": rooted_policy_record(
            generator["manifest_root"], generator["manifest"], roots, f"{label} manifest"
        ),
        "generator": rooted_policy_record(
            generator["tool_root"], generator["tool"], roots, f"{label} generator"
        ),
        "wrapper": rooted_policy_record(
            generator["wrapper_root"], generator["wrapper"], roots, f"{label} wrapper"
        ),
        "prepared_metadata": rooted_policy_record(
            "PREPARED", ".mos-agondev-worktree.json", roots, f"{label} prepared metadata"
        ),
    }
    declared = step.document["declared_inputs"]
    for name, record in expected_records.items():
        require_unique_declared_policy_file(
            declared, record, roots, f"{label} {name}"
        )
    build_tool = roots[generator["tool_root"]].resolved
    generator_path = resolve_rooted_path(expected_records["generator"]["path"], roots, f"{label} generator")
    wrapper_path = resolve_rooted_path(expected_records["wrapper"]["path"], roots, f"{label} wrapper")
    verify_tracked_file(build_tool, generator_path, f"{label} generator")
    verify_tracked_file(build_tool, wrapper_path, f"{label} wrapper")

    manifest_path = resolve_rooted_path(
        expected_records["manifest"]["path"], roots, f"{label} manifest"
    )
    manifest = require_object(load_json(manifest_path, f"{label} manifest"), f"{label} manifest")
    require_exact_keys(
        manifest,
        (
            "anonymous_label_strategy",
            "files",
            "input_identity",
            "input_provenance",
            "macros",
            "schema",
        ),
        f"{label} manifest",
    )
    if (
        require_exact_integer(manifest["schema"], f"{label} manifest schema")
        != generator["manifest_schema"]
    ):
        raise GateError(f"{label} generator manifest schema differs from policy")
    provenance = require_object(manifest["input_provenance"], f"{label} manifest provenance")
    require_exact_keys(
        provenance,
        (
            "metadata",
            "metadata_sha256",
            "prepared_file_count",
            "source_head",
            "tracked_dirty",
        ),
        f"{label} manifest provenance",
    )
    require_exact_integer(
        provenance["prepared_file_count"],
        f"{label} manifest prepared_file_count",
        minimum=0,
    )
    if provenance != {
        "metadata": ".mos-agondev-worktree.json",
        "metadata_sha256": prepared["metadata_sha256"],
        "prepared_file_count": prepared["file_count"],
        "source_head": prepared["source_commit"],
        "tracked_dirty": False,
    } or manifest["input_identity"] != prepared["source_commit"]:
        raise GateError(f"{label} generator manifest is not bound to prepared source")
    files = manifest["files"]
    if not isinstance(files, list):
        raise GateError(f"{label} generator manifest files are malformed")
    outputs: list[str] = []
    for index, entry in enumerate(files):
        entry = require_object(entry, f"{label} manifest file {index}")
        output_name = safe_relative(entry.get("output"), f"{label} manifest output")
        outputs.append(output_name.as_posix())
    if len(outputs) != len(set(outputs)):
        raise GateError(f"{label} generator manifest has duplicate outputs")
    generated_prefix = safe_relative(generator["manifest"], f"{label} manifest").parent
    generated_source = safe_relative(unit["source"], f"{label} generated source")
    try:
        manifest_output = generated_source.relative_to(generated_prefix).as_posix()
    except ValueError as error:
        raise GateError(f"{label} generated source is outside its manifest tree") from error
    matches = [entry for entry in files if entry.get("output") == manifest_output]
    if len(matches) != 1:
        raise GateError(f"{label} generated source is absent or ambiguous in manifest")
    entry = matches[0]
    maintained_name = safe_relative(unit["maintained_source"], f"{label} maintained source")
    maintained_path = regular_file(
        roots[unit["maintained_source_root"]].lexical.joinpath(*maintained_name.parts),
        f"{label} maintained source",
        root=roots[unit["maintained_source_root"]].lexical,
    )
    maintained_digest = sha256_generator_text_input(
        maintained_path, f"{label} maintained source"
    )
    if (
        entry.get("source") != maintained_name.as_posix()
        or entry.get("source_sha256") != maintained_digest
        or entry.get("output_sha256") != step.document["source"]["sha256"]
    ):
        raise GateError(f"{label} generated/maintained source hashes do not match manifest")
    source_files = entry.get("source_files")
    if not isinstance(source_files, list) or not source_files:
        raise GateError(f"{label} manifest has no maintained source closure")
    source_names: set[str] = set()
    for index, source_record in enumerate(source_files):
        source_record = require_object(source_record, f"{label} source closure {index}")
        require_exact_keys(source_record, ("sha256", "source"), f"{label} source closure {index}")
        source_name = safe_relative(source_record["source"], f"{label} source closure name")
        if source_name.as_posix() in source_names:
            raise GateError(f"{label} manifest source closure has a duplicate")
        source_names.add(source_name.as_posix())
        source_path = regular_file(
            roots[unit["maintained_source_root"]].lexical.joinpath(*source_name.parts),
            f"{label} source closure file",
            root=roots[unit["maintained_source_root"]].lexical,
        )
        if sha256_generator_text_input(
            source_path, f"{label} source closure file"
        ) != require_sha256(
            source_record["sha256"], f"{label} source closure digest"
        ):
            raise GateError(f"{label} manifest source closure is stale")
    if maintained_name.as_posix() not in source_names:
        raise GateError(f"{label} manifest source closure omits the maintained source")

    manifest_key = expected_records["manifest"]["path"]
    if manifest_key not in replayed_manifests:
        environment = step.document["environment"]["variables"]
        with tempfile.TemporaryDirectory(prefix="port008-zds2gas-") as directory:
            replay_root = Path(directory) / "generated"
            run_checked(
                (
                    os.fspath(tools["python"]["resolved"]),
                    "-B",
                    os.fspath(generator_path),
                    "tree",
                    os.fspath(roots["PREPARED"].resolved),
                    os.fspath(replay_root),
                ),
                environment=environment,
                timeout=120,
            )
            replay_manifest = regular_file(replay_root / "manifest.json", f"{label} replay manifest")
            if replay_manifest.read_bytes() != manifest_path.read_bytes():
                raise GateError(f"{label} generator replay differs from captured manifest")
            replay_source = regular_file(
                replay_root.joinpath(*PurePosixPath(manifest_output).parts),
                f"{label} replay generated source",
            )
            if sha256_file(replay_source) != step.document["source"]["sha256"]:
                raise GateError(f"{label} generator replay differs from assembled source")
        replayed_manifests[manifest_key] = sha256_file(manifest_path)
    return {
        "maintained_source": maintained_name.as_posix(),
        "maintained_source_sha256": maintained_digest,
        "manifest_sha256": replayed_manifests[manifest_key],
        "generator_replay_proved": True,
    }


def nm_symbols(tool: Path, path: Path, label: str) -> dict[str, list[dict[str, Any]]]:
    completed = run_checked(
        (os.fspath(tool), "-P", "--defined-only", "--print-size", os.fspath(path))
    )
    result: dict[str, list[dict[str, Any]]] = {}
    for line in os.fsdecode(completed.stdout).splitlines():
        fields = line.split()
        if len(fields) not in (3, 4):
            continue
        name, symbol_type, value = fields[:3]
        if len(symbol_type) != 1:
            raise GateError(f"{label} has malformed symbol type for {name!r}")
        try:
            address = int(value, 16)
            size = int(fields[3], 16) if len(fields) == 4 else None
        except ValueError as error:
            raise GateError(f"{label} has malformed nm row: {line!r}") from error
        result.setdefault(name, []).append(
            {"name": name, "type": symbol_type, "address": address, "size": size}
        )
    if not result:
        raise GateError(f"{label} has no defined symbols")
    return result


def select_symbol(
    table: Mapping[str, list[dict[str, Any]]], specification: dict[str, Any], label: str
) -> dict[str, Any]:
    records = table.get(specification["name"], [])
    if len(records) != 1:
        raise GateError(
            f"{label} symbol {specification['name']} occurs {len(records)} times"
        )
    record = records[0]
    if record["type"] not in specification["types"]:
        raise GateError(
            f"{label} symbol {specification['name']} has type {record['type']}"
        )
    return {key: record[key] for key in ("name", "type", "size")}


def normalize_instruction(text: str) -> str:
    normalized = " ".join(text.split())
    return re.sub(
        r"(?<![A-Za-z0-9_])(?:0x)?[0-9a-fA-F]+\s*<([^>]+)>",
        r"<\1>",
        normalized,
    )


def normalized_disassembly(
    tool: Path, image: Path, symbol: str, label: str, *, relocations: bool
) -> dict[str, Any]:
    argv = [os.fspath(tool), "-d"]
    if relocations:
        argv.append("-r")
    argv.extend(("--no-show-raw-insn", f"--disassemble={symbol}", os.fspath(image)))
    output = os.fsdecode(run_checked(argv).stdout).splitlines()
    start: int | None = None
    instructions: list[dict[str, Any]] = []
    for line in output:
        header = DISASSEMBLY_HEADER.match(line)
        if header is not None:
            if header.group(2) == symbol:
                start = int(header.group(1), 16)
                continue
            if start is not None:
                break
        if start is None:
            continue
        instruction = DISASSEMBLY_LINE.match(line)
        if instruction is None:
            continue
        address = int(instruction.group(1), 16)
        if address < start:
            raise GateError(f"{label} disassembly address precedes {symbol}")
        instructions.append(
            {
                "offset": address - start,
                "text": normalize_instruction(instruction.group(2)),
            }
        )
    if start is None or not instructions:
        raise GateError(f"{label} has no disassembly for {symbol}")
    return {"symbol": symbol, "instructions": instructions}


def resolve_ez80_imm24_relocation(
    expression: str,
    section_contributions: Sequence[dict[str, Any]],
    linked_symbols: Mapping[str, list[dict[str, Any]]],
    label: str,
) -> int:
    """Resolve the exact r_imm24 expression using map and final-symbol authority."""

    match = RELOCATION_TARGET.fullmatch(expression)
    if match is None:
        raise GateError(f"{label} has an unsupported relocation target {expression!r}")
    target, addend_text = match.groups()
    addend = int(addend_text, 16) if addend_text is not None else 0
    if target.startswith("."):
        matches = [
            contribution
            for contribution in section_contributions
            if contribution["section"] == target and contribution["size"] > 0
        ]
        if len(matches) != 1:
            raise GateError(
                f"{label} section target {target!r} has {len(matches)} map contributions"
            )
        contribution = matches[0]
        if addend >= contribution["size"]:
            raise GateError(f"{label} section relocation addend is out of range")
        value = contribution["address"] + addend
    else:
        matches = linked_symbols.get(target, [])
        if len(matches) != 1:
            raise GateError(
                f"{label} symbol target {target!r} occurs {len(matches)} times"
            )
        value = matches[0]["address"] + addend
    if not 0 <= value <= 0xFFFFFF:
        raise GateError(f"{label} relocation value is outside the eZ80 ADL address space")
    return value


def objdump_section_table(tool: Path, image: Path, label: str) -> dict[str, dict[str, Any]]:
    output = os.fsdecode(
        run_checked((os.fspath(tool), "-h", os.fspath(image))).stdout
    ).splitlines()
    sections: dict[str, dict[str, Any]] = {}
    pending: dict[str, Any] | None = None
    for line in output:
        row = SECTION_TABLE_ROW.match(line)
        if row is not None:
            name, size_text, vma_text = row.groups()
            if name in sections:
                raise GateError(f"{label} has duplicate section {name!r}")
            pending = {
                "name": name,
                "size": int(size_text, 16),
                "vma": int(vma_text, 16),
                "flags": None,
            }
            sections[name] = pending
            continue
        if pending is not None and line.strip():
            flags = tuple(item.strip() for item in line.strip().split(","))
            if not flags or any(not item for item in flags):
                raise GateError(f"{label} section {pending['name']!r} has malformed flags")
            pending["flags"] = flags
            pending = None
    if pending is not None:
        raise GateError(f"{label} section {pending['name']!r} omits flags")
    if not sections or any(section["flags"] is None for section in sections.values()):
        raise GateError(f"{label} has an incomplete section table")
    return sections


def objdump_section_bytes(
    tool: Path,
    image: Path,
    label: str,
    *,
    section: str | None = None,
    start: int | None = None,
    size: int | None = None,
) -> bytes:
    if (section is None) == (start is None or size is None):
        raise GateError(f"{label} byte-range request is malformed")
    argv = [os.fspath(tool), "-s"]
    if section is not None:
        argv.extend(("-j", section))
    else:
        assert start is not None and size is not None
        argv.extend((f"--start-address={start:#x}", f"--stop-address={start + size:#x}"))
    argv.append(os.fspath(image))
    output = os.fsdecode(run_checked(argv).stdout).splitlines()
    observed: dict[int, int] = {}
    for line in output:
        row = SECTION_CONTENT_ROW.match(line)
        if row is None:
            continue
        address_text, chunks_text = row.groups()
        chunks = chunks_text.split()
        if not chunks or any(
            len(chunk) > 8
            or len(chunk) % 2
            or re.fullmatch(r"[0-9a-fA-F]+", chunk) is None
            for chunk in chunks
        ):
            raise GateError(f"{label} has malformed objdump content bytes")
        row_bytes = bytes.fromhex("".join(chunks))
        address = int(address_text, 16)
        for index, value in enumerate(row_bytes):
            byte_address = address + index
            if byte_address in observed:
                raise GateError(f"{label} repeats content address {byte_address:#x}")
            observed[byte_address] = value
    if section is not None:
        if not observed:
            raise GateError(f"{label} has no contents for section {section!r}")
        first = min(observed)
        last = max(observed) + 1
    else:
        assert start is not None and size is not None
        first = start
        last = start + size
        outside = sorted(address for address in observed if not first <= address < last)
        if outside:
            raise GateError(f"{label} objdump returned bytes outside the requested range")
    missing = [address for address in range(first, last) if address not in observed]
    if missing:
        raise GateError(f"{label} content bytes are not contiguous")
    return bytes(observed[address] for address in range(first, last))


def objdump_relocations(
    tool: Path, image: Path, label: str
) -> dict[str, list[dict[str, Any]]]:
    output = os.fsdecode(
        run_checked((os.fspath(tool), "-r", os.fspath(image))).stdout
    ).splitlines()
    result: dict[str, list[dict[str, Any]]] = {}
    current_section: str | None = None
    for line in output:
        header = RELOCATION_SECTION_HEADER.match(line)
        if header is not None:
            current_section = header.group(1)
            if current_section in result:
                raise GateError(f"{label} repeats relocation section {current_section!r}")
            result[current_section] = []
            continue
        relocation = RELOCATION_TABLE_ROW.match(line)
        if relocation is None:
            continue
        if current_section is None:
            raise GateError(f"{label} has a relocation outside a section")
        offset_text, relocation_type, target = relocation.groups()
        result[current_section].append(
            {
                "offset": int(offset_text, 16),
                "type": relocation_type,
                "target": target,
            }
        )
    for section, records in result.items():
        offsets = [record["offset"] for record in records]
        if offsets != sorted(offsets) or len(offsets) != len(set(offsets)):
            raise GateError(f"{label} section {section!r} relocations are unordered or duplicate")
    return result


def normalized_ez80_linked_object(
    tool: Path,
    object_image: Path,
    linked_image: Path,
    section_contributions: Sequence[dict[str, Any]],
    linked_symbols: Mapping[str, list[dict[str, Any]]],
    label: str,
) -> dict[str, Any]:
    """Verify and normalize every allocated contribution from one eZ80 object."""

    section_table = objdump_section_table(tool, object_image, f"{label} object")
    relocations_by_section = objdump_relocations(tool, object_image, f"{label} object")
    relevant_sections = {
        name: section
        for name, section in section_table.items()
        if section["size"] > 0
        and "ALLOC" in section["flags"]
        and not any(name.startswith(prefix) for prefix in NONALLOCATED_SECTION_PREFIXES)
    }
    if not relevant_sections:
        raise GateError(f"{label} object has no allocated sections")
    contributions_by_section: dict[str, list[dict[str, Any]]] = {}
    for contribution in section_contributions:
        contributions_by_section.setdefault(contribution["section"], []).append(contribution)
    normalized_sections: list[dict[str, Any]] = []
    for section_name, section in sorted(relevant_sections.items()):
        if section["vma"] != 0:
            raise GateError(f"{label} section {section_name!r} has unsupported nonzero VMA")
        contributions = [
            contribution
            for contribution in contributions_by_section.get(section_name, [])
            if contribution["size"] > 0
        ]
        if len(contributions) != 1:
            raise GateError(
                f"{label} allocated section {section_name!r} has "
                f"{len(contributions)} map contributions"
            )
        contribution = contributions[0]
        if contribution["size"] != section["size"]:
            raise GateError(f"{label} mapped section size differs from its object")
        relocation_records = relocations_by_section.pop(section_name, [])
        has_contents = "CONTENTS" in section["flags"]
        if not has_contents:
            if relocation_records:
                raise GateError(f"{label} non-content section carries relocations")
            normalized_sections.append(
                {"section": section_name, "size": section["size"], "contents": None, "relocations": []}
            )
            continue
        object_bytes = objdump_section_bytes(
            tool,
            object_image,
            f"{label} object section {section_name}",
            section=section_name,
        )
        if len(object_bytes) != section["size"]:
            raise GateError(f"{label} object section content size differs from its table")
        linked_bytes = objdump_section_bytes(
            tool,
            linked_image,
            f"{label} linked section {section_name}",
            start=contribution["address"],
            size=contribution["size"],
        )
        if len(linked_bytes) != len(object_bytes):
            raise GateError(f"{label} linked contribution size differs from its object")
        masked = bytearray(linked_bytes)
        protected: set[int] = set()
        normalized_relocations: list[dict[str, Any]] = []
        for relocation in relocation_records:
            if relocation["type"] != "r_imm24":
                raise GateError(
                    f"{label} has unsupported relocation type {relocation['type']!r}"
                )
            offset = relocation["offset"]
            width = 3
            positions = set(range(offset, offset + width))
            if offset < 0 or offset + width > len(linked_bytes):
                raise GateError(f"{label} relocation is outside its section")
            if protected & positions:
                raise GateError(f"{label} has overlapping relocations")
            protected.update(positions)
            expected = resolve_ez80_imm24_relocation(
                relocation["target"],
                section_contributions,
                linked_symbols,
                f"{label} {section_name} relocation at {offset}",
            ).to_bytes(width, "little")
            if linked_bytes[offset : offset + width] != expected:
                raise GateError(f"{label} linked relocation bytes are incorrect")
            masked[offset : offset + width] = b"\0" * width
            normalized_relocations.append(relocation)
        for index, (object_byte, linked_byte) in enumerate(
            zip(object_bytes, linked_bytes, strict=True)
        ):
            if index not in protected and object_byte != linked_byte:
                raise GateError(
                    f"{label} linked non-relocation byte differs from its object at "
                    f"{section_name}+{index:#x}"
                )
        normalized_sections.append(
            {
                "section": section_name,
                "size": section["size"],
                "contents": bytes(masked).hex(),
                "relocations": normalized_relocations,
            }
        )
    unknown_relocation_sections = {
        name: records for name, records in relocations_by_section.items() if records
    }
    if unknown_relocation_sections:
        raise GateError(
            f"{label} has relocations outside allocated production sections: "
            f"{sorted(unknown_relocation_sections)}"
        )
    return {"normalization": "ez80-r_imm24-full-allocation-v1", "sections": normalized_sections}


def object_architecture(objdump: Path, path: Path, expected: str, label: str) -> None:
    output = os.fsdecode(run_checked((os.fspath(objdump), "-f", os.fspath(path))).stdout)
    match = ARCHITECTURE_RE.search(output)
    if match is None or match.group(1).strip() != expected:
        observed = match.group(1).strip() if match else None
        raise GateError(f"{label} architecture mismatch: {observed!r} != {expected!r}")


def path_aliases(path: Path, normalized: str, working_directory: Path) -> set[str]:
    aliases = {os.fspath(path), normalized}
    try:
        aliases.add(path.relative_to(working_directory).as_posix())
    except ValueError:
        pass
    return aliases


def map_contribution_and_owners(
    map_path: Path,
    object_path: Path,
    normalized_object: str,
    working_directory: Path,
    symbols: Sequence[dict[str, Any]],
    label: str,
) -> dict[str, Any]:
    text = map_path.read_text(encoding="utf-8", errors="strict")
    aliases = path_aliases(object_path, normalized_object, working_directory)
    load_aliases = {
        line[len("LOAD ") :].strip()
        for line in text.splitlines()
        if line.startswith("LOAD ")
    }
    matched_loads = sorted(aliases & load_aliases)
    if len(matched_loads) != 1:
        raise GateError(f"{label} map has {len(matched_loads)} exact LOAD records")
    marker = "Linker script and memory map"
    if marker not in text:
        raise GateError(f"{label} map lacks the linker memory-map section")
    allocated = 0
    section_contributions: list[dict[str, Any]] = []
    current_owner = False
    symbol_owners: dict[str, int] = {item["map_name"]: 0 for item in symbols}
    for line in text.split(marker, 1)[1].splitlines():
        contribution = MAP_CONTRIBUTION.match(line)
        if contribution is not None:
            section, address_text, size_text, owner = contribution.groups()
            owner = owner.strip()
            current_owner = owner in aliases
            if current_owner:
                address = int(address_text, 16)
                size = int(size_text, 16)
                if section is not None:
                    section_contributions.append(
                        {"section": section, "address": address, "size": size}
                    )
                if (
                    address > 0
                    and size > 0
                    and not any((section or "").startswith(prefix) for prefix in NONALLOCATED_SECTION_PREFIXES)
                ):
                    allocated += size
            continue
        symbol = MAP_SYMBOL.match(line)
        if current_owner and symbol is not None and symbol.group(1) in symbol_owners:
            symbol_owners[symbol.group(1)] += 1
    if allocated <= 0:
        raise GateError(f"{label} has LOAD but no nonzero allocated contribution")
    wrong = {name: count for name, count in symbol_owners.items() if count != 1}
    if wrong:
        raise GateError(f"{label} map symbol ownership is missing or ambiguous: {wrong}")
    return {
        "load_record": matched_loads[0],
        "allocated_bytes": allocated,
        "section_contributions": section_contributions,
    }


def normalized_working_directory(
    value: str, roots: Mapping[str, RootBinding], label: str
) -> Path:
    match = ROOTED_PATH_RE.fullmatch(value)
    if match is None or match.group(1) not in roots:
        raise GateError(f"{label} working directory is malformed")
    root = roots[match.group(1)]
    require_stable_root(root, f"{label} working directory")
    suffix = match.group(2)
    if suffix is None:
        path = root.lexical
    else:
        relative = safe_relative(suffix, f"{label} working-directory suffix")
        path = root.lexical.joinpath(*relative.parts)
    no_symlink_components(path, root.lexical, f"{label} working directory")
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError(f"{label} working directory is unavailable: {path}") from error
    if not resolved.is_dir():
        raise GateError(f"{label} working directory is not a directory")
    if resolved != root.resolved and not resolved.is_relative_to(root.resolved):
        raise GateError(f"{label} working directory escapes its declared root")
    return resolved


def validate_mos_capture(
    build: dict[str, Any],
    target_policy: dict[str, Any],
    evidence_root: Path,
    roots: Mapping[str, RootBinding],
    tools: Mapping[str, dict[str, Any]],
    prepared: dict[str, Any] | None,
) -> dict[str, Any]:
    capture = require_object(build["capture"], "build capture")
    require_exact_keys(capture, ("format", "unit_records", "link_record", "record"), "build capture")
    if capture["format"] != target_policy["capture_format"] or capture["record"] is not None:
        raise GateError("EMOS build capture has the wrong format/record shape")
    role_policy = target_policy["roles"][build["role"]]
    required_units = role_policy["required_units"]
    unit_references = require_object(capture["unit_records"], "unit_records")
    if set(unit_references) != set(required_units):
        raise GateError(
            "unit records differ from policy: "
            f"missing={sorted(set(required_units) - set(unit_references))}, "
            f"unknown={sorted(set(unit_references) - set(required_units))}"
        )
    units_by_id = {item["id"]: item for item in target_policy["units"]}
    steps: dict[str, StepView] = {}
    generator_records: dict[str, dict[str, Any]] = {}
    replayed_manifests: dict[str, str] = {}
    for unit_id in required_units:
        unit = units_by_id[unit_id]
        step = load_mos_step(
            unit_references[unit_id],
            evidence_root,
            roots,
            target_policy["capture_evidence_kind"],
            target_policy["environment_policy"],
            f"unit {unit_id}",
        )
        if step.document["step_kind"] != unit["producer_kind"]:
            raise GateError(f"unit {unit_id} producer kind mismatch")
        expected_source = roots[unit["source_root"]].resolved / unit["source"]
        if step.source_path != expected_source.resolve(strict=True):
            raise GateError(f"unit {unit_id} source path mismatch")
        if normalized_working_directory(
            step.document["working_directory"], roots, f"unit {unit_id}"
        ) != roots["BUILD"].resolved:
            raise GateError(f"unit {unit_id} did not execute at the production BUILD root")
        expected_output = roots["BUILD"].resolved.joinpath(
            *PurePosixPath(unit["object_suffix"].lstrip("/")).parts
        )
        if step.output_path != expected_output.resolve(strict=True):
            raise GateError(f"unit {unit_id} output path mismatch")
        depfile_path = resolve_rooted_path(
            step.document["depfile"]["path"], roots, f"unit {unit_id} depfile"
        )
        if not depfile_path.is_relative_to(roots["BUILD"].resolved):
            raise GateError(f"unit {unit_id} depfile is outside production BUILD")
        expected_tools = (
            ("compiler", "assembler")
            if unit["producer_kind"] == "c-compile"
            else ("python", "assembler")
        )
        executables_match_tools(step, tools, expected_tools, f"unit {unit_id}")
        require_no_response_indirection(step, f"unit {unit_id}")
        validate_mos_driver_selection(
            step,
            roots,
            unit["producer_kind"] == "c-compile",
            f"unit {unit_id}",
        )
        validate_mos_command(step, unit, roots, f"unit {unit_id}")
        if unit["producer_kind"] == "wrapped-assembly":
            if prepared is None:
                raise GateError("wrapped assembly lacks prepared-source authority")
            generator_records[unit_id] = validate_wrapped_assembly(
                step,
                unit,
                roots,
                prepared,
                tools,
                replayed_manifests,
                f"unit {unit_id}",
            )
        steps[unit_id] = step
    link = load_mos_step(
        capture["link_record"],
        evidence_root,
        roots,
        target_policy["capture_evidence_kind"],
        target_policy["environment_policy"],
        "final link",
    )
    if link.document["step_kind"] != "final-link":
        raise GateError("final link record has the wrong step kind")
    require_no_response_indirection(link, "final link")
    executables_match_tools(link, tools, ("linker",), "final link")
    validate_mos_driver_selection(link, roots, False, "final link")
    expected_elf = roots["BUILD"].resolved.joinpath(
        *PurePosixPath(target_policy["final_image_suffix"].lstrip("/")).parts
    ).resolve(strict=True)
    if link.output_path != expected_elf:
        raise GateError("final image path differs from tracked policy")
    link_working = normalized_working_directory(
        link.document["working_directory"], roots, "final link"
    )
    if link_working != roots["BUILD"].resolved:
        raise GateError("final link did not execute at the production BUILD root")
    expected_linker_script = roots["BUILD"].resolved.joinpath(
        *safe_relative(
            target_policy["final_linker_script"], "EMOS final linker script policy"
        ).parts
    ).resolve(strict=True)
    if resolve_rooted_path(
        link.document["source"]["path"], roots, "final linker script"
    ) != expected_linker_script:
        raise GateError("final link does not consume the policy linker script")
    require_command_path_pair(
        link.command, "-o", link.document["output"]["path"], roots, link_working, "final link"
    )
    require_command_path_pair(
        link.command, "-T", link.document["source"]["path"], roots, link_working, "final link"
    )
    require_command_path_pair(
        link.command,
        "--dependency-file",
        link.document["depfile"]["path"],
        roots,
        link_working,
        "final link",
    )
    if not link.document["ordered_link_inputs"]:
        raise GateError("final link record has no ordered inputs")
    ordered_records = link.document["ordered_link_inputs"]
    ordered = {item["path"]: item for item in ordered_records}
    command_positions: list[int] = []
    for item in ordered_records:
        positions = command_path_positions(
            link.command, item["path"], roots, link_working, "final link input"
        )
        if len(positions) != 1:
            raise GateError(f"final link command does not consume {item['path']} exactly once")
        command_positions.append(positions[0])
    if command_positions != sorted(command_positions):
        raise GateError("final link command changes the recorded input order")
    producers = link.document["producer_records"]
    for unit_id, step in steps.items():
        output_record = step.document["output"]
        if ordered.get(output_record["path"]) != output_record:
            raise GateError(f"final link did not consume exact unit {unit_id} output")
        matching = [
            item
            for item in producers
            if item["input"] == output_record["path"]
            and item["record_sha256"] == step.record_sha256
            and item["output_sha256"] == output_record["sha256"]
        ]
        if len(matching) != 1:
            raise GateError(f"final link lacks exact producer chain for {unit_id}")
        producer_path = resolve_rooted_path(
            matching[0]["record"], roots, f"unit {unit_id} producer record"
        )
        if producer_path != step.record_path:
            raise GateError(f"final link producer record path differs for {unit_id}")
    for forbidden_id in role_policy["forbidden_units"]:
        forbidden_suffix = units_by_id[forbidden_id]["object_suffix"]
        if any(item["path"].endswith(forbidden_suffix) for item in ordered_records):
            raise GateError(f"final link consumes role-forbidden unit {forbidden_id}")
    map_records = [
        item for item in link.document["secondary_outputs"] if item["path"].endswith(".map")
    ]
    if len(map_records) != 1:
        raise GateError("final link must produce exactly one map file")
    expected_map = roots["BUILD"].resolved.joinpath(
        *PurePosixPath(target_policy["link_map_suffix"].lstrip("/")).parts
    ).resolve(strict=True)
    if resolve_rooted_path(
        map_records[0]["path"], roots, "final link map"
    ) != expected_map:
        raise GateError("final link map path differs from tracked policy")
    require_command_path_pair(
        link.command, "-Map", map_records[0]["path"], roots, link_working, "final link"
    )
    if link.document["captured_stdout"] is None:
        raise GateError("final link lacks captured linker trace output")
    if (
        link.command.count("--trace") != 1
        or link.document["captured_stdout"]["size"] <= 0
    ):
        raise GateError("final link lacks a nonempty hash-bound --trace diagnostic")
    map_path = verify_file_record(map_records[0], roots, "final link map")
    elf_path = link.output_path
    linked_table = nm_symbols(tools["nm"]["resolved"], elf_path, "final image")
    for forbidden in role_policy["forbidden_symbols"]:
        if forbidden in linked_table:
            raise GateError(f"final image contains role-forbidden symbol {forbidden}")
    identity_binding = validate_mos_identity_binding(build, steps, elf_path)
    working = normalized_working_directory(
        link.document["working_directory"], roots, "final link"
    )
    unit_results: dict[str, Any] = {}
    for unit_id, step in steps.items():
        unit = units_by_id[unit_id]
        object_architecture(
            tools["objdump"]["resolved"],
            step.output_path,
            target_policy["object_architecture"],
            f"unit {unit_id}",
        )
        object_table = nm_symbols(tools["nm"]["resolved"], step.output_path, f"unit {unit_id}")
        object_symbols = [
            select_symbol(object_table, symbol, f"unit {unit_id}")
            for symbol in unit["symbols"]
        ]
        linked_symbols = [
            select_symbol(linked_table, symbol, f"linked unit {unit_id}")
            for symbol in unit["symbols"]
        ]
        map_record = map_contribution_and_owners(
            map_path,
            step.output_path,
            step.document["output"]["path"],
            working,
            unit["symbols"],
            f"unit {unit_id}",
        )
        object_disassembly = [
            normalized_disassembly(
                tools["objdump"]["resolved"],
                step.output_path,
                symbol["name"],
                f"unit {unit_id} object",
                relocations=True,
            )
            for symbol in unit["symbols"]
        ]
        linked_disassembly = normalized_ez80_linked_object(
            tools["objdump"]["resolved"],
            step.output_path,
            elf_path,
            map_record["section_contributions"],
            linked_table,
            f"unit {unit_id} linked image",
        )
        normalized_command = normalize_policy_command(
            step.command, roots, identity_binding
        )
        normalized_driver_selection = normalized_mos_driver_selection(
            step.document["driver_selection"], roots, identity_binding
        )
        command_material = command_policy_material(
            actual_arguments=step.command,
            expanded_arguments=step.command,
            response_files=step.document["response_files"],
            roots=roots,
            identity_binding=identity_binding,
            tool_selection=normalized_driver_selection,
        )
        unit_results[unit_id] = {
            "classification": unit["classification"],
            "source_sha256": step.document["source"]["sha256"],
            "dependencies": normalized_dependencies(step),
            "declared_inputs": normalized_declared_inputs(step),
            "command": normalized_command,
            "command_policy_material": command_material,
            "command_sha256": command_fingerprint(command_material),
            "driver_selection": normalized_driver_selection,
            "environment": step.document["environment"],
            "executables": step.document["executables"],
            "response_files": step.document["response_files"],
            "object_path": step.document["output"]["path"],
            "object_sha256": step.document["output"]["sha256"],
            "object_size": step.document["output"]["size"],
            "object_symbols": object_symbols,
            "linked_symbols": linked_symbols,
            "object_disassembly_sha256": sha256_bytes(canonical_bytes(object_disassembly)),
            "linked_disassembly_sha256": sha256_bytes(canonical_bytes(linked_disassembly)),
            "map": map_record,
            "step_record_sha256": step.record_sha256,
            "generator": generator_records.get(unit_id),
        }
    all_steps = [*steps.values(), link]
    first_recorder = all_steps[0].document["recorder"]
    first_session = all_steps[0].document["session"]
    first_environment = all_steps[0].document["environment"]
    if any(
        not file_records_same_identity(
            step.document["recorder"],
            first_recorder,
            roots,
            "EMOS recorder",
        )
        for step in all_steps[1:]
    ):
        raise GateError("EMOS records were emitted by different recorder bytes")
    if any(
        not file_records_same_identity(
            step.document["session"],
            first_session,
            roots,
            "EMOS session marker",
        )
        for step in all_steps[1:]
    ):
        raise GateError("EMOS records do not share one provenance session")
    if any(step.document["environment"] != first_environment for step in all_steps[1:]):
        raise GateError("EMOS records do not share one exact child environment")
    recorder_policy = require_object(target_policy["recorder"], "EMOS recorder policy")
    require_exact_keys(
        recorder_policy, ("root", "path", "session_path"), "EMOS recorder policy"
    )
    expected_recorder = rooted_policy_record(
        recorder_policy["root"], recorder_policy["path"], roots, "EMOS recorder"
    )
    expected_session = rooted_policy_record(
        "PROVENANCE", recorder_policy["session_path"], roots, "EMOS session marker"
    )
    if not file_records_same_identity(
        first_recorder, expected_recorder, roots, "EMOS recorder authority"
    ) or not file_records_same_identity(
        first_session, expected_session, roots, "EMOS session authority"
    ):
        raise GateError("EMOS recorder/session authority differs from tracked policy")
    verify_tracked_file(
        roots[recorder_policy["root"]].resolved,
        resolve_rooted_path(expected_recorder["path"], roots, "EMOS recorder"),
        "EMOS recorder",
    )
    session_document = require_object(
        load_json(resolve_rooted_path(expected_session["path"], roots, "EMOS session"), "EMOS session"),
        "EMOS session",
    )
    require_exact_keys(
        session_document,
        ("schema_version", "evidence_kind", "fresh_directory_required", "session_id"),
        "EMOS provenance session",
    )
    if (
        require_exact_integer(
            session_document["schema_version"], "EMOS session schema_version"
        )
        != 1
        or session_document["evidence_kind"]
        != "mos-agondev-target-provenance-session"
        or session_document["fresh_directory_required"] is not True
        or not isinstance(session_document["session_id"], str)
        or re.fullmatch(r"[0-9a-f]{32}", session_document["session_id"]) is None
    ):
        raise GateError("EMOS provenance session marker is not canonical")
    normalized_link_command = normalize_policy_command(
        link.command, roots, identity_binding
    )
    normalized_link_driver_selection = normalized_mos_driver_selection(
        link.document["driver_selection"], roots, identity_binding
    )
    link_command_material = command_policy_material(
        actual_arguments=link.command,
        expanded_arguments=link.command,
        response_files=link.document["response_files"],
        roots=roots,
        identity_binding=identity_binding,
        tool_selection=normalized_link_driver_selection,
    )
    return {
        "capture_format": capture["format"],
        "session_id": session_document["session_id"],
        "final_image": {
            "path": link.document["output"]["path"],
            "sha256": link.document["output"]["sha256"],
            "size": link.document["output"]["size"],
            "instance_path_sha256": sha256_bytes(os.fsencode(os.fspath(elf_path))),
        },
        "link_map": map_records[0],
        "linker_trace": {
            **link.document["captured_stdout"],
            "claim_scope": "hash-bound-diagnostic-only",
        },
        "link_record_sha256": link.record_sha256,
        "final_link_command": normalized_link_command,
        "final_link_command_policy_material": link_command_material,
        "final_link_command_sha256": command_fingerprint(link_command_material),
        "identity_binding": identity_binding,
        "units": unit_results,
    }


P4_ARTIFACT_FIELDS = {"path", "size", "sha256", "inode", "mtime_ns", "ctime_ns"}
P4_EVENT_FIELDS = {
    "session_id",
    "sequence",
    "kind",
    "started_time_ns",
    "finished_time_ns",
    "working_directory",
    "execution_policy",
    "shell",
    "command",
    "escaped_arguments",
    "shell_command",
    "argument_boundary_policy",
    "actual_argument_vector",
    "expanded_argument_vector",
    "response_files",
    "dependencies",
    "dependency_scans",
    "input_stability",
    "input_stability_detail",
    "producer_chaining",
    "child_environment",
    "capture_errors",
    "source",
    "output",
    "source_before",
    "source_after",
    "source_stable",
    "output_before",
    "output_after",
    "output_fresh",
    "map_before",
    "map_after",
    "map_fresh",
    "declared_map_paths",
    "driver_identity",
    "exit_status",
    "spawn_exception",
}


def p4_scons_literal_escape(value: str) -> str | None:
    """Reproduce the recorder's pinned SCons Literal escape form."""

    if any(character in value for character in ("\n", "\r", "`")):
        return None
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace('"', '\\"').replace("$", "\\$")
    return f'"{escaped}"'


def p4_ordinary_scons_word(value: str) -> str:
    """Reproduce the recorder's canonical ordinary SCons POSIX word."""

    if "\x00" in value or "\n" in value or "\r" in value:
        raise GateError("P4 decoded SCons argument contains NUL or a newline")
    if value == "" or any(character.isspace() for character in value):
        body = value.replace("\\", "\\\\")
        for character in ('"', "$", "`"):
            body = body.replace(character, "\\" + character)
        return f'"{body}"'
    return "".join(
        "\\" + character if character in P4_UNQUOTED_SHELL_META else character
        for character in value
    )


def decode_p4_scons_word(argument: Any, label: str) -> str:
    """Independently invert one canonical pinned SCons POSIX word.

    This intentionally is not a shell parser.  It accepts exactly the two
    forms implemented by the authenticated recorder, then requires a byte-
    exact round trip through one of those forms.
    """

    if not isinstance(argument, str) or not argument:
        raise GateError(f"{label} is an empty/non-string SCons word")
    if any(character in argument for character in ("\x00", "\n", "\r")):
        raise GateError(f"{label} contains NUL or a newline")
    decoded: list[str] = []
    if argument.startswith('"'):
        if len(argument) < 2 or not argument.endswith('"'):
            raise GateError(f"{label} has an unterminated double quote")
        index = 1
        end = len(argument) - 1
        while index < end:
            character = argument[index]
            if character == "\\":
                index += 1
                if index >= end or argument[index] not in P4_DOUBLE_QUOTE_ESCAPABLE:
                    raise GateError(f"{label} has a noncanonical double-quote escape")
                decoded.append(argument[index])
            elif character in ('"', "$", "`"):
                raise GateError(f"{label} contains live quote/substitution syntax")
            else:
                decoded.append(character)
            index += 1
    else:
        index = 0
        while index < len(argument):
            character = argument[index]
            if character == "\\":
                index += 1
                if index >= len(argument):
                    raise GateError(f"{label} ends with a backslash")
                decoded.append(argument[index])
            elif character in P4_UNQUOTED_SHELL_META:
                raise GateError(f"{label} contains live unquoted shell syntax")
            else:
                decoded.append(character)
            index += 1
    value = "".join(decoded)
    accepted = {p4_ordinary_scons_word(value)}
    literal = p4_scons_literal_escape(value)
    if literal is not None:
        accepted.add(literal)
    if argument not in accepted:
        raise GateError(f"{label} is not a canonical pinned SCons POSIX encoding")
    return value


def decode_p4_response_bytes(data: bytes, label: str) -> tuple[list[str], list[str]]:
    """Decode and byte-round-trip the capture-owned one-line response format."""

    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeError as error:
        raise GateError(f"{label} is not UTF-8") from error
    if not text.endswith("\n") or "\n" in text[:-1] or "\r" in text:
        raise GateError(f"{label} must contain exactly one final newline")
    body = text[:-1]
    if not body:
        raise GateError(f"{label} contains no argument words")
    encoded_words: list[str] = []
    index = 0
    while index < len(body):
        if body[index] == " ":
            raise GateError(f"{label} has an empty/repeated argument boundary")
        start = index
        if body[index] == '"':
            index += 1
            while index < len(body):
                if body[index] == "\\":
                    index += 2
                    continue
                if body[index] == '"':
                    index += 1
                    break
                index += 1
            else:
                raise GateError(f"{label} has an unterminated quoted word")
            if index < len(body) and body[index] != " ":
                raise GateError(f"{label} concatenates text after a quoted word")
        else:
            while index < len(body) and body[index] != " ":
                index += 1
        encoded_words.append(body[start:index])
        if index < len(body):
            index += 1
            if index == len(body):
                raise GateError(f"{label} has a trailing empty argument")
    decoded = [
        decode_p4_scons_word(word, f"{label} word {ordinal}")
        for ordinal, word in enumerate(encoded_words)
    ]
    canonical = " ".join(p4_ordinary_scons_word(value) for value in decoded) + "\n"
    if canonical.encode("utf-8") != data:
        raise GateError(f"{label} does not round-trip through pinned quote-spaces")
    return decoded, encoded_words


def p4_path_under_roots(
    value: Any,
    roots: Mapping[str, RootBinding],
    allowed_roots: Iterable[str],
    label: str,
) -> Path:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise GateError(f"{label} path is malformed")
    path = Path(value)
    if not path.is_absolute() or os.fspath(path) != os.path.abspath(value):
        raise GateError(f"{label} path is not canonical absolute: {value!r}")
    candidates = [
        roots[name]
        for name in allowed_roots
        if path == roots[name].resolved or path.is_relative_to(roots[name].resolved)
    ]
    if not candidates:
        raise GateError(f"{label} is outside policy roots: {value}")
    owner = max(candidates, key=lambda item: len(os.fspath(item.resolved)))
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError(f"{label} is unavailable: {path}: {error}") from error
    if resolved != path:
        raise GateError(f"{label} path is not its resolved canonical path")
    if not owner.allow_symlink:
        no_symlink_components(path, owner.resolved, label)
    return resolved


def p4_canonical_argument_file(value: Any, cwd: Path, label: str) -> Path:
    """Resolve one argv file operand without admitting symlink/path aliases."""

    if not isinstance(value, str) or not value or "\x00" in value:
        raise GateError(f"{label} path operand is malformed")
    candidate = Path(value)
    lexical = candidate if candidate.is_absolute() else cwd / candidate
    try:
        resolved = lexical.resolve(strict=True)
    except (OSError, RuntimeError, ValueError) as error:
        raise GateError(f"{label} path operand is unavailable: {value!r}") from error
    if lexical != resolved:
        raise GateError(f"{label} path operand is not canonical or traverses a symlink")
    if not resolved.is_file():
        raise GateError(f"{label} path operand is not a regular file")
    return resolved


def require_p4_output_argument(
    arguments: Sequence[str], output: Path, cwd: Path, label: str
) -> None:
    """Require the production driver's exact split `-o FILE` grammar."""

    if any(argument.startswith("-o") and argument != "-o" for argument in arguments):
        raise GateError(f"{label} uses an unsupported attached output option")
    positions = [index for index, argument in enumerate(arguments) if argument == "-o"]
    if len(positions) != 1 or positions[0] + 1 >= len(arguments):
        raise GateError(f"{label} must contain exactly one complete -o option")
    observed = p4_canonical_argument_file(
        arguments[positions[0] + 1], cwd, f"{label} output"
    )
    if not canonical_file_paths_match(observed, output, f"{label} output"):
        raise GateError(f"{label} -o path differs from its captured output")


def validate_p4_compile_argument_paths(
    arguments: Sequence[str], source: Path, output: Path, cwd: Path, label: str
) -> None:
    """Bind one C++ source and one object output to the actual compiler argv."""

    if arguments.count("-c") != 1 or "-" in arguments or any(
        argument == "-x" or argument.startswith("-x") for argument in arguments
    ):
        raise GateError(f"{label} does not use the supported single-source compile grammar")
    source_operands: list[Path] = []
    skip_value = False
    for index, argument in enumerate(arguments[1:], 1):
        if skip_value:
            skip_value = False
            continue
        if argument in P4_COMPILE_VALUE_OPTIONS:
            if index + 1 >= len(arguments):
                raise GateError(f"{label} ends with a value-taking compiler option")
            skip_value = True
            continue
        if argument.startswith(("-", "@")):
            continue
        source_operands.append(
            p4_canonical_argument_file(
                argument, cwd, f"{label} source argument {index}"
            )
        )
    if len(source_operands) != 1 or not canonical_file_paths_match(
        source_operands[0], source, f"{label} source"
    ):
        raise GateError(f"{label} must compile exactly its one captured source")
    require_p4_output_argument(arguments, output, cwd, label)
    if any(argument.startswith(P4_MAP_OPTION_PREFIXES) for argument in arguments):
        raise GateError(f"{label} compile argv contains a map-output option")


def validate_p4_link_argument_paths(
    arguments: Sequence[str], output: Path, map_path: Path, cwd: Path, label: str
) -> None:
    """Bind the final ELF and canonical map option to the actual linker argv."""

    require_p4_output_argument(arguments, output, cwd, label)
    map_arguments = [
        argument
        for argument in arguments
        if argument.startswith(P4_MAP_OPTION_PREFIXES)
    ]
    if (
        len(map_arguments) != 1
        or not map_arguments[0].startswith(P4_CANONICAL_MAP_PREFIX)
        or map_arguments[0] == P4_CANONICAL_MAP_PREFIX
    ):
        raise GateError(
            f"{label} must contain exactly one canonical -Wl,-Map=FILE option"
        )
    observed_map = p4_canonical_argument_file(
        map_arguments[0][len(P4_CANONICAL_MAP_PREFIX) :],
        cwd,
        f"{label} map output",
    )
    if not canonical_file_paths_match(observed_map, map_path, f"{label} map output"):
        raise GateError(f"{label} map option differs from its captured map")


def validate_p4_artifact(
    value: Any,
    roots: Mapping[str, RootBinding],
    allowed_roots: Iterable[str],
    label: str,
) -> Path:
    record = require_object(value, label)
    require_exact_keys(record, P4_ARTIFACT_FIELDS, label)
    require_exact_integer(record["size"], f"{label}.size", minimum=0)
    require_exact_integer(record["inode"], f"{label}.inode", minimum=0)
    require_exact_integer(record["mtime_ns"], f"{label}.mtime_ns")
    require_exact_integer(record["ctime_ns"], f"{label}.ctime_ns")
    path = p4_path_under_roots(record["path"], roots, allowed_roots, label)
    if not path.is_file():
        raise GateError(f"{label} is not a regular file")
    metadata = path.stat()
    expected = {
        "path": os.fspath(path),
        "size": metadata.st_size,
        "sha256": sha256_file(path),
        "inode": metadata.st_ino,
        "mtime_ns": metadata.st_mtime_ns,
        "ctime_ns": metadata.st_ctime_ns,
    }
    if record != expected:
        raise GateError(f"{label} no longer matches the captured artifact")
    return path


def validate_p4_runtime_package(
    value: Any,
    *,
    name: str,
    specification: Any,
    roots: Mapping[str, RootBinding],
) -> dict[str, Any]:
    record = require_object(value, f"P4 {name} runtime")
    require_exact_keys(
        record,
        (
            "name",
            "version",
            "package_root",
            "module_relative_path",
            "module_file",
            "excluded_patterns",
            "files",
            "tree_sha256",
        ),
        f"P4 {name} runtime",
    )
    policy = require_object(specification, f"P4 {name} runtime policy")
    require_exact_keys(
        policy,
        ("version", "package_root", "module_relative_path", "tree_sha256"),
        f"P4 {name} runtime policy",
    )
    package_root = expanded_policy_location(
        policy["package_root"], roots, f"P4 {name} package root"
    )
    runtime_owners = [
        roots[root_name]
        for root_name in ("VENV_RUNTIME", "PIO_PACKAGES")
        if package_root == roots[root_name].resolved
        or package_root.is_relative_to(roots[root_name].resolved)
    ]
    if len(runtime_owners) != 1:
        raise GateError(f"P4 {name} package root lacks one runtime authority")
    no_symlink_components(
        package_root, runtime_owners[0].resolved, f"P4 {name} package root"
    )
    try:
        package_root = package_root.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError(f"P4 {name} package root is unavailable") from error
    if not package_root.is_dir():
        raise GateError(f"P4 {name} package root is not a directory")
    if (
        record["name"] != name
        or record["version"] != policy["version"]
        or record["package_root"] != os.fspath(package_root)
        or record["module_relative_path"] != policy["module_relative_path"]
        or record["excluded_patterns"] != []
        or record["tree_sha256"] != policy["tree_sha256"]
    ):
        raise GateError(f"P4 {name} runtime differs from tracked policy")
    files = require_object(record["files"], f"P4 {name} runtime files")
    observed_names: list[str] = []
    for path in sorted(package_root.rglob("*")):
        metadata = path.lstat()
        if stat.S_ISLNK(metadata.st_mode):
            raise GateError(f"P4 {name} package contains a symbolic link: {path}")
        if stat.S_ISDIR(metadata.st_mode):
            continue
        if not stat.S_ISREG(metadata.st_mode):
            raise GateError(f"P4 {name} package contains a non-regular member: {path}")
        relative = path.relative_to(package_root)
        observed_names.append(relative.as_posix())
    if list(files) != observed_names:
        raise GateError(f"P4 {name} runtime file set/order differs from live package")
    digest_input: list[dict[str, Any]] = []
    for relative_name, artifact in files.items():
        relative = safe_relative(relative_name, f"P4 {name} runtime file")
        path = validate_p4_artifact(
            artifact,
            roots,
            ("VENV_RUNTIME", "PIO_PACKAGES"),
            f"P4 {name} runtime file {relative_name}",
        )
        if path != package_root.joinpath(*relative.parts):
            raise GateError(f"P4 {name} runtime file path differs from package key")
        digest_input.append(
            {
                "path": relative_name,
                "size": artifact["size"],
                "sha256": artifact["sha256"],
            }
        )
    observed_tree = sha256_bytes(
        json.dumps(digest_input, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )
    if observed_tree != require_sha256(record["tree_sha256"], f"P4 {name} tree"):
        raise GateError(f"P4 {name} runtime tree digest is not reproducible")
    module_relative = safe_relative(
        record["module_relative_path"], f"P4 {name} module relative path"
    ).as_posix()
    if record["module_file"] != files.get(module_relative):
        raise GateError(f"P4 {name} module file is not bound to its package tree")
    return {
        "name": name,
        "version": record["version"],
        "tree_sha256": observed_tree,
        "file_count": len(files),
    }


def validate_p4_capture_runtime(
    value: Any,
    target_policy: dict[str, Any],
    roots: Mapping[str, RootBinding],
    tools: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    capture = require_object(value, "P4 capture runtime")
    require_exact_keys(
        capture, ("input_stability", "before", "after"), "P4 capture runtime"
    )
    if (
        capture["input_stability"] != "verified-before-and-after"
        or capture["before"] != capture["after"]
    ):
        raise GateError("P4 capture runtime was not stable before and after capture")
    runtime = require_object(capture["before"], "P4 capture runtime before")
    require_exact_keys(
        runtime,
        ("policy", "launcher", "python", "platformio", "scons"),
        "P4 capture runtime before",
    )
    if runtime["policy"] != "capture-runtime-file-set-v1":
        raise GateError("P4 capture runtime policy is unsupported")
    policy = require_object(target_policy["capture_runtime_policy"], "P4 runtime policy")
    require_exact_keys(
        policy,
        (
            "python_invoked_path",
            "python_tool",
            "launcher_path",
            "launcher_sha256",
            "implementation",
            "version",
            "version_info",
            "platformio",
            "scons",
        ),
        "P4 runtime policy",
    )
    python = require_object(runtime["python"], "P4 capture Python")
    require_exact_keys(
        python,
        (
            "invoked_path",
            "executable",
            "implementation",
            "version",
            "version_info",
            "bytecode_writes_disabled",
        ),
        "P4 capture Python",
    )
    python_tool = tools.get(policy["python_tool"])
    if python_tool is None:
        raise GateError("P4 capture Python policy names an unknown tool")
    invoked = expanded_policy_location(
        policy["python_invoked_path"], roots, "P4 invoked Python"
    )
    try:
        invoked_resolved = invoked.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError("P4 invoked Python path is unavailable") from error
    if (
        python["invoked_path"] != os.fspath(invoked)
        or invoked_resolved != python_tool["resolved"]
        or python["implementation"] != policy["implementation"]
        or python["version"] != policy["version"]
        or python["version_info"] != policy["version_info"]
        or python["bytecode_writes_disabled"] is not True
    ):
        raise GateError("P4 capture Python identity differs from tracked policy")
    executable = validate_p4_artifact(
        python["executable"], roots, ("PYTHON_RUNTIME",), "P4 capture Python executable"
    )
    if (
        executable != python_tool["resolved"]
        or python["executable"]["sha256"] != python_tool["sha256"]
        or python["executable"]["size"] != python_tool["size"]
    ):
        raise GateError("P4 capture Python bytes differ from policy tool")
    launcher = require_object(runtime["launcher"], "P4 capture launcher")
    require_exact_keys(
        launcher, ("invoked_path", "artifact"), "P4 capture launcher"
    )
    launcher_path = expanded_policy_location(
        policy["launcher_path"], roots, "P4 capture launcher policy"
    ).resolve(strict=True)
    launcher_artifact = validate_p4_artifact(
        launcher["artifact"],
        roots,
        ("VENV_RUNTIME", "PIO_PACKAGES"),
        "P4 capture launcher artifact",
    )
    if (
        launcher["invoked_path"] != os.fspath(launcher_path)
        or launcher_artifact != launcher_path
        or launcher["artifact"]["sha256"]
        != require_sha256(policy["launcher_sha256"], "P4 capture launcher policy digest")
    ):
        raise GateError("P4 capture launcher differs from tracked policy")
    packages = [
        validate_p4_runtime_package(
            runtime[name], name=name, specification=policy[name], roots=roots
        )
        for name in ("platformio", "scons")
    ]
    return {
        "policy": runtime["policy"],
        "python_sha256": python["executable"]["sha256"],
        "python_version": python["version"],
        "packages": packages,
    }


def validate_p4_probe(
    value: Any,
    expected_arguments: Sequence[str],
    environment: Mapping[str, str],
    cwd: Path,
    label: str,
) -> None:
    probe = require_object(value, label)
    require_exact_keys(
        probe,
        ("arguments", "exit_status", "output_utf8", "output_truncated"),
        label,
    )
    if (
        probe["arguments"] != list(expected_arguments)
        or require_exact_integer(probe["exit_status"], f"{label} exit_status") != 0
    ):
        raise GateError(f"{label} arguments/status differ from policy")
    if probe["output_truncated"] is not False or not isinstance(probe["output_utf8"], str):
        raise GateError(f"{label} output is incomplete")
    observed = run_combined(expected_arguments, cwd=cwd, environment=environment)
    if observed.decode("utf-8", errors="replace") != probe["output_utf8"]:
        raise GateError(f"{label} output is not reproducible")


def validate_p4_driver_identity(
    value: Any,
    *,
    role: str,
    event: dict[str, Any],
    roots: Mapping[str, RootBinding],
    tools: Mapping[str, dict[str, Any]],
    target_machine: str,
    assembler_selector_arguments: Sequence[str],
    label: str,
) -> dict[str, Any]:
    identity = require_object(value, label)
    expected_keys = {
        "invoked",
        "resolved_path",
        "sha256",
        "size",
        "version_probe",
        "target_probe",
        "compiler_subtools" if role == "compile" else "link_subtools",
    }
    if role == "link":
        expected_keys.add("linker")
    require_exact_keys(identity, expected_keys, label)
    driver_tool = tools["compiler" if role == "compile" else "link_driver"]
    if (
        identity["invoked"] != event["command"]
        or identity["invoked"] != event["expanded_argument_vector"][0]
        or Path(identity["resolved_path"]) != driver_tool["resolved"]
        or identity["sha256"] != driver_tool["sha256"]
        or identity["size"] != driver_tool["size"]
    ):
        raise GateError(f"{label} is not the policy compiler driver")
    environment = event["child_environment"]["variables"]
    cwd = p4_path_under_roots(event["working_directory"], roots, ("PROJECT",), label)
    if not cwd.is_dir():
        raise GateError(f"{label} working directory is not a directory")
    driver = os.fspath(driver_tool["resolved"])
    validate_p4_probe(identity["version_probe"], (driver, "--version"), environment, cwd, f"{label} version")
    validate_p4_probe(identity["target_probe"], (driver, "-dumpmachine"), environment, cwd, f"{label} target")
    if identity["target_probe"]["output_utf8"].strip() != target_machine:
        raise GateError(f"{label} target machine differs from policy")
    dependency_before = require_object(event["dependencies"]["before"], f"{label} dependencies")
    expected_driver_artifact = dependency_before.get(identity["resolved_path"])
    validate_p4_artifact(expected_driver_artifact, roots, ("TOOLCHAIN",), f"{label} executable")
    if expected_driver_artifact["sha256"] != identity["sha256"]:
        raise GateError(f"{label} executable dependency does not match identity")

    subtool_field = "compiler_subtools" if role == "compile" else "link_subtools"
    expected_subtools = (
        {"cc1plus": "cc1plus", "as": "assembler"}
        if role == "compile"
        else {"collect2": "collect2", "ld": "linker"}
    )
    subtools = require_object(identity[subtool_field], f"{label} subtools")
    if set(subtools) != set(expected_subtools):
        raise GateError(f"{label} selected-subtool set differs from policy")
    for program_name, tool_name in expected_subtools.items():
        record = require_object(subtools[program_name], f"{label} {program_name}")
        record_fields = {
            "program_name",
            "selection_probe",
            "invoked",
            "resolved_path",
            "sha256",
            "size",
            "version_probe",
        }
        if role == "compile" and program_name == "as":
            record_fields.add("dispatcher_backend")
        require_exact_keys(
            record,
            record_fields,
            f"{label} {program_name}",
        )
        tool = tools[tool_name]
        if (
            record["program_name"] != program_name
            or Path(record["resolved_path"]) != tool["resolved"]
            or record["sha256"] != tool["sha256"]
            or record["size"] != tool["size"]
        ):
            raise GateError(f"{label} selected {program_name} differs from policy")
        validate_p4_probe(
            record["selection_probe"],
            (driver, f"-print-prog-name={program_name}"),
            environment,
            cwd,
            f"{label} {program_name} selection",
        )
        selected = os.fspath(tool["resolved"])
        selected_lines = record["selection_probe"]["output_utf8"].strip().splitlines()
        if len(selected_lines) != 1 or record["invoked"] != selected_lines[0]:
            raise GateError(f"{label} {program_name} selected invocation is ambiguous")
        selected_invoked = Path(record["invoked"])
        if not selected_invoked.is_absolute():
            selected_invoked_text = shutil.which(
                record["invoked"], path=environment.get("PATH")
            )
            if selected_invoked_text is None:
                raise GateError(f"{label} {program_name} selected invocation is unavailable")
            selected_invoked = Path(selected_invoked_text)
        try:
            selected_invoked = selected_invoked.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise GateError(f"{label} {program_name} selected invocation is unavailable") from error
        if selected_invoked != tool["resolved"]:
            raise GateError(f"{label} {program_name} selection does not resolve to policy tool")
        validate_p4_probe(
            record["version_probe"],
            (selected, "--version"),
            environment,
            cwd,
            f"{label} {program_name} version",
        )
        artifact = dependency_before.get(record["resolved_path"])
        validate_p4_artifact(artifact, roots, ("TOOLCHAIN",), f"{label} {program_name} dependency")
        if artifact["sha256"] != record["sha256"]:
            raise GateError(f"{label} selected {program_name} dependency mismatch")
        if role == "compile" and program_name == "as":
            dispatch = require_object(
                record["dispatcher_backend"], f"{label} assembler dispatch"
            )
            require_exact_keys(
                dispatch,
                (
                    "policy",
                    "selector_arguments",
                    "probe_environment",
                    "selection_probe",
                    "executed_argument_vector",
                    "backend",
                ),
                f"{label} assembler dispatch",
            )
            selectors = [
                argument
                for argument in event["expanded_argument_vector"]
                if argument.startswith("-march=")
                or argument.startswith("-mespv-spec=")
            ]
            if any(
                sum(argument.startswith(prefix) for argument in selectors) > 1
                for prefix in ("-march=", "-mespv-spec=")
            ):
                raise GateError(f"{label} has duplicate assembler dispatch selectors")
            if selectors != list(assembler_selector_arguments):
                raise GateError(f"{label} assembler selectors differ from product policy")
            if (
                dispatch["policy"] != "espressif-debug-trace-dispatch-v1"
                or dispatch["selector_arguments"] != selectors
                or dispatch["probe_environment"]
                != {
                    "base": "sanitized-deterministic-v1",
                    "added_variables": {"ESP_DEBUG_TRACE": "1"},
                }
            ):
                raise GateError(f"{label} assembler dispatch policy/selectors differ")
            dispatch_environment = dict(environment)
            dispatch_environment["ESP_DEBUG_TRACE"] = "1"
            dispatch_arguments = (selected, *selectors, "--version")
            validate_p4_probe(
                dispatch["selection_probe"],
                dispatch_arguments,
                dispatch_environment,
                cwd,
                f"{label} assembler dispatch selection",
            )
            execute_lines = [
                line[len("Execute: ") :]
                for line in dispatch["selection_probe"]["output_utf8"].splitlines()
                if line.startswith("Execute: ")
            ]
            if len(execute_lines) != 1:
                raise GateError(f"{label} assembler dispatch selection is ambiguous")
            try:
                executed = json.loads(execute_lines[0])
            except json.JSONDecodeError as error:
                raise GateError(f"{label} assembler dispatch trace is not JSON") from error
            if (
                not isinstance(executed, list)
                or not executed
                or any(not isinstance(item, str) for item in executed)
                or executed[1:] != [*selectors, "--version"]
                or dispatch["executed_argument_vector"] != executed
            ):
                raise GateError(f"{label} assembler dispatch trace arguments differ")
            backend = require_object(dispatch["backend"], f"{label} assembler backend")
            require_exact_keys(
                backend,
                (
                    "invoked",
                    "resolved_path",
                    "sha256",
                    "size",
                    "version_probe",
                ),
                f"{label} assembler backend",
            )
            backend_tool = tools["assembler_backend"]
            if (
                backend["invoked"] != executed[0]
                or Path(backend["resolved_path"]) != backend_tool["resolved"]
                or backend["sha256"] != backend_tool["sha256"]
                or backend["size"] != backend_tool["size"]
            ):
                raise GateError(f"{label} assembler backend differs from policy")
            validate_p4_probe(
                backend["version_probe"],
                (os.fspath(backend_tool["resolved"]), "--version"),
                environment,
                cwd,
                f"{label} assembler backend version",
            )
            backend_artifact = dependency_before.get(backend["resolved_path"])
            validate_p4_artifact(
                backend_artifact,
                roots,
                ("TOOLCHAIN",),
                f"{label} assembler backend dependency",
            )
            if backend_artifact["sha256"] != backend["sha256"]:
                raise GateError(f"{label} assembler backend dependency mismatch")
    if role == "link" and identity["linker"] != subtools["ld"]:
        raise GateError("P4 linker alias differs from selected ld")
    return identity


def validate_p4_response_files(
    event: dict[str, Any],
    evidence_root: Path,
    roots: Mapping[str, RootBinding],
    working_directory: Path,
    label: str,
) -> None:
    responses = event["response_files"]
    if not isinstance(responses, list):
        raise GateError(f"{label} response_files must be an array")
    paths: set[str] = set()
    blobs: set[str] = set()
    references: set[str] = set()
    by_reference: dict[str, dict[str, Any]] = {}
    for index, response in enumerate(responses):
        response = require_object(response, f"{label} response {index}")
        require_exact_keys(
            response,
            (
                "reference",
                "path",
                "size",
                "sha256",
                "saved_blob",
                "before",
                "after",
                "stable_before_and_after",
                "argument_boundary_policy",
                "encoded_argument_words",
                "decoded_argument_vector",
                "byte_round_trip_verified",
            ),
            f"{label} response {index}",
        )
        if (
            response["path"] in paths
            or response["saved_blob"] in blobs
            or response["reference"] in references
        ):
            raise GateError(f"{label} response files are duplicate/ambiguous")
        paths.add(response["path"])
        blobs.add(response["saved_blob"])
        references.add(response["reference"])
        by_reference[response["reference"]] = response
        if (
            not isinstance(response["reference"], str)
            or not response["reference"].startswith("@")
            or len(response["reference"]) == 1
        ):
            raise GateError(f"{label} response reference is malformed")
        referenced_path = Path(response["reference"][1:])
        if not referenced_path.is_absolute():
            referenced_path = working_directory / referenced_path
        try:
            referenced_path = referenced_path.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise GateError(f"{label} response reference is unavailable") from error
        if os.fspath(referenced_path) != response["path"]:
            raise GateError(f"{label} response reference resolves to different bytes")
        before = validate_p4_artifact(
            response["before"], roots, ("PROVENANCE", "BUILD", "SOURCE"), f"{label} response before"
        )
        after = validate_p4_artifact(
            response["after"], roots, ("PROVENANCE", "BUILD", "SOURCE"), f"{label} response after"
        )
        if before != referenced_path or after != referenced_path:
            raise GateError(f"{label} response artifact path differs from its reference")
        if response["before"] != response["after"] or response["stable_before_and_after"] is not True:
            raise GateError(f"{label} response file was not stable")
        blob = evidence_file(evidence_root, response["saved_blob"], f"{label} saved response")
        blob_bytes = blob.read_bytes()
        if b"@" in blob_bytes:
            raise GateError(
                f"{label} response contains unproved nested/tool response indirection"
            )
        require_exact_integer(
            response["size"], f"{label} response {index} size", minimum=0
        )
        if len(blob_bytes) != response["size"] or sha256_bytes(blob_bytes) != response["sha256"]:
            raise GateError(f"{label} saved response bytes differ")
        decoded_arguments, encoded_words = decode_p4_response_bytes(
            blob_bytes, f"{label} saved response"
        )
        if (
            response["argument_boundary_policy"]
            != "pinned-scons-quote-spaces-response-v1"
            or response["encoded_argument_words"] != encoded_words
            or response["decoded_argument_vector"] != decoded_arguments
            or response["byte_round_trip_verified"] is not True
        ):
            raise GateError(f"{label} response boundary/round-trip proof differs")
        if before.stat().st_size != response["size"] or sha256_file(before) != response["sha256"]:
            raise GateError(f"{label} response record differs from live input")

    used: set[str] = set()

    def expand(arguments: Sequence[str]) -> list[str]:
        expanded_arguments: list[str] = []
        for argument in arguments:
            if not argument.startswith("@") or len(argument) == 1:
                expanded_arguments.append(argument)
                continue
            record = by_reference.get(argument)
            if record is None or argument in used:
                raise GateError(f"{label} response reference is absent or reused")
            used.add(argument)
            blob = evidence_file(
                evidence_root, record["saved_blob"], f"{label} saved response"
            )
            words = record["decoded_argument_vector"]
            if any(word.startswith("@") or ",@" in word for word in words):
                raise GateError(f"{label} response contains nested/tool indirection")
            expanded_arguments.extend(words)
        return expanded_arguments

    reconstructed = expand(event["actual_argument_vector"])
    if reconstructed != event["expanded_argument_vector"] or used != references:
        raise GateError(f"{label} expanded argv does not derive from saved response bytes")


def validate_p4_dependency_map(
    value: Any,
    roots: Mapping[str, RootBinding],
    label: str,
) -> dict[str, dict[str, Any]]:
    dependencies = require_object(value, label)
    for path_name, artifact in dependencies.items():
        if not isinstance(path_name, str):
            raise GateError(f"{label} contains a non-string path")
        validate_p4_artifact(
            artifact,
            roots,
            (
                "SOURCE",
                "BUILD",
                "TOOLCHAIN",
                "VENV_RUNTIME",
                "PIO_PACKAGES",
                "PROVENANCE",
            ),
            f"{label} {path_name}",
        )
        if artifact["path"] != path_name:
            raise GateError(f"{label} key differs from artifact path")
    return dependencies


def validate_p4_dependency_scan(
    value: Any,
    roots: Mapping[str, RootBinding],
    phase: str,
    label: str,
) -> dict[str, Any]:
    scan = require_object(value, label)
    require_exact_keys(
        scan,
        (
            "phase",
            "argument_vector",
            "exit_status",
            "output_utf8",
            "output_truncated",
            "depfile",
            "dependencies",
        ),
        label,
    )
    if (
        scan["phase"] != phase
        or require_exact_integer(scan["exit_status"], f"{label} exit_status") != 0
        or scan["output_truncated"] is not False
        or not isinstance(scan["argument_vector"], list)
        or not isinstance(scan["output_utf8"], str)
    ):
        raise GateError(f"{label} is incomplete")
    validate_p4_artifact(scan["depfile"], roots, ("PROVENANCE",), f"{label} depfile")
    validate_p4_dependency_map(scan["dependencies"], roots, f"{label} dependencies")
    return scan


def expected_p4_dependency_scan_arguments(
    arguments: Sequence[str], depfile: Path, output: Path
) -> list[str]:
    """Derive the recorder's preprocessing-only dependency command."""

    filtered: list[str] = []
    dependency_flags = {"-M", "-MM", "-MD", "-MMD", "-MP"}
    dependency_options = {"-MF", "-MT", "-MQ"}
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument == "-c" or argument in dependency_flags:
            index += 1
            continue
        if argument == "-o" or argument in dependency_options:
            if index + 1 >= len(arguments):
                raise GateError("P4 compile has a truncated output/dependency option")
            index += 2
            continue
        if any(
            argument.startswith(prefix) and len(argument) > len(prefix)
            for prefix in dependency_options
        ):
            index += 1
            continue
        filtered.append(argument)
        index += 1
    filtered.extend(("-M", "-MF", os.fspath(depfile), "-MT", os.fspath(output)))
    return filtered


def validate_p4_event(
    event: Any,
    *,
    role: str,
    session_id: str,
    evidence_root: Path,
    roots: Mapping[str, RootBinding],
    target_policy: dict[str, Any],
    tools: Mapping[str, dict[str, Any]],
    label: str,
) -> dict[str, Any]:
    event = require_object(event, label)
    require_exact_keys(event, P4_EVENT_FIELDS, label)
    if event["session_id"] != session_id:
        raise GateError(f"{label} belongs to another session")
    if type(event["sequence"]) is not int or event["sequence"] < 0:
        raise GateError(f"{label} sequence is malformed")
    if (
        type(event["started_time_ns"]) is not int
        or type(event["finished_time_ns"]) is not int
        or event["finished_time_ns"] < event["started_time_ns"]
    ):
        raise GateError(f"{label} timing is malformed")
    expected_kind = "cxx_compile" if role == "compile" else "final_cxx_link"
    if event["kind"] != expected_kind:
        raise GateError(f"{label} has the wrong actual-step kind")
    if (
        require_exact_integer(event["exit_status"], f"{label} exit_status") != 0
        or event["spawn_exception"] is not None
    ):
        raise GateError(f"{label} did not execute successfully")
    if event["capture_errors"] != []:
        raise GateError(f"{label} has command/response capture errors")
    if event["input_stability"] != "verified-before-and-after" or event[
        "input_stability_detail"
    ] != {"verified_before_and_after": True}:
        raise GateError(f"{label} lacks exact before/after input stability")
    environment = validate_environment(
        event["child_environment"],
        target_policy["environment_policy"],
        roots,
        f"{label}.child_environment",
    )
    escaped = event["escaped_arguments"]
    actual = event["actual_argument_vector"]
    expanded = event["expanded_argument_vector"]
    if not all(
        isinstance(value, list) and value and all(isinstance(item, str) and item for item in value)
        for value in (escaped, actual, expanded)
    ):
        raise GateError(f"{label} argument vectors are malformed")
    decoded = [
        decode_p4_scons_word(item, f"{label} escaped argument {index}")
        for index, item in enumerate(escaped)
    ]
    if (
        decoded != actual
        or event["argument_boundary_policy"]
        != "pinned-scons-posix-shell-word-inverse-v1"
    ):
        raise GateError(f"{label} actual argv differs from SCons argument boundaries")
    working_directory = p4_path_under_roots(
        event["working_directory"], roots, ("PROJECT",), f"{label} working directory"
    )
    if working_directory != roots["PROJECT"].resolved or not working_directory.is_dir():
        raise GateError(f"{label} working directory is not the committed project root")
    if (
        event["command"] != actual[0]
        or actual[0] != expanded[0]
        or event["execution_policy"] != "direct-subprocess-no-shell-v1"
        or event["shell"] is not None
    ):
        raise GateError(f"{label} is not a direct no-shell execution bound to argv[0]")
    unproved_options = sorted(
        {
            argument
            for argument in expanded
            if any(
                argument == prefix
                or argument.startswith(prefix + "=")
                or (prefix == "-B" and argument.startswith("-B"))
                for prefix in P4_UNPROVED_NESTED_TOOL_OPTIONS
            )
        }
    )
    if unproved_options:
        raise GateError(
            f"{label} selects an unauthenticated nested tool/plugin: {unproved_options}"
        )
    if event["shell_command"] != " ".join(escaped):
        raise GateError(f"{label} command diagnostic differs from raw arguments")
    for item in [event["shell_command"], *actual, *expanded]:
        if "\x00" in item or "\n" in item or "\r" in item:
            raise GateError(f"{label} contains NUL or newline text")
        reject_reserved_root_placeholder(item, label)
    for item in [*actual, *expanded]:
        if ",@" in item:
            raise GateError(f"{label} contains unproved tool response indirection")
    if any(item.startswith("@") for item in expanded):
        raise GateError(f"{label} expanded argv retains a response-file reference")
    validate_p4_response_files(
        event, evidence_root, roots, working_directory, label
    )
    dependencies = require_object(event["dependencies"], f"{label}.dependencies")
    require_exact_keys(dependencies, ("before", "after"), f"{label}.dependencies")
    before = validate_p4_dependency_map(dependencies["before"], roots, f"{label} dependencies before")
    after = validate_p4_dependency_map(dependencies["after"], roots, f"{label} dependencies after")
    if before != after:
        raise GateError(f"{label} dependencies changed during the actual step")
    scans = require_object(event["dependency_scans"], f"{label}.dependency_scans")
    require_exact_keys(scans, ("before", "after"), f"{label}.dependency_scans")
    if role == "compile":
        scan_before = validate_p4_dependency_scan(
            scans["before"], roots, "before", f"{label} dependency scan before"
        )
        scan_after = validate_p4_dependency_scan(
            scans["after"], roots, "after", f"{label} dependency scan after"
        )
        if scan_before["dependencies"] != scan_after["dependencies"]:
            raise GateError(f"{label} compiler-reported dependencies changed")
        if event["source_before"] != event["source_after"] or event["source_stable"] is not True:
            raise GateError(f"{label} source was not stable")
        source = validate_p4_artifact(
            event["source_before"], roots, ("PROJECT",), f"{label} source"
        )
        if os.fspath(source) != event["source"]:
            raise GateError(f"{label} source path differs from its artifact")
        if event["output_before"] is not None or event["output_fresh"] is not True:
            raise GateError(f"{label} object was not absent before compilation")
        output = validate_p4_artifact(
            event["output_after"], roots, ("BUILD",), f"{label} output"
        )
        if os.fspath(output) != event["output"]:
            raise GateError(f"{label} output path differs from its artifact")
        validate_p4_compile_argument_paths(
            expanded, source, output, working_directory, label
        )
        if event["map_before"] is not None or event["map_after"] is not None or event["map_fresh"] is not False:
            raise GateError(f"{label} compile step has unexpected map claims")
        for phase, scan in (("before", scan_before), ("after", scan_after)):
            scan_depfile = Path(scan["depfile"]["path"])
            expected_scan = expected_p4_dependency_scan_arguments(
                expanded, scan_depfile, output
            )
            if scan["argument_vector"] != expected_scan:
                raise GateError(f"{label} {phase} dependency scan is not derived from actual argv")
            for path_name, artifact in scan["dependencies"].items():
                if dependencies[phase].get(path_name) != artifact:
                    raise GateError(f"{label} {phase} dependency snapshot omits scan input")
        chaining = event["producer_chaining"]
        if not isinstance(chaining, list) or len(chaining) != 1:
            raise GateError(f"{label} source producer chain is incomplete")
        chain = require_object(chaining[0], f"{label} source chain")
        require_exact_keys(
            chain,
            (
                "input_path",
                "producer_kind",
                "producer_output_sha256",
                "consumer_input_sha256",
                "matched",
            ),
            f"{label} source chain",
        )
        if (
            chain.get("input_path") != event["source"]
            or chain.get("producer_kind") != "captured-source-inventory"
            or chain.get("producer_output_sha256") != event["source_before"]["sha256"]
            or chain.get("consumer_input_sha256") != event["source_before"]["sha256"]
            or chain.get("matched") is not True
        ):
            raise GateError(f"{label} source producer chain does not bind the compile")
    else:
        if scans != {"before": None, "after": None}:
            raise GateError(f"{label} final link has unexpected dependency scans")
        if event["output_before"] is not None or event["map_before"] is not None:
            raise GateError(f"{label} final outputs existed before the link")
        if event["output_fresh"] is not True or event["map_fresh"] is not True:
            raise GateError(f"{label} final outputs were not fresh")
        output = validate_p4_artifact(
            event["output_after"], roots, ("BUILD",), f"{label} ELF"
        )
        map_path = validate_p4_artifact(
            event["map_after"], roots, ("BUILD",), f"{label} map"
        )
        if os.fspath(output) != event["output"]:
            raise GateError(f"{label} ELF path differs from its artifact")
        validate_p4_link_argument_paths(
            expanded, output, map_path, working_directory, label
        )
        if event["source"] is not None or event["source_before"] is not None or event["source_after"] is not None:
            raise GateError(f"{label} final link has a false primary-source claim")
        if event["declared_map_paths"] != [os.fspath(map_path)]:
            raise GateError(f"{label} does not declare exactly its captured map")
    validate_p4_driver_identity(
        event["driver_identity"],
        role=role,
        event=event,
        roots=roots,
        tools=tools,
        target_machine=target_policy["target_machine"],
        assembler_selector_arguments=target_policy["assembler_selector_arguments"],
        label=f"{label} driver",
    )
    return event


def p4_expected_objects(
    selection: dict[str, Any], roots: Mapping[str, RootBinding]
) -> dict[str, tuple[Path, Path]]:
    result: dict[str, tuple[Path, Path]] = {}
    for relative_name in selection["project_translation_units"]:
        relative = safe_relative(relative_name, "P4 selected project unit")
        source = regular_file(roots["PROJECT"].resolved.joinpath(*relative.parts), "P4 selected source")
        object_path = roots["BUILD"].resolved.joinpath(*PurePosixPath(relative_name + ".o").parts)
        key = PurePosixPath(relative_name + ".o").as_posix()
        result[key] = (source, object_path)
    for relative_name in selection["vendored_translation_units"]:
        relative = safe_relative(relative_name, "P4 selected vendored unit")
        source = regular_file(roots["PROJECT"].resolved.joinpath(*relative.parts), "P4 selected source")
        key = f"selected-vdp-gl/{source.stem}.o"
        object_path = roots["BUILD"].resolved / key
        if key in result:
            raise GateError(f"P4 selection has a duplicate object path {key}")
        result[key] = (source, object_path)
    return result


def validate_p4_generated_build_files(
    selection: dict[str, Any], roots: Mapping[str, RootBinding]
) -> list[dict[str, Any]]:
    """Reproduce the tracked selector's one ignored CMake boundary."""

    if selection["generated_build_files"] != ["video/CMakeLists.txt"]:
        raise GateError("P4 selection has an unsupported generated-build-file set")
    project = roots["PROJECT"].resolved
    component_sources: list[str] = []
    for relative_name in selection["project_translation_units"]:
        relative = safe_relative(relative_name, "P4 generated CMake source")
        source = regular_file(
            project.joinpath(*relative.parts),
            "P4 generated CMake source",
            root=project,
        )
        component_sources.append(
            Path(os.path.relpath(source, project / "video")).as_posix()
        )
    embedded_text_files: list[str] = []
    for relative_name in selection["embedded_text_files"]:
        relative = safe_relative(relative_name, "P4 generated CMake embedded file")
        source = regular_file(
            project.joinpath(*relative.parts),
            "P4 generated CMake embedded file",
            root=project,
        )
        try:
            embedded_text_files.append(source.relative_to(project / "video").as_posix())
        except ValueError as error:
            raise GateError("P4 embedded text file is outside the video component") from error
    cmake_text = (
        "# Generated by pio/select_sources.py for an allowlisted P4 target.\n"
        "# Hybrid Arduino/ESP-IDF ignores PlatformIO build_src_filter; do not hand-edit.\n"
        "idf_component_register(\n"
        "  SRCS\n"
    )
    cmake_text += "".join(
        f'    "${{CMAKE_CURRENT_LIST_DIR}}/{path}"\n'
        for path in component_sources
    )
    if embedded_text_files:
        cmake_text += "  EMBED_TXTFILES\n"
        cmake_text += "".join(
            f'    "${{CMAKE_CURRENT_LIST_DIR}}/{path}"\n'
            for path in embedded_text_files
        )
    cmake_text += ")\n"
    cmake_text += 'target_compile_options(${COMPONENT_LIB} PRIVATE "-std=gnu++17")\n'
    path = regular_file(
        project / "video/CMakeLists.txt", "P4 generated CMake boundary", root=project
    )
    expected_bytes = cmake_text.encode("utf-8")
    if path.read_bytes() != expected_bytes:
        raise GateError("P4 generated CMake boundary differs from tracked selector/manifest")
    return [
        {
            "path": "${PROJECT}/video/CMakeLists.txt",
            "sha256": sha256_bytes(expected_bytes),
            "size": len(expected_bytes),
            "reproduced_from_tracked_selector": True,
        }
    ]


def validate_p4_local_identity(
    value: Any,
    *,
    build: dict[str, Any],
    selection: dict[str, Any],
    inventory: dict[str, Any],
    compile_events_by_source: Mapping[Path, dict[str, Any]],
    elf_path: Path,
    roots: Mapping[str, RootBinding],
) -> dict[str, Any]:
    identity = require_object(value, "P4 local build identity")
    require_exact_keys(
        identity,
        (
            "consumer",
            "generated_header",
            "generator",
            "artifact",
            "content_utf8",
            "definitions",
            "final_elf_strings",
        ),
        "P4 local build identity",
    )
    selector = require_object(
        selection["translation_unit_local_build_identity"],
        "P4 identity selector",
    )
    require_exact_keys(selector, ("consumer", "generated_header"), "P4 identity selector")
    if (
        identity["consumer"] != selector["consumer"]
        or identity["generated_header"] != selector["generated_header"]
        or identity["generator"] != "pio/build_identity.py"
    ):
        raise GateError("P4 local identity differs from the committed selector/generator")
    header_record = inventory.get(selector["generated_header"])
    if identity["artifact"] != header_record:
        raise GateError("P4 local identity artifact differs from source inventory")
    header_path = validate_p4_artifact(
        header_record, roots, ("PROJECT",), "P4 generated identity header"
    )
    if header_path.read_text(encoding="utf-8", errors="strict") != identity["content_utf8"]:
        raise GateError("P4 generated identity header bytes differ from report")
    marker = "UNVERSIONED-DO-NOT-DEPLOY"
    build_identity = build["identity"]
    expected_values = {
        "AGON_EXTENDER_SOURCE_IDENTITY": build_identity["source_identity"] or marker,
        "AGON_EXTENDER_BUILD_ID": build_identity["build_id"] or marker,
        "AGON_EXTENDER_ARTIFACT_STATUS": build_identity["lifecycle_status"] or marker,
    }
    if build["role"] == "qualification":
        expected_values["AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY"] = (
            build_identity["composition_identity"] or marker
        )
    if identity["definitions"] != expected_values:
        raise GateError("P4 generated identity definitions do not match the build record")
    expected_content = (
        "// Generated by pio/build_identity.py; do not edit.\n"
        "#pragma once\n"
        f'#define AGON_EXTENDER_SOURCE_IDENTITY "{expected_values["AGON_EXTENDER_SOURCE_IDENTITY"]}"\n'
        f'#define AGON_EXTENDER_BUILD_ID "{expected_values["AGON_EXTENDER_BUILD_ID"]}"\n'
        f'#define AGON_EXTENDER_ARTIFACT_STATUS "{expected_values["AGON_EXTENDER_ARTIFACT_STATUS"]}"\n'
    )
    if build["role"] == "qualification":
        expected_content += (
            '#define AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY '
            f'"{expected_values["AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY"]}"\n'
        )
    if identity["content_utf8"] != expected_content:
        raise GateError("P4 generated identity header content is not canonical")
    consumer_path = regular_file(
        roots["PROJECT"].resolved.joinpath(
            *safe_relative(selector["consumer"], "P4 identity consumer").parts
        ),
        "P4 identity consumer",
        root=roots["PROJECT"].resolved,
    )
    consumer_event = compile_events_by_source.get(consumer_path)
    if consumer_event is None:
        raise GateError("P4 identity consumer compile is absent")
    header_key = os.fspath(header_path)
    for source_path, event in compile_events_by_source.items():
        before = event["dependencies"]["before"]
        after = event["dependencies"]["after"]
        if source_path == consumer_path:
            if before.get(header_key) != header_record or after.get(header_key) != header_record:
                raise GateError("P4 boot compile did not consume exact identity header")
        elif header_key in before or header_key in after:
            raise GateError("P4 local identity leaked into a non-boot compile")
        for argument in event["expanded_argument_vector"]:
            if any(name in argument for name in expected_values):
                raise GateError("P4 identity macro leaked into compiler command arguments")
    elf = elf_path.read_bytes()
    strings = require_object(identity["final_elf_strings"], "P4 final identity strings")
    if set(strings) != set(expected_values):
        raise GateError("P4 final identity string set is incomplete")
    for name, expected in expected_values.items():
        string_record = require_object(strings[name], f"P4 final identity {name}")
        require_exact_keys(string_record, ("value", "ascii_occurrences"), f"P4 final identity {name}")
        encoded = expected.encode("ascii", errors="strict")
        occurrences = elf.count(encoded)
        independently_terminated_occurrences = elf.count(encoded + b"\0")
        if (
            string_record != {"value": expected, "ascii_occurrences": occurrences}
            or independently_terminated_occurrences < 1
        ):
            raise GateError(f"P4 final image does not bind {name}")
    marker_present = marker.encode("ascii") in elf
    return {
        "consumer": selector["consumer"],
        "generated_header_sha256": header_record["sha256"],
        "source_identity": build_identity["source_identity"],
        "build_id": build_identity["build_id"],
        "lifecycle_status": build_identity["lifecycle_status"],
        "composition_identity": build_identity["composition_identity"],
        "unversioned_marker_absent": not marker_present,
        "identity_values_bound": not marker_present and all(
            isinstance(build_identity[field], str) and bool(build_identity[field])
            for field in ("source_identity", "build_id", "lifecycle_status")
        )
        and (
            build["role"] == "release"
            or isinstance(build_identity["composition_identity"], str)
            and bool(build_identity["composition_identity"])
        ),
    }


def validate_p4_capture(
    build: dict[str, Any],
    target_policy: dict[str, Any],
    evidence_root: Path,
    roots: Mapping[str, RootBinding],
    tools: Mapping[str, dict[str, Any]],
) -> dict[str, Any]:
    capture = require_object(build["capture"], "build capture")
    require_exact_keys(capture, ("format", "unit_records", "link_record", "record"), "build capture")
    if (
        capture["format"] != target_policy["capture_format"]
        or capture["unit_records"] != {}
        or capture["link_record"] is not None
        or capture["record"] is None
    ):
        raise GateError("P4 build capture has the wrong exact shape")
    selection_name = target_policy["roles"][build["role"]]["source_selection"]
    if selection_name is None:
        raise GateError(
            "P4 release source selection is absent because no production release consumer exists"
        )
    report_path = verify_evidence_reference(capture["record"], evidence_root, "P4 provenance report")
    if report_path != evidence_root / "provenance.json":
        raise GateError("P4 provenance report must be at the evidence-root canonical path")
    report = require_object(load_json(report_path, "P4 provenance report"), "P4 provenance report")
    require_exact_keys(
        report,
        (
            "schema_version",
            "evidence_kind",
            "status",
            "session_id",
            "environment",
            "started_time_ns",
            "completed_time_ns",
            "source_selection",
            "capture_runtime",
            "source_and_build_input_inventory",
            "translation_unit_local_build_identity",
            "capture",
            "artifacts",
            "tools",
            "raw_event_log_sha256",
            "raw_event_lines",
            "checked_claims",
        ),
        "P4 provenance report",
    )
    if (
        report["schema_version"] != "1.0.0"
        or report["evidence_kind"] != target_policy["capture_evidence_kind"]
        or report["status"] != "complete"
        or report["environment"] != "p4-port008-nonrelease-qualification"
    ):
        raise GateError("P4 provenance report schema/status/environment is unsupported")
    session_id = report["session_id"]
    if not isinstance(session_id, str) or re.fullmatch(r"[0-9a-f]{32}", session_id) is None:
        raise GateError("P4 provenance session_id is malformed")
    if (
        type(report["started_time_ns"]) is not int
        or type(report["completed_time_ns"]) is not int
        or report["completed_time_ns"] < report["started_time_ns"]
    ):
        raise GateError("P4 provenance report timing is malformed")
    capture_runtime = validate_p4_capture_runtime(
        report["capture_runtime"], target_policy, roots, tools
    )

    selection_path = regular_file(
        roots["PROJECT"].resolved.joinpath(*safe_relative(selection_name, "P4 selection").parts),
        "P4 source selection",
        root=roots["PROJECT"].resolved,
    )
    verify_tracked_file(roots["SOURCE"].resolved, selection_path, "P4 source selection")
    if report["source_selection"] != {
        "path": os.fspath(selection_path),
        "sha256": sha256_file(selection_path),
    }:
        raise GateError("P4 report does not bind the policy source selection")
    selection = require_object(load_json(selection_path, "P4 source selection"), "P4 source selection")
    require_exact_keys(
        selection,
        (
            "schema_version",
            "environment",
            "diagnostic_status",
            "generated_build_files",
            "translation_unit_local_build_identity",
            "project_translation_units",
            "forbidden_project_translation_units",
            "vendored_translation_units",
            "embedded_text_files",
            "header_defined_official_implementation",
            "excluded_source_families",
        ),
        "P4 source selection",
    )
    if selection["schema_version"] != "1.0.0" or selection["environment"] != report["environment"]:
        raise GateError("P4 source selection schema/environment differs from capture")
    for field in (
        "project_translation_units",
        "vendored_translation_units",
        "embedded_text_files",
        "header_defined_official_implementation",
        "forbidden_project_translation_units",
        "generated_build_files",
        "excluded_source_families",
    ):
        values = selection[field]
        if not isinstance(values, list) or len(values) != len(set(values)) or any(
            not isinstance(item, str) or not item for item in values
        ):
            raise GateError(f"P4 source selection {field} is malformed")
    selected_names = [
        *selection["project_translation_units"],
        *selection["vendored_translation_units"],
        *selection["embedded_text_files"],
        *selection["header_defined_official_implementation"],
    ]
    forbidden_selected = sorted(
        set(selection["forbidden_project_translation_units"]) & set(selected_names)
    )
    excluded_selected = sorted(
        name
        for name in selected_names
        if any(
            fnmatch.fnmatchcase(name, pattern)
            for pattern in selection["excluded_source_families"]
        )
    )
    if forbidden_selected or excluded_selected:
        raise GateError(
            "P4 committed source selection includes a forbidden family: "
            f"forbidden={forbidden_selected}, excluded={excluded_selected}"
        )
    generated_build_files = validate_p4_generated_build_files(selection, roots)
    selector = require_object(
        selection["translation_unit_local_build_identity"], "P4 identity selector"
    )
    require_exact_keys(selector, ("consumer", "generated_header"), "P4 identity selector")

    expected_inventory_names: set[str] = set()
    for field in (
        "project_translation_units",
        "vendored_translation_units",
        "embedded_text_files",
        "header_defined_official_implementation",
    ):
        expected_inventory_names.update(selection[field])
    expected_inventory_names.update(selection["generated_build_files"])
    expected_inventory_names.add(selector["generated_header"])
    expected_inventory_names.add(selection_name)
    expected_inventory_names.update(target_policy["capture_boundary_files"])
    inventory = require_object(
        report["source_and_build_input_inventory"], "P4 source/build inventory"
    )
    if set(inventory) != expected_inventory_names:
        raise GateError(
            "P4 source/build inventory differs from policy selection: "
            f"missing={sorted(expected_inventory_names - set(inventory))}, "
            f"unknown={sorted(set(inventory) - expected_inventory_names)}"
        )
    for relative_name, artifact in inventory.items():
        path = validate_p4_artifact(artifact, roots, ("PROJECT",), f"P4 inventory {relative_name}")
        expected_path = roots["PROJECT"].resolved.joinpath(
            *safe_relative(relative_name, "P4 inventory name").parts
        )
        if path != expected_path:
            raise GateError(f"P4 inventory path differs for {relative_name}")
        if relative_name in selection["generated_build_files"]:
            matching_generated = [
                item
                for item in generated_build_files
                if item["path"] == "${PROJECT}/" + relative_name
            ]
            if len(matching_generated) != 1 or any(
                artifact[field] != matching_generated[0][field]
                for field in ("sha256", "size")
            ):
                raise GateError(
                    f"P4 generated inventory artifact differs from reproduction: {relative_name}"
                )
        elif relative_name != selector["generated_header"]:
            verify_tracked_file(roots["SOURCE"].resolved, path, f"P4 inventory {relative_name}")

    raw_path = regular_file(report_path.parent / "events.jsonl", "P4 raw event log", root=evidence_root)
    if sha256_file(raw_path) != require_sha256(report["raw_event_log_sha256"], "P4 raw event log"):
        raise GateError("P4 raw event log digest differs from final report")
    raw_bytes = raw_path.read_bytes()
    if not raw_bytes or not raw_bytes.endswith(b"\n"):
        raise GateError("P4 raw event log is empty or unterminated")
    raw_events: list[dict[str, Any]] = []
    raw_lines: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw_bytes.splitlines(keepends=True), 1):
        try:
            event = json.loads(line.decode("utf-8", errors="strict"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise GateError(f"P4 raw event line {line_number} is invalid") from error
        event = require_object(event, f"P4 raw event {line_number}")
        if line != (json.dumps(event, sort_keys=True) + "\n").encode("utf-8"):
            raise GateError(f"P4 raw event line {line_number} is not canonical recorder output")
        raw_events.append(event)
        raw_lines.append(
            {
                "line_number": line_number,
                "sequence": event.get("sequence"),
                "size": len(line),
                "sha256": sha256_bytes(line),
            }
        )
    reported_raw_lines = report["raw_event_lines"]
    if not isinstance(reported_raw_lines, list):
        raise GateError("P4 report raw_event_lines must be an array")
    for index, item in enumerate(reported_raw_lines):
        item = require_object(item, f"P4 report raw event line {index}")
        require_exact_keys(
            item,
            ("line_number", "sequence", "size", "sha256"),
            f"P4 report raw event line {index}",
        )
        require_exact_integer(
            item["line_number"], f"P4 report raw event line {index} number", minimum=1
        )
        require_exact_integer(
            item["sequence"], f"P4 report raw event line {index} sequence", minimum=0
        )
        require_exact_integer(
            item["size"], f"P4 report raw event line {index} size", minimum=1
        )
        require_sha256(item["sha256"], f"P4 report raw event line {index} digest")
    if reported_raw_lines != raw_lines:
        raise GateError("P4 report line hashes differ from raw event bytes")
    sequences = [event.get("sequence") for event in raw_events]
    if len(sequences) != len(set(sequences)) or any(
        type(item) is not int or item < 0 for item in sequences
    ):
        raise GateError("P4 raw event sequences are duplicate or malformed")
    if any(event.get("session_id") != session_id for event in raw_events):
        raise GateError("P4 raw event log mixes provenance sessions")

    report_capture = require_object(report["capture"], "P4 report capture")
    require_exact_keys(
        report_capture,
        (
            "all_cxx_compile_steps",
            "required_target_compiles",
            "final_link",
            "firmware_map_direct_loads",
        ),
        "P4 report capture",
    )
    all_compile_events = [event for event in raw_events if event.get("kind") == "cxx_compile"]
    if report_capture["all_cxx_compile_steps"] != all_compile_events:
        raise GateError("P4 report compile events differ from ordered raw event log")
    raw_links = [event for event in raw_events if event.get("kind") == "final_cxx_link"]
    if len(raw_links) != 1 or report_capture["final_link"] != raw_links[0]:
        raise GateError("P4 report final link differs from ordered raw event log")

    expected_objects = p4_expected_objects(selection, roots)
    required_records = report_capture["required_target_compiles"]
    if not isinstance(required_records, list):
        raise GateError("P4 required target compiles must be an array")
    required_by_output: dict[Path, dict[str, Any]] = {}
    for event in required_records:
        if event not in raw_events or not isinstance(event.get("output"), str):
            raise GateError("P4 required compile is not an exact raw event")
        output_path = Path(event["output"])
        if output_path in required_by_output:
            raise GateError("P4 required compile output is duplicated")
        required_by_output[output_path] = event
    expected_paths = {object_path for _source, object_path in expected_objects.values()}
    if set(required_by_output) != expected_paths:
        raise GateError("P4 required compile set differs from committed selection")
    expected_required_order = [
        required_by_output[path] for path in sorted(expected_paths)
    ]
    if required_records != expected_required_order:
        raise GateError("P4 required compile order is not canonical")
    required_sequences = {event.get("sequence") for event in required_records}
    for expected_path, required_event in required_by_output.items():
        matches = [
            event
            for event in all_compile_events
            if event.get("output") == os.fspath(expected_path)
        ]
        if matches != [required_event]:
            raise GateError("P4 selected object has a duplicate/ambiguous producer")
    external_compile_counts: dict[str, int] = {}
    external_project_prefixes = [
        PurePosixPath(value)
        for value in target_policy["external_project_compile_prefixes"]
    ]
    for event in all_compile_events:
        if event.get("sequence") in required_sequences:
            continue
        source_name = event.get("source")
        if not isinstance(source_name, str):
            raise GateError("P4 external C++ compile has no source path")
        external_source = p4_path_under_roots(
            source_name,
            roots,
            ("PROJECT", "PIO_PACKAGES", "BUILD", "TOOLCHAIN"),
            "P4 external C++ compile source",
        )
        if not external_source.is_file():
            raise GateError("P4 external C++ compile source is not a regular file")
        category: str
        if external_source.is_relative_to(roots["PIO_PACKAGES"].resolved):
            category = "pio-packages"
        elif external_source.is_relative_to(roots["BUILD"].resolved):
            category = "generated-build"
        elif external_source.is_relative_to(roots["TOOLCHAIN"].resolved):
            category = "toolchain"
        elif external_source.is_relative_to(roots["PROJECT"].resolved):
            relative = PurePosixPath(
                external_source.relative_to(roots["PROJECT"].resolved).as_posix()
            )
            matching = [
                prefix
                for prefix in external_project_prefixes
                if relative == prefix or relative.is_relative_to(prefix)
            ]
            if len(matching) != 1:
                raise GateError(
                    "P4 actual compile set contains an unselected product source"
                )
            category = f"project-prefix:{matching[0].as_posix()}"
        else:
            raise GateError("P4 external C++ compile source has no policy category")
        external_compile_counts[category] = external_compile_counts.get(category, 0) + 1
    compile_by_source: dict[Path, dict[str, Any]] = {}
    for ordinal, event in enumerate(required_records):
        validate_p4_event(
            event,
            role="compile",
            session_id=session_id,
            evidence_root=evidence_root,
            roots=roots,
            target_policy=target_policy,
            tools=tools,
            label=f"P4 required compile {ordinal}",
        )
        source = Path(event["source"])
        if source in compile_by_source:
            raise GateError("P4 required source is compiled more than once")
        compile_by_source[source] = event
    link_event = validate_p4_event(
        raw_links[0],
        role="link",
        session_id=session_id,
        evidence_root=evidence_root,
        roots=roots,
        target_policy=target_policy,
        tools=tools,
        label="P4 final link",
    )

    artifacts = require_object(report["artifacts"], "P4 report artifacts")
    require_exact_keys(artifacts, ("objects", "elf", "map"), "P4 report artifacts")
    object_records = require_object(artifacts["objects"], "P4 object artifacts")
    if set(object_records) != set(expected_objects):
        raise GateError("P4 object artifact set differs from committed selection")
    for relative, (source, object_path) in expected_objects.items():
        artifact = object_records[relative]
        observed = validate_p4_artifact(artifact, roots, ("BUILD",), f"P4 object {relative}")
        if observed != object_path or artifact != required_by_output[object_path]["output_after"]:
            raise GateError(f"P4 object artifact is not its exact compile output: {relative}")
        if Path(required_by_output[object_path]["source"]) != source:
            raise GateError(f"P4 object source differs from selection: {relative}")
    elf_path = validate_p4_artifact(artifacts["elf"], roots, ("BUILD",), "P4 final ELF")
    map_path = validate_p4_artifact(artifacts["map"], roots, ("BUILD",), "P4 final map")
    if (
        artifacts["elf"] != link_event["output_after"]
        or artifacts["map"] != link_event["map_after"]
        or not os.fspath(elf_path).endswith(target_policy["final_image_suffix"])
        or not os.fspath(map_path).endswith(target_policy["link_map_suffix"])
    ):
        raise GateError("P4 final artifact paths/bytes differ from actual link")

    expanded_link = link_event["expanded_argument_vector"]
    link_chains = link_event["producer_chaining"]
    if not isinstance(link_chains, list) or len(link_chains) != len(expected_paths):
        raise GateError("P4 final link producer chain is incomplete")
    chains_by_input: dict[str, dict[str, Any]] = {}
    for chain in link_chains:
        chain = require_object(chain, "P4 link producer chain")
        require_exact_keys(
            chain,
            (
                "input_path",
                "producer_sequence",
                "producer_output_sha256",
                "consumer_input_sha256",
                "matched",
            ),
            "P4 link producer chain",
        )
        if chain["input_path"] in chains_by_input:
            raise GateError("P4 final link producer input is duplicated")
        require_exact_integer(
            chain["producer_sequence"],
            "P4 link producer chain sequence",
            minimum=0,
        )
        chains_by_input[chain["input_path"]] = chain
    for path in expected_paths:
        event = required_by_output[path]
        chain = chains_by_input.get(os.fspath(path))
        if (
            expanded_link.count(os.fspath(path)) != 1
            or chain is None
            or chain["producer_sequence"] != event["sequence"]
            or chain["producer_output_sha256"] != event["output_after"]["sha256"]
            or chain["consumer_input_sha256"] != event["output_after"]["sha256"]
            or chain["matched"] is not True
        ):
            raise GateError(f"P4 final link does not consume exact producer output {path}")

    map_text = map_path.read_text(encoding="utf-8", errors="strict")
    map_loads = [line[len("LOAD ") :].strip() for line in map_text.splitlines() if line.startswith("LOAD ")]
    if report_capture["firmware_map_direct_loads"] != map_loads:
        raise GateError("P4 report map LOAD list differs from the actual map")
    resolved_loads = [
        (roots["PROJECT"].resolved / value).resolve(strict=False)
        if not Path(value).is_absolute()
        else Path(value).resolve(strict=False)
        for value in map_loads
    ]
    for path in expected_paths:
        if resolved_loads.count(path) != 1:
            raise GateError(f"P4 map does not directly LOAD exact object {path}")

    units_by_id = {item["id"]: item for item in target_policy["units"]}
    role_policy = target_policy["roles"][build["role"]]
    for forbidden_id in role_policy["forbidden_units"]:
        forbidden = units_by_id[forbidden_id]
        forbidden_source = roots[forbidden["source_root"]].resolved / forbidden["source"]
        if forbidden_source in compile_by_source:
            raise GateError(f"P4 capture compiles role-forbidden unit {forbidden_id}")
    for unit_id in role_policy["required_units"]:
        unit = units_by_id[unit_id]
        source = (roots[unit["source_root"]].resolved / unit["source"]).resolve(strict=True)
        if source not in compile_by_source:
            raise GateError(f"P4 capture omits policy unit {unit_id}")

    top_tools = require_object(report["tools"], "P4 report tools")
    require_exact_keys(
        top_tools,
        (
            "compile_drivers",
            "compiler_selected_subtools",
            "link_driver",
            "link_driver_selected_subtools",
            "linker",
        ),
        "P4 report tools",
    )
    unique_drivers: list[dict[str, Any]] = []
    unique_subtools: list[dict[str, Any]] = []
    driver_keys: set[tuple[str, str]] = set()
    subtool_keys: set[tuple[str, str, str]] = set()
    for event in required_records:
        identity = event["driver_identity"]
        driver_key = (identity["resolved_path"], identity["sha256"])
        if driver_key not in driver_keys:
            driver_keys.add(driver_key)
            unique_drivers.append(identity)
        for name, subtool in identity["compiler_subtools"].items():
            key = (name, subtool["resolved_path"], subtool["sha256"])
            if key not in subtool_keys:
                subtool_keys.add(key)
                unique_subtools.append(subtool)
    if (
        top_tools["compile_drivers"] != unique_drivers
        or top_tools["compiler_selected_subtools"] != unique_subtools
        or top_tools["link_driver"] != link_event["driver_identity"]
        or top_tools["link_driver_selected_subtools"] != link_event["driver_identity"]["link_subtools"]
        or top_tools["linker"] != link_event["driver_identity"]["linker"]
    ):
        raise GateError("P4 top-level tool identities differ from raw actual steps")

    identity_binding = validate_p4_local_identity(
        report["translation_unit_local_build_identity"],
        build=build,
        selection=selection,
        inventory=inventory,
        compile_events_by_source=compile_by_source,
        elf_path=elf_path,
        roots=roots,
    )

    session_path = regular_file(report_path.parent / "session.json", "P4 session", root=evidence_root)
    session = require_object(load_json(session_path, "P4 session"), "P4 session")
    require_exact_keys(
        session,
        (
            "schema_version",
            "evidence_kind",
            "status",
            "session_id",
            "environment",
            "started_time_ns",
            "project_root",
            "build_root",
            "completion_report",
            "failure_report",
            "platformio_version",
            "scons_version",
            "python_version",
            "capture_runtime",
            "source_selection",
            "capture_hook",
            "child_environment_policy",
            "completed_time_ns",
            "report_sha256",
        ),
        "P4 session",
    )
    require_exact_integer(
        session["started_time_ns"], "P4 session started_time_ns", minimum=0
    )
    require_exact_integer(
        session["completed_time_ns"], "P4 session completed_time_ns", minimum=0
    )
    hook_path = roots["PROJECT"].resolved / "pio/capture_p4_actual_steps.py"
    expected_session_environment = {
        "allowlist": ["PATH"],
        "forced": {
            "LANG": "C",
            "LC_ALL": "C",
            "TZ": "UTC",
            "TMPDIR": os.fspath(evidence_root / "tmp"),
            "PWD": os.fspath(roots["PROJECT"].resolved),
        },
        "explicitly_cleared_compiler_linker_influence_variables": [
            "C_INCLUDE_PATH",
            "COMPILER_PATH",
            "CPATH",
            "CPLUS_INCLUDE_PATH",
            "GCC_EXEC_PREFIX",
            "LIBRARY_PATH",
            "LD_LIBRARY_PATH",
            "OBJC_INCLUDE_PATH",
            "SDKROOT",
        ],
    }
    if (
        session["schema_version"] != report["schema_version"]
        or session["evidence_kind"] != report["evidence_kind"]
        or session["status"] != "complete"
        or session["session_id"] != session_id
        or session["environment"] != report["environment"]
        or session["started_time_ns"] != report["started_time_ns"]
        or session["completed_time_ns"] != report["completed_time_ns"]
        or session["project_root"] != os.fspath(roots["PROJECT"].resolved)
        or session["build_root"] != os.fspath(roots["BUILD"].resolved)
        or session["completion_report"] != "provenance.json"
        or session["failure_report"] != "failure.json"
        or session["capture_runtime"] != report["capture_runtime"]
        or session["platformio_version"]
        != report["capture_runtime"]["before"]["platformio"]["version"]
        or session["scons_version"]
        != report["capture_runtime"]["before"]["scons"]["version"]
        or session["python_version"]
        != report["capture_runtime"]["before"]["python"]["version"]
        or session["source_selection"] != report["source_selection"]
        or session["capture_hook"] != {"path": os.fspath(hook_path), "sha256": sha256_file(hook_path)}
        or session["child_environment_policy"] != expected_session_environment
        or session["report_sha256"] != sha256_file(report_path)
    ):
        raise GateError("P4 session does not bind the exact completed report/build boundary")

    expected_claims = {
        "actual_scons_compile_steps_observed": True,
        "actual_scons_final_link_step_observed": True,
        "required_objects_fresh_and_hashed": True,
        "final_elf_and_map_fresh_and_hashed": True,
        "required_objects_present_in_link_command": True,
        "required_objects_present_as_direct_map_loads": True,
        "required_policy_unit_final_link_inputs_proved": True,
        "complete_implicit_default_or_library_link_input_closure_proved": False,
        "response_file_bytes_preserved": True,
        "compiler_reported_target_compile_inputs_stable": True,
        "compile_to_final_link_producer_chaining_proved": True,
        "sanitized_recorded_child_environment_proved": True,
        "producer_outputs_absent_before_steps": True,
        "selected_inputs_stable_during_capture": True,
        "build_identity_local_to_boot_compile_proved": True,
        "build_identity_values_present_in_final_elf": True,
        "espidf_cmake_database_used_as_evidence": False,
        "release_object_equivalence_proved": False,
        "independent_complete_transitive_include_closure_proved": False,
        "git_cleanliness_or_commit_proved": False,
        "runtime_or_physical_qualification_proved": False,
    }
    if report["checked_claims"] != expected_claims:
        raise GateError("P4 recorder claim set differs from the gate's exact schema")

    linked_table = nm_symbols(tools["nm"]["resolved"], elf_path, "P4 final image")
    for forbidden in role_policy["forbidden_symbols"]:
        if forbidden in linked_table:
            raise GateError(f"P4 final image contains role-forbidden symbol {forbidden}")
    unit_results: dict[str, Any] = {}
    for unit_id in role_policy["required_units"]:
        unit = units_by_id[unit_id]
        source_path = (roots[unit["source_root"]].resolved / unit["source"]).resolve(strict=True)
        event = compile_by_source[source_path]
        object_path = Path(event["output"])
        if not os.fspath(object_path).endswith(unit["object_suffix"]):
            raise GateError(f"P4 unit {unit_id} object path differs from policy")
        object_architecture(
            tools["objdump"]["resolved"], object_path, target_policy["object_architecture"], f"P4 unit {unit_id}"
        )
        object_table = nm_symbols(tools["nm"]["resolved"], object_path, f"P4 unit {unit_id}")
        object_symbols = [select_symbol(object_table, symbol, f"P4 unit {unit_id}") for symbol in unit["symbols"]]
        linked_symbols = [select_symbol(linked_table, symbol, f"P4 linked unit {unit_id}") for symbol in unit["symbols"]]
        map_record = map_contribution_and_owners(
            map_path,
            object_path,
            normalize_external_text(os.fspath(object_path), roots),
            roots["PROJECT"].resolved,
            unit["symbols"],
            f"P4 unit {unit_id}",
        )
        object_disassembly = [
            normalized_disassembly(
                tools["objdump"]["resolved"], object_path, symbol["name"], f"P4 unit {unit_id} object", relocations=True
            )
            for symbol in unit["symbols"]
        ]
        linked_disassembly = [
            normalized_disassembly(
                tools["objdump"]["resolved"], elf_path, symbol["name"], f"P4 unit {unit_id} linked", relocations=False
            )
            for symbol in unit["symbols"]
        ]
        dependencies = [
            {
                "path": normalize_external_text(path_name, roots),
                "sha256": record["sha256"],
                "size": record["size"],
            }
            for path_name, record in sorted(event["dependencies"]["before"].items())
        ]
        normalized_environment = normalize_external_value(
            event["child_environment"], roots
        )
        normalized_command = normalize_policy_command(
            event["expanded_argument_vector"], roots, identity_binding
        )
        command_material = command_policy_material(
            actual_arguments=event["actual_argument_vector"],
            expanded_arguments=event["expanded_argument_vector"],
            response_files=event["response_files"],
            roots=roots,
            identity_binding=identity_binding,
            tool_selection=event["driver_identity"],
        )
        unit_results[unit_id] = {
            "classification": unit["classification"],
            "source_sha256": event["source_before"]["sha256"],
            "dependencies": dependencies,
            "declared_inputs": dependencies,
            "command": normalized_command,
            "command_policy_material": command_material,
            "command_sha256": command_fingerprint(command_material),
            "driver_selection": command_material["tool_selection"],
            "environment": normalized_environment,
            "executables": {
                "driver_sha256": event["driver_identity"]["sha256"],
                "subtools": {
                    name: record["sha256"]
                    for name, record in event["driver_identity"]["compiler_subtools"].items()
                },
            },
            "response_files": [
                {"path": normalize_external_text(item["path"], roots), "sha256": item["sha256"], "size": item["size"]}
                for item in event["response_files"]
            ],
            "object_path": normalize_external_text(os.fspath(object_path), roots),
            "object_sha256": event["output_after"]["sha256"],
            "object_size": event["output_after"]["size"],
            "object_symbols": object_symbols,
            "linked_symbols": linked_symbols,
            "object_disassembly_sha256": sha256_bytes(canonical_bytes(object_disassembly)),
            "linked_disassembly_sha256": sha256_bytes(canonical_bytes(linked_disassembly)),
            "map": map_record,
            "step_record_sha256": next(
                item["sha256"] for item in raw_lines if item["sequence"] == event["sequence"]
            ),
            "generator": None,
        }
    normalized_link_command = normalize_policy_command(
        link_event["expanded_argument_vector"], roots, identity_binding
    )
    link_command_material = command_policy_material(
        actual_arguments=link_event["actual_argument_vector"],
        expanded_arguments=link_event["expanded_argument_vector"],
        response_files=link_event["response_files"],
        roots=roots,
        identity_binding=identity_binding,
        tool_selection=link_event["driver_identity"],
    )
    return {
        "capture_format": capture["format"],
        "session_id": session_id,
        "final_image": {
            "path": normalize_external_text(os.fspath(elf_path), roots),
            "sha256": artifacts["elf"]["sha256"],
            "size": artifacts["elf"]["size"],
            "instance_path_sha256": sha256_bytes(os.fsencode(os.fspath(elf_path))),
        },
        "link_map": {
            "path": normalize_external_text(os.fspath(map_path), roots),
            "sha256": artifacts["map"]["sha256"],
            "size": artifacts["map"]["size"],
        },
        "link_record_sha256": next(
            item["sha256"] for item in raw_lines if item["sequence"] == link_event["sequence"]
        ),
        "final_link_command": normalized_link_command,
        "final_link_command_policy_material": link_command_material,
        "final_link_command_sha256": command_fingerprint(link_command_material),
        "capture_runtime": capture_runtime,
        "unclaimed_external_compile_steps": {
            "count": sum(external_compile_counts.values()),
            "categories": dict(sorted(external_compile_counts.items())),
            "claim_scope": "classified-only-not-product-authority",
        },
        "generated_build_files": generated_build_files,
        "identity_binding": identity_binding,
        "units": unit_results,
    }


def validate_identity(
    build: dict[str, Any],
    target_policy: dict[str, Any],
    policy: dict[str, Any],
    roots: Mapping[str, RootBinding],
) -> tuple[bool, list[str], dict[str, Any]]:
    identity = require_object(build["identity"], "build identity")
    require_exact_keys(
        identity,
        (
            "artifact_id",
            "variant",
            "source_identity",
            "build_id",
            "lifecycle_status",
            "composition_artifact_id",
            "composition_identity",
        ),
        "build identity",
    )
    blockers: list[str] = []
    registry_spec = policy["identity_registry"]
    registry_root = roots[registry_spec["root"]].resolved
    registry_path = regular_file(
        registry_root / registry_spec["path"], "identity registry", root=registry_root
    )
    verify_tracked_file(registry_root, registry_path, "identity registry")
    try:
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as error:
        raise GateError(f"cannot parse identity registry: {error}") from error
    artifacts = identity_registry_artifacts(registry)
    if identity["artifact_id"] != target_policy["artifact_id"]:
        blockers.append("firmware artifact_id is absent or does not match policy")
    if identity["variant"] != target_policy["variant"]:
        blockers.append("firmware variant is absent or does not match policy")
    artifact = artifacts.get(target_policy["artifact_id"])
    if artifact is None:
        blockers.append("firmware artifact is absent from the authority registry")
    else:
        if artifact.get("kind") != target_policy["artifact_kind"]:
            blockers.append("firmware artifact kind does not match policy")
        variants = artifact.get("variants")
        if not isinstance(variants, list) or target_policy["variant"] not in variants:
            blockers.append("firmware variant is absent from the authority registry")
        if artifact.get("identity_scheme") != "semantic_version":
            blockers.append("firmware identity scheme is not semantic_version")
        if identity["source_identity"] != artifact.get("latest_identity"):
            blockers.append("firmware source identity is not the registry's latest identity")
        if identity["lifecycle_status"] != artifact.get("status"):
            blockers.append("firmware lifecycle status does not match the registry")
        if artifact.get("status") not in registry_spec["eligible_statuses"]:
            blockers.append(f"firmware lifecycle status {artifact.get('status')!r} is ineligible")
    build_id = identity["build_id"]
    if not build_id_matches_source(build_id, identity["source_identity"]):
        blockers.append(
            "build_id is absent, is not derived from the approved source identity, "
            "or lacks a real UTC calendar timestamp"
        )
    role_policy = target_policy["roles"][build["role"]]
    if role_policy["requires_separate_composition_identity"]:
        composition_id = identity["composition_artifact_id"]
        composition_identity = identity["composition_identity"]
        expected_id = role_policy["expected_composition_artifact_id"]
        if composition_id != expected_id:
            blockers.append("qualification composition artifact_id does not match policy")
        composition = artifacts.get(composition_id) if isinstance(composition_id, str) else None
        if composition is None or not isinstance(composition_identity, str):
            blockers.append("qualification composition lacks a separately registered identity")
        elif composition.get("kind") != role_policy["expected_composition_artifact_kind"]:
            blockers.append("qualification composition kind does not match policy")
        elif composition.get("identity_scheme") != "revision":
            blockers.append("qualification composition identity scheme is not revision")
        elif composition_identity != composition.get("latest_identity"):
            blockers.append("qualification composition identity does not match the registry")
        elif composition.get("status") not in registry_spec["eligible_statuses"]:
            blockers.append("qualification composition identity is not candidate/qualified/released")
    elif identity["composition_artifact_id"] is not None or identity["composition_identity"] is not None:
        blockers.append("release build must not claim a qualification composition identity")
    return not blockers, blockers, {
        "registry_sha256": sha256_file(registry_path),
        "artifact_id": identity["artifact_id"],
        "variant": identity["variant"],
        "source_identity": identity["source_identity"],
        "build_id": identity["build_id"],
        "lifecycle_status": identity["lifecycle_status"],
        "composition_artifact_id": identity["composition_artifact_id"],
        "composition_identity": identity["composition_identity"],
    }


BUILD_FIELDS = {
    "schema_version",
    "evidence_kind",
    "policy_sha256",
    "target",
    "role",
    "identity",
    "repositories",
    "capture",
}


def validate_build(
    *,
    policy_path: Path,
    build_path: Path,
    evidence_root: Path,
    root_arguments: Sequence[str],
) -> dict[str, Any]:
    policy_path = regular_file(policy_path, "policy")
    policy = validate_policy(load_json(policy_path, "policy"))
    evidence_root = Path(os.path.abspath(evidence_root))
    no_absolute_symlink_components(evidence_root, "evidence root")
    try:
        evidence_root = evidence_root.resolve(strict=True)
    except (OSError, RuntimeError) as error:
        raise GateError(f"evidence root is unavailable: {error}") from error
    if not evidence_root.is_dir():
        raise GateError("evidence root is not a directory")
    build_path = regular_file(build_path, "build record", root=evidence_root)
    build = require_object(load_json(build_path, "build record"), "build record")
    require_exact_keys(build, BUILD_FIELDS, "build record")
    if (
        require_exact_integer(build["schema_version"], "build record schema_version")
        != BUILD_SCHEMA
        or build["evidence_kind"] != BUILD_KIND
    ):
        raise GateError("unsupported build-record schema/kind")
    if build["target"] not in policy["targets"] or build["role"] not in {
        "qualification",
        "release",
    }:
        raise GateError("build record has an unsupported target or role")
    target_policy = policy["targets"][build["target"]]
    roots = parse_root_arguments(root_arguments, target_policy)
    if build["target"] == "p4":
        root_relations = (
            ("PROJECT", "SOURCE", "project_relative"),
            ("VENV_RUNTIME", "SOURCE", "venv_relative"),
            ("PIO_PACKAGES", "PROJECT", "pio_packages_relative"),
            ("TOOLCHAIN", "PIO_PACKAGES", "toolchain_package_relative"),
        )
        for child_name, parent_name, policy_field in root_relations:
            relative = safe_relative(
                target_policy[policy_field], f"P4 {policy_field} policy"
            )
            expected_child = roots[parent_name].resolved.joinpath(*relative.parts)
            no_symlink_components(
                expected_child,
                roots[parent_name].resolved,
                f"P4 {child_name} root",
            )
            try:
                expected_child = expected_child.resolve(strict=True)
            except (OSError, RuntimeError) as error:
                raise GateError(
                    f"P4 {child_name} root is unavailable under {parent_name}"
                ) from error
            if roots[child_name].resolved != expected_child:
                raise GateError(
                    f"P4 {child_name} root is not the policy child of {parent_name}"
                )
    else:
        build_relative = safe_relative(
            target_policy["build_relative"], "EMOS build_relative policy"
        )
        expected_build = roots["BUILD_TOOL"].resolved.joinpath(
            *build_relative.parts
        )
        no_symlink_components(
            expected_build, roots["BUILD_TOOL"].resolved, "EMOS BUILD root"
        )
        try:
            expected_build = expected_build.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise GateError("EMOS BUILD root is unavailable under BUILD_TOOL") from error
        if roots["BUILD"].resolved != expected_build:
            raise GateError("EMOS BUILD root is not the policy child of BUILD_TOOL")
    if roots["PROVENANCE"].resolved != evidence_root:
        raise GateError("PROVENANCE root does not match --evidence-root")
    policy_digest = verify_policy_authority(policy_path, roots)
    if build["policy_sha256"] != policy_digest:
        raise GateError("build record policy digest mismatch")
    repository_records = build["repositories"]
    if not isinstance(repository_records, list):
        raise GateError("build repositories must be an array")
    expected_repositories = target_policy["repositories"]
    if [item.get("id") for item in repository_records if isinstance(item, dict)] != [
        item["id"] for item in expected_repositories
    ]:
        raise GateError("build repository order/set differs from policy")
    repositories: dict[str, dict[str, Any]] = {}
    for observed, expected in zip(repository_records, expected_repositories, strict=True):
        record = verify_repository(observed, expected, roots)
        repositories[record["id"]] = record
    if build["target"] == "p4" and (
        repositories["authority"]["commit"]
        != repositories["product-source"]["commit"]
    ):
        raise GateError(
            "P4 policy/registry authority and product source are not the same commit"
        )
    tools = {
        name: verify_tool(name, specification, roots)
        for name, specification in target_policy["tools"].items()
    }
    prepared = verify_prepared_source(
        target_policy,
        repositories,
        roots,
        tools.get("python", {}).get("resolved"),
    )
    if build["target"] == "emos":
        capture = validate_mos_capture(
            build, target_policy, evidence_root, roots, tools, prepared
        )
    else:
        capture = validate_p4_capture(
            build, target_policy, evidence_root, roots, tools
        )
    command_policy_proved, command_blockers, command_candidates = evaluate_command_policy(
        target_policy, build["role"], capture
    )
    capture["command_policy"] = {
        "status": target_policy["command_policy_status"],
        "proved": command_policy_proved,
        "candidates": command_candidates,
    }
    identity_eligible, blockers, identity = validate_identity(
        build, target_policy, policy, roots
    )
    blockers.extend(command_blockers)
    identity_binding_proved = capture["identity_binding"]["identity_values_bound"] is True
    if not identity_binding_proved:
        blockers.append(
            "captured composition remains unversioned or does not bind every build-record identity value"
        )
    release_status = target_policy["release_consumer"]["status"]
    if release_status == "absent":
        blockers.append(target_policy["release_consumer"]["note"])
    eligible = (
        identity_eligible
        and identity_binding_proved
        and command_policy_proved
        and release_status != "absent"
    )
    return {
        "schema_version": 1,
        "evidence_kind": "port-008-production-object-build-validation",
        "target": build["target"],
        "role": build["role"],
        "policy_sha256": policy_digest,
        "build_record_sha256": sha256_file(build_path),
        "repository_source_authority_proved": True,
        "target_tool_authority_proved": True,
        "target_tool_authority_scope": "selected-executable-bytes-and-recorded-subtools-only",
        "complete_target_tool_host_execution_closure_proved": False,
        "capture_runtime_authority_proved": build["target"] == "p4",
        "capture_runtime_authority_scope": (
            "recorded-python-executable-platformio-scons-and-launcher-files-only"
            if build["target"] == "p4"
            else "recorder-file-only-host-python-runtime-unrecorded"
        ),
        "complete_capture_execution_runtime_closure_proved": False,
        "intended_command_policy_proved": command_policy_proved,
        "actual_required_unit_steps_proved": True,
        "required_unit_final_link_inputs_proved": True,
        "complete_implicit_link_input_closure_proved": False,
        "required_unit_nonzero_link_contribution_proved": True,
        "required_unit_symbol_origin_proved": True,
        "identity_binding_proved": identity_binding_proved,
        "identity_eligible": identity_eligible,
        "equivalence_eligible": eligible,
        "equivalence_proved": False,
        "blockers": sorted(set(blockers)),
        "identity": identity,
        "repositories": list(repositories.values()),
        "prepared_source": prepared,
        "tools": [
            {key: value[key] for key in ("name", "path", "sha256", "size", "version_output_sha256")}
            for value in tools.values()
        ],
        "capture": capture,
    }


def composition_dependencies_match_policy(
    qualification_dependencies: Sequence[dict[str, Any]],
    release_dependencies: Sequence[dict[str, Any]],
    expected_delta: Mapping[str, Sequence[str]],
) -> bool:
    qualification = {record["path"]: record for record in qualification_dependencies}
    release = {record["path"]: record for record in release_dependencies}
    qualification_paths = set(qualification)
    release_paths = set(release)
    if qualification_paths - release_paths != set(
        expected_delta["qualification_only"]
    ) or release_paths - qualification_paths != set(expected_delta["release_only"]):
        return False
    return all(
        qualification[path] == release[path]
        for path in qualification_paths & release_paths
    )


def compare_validations(
    qualification: dict[str, Any], release: dict[str, Any], policy: dict[str, Any]
) -> dict[str, Any]:
    if qualification["target"] != release["target"]:
        raise GateError("qualification/release target mismatch")
    if qualification["role"] != "qualification" or release["role"] != "release":
        raise GateError("comparison roles must be qualification then release")
    if qualification["policy_sha256"] != release["policy_sha256"]:
        raise GateError("qualification/release policy digests differ")
    for field in ("build_record_sha256",):
        if qualification[field] == release[field]:
            raise GateError(f"same-build self-comparison: identical {field}")
    q_capture = qualification["capture"]
    r_capture = release["capture"]
    if q_capture["session_id"] == r_capture["session_id"]:
        raise GateError("same-build self-comparison: identical provenance session")
    if (
        q_capture["final_image"]["instance_path_sha256"]
        == r_capture["final_image"]["instance_path_sha256"]
    ):
        raise GateError("same-build self-comparison: identical final-image instance")
    if qualification["identity"]["build_id"] == release["identity"]["build_id"]:
        raise GateError("same-build self-comparison: identical immutable build ID")
    if q_capture["final_image"]["sha256"] == r_capture["final_image"]["sha256"]:
        raise GateError("qualification/release final compositions are unexpectedly byte-identical")
    target_policy = policy["targets"][qualification["target"]]
    equality_ids = [
        unit["id"]
        for unit in target_policy["units"]
        if unit["classification"] == "equality"
    ]
    differences: list[str] = []
    lineage_fields = (
        "artifact_id",
        "variant",
        "source_identity",
        "lifecycle_status",
        "registry_sha256",
    )
    for field in lineage_fields:
        if qualification["identity"][field] != release["identity"][field]:
            differences.append(f"firmware lineage differs in {field}")
    qualification_repositories = {
        item["id"]: item["commit"] for item in qualification["repositories"]
    }
    release_repositories = {
        item["id"]: item["commit"] for item in release["repositories"]
    }
    if qualification_repositories != release_repositories:
        differences.append("policy/registry and product source commits differ")
    if qualification["target"] == "emos":
        for field in ("source_commit", "checker_commit"):
            if qualification["prepared_source"][field] != release["prepared_source"][field]:
                differences.append(f"EMOS prepared-source lineage differs in {field}")
        for unit in target_policy["units"]:
            if unit["classification"] != "composition-dependent":
                continue
            unit_id = unit["id"]
            left = q_capture["units"].get(unit_id)
            right = r_capture["units"].get(unit_id)
            if left is None or right is None:
                differences.append(f"{unit_id}: missing composition-dependent owner")
                continue
            owner_fields = (
                "source_sha256",
                "declared_inputs",
                "environment",
                "executables",
                "response_files",
                "generator",
            )
            changed = [field for field in owner_fields if left[field] != right[field]]
            if changed:
                differences.append(
                    f"{unit_id}: composition-owner inputs differ in {', '.join(changed)}"
                )
            if not composition_dependencies_match_policy(
                left["dependencies"],
                right["dependencies"],
                unit["expected_dependency_delta"],
            ):
                differences.append(
                    f"{unit_id}: composition-owner dependencies differ from exact policy delta"
                )
    comparison: dict[str, Any] = {}
    for unit_id in equality_ids:
        left = q_capture["units"].get(unit_id)
        right = r_capture["units"].get(unit_id)
        if left is None or right is None:
            differences.append(f"{unit_id}: missing equality unit")
            continue
        fields = [
            "source_sha256",
            "dependencies",
            "declared_inputs",
            "environment",
            "executables",
            "response_files",
            "object_sha256",
            "object_size",
            "object_symbols",
            "linked_symbols",
            "object_disassembly_sha256",
            "linked_disassembly_sha256",
            "generator",
            "command_policy_material",
            "driver_selection",
        ]
        if target_policy["equality_compile_commands_must_match"]:
            fields.append("command")
        changed = [field for field in fields if left[field] != right[field]]
        if changed:
            differences.append(f"{unit_id}: differs in {', '.join(changed)}")
        comparison[unit_id] = {
            "object_sha256": left["object_sha256"],
            "matching_fields": sorted(set(fields) - set(changed)),
            "different_fields": changed,
        }
    blockers = sorted(
        set(qualification["blockers"] + release["blockers"] + differences)
    )
    proved = (
        qualification["equivalence_eligible"]
        and release["equivalence_eligible"]
        and not differences
    )
    return {
        "schema_version": 1,
        "evidence_kind": "port-008-production-object-equivalence",
        "target": qualification["target"],
        "qualification_build_record_sha256": qualification["build_record_sha256"],
        "release_build_record_sha256": release["build_record_sha256"],
        "production_unit_set_complete": not any("missing equality unit" in item for item in differences),
        "object_bytes_identical": not any("object_sha256" in item for item in differences),
        "compile_inputs_identical": not any(
            any(
                field in item
                for field in (
                    "source_sha256",
                    "dependencies",
                    "declared_inputs",
                    "environment",
                    "executables",
                    "response_files",
                    "generator",
                    "command",
                    "command_policy_material",
                    "driver_selection",
                )
            )
            for item in differences
        ),
        "linked_symbols_and_normalized_disassembly_identical": not any(
            "linked_symbols" in item or "linked_disassembly_sha256" in item
            for item in differences
        ),
        "units": comparison,
        "blockers": blockers,
        "equivalence_proved": proved,
    }


def compare_builds(
    *,
    policy_path: Path,
    qualification_build: Path,
    qualification_evidence_root: Path,
    qualification_roots: Sequence[str],
    release_build: Path,
    release_evidence_root: Path,
    release_roots: Sequence[str],
) -> dict[str, Any]:
    policy_path = regular_file(policy_path, "policy")
    policy = validate_policy(load_json(policy_path, "policy"))
    qualification = validate_build(
        policy_path=policy_path,
        build_path=qualification_build,
        evidence_root=qualification_evidence_root,
        root_arguments=qualification_roots,
    )
    release = validate_build(
        policy_path=policy_path,
        build_path=release_build,
        evidence_root=release_evidence_root,
        root_arguments=release_roots,
    )
    return compare_validations(qualification, release, policy)


def write_report(path: Path, report: dict[str, Any]) -> None:
    path = Path(os.path.abspath(path))
    if os.path.lexists(path):
        raise GateError(f"refusing to overwrite report: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(report, indent=2, sort_keys=True) + "\n"
    try:
        with path.open("x", encoding="utf-8", newline="") as stream:
            stream.write(data)
    except FileExistsError as error:
        raise GateError(f"refusing raced report path: {path}") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="action", required=True)
    validate = subparsers.add_parser("validate", help="validate one raw target build")
    validate.add_argument("--policy", required=True, type=Path)
    validate.add_argument("--build-record", required=True, type=Path)
    validate.add_argument("--evidence-root", required=True, type=Path)
    validate.add_argument("--root", action="append", default=[])
    validate.add_argument("--report", type=Path)
    compare = subparsers.add_parser("compare", help="compare qualification and release builds")
    compare.add_argument("--policy", required=True, type=Path)
    compare.add_argument("--qualification-build-record", required=True, type=Path)
    compare.add_argument("--qualification-evidence-root", required=True, type=Path)
    compare.add_argument("--qualification-root", action="append", default=[])
    compare.add_argument("--release-build-record", required=True, type=Path)
    compare.add_argument("--release-evidence-root", required=True, type=Path)
    compare.add_argument("--release-root", action="append", default=[])
    compare.add_argument("--report", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.action == "validate":
            report = validate_build(
                policy_path=args.policy,
                build_path=args.build_record,
                evidence_root=args.evidence_root,
                root_arguments=args.root,
            )
            success = report["equivalence_eligible"]
        else:
            report = compare_builds(
                policy_path=args.policy,
                qualification_build=args.qualification_build_record,
                qualification_evidence_root=args.qualification_evidence_root,
                qualification_roots=args.qualification_root,
                release_build=args.release_build_record,
                release_evidence_root=args.release_evidence_root,
                release_roots=args.release_root,
            )
            success = report["equivalence_proved"]
        if args.report is not None:
            write_report(args.report, report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if success else 1
    except (GateError, OSError, subprocess.SubprocessError, yaml.YAMLError) as error:
        print(f"production-object provenance failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
