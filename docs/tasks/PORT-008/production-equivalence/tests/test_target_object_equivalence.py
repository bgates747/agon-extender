"""Regression tests for the PORT-008 preliminary object-similarity checker."""

from __future__ import annotations

from contextlib import redirect_stderr
import importlib.util
from io import StringIO
import json
from pathlib import Path
import shlex
import stat
import subprocess
import tempfile
import unittest

from jsonschema import Draft202012Validator


TASK_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = TASK_ROOT / "scripts/validate-target-object-equivalence.py"
SPEC = importlib.util.spec_from_file_location("port008_object_gate", SCRIPT)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


COMPILER_SOURCE = r'''#!/usr/bin/env python3
import pathlib
import sys

if "--version" in sys.argv:
    print("synthetic target compiler 1.0")
    raise SystemExit(0)
if "-dumpmachine" in sys.argv:
    print("synthetic32-none-elf")
    raise SystemExit(0)

args = sys.argv[1:]
output = None
dependency = None
for index, value in enumerate(args):
    if value == "-o" and index + 1 < len(args):
        output = args[index + 1]
    elif value.startswith("-o") and len(value) > 2:
        output = value[2:]
    elif value == "-MF" and index + 1 < len(args):
        dependency = args[index + 1]
    elif value.startswith("-MF") and len(value) > 3:
        dependency = value[3:]
if output is None:
    print("missing output", file=sys.stderr)
    raise SystemExit(2)
pathlib.Path(output).write_bytes(b"SYNTHETIC-TARGET-OBJECT-v1\n")
if dependency is not None:
    pathlib.Path(dependency).write_text("synthetic dependency\n")
'''


NM_SOURCE = r'''#!/usr/bin/env python3
import pathlib
import sys

if "--version" in sys.argv:
    print("synthetic target nm 1.0")
    raise SystemExit(0)
image = pathlib.Path(sys.argv[-1]).read_bytes()
size = "10" if b"BAD-SYMBOL" in image else "8"
print(f"_prod T 1000 {size}")
'''


OBJDUMP_SOURCE = r'''#!/usr/bin/env python3
import pathlib
import sys

if "--version" in sys.argv:
    print("synthetic target objdump 1.0")
    raise SystemExit(0)
if "-f" in sys.argv:
    print("architecture: synthetic32, flags 0x0:")
    raise SystemExit(0)

image = pathlib.Path(sys.argv[-1]).read_bytes()
symbol_option = next(value for value in sys.argv if value.startswith("--disassemble="))
symbol = symbol_option.split("=", 1)[1]
if "release" in sys.argv[-1]:
    address = 0x2000
elif "qualification" in sys.argv[-1]:
    address = 0x1000
else:
    address = 0x3000
increment = 2 if b"BAD-DISASM" in image else 1
print(f"{address:08x} <{symbol}>:")
print(f" {address:08x}: addi r0,r0,{increment}")
print(f" {address + 4:08x}: jal {address + 0x100:x} <_helper>")
'''


def write_executable(path: Path, source: str) -> None:
    path.write_text(source, encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def file_record(path: Path, root: Path) -> dict[str, str]:
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": gate.sha256_file(path),
    }


def tool_record(path: Path) -> dict[str, str]:
    completed = gate.run_checked([str(path), "--version"])
    return {
        "name": path.name,
        "executable_sha256": gate.sha256_file(path),
        "version_output_sha256": gate.canonical_sha256(
            gate.command_output_record(completed)
        ),
    }


def regular_archive(records: list[tuple[str, bytes]]) -> bytes:
    output = bytearray(gate.AR_MAGIC)
    for name, payload in records:
        archive_name = name + "/"
        header = (
            f"{archive_name:<16}"
            f"{0:<12}"
            f"{0:<6}"
            f"{0:<6}"
            f"{100644:<8}"
            f"{len(payload):<10}"
            "`\n"
        ).encode("ascii")
        if len(header) != gate.AR_HEADER_SIZE:
            raise AssertionError(len(header))
        output.extend(header)
        output.extend(payload)
        if len(payload) & 1:
            output.extend(b"\n")
    return bytes(output)


class SyntheticEvidence:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.source = root / "src/production.c"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("int production(void) { return 1; }\n", encoding="utf-8")
        (root / "include").mkdir()

        self.compiler = root / "tools/synthetic32-none-elf-gcc"
        self.nm = root / "tools/synthetic32-none-elf-nm"
        self.objdump = root / "tools/synthetic32-none-elf-objdump"
        self.compiler.parent.mkdir()
        write_executable(self.compiler, COMPILER_SOURCE)
        write_executable(self.nm, NM_SOURCE)
        write_executable(self.objdump, OBJDUMP_SOURCE)

        self.build_dirs: dict[str, Path] = {}
        self.compile_databases: dict[str, Path] = {}
        self.outputs: dict[str, Path] = {}
        self.images: dict[str, Path] = {}
        for role in gate.ROLES:
            build = root / f"build-{role}"
            build.mkdir()
            self.build_dirs[role] = build
            response = build / "cflags"
            response.write_text(
                f"-Wall -I{root / 'include'}\n", encoding="utf-8", newline="\n"
            )
            output = build / "production.o"
            argv = [
                str(self.compiler),
                "-DPORT008_PRODUCTION=1",
                f"@{response}",
                "-O2",
                "-c",
                str(self.source),
                "-o",
                str(output),
            ]
            subprocess.run(argv, check=True)
            self.outputs[role] = output
            database = build / "compile_commands.json"
            database.write_text(
                json.dumps(
                    [
                        {
                            "directory": str(build),
                            "command": shlex.join(argv),
                            "file": str(self.source),
                            "output": str(output),
                        }
                    ],
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            self.compile_databases[role] = database
            image = build / f"{role}.elf"
            image.write_bytes(role.upper().encode("ascii") + b"-LINKED-IMAGE\n")
            self.images[role] = image

        self.manifest = self.make_manifest()
        self.manifest_path = root / "target-object-equivalence.json"
        self.write_manifest()

    @staticmethod
    def symbol_records(size: int = 8) -> list[dict[str, object]]:
        return [{"name": "_prod", "type": "T", "size": size}]

    @staticmethod
    def disassembly(increment: int = 1) -> list[dict[str, object]]:
        return [
            {
                "symbol": "_prod",
                "instructions": [
                    {"offset": 0, "text": f"addi r0,r0,{increment}"},
                    {"offset": 4, "text": "jal <_helper>"},
                ],
            }
        ]

    def normalized_compile(self, role: str) -> tuple[dict, list[str], list[str]]:
        records = gate.load_compile_database(
            self.compile_databases[role], f"{role} compile database"
        )
        _, directory, argv = gate.select_compile_record(
            records,
            self.root,
            self.source,
            self.outputs[role],
            f"{role} compile database",
        )
        command, definitions, flags, _, _ = gate.normalize_compile_record(
            argv,
            directory=directory,
            root=self.root,
            build_root=self.build_dirs[role],
            source=self.source,
            output=self.outputs[role],
            label=role,
        )
        return command, definitions, flags

    def unit_build(self, role: str) -> dict:
        command, definitions, flags = self.normalized_compile(role)
        output = self.outputs[role]
        payload_digest = gate.sha256_file(output)
        return {
            "producer_kind": "compiler-driver",
            "source": file_record(self.source, self.root),
            "compile_output": file_record(output, self.root),
            "compiler": tool_record(self.compiler),
            "normalized_compile_command_sha256": gate.canonical_sha256(command),
            "normalized_defines_sha256": gate.canonical_sha256(definitions),
            "normalized_flags_sha256": gate.canonical_sha256(flags),
            "artifact": {
                "kind": "object",
                "path": output.relative_to(self.root).as_posix(),
                "container_sha256": payload_digest,
                "member": None,
                "payload_sha256": payload_digest,
            },
            "linked_symbol_records_sha256": gate.canonical_sha256(
                self.symbol_records()
            ),
            "normalized_linked_disassembly_sha256": gate.canonical_sha256(
                self.disassembly()
            ),
            "normalized_object_disassembly_sha256": gate.canonical_sha256(
                self.disassembly()
            ),
        }

    def make_manifest(self) -> dict:
        return {
            "schema_version": 1,
            "evidence_kind": "port-008-preliminary-object-similarity",
            "evidence_class": "preliminary-compile-output-final-symbol-similarity",
            "input_trust_model": "trusted-local-reviewed-inputs",
            "target": {
                "artifact_id": "synthetic-port008-target",
                "compiler_triple": "synthetic32-none-elf",
                "object_architecture": "synthetic32",
                "host_native": False,
            },
            "inspection_tools": {
                "nm": tool_record(self.nm),
                "objdump": tool_record(self.objdump),
            },
            "builds": {
                "qualification": {
                    "build_id": "synthetic-qualification-b2026-09-01-00-00-00Z",
                    "composition_class": "qualification-only",
                    "source_commit": "a" * 40,
                    "dirty": False,
                    "build_root": self.build_dirs["qualification"].relative_to(
                        self.root
                    ).as_posix(),
                    "compile_database": file_record(
                        self.compile_databases["qualification"], self.root
                    ),
                    "linked_image": file_record(
                        self.images["qualification"], self.root
                    ),
                },
                "release": {
                    "build_id": "synthetic-release-b2026-09-01-00-00-01Z",
                    "composition_class": "production-release",
                    "source_commit": "b" * 40,
                    "dirty": False,
                    "build_root": self.build_dirs["release"].relative_to(
                        self.root
                    ).as_posix(),
                    "compile_database": file_record(
                        self.compile_databases["release"], self.root
                    ),
                    "linked_image": file_record(self.images["release"], self.root),
                },
            },
            "production_units": [
                {
                    "id": "production-record-engine",
                    "symbols": [{"object_name": "_prod", "linked_name": "_prod"}],
                    "builds": {
                        role: self.unit_build(role) for role in gate.ROLES
                    },
                }
            ],
        }

    def refresh_build_file(self, role: str, name: str, path: Path) -> None:
        self.manifest["builds"][role][name] = file_record(path, self.root)

    def refresh_compile_evidence(self, role: str) -> None:
        self.refresh_build_file(role, "compile_database", self.compile_databases[role])
        observed = self.unit_build(role)
        self.manifest["production_units"][0]["builds"][role].update(
            {
                "normalized_compile_command_sha256": observed[
                    "normalized_compile_command_sha256"
                ],
                "normalized_defines_sha256": observed["normalized_defines_sha256"],
                "normalized_flags_sha256": observed["normalized_flags_sha256"],
            }
        )

    def write_manifest(self) -> None:
        self.manifest_path.write_text(
            json.dumps(self.manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    def validate(self) -> dict:
        self.write_manifest()
        return gate.validate(
            self.manifest_path,
            self.root,
            self.root,
            self.nm,
            self.objdump,
            replay_timeout=10,
        )


class PreliminaryObjectSimilarityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.evidence = SyntheticEvidence(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_schema_is_valid_draft_2020_12(self) -> None:
        schema = json.loads(
            (TASK_ROOT / "schema/target-object-equivalence-v1.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator.check_schema(schema)

    def test_cli_requires_trusted_input_acknowledgement(self) -> None:
        stderr = StringIO()
        arguments = [
            "--manifest",
            str(self.evidence.manifest_path),
            "--qualification-root",
            str(self.evidence.root),
            "--release-root",
            str(self.evidence.root),
            "--nm",
            str(self.evidence.nm),
            "--objdump",
            str(self.evidence.objdump),
        ]
        with redirect_stderr(stderr), self.assertRaisesRegex(SystemExit, "2"):
            gate.main(arguments)
        self.assertIn("--acknowledge-trusted-inputs is required", stderr.getvalue())

    def test_preliminary_checks_pass_without_equivalence_claim(self) -> None:
        report = self.evidence.validate()
        self.assertTrue(report["preliminary_checks_passed"])
        self.assertFalse(report["equivalence_proved"])
        self.assertEqual(
            "preliminary-compile-output-final-symbol-similarity",
            report["evidence_class"],
        )
        self.assertEqual(
            {"qualification": "a" * 40, "release": "b" * 40},
            report["manifest_attested_source_commits"],
        )
        self.assertEqual(
            gate.sha256_file(self.evidence.outputs["qualification"]),
            report["production_units"][0]["supplied_artifact_payload_sha256"],
        )
        self.assertEqual(list(gate.MISSING_CLAIMS), report["missing_claims"])
        self.assertFalse(report["claims"]["link_contribution_proved"])
        self.assertFalse(
            report["claims"]["git_cleanliness_and_commit_provenance_proved"]
        )
        self.assertFalse(report["claims"]["target_and_tool_authority_proved"])

    def test_host_same_source_manifest_is_rejected_by_schema(self) -> None:
        self.evidence.manifest["evidence_class"] = "host-source"
        with self.assertRaisesRegex(gate.GateError, "schema error"):
            self.evidence.validate()

    def test_stale_object_is_rejected_by_compile_replay(self) -> None:
        role = "release"
        output = self.evidence.outputs[role]
        output.write_bytes(b"STALE-OBJECT\n")
        digest = gate.sha256_file(output)
        unit = self.evidence.manifest["production_units"][0]["builds"][role]
        unit["compile_output"] = file_record(output, self.evidence.root)
        unit["artifact"].update(
            {"container_sha256": digest, "payload_sha256": digest}
        )
        with self.assertRaisesRegex(gate.GateError, "replay object differs"):
            self.evidence.validate()

    def test_different_compile_flag_is_rejected_even_when_object_bytes_match(self) -> None:
        role = "release"
        database = json.loads(
            self.evidence.compile_databases[role].read_text(encoding="utf-8")
        )
        database[0]["command"] = database[0]["command"].replace("-O2", "-O3")
        self.evidence.compile_databases[role].write_text(
            json.dumps(database, indent=2) + "\n", encoding="utf-8"
        )
        self.evidence.refresh_compile_evidence(role)
        with self.assertRaisesRegex(gate.GateError, "compiler flags differ"):
            self.evidence.validate()

    def test_ez80_architecture_flag_with_equals_is_not_mistaken_for_side_output(self) -> None:
        for role in gate.ROLES:
            database = json.loads(
                self.evidence.compile_databases[role].read_text(encoding="utf-8")
            )
            database[0]["command"] = database[0]["command"].replace(
                "-O2", "-O2 -Wa,-march=ez80+full"
            )
            self.evidence.compile_databases[role].write_text(
                json.dumps(database, indent=2) + "\n", encoding="utf-8"
            )
            self.evidence.refresh_compile_evidence(role)
        report = self.evidence.validate()
        self.assertTrue(report["preliminary_checks_passed"])
        self.assertFalse(report["equivalence_proved"])

    def test_response_file_side_output_is_rejected_before_compile_replay(self) -> None:
        role = "release"
        response = self.evidence.build_dirs[role] / "cflags"
        response.write_text(
            f"-Wall -I{self.evidence.root / 'include'} -MF leaked.d\n",
            encoding="utf-8",
        )
        self.evidence.refresh_compile_evidence(role)
        with self.assertRaisesRegex(gate.GateError, "compiler flags differ"):
            self.evidence.validate()
        self.assertFalse((self.evidence.build_dirs[role] / "leaked.d").exists())

    def test_linked_symbol_difference_is_rejected_after_record_verification(self) -> None:
        role = "release"
        image = self.evidence.images[role]
        image.write_bytes(b"BAD-SYMBOL RELEASE LINKED IMAGE\n")
        self.evidence.refresh_build_file(role, "linked_image", image)
        unit = self.evidence.manifest["production_units"][0]["builds"][role]
        unit["linked_symbol_records_sha256"] = gate.canonical_sha256(
            self.evidence.symbol_records(size=16)
        )
        with self.assertRaisesRegex(gate.GateError, "linked symbol records differ"):
            self.evidence.validate()

    def test_linked_disassembly_difference_is_rejected_after_record_verification(self) -> None:
        role = "release"
        image = self.evidence.images[role]
        image.write_bytes(b"BAD-DISASM RELEASE LINKED IMAGE\n")
        self.evidence.refresh_build_file(role, "linked_image", image)
        unit = self.evidence.manifest["production_units"][0]["builds"][role]
        unit["normalized_linked_disassembly_sha256"] = gate.canonical_sha256(
            self.evidence.disassembly(increment=2)
        )
        with self.assertRaisesRegex(
            gate.GateError, "normalized linked disassembly records differ"
        ):
            self.evidence.validate()

    def test_archive_member_is_hashed_and_must_be_unique(self) -> None:
        payload = self.evidence.outputs["qualification"].read_bytes()
        for role in gate.ROLES:
            archive = self.evidence.build_dirs[role] / "libproduction.a"
            archive.write_bytes(regular_archive([("production.o", payload)]))
            unit = self.evidence.manifest["production_units"][0]["builds"][role]
            unit["artifact"] = {
                "kind": "archive-member",
                "path": archive.relative_to(self.evidence.root).as_posix(),
                "container_sha256": gate.sha256_file(archive),
                "member": "production.o",
                "payload_sha256": gate.sha256_bytes(payload),
            }
        report = self.evidence.validate()
        self.assertTrue(report["preliminary_checks_passed"])
        self.assertFalse(report["equivalence_proved"])

        archive = self.evidence.build_dirs["release"] / "libproduction.a"
        archive.write_bytes(
            regular_archive([("production.o", payload), ("production.o", payload)])
        )
        self.evidence.manifest["production_units"][0]["builds"]["release"][
            "artifact"
        ]["container_sha256"] = gate.sha256_file(archive)
        with self.assertRaisesRegex(gate.GateError, "exactly one member"):
            self.evidence.validate()

    def test_direct_assembler_producer_is_rejected_clearly(self) -> None:
        role = "release"
        assembler = self.evidence.root / "tools/synthetic32-none-elf-as"
        write_executable(assembler, COMPILER_SOURCE)
        database = json.loads(
            self.evidence.compile_databases[role].read_text(encoding="utf-8")
        )
        argv = shlex.split(database[0]["command"])
        argv[0] = str(assembler)
        argv.remove("-c")
        database[0]["command"] = shlex.join(argv)
        self.evidence.compile_databases[role].write_text(
            json.dumps(database, indent=2) + "\n", encoding="utf-8"
        )
        self.evidence.refresh_build_file(
            role, "compile_database", self.evidence.compile_databases[role]
        )
        unit = self.evidence.manifest["production_units"][0]["builds"][role]
        unit["compiler"] = tool_record(assembler)
        with self.assertRaisesRegex(
            gate.GateError, "unsupported direct assembler producer"
        ):
            self.evidence.validate()

    def test_declared_assembler_producer_is_rejected_clearly(self) -> None:
        self.evidence.manifest["production_units"][0]["builds"]["release"][
            "producer_kind"
        ] = "direct-assembler"
        with self.assertRaisesRegex(
            gate.GateError,
            "declares unsupported producer_kind.*direct assembler objects",
        ):
            self.evidence.validate()

    def test_same_build_id_is_not_an_equivalence_comparison(self) -> None:
        self.evidence.manifest["builds"]["release"]["build_id"] = self.evidence.manifest[
            "builds"
        ]["qualification"]["build_id"]
        with self.assertRaisesRegex(gate.GateError, "build IDs must be distinct"):
            self.evidence.validate()

    def test_shell_operator_in_compile_database_is_rejected(self) -> None:
        role = "release"
        database = json.loads(
            self.evidence.compile_databases[role].read_text(encoding="utf-8")
        )
        database[0]["command"] += " ; true"
        self.evidence.compile_databases[role].write_text(
            json.dumps(database, indent=2) + "\n", encoding="utf-8"
        )
        self.evidence.refresh_build_file(role, "compile_database", self.evidence.compile_databases[role])
        with self.assertRaisesRegex(gate.GateError, "shell operator"):
            self.evidence.validate()

    def test_compiler_identity_mismatch_is_rejected(self) -> None:
        unit = self.evidence.manifest["production_units"][0]["builds"]["release"]
        unit["compiler"]["executable_sha256"] = "0" * 64
        with self.assertRaisesRegex(gate.GateError, "compiler executable SHA-256 mismatch"):
            self.evidence.validate()

    def test_report_output_is_append_only(self) -> None:
        report = self.evidence.validate()
        destination = self.evidence.root / "gate-report.json"
        gate.write_report(destination, report)
        with self.assertRaisesRegex(gate.GateError, "refusing to overwrite"):
            gate.write_report(destination, report)


if __name__ == "__main__":
    unittest.main()
