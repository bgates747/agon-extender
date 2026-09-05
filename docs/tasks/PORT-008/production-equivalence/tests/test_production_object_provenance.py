from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[5]
SCRIPT = (
    ROOT
    / "docs/tasks/PORT-008/production-equivalence/scripts/"
    "validate-production-object-provenance.py"
)
POLICY = (
    ROOT
    / "docs/tasks/PORT-008/production-equivalence/object-equivalence/"
    "production-object-policy.json"
)
SPEC = importlib.util.spec_from_file_location("production_object_gate", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
gate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = gate
SPEC.loader.exec_module(gate)


def artifact(path: Path) -> dict[str, object]:
    metadata = path.stat()
    return {
        "path": str(path.resolve()),
        "size": metadata.st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "inode": metadata.st_ino,
        "mtime_ns": metadata.st_mtime_ns,
        "ctime_ns": metadata.st_ctime_ns,
    }


def rooted(name: str, path: Path, *, allow_symlink: bool = False):
    return gate.RootBinding(name, path, path.resolve(), allow_symlink)


class ProductionObjectPolicyTests(unittest.TestCase):
    def policy(self):
        return json.loads(POLICY.read_text())

    def test_current_policy_owns_exact_targets_boundaries_and_project_root(self):
        policy = gate.validate_policy(self.policy())
        self.assertEqual({"emos", "p4"}, set(policy["targets"]))
        self.assertEqual(
            [
                "PORT008-PROV-P023",
                "PORT008-PROV-P024",
                "PORT008-PROV-P025",
                "PORT008-PROV-P026",
                "PORT008-PROV-P027",
                "PORT008-PROV-P028",
                "PORT008-PROV-P029",
                "PORT008-PROV-P030",
                "PORT008-PROV-P031",
            ],
            [item["id"] for item in policy["known_open_boundaries"]],
        )
        self.assertEqual("vdp", policy["targets"]["p4"]["project_relative"])
        self.assertIn("PYTHON_RUNTIME", policy["targets"]["p4"]["required_roots"])

    def test_policy_rejects_shrunk_role_and_unknown_unit_field(self):
        policy = self.policy()
        policy["targets"]["emos"]["roles"]["qualification"]["required_units"].pop(0)
        with self.assertRaisesRegex(gate.GateError, "command-fingerprint|role presence"):
            gate.validate_policy(policy)
        policy = self.policy()
        policy["targets"]["p4"]["units"][0]["evidence_can_override"] = True
        with self.assertRaisesRegex(gate.GateError, "fields differ"):
            gate.validate_policy(policy)

    def test_policy_rejects_boolean_integer_fields(self):
        policy = self.policy()
        policy["schema_version"] = True
        with self.assertRaisesRegex(gate.GateError, "must be an integer"):
            gate.validate_policy(policy)

    def test_policy_requires_exact_composition_dependency_delta(self):
        def owner(policy):
            return next(
                unit
                for unit in policy["targets"]["emos"]["units"]
                if unit["id"] == "emos-mode-coordinator"
            )

        policy = self.policy()
        del owner(policy)["expected_dependency_delta"]
        with self.assertRaisesRegex(gate.GateError, "fields differ"):
            gate.validate_policy(policy)

        invalid = (
            {"qualification_only": "not-a-list", "release_only": []},
            {
                "qualification_only": ["${UNKNOWN}/header.h"],
                "release_only": [],
            },
            {
                "qualification_only": ["${PREPARED}/a/../header.h"],
                "release_only": [],
            },
            {
                "qualification_only": ["${PREPARED}/header.h"],
                "release_only": ["${PREPARED}/header.h"],
            },
        )
        for value in invalid:
            policy = self.policy()
            owner(policy)["expected_dependency_delta"] = value
            with self.subTest(value=value), self.assertRaises(gate.GateError):
                gate.validate_policy(policy)
        policy = self.policy()
        wrapped = next(
            unit
            for unit in policy["targets"]["emos"]["units"]
            if unit["producer_kind"] == "wrapped-assembly"
        )
        wrapped["generator"]["manifest_schema"] = True
        with self.assertRaisesRegex(gate.GateError, "must be an integer"):
            gate.validate_policy(policy)

    def test_policy_rejects_escaping_or_noncanonical_output_suffixes(self):
        for target_name, field in (
            ("emos", "final_image_suffix"),
            ("emos", "link_map_suffix"),
            ("p4", "final_image_suffix"),
            ("p4", "link_map_suffix"),
        ):
            for value in ("/../outside", "//outside", "/./outside", "/"):
                policy = self.policy()
                policy["targets"][target_name][field] = value
                with self.subTest(target=target_name, field=field, value=value):
                    with self.assertRaises(gate.GateError):
                        gate.validate_policy(policy)
        policy = self.policy()
        policy["targets"]["emos"]["units"][0]["object_suffix"] = "/../outside.o"
        with self.assertRaisesRegex(gate.GateError, "normalized relative path"):
            gate.validate_policy(policy)

    def test_policy_rejects_missing_known_boundary(self):
        policy = self.policy()
        policy["known_open_boundaries"].pop()
        with self.assertRaisesRegex(gate.GateError, "boundary set"):
            gate.validate_policy(policy)

    def test_registry_artifact_index_rejects_ambiguous_records(self):
        self.assertEqual(
            {"one": {"artifact_id": "one"}},
            gate.identity_registry_artifacts(
                {"artifacts": [{"artifact_id": "one"}]}
            ),
        )
        invalid = (
            {"artifacts": {}},
            {"artifacts": ["not-a-record"]},
            {"artifacts": [{}]},
            {"artifacts": [{"artifact_id": ""}]},
            {
                "artifacts": [
                    {"artifact_id": "duplicate"},
                    {"artifact_id": "duplicate"},
                ]
            },
        )
        for registry in invalid:
            with self.subTest(registry=registry), self.assertRaises(
                gate.GateError
            ):
                gate.identity_registry_artifacts(registry)

    def test_build_id_requires_real_utc_calendar_timestamp(self):
        source = "agon-emos-v1.2.3"
        self.assertTrue(
            gate.build_id_matches_source(
                "agon-emos-v1.2.3-b2028-02-29-23-59-59Z", source
            )
        )
        invalid = (
            "agon-emos-v1.2.3-b2027-02-29-23-59-59Z",
            "agon-emos-v1.2.3-b2028-02-30-23-59-59Z",
            "agon-emos-v1.2.3-b2028-12-01-24-00-00Z",
            "agon-emos-v1.2.3-b2028-12-01-23-60-00Z",
            "other-v1.2.3-b2028-12-01-23-59-59Z",
        )
        for build_id in invalid:
            with self.subTest(build_id=build_id):
                self.assertFalse(gate.build_id_matches_source(build_id, source))


class PathAndEnvironmentTests(unittest.TestCase):
    def test_literal_reserved_placeholder_is_rejected_before_root_normalization(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary).resolve()
            roots = {"PROJECT": rooted("PROJECT", project)}
            actual = f"-DVALUE={project}/include"
            forged = "-DVALUE=${PROJECT}/include"
            self.assertEqual(
                gate.normalize_external_text(actual, roots),
                gate.normalize_external_text(forged, roots),
            )
            gate.reject_reserved_root_placeholder(actual, "actual argument")
            with self.assertRaisesRegex(
                gate.GateError, "literal reserved root placeholder"
            ):
                gate.reject_reserved_root_placeholder(forged, "forged argument")

    def test_generator_text_digest_matches_universal_newline_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.inc"
            source.write_bytes(b"first\r\nsecond\rthird\n")
            self.assertNotEqual(
                hashlib.sha256(source.read_bytes()).hexdigest(),
                gate.sha256_generator_text_input(source, "synthetic source"),
            )
            self.assertEqual(
                hashlib.sha256(b"first\nsecond\nthird\n").hexdigest(),
                gate.sha256_generator_text_input(source, "synthetic source"),
            )

    def test_generator_text_digest_rejects_non_utf8_input(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "source.inc"
            source.write_bytes(b"\xff")
            with self.assertRaisesRegex(gate.GateError, "generator UTF-8 input"):
                gate.sha256_generator_text_input(source, "synthetic source")

    def test_strict_root_rejects_symlinked_ancestor(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            real = base / "real"
            child = real / "child"
            child.mkdir(parents=True)
            alias = base / "alias"
            alias.symlink_to(real, target_is_directory=True)
            policy = {
                "required_roots": ["STRICT"],
                "root_policy": {"STRICT": {"allow_symlink": False}},
            }
            with self.assertRaisesRegex(gate.GateError, "symbolic link"):
                gate.parse_root_arguments([f"STRICT={alias / 'child'}"], policy)

    def test_root_bindings_require_absolute_cli_paths(self):
        policy = {
            "required_roots": ["ROOT"],
            "root_policy": {"ROOT": {"allow_symlink": False}},
        }
        for value in (".", "docs"):
            with self.subTest(value=value), self.assertRaisesRegex(
                gate.GateError, "must be absolute"
            ):
                gate.parse_root_arguments([f"ROOT={value}"], policy)

    def test_root_leaf_symlink_does_not_authorize_descendant_symlinks(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            real = base / "real"
            real.mkdir()
            ordinary = real / "ordinary"
            ordinary.write_text("inside\n", encoding="utf-8")
            outside = base / "outside"
            outside.write_text("outside\n", encoding="utf-8")
            (real / "escaped").symlink_to(outside)
            alias = base / "alias"
            alias.symlink_to(real, target_is_directory=True)
            policy = {
                "required_roots": ["OPEN"],
                "root_policy": {"OPEN": {"allow_symlink": True}},
            }
            roots = gate.parse_root_arguments([f"OPEN={alias}"], policy)
            self.assertEqual(
                ordinary,
                gate.resolve_rooted_path(
                    "${OPEN}/ordinary", roots, "ordinary rooted file"
                ),
            )
            with self.assertRaisesRegex(gate.GateError, "symbolic link"):
                gate.resolve_rooted_path(
                    "${OPEN}/escaped", roots, "escaped rooted file"
                )

    def test_root_leaf_symlink_retarget_is_rejected_even_within_original_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            real = base / "real"
            inner = real / "inner"
            sibling = base / "sibling"
            inner.mkdir(parents=True)
            sibling.mkdir()
            (real / "file").write_text("original\n", encoding="utf-8")
            (inner / "file").write_text("inner\n", encoding="utf-8")
            (sibling / "file").write_text("sibling\n", encoding="utf-8")
            alias = base / "alias"
            alias.symlink_to(real, target_is_directory=True)
            policy = {
                "required_roots": ["OPEN"],
                "root_policy": {"OPEN": {"allow_symlink": True}},
            }
            roots = gate.parse_root_arguments([f"OPEN={alias}"], policy)
            for target in (inner, sibling):
                alias.unlink()
                alias.symlink_to(target, target_is_directory=True)
                with self.subTest(target=target), self.assertRaisesRegex(
                    gate.GateError, "declared root changed"
                ):
                    gate.resolve_rooted_path(
                        "${OPEN}/file", roots, "retargeted rooted file"
                    )

    def test_rooted_path_rejects_double_slash_absolute_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "root"
            root.mkdir()
            outside = base / "outside"
            outside.write_text("outside\n", encoding="utf-8")
            roots = {"OPEN": rooted("OPEN", root, allow_symlink=True)}
            escaped = "${OPEN}/" + outside.as_posix()
            with self.assertRaisesRegex(gate.GateError, "normalized relative path"):
                gate.resolve_rooted_path(escaped, roots, "escaped rooted file")
            with self.assertRaisesRegex(gate.GateError, "normalized relative path"):
                gate.expanded_policy_location(escaped, roots, "escaped policy file")

    def test_rooted_path_rejects_noncanonical_suffixes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate"
            candidate.write_text("inside\n", encoding="utf-8")
            roots = {"ROOT": rooted("ROOT", root)}
            for value in (
                "${ROOT}/.",
                "${ROOT}/candidate/",
                "${ROOT}/./candidate",
                "${ROOT}/child/../candidate",
                "${ROOT}/child//candidate",
                "${ROOT}/child\\candidate",
            ):
                with self.subTest(value=value), self.assertRaises(gate.GateError):
                    gate.resolve_rooted_existing_path(value, roots, "rooted path")
            with self.assertRaises(gate.GateError):
                gate.safe_relative("part\x00name", "NUL path")

    def test_rooted_path_rejects_unknown_root_and_special_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fifo = root / "fifo"
            os.mkfifo(fifo)
            roots = {"ROOT": rooted("ROOT", root)}
            with self.assertRaisesRegex(gate.GateError, "declared root"):
                gate.resolve_rooted_path(
                    "${UNKNOWN}/fifo", roots, "unknown rooted file"
                )
            with self.assertRaisesRegex(gate.GateError, "not a regular file"):
                gate.resolve_rooted_path("${ROOT}/fifo", roots, "special rooted file")

    def test_working_directory_rejects_parent_escape(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "build"
            root.mkdir()
            roots = {"BUILD": rooted("BUILD", root)}
            with self.assertRaisesRegex(gate.GateError, "normalized relative path"):
                gate.normalized_working_directory(
                    "${BUILD}/../outside", roots, "synthetic"
                )

    def test_emos_environment_is_exact_not_label_only(self):
        policy = json.loads(POLICY.read_text())["targets"]["emos"]
        environment = {
            "policy": "sanitized-deterministic-v1",
            "variables": {"LANG": "C", "LC_ALL": "C", "PATH": "/usr/bin:/bin"},
            "cleared_variables": list(
                policy["environment_policy"]["exact_cleared_variables"]
            ),
            "source_date_epoch": {"disposition": "cleared", "value": None},
        }
        self.assertEqual(
            environment,
            gate.validate_environment(
                environment, policy["environment_policy"], {}, "EMOS environment"
            ),
        )
        changed = copy.deepcopy(environment)
        changed["variables"]["CPATH"] = "/tmp/injected"
        with self.assertRaises(gate.GateError):
            gate.validate_environment(
                changed, policy["environment_policy"], {}, "EMOS environment"
            )

    def test_only_authenticated_session_marker_is_removed_from_cross_role_inputs(self):
        session = {"path": "${PROVENANCE}/.mos-session.json", "sha256": "session", "size": 1}
        recorder = {"path": "${BUILD_TOOL}/recorder.py", "sha256": "recorder", "size": 2}
        semantic = {"path": "${PREPARED}/src/header.h", "sha256": "semantic", "size": 3}
        step = gate.StepView(
            Path("record.json"),
            "record",
            {
                "session": session,
                "declared_inputs": [session, recorder, semantic],
            },
            Path("source"),
            Path("object"),
            ("compiler",),
            (),
        )
        self.assertEqual(
            [recorder, semantic],
            gate.normalized_declared_inputs(step),
        )

    def test_command_path_positions_ignores_existing_rooted_include_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            toolchain = root / "toolchain"
            include = toolchain / "include"
            prepared = root / "prepared"
            include.mkdir(parents=True)
            prepared.mkdir()
            source = prepared / "source.c"
            source.write_text("int source;\n", encoding="utf-8")
            roots = {
                "TOOLCHAIN": rooted("TOOLCHAIN", toolchain),
                "PREPARED": rooted("PREPARED", prepared),
            }
            command = [
                "compiler",
                "-isystem",
                "${TOOLCHAIN}/include",
                "-c",
                "${PREPARED}/source.c",
            ]
            self.assertEqual(
                [4],
                gate.command_path_positions(
                    command,
                    "${PREPARED}/source.c",
                    roots,
                    root,
                    "synthetic source",
                ),
            )

    def test_command_path_positions_rejects_malformed_root_placeholder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.c"
            source.write_text("int source;\n", encoding="utf-8")
            roots = {"PREPARED": rooted("PREPARED", root)}
            with self.assertRaisesRegex(gate.GateError, "malformed root placeholder"):
                gate.command_path_positions(
                    ["compiler", "${PREPARED/source.c", "${PREPARED}/source.c"],
                    "${PREPARED}/source.c",
                    roots,
                    root,
                    "synthetic source",
                )

    def test_command_path_positions_rejects_missing_rooted_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.c"
            source.write_text("int source;\n", encoding="utf-8")
            roots = {"PREPARED": rooted("PREPARED", root)}
            with self.assertRaisesRegex(gate.GateError, "does not exist|unavailable"):
                gate.command_path_positions(
                    ["compiler", "${PREPARED}/missing", "${PREPARED}/source.c"],
                    "${PREPARED}/source.c",
                    roots,
                    root,
                    "synthetic source",
                )

    def test_command_path_positions_matches_only_the_source_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.c"
            other = root / "other.c"
            source.write_text("int source;\n", encoding="utf-8")
            other.write_text("int other;\n", encoding="utf-8")
            roots = {"PREPARED": rooted("PREPARED", root)}
            self.assertEqual(
                [3],
                gate.command_path_positions(
                    [
                        "compiler",
                        "${PREPARED}/other.c",
                        "-c",
                        "${PREPARED}/source.c",
                    ],
                    "${PREPARED}/source.c",
                    roots,
                    root,
                    "synthetic source",
                ),
            )

    def test_command_path_positions_rejects_any_hardlink_source_alias(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source.c"
            alias = root / "alias.c"
            source.write_text("int source;\n", encoding="utf-8")
            alias.hardlink_to(source)
            roots = {"PREPARED": rooted("PREPARED", root)}
            for command in (
                ["compiler", "${PREPARED}/alias.c", "-c"],
                [
                    "compiler",
                    "${PREPARED}/alias.c",
                    "-c",
                    "${PREPARED}/source.c",
                ],
            ):
                with self.subTest(command=command), self.assertRaisesRegex(
                    gate.GateError, "hardlink alias"
                ):
                    gate.command_path_positions(
                        command,
                        "${PREPARED}/source.c",
                        roots,
                        root,
                        "synthetic source",
                    )

    def test_file_identity_registration_rejects_nested_and_hardlink_aliases(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            canonical = root / "canonical"
            hardlink = root / "hardlink"
            canonical.write_text("input\n", encoding="utf-8")
            hardlink.hardlink_to(canonical)
            seen: set[Path] = set()
            gate.register_unique_file_path(canonical, seen, "synthetic records")
            with self.assertRaisesRegex(gate.GateError, "duplicate resolved file"):
                gate.register_unique_file_path(canonical, seen, "synthetic records")
            with self.assertRaisesRegex(gate.GateError, "hardlink alias"):
                gate.register_unique_file_path(hardlink, seen, "synthetic records")

    def test_predeclared_record_accepts_nested_root_spelling_not_hardlink(self):
        with tempfile.TemporaryDirectory() as temporary:
            build_tool = Path(temporary) / "build-tool"
            build = build_tool / "projects/mos-port"
            canonical = build / "input"
            hardlink = build / "hardlink"
            canonical.parent.mkdir(parents=True)
            canonical.write_text("input\n", encoding="utf-8")
            hardlink.hardlink_to(canonical)
            roots = {
                "BUILD_TOOL": rooted("BUILD_TOOL", build_tool),
                "BUILD": rooted("BUILD", build),
            }
            declared = {
                "path": "${BUILD_TOOL}/projects/mos-port/input",
                "sha256": hashlib.sha256(canonical.read_bytes()).hexdigest(),
                "size": canonical.stat().st_size,
            }
            nested = {**declared, "path": "${BUILD}/input"}
            hardlinked = {**declared, "path": "${BUILD}/hardlink"}
            declared_path = gate.verify_file_record(declared, roots, "declared")
            nested_path = gate.verify_file_record(nested, roots, "nested")
            gate.require_predeclared_file_record(
                nested, nested_path, {declared_path: declared}, "nested input"
            )
            hardlink_path = gate.verify_file_record(hardlinked, roots, "hardlink")
            with self.assertRaisesRegex(gate.GateError, "hardlink alias"):
                gate.require_predeclared_file_record(
                    hardlinked,
                    hardlink_path,
                    {declared_path: declared},
                    "hardlinked input",
                )

    def test_file_record_rejects_boolean_size(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate"
            candidate.write_bytes(b"x")
            roots = {"ROOT": rooted("ROOT", root)}
            record = {
                "path": "${ROOT}/candidate",
                "sha256": hashlib.sha256(b"x").hexdigest(),
                "size": True,
            }
            with self.assertRaisesRegex(gate.GateError, "nonnegative integer"):
                gate.verify_file_record(record, roots, "synthetic file")
            record["size"] = 2
            with self.assertRaisesRegex(gate.GateError, "size mismatch"):
                gate.verify_file_record(record, roots, "synthetic file")

    def test_file_record_identity_accepts_one_nested_root_spelling(self):
        with tempfile.TemporaryDirectory() as temporary:
            build_tool = Path(temporary) / "build-tool"
            build = build_tool / "projects/mos-port"
            recorder = build / "tools/recorder.py"
            recorder.parent.mkdir(parents=True)
            recorder.write_text("# recorder\n", encoding="utf-8")
            roots = {
                "BUILD_TOOL": rooted("BUILD_TOOL", build_tool),
                "BUILD": rooted("BUILD", build),
            }
            canonical = gate.rooted_policy_record(
                "BUILD_TOOL",
                "projects/mos-port/tools/recorder.py",
                roots,
                "synthetic recorder",
            )
            nested = {**canonical, "path": "${BUILD}/tools/recorder.py"}
            self.assertTrue(
                gate.file_records_same_identity(
                    canonical, nested, roots, "synthetic recorder"
                )
            )

    def test_declared_policy_file_accepts_one_exact_nested_root_alias(self):
        with tempfile.TemporaryDirectory() as temporary:
            build_tool = Path(temporary) / "build-tool"
            build = build_tool / "projects/mos-port"
            generator = build / "tools/generator.py"
            generator.parent.mkdir(parents=True)
            generator.write_text("# generator\n", encoding="utf-8")
            roots = {
                "BUILD_TOOL": rooted("BUILD_TOOL", build_tool),
                "BUILD": rooted("BUILD", build),
            }
            expected = gate.rooted_policy_record(
                "BUILD_TOOL",
                "projects/mos-port/tools/generator.py",
                roots,
                "synthetic generator",
            )
            observed = {
                **expected,
                "path": "${BUILD}/tools/generator.py",
            }
            self.assertEqual(
                observed,
                gate.require_unique_declared_policy_file(
                    [observed], expected, roots, "synthetic generator"
                ),
            )

    def test_declared_policy_file_rejects_duplicate_nested_root_aliases(self):
        with tempfile.TemporaryDirectory() as temporary:
            build_tool = Path(temporary) / "build-tool"
            build = build_tool / "projects/mos-port"
            generator = build / "tools/generator.py"
            generator.parent.mkdir(parents=True)
            generator.write_text("# generator\n", encoding="utf-8")
            roots = {
                "BUILD_TOOL": rooted("BUILD_TOOL", build_tool),
                "BUILD": rooted("BUILD", build),
            }
            expected = gate.rooted_policy_record(
                "BUILD_TOOL",
                "projects/mos-port/tools/generator.py",
                roots,
                "synthetic generator",
            )
            alias = {**expected, "path": "${BUILD}/tools/generator.py"}
            with self.assertRaisesRegex(gate.GateError, "duplicate rooted aliases"):
                gate.require_unique_declared_policy_file(
                    [expected, alias], expected, roots, "synthetic generator"
                )

    def test_declared_policy_file_rejects_duplicate_hardlink_alias(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generator = root / "generator.py"
            alias = root / "generator-alias.py"
            generator.write_text("# generator\n", encoding="utf-8")
            alias.hardlink_to(generator)
            roots = {"BUILD_TOOL": rooted("BUILD_TOOL", root)}
            expected = gate.rooted_policy_record(
                "BUILD_TOOL", "generator.py", roots, "synthetic generator"
            )
            aliased = {**expected, "path": "${BUILD_TOOL}/generator-alias.py"}
            with self.assertRaisesRegex(gate.GateError, "hardlink alias"):
                gate.require_unique_declared_policy_file(
                    [expected, aliased], expected, roots, "synthetic generator"
                )
            with self.assertRaisesRegex(gate.GateError, "hardlink alias"):
                gate.require_unique_declared_policy_file(
                    [aliased], expected, roots, "synthetic generator"
                )

    def test_declared_policy_file_rejects_changed_digest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generator = root / "generator.py"
            generator.write_text("# generator\n", encoding="utf-8")
            roots = {"BUILD_TOOL": rooted("BUILD_TOOL", root)}
            expected = gate.rooted_policy_record(
                "BUILD_TOOL", "generator.py", roots, "synthetic generator"
            )
            changed = {**expected, "sha256": "0" * 64}
            with self.assertRaisesRegex(gate.GateError, "SHA-256 mismatch"):
                gate.require_unique_declared_policy_file(
                    [changed], expected, roots, "synthetic generator"
                )


class LinkMapTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.object = self.root / "owner.o"
        self.object.write_bytes(b"object")
        self.symbols = [{"map_name": "owned()"}]

    def tearDown(self):
        self.temporary.cleanup()

    def write_map(self, contribution: str) -> Path:
        path = self.root / "firmware.map"
        path.write_text(
            f"LOAD {self.object}\n"
            "Linker script and memory map\n"
            f"{contribution}\n",
            encoding="utf-8",
        )
        return path

    def test_requires_nonzero_contribution_and_exact_symbol_owner(self):
        path = self.write_map(
            f" .text 0x00001000 0x00000010 {self.object}\n"
            "                0x00001000 owned()"
        )
        result = gate.map_contribution_and_owners(
            path,
            self.object,
            "${BUILD}/owner.o",
            self.root,
            self.symbols,
            "owner",
        )
        self.assertEqual(16, result["allocated_bytes"])

    def test_load_only_and_ambiguous_symbol_are_false_greens(self):
        zero = self.write_map(
            f" .text 0x00001000 0x00000000 {self.object}\n"
            "                0x00001000 owned()"
        )
        with self.assertRaisesRegex(gate.GateError, "no nonzero"):
            gate.map_contribution_and_owners(
                zero, self.object, "${BUILD}/owner.o", self.root, self.symbols, "owner"
            )
        ambiguous = self.write_map(
            f" .text 0x00001000 0x00000010 {self.object}\n"
            "                0x00001000 owned()\n"
            "                0x00001004 owned()"
        )
        with self.assertRaisesRegex(gate.GateError, "ambiguous"):
            gate.map_contribution_and_owners(
                ambiguous,
                self.object,
                "${BUILD}/owner.o",
                self.root,
                self.symbols,
                "owner",
            )


class EmosIdentityAndCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.elf = self.root / "MOS.elf"
        self.values = {
            "EMOS_SOURCE_IDENTITY": "agon-emos-v1.0.0",
            "EMOS_BUILD_ID": "agon-emos-v1.0.0-b2026-09-01-00-00-00Z",
            "EMOS_ARTIFACT_STATUS": "candidate",
            "EMOS_QUALIFICATION_COMPOSITION_IDENTITY": (
                "port-008-forward-qualification-r02"
            ),
        }
        self.build = {
            "role": "qualification",
            "identity": {
                "source_identity": self.values["EMOS_SOURCE_IDENTITY"],
                "build_id": self.values["EMOS_BUILD_ID"],
                "lifecycle_status": self.values["EMOS_ARTIFACT_STATUS"],
                "composition_identity": self.values[
                    "EMOS_QUALIFICATION_COMPOSITION_IDENTITY"
                ],
            },
        }
        self.elf.write_bytes(
            b"\0".join(value.encode("ascii") for value in self.values.values())
            + b"\0"
        )

    def tearDown(self):
        self.temporary.cleanup()

    def step(self, command, *, responses=None):
        return gate.StepView(
            self.root / "record.json",
            "record",
            {"response_files": [] if responses is None else responses},
            self.root / "source.c",
            self.root / "source.o",
            tuple(command),
            (),
        )

    def owner_command(self):
        return [
            "clang",
            "-DAGONDEV",
            "-D_EZ80",
            "-D",
            "_EZ80F92",
            "-DNDEBUG",
            *[f'-D{name}="{value}"' for name, value in self.values.items()],
            "-DEMOS_PARALLEL_FIXED_QUALIFICATION=1",
            "-c",
            "emos.c",
        ]

    def steps(self, owner=None, other=None):
        return {
            "emos-mode-coordinator": self.step(owner or self.owner_command()),
            "emos-parallel-owner": self.step(
                other
                or ["clang", "-DAGONDEV", "-D_EZ80", "-DNDEBUG", "-c", "owner.c"]
            ),
        }

    def test_real_valueless_defines_and_exact_fixed_role_pass(self):
        definitions = gate.command_defines(self.owner_command(), "owner")
        self.assertEqual("1", definitions["AGONDEV"])
        self.assertEqual("1", definitions["_EZ80F92"])
        result = gate.validate_mos_identity_binding(
            self.build, self.steps(), self.elf
        )
        self.assertTrue(result["fixed_qualification_role_bound"])

    def test_build_id_substring_does_not_bind_source_identity(self):
        self.elf.write_bytes(
            b"\0".join(
                value.encode("ascii")
                for name, value in self.values.items()
                if name != "EMOS_SOURCE_IDENTITY"
            )
            + b"\0"
        )
        self.assertIn(
            self.values["EMOS_SOURCE_IDENTITY"].encode("ascii"),
            self.elf.read_bytes(),
        )
        with self.assertRaisesRegex(
            gate.GateError, "independently terminated EMOS_SOURCE_IDENTITY"
        ):
            gate.validate_mos_identity_binding(
                self.build, self.steps(), self.elf
            )

    def test_fixed_role_missing_zero_undefine_and_leak_fail(self):
        cases = {
            "missing": [
                item
                for item in self.owner_command()
                if not item.startswith("-DEMOS_PARALLEL_FIXED_QUALIFICATION")
            ],
            "zero": [
                "-DEMOS_PARALLEL_FIXED_QUALIFICATION=0"
                if item.startswith("-DEMOS_PARALLEL_FIXED_QUALIFICATION")
                else item
                for item in self.owner_command()
            ],
            "undefine": [
                *self.owner_command(),
                "-UEMOS_PARALLEL_FIXED_QUALIFICATION",
            ],
        }
        for name, owner in cases.items():
            with self.subTest(name=name), self.assertRaises(gate.GateError):
                gate.validate_mos_identity_binding(
                    self.build, self.steps(owner=owner), self.elf
                )
        leaked = [
            "clang",
            "-DEMOS_PARALLEL_FIXED_QUALIFICATION=1",
            "-c",
            "owner.c",
        ]
        with self.assertRaisesRegex(gate.GateError, "leaked"):
            gate.validate_mos_identity_binding(
                self.build, self.steps(other=leaked), self.elf
            )

    def test_release_cannot_carry_fixed_role_even_zero(self):
        release = copy.deepcopy(self.build)
        release["role"] = "release"
        release["identity"]["composition_identity"] = None
        for value in ("0", "1"):
            owner = [
                item
                for item in self.owner_command()
                if not item.startswith(
                    "-DEMOS_QUALIFICATION_COMPOSITION_IDENTITY"
                )
                and not item.startswith("-DEMOS_PARALLEL_FIXED_QUALIFICATION")
            ]
            owner.append(f"-DEMOS_PARALLEL_FIXED_QUALIFICATION={value}")
            with self.subTest(value=value), self.assertRaisesRegex(
                gate.GateError, "qualification-only role"
            ):
                gate.validate_mos_identity_binding(
                    release, self.steps(owner=owner), self.elf
                )

    def test_emos_product_policy_rejects_all_response_indirection(self):
        with self.assertRaisesRegex(gate.GateError, "response file"):
            gate.require_no_response_indirection(
                self.step(["clang", "@args.rsp"], responses=[{"path": "args.rsp"}]),
                "unit",
            )
        with self.assertRaisesRegex(gate.GateError, "response indirection"):
            gate.require_no_response_indirection(
                self.step(["clang", "@args.rsp"]), "final link"
            )


class CommandPolicyTests(unittest.TestCase):
    def test_identity_values_are_narrowly_normalized_but_flags_are_not(self):
        binding_a = {
            "source_identity": "agon-emos-v1.0.0",
            "build_id": "agon-emos-v1.0.0-b2026-09-01-00-00-00Z",
            "lifecycle_status": "candidate",
            "captured_composition_identity": "procedure-r01",
        }
        binding_b = {
            **binding_a,
            "build_id": "agon-emos-v1.0.0-b2026-09-01-00-00-01Z",
        }
        command_a = ["clang", f'-DEMOS_BUILD_ID="{binding_a["build_id"]}"', "-O2"]
        command_b = ["clang", f'-DEMOS_BUILD_ID="{binding_b["build_id"]}"', "-O2"]
        self.assertEqual(
            gate.normalize_policy_command(command_a, {}, binding_a),
            gate.normalize_policy_command(command_b, {}, binding_b),
        )
        command_b[-1] = "-O0"
        self.assertNotEqual(
            gate.normalize_policy_command(command_a, {}, binding_a),
            gate.normalize_policy_command(command_b, {}, binding_b),
        )
        selection_a = [
            {
                "driver": "clang",
                "selected_executable": "as",
                "selected_executable_sha256": "assembler",
                "probe_command": command_a,
                "probe_output": (
                    'clang version fixed\n'
                    f'"cc1" "-D" "EMOS_BUILD_ID=\\"{binding_a["build_id"]}\\"" '
                    '"/plugin/candidate/config"\n'
                ),
                "selected_invocation": [
                    "cc1",
                    f'-DEMOS_BUILD_ID="{binding_a["build_id"]}"',
                    "/plugin/candidate/config",
                ],
            }
        ]
        selection_b = copy.deepcopy(selection_a)
        selection_b[0]["probe_command"] = [
            "clang",
            f'-DEMOS_BUILD_ID="{binding_b["build_id"]}"',
            "-O2",
        ]
        selection_b[0]["selected_invocation"][1] = (
            f'-DEMOS_BUILD_ID="{binding_b["build_id"]}"'
        )
        selection_b[0]["probe_output"] = selection_b[0]["probe_output"].replace(
            binding_a["build_id"], binding_b["build_id"]
        )
        self.assertEqual(
            gate.normalized_mos_driver_selection(selection_a, {}, binding_a),
            gate.normalized_mos_driver_selection(selection_b, {}, binding_b),
        )
        selection_b[0]["selected_invocation"][2] = "/plugin/released/config"
        selection_b[0]["probe_output"] = selection_b[0]["probe_output"].replace(
            "/plugin/candidate/config", "/plugin/released/config"
        )
        self.assertNotEqual(
            gate.normalized_mos_driver_selection(selection_a, {}, binding_a),
            gate.normalized_mos_driver_selection(selection_b, {}, binding_b),
        )

    def test_pinned_scons_inverse_rejects_general_shell_forms(self):
        for value in (
            "/tool/g++",
            "/source tree/main.cpp",
            "literal$dollar",
            "literal\\backslash",
        ):
            encoded = gate.p4_ordinary_scons_word(value)
            self.assertEqual(value, gate.decode_p4_scons_word(encoded, "word"))
        for unsafe in ("$VAR", "*.cpp", "'single-quoted'", r"dollar\\$word"):
            with self.subTest(unsafe=unsafe), self.assertRaises(gate.GateError):
                gate.decode_p4_scons_word(unsafe, "word")

    def test_frozen_unit_and_final_link_fingerprints_reject_flag_or_order_drift(self):
        policy = gate.validate_policy(json.loads(POLICY.read_text()))["targets"]["emos"]
        policy = copy.deepcopy(policy)
        role = policy["roles"]["qualification"]
        material = {
            "actual_argument_vector": ["compiler", "-O2", "-c", "source.c"],
            "response_files": [],
            "expanded_argument_vector": ["compiler", "-O2", "-c", "source.c"],
        }
        link = {
            "actual_argument_vector": ["ld", "-T", "mos.ld", "one.o", "two.o"],
            "response_files": [],
            "expanded_argument_vector": ["ld", "-T", "mos.ld", "one.o", "two.o"],
        }
        capture = {
            "units": {
                unit_id: {
                    "command_policy_material": copy.deepcopy(material),
                    "command_sha256": gate.command_fingerprint(material),
                }
                for unit_id in role["required_units"]
            },
            "final_link_command_policy_material": copy.deepcopy(link),
            "final_link_command_sha256": gate.command_fingerprint(link),
        }
        proved, blockers, candidates = gate.evaluate_command_policy(
            policy, "qualification", capture
        )
        self.assertFalse(proved)
        self.assertTrue(any("await" in item for item in blockers))
        self.assertEqual(
            capture["final_link_command_sha256"],
            candidates["final_link_command_sha256"],
        )
        policy["command_policy_status"] = "frozen"
        role["unit_command_sha256"] = {
            unit_id: value["command_sha256"]
            for unit_id, value in capture["units"].items()
        }
        role["final_link_command_sha256"] = capture[
            "final_link_command_sha256"
        ]
        proved, blockers, _candidates = gate.evaluate_command_policy(
            policy, "qualification", capture
        )
        self.assertTrue(proved)
        self.assertEqual([], blockers)
        for mutation in ("--wrap=symbol", "-lunauthorized", "-Tother.ld"):
            changed = copy.deepcopy(capture)
            changed_link = changed["final_link_command_policy_material"]
            changed_link["actual_argument_vector"].append(mutation)
            changed_link["expanded_argument_vector"].append(mutation)
            changed["final_link_command_sha256"] = gate.command_fingerprint(
                changed_link
            )
            with self.subTest(mutation=mutation), self.assertRaisesRegex(
                gate.GateError, "final-link command"
            ):
                gate.evaluate_command_policy(policy, "qualification", changed)
        reordered = copy.deepcopy(capture)
        reordered_link = reordered["final_link_command_policy_material"]
        for field in ("actual_argument_vector", "expanded_argument_vector"):
            reordered_link[field][-2:] = reversed(reordered_link[field][-2:])
        reordered["final_link_command_sha256"] = gate.command_fingerprint(
            reordered_link
        )
        with self.assertRaisesRegex(gate.GateError, "final-link command"):
            gate.evaluate_command_policy(policy, "qualification", reordered)


class P4BoundaryTests(unittest.TestCase):
    def test_p4_compile_argv_binds_exact_source_and_output_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            source = project / "video/source.cpp"
            other = project / "video/other.cpp"
            extra_c = project / "video/extra.c"
            source_alias = project / "video/source-alias.cpp"
            output = project / ".pio/source.cpp.o"
            other_output = project / ".pio/other.cpp.o"
            source.parent.mkdir(parents=True)
            output.parent.mkdir(parents=True)
            source.write_text("int source;\n", encoding="utf-8")
            other.write_text("int other;\n", encoding="utf-8")
            extra_c.write_text("int extra;\n", encoding="utf-8")
            source_alias.hardlink_to(source)
            output.write_bytes(b"object")
            other_output.write_bytes(b"other object")
            valid = [
                "riscv32-esp-elf-g++",
                "-o",
                ".pio/source.cpp.o",
                "-c",
                "video/source.cpp",
            ]
            gate.validate_p4_compile_argument_paths(
                valid, source, output, project, "synthetic compile"
            )
            mutations = {
                "different claimed source": [*valid[:-1], "video/other.cpp"],
                "duplicate source": [*valid, str(source)],
                "extra differently suffixed source": [*valid, "video/extra.c"],
                "hardlink source": [*valid[:-1], "video/source-alias.cpp"],
                "different output": [
                    valid[0],
                    "-o",
                    ".pio/other.cpp.o",
                    *valid[3:],
                ],
                "duplicate output": [*valid, "-o", ".pio/source.cpp.o"],
                "attached output": [
                    valid[0],
                    "-o.pio/source.cpp.o",
                    *valid[3:],
                ],
                "missing compile mode": [item for item in valid if item != "-c"],
            }
            for name, arguments in mutations.items():
                with self.subTest(name=name), self.assertRaises(gate.GateError):
                    gate.validate_p4_compile_argument_paths(
                        arguments, source, output, project, "synthetic compile"
                    )

    def test_p4_link_argv_binds_exact_elf_and_canonical_map_option(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            build = project / ".pio"
            build.mkdir(parents=True)
            output = build / "firmware.elf"
            other_output = build / "other.elf"
            map_path = build / "firmware.map"
            other_map = build / "other.map"
            for path in (output, other_output, map_path, other_map):
                path.write_bytes(path.name.encode("ascii"))
            valid = [
                "riscv32-esp-elf-g++",
                "-o",
                ".pio/firmware.elf",
                "-Wl,-Map=.pio/firmware.map",
            ]
            gate.validate_p4_link_argument_paths(
                valid, output, map_path, project, "synthetic link"
            )
            mutations = {
                "different output": [
                    valid[0],
                    "-o",
                    ".pio/other.elf",
                    valid[3],
                ],
                "missing output": [valid[0], valid[3]],
                "duplicate output": [*valid, "-o", ".pio/firmware.elf"],
                "different map": [
                    *valid[:3],
                    "-Wl,-Map=.pio/other.map",
                ],
                "missing map": valid[:3],
                "duplicate map": [*valid, valid[3]],
                "double-dash map": [
                    *valid[:3],
                    "-Wl,--Map=.pio/firmware.map",
                ],
                "comma map": [
                    *valid[:3],
                    "-Wl,-Map,.pio/firmware.map",
                ],
                "separate map": [
                    *valid[:3],
                    "-Map",
                    ".pio/firmware.map",
                ],
            }
            for name, arguments in mutations.items():
                with self.subTest(name=name), self.assertRaises(gate.GateError):
                    gate.validate_p4_link_argument_paths(
                        arguments, output, map_path, project, "synthetic link"
                    )

    def test_p4_artifact_and_probe_reject_boolean_integers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "candidate"
            candidate.write_bytes(b"x")
            roots = {"BUILD": rooted("BUILD", root)}
            record = artifact(candidate)
            record["size"] = True
            with self.assertRaisesRegex(gate.GateError, "must be an integer"):
                gate.validate_p4_artifact(
                    record, roots, ("BUILD",), "synthetic P4 artifact"
                )
            probe = {
                "arguments": [],
                "exit_status": False,
                "output_utf8": "",
                "output_truncated": False,
            }
            with self.assertRaisesRegex(gate.GateError, "must be an integer"):
                gate.validate_p4_probe(
                    probe, (), {}, root, "synthetic P4 probe"
                )

    def test_project_sources_resolve_below_repository_top_level(self):
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary) / "repo"
            project = source_root / "vdp"
            build = Path(temporary) / "build"
            (project / "video").mkdir(parents=True)
            build.mkdir()
            selected = project / "video/selected.cpp"
            selected.write_text("int selected;\n")
            roots = {
                "SOURCE": rooted("SOURCE", source_root),
                "PROJECT": rooted("PROJECT", project),
                "BUILD": rooted("BUILD", build),
            }
            objects = gate.p4_expected_objects(
                {
                    "project_translation_units": ["video/selected.cpp"],
                    "vendored_translation_units": [],
                },
                roots,
            )
            self.assertEqual(selected.resolve(), next(iter(objects.values()))[0])
            self.assertNotEqual(source_root.resolve(), project.resolve())

    def test_generated_cmake_is_reproduced_and_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "repo/vdp"
            (project / "video").mkdir(parents=True)
            source = project / "video/selected.cpp"
            source.write_text("int selected;\n")
            cmake = project / "video/CMakeLists.txt"
            cmake.write_text(
                "# Generated by pio/select_sources.py for an allowlisted P4 target.\n"
                "# Hybrid Arduino/ESP-IDF ignores PlatformIO build_src_filter; do not hand-edit.\n"
                "idf_component_register(\n"
                "  SRCS\n"
                '    "${CMAKE_CURRENT_LIST_DIR}/selected.cpp"\n'
                ")\n"
                'target_compile_options(${COMPONENT_LIB} PRIVATE "-std=gnu++17")\n'
            )
            selection = {
                "generated_build_files": ["video/CMakeLists.txt"],
                "project_translation_units": ["video/selected.cpp"],
                "embedded_text_files": [],
            }
            roots = {"PROJECT": rooted("PROJECT", project)}
            result = gate.validate_p4_generated_build_files(selection, roots)
            self.assertTrue(result[0]["reproduced_from_tracked_selector"])
            cmake.write_text("tampered\n")
            with self.assertRaisesRegex(gate.GateError, "differs"):
                gate.validate_p4_generated_build_files(selection, roots)

    def test_local_identity_binds_firmware_and_composition_values(self):
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "project"
            consumer = project / "video/boot.cpp"
            header = project / ".pio/build-identities/qualification/build_identity.hpp"
            consumer.parent.mkdir(parents=True)
            header.parent.mkdir(parents=True)
            consumer.write_text("// boot\n")
            values = {
                "AGON_EXTENDER_SOURCE_IDENTITY": "extender-vdp-v1.0.0",
                "AGON_EXTENDER_BUILD_ID": "extender-vdp-v1.0.0-b2026-09-01-00-00-00Z",
                "AGON_EXTENDER_ARTIFACT_STATUS": "candidate",
                "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY": "port-008-forward-qualification-r02",
            }
            content = (
                "// Generated by pio/build_identity.py; do not edit.\n"
                "#pragma once\n"
                + "".join(f'#define {name} "{value}"\n' for name, value in values.items())
            )
            header.write_text(content)
            elf = Path(temporary) / "firmware.elf"
            elf.write_bytes(
                b"\0".join(value.encode() for value in values.values()) + b"\0"
            )
            header_record = artifact(header)
            event = {
                "dependencies": {
                    "before": {str(header.resolve()): header_record},
                    "after": {str(header.resolve()): header_record},
                },
                "expanded_argument_vector": ["compiler", "-c", str(consumer)],
            }
            build = {
                "role": "qualification",
                "identity": {
                    "source_identity": values["AGON_EXTENDER_SOURCE_IDENTITY"],
                    "build_id": values["AGON_EXTENDER_BUILD_ID"],
                    "lifecycle_status": values["AGON_EXTENDER_ARTIFACT_STATUS"],
                    "composition_identity": values[
                        "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY"
                    ],
                },
            }
            report = {
                "consumer": "video/boot.cpp",
                "generated_header": ".pio/build-identities/qualification/build_identity.hpp",
                "generator": "pio/build_identity.py",
                "artifact": header_record,
                "content_utf8": content,
                "definitions": values,
                "final_elf_strings": {
                    name: {
                        "value": value,
                        "ascii_occurrences": elf.read_bytes().count(value.encode()),
                    }
                    for name, value in values.items()
                },
            }
            result = gate.validate_p4_local_identity(
                report,
                build=build,
                selection={
                    "translation_unit_local_build_identity": {
                        "consumer": "video/boot.cpp",
                        "generated_header": ".pio/build-identities/qualification/build_identity.hpp",
                    }
                },
                inventory={
                    ".pio/build-identities/qualification/build_identity.hpp": header_record
                },
                compile_events_by_source={consumer.resolve(): event},
                elf_path=elf,
                roots={"PROJECT": rooted("PROJECT", project)},
            )
            self.assertTrue(result["identity_values_bound"])
            elf.write_bytes(
                b"\0".join(
                    value.encode()
                    for name, value in values.items()
                    if name != "AGON_EXTENDER_SOURCE_IDENTITY"
                )
                + b"\0"
            )
            report_without_standalone_source = copy.deepcopy(report)
            report_without_standalone_source["final_elf_strings"] = {
                name: {
                    "value": value,
                    "ascii_occurrences": elf.read_bytes().count(value.encode()),
                }
                for name, value in values.items()
            }
            self.assertIn(
                values["AGON_EXTENDER_SOURCE_IDENTITY"].encode(),
                elf.read_bytes(),
            )
            with self.assertRaisesRegex(
                gate.GateError, "does not bind AGON_EXTENDER_SOURCE_IDENTITY"
            ):
                gate.validate_p4_local_identity(
                    report_without_standalone_source,
                    build=build,
                    selection={
                        "translation_unit_local_build_identity": {
                            "consumer": "video/boot.cpp",
                            "generated_header": ".pio/build-identities/qualification/build_identity.hpp",
                        }
                    },
                    inventory={
                        ".pio/build-identities/qualification/build_identity.hpp": header_record
                    },
                    compile_events_by_source={consumer.resolve(): event},
                    elf_path=elf,
                    roots={"PROJECT": rooted("PROJECT", project)},
                )
            elf.write_bytes(
                b"\0".join(value.encode() for value in values.values()) + b"\0"
            )
            swapped = copy.deepcopy(build)
            swapped["identity"]["build_id"] = (
                "extender-vdp-v1.0.0-b2026-09-01-00-00-01Z"
            )
            with self.assertRaisesRegex(gate.GateError, "definitions"):
                gate.validate_p4_local_identity(
                    report,
                    build=swapped,
                    selection={
                        "translation_unit_local_build_identity": {
                            "consumer": "video/boot.cpp",
                            "generated_header": ".pio/build-identities/qualification/build_identity.hpp",
                        }
                    },
                    inventory={
                        ".pio/build-identities/qualification/build_identity.hpp": header_record
                    },
                    compile_events_by_source={consumer.resolve(): event},
                    elf_path=elf,
                    roots={"PROJECT": rooted("PROJECT", project)},
                )


class Ez80LinkedProjectionTests(unittest.TestCase):
    def projection(
        self,
        *,
        target_address=0x123456,
        linked_bytes=b"\xcd\x56\x34\x12\x20\x79",
        relocations=None,
        section_size=6,
        contributions=None,
        linked_symbols=None,
    ):
        if relocations is None:
            relocations = [
                {"offset": 1, "type": "r_imm24", "target": "target"}
            ]
        if contributions is None:
            contributions = [
                {"section": ".text", "address": 0x100, "size": section_size}
            ]
        if linked_symbols is None:
            linked_symbols = {
                "target": [
                    {"name": "target", "type": "T", "address": target_address, "size": 1}
                ]
            }
        section_table = {
            ".text": {
                "name": ".text",
                "size": section_size,
                "vma": 0,
                "flags": ("CONTENTS", "ALLOC", "LOAD", "CODE"),
            }
        }
        with (
            mock.patch.object(gate, "objdump_section_table", return_value=section_table),
            mock.patch.object(
                gate,
                "objdump_relocations",
                return_value={".text": relocations},
            ),
            mock.patch.object(
                gate,
                "objdump_section_bytes",
                side_effect=[b"\xcd\x00\x00\x00\x20\x79", linked_bytes],
            ),
        ):
            return gate.normalized_ez80_linked_object(
                Path("objdump"),
                Path("unit.o"),
                Path("firmware.elf"),
                contributions,
                linked_symbols,
                "synthetic unit",
            )

    def test_verified_relocation_rebasing_has_one_canonical_projection(self):
        first = self.projection()
        second = self.projection(
            target_address=0x654321,
            linked_bytes=b"\xcd\x21\x43\x65\x20\x79",
        )
        self.assertEqual(first, second)
        self.assertEqual(
            "cd0000002079", first["sections"][0]["contents"]
        )
        self.assertEqual(
            [{"offset": 1, "type": "r_imm24", "target": "target"}],
            first["sections"][0]["relocations"],
        )

    def test_projection_rejects_wrong_relocation_and_nonrelocation_bytes(self):
        with self.assertRaisesRegex(gate.GateError, "relocation bytes are incorrect"):
            self.projection(linked_bytes=b"\xcd\x57\x34\x12\x20\x79")
        with self.assertRaisesRegex(gate.GateError, "non-relocation byte differs"):
            self.projection(linked_bytes=b"\xcd\x56\x34\x12\x21\x79")

    def test_projection_rejects_unknown_overlapping_and_out_of_range_relocations(self):
        cases = (
            (
                [{"offset": 1, "type": "r_rel8", "target": "target"}],
                "unsupported relocation type",
            ),
            (
                [
                    {"offset": 1, "type": "r_imm24", "target": "target"},
                    {"offset": 2, "type": "r_imm24", "target": "target"},
                ],
                "overlapping relocations",
            ),
            (
                [{"offset": 5, "type": "r_imm24", "target": "target"}],
                "outside its section",
            ),
        )
        for relocations, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(
                gate.GateError, message
            ):
                self.projection(relocations=relocations)

    def test_projection_rejects_ambiguous_symbol_and_map_contribution(self):
        duplicate = {
            "target": [
                {"name": "target", "type": "T", "address": 0x123456, "size": 1},
                {"name": "target", "type": "T", "address": 0x123456, "size": 1},
            ]
        }
        with self.assertRaisesRegex(gate.GateError, "occurs 2 times"):
            self.projection(linked_symbols=duplicate)
        contributions = [
            {"section": ".text", "address": 0x100, "size": 6},
            {"section": ".text", "address": 0x200, "size": 6},
        ]
        with self.assertRaisesRegex(gate.GateError, "has 2 map contributions"):
            self.projection(contributions=contributions)

    def test_section_relocation_resolution_is_exact_and_bounded(self):
        contributions = [
            {"section": ".rodata", "address": 0x2000, "size": 4}
        ]
        self.assertEqual(
            0x2003,
            gate.resolve_ez80_imm24_relocation(
                ".rodata+0x3", contributions, {}, "synthetic relocation"
            ),
        )
        with self.assertRaisesRegex(gate.GateError, "addend is out of range"):
            gate.resolve_ez80_imm24_relocation(
                ".rodata+0x4", contributions, {}, "synthetic relocation"
            )

    def test_objdump_parsers_cover_unaligned_full_sections_and_relocations(self):
        section_output = b"""Sections:\nIdx Name          Size      VMA       LMA       File off  Algn\n  0 .STARTUP      00000010  00000000  00000000  00000034  2**0\n                  CONTENTS, ALLOC, LOAD, RELOC, READONLY, CODE\n"""
        content_field = "fde5 fd210000 00fd39c5 fd7e06e6 b0f6"
        self.assertEqual(36, len(content_field))
        content_output = (
            "Contents of section .startup:\n"
            f" 1a5a {content_field} deadbeefdeadbeef\n"
        ).encode()
        relocation_output = b"""RELOCATION RECORDS FOR [.STARTUP]:\nOFFSET   TYPE              VALUE\n00000001 r_imm24           target\n00000005 r_imm24           .STARTUP+0x00000008\n"""
        with mock.patch.object(
            gate,
            "run_checked",
            side_effect=[
                type("Result", (), {"stdout": section_output})(),
                type("Result", (), {"stdout": content_output})(),
                type("Result", (), {"stdout": relocation_output})(),
            ],
        ):
            sections = gate.objdump_section_table(
                Path("objdump"), Path("unit.o"), "synthetic object"
            )
            contents = gate.objdump_section_bytes(
                Path("objdump"),
                Path("firmware.elf"),
                "synthetic linked section",
                start=0x1A5A,
                size=16,
            )
            relocations = gate.objdump_relocations(
                Path("objdump"), Path("unit.o"), "synthetic object"
            )
        self.assertEqual(16, sections[".STARTUP"]["size"])
        self.assertEqual(16, len(contents))
        self.assertEqual(2, len(relocations[".STARTUP"]))


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        self.policy = gate.validate_policy(json.loads(POLICY.read_text()))

    def unit(self):
        return {
            "source_sha256": "source",
            "dependencies": [{"path": "${SOURCE}/x", "sha256": "dep", "size": 1}],
            "declared_inputs": [{"path": "${SOURCE}/x", "sha256": "dep", "size": 1}],
            "environment": {"policy": "exact"},
            "executables": {"compiler": "tool"},
            "response_files": [],
            "object_sha256": "object",
            "object_size": 7,
            "object_symbols": [{"name": "owned", "type": "T", "size": 7}],
            "linked_symbols": [{"name": "owned", "type": "T", "size": 7}],
            "object_disassembly_sha256": "object-disassembly",
            "linked_disassembly_sha256": "role-dependent-linked-disassembly",
            "generator": None,
            "driver_selection": [],
            "command": ["compiler", "-c", "${SOURCE}/x"],
            "command_policy_material": {
                "actual_argument_vector": ["compiler", "-c", "${SOURCE}/x"],
                "response_files": [],
                "expanded_argument_vector": ["compiler", "-c", "${SOURCE}/x"],
                "tool_selection": [],
            },
        }

    def validation(self, role: str):
        units = {
            item["id"]: self.unit()
            for item in self.policy["targets"]["emos"]["units"]
            if item["classification"] in {"equality", "composition-dependent"}
        }
        if role == "qualification":
            units["emos-mode-coordinator"]["dependencies"].append(
                {
                    "path": "${PREPARED}/src/emos_parallel.h",
                    "sha256": "qualification-header",
                    "size": 17,
                }
            )
            units["emos-mode-coordinator"]["dependencies"].sort(
                key=lambda record: record["path"]
            )
        suffix = "q" if role == "qualification" else "r"
        return {
            "target": "emos",
            "role": role,
            "policy_sha256": "policy",
            "build_record_sha256": f"build-{suffix}",
            "blockers": [],
            "equivalence_eligible": True,
            "identity": {
                "artifact_id": "agon-emos",
                "variant": "port008-forward",
                "source_identity": "agon-emos-v1.0.0",
                "build_id": f"agon-emos-v1.0.0-b2026-09-01-00-00-0{0 if role == 'qualification' else 1}Z",
                "lifecycle_status": "candidate",
                "registry_sha256": "registry",
            },
            "repositories": [
                {"id": "authority", "commit": "authority"},
                {"id": "product-source", "commit": "product"},
                {"id": "build-tool", "commit": "build-tool"},
            ],
            "prepared_source": {
                "source_commit": "product",
                "checker_commit": "build-tool",
            },
            "capture": {
                "session_id": f"{suffix * 32}",
                "final_image": {
                    "path": "${BUILD}/bin/MOS.elf",
                    "sha256": f"image-{suffix}",
                    "instance_path_sha256": f"instance-{suffix}",
                },
                "units": units,
            },
        }

    def test_exact_units_prove_equivalence_despite_same_normalized_image_path(self):
        qualification = self.validation("qualification")
        release = self.validation("release")
        result = gate.compare_validations(qualification, release, self.policy)
        self.assertTrue(result["equivalence_proved"])
        self.assertTrue(result["linked_symbols_and_normalized_disassembly_identical"])

    def test_linked_instruction_or_relaxation_drift_fails_even_with_same_object(self):
        qualification = self.validation("qualification")
        release = self.validation("release")
        first = next(iter(release["capture"]["units"].values()))
        self.assertEqual(
            next(iter(qualification["capture"]["units"].values()))["object_sha256"],
            first["object_sha256"],
        )
        first["linked_disassembly_sha256"] = "different-linked-instructions"
        result = gate.compare_validations(qualification, release, self.policy)
        self.assertFalse(result["equivalence_proved"])
        self.assertTrue(
            any("linked_disassembly_sha256" in item for item in result["blockers"])
        )

    def test_command_drift_and_self_comparison_fail_closed(self):
        qualification = self.validation("qualification")
        release = self.validation("release")
        first = next(iter(release["capture"]["units"].values()))
        first["command"].append("-DROLE_LEAK=1")
        result = gate.compare_validations(qualification, release, self.policy)
        self.assertFalse(result["equivalence_proved"])
        self.assertTrue(any("command" in item for item in result["blockers"]))
        release = self.validation("release")
        release["capture"]["session_id"] = qualification["capture"]["session_id"]
        with self.assertRaisesRegex(gate.GateError, "identical provenance session"):
            gate.compare_validations(qualification, release, self.policy)

    def test_semantic_dependency_drift_is_not_hidden_by_distinct_sessions(self):
        qualification = self.validation("qualification")
        release = self.validation("release")
        first = next(iter(release["capture"]["units"].values()))
        first["dependencies"][0]["sha256"] = "changed-semantic-header"
        result = gate.compare_validations(qualification, release, self.policy)
        self.assertFalse(result["equivalence_proved"])
        self.assertTrue(any("dependencies" in item for item in result["blockers"]))

    def test_lineage_commit_and_composition_owner_drift_fail(self):
        qualification = self.validation("qualification")
        release = self.validation("release")
        release["identity"]["source_identity"] = "agon-emos-v1.0.1"
        release["repositories"][1]["commit"] = "different-product"
        owner = release["capture"]["units"]["emos-mode-coordinator"]
        owner["source_sha256"] = "different-owner-source"
        owner["dependencies"][0]["sha256"] = "different-owner-dependency"
        result = gate.compare_validations(qualification, release, self.policy)
        self.assertFalse(result["equivalence_proved"])
        self.assertTrue(any("source_identity" in item for item in result["blockers"]))
        self.assertTrue(any("source commits" in item for item in result["blockers"]))
        self.assertTrue(any("composition-owner inputs" in item for item in result["blockers"]))

    def test_composition_dependency_delta_must_match_policy_exactly(self):
        mutations = (
            (
                "missing qualification-only dependency",
                lambda qualification, release: qualification["capture"]["units"][
                    "emos-mode-coordinator"
                ]["dependencies"].pop(),
            ),
            (
                "extra qualification-only dependency",
                lambda qualification, release: qualification["capture"]["units"][
                    "emos-mode-coordinator"
                ]["dependencies"].append(
                    {"path": "${PREPARED}/extra.h", "sha256": "extra", "size": 1}
                ),
            ),
            (
                "wrong-direction dependency",
                lambda qualification, release: release["capture"]["units"][
                    "emos-mode-coordinator"
                ]["dependencies"].append(
                    qualification["capture"]["units"]["emos-mode-coordinator"][
                        "dependencies"
                    ].pop()
                ),
            ),
            (
                "shared dependency content drift",
                lambda qualification, release: release["capture"]["units"][
                    "emos-mode-coordinator"
                ]["dependencies"][0].update(sha256="changed"),
            ),
        )
        for label, mutate in mutations:
            qualification = self.validation("qualification")
            release = self.validation("release")
            mutate(qualification, release)
            with self.subTest(label=label):
                result = gate.compare_validations(
                    qualification, release, self.policy
                )
                self.assertFalse(result["equivalence_proved"])
                self.assertTrue(
                    any(
                        "composition-owner dependencies differ from exact policy delta"
                        in blocker
                        for blocker in result["blockers"]
                    )
                )


if __name__ == "__main__":
    unittest.main()
