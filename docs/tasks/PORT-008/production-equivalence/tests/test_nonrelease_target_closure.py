"""Regression tests for the PORT-008 non-release target-closure gate."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest import mock


TASK_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = TASK_ROOT / "scripts/validate-nonrelease-target-closure.py"
SPEC = importlib.util.spec_from_file_location(
    "port008_nonrelease_target_closure", SCRIPT
)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class SyntheticClosure:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.project_root = root / "vdp"
        self.manifest_root = self.project_root / "pio"
        self.manifest_root.mkdir(parents=True)
        self.environment = gate.QUALIFICATION_ENVIRONMENT
        self.build_root = (
            self.project_root / ".pio" / "build" / self.environment
        )
        self.build_root.mkdir(parents=True)
        self.map_path = self.build_root / "firmware.map"
        self.elf_path = self.build_root / "firmware.elf"
        self.elf_path.write_bytes(b"synthetic target ELF\n")
        for unit in gate.REQUIRED_TRANSLATION_UNITS:
            object_path = self.build_root / gate.object_path(unit)
            object_path.parent.mkdir(parents=True, exist_ok=True)
            object_path.write_bytes(
                f"synthetic object for {unit}\n".encode("utf-8")
            )

        self.qualification_manifest = (
            self.manifest_root / gate.QUALIFICATION_MANIFEST_NAME
        )
        self.ordinary_paths = {
            environment: self.manifest_root / filename
            for environment, filename in gate.ORDINARY_MANIFESTS.items()
        }
        self.nm_path = root / "tools" / "synthetic32-none-elf-nm"
        self.nm_path.parent.mkdir()
        self.untrusted_marker = root / "manifest-tool-was-executed"
        self.documents = self.make_documents()
        self.write_manifests()
        self.write_map()
        self.write_nm()

    def make_documents(self) -> dict[str, dict]:
        qualification = {
            "environment": self.environment,
            "component_compile_definitions": [
                gate.QUALIFICATION_DEFINITION
            ],
            "project_translation_units": [
                *gate.REQUIRED_TRANSLATION_UNITS,
                "video/extender/display/p4_display_controller.cpp",
            ],
            "forbidden_project_translation_units": [
                *gate.FORBIDDEN_TRANSLATION_UNITS
            ],
            # A manifest tool is inert data.  The validator must never run it.
            "tools": [{"command": str(self.untrusted_marker)}],
        }
        documents = {"qualification": qualification}
        for environment in gate.ORDINARY_MANIFESTS:
            documents[environment] = {
                "environment": environment,
                "project_translation_units": [
                    "video/extender/transport/disconnected_stream.cpp"
                ],
                "forbidden_project_translation_units": [
                    gate.QUALIFICATION_TRANSLATION_UNIT
                ],
            }
        return documents

    def write_manifests(self) -> None:
        self.qualification_manifest.write_text(
            json.dumps(self.documents["qualification"], indent=2) + "\n",
            encoding="utf-8",
        )
        for environment, path in self.ordinary_paths.items():
            path.write_text(
                json.dumps(self.documents[environment], indent=2) + "\n",
                encoding="utf-8",
            )

    def expected_load(self, translation_unit: str) -> str:
        relative_build = self.build_root.relative_to(self.project_root)
        return (relative_build / gate.object_path(translation_unit)).as_posix()

    def write_map(self, extra: list[str] | None = None) -> None:
        lines = [
            f"LOAD {self.expected_load(unit)}"
            for unit in gate.REQUIRED_TRANSLATION_UNITS
        ]
        lines.extend(extra or [])
        self.map_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def write_nm(self, omit: str | None = None) -> None:
        symbols = [
            symbol for symbol in gate.REQUIRED_LINKED_SYMBOLS if symbol != omit
        ]
        output = "\n".join(
            f"{0x1000 + index * 4:08x} T {symbol}"
            for index, symbol in enumerate(symbols)
        )
        source = (
            "#!/usr/bin/env python3\n"
            "import sys\n"
            f"sys.stdout.write({(output + chr(10))!r})\n"
        )
        self.nm_path.write_text(source, encoding="utf-8")
        self.nm_path.chmod(self.nm_path.stat().st_mode | stat.S_IXUSR)

    def validate(self) -> dict:
        self.write_manifests()
        return gate.validate(
            environment=self.environment,
            build_root=self.build_root,
            map_path=self.map_path,
            elf_path=self.elf_path,
            qualification_manifest=self.qualification_manifest,
            nm_path=self.nm_path,
        )


class NonreleaseTargetClosureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.evidence = SyntheticClosure(Path(self.temporary.name))

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_valid_closure_passes_without_release_or_runtime_claim(self) -> None:
        report = self.evidence.validate()
        self.assertTrue(
            report["bounded_nonrelease_closure_checks_passed"]
        )
        self.assertFalse(report["release_object_equivalence_proved"])
        self.assertFalse(report["required_symbol_origin_proved"])
        self.assertFalse(report["map_elf_pairing_proved"])
        self.assertEqual(
            "explicitly-supplied-trusted-executable",
            report["target_nm_trust_model"],
        )
        self.assertFalse(report["runtime_or_physical_qualification_proved"])
        self.assertFalse(self.evidence.untrusted_marker.exists())

    def test_missing_required_load_fails_closed(self) -> None:
        lines = self.evidence.map_path.read_text(encoding="utf-8").splitlines()
        self.evidence.map_path.write_text(
            "\n".join(lines[1:]) + "\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(
            gate.ClosureError, "exactly one direct LOAD"
        ):
            self.evidence.validate()

    def test_duplicate_required_load_fails_closed(self) -> None:
        unit = gate.REQUIRED_TRANSLATION_UNITS[0]
        self.evidence.write_map(
            [f"LOAD .pio/build/other/{gate.object_path(unit)}"]
        )
        with self.assertRaisesRegex(
            gate.ClosureError, "exactly one direct LOAD"
        ):
            self.evidence.validate()

    def test_wrong_root_required_load_fails_closed(self) -> None:
        unit = gate.REQUIRED_TRANSLATION_UNITS[0]
        lines = self.evidence.map_path.read_text(encoding="utf-8").splitlines()
        lines[0] = f"LOAD .pio/build/other/{gate.object_path(unit)}"
        self.evidence.map_path.write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
        with self.assertRaisesRegex(gate.ClosureError, "outside the supplied"):
            self.evidence.validate()

    def test_forbidden_prototype_load_fails_closed(self) -> None:
        forbidden = gate.object_path(gate.FORBIDDEN_TRANSLATION_UNITS[0])
        self.evidence.write_map(
            [f"LOAD .pio/build/{self.evidence.environment}/{forbidden}"]
        )
        with self.assertRaisesRegex(
            gate.ClosureError, "forbidden direct LOAD input"
        ):
            self.evidence.validate()

    def test_forbidden_archive_reference_fails_closed(self) -> None:
        forbidden_name = Path(
            gate.object_path(gate.FORBIDDEN_TRANSLATION_UNITS[1])
        ).name
        self.evidence.write_map(
            [f"archive/libprototype.a({forbidden_name})"]
        )
        with self.assertRaisesRegex(gate.ClosureError, "references forbidden"):
            self.evidence.validate()

    def test_required_load_target_must_exist(self) -> None:
        unit = gate.REQUIRED_TRANSLATION_UNITS[0]
        (self.evidence.build_root / gate.object_path(unit)).unlink()
        with self.assertRaisesRegex(gate.ClosureError, "does not exist"):
            self.evidence.validate()

    def test_missing_linked_symbol_fails_closed(self) -> None:
        missing = gate.REQUIRED_LINKED_SYMBOLS[-1]
        self.evidence.write_nm(omit=missing)
        with self.assertRaisesRegex(gate.ClosureError, "lacks required"):
            self.evidence.validate()

    def test_qualification_manifest_omission_fails_closed(self) -> None:
        self.evidence.documents["qualification"][
            "project_translation_units"
        ].remove(gate.REQUIRED_TRANSLATION_UNITS[0])
        with self.assertRaisesRegex(gate.ClosureError, "omits required"):
            self.evidence.validate()

    def test_ordinary_manifest_must_forbid_qualification(self) -> None:
        ordinary = next(iter(gate.ORDINARY_MANIFESTS))
        self.evidence.documents[ordinary][
            "forbidden_project_translation_units"
        ] = []
        with self.assertRaisesRegex(gate.ClosureError, "explicitly forbid"):
            self.evidence.validate()

    def test_ordinary_manifest_must_not_select_qualification(self) -> None:
        ordinary = next(iter(gate.ORDINARY_MANIFESTS))
        self.evidence.documents[ordinary]["project_translation_units"].append(
            gate.QUALIFICATION_TRANSLATION_UNIT
        )
        with self.assertRaisesRegex(gate.ClosureError, "selects qualification"):
            self.evidence.validate()

    def test_nm_timeout_fails_closed(self) -> None:
        with mock.patch.object(
            gate.subprocess,
            "run",
            side_effect=subprocess.TimeoutExpired(["synthetic-nm"], 30),
        ), self.assertRaisesRegex(gate.ClosureError, "timed out"):
            self.evidence.validate()

    def test_map_and_elf_must_name_one_image(self) -> None:
        other_elf = self.evidence.build_root / "other.elf"
        other_elf.write_bytes(b"other synthetic target ELF\n")
        with self.assertRaisesRegex(gate.ClosureError, "one nominal image"):
            gate.validate(
                environment=self.evidence.environment,
                build_root=self.evidence.build_root,
                map_path=self.evidence.map_path,
                elf_path=other_elf,
                qualification_manifest=self.evidence.qualification_manifest,
                nm_path=self.evidence.nm_path,
            )


if __name__ == "__main__":
    unittest.main()
