"""Opt-in actual-action provenance for the PORT-008 P4 composition.

This PlatformIO pre-script wraps SCons' existing ``SPAWN`` callable.  For an
observed C++ compile or link, the wrapper strictly inverts the pinned SCons
POSIX one-word encoding and executes that exact argument vector directly,
without a shell.  When capture is enabled, the child receives a recorded
minimal environment with a fixed C locale and compiler/linker injection
variables removed.  Non-C++ actions retain SCons' ordinary spawn behavior.
This is intentionally not based on ESP-IDF's generated
``compile_commands.json`` or ``build.ninja``: those describe unused CMake
``.obj`` nodes in this hybrid build, while SCons produces the linked ``.o``
objects.

The recorder is inert unless ``AGON_EXTENDER_P4_PROVENANCE_DIR`` names a fresh
absolute output directory.  An enabled capture requires every allowlisted
project/vendored C++ object and the final ELF/map to be freshly produced in
the same invocation.  Incremental, stale, incomplete, duplicate, or failed
steps leave an incomplete session and fail the PlatformIO build before its
ordinary size check.

SECURITY: the output contains exact local commands and absolute tool/source
paths.  It is machine-local evidence and may disclose local directory names.
The recorder never executes a command from the source-selection manifest.  It
does execute identity probes against compiler/linker programs already selected
by the observed build command.
"""

from __future__ import annotations

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
import threading
import time
from typing import Any, Callable, Iterable, Mapping, Sequence
import uuid


ENVIRONMENT = "p4-port008-nonrelease-qualification"
OUTPUT_VARIABLE = "AGON_EXTENDER_P4_PROVENANCE_DIR"
EVIDENCE_KIND = "p4-platformio-scons-actual-step-provenance"
SCHEMA_VERSION = "1.0.0"
MAX_RESPONSE_BYTES = 16 * 1024 * 1024
MAX_IDENTITY_OUTPUT_BYTES = 64 * 1024
IDENTITY_TIMEOUT_SECONDS = 15
CPP_SUFFIXES = (".cc", ".cpp", ".cxx", ".C")
DRIVER_NAME = re.compile(r"(?:^|[-_])(?:g\+\+|clang\+\+|c\+\+)$")
MAP_FLAG = re.compile(r"^-Wl,(?:--?Map)(?:=|,)(.+)$")
MAP_LOAD = re.compile(r"^LOAD[ \t]+(.+?)[ \t]*$")
IDENTITY_DEFINE = re.compile(
    r'^#define (AGON_EXTENDER_(?:SOURCE_IDENTITY|BUILD_ID|ARTIFACT_STATUS|'
    r'QUALIFICATION_COMPOSITION_IDENTITY)) '
    r'"([A-Za-z0-9][A-Za-z0-9.-]*)"$'
)
DEPENDENCY_OPTIONS = ("-include", "-imacros", "-T")
# SCons 4.8.1's POSIX action path presents one independently escaped shell word
# per list element.  Capture accepts only the two encodings that path emits:
# ordinary quote-spaces words and SCons.Platform.posix.escape literal words.
# This set is deliberately broader than shell control operators because glob,
# comment, tilde, and substitution syntax also changes argv under ``sh -c``.
UNQUOTED_SHELL_META = frozenset(" \t\n\r\v\f\\'\"`$&;|<>()*?[#~")
DOUBLE_QUOTE_ESCAPABLE = frozenset('\\\\\"$`')
UNPROVED_NESTED_TOOL_OPTIONS = (
    "-B",
    "-flto",
    "-fplugin",
    "-fuse-ld",
    "-specs",
    "--specs",
    "-wrapper",
)
CLEARED_INFLUENCE_VARIABLES = (
    "C_INCLUDE_PATH",
    "COMPILER_PATH",
    "CPATH",
    "CPLUS_INCLUDE_PATH",
    "GCC_EXEC_PREFIX",
    "LIBRARY_PATH",
    "LD_LIBRARY_PATH",
    "OBJC_INCLUDE_PATH",
    "SDKROOT",
)


class ProvenanceError(RuntimeError):
    """One actual-step provenance invariant was absent or contradictory."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _atomic_json(path: Path, document: Mapping[str, Any], *, exclusive: bool) -> None:
    encoded = (
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    ).encode("utf-8")
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(temporary, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
        if exclusive:
            try:
                os.link(temporary, path)
            except FileExistsError as exc:
                raise ProvenanceError(
                    f"refusing to overwrite evidence file: {path}"
                ) from exc
            temporary.unlink()
        else:
            os.replace(temporary, path)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _regular_file(path: Path, label: str) -> Path:
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ProvenanceError(f"{label} does not exist: {path}: {exc}") from exc
    if not resolved.is_file():
        raise ProvenanceError(f"{label} is not a regular file: {path}")
    return resolved


def _runtime_package_identity(
    module: Any, *, name: str, version: str
) -> dict[str, Any]:
    """Hash one installed package's immutable source/resource file set."""

    module_name = getattr(module, "__file__", None)
    if not isinstance(module_name, str) or not module_name:
        raise ProvenanceError(f"{name} package has no module file")
    lexical_module = Path(os.path.abspath(module_name))
    _reject_symlink_components(lexical_module, f"{name} module path")
    module_file = _regular_file(lexical_module, f"{name} module file")
    package_root = module_file.parent
    files: dict[str, dict[str, Any]] = {}
    for path in sorted(package_root.rglob("*")):
        try:
            mode = path.lstat().st_mode
        except OSError as exc:
            raise ProvenanceError(
                f"cannot inspect {name} package member {path}: {exc}"
            ) from exc
        if stat.S_ISLNK(mode):
            raise ProvenanceError(
                f"{name} package contains a symbolic link: {path}"
            )
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise ProvenanceError(
                f"{name} package contains a non-regular file: {path}"
            )
        relative = path.relative_to(package_root).as_posix()
        artifact = _artifact(path)
        assert artifact is not None
        files[relative] = artifact
    module_relative = module_file.relative_to(package_root).as_posix()
    if module_relative not in files:
        raise ProvenanceError(f"{name} module file is absent from its package set")
    digest_input = [
        {
            "path": relative,
            "size": artifact["size"],
            "sha256": artifact["sha256"],
        }
        for relative, artifact in files.items()
    ]
    return {
        "name": name,
        "version": version,
        "package_root": str(package_root),
        "module_relative_path": module_relative,
        "module_file": files[module_relative],
        "excluded_patterns": [],
        "files": files,
        "tree_sha256": sha256_bytes(
            json.dumps(digest_input, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ),
    }


def _capture_runtime_identity(
    platformio_module: Any, scons_module: Any
) -> dict[str, Any]:
    """Bind the interpreter and complete installed PlatformIO/SCons trees."""

    invoked_python = Path(os.path.abspath(sys.executable))
    python_executable = _regular_file(invoked_python, "capture Python executable")
    executable_artifact = _artifact(python_executable)
    assert executable_artifact is not None
    invoked_launcher = Path(os.path.abspath(sys.argv[0]))
    launcher = _regular_file(invoked_launcher, "capture process launcher")
    launcher_artifact = _artifact(launcher)
    assert launcher_artifact is not None
    return {
        "policy": "capture-runtime-file-set-v1",
        "python": {
            "invoked_path": str(invoked_python),
            "executable": executable_artifact,
            "implementation": sys.implementation.name,
            "version": sys.version,
            "bytecode_writes_disabled": sys.dont_write_bytecode,
            "version_info": [
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
                sys.version_info.releaselevel,
                sys.version_info.serial,
            ],
        },
        "launcher": {
            "invoked_path": str(invoked_launcher),
            "artifact": launcher_artifact,
        },
        "platformio": _runtime_package_identity(
            platformio_module,
            name="platformio",
            version=str(platformio_module.__version__),
        ),
        "scons": _runtime_package_identity(
            scons_module,
            name="scons",
            version=str(scons_module.__version__),
        ),
    }


def _reject_symlink_components(path: Path, label: str) -> None:
    if not path.is_absolute():
        raise ProvenanceError(f"{label} must be absolute: {path}")
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        try:
            current.lstat()
        except FileNotFoundError:
            continue
        if current.is_symlink():
            raise ProvenanceError(f"{label} traverses a symlink: {current}")


def _normalized_manifest_paths(
    document: Mapping[str, Any], field: str
) -> tuple[str, ...]:
    value = document.get(field, [])
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ProvenanceError(f"source selection {field} must be a string array")
    if len(value) != len(set(value)):
        raise ProvenanceError(f"source selection {field} contains a duplicate")
    for item in value:
        pure = PurePosixPath(item)
        if (
            pure.is_absolute()
            or not pure.parts
            or any(part in ("", ".", "..") for part in pure.parts)
            or "\\" in item
        ):
            raise ProvenanceError(
                f"source selection {field} contains an unsafe path: {item!r}"
            )
    return tuple(value)


def _artifact(path: Path) -> dict[str, Any] | None:
    if path.is_symlink():
        raise ProvenanceError(f"artifact path is a symlink: {path}")
    try:
        stat = path.stat()
    except FileNotFoundError:
        return None
    if not path.is_file():
        raise ProvenanceError(f"expected regular artifact is not a file: {path}")
    return {
        "path": str(path.resolve(strict=True)),
        "size": stat.st_size,
        "sha256": sha256_file(path),
        "inode": stat.st_ino,
        "mtime_ns": stat.st_mtime_ns,
        "ctime_ns": stat.st_ctime_ns,
    }


def _resolve_argument_path(value: str, cwd: Path) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = cwd / path
    return path.resolve(strict=False)


def _option_output(arguments: Sequence[str], cwd: Path) -> Path | None:
    for index, argument in enumerate(arguments):
        if argument == "-o" and index + 1 < len(arguments):
            return _resolve_argument_path(arguments[index + 1], cwd)
        if argument.startswith("-o") and len(argument) > 2:
            return _resolve_argument_path(argument[2:], cwd)
    return None


def _driver_index(arguments: Sequence[str]) -> int | None:
    for index, argument in enumerate(arguments):
        if DRIVER_NAME.search(Path(argument).name):
            return index
    return None


def _candidate_source(arguments: Sequence[str], cwd: Path) -> Path | None:
    candidates = [
        _resolve_argument_path(argument, cwd)
        for argument in arguments
        if argument.endswith(CPP_SUFFIXES)
    ]
    return candidates[-1] if candidates else None


def _map_paths(arguments: Sequence[str], cwd: Path) -> tuple[Path, ...]:
    results: list[Path] = []
    for argument in arguments:
        match = MAP_FLAG.fullmatch(argument)
        if match is not None:
            results.append(_resolve_argument_path(match.group(1), cwd))
    return tuple(results)


def _direct_dependency_paths(
    arguments: Sequence[str], cwd: Path, output: Path | None
) -> tuple[Path, ...]:
    """Return observable direct file arguments, excluding response references."""

    candidates: list[str] = []
    for index, argument in enumerate(arguments):
        if argument in DEPENDENCY_OPTIONS and index + 1 < len(arguments):
            candidates.append(arguments[index + 1])
            continue
        if argument.startswith("-T") and len(argument) > 2:
            candidates.append(argument[2:])
            continue
        if argument.startswith("-Wl,-T,"):
            candidates.append(argument[len("-Wl,-T,") :])
            continue
        if argument.startswith("-Wl,-T") and len(argument) > len("-Wl,-T"):
            candidates.append(argument[len("-Wl,-T") :])
            continue
        if argument.startswith("-") or argument.startswith("@"):
            continue
        candidates.append(argument)
    results: list[Path] = []
    for candidate in candidates:
        path = _resolve_argument_path(candidate, cwd)
        if path == output or not path.is_file():
            continue
        if path not in results:
            results.append(path)
    return tuple(results)


def _run_identity_probe(
    arguments: Sequence[str], *, environment: Mapping[str, str], cwd: Path
) -> dict[str, Any]:
    try:
        completed = subprocess.run(
            list(arguments),
            cwd=cwd,
            env=dict(environment),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
            timeout=IDENTITY_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"arguments": list(arguments), "error": str(exc)}
    output = completed.stdout[:MAX_IDENTITY_OUTPUT_BYTES]
    return {
        "arguments": list(arguments),
        "exit_status": completed.returncode,
        "output_utf8": output.decode("utf-8", errors="replace"),
        "output_truncated": len(completed.stdout) > len(output),
    }


def _scons_posix_literal_escape(value: str) -> str | None:
    """Reproduce the pinned SCons POSIX ``escape`` result when shell-safe."""

    if any(character in value for character in ("\n", "\r", "`")):
        # SCons 4.8.1 does not escape a backtick inside its double quotes. Such
        # an element would perform command substitution under the old shell
        # path, so it has no accepted direct-exec inverse.
        return None
    escaped = value.replace("\\", "\\\\")
    escaped = escaped.replace('"', '\\"').replace("$", "\\$")
    return f'"{escaped}"'


def _ordinary_scons_posix_word(value: str) -> str:
    """Return the canonical shell-safe ordinary SCons word for ``value``."""

    if "\x00" in value or "\n" in value or "\r" in value:
        raise ProvenanceError("an argument contains NUL or a newline")
    if value == "" or any(character.isspace() for character in value):
        body = value.replace("\\", "\\\\")
        for character in ('"', "$", "`"):
            body = body.replace(character, "\\" + character)
        return f'"{body}"'
    return "".join(
        "\\" + character if character in UNQUOTED_SHELL_META else character
        for character in value
    )


def _decode_pinned_scons_posix_word(argument: str, label: str) -> str:
    """Strictly invert one accepted SCons POSIX word and prove round-trip.

    This is intentionally not a general shell parser. It accepts only one
    fully unquoted word or one fully double-quoted word, with POSIX backslash
    escapes and no live expansion syntax. Re-encoding the decoded value with
    either the ordinary SCons form or the pinned literal escape must reproduce
    the input byte-for-byte.
    """

    if not argument:
        raise ProvenanceError(f"{label} is an empty unquoted SCons word")
    if any(character in argument for character in ("\x00", "\n", "\r")):
        raise ProvenanceError(f"{label} contains NUL or a newline")

    decoded: list[str] = []
    if argument.startswith('"'):
        if len(argument) < 2 or not argument.endswith('"'):
            raise ProvenanceError(f"{label} has an unterminated double quote")
        index = 1
        end = len(argument) - 1
        while index < end:
            character = argument[index]
            if character == "\\":
                index += 1
                if index >= end or argument[index] not in DOUBLE_QUOTE_ESCAPABLE:
                    raise ProvenanceError(
                        f"{label} has a noncanonical double-quote escape"
                    )
                decoded.append(argument[index])
            elif character in ('"', "$", "`"):
                raise ProvenanceError(
                    f"{label} contains live quote or substitution syntax"
                )
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
                    raise ProvenanceError(f"{label} ends with a backslash")
                decoded.append(argument[index])
            elif character in UNQUOTED_SHELL_META:
                raise ProvenanceError(
                    f"{label} contains live unquoted shell syntax"
                )
            else:
                decoded.append(character)
            index += 1

    value = "".join(decoded)
    accepted = {_ordinary_scons_posix_word(value)}
    literal = _scons_posix_literal_escape(value)
    if literal is not None:
        accepted.add(literal)
    if argument not in accepted:
        raise ProvenanceError(
            f"{label} is not a canonical pinned SCons POSIX encoding"
        )
    return value


def _decode_scons_arguments(arguments: Sequence[str]) -> list[str]:
    """Strictly decode independently escaped SCons argument boundaries."""

    return [
        _decode_pinned_scons_posix_word(
            argument, f"escaped SCons argument {index}"
        )
        for index, argument in enumerate(arguments)
    ]


def _decode_pinned_scons_response(
    data: bytes, label: str
) -> tuple[list[str], list[str]]:
    """Decode and byte-round-trip the capture-owned SCons response format."""

    try:
        text = data.decode("utf-8", errors="strict")
    except UnicodeError as exc:
        raise ProvenanceError(f"{label} is not UTF-8: {exc}") from exc
    if not text.endswith("\n") or "\n" in text[:-1] or "\r" in text:
        raise ProvenanceError(
            f"{label} must contain exactly one newline at end of file"
        )
    body = text[:-1]
    if not body:
        raise ProvenanceError(f"{label} contains no argument words")

    encoded_words: list[str] = []
    index = 0
    while index < len(body):
        if body[index] == " ":
            raise ProvenanceError(
                f"{label} has a noncanonical empty or repeated argument boundary"
            )
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
                raise ProvenanceError(f"{label} has an unterminated quoted word")
            if index < len(body) and body[index] != " ":
                raise ProvenanceError(
                    f"{label} concatenates text after a quoted word"
                )
        else:
            while index < len(body) and body[index] != " ":
                index += 1
        encoded_words.append(body[start:index])
        if index < len(body):
            index += 1
            if index == len(body):
                raise ProvenanceError(f"{label} has a trailing empty argument")

    decoded = [
        _decode_pinned_scons_posix_word(word, f"{label} word {ordinal}")
        for ordinal, word in enumerate(encoded_words)
    ]
    canonical = " ".join(
        _ordinary_scons_posix_word(argument) for argument in decoded
    ) + "\n"
    if canonical.encode("utf-8") != data:
        raise ProvenanceError(
            f"{label} does not round-trip through pinned SCons quote-spaces"
        )
    return decoded, encoded_words


def _reject_unproved_nested_tool_options(arguments: Sequence[str]) -> None:
    matches = sorted(
        {
            argument
            for argument in arguments
            if any(
                argument == prefix
                or argument.startswith(prefix + "=")
                or (prefix == "-B" and argument.startswith("-B"))
                for prefix in UNPROVED_NESTED_TOOL_OPTIONS
            )
        }
    )
    if matches:
        raise ProvenanceError(
            "C++ command selects an unproved nested tool/plugin path: "
            + ", ".join(matches)
        )


def _assembler_dispatch_selector_arguments(
    arguments: Sequence[str],
) -> tuple[str, ...]:
    """Extract the Espressif assembler dispatcher's visible selectors."""

    selectors = tuple(
        argument
        for argument in arguments
        if argument.startswith("-march=") or argument.startswith("-mespv-spec=")
    )
    for prefix in ("-march=", "-mespv-spec="):
        if sum(argument.startswith(prefix) for argument in selectors) > 1:
            raise ProvenanceError(
                f"compile command contains duplicate assembler selector {prefix}"
            )
    return selectors


def _dependency_scan_arguments(
    arguments: Sequence[str], driver_index: int, depfile: Path, target: Path
) -> list[str]:
    """Derive a preprocessing-only transitive dependency scan invocation."""

    result = list(arguments[driver_index:])
    filtered: list[str] = []
    dependency_flags = {"-M", "-MM", "-MD", "-MMD", "-MP"}
    dependency_options = {"-MF", "-MT", "-MQ"}
    index = 0
    while index < len(result):
        argument = result[index]
        if argument == "-c" or argument in dependency_flags:
            index += 1
            continue
        if argument == "-o" or argument in dependency_options:
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
    filtered.extend(["-M", "-MF", str(depfile), "-MT", str(target)])
    return filtered


def _parse_depfile(path: Path, cwd: Path) -> tuple[Path, ...]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ProvenanceError(
            f"dependency file is not readable UTF-8: {path}: {exc}"
        ) from exc
    logical = text.replace("\\\n", "")
    delimiter = logical.find(": ")
    if delimiter < 0:
        raise ProvenanceError(f"dependency file has no target delimiter: {path}")
    try:
        names = shlex.split(logical[delimiter + 2 :], posix=True)
    except ValueError as exc:
        raise ProvenanceError(
            f"dependency file is not parseable: {path}: {exc}"
        ) from exc
    dependencies: list[Path] = []
    for name in names:
        dependency = _resolve_argument_path(name, cwd)
        if dependency not in dependencies:
            dependencies.append(dependency)
    if not dependencies:
        raise ProvenanceError(f"dependency file contains no inputs: {path}")
    return tuple(dependencies)


def _persistent_tempfile_class(output_root: Path):
    """Return a SCons TEMPFILE implementation with retained response bytes."""

    import SCons.Subst

    class PersistentProvenanceTempFile:
        def __init__(self, command, command_string=None) -> None:
            self.command = command
            self.command_string = command_string

        def __call__(self, target, source, environment, for_signature):
            if for_signature:
                return self.command
            command = environment.subst_list(
                self.command,
                SCons.Subst.SUBST_CMD,
                target,
                source,
            )[0]
            maximum = int(environment.subst("$MAXLINELENGTH"))
            if sum(len(str(item)) for item in command) + len(command) - 1 <= maximum:
                return self.command
            escape_argument = environment.get(
                "TEMPFILEARGESCFUNC", SCons.Subst.quote_spaces
            )
            join_character = environment.get("TEMPFILEARGJOIN", " ")
            prefix = environment.subst("$TEMPFILEPREFIX") or "@"
            if escape_argument is not SCons.Subst.quote_spaces:
                raise ProvenanceError(
                    "P4 provenance requires SCons TEMPFILEARGESCFUNC="
                    "SCons.Subst.quote_spaces"
                )
            if join_character != " ":
                raise ProvenanceError(
                    "P4 provenance requires a single-space TEMPFILEARGJOIN"
                )
            if prefix != "@":
                raise ProvenanceError(
                    "P4 provenance requires the exact @ TEMPFILEPREFIX"
                )
            response = (
                join_character.join(
                    str(escape_argument(str(argument))) for argument in command[1:]
                )
                + "\n"
            ).encode("utf-8")
            digest = sha256_bytes(response)
            path = output_root / "responses" / f"scons-{digest}.rsp"
            try:
                descriptor = os.open(
                    path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                )
            except FileExistsError:
                if sha256_file(path) != digest:
                    raise ProvenanceError(f"persistent response collision: {path}")
            else:
                with os.fdopen(descriptor, "wb") as destination:
                    destination.write(response)
                    destination.flush()
                    os.fsync(destination.fileno())
            return [command[0], prefix + str(path)]

    return PersistentProvenanceTempFile


class CaptureSession:
    """One fresh PlatformIO invocation's in-memory and durable event state."""

    def __init__(
        self,
        *,
        project_root: Path,
        build_root: Path,
        output_root: Path,
        selection_path: Path,
        hook_path: Path,
        platformio_version: str,
        scons_version: str,
        capture_runtime: Mapping[str, Any] | None = None,
        runtime_refresh: Callable[[], Mapping[str, Any]] | None = None,
    ) -> None:
        self.project_root = project_root.resolve(strict=True)
        self.build_root = build_root.resolve(strict=True)
        self.output_root = output_root
        self.selection_path = _regular_file(
            selection_path, "qualification source-selection manifest"
        )
        self.hook_path = _regular_file(hook_path, "provenance capture hook")
        if capture_runtime is None:
            capture_runtime = {
                "policy": "direct-host-test-unqualified-v1",
                "platformio_version": platformio_version,
                "scons_version": scons_version,
                "python_version": sys.version,
            }
        self.capture_runtime = json.loads(json.dumps(capture_runtime))
        self._runtime_refresh = runtime_refresh
        self.elf_path = self.build_root / "firmware.elf"
        self.map_path = self.build_root / "firmware.map"
        self.session_id = uuid.uuid4().hex
        self.started_ns = time.time_ns()
        self._lock = threading.Lock()
        self._events: list[dict[str, Any]] = []
        self._sequence = 0
        self._tool_cache: dict[str, dict[str, Any]] = {}
        self._finalized = False

        if not output_root.is_absolute():
            raise ProvenanceError(
                f"{OUTPUT_VARIABLE} must name an absolute path: {output_root}"
            )
        if any(character.isspace() for character in str(output_root)):
            raise ProvenanceError(
                f"{OUTPUT_VARIABLE} must not contain whitespace: {output_root}"
            )
        _reject_symlink_components(output_root, OUTPUT_VARIABLE)
        if output_root != output_root.resolve(strict=False):
            raise ProvenanceError(
                f"{OUTPUT_VARIABLE} must be a canonical absolute path: {output_root}"
            )
        if output_root.exists() or output_root.is_symlink():
            raise ProvenanceError(
                f"{OUTPUT_VARIABLE} must name a fresh nonexisting directory: "
                f"{output_root}"
            )
        parent = output_root.parent.resolve(strict=True)
        if not parent.is_dir():
            raise ProvenanceError(
                f"provenance output parent is not a directory: {parent}"
            )
        output_root.mkdir(mode=0o700)
        self.output_root = output_root.resolve(strict=True)
        (self.output_root / "responses").mkdir(mode=0o700)
        (self.output_root / "dependency-scans").mkdir(mode=0o700)
        (self.output_root / "tmp").mkdir(mode=0o700)

        try:
            selection = json.loads(self.selection_path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ProvenanceError(
                f"source selection is not readable UTF-8 JSON: {exc}"
            ) from exc
        if not isinstance(selection, dict):
            raise ProvenanceError("source selection must contain one JSON object")
        if selection.get("environment") != ENVIRONMENT:
            raise ProvenanceError(
                f"source selection does not describe {ENVIRONMENT!r}"
            )
        self.selection = selection
        self.expected_objects = self._build_expected_objects(selection)
        self.source_inventory = self._build_source_inventory(selection)
        self.local_build_identity = self._build_local_build_identity(selection)
        stale_outputs = [
            path
            for path in (*self.expected_objects, self.elf_path, self.map_path)
            if path.exists() or path.is_symlink()
        ]
        if stale_outputs:
            raise ProvenanceError(
                "actual-step capture requires absent target outputs before any "
                "producer runs; clean with capture disabled first: "
                + ", ".join(str(path) for path in stale_outputs)
            )
        session = {
            "schema_version": SCHEMA_VERSION,
            "evidence_kind": EVIDENCE_KIND,
            "status": "incomplete",
            "session_id": self.session_id,
            "environment": ENVIRONMENT,
            "started_time_ns": self.started_ns,
            "project_root": str(self.project_root),
            "build_root": str(self.build_root),
            "completion_report": "provenance.json",
            "failure_report": "failure.json",
            "platformio_version": platformio_version,
            "scons_version": scons_version,
            "python_version": sys.version,
            "capture_runtime": {
                "input_stability": "not-yet-verified",
                "before": self.capture_runtime,
                "after": None,
            },
            "source_selection": {
                "path": str(self.selection_path),
                "sha256": sha256_file(self.selection_path),
            },
            "capture_hook": {
                "path": str(self.hook_path),
                "sha256": sha256_file(self.hook_path),
            },
            "child_environment_policy": {
                "allowlist": ["PATH"],
                "forced": {
                    "LANG": "C",
                    "LC_ALL": "C",
                    "TZ": "UTC",
                    "TMPDIR": str(self.output_root / "tmp"),
                    "PWD": str(self.project_root),
                },
                "explicitly_cleared_compiler_linker_influence_variables": list(
                    CLEARED_INFLUENCE_VARIABLES
                ),
            },
        }
        _atomic_json(self.output_root / "session.json", session, exclusive=True)

    def _build_expected_objects(
        self, selection: Mapping[str, Any]
    ) -> dict[Path, Path]:
        expected: dict[Path, Path] = {}
        for relative in _normalized_manifest_paths(
            selection, "project_translation_units"
        ):
            source = _regular_file(
                self.project_root / PurePosixPath(relative),
                f"selected project source {relative}",
            )
            output = (self.build_root / PurePosixPath(relative + ".o")).resolve(
                strict=False
            )
            if output in expected:
                raise ProvenanceError(f"duplicate expected object path: {output}")
            expected[output] = source
        for relative in _normalized_manifest_paths(
            selection, "vendored_translation_units"
        ):
            source = _regular_file(
                self.project_root / PurePosixPath(relative),
                f"selected vendored source {relative}",
            )
            output = (
                self.build_root / "selected-vdp-gl" / (source.stem + ".o")
            ).resolve(strict=False)
            if output in expected:
                raise ProvenanceError(f"duplicate expected object path: {output}")
            expected[output] = source
        if not expected:
            raise ProvenanceError("source selection contains no expected C++ objects")
        return expected

    def _build_source_inventory(
        self, selection: Mapping[str, Any]
    ) -> dict[str, dict[str, Any]]:
        fields = (
            "project_translation_units",
            "vendored_translation_units",
            "embedded_text_files",
            "header_defined_official_implementation",
            "generated_build_files",
        )
        relatives: list[str] = []
        for field in fields:
            relatives.extend(_normalized_manifest_paths(selection, field))
        local_identity = selection.get("translation_unit_local_build_identity")
        if not isinstance(local_identity, dict):
            raise ProvenanceError(
                "qualification source selection lacks translation-unit-local "
                "build identity"
            )
        generated_header = local_identity.get("generated_header")
        expected_generated_header = (
            f".pio/build-identities/{ENVIRONMENT}/build_identity.hpp"
        )
        if generated_header != expected_generated_header:
            raise ProvenanceError(
                "qualification local build-identity header path is absent or "
                "not environment-owned"
            )
        relatives.append(generated_header)
        inventory: dict[str, dict[str, Any]] = {}
        for relative in sorted(set(relatives)):
            path = _regular_file(
                self.project_root / PurePosixPath(relative),
                f"selected source input {relative}",
            )
            artifact = _artifact(path)
            assert artifact is not None
            inventory[relative] = artifact
        for relative in (
            "platformio.ini",
            "pio/select_sources.py",
            "pio/build_identity.py",
            "pio/capture_p4_actual_steps.py",
            "pio/p4-port008-nonrelease-qualification-source-selection.json",
        ):
            path = _regular_file(
                self.project_root / relative, f"build boundary {relative}"
            )
            artifact = _artifact(path)
            assert artifact is not None
            inventory[relative] = artifact
        return inventory

    def _build_local_build_identity(
        self, selection: Mapping[str, Any]
    ) -> dict[str, Any]:
        record = selection.get("translation_unit_local_build_identity")
        if not isinstance(record, dict) or set(record) != {
            "consumer",
            "generated_header",
        }:
            raise ProvenanceError(
                "qualification local build-identity selector is malformed"
            )
        consumer = record["consumer"]
        generated_header = record["generated_header"]
        if consumer not in _normalized_manifest_paths(
            selection, "project_translation_units"
        ):
            raise ProvenanceError(
                "qualification local build-identity consumer is not selected"
            )
        expected_header = (
            f".pio/build-identities/{ENVIRONMENT}/build_identity.hpp"
        )
        if generated_header != expected_header:
            raise ProvenanceError(
                "qualification local build-identity header path is not "
                "environment-owned"
            )
        path = _regular_file(
            self.project_root / PurePosixPath(generated_header),
            "generated qualification build-identity header",
        )
        try:
            content = path.read_text(encoding="utf-8", errors="strict")
        except (OSError, UnicodeError) as exc:
            raise ProvenanceError(
                f"generated build-identity header is unreadable: {exc}"
            ) from exc
        definitions: dict[str, str] = {}
        for line in content.splitlines():
            match = IDENTITY_DEFINE.fullmatch(line)
            if match is not None:
                definitions[match.group(1)] = match.group(2)
        expected_definitions = {
            "AGON_EXTENDER_SOURCE_IDENTITY",
            "AGON_EXTENDER_BUILD_ID",
            "AGON_EXTENDER_ARTIFACT_STATUS",
            "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY",
        }
        if set(definitions) != expected_definitions:
            raise ProvenanceError(
                "generated build-identity header lacks the exact four "
                "qualification identity definitions"
            )
        return {
            "consumer": consumer,
            "generated_header": generated_header,
            "generator": "pio/build_identity.py",
            "artifact": self.source_inventory[generated_header],
            "content_utf8": content,
            "definitions": definitions,
        }

    def _sanitized_environment(
        self, environment: Mapping[str, str]
    ) -> dict[str, str]:
        path = environment.get("PATH")
        if not isinstance(path, str) or not path:
            raise ProvenanceError("SCons child environment has no usable PATH")
        sanitized = {
            "PATH": path,
            "LANG": "C",
            "LC_ALL": "C",
            "TZ": "UTC",
            "TMPDIR": str(self.output_root / "tmp"),
            "PWD": str(self.project_root),
        }
        leaked = set(CLEARED_INFLUENCE_VARIABLES) & set(sanitized)
        if leaked:
            raise ProvenanceError(
                "sanitized child environment retained compiler/linker injection "
                "variables: " + ", ".join(sorted(leaked))
            )
        return sanitized

    def _snapshot_paths(
        self, paths: Iterable[Path], label: str
    ) -> dict[str, dict[str, Any]]:
        snapshots: dict[str, dict[str, Any]] = {}
        for path in paths:
            resolved = _regular_file(path, label)
            artifact = _artifact(resolved)
            assert artifact is not None
            snapshots[str(resolved)] = artifact
        return snapshots

    def _dependency_scan(
        self,
        *,
        sequence: int,
        phase: str,
        arguments: Sequence[str],
        driver_index: int,
        output: Path,
        environment: Mapping[str, str],
        cwd: Path,
    ) -> dict[str, Any]:
        depfile = self.output_root / "dependency-scans" / f"{sequence}.{phase}.d"
        if depfile.exists() or depfile.is_symlink():
            raise ProvenanceError(f"stale dependency scan output exists: {depfile}")
        scan_arguments = _dependency_scan_arguments(
            arguments, driver_index, depfile, output
        )
        try:
            completed = subprocess.run(
                scan_arguments,
                cwd=cwd,
                env=dict(environment),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {
                "phase": phase,
                "argument_vector": scan_arguments,
                "error": str(exc),
            }
        output_bytes = completed.stdout[:MAX_IDENTITY_OUTPUT_BYTES]
        record: dict[str, Any] = {
            "phase": phase,
            "argument_vector": scan_arguments,
            "exit_status": completed.returncode,
            "output_utf8": output_bytes.decode("utf-8", errors="replace"),
            "output_truncated": len(completed.stdout) > len(output_bytes),
        }
        if record["output_truncated"]:
            record["error"] = "dependency scan output exceeded capture limit"
            return record
        if completed.returncode != 0 or not depfile.is_file():
            record["error"] = "dependency scan did not produce its depfile"
            return record
        try:
            dependencies = _parse_depfile(depfile, cwd)
            snapshots = self._snapshot_paths(
                dependencies, f"{phase} transitive compile dependency"
            )
        except ProvenanceError as exc:
            record["error"] = str(exc)
            return record
        depfile_artifact = _artifact(depfile)
        assert depfile_artifact is not None
        record["depfile"] = depfile_artifact
        record["dependencies"] = snapshots
        return record

    def _capture_response_files(
        self, arguments: Sequence[str], cwd: Path
    ) -> tuple[list[str], list[dict[str, Any]], list[str]]:
        records: list[dict[str, Any]] = []
        errors: list[str] = []

        def expand(items: Sequence[str], depth: int) -> list[str]:
            expanded: list[str] = []
            for item in items:
                if ",@" in item:
                    errors.append(
                        "tool/linker response indirection is outside the capture "
                        f"contract: {item}"
                    )
                    expanded.append(item)
                    continue
                if not item.startswith("@") or len(item) == 1:
                    expanded.append(item)
                    continue
                if depth != 0:
                    errors.append(
                        "nested response-file indirection is outside the capture "
                        f"contract: {item}"
                    )
                    expanded.append(item)
                    continue
                response_path = _resolve_argument_path(item[1:], cwd)
                try:
                    data = response_path.read_bytes()
                except OSError as exc:
                    errors.append(f"unreadable response file {response_path}: {exc}")
                    expanded.append(item)
                    continue
                if len(data) > MAX_RESPONSE_BYTES:
                    errors.append(
                        f"response file exceeds {MAX_RESPONSE_BYTES} bytes: "
                        f"{response_path}"
                    )
                    expanded.append(item)
                    continue
                digest = sha256_bytes(data)
                blob = self.output_root / "responses" / f"{digest}.rsp"
                try:
                    descriptor = os.open(
                        blob, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
                    )
                except FileExistsError:
                    if sha256_file(blob) != digest:
                        errors.append(f"response blob collision at {blob}")
                else:
                    with os.fdopen(descriptor, "wb") as output:
                        output.write(data)
                        output.flush()
                        os.fsync(output.fileno())
                records.append(
                    {
                        "reference": item,
                        "path": str(response_path),
                        "size": len(data),
                        "sha256": digest,
                        "saved_blob": f"responses/{digest}.rsp",
                        "before": _artifact(response_path),
                    }
                )
                try:
                    response_arguments, encoded_words = (
                        _decode_pinned_scons_response(
                            data, f"response file {response_path}"
                        )
                    )
                except ProvenanceError as exc:
                    errors.append(f"unparseable response file {response_path}: {exc}")
                    expanded.append(item)
                    continue
                records[-1].update(
                    {
                        "argument_boundary_policy": (
                            "pinned-scons-quote-spaces-response-v1"
                        ),
                        "encoded_argument_words": encoded_words,
                        "decoded_argument_vector": response_arguments,
                        "byte_round_trip_verified": True,
                    }
                )
                before = records[-1]["before"]
                if (
                    not isinstance(before, dict)
                    or before.get("sha256") != digest
                    or before.get("size") != len(data)
                ):
                    errors.append(
                        f"response file changed while being captured: {response_path}"
                    )
                    expanded.append(item)
                    continue
                expanded.extend(expand(response_arguments, depth + 1))
            return expanded

        return expand(arguments, 0), records, errors

    def _resolve_tool(self, invoked: str, environment: Mapping[str, str]) -> Path:
        candidate = Path(invoked)
        if candidate.is_absolute() or "/" in invoked:
            return _regular_file(
                _resolve_argument_path(invoked, self.project_root),
                f"observed build tool {invoked}",
            )
        resolved = shutil.which(invoked, path=environment.get("PATH"))
        if resolved is None:
            raise ProvenanceError(f"observed build tool is not on PATH: {invoked}")
        return _regular_file(Path(resolved), f"observed build tool {invoked}")

    def _assembler_dispatch_backend(
        self,
        dispatcher: Path,
        step_arguments: Sequence[str],
        environment: Mapping[str, str],
    ) -> dict[str, Any]:
        """Prove the backend selected by Espressif's assembler dispatcher."""

        selectors = _assembler_dispatch_selector_arguments(step_arguments)
        probe_environment = dict(environment)
        probe_environment["ESP_DEBUG_TRACE"] = "1"
        probe_arguments = [str(dispatcher), *selectors, "--version"]
        selection_probe = _run_identity_probe(
            probe_arguments,
            environment=probe_environment,
            cwd=self.project_root,
        )
        record: dict[str, Any] = {
            "policy": "espressif-debug-trace-dispatch-v1",
            "selector_arguments": list(selectors),
            "probe_environment": {
                "base": "sanitized-deterministic-v1",
                "added_variables": {"ESP_DEBUG_TRACE": "1"},
            },
            "selection_probe": selection_probe,
        }
        output = selection_probe.get("output_utf8", "")
        execute_lines = [
            line[len("Execute: ") :]
            for line in output.splitlines()
            if line.startswith("Execute: ")
        ]
        if (
            selection_probe.get("exit_status") != 0
            or selection_probe.get("output_truncated")
            or len(execute_lines) != 1
        ):
            record["error"] = (
                "assembler dispatcher did not report exactly one nested execution"
            )
            return record
        try:
            executed = json.loads(execute_lines[0])
        except json.JSONDecodeError as exc:
            record["error"] = f"assembler dispatcher trace is not JSON: {exc}"
            return record
        if (
            not isinstance(executed, list)
            or not executed
            or any(not isinstance(argument, str) for argument in executed)
            or executed[1:] != [*selectors, "--version"]
        ):
            record["error"] = (
                "assembler dispatcher trace arguments differ from its probe"
            )
            return record
        record["executed_argument_vector"] = executed
        try:
            backend = self._resolve_tool(executed[0], environment)
        except ProvenanceError as exc:
            record["error"] = str(exc)
            return record
        record["backend"] = {
            "invoked": executed[0],
            "resolved_path": str(backend),
            "sha256": sha256_file(backend),
            "size": backend.stat().st_size,
            "version_probe": _run_identity_probe(
                [str(backend), "--version"],
                environment=environment,
                cwd=self.project_root,
            ),
        }
        return record

    def _tool_identity(
        self,
        invoked: str,
        environment: Mapping[str, str],
        *,
        role: str,
        step_arguments: Sequence[str],
    ) -> dict[str, Any]:
        try:
            resolved = self._resolve_tool(invoked, environment)
        except ProvenanceError as exc:
            return {"invoked": invoked, "error": str(exc)}
        if role not in ("compile", "link", "other"):
            return {"invoked": invoked, "error": f"unknown tool role: {role}"}
        assembler_selectors = (
            _assembler_dispatch_selector_arguments(step_arguments)
            if role == "compile"
            else ()
        )
        cache_key = f"{resolved}:{role}:{json.dumps(assembler_selectors)}"
        with self._lock:
            cached = self._tool_cache.get(cache_key)
        if cached is not None:
            return cached
        identity: dict[str, Any] = {
            "invoked": invoked,
            "resolved_path": str(resolved),
            "sha256": sha256_file(resolved),
            "size": resolved.stat().st_size,
            "version_probe": _run_identity_probe(
                [str(resolved), "--version"],
                environment=environment,
                cwd=self.project_root,
            ),
            "target_probe": _run_identity_probe(
                [str(resolved), "-dumpmachine"],
                environment=environment,
                cwd=self.project_root,
            ),
        }
        selected_names: tuple[str, ...]
        selected_field: str | None
        if role == "compile":
            selected_names = ("cc1plus", "as")
            selected_field = "compiler_subtools"
        elif role == "link":
            selected_names = ("collect2", "ld")
            selected_field = "link_subtools"
        else:
            selected_names = ()
            selected_field = None
        if selected_field is not None:
            selected_programs: dict[str, dict[str, Any]] = {}
            for program_name in selected_names:
                selection_probe = _run_identity_probe(
                    [str(resolved), f"-print-prog-name={program_name}"],
                    environment=environment,
                    cwd=self.project_root,
                )
                record: dict[str, Any] = {
                    "program_name": program_name,
                    "selection_probe": selection_probe,
                }
                output_lines = (
                    selection_probe.get("output_utf8", "").strip().splitlines()
                )
                if (
                    selection_probe.get("exit_status") != 0
                    or selection_probe.get("output_truncated")
                    or len(output_lines) != 1
                    or not output_lines[0]
                ):
                    record["error"] = (
                        "compiler driver did not identify exactly one selected "
                        f"{program_name} executable"
                    )
                else:
                    selected_name = output_lines[0]
                    record["invoked"] = selected_name
                    try:
                        selected = self._resolve_tool(selected_name, environment)
                    except ProvenanceError as exc:
                        record["error"] = str(exc)
                    else:
                        record.update(
                            {
                                "resolved_path": str(selected),
                                "sha256": sha256_file(selected),
                                "size": selected.stat().st_size,
                                "version_probe": _run_identity_probe(
                                    [str(selected), "--version"],
                                    environment=environment,
                                    cwd=self.project_root,
                                ),
                            }
                        )
                        if role == "compile" and program_name == "as":
                            record["dispatcher_backend"] = (
                                self._assembler_dispatch_backend(
                                    selected, step_arguments, environment
                                )
                            )
                selected_programs[program_name] = record
            identity[selected_field] = selected_programs
            if role == "link":
                # Compatibility alias for consumers that name the final linker.
                identity["linker"] = selected_programs["ld"]
        with self._lock:
            self._tool_cache.setdefault(cache_key, identity)
            return self._tool_cache[cache_key]

    def spawn(
        self,
        original_spawn: Callable[..., int],
        shell: str,
        escape: Callable[..., Any],
        command: str,
        arguments: Sequence[Any],
        environment: Mapping[str, str],
    ) -> int:
        """Observe one SCons command and directly execute each C++ step."""

        escaped_arguments = [str(argument) for argument in arguments]
        if not escaped_arguments:
            return original_spawn(shell, escape, command, arguments, environment)
        try:
            first_argument = _decode_pinned_scons_posix_word(
                escaped_arguments[0], "escaped SCons argument 0"
            )
        except ProvenanceError:
            # Provenance does not interpret or modify non-C++ shell actions.
            return original_spawn(shell, escape, command, arguments, environment)
        if _driver_index([first_argument]) != 0:
            return original_spawn(shell, escape, command, arguments, environment)

        working_directory = Path.cwd().resolve(strict=True)
        sanitized_environment = self._sanitized_environment(environment)
        with self._lock:
            sequence = self._sequence
            self._sequence += 1
        shell_command = " ".join(escaped_arguments)
        actual_arguments = _decode_scons_arguments(escaped_arguments)
        parse_errors: list[str] = []
        (
            expanded_arguments,
            response_files,
            response_errors,
        ) = self._capture_response_files(actual_arguments, working_directory)
        parse_errors.extend(response_errors)
        driver_index = _driver_index(expanded_arguments)
        output = _option_output(expanded_arguments, working_directory)
        source = _candidate_source(expanded_arguments, working_directory)
        kind = "other_cxx_driver"
        if "-c" in expanded_arguments:
            kind = "cxx_compile"
        elif output == self.elf_path:
            kind = "final_cxx_link"
        elif output is not None and output.suffix == ".elf":
            kind = "other_cxx_link"

        cxx_step = True
        if driver_index != 0:
            raise ProvenanceError(
                "C++ compiler driver must be exact argv[0] for direct execution"
            )
        if working_directory != self.project_root:
            raise ProvenanceError(
                "C++ target step working directory differs from PROJECT_DIR: "
                f"{working_directory} != {self.project_root}"
            )
        if not actual_arguments or str(command) != escaped_arguments[0]:
            raise ProvenanceError(
                "SCons command does not match its first escaped argument"
            )
        if parse_errors:
            raise ProvenanceError(
                "C++ command response provenance is incomplete: "
                + "; ".join(parse_errors)
            )
        _reject_unproved_nested_tool_options(expanded_arguments)

        required_compile = kind == "cxx_compile" and output in self.expected_objects
        if required_compile:
            source = self.expected_objects[output]

        driver_identity: dict[str, Any] | None = None
        if driver_index is not None:
            driver_identity = self._tool_identity(
                expanded_arguments[driver_index],
                sanitized_environment,
                role=(
                    "compile"
                    if kind == "cxx_compile"
                    else "link"
                    if kind == "final_cxx_link"
                    else "other"
                ),
                step_arguments=expanded_arguments,
            )

        source_before = (
            _artifact(source) if source is not None and source.exists() else None
        )
        output_before = (
            _artifact(output) if output is not None and output.exists() else None
        )
        map_before = (
            _artifact(self.map_path)
            if kind == "final_cxx_link" and self.map_path.exists()
            else None
        )
        if required_compile and output_before is not None:
            raise ProvenanceError(
                f"required object existed before its producer step: {output}"
            )
        if kind == "final_cxx_link" and (
            output_before is not None or map_before is not None
        ):
            raise ProvenanceError(
                "firmware.elf/map existed before the actual final-link step"
            )

        dependency_scan_before: dict[str, Any] | None = None
        if required_compile and driver_index is not None and output is not None:
            dependency_scan_before = self._dependency_scan(
                sequence=sequence,
                phase="before",
                arguments=expanded_arguments,
                driver_index=driver_index,
                output=output,
                environment=sanitized_environment,
                cwd=working_directory,
            )
            if output.exists() or output.is_symlink():
                raise ProvenanceError(
                    "required object appeared before its direct compiler producer "
                    f"step: {output}"
                )

        dependency_paths: set[Path] = set()
        if kind == "final_cxx_link":
            dependency_paths.update(self.expected_objects)
            dependency_paths.update(
                _direct_dependency_paths(
                    expanded_arguments, working_directory, output
                )
            )
            dependency_paths.discard(self.map_path)
        if isinstance(driver_identity, dict):
            if "resolved_path" in driver_identity:
                dependency_paths.add(Path(driver_identity["resolved_path"]))
            for field in ("compiler_subtools", "link_subtools"):
                subtools = driver_identity.get(field)
                if not isinstance(subtools, dict):
                    continue
                for subtool in subtools.values():
                    if isinstance(subtool, dict) and "resolved_path" in subtool:
                        dependency_paths.add(Path(subtool["resolved_path"]))
                    if not isinstance(subtool, dict):
                        continue
                    dispatch = subtool.get("dispatcher_backend")
                    backend = (
                        dispatch.get("backend")
                        if isinstance(dispatch, dict)
                        else None
                    )
                    if isinstance(backend, dict) and "resolved_path" in backend:
                        dependency_paths.add(Path(backend["resolved_path"]))
        dependencies_before = self._snapshot_paths(
            sorted(dependency_paths), "actual-step direct dependency"
        )

        producer_chaining: list[dict[str, Any]] = []
        if kind == "final_cxx_link":
            with self._lock:
                prior_events = list(self._events)
            for expected in sorted(self.expected_objects):
                producers = [
                    event
                    for event in prior_events
                    if event.get("kind") == "cxx_compile"
                    and event.get("output") == str(expected)
                    and event.get("exit_status") == 0
                ]
                link_input = dependencies_before.get(str(expected))
                producer_output = (
                    producers[0].get("output_after")
                    if len(producers) == 1
                    else None
                )
                producer_chaining.append(
                    {
                        "input_path": str(expected),
                        "producer_sequence": (
                            producers[0].get("sequence")
                            if len(producers) == 1
                            else None
                        ),
                        "producer_output_sha256": (
                            producer_output.get("sha256")
                            if isinstance(producer_output, dict)
                            else None
                        ),
                        "consumer_input_sha256": (
                            link_input.get("sha256")
                            if isinstance(link_input, dict)
                            else None
                        ),
                        "matched": (
                            len(producers) == 1
                            and isinstance(producer_output, dict)
                            and producer_output == link_input
                        ),
                    }
                )

        started_ns = time.time_ns()
        spawn_exception: str | None = None
        try:
            result = subprocess.run(
                actual_arguments,
                cwd=self.project_root,
                env=dict(sanitized_environment),
                stdin=None,
                check=False,
                close_fds=True,
            ).returncode
        except BaseException as exc:
            spawn_exception = f"{type(exc).__name__}: {exc}"
            result = -1
        finished_ns = time.time_ns()
        source_after = (
            _artifact(source) if source is not None and source.exists() else None
        )
        output_after = (
            _artifact(output) if output is not None and output.exists() else None
        )
        map_after = (
            _artifact(self.map_path)
            if kind == "final_cxx_link" and self.map_path.exists()
            else None
        )
        dependencies_after = self._snapshot_paths(
            sorted(dependency_paths), "post-step direct dependency"
        )
        for response in response_files:
            response_path = Path(response["path"])
            response["after"] = (
                _artifact(response_path) if response_path.exists() else None
            )
            response["stable_before_and_after"] = (
                response["before"] == response["after"]
            )
        dependency_scan_after: dict[str, Any] | None = None
        if required_compile and driver_index is not None and output is not None:
            dependency_scan_after = self._dependency_scan(
                sequence=sequence,
                phase="after",
                arguments=expanded_arguments,
                driver_index=driver_index,
                output=output,
                environment=sanitized_environment,
                cwd=working_directory,
            )

        if required_compile:
            scan_stable = (
                isinstance(dependency_scan_before, dict)
                and isinstance(dependency_scan_after, dict)
                and "error" not in dependency_scan_before
                and "error" not in dependency_scan_after
                and dependency_scan_before.get("dependencies")
                == dependency_scan_after.get("dependencies")
            )
            compile_dependencies_before = dict(
                dependency_scan_before.get("dependencies", {})
                if isinstance(dependency_scan_before, dict)
                else {}
            )
            compile_dependencies_after = dict(
                dependency_scan_after.get("dependencies", {})
                if isinstance(dependency_scan_after, dict)
                else {}
            )
            compile_dependencies_before.update(dependencies_before)
            compile_dependencies_after.update(dependencies_after)
            dependencies = {
                "before": compile_dependencies_before,
                "after": compile_dependencies_after,
            }
            source_inventory_record = None
            try:
                source_relative = source.relative_to(self.project_root).as_posix()
            except (AttributeError, ValueError):
                source_relative = None
            if source_relative is not None:
                source_inventory_record = self.source_inventory.get(source_relative)
            current_source_input = compile_dependencies_before.get(str(source))
            producer_chaining.append(
                {
                    "input_path": str(source),
                    "producer_kind": "captured-source-inventory",
                    "producer_output_sha256": (
                        source_inventory_record.get("sha256")
                        if isinstance(source_inventory_record, dict)
                        else None
                    ),
                    "consumer_input_sha256": (
                        current_source_input.get("sha256")
                        if isinstance(current_source_input, dict)
                        else None
                    ),
                    "matched": source_inventory_record == current_source_input,
                }
            )
            input_stable = (
                scan_stable
                and compile_dependencies_before == compile_dependencies_after
                and producer_chaining[-1]["matched"]
            )
        elif kind == "final_cxx_link":
            dependencies = {
                "before": dependencies_before,
                "after": dependencies_after,
            }
            input_stable = (
                dependencies_before == dependencies_after
                and all(item["matched"] for item in producer_chaining)
            )
        else:
            dependencies = {
                "before": dependencies_before,
                "after": dependencies_after,
            }
            input_stable = dependencies_before == dependencies_after
        response_stable = all(
            response.get("stable_before_and_after") is True
            for response in response_files
        )
        if required_compile or kind == "final_cxx_link":
            input_stability_status = (
                "verified-before-and-after"
                if input_stable and response_stable
                else "failed"
            )
        else:
            input_stability_status = "not-required-non-target-step"
        event: dict[str, Any] = {
            "session_id": self.session_id,
            "sequence": sequence,
            "kind": kind,
            "started_time_ns": started_ns,
            "finished_time_ns": finished_ns,
            "working_directory": str(working_directory),
            "execution_policy": (
                "direct-subprocess-no-shell-v1"
                if cxx_step
                else "scons-original-spawn-non-cxx-v1"
            ),
            "shell": None if cxx_step else str(shell),
            "command": actual_arguments[0] if cxx_step else str(command),
            "escaped_arguments": escaped_arguments,
            "shell_command": shell_command,
            "argument_boundary_policy": (
                "pinned-scons-posix-shell-word-inverse-v1"
            ),
            "actual_argument_vector": actual_arguments,
            "expanded_argument_vector": expanded_arguments,
            "response_files": response_files,
            "dependencies": dependencies,
            "dependency_scans": {
                "before": dependency_scan_before,
                "after": dependency_scan_after,
            },
            "input_stability": input_stability_status,
            "input_stability_detail": {
                "verified_before_and_after": input_stability_status
                == "verified-before-and-after",
            },
            "producer_chaining": producer_chaining,
            "child_environment": (
                {
                    "policy": "sanitized-deterministic-v1",
                    "variables": sanitized_environment,
                    "cleared_variables": [
                        *CLEARED_INFLUENCE_VARIABLES,
                        "SOURCE_DATE_EPOCH",
                    ],
                    "source_date_epoch": {
                        "disposition": "cleared",
                        "value": None,
                    },
                }
                if cxx_step
                else {
                    "policy": "unmodified-non-cxx-step",
                    "variables_recorded": False,
                }
            ),
            "capture_errors": parse_errors,
            "source": str(source) if source is not None else None,
            "output": str(output) if output is not None else None,
            "source_before": source_before,
            "source_after": source_after,
            "source_stable": source_before == source_after,
            "output_before": output_before,
            "output_after": output_after,
            "output_fresh": output_before is None and output_after is not None,
            "map_before": map_before,
            "map_after": map_after,
            "map_fresh": map_before is None and map_after is not None,
            "declared_map_paths": [
                str(path)
                for path in _map_paths(expanded_arguments, working_directory)
            ],
            "driver_identity": driver_identity,
            "exit_status": result,
            "spawn_exception": spawn_exception,
        }
        encoded = (json.dumps(event, sort_keys=True) + "\n").encode("utf-8")
        with self._lock:
            with (self.output_root / "events.jsonl").open("ab") as output_file:
                output_file.write(encoded)
                output_file.flush()
                os.fsync(output_file.fileno())
            self._events.append(event)
        if spawn_exception is not None:
            raise ProvenanceError(
                f"observed SCons SPAWN raised an exception: {spawn_exception}"
            )
        return result

    def _relative_object(self, path: Path) -> str:
        try:
            return path.relative_to(self.build_root).as_posix()
        except ValueError as exc:
            raise ProvenanceError(
                f"expected object lies outside the environment build root: {path}"
            ) from exc

    def _validate_tool_identity(self, identity: Mapping[str, Any], label: str) -> None:
        if "error" in identity:
            raise ProvenanceError(f"{label} identity failed: {identity['error']}")
        for probe_name in ("version_probe", "target_probe"):
            probe = identity.get(probe_name)
            if not isinstance(probe, dict) or probe.get("exit_status") != 0:
                raise ProvenanceError(f"{label} {probe_name} did not succeed")
            if probe.get("output_truncated"):
                raise ProvenanceError(f"{label} {probe_name} output was truncated")

    def _validate_tool_dependency_binding(
        self, event: Mapping[str, Any], identity: Mapping[str, Any], label: str
    ) -> None:
        dependencies = event.get("dependencies")
        before = dependencies.get("before") if isinstance(dependencies, dict) else None
        if not isinstance(before, dict):
            raise ProvenanceError(f"{label} dependency snapshot is absent")
        path = identity.get("resolved_path")
        observed = before.get(path) if isinstance(path, str) else None
        if not isinstance(observed, dict) or observed.get("sha256") != identity.get(
            "sha256"
        ):
            raise ProvenanceError(
                f"{label} identity does not match the executable used by the step"
            )

    def _validate_selected_subtools(
        self,
        event: Mapping[str, Any],
        identity: Mapping[str, Any],
        *,
        field: str,
        expected_names: Sequence[str],
        label: str,
    ) -> None:
        subtools = identity.get(field)
        if not isinstance(subtools, dict) or set(subtools) != set(expected_names):
            raise ProvenanceError(f"{label} selected-subtool set is incomplete")
        for name in expected_names:
            subtool = subtools[name]
            if not isinstance(subtool, dict) or "error" in subtool:
                raise ProvenanceError(f"{label} selected {name} identity failed")
            selection_probe = subtool.get("selection_probe")
            if (
                not isinstance(selection_probe, dict)
                or selection_probe.get("exit_status") != 0
                or selection_probe.get("output_truncated")
            ):
                raise ProvenanceError(
                    f"{label} selected {name} path probe did not succeed"
                )
            version_probe = subtool.get("version_probe")
            if (
                not isinstance(version_probe, dict)
                or version_probe.get("exit_status") != 0
                or version_probe.get("output_truncated")
            ):
                raise ProvenanceError(
                    f"{label} selected {name} version probe did not succeed"
                )
            self._validate_tool_dependency_binding(
                event, subtool, f"{label} selected {name}"
            )
            if field == "compiler_subtools" and name == "as":
                dispatch = subtool.get("dispatcher_backend")
                if not isinstance(dispatch, dict) or "error" in dispatch:
                    raise ProvenanceError(
                        f"{label} assembler backend dispatch identity failed"
                    )
                arguments = event.get("expanded_argument_vector")
                if not isinstance(arguments, list) or dispatch.get(
                    "selector_arguments"
                ) != list(_assembler_dispatch_selector_arguments(arguments)):
                    raise ProvenanceError(
                        f"{label} assembler dispatch selectors differ from compile"
                    )
                if dispatch.get("policy") != "espressif-debug-trace-dispatch-v1":
                    raise ProvenanceError(
                        f"{label} assembler dispatch policy is unsupported"
                    )
                if dispatch.get("probe_environment") != {
                    "base": "sanitized-deterministic-v1",
                    "added_variables": {"ESP_DEBUG_TRACE": "1"},
                }:
                    raise ProvenanceError(
                        f"{label} assembler dispatch probe environment differs"
                    )
                dispatch_probe = dispatch.get("selection_probe")
                if (
                    not isinstance(dispatch_probe, dict)
                    or dispatch_probe.get("exit_status") != 0
                    or dispatch_probe.get("output_truncated")
                ):
                    raise ProvenanceError(
                        f"{label} assembler dispatch selection probe failed"
                    )
                executed = dispatch.get("executed_argument_vector")
                selectors = dispatch.get("selector_arguments")
                if (
                    not isinstance(executed, list)
                    or not executed
                    or any(not isinstance(argument, str) for argument in executed)
                    or executed[1:] != [*selectors, "--version"]
                    or dispatch_probe.get("arguments")
                    != [subtool.get("resolved_path"), *selectors, "--version"]
                ):
                    raise ProvenanceError(
                        f"{label} assembler dispatch execution vector differs"
                    )
                backend = dispatch.get("backend")
                if (
                    not isinstance(backend, dict)
                    or backend.get("invoked") != executed[0]
                ):
                    raise ProvenanceError(
                        f"{label} assembler backend identity is absent"
                    )
                backend_probe = backend.get("version_probe")
                if (
                    not isinstance(backend_probe, dict)
                    or backend_probe.get("exit_status") != 0
                    or backend_probe.get("output_truncated")
                ):
                    raise ProvenanceError(
                        f"{label} assembler backend version probe failed"
                    )
                self._validate_tool_dependency_binding(
                    event, backend, f"{label} selected assembler backend"
                )

    def _validate_link_event(
        self, event: Mapping[str, Any], expected_paths: set[Path]
    ) -> None:
        if event.get("exit_status") != 0 or event.get("spawn_exception") is not None:
            raise ProvenanceError("final link step did not complete successfully")
        if event.get("capture_errors"):
            raise ProvenanceError(
                "final link command or response files were not captured exactly"
            )
        if (
            event.get("output_before") is not None
            or event.get("map_before") is not None
        ):
            raise ProvenanceError("final ELF/map were present before the link step")
        if not event.get("output_fresh") or not event.get("map_fresh"):
            raise ProvenanceError(
                "final ELF/map were not freshly produced by the link step"
            )
        if event.get("input_stability") != "verified-before-and-after":
            raise ProvenanceError("final link input stability was not verified")
        producer_chaining = event.get("producer_chaining")
        if not isinstance(producer_chaining, list) or len(producer_chaining) != len(
            expected_paths
        ):
            raise ProvenanceError("final link producer chain is incomplete")
        if any(record.get("matched") is not True for record in producer_chaining):
            raise ProvenanceError(
                "final link input does not match its compile producer"
            )
        if event.get("declared_map_paths") != [str(self.map_path)]:
            raise ProvenanceError(
                "final link command did not declare exactly the expected firmware.map"
            )
        identity = event.get("driver_identity")
        if not isinstance(identity, dict):
            raise ProvenanceError("final link driver identity is absent")
        self._validate_tool_identity(identity, "final link driver")
        self._validate_tool_dependency_binding(event, identity, "final link driver")
        self._validate_selected_subtools(
            event,
            identity,
            field="link_subtools",
            expected_names=("collect2", "ld"),
            label="final link driver",
        )
        linker = identity.get("linker")
        if not isinstance(linker, dict) or "error" in linker:
            raise ProvenanceError("final linker's binary identity is absent")
        linker_probe = linker.get("version_probe")
        if not isinstance(linker_probe, dict) or linker_probe.get("exit_status") != 0:
            raise ProvenanceError("final linker version probe did not succeed")
        self._validate_tool_dependency_binding(event, linker, "final linker")
        arguments = event.get("expanded_argument_vector")
        if not isinstance(arguments, list):
            raise ProvenanceError("final link expanded argument vector is absent")
        observed_objects = [
            _resolve_argument_path(argument, self.project_root)
            for argument in arguments
            if isinstance(argument, str) and argument.endswith(".o")
        ]
        for expected in expected_paths:
            if observed_objects.count(expected) != 1:
                raise ProvenanceError(
                    "final link command must consume exactly one expected object: "
                    f"{expected}"
                )

    def _validate_map_loads(self, expected_paths: set[Path]) -> list[str]:
        try:
            text = self.map_path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise ProvenanceError(f"firmware.map is not readable UTF-8: {exc}") from exc
        loads = [
            match.group(1)
            for line in text.splitlines()
            if (match := MAP_LOAD.fullmatch(line)) is not None
        ]
        resolved = [_resolve_argument_path(load, self.project_root) for load in loads]
        for expected in expected_paths:
            if resolved.count(expected) != 1:
                raise ProvenanceError(
                    "firmware.map must contain exactly one direct LOAD for expected "
                    f"object: {expected}"
                )
        return loads

    def _validate_inventory_unchanged(self) -> None:
        for relative, before in self.source_inventory.items():
            path = self.project_root / PurePosixPath(relative)
            after = _artifact(path)
            if after != before:
                raise ProvenanceError(
                    f"selected source/build input changed during capture: {relative}"
                )

    def _write_failure(self, error: BaseException) -> None:
        failure_path = self.output_root / "failure.json"
        if failure_path.exists():
            return
        _atomic_json(
            failure_path,
            {
                "schema_version": SCHEMA_VERSION,
                "evidence_kind": EVIDENCE_KIND,
                "status": "failed",
                "session_id": self.session_id,
                "environment": ENVIRONMENT,
                "error": f"{type(error).__name__}: {error}",
                "events_recorded": len(self._events),
            },
            exclusive=True,
        )

    def _load_and_validate_raw_events(
        self, expected_events: Sequence[Mapping[str, Any]]
    ) -> tuple[Path, list[dict[str, Any]], list[dict[str, Any]]]:
        """Bind the final report to the exact append-only JSONL event bytes."""

        event_log = self.output_root / "events.jsonl"
        if event_log.is_symlink():
            raise ProvenanceError("raw provenance event log is a symlink")
        event_log = _regular_file(event_log, "raw provenance event log")
        try:
            encoded = event_log.read_bytes()
        except OSError as exc:
            raise ProvenanceError(
                f"raw provenance event log is unreadable: {exc}"
            ) from exc
        if not encoded or not encoded.endswith(b"\n"):
            raise ProvenanceError(
                "raw provenance event log is empty or lacks its final newline"
            )
        raw_events: list[dict[str, Any]] = []
        line_records: list[dict[str, Any]] = []
        for line_number, line in enumerate(encoded.splitlines(keepends=True), 1):
            try:
                event = json.loads(line.decode("utf-8", errors="strict"))
            except (UnicodeError, json.JSONDecodeError) as exc:
                raise ProvenanceError(
                    f"raw provenance event {line_number} is invalid JSON: {exc}"
                ) from exc
            if not isinstance(event, dict):
                raise ProvenanceError(
                    f"raw provenance event {line_number} is not an object"
                )
            canonical = (json.dumps(event, sort_keys=True) + "\n").encode("utf-8")
            if line != canonical:
                raise ProvenanceError(
                    f"raw provenance event {line_number} is not the exact "
                    "canonical recorder encoding"
                )
            raw_events.append(event)
            line_records.append(
                {
                    "line_number": line_number,
                    "sequence": event.get("sequence"),
                    "size": len(line),
                    "sha256": sha256_bytes(line),
                }
            )
        if raw_events != list(expected_events):
            raise ProvenanceError(
                "raw provenance event log differs from the in-memory actual-step "
                "records"
            )
        return event_log, raw_events, line_records

    def finalize(self) -> dict[str, Any]:
        """Validate the same-invocation capture and create the final report."""

        with self._lock:
            if self._finalized:
                raise ProvenanceError("provenance session was finalized more than once")
            self._finalized = True
            expected_events = list(self._events)
        try:
            if not expected_events:
                raise ProvenanceError(
                    "capture requires exactly one executed C++ compile for every "
                    "selected target; observed no actual steps"
                )
            event_log, events, raw_event_lines = self._load_and_validate_raw_events(
                expected_events
            )
            expected_paths = set(self.expected_objects)
            compile_events = [
                event for event in events if event.get("kind") == "cxx_compile"
            ]
            required_events: dict[Path, dict[str, Any]] = {}
            for output, source in self.expected_objects.items():
                matches = [
                    event
                    for event in compile_events
                    if event.get("output") == str(output)
                ]
                if len(matches) != 1:
                    raise ProvenanceError(
                        "capture requires exactly one executed C++ compile for "
                        f"{self._relative_object(output)}; observed {len(matches)}"
                    )
                event = matches[0]
                if event.get("source") != str(source):
                    raise ProvenanceError(
                        f"compile source mismatch for {self._relative_object(output)}"
                    )
                if (
                    event.get("exit_status") != 0
                    or event.get("spawn_exception") is not None
                ):
                    raise ProvenanceError(
                        f"compile failed for {self._relative_object(output)}"
                    )
                if event.get("capture_errors"):
                    raise ProvenanceError(
                        "compile command or response files were not captured "
                        "exactly for "
                        f"{self._relative_object(output)}"
                    )
                if event.get("output_before") is not None:
                    raise ProvenanceError(
                        "required object existed before its compile producer: "
                        f"{self._relative_object(output)}"
                    )
                if not event.get("output_fresh") or not event.get("source_stable"):
                    raise ProvenanceError(
                        "compile did not freshly produce an object from a stable "
                        "source: "
                        f"{self._relative_object(output)}"
                    )
                if event.get("input_stability") != "verified-before-and-after":
                    raise ProvenanceError(
                        "transitive compile input stability was not verified for "
                        f"{self._relative_object(output)}"
                    )
                chaining = event.get("producer_chaining")
                if not isinstance(chaining, list) or any(
                    record.get("matched") is not True for record in chaining
                ):
                    raise ProvenanceError(
                        "compile input producer chain is incomplete for "
                        f"{self._relative_object(output)}"
                    )
                identity = event.get("driver_identity")
                if not isinstance(identity, dict):
                    raise ProvenanceError(
                        f"compiler identity absent for {self._relative_object(output)}"
                    )
                self._validate_tool_identity(
                    identity, f"compiler for {self._relative_object(output)}"
                )
                self._validate_tool_dependency_binding(
                    event,
                    identity,
                    f"compiler for {self._relative_object(output)}",
                )
                self._validate_selected_subtools(
                    event,
                    identity,
                    field="compiler_subtools",
                    expected_names=("cc1plus", "as"),
                    label=f"compiler for {self._relative_object(output)}",
                )
                required_events[output] = event

            link_events = [
                event for event in events if event.get("kind") == "final_cxx_link"
            ]
            if len(link_events) != 1:
                raise ProvenanceError(
                    "capture requires exactly one executed final firmware.elf link; "
                    f"observed {len(link_events)}"
                )
            link_event = link_events[0]
            self._validate_link_event(link_event, expected_paths)
            map_loads = self._validate_map_loads(expected_paths)
            self._validate_inventory_unchanged()

            runtime_after = (
                json.loads(json.dumps(self._runtime_refresh()))
                if self._runtime_refresh is not None
                else json.loads(json.dumps(self.capture_runtime))
            )
            if runtime_after != self.capture_runtime:
                raise ProvenanceError(
                    "Python/PlatformIO/SCons capture runtime changed during build"
                )
            capture_runtime = {
                "input_stability": "verified-before-and-after",
                "before": self.capture_runtime,
                "after": runtime_after,
            }

            identity_header_path = _regular_file(
                self.project_root
                / PurePosixPath(
                    self.local_build_identity["generated_header"]
                ),
                "generated qualification build-identity header",
            )
            identity_consumer_path = _regular_file(
                self.project_root
                / PurePosixPath(self.local_build_identity["consumer"]),
                "qualification build-identity consumer",
            )
            identity_header_key = str(identity_header_path)
            for output, event in required_events.items():
                dependencies = event.get("dependencies")
                before = (
                    dependencies.get("before")
                    if isinstance(dependencies, dict)
                    else None
                )
                after = (
                    dependencies.get("after")
                    if isinstance(dependencies, dict)
                    else None
                )
                if not isinstance(before, dict) or not isinstance(after, dict):
                    raise ProvenanceError(
                        "compile dependency snapshots are absent while checking "
                        "local build identity"
                    )
                is_consumer = self.expected_objects[output] == identity_consumer_path
                if is_consumer:
                    expected_identity_artifact = self.local_build_identity[
                        "artifact"
                    ]
                    if (
                        before.get(identity_header_key)
                        != expected_identity_artifact
                        or after.get(identity_header_key)
                        != expected_identity_artifact
                    ):
                        raise ProvenanceError(
                            "boot compile did not consume the captured local "
                            "build-identity header"
                        )
                elif identity_header_key in before or identity_header_key in after:
                    raise ProvenanceError(
                        "generated build identity leaked into non-boot object "
                        f"{self._relative_object(output)}"
                    )

            objects: dict[str, dict[str, Any]] = {}
            required_compile_records: list[dict[str, Any]] = []
            for output in sorted(expected_paths):
                current = _artifact(output)
                event = required_events[output]
                if current != event.get("output_after"):
                    raise ProvenanceError(
                        "compiled object changed after its captured compile step: "
                        f"{self._relative_object(output)}"
                    )
                assert current is not None
                relative = self._relative_object(output)
                objects[relative] = current
                required_compile_records.append(event)
            elf = _artifact(self.elf_path)
            map_artifact = _artifact(self.map_path)
            if elf != link_event.get("output_after"):
                raise ProvenanceError(
                    "firmware.elf changed after the captured final link"
                )
            if map_artifact != link_event.get("map_after"):
                raise ProvenanceError(
                    "firmware.map changed after the captured final link"
                )
            assert elf is not None and map_artifact is not None
            try:
                elf_bytes = self.elf_path.read_bytes()
            except OSError as exc:
                raise ProvenanceError(
                    f"firmware.elf is unreadable for identity binding: {exc}"
                ) from exc
            identity_elf_strings: dict[str, dict[str, Any]] = {}
            for name, value in self.local_build_identity["definitions"].items():
                occurrences = elf_bytes.count(value.encode("ascii"))
                if occurrences < 1:
                    raise ProvenanceError(
                        f"firmware.elf lacks local build-identity value {name}"
                    )
                identity_elf_strings[name] = {
                    "value": value,
                    "ascii_occurrences": occurrences,
                }

            compiler_identities: dict[str, dict[str, Any]] = {}
            compiler_subtool_identities: dict[str, dict[str, Any]] = {}
            for event in required_compile_records:
                identity = event["driver_identity"]
                key = f"{identity['resolved_path']}:{identity['sha256']}"
                compiler_identities[key] = identity
                for name, subtool in identity["compiler_subtools"].items():
                    subtool_key = (
                        f"{name}:{subtool['resolved_path']}:{subtool['sha256']}"
                    )
                    compiler_subtool_identities[subtool_key] = subtool
            report = {
                "schema_version": SCHEMA_VERSION,
                "evidence_kind": EVIDENCE_KIND,
                "status": "complete",
                "session_id": self.session_id,
                "environment": ENVIRONMENT,
                "started_time_ns": self.started_ns,
                "completed_time_ns": time.time_ns(),
                "source_selection": {
                    "path": str(self.selection_path),
                    "sha256": sha256_file(self.selection_path),
                },
                "capture_runtime": capture_runtime,
                "source_and_build_input_inventory": self.source_inventory,
                "translation_unit_local_build_identity": {
                    **self.local_build_identity,
                    "final_elf_strings": identity_elf_strings,
                },
                "capture": {
                    "all_cxx_compile_steps": compile_events,
                    "required_target_compiles": required_compile_records,
                    "final_link": link_event,
                    "firmware_map_direct_loads": map_loads,
                },
                "artifacts": {
                    "objects": objects,
                    "elf": elf,
                    "map": map_artifact,
                },
                "tools": {
                    "compile_drivers": list(compiler_identities.values()),
                    "compiler_selected_subtools": list(
                        compiler_subtool_identities.values()
                    ),
                    "link_driver": link_event["driver_identity"],
                    "link_driver_selected_subtools": link_event[
                        "driver_identity"
                    ]["link_subtools"],
                    "linker": link_event["driver_identity"]["linker"],
                },
                "raw_event_log_sha256": sha256_file(event_log),
                "raw_event_lines": raw_event_lines,
                "checked_claims": {
                    "actual_scons_compile_steps_observed": True,
                    "actual_scons_final_link_step_observed": True,
                    "required_objects_fresh_and_hashed": True,
                    "final_elf_and_map_fresh_and_hashed": True,
                    "required_objects_present_in_link_command": True,
                    "required_objects_present_as_direct_map_loads": True,
                    "response_file_bytes_preserved": True,
                    "compiler_reported_target_compile_inputs_stable": True,
                    "compile_to_final_link_producer_chaining_proved": True,
                    "required_policy_unit_final_link_inputs_proved": True,
                    "complete_implicit_default_or_library_link_input_closure_proved": False,
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
                },
            }
            _atomic_json(
                self.output_root / "provenance.json", report, exclusive=True
            )
            session = json.loads(
                (self.output_root / "session.json").read_text(encoding="utf-8")
            )
            session["status"] = "complete"
            session["completed_time_ns"] = report["completed_time_ns"]
            session["report_sha256"] = sha256_file(
                self.output_root / "provenance.json"
            )
            session["capture_runtime"] = capture_runtime
            _atomic_json(
                self.output_root / "session.json", session, exclusive=False
            )
            return report
        except BaseException as exc:
            self._write_failure(exc)
            raise


def install(env: Any) -> CaptureSession | None:
    """Install the qualification-only SCons wrapper when explicitly enabled."""

    environment = env.subst("$PIOENV")
    if environment != ENVIRONMENT:
        raise ProvenanceError(
            f"P4 actual-step capture is forbidden for environment {environment!r}"
        )
    requested = os.environ.get(OUTPUT_VARIABLE)
    if not requested:
        return None
    if env.IsCleanTarget():
        raise ProvenanceError(
            f"unset {OUTPUT_VARIABLE} while cleaning; capture requires a subsequent "
            "fresh build with a new evidence directory"
        )
    try:
        import platformio
        import SCons
    except ImportError as exc:  # pragma: no cover - available inside PlatformIO
        raise ProvenanceError(f"cannot identify PlatformIO/SCons: {exc}") from exc
    # Cache files are executable inputs too. Prevent the capture invocation from
    # mutating them after the complete installed package trees are inventoried.
    sys.dont_write_bytecode = True
    project_root = Path(env.subst("$PROJECT_DIR")).resolve(strict=True)
    build_root = Path(env.subst("$BUILD_DIR")).resolve(strict=True)
    # PlatformIO/SCons executes extra scripts with exec(), not as imported
    # Python modules, so __file__ is not part of that execution namespace.
    # The qualification hook is a committed project-relative build boundary;
    # resolve that exact path from SCons' authoritative PROJECT_DIR instead.
    hook_path = project_root / "pio/capture_p4_actual_steps.py"
    session = CaptureSession(
        project_root=project_root,
        build_root=build_root,
        output_root=Path(requested),
        selection_path=(
            project_root
            / "pio/p4-port008-nonrelease-qualification-source-selection.json"
        ),
        hook_path=hook_path,
        platformio_version=platformio.__version__,
        scons_version=SCons.__version__,
        capture_runtime=_capture_runtime_identity(platformio, SCons),
        runtime_refresh=lambda: _capture_runtime_identity(platformio, SCons),
    )
    original_spawn = env["SPAWN"]

    def capture_spawn(shell, escape, command, arguments, spawn_environment):
        return session.spawn(
            original_spawn,
            shell,
            escape,
            command,
            arguments,
            spawn_environment,
        )

    def finalize_capture(target, source, action_environment):
        session.finalize()
        return 0

    env.Replace(
        SPAWN=capture_spawn,
        TEMPFILE=_persistent_tempfile_class(session.output_root),
    )
    env.AddPreAction(
        "checkprogsize",
        env.VerboseAction(
            finalize_capture,
            "Finalizing fail-closed P4 actual-step provenance",
        ),
    )
    return session


# SCons injects Import when executing this file as an extra script.  Leaving
# ordinary Python import inert makes the capture core directly testable.
try:  # pragma: no cover - exercised by PlatformIO, not host unit tests
    Import  # type: ignore[name-defined]
except NameError:
    pass
else:
    Import("env")  # type: ignore[name-defined]
    install(env)  # type: ignore[name-defined]
