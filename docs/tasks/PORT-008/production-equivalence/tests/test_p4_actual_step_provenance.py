"""Host-only adversarial tests for the P4 SCons actual-step recorder."""

from __future__ import annotations

import importlib.util
import inspect
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys
import tempfile
from types import ModuleType, SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[5]
SCRIPT = ROOT / "vdp/pio/capture_p4_actual_steps.py"
BUILD_IDENTITY_SCRIPT = ROOT / "vdp/pio/build_identity.py"
SPEC = importlib.util.spec_from_file_location("p4_actual_steps", SCRIPT)
assert SPEC and SPEC.loader
capture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(capture)
IDENTITY_SPEC = importlib.util.spec_from_file_location(
    "p4_build_identity", BUILD_IDENTITY_SCRIPT
)
assert IDENTITY_SPEC and IDENTITY_SPEC.loader
build_identity = importlib.util.module_from_spec(IDENTITY_SPEC)
IDENTITY_SPEC.loader.exec_module(build_identity)


FAKE_DRIVER = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import re
import shlex
import sys

root = Path(__file__).resolve().parents[1]
actions = root / ".test-actions"

def expand_response(arguments):
    expanded = []
    for argument in arguments:
        if argument.startswith("@"):
            expanded.extend(
                expand_response(shlex.split(Path(argument[1:]).read_text()))
            )
        else:
            expanded.append(argument)
    return expanded

arguments = expand_response(sys.argv[1:])
if arguments == ["--version"]:
    print("synthetic-riscv32-g++ 1.0")
elif arguments == ["-dumpmachine"]:
    print("riscv32-esp-elf")
elif arguments == ["-print-prog-name=ld"]:
    print(root / "tools/riscv32-esp-elf-ld")
elif arguments == ["-print-prog-name=cc1plus"]:
    print(root / "tools/cc1plus")
elif arguments == ["-print-prog-name=as"]:
    print(root / "tools/riscv32-esp-elf-as")
elif arguments == ["-print-prog-name=collect2"]:
    print(root / "tools/collect2")
elif "-M" in arguments:
    depfile = Path(arguments[arguments.index("-MF") + 1])
    target = arguments[arguments.index("-MT") + 1]
    source = next(Path(item) for item in arguments if item.endswith(".cpp"))
    header = source.with_name("input.hpp")
    identity = root / (
        ".pio/build-identities/"
        "p4-port008-nonrelease-qualification/build_identity.hpp"
    )
    depfile.write_text(
        f"{shlex.quote(target)}: {shlex.quote(str(source))} "
        f"{shlex.quote(str(header))} {shlex.quote(str(identity))}\n",
        encoding="utf-8",
    )
else:
    output = Path(arguments[arguments.index("-o") + 1])
    output.parent.mkdir(parents=True, exist_ok=True)
    with (root / ".test-spawn-records.jsonl").open("a", encoding="utf-8") as log:
        log.write(
            json.dumps(
                {
                    "argv": sys.argv,
                    "cwd": os.getcwd(),
                    "environment": dict(os.environ),
                },
                sort_keys=True,
            )
            + "\n"
        )
    if "-c" in arguments:
        output.write_bytes(b"fresh selected object")
        source = next(Path(item) for item in arguments if item.endswith(".cpp"))
        if (actions / "change-header").exists():
            source.with_name("input.hpp").write_text("#define INPUT_VALUE 8\n")
        identity = root / (
            ".pio/build-identities/"
            "p4-port008-nonrelease-qualification/build_identity.hpp"
        )
        if (actions / "change-identity").exists():
            identity.write_text(
                identity.read_text().replace("synthetic-build", "tampered-build")
            )
        if (actions / "delete-header").exists():
            source.with_name("input.hpp").unlink()
    else:
        identity = root / (
            ".pio/build-identities/"
            "p4-port008-nonrelease-qualification/build_identity.hpp"
        )
        values = re.findall(r'^#define AGON_EXTENDER_[A-Z_]+ "([^"]+)"$', identity.read_text(), re.M)
        identity_bytes = b"" if (actions / "omit-identity").exists() else b"\0".join(
            value.encode("ascii") for value in values
        )
        output.write_bytes(b"fresh final ELF\0" + identity_bytes)
        map_argument = next(
            argument for argument in arguments if argument.startswith("-Wl,-Map=")
        )
        map_path = Path(map_argument.split("=", 1)[1])
        objects = [Path(argument) for argument in arguments if argument.endswith(".o")]
        map_path.write_text("".join(f"LOAD {item}\n" for item in objects))
        restore = actions / "restore-object"
        if restore.exists():
            objects[0].write_bytes(restore.read_bytes())
'''

FAKE_LINKER = r'''#!/usr/bin/env python3
import sys
if sys.argv[1:] == ["--version"]:
    print("synthetic-riscv32-ld 1.0")
else:
    raise SystemExit("synthetic linker only supports --version")
'''

FAKE_SUBTOOL = r'''#!/usr/bin/env python3
from pathlib import Path
import sys
if sys.argv[1:] == ["--version"]:
    print(f"synthetic-{Path(__file__).name} 1.0")
else:
    raise SystemExit("synthetic subtool only supports --version")
'''

FAKE_ASSEMBLER_DISPATCHER = r'''#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

root = Path(__file__).parent
selectors = [
    argument for argument in sys.argv[1:]
    if argument.startswith("-march=") or argument.startswith("-mespv-spec=")
]
backend_name = (
    "riscv32-esp-elf-as-xespv2p1"
    if any("xesppie" in argument for argument in selectors)
    else "riscv32-esp-elf-as-xespv2p2"
)
backend = root / backend_name
if os.environ.get("ESP_DEBUG_TRACE") == "1" and sys.argv[-1:] == ["--version"]:
    print("Execute: " + json.dumps([str(backend), *sys.argv[1:]]))
    print("synthetic-riscv32-assembler-dispatcher 1.0")
elif sys.argv[1:] == ["--version"]:
    print("synthetic-riscv32-assembler-dispatcher 1.0")
else:
    raise SystemExit("synthetic assembler dispatcher only supports --version")
'''


class SyntheticCapture:
    def __init__(
        self,
        root: Path,
        *,
        stale_object: bool = False,
        spaced_paths: bool = False,
    ) -> None:
        self.root = root
        self.project = root / ("vdp workspace" if spaced_paths else "vdp")
        self.build = self.project / ".pio/build" / capture.ENVIRONMENT
        self.build.mkdir(parents=True)
        self.output = root / "evidence"
        source_relative = (
            "video sources/main file.cpp" if spaced_paths else "video/main.cpp"
        )
        header_relative = (
            "video sources/input.hpp" if spaced_paths else "video/input.hpp"
        )
        self.source = self.project / source_relative
        self.header = self.project / header_relative
        self.source.parent.mkdir(parents=True)
        self.source.write_text('#include "input.hpp"\nint value() { return 7; }\n')
        self.header.write_text("#define INPUT_VALUE 7\n")
        (self.project / "platformio.ini").write_text("[platformio]\n")
        pio = self.project / "pio"
        pio.mkdir()
        (pio / "select_sources.py").write_text("# synthetic selector\n")
        self.hook = pio / "capture_p4_actual_steps.py"
        self.hook.write_bytes(SCRIPT.read_bytes())
        (pio / "build_identity.py").write_bytes(BUILD_IDENTITY_SCRIPT.read_bytes())
        generated_build = self.project / "video/CMakeLists.txt"
        generated_build.parent.mkdir(exist_ok=True)
        generated_build.write_text("# synthetic generated build boundary\n")
        identity_relative = (
            f".pio/build-identities/{capture.ENVIRONMENT}/build_identity.hpp"
        )
        self.identity_header = self.project / identity_relative
        self.identity_header.parent.mkdir(parents=True)
        self.identity_values = {
            "AGON_EXTENDER_SOURCE_IDENTITY": "synthetic-source",
            "AGON_EXTENDER_BUILD_ID": "synthetic-build",
            "AGON_EXTENDER_ARTIFACT_STATUS": "synthetic-status",
            "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY": (
                "synthetic-composition-r01"
            ),
        }
        self.identity_header.write_text(
            "// Generated by pio/build_identity.py; do not edit.\n"
            "#pragma once\n"
            + "".join(
                f'#define {name} "{value}"\n'
                for name, value in self.identity_values.items()
            )
        )
        self.manifest = pio / (
            "p4-port008-nonrelease-qualification-source-selection.json"
        )
        self.manifest.write_text(
            json.dumps(
                {
                    "environment": capture.ENVIRONMENT,
                    "translation_unit_local_build_identity": {
                        "consumer": source_relative,
                        "generated_header": identity_relative,
                    },
                    "project_translation_units": [source_relative],
                    "vendored_translation_units": [],
                    "embedded_text_files": [],
                    "generated_build_files": ["video/CMakeLists.txt"],
                    "header_defined_official_implementation": [
                        header_relative
                    ],
                }
            )
            + "\n"
        )
        tools = self.project / "tools"
        tools.mkdir()
        self.driver = tools / "riscv32-esp-elf-g++"
        self.linker = tools / "riscv32-esp-elf-ld"
        for path, text in (
            (self.driver, FAKE_DRIVER),
            (self.linker, FAKE_LINKER),
            (tools / "cc1plus", FAKE_SUBTOOL),
            (tools / "riscv32-esp-elf-as", FAKE_ASSEMBLER_DISPATCHER),
            (tools / "riscv32-esp-elf-as-xespv2p1", FAKE_SUBTOOL),
            (tools / "riscv32-esp-elf-as-xespv2p2", FAKE_SUBTOOL),
            (tools / "collect2", FAKE_SUBTOOL),
        ):
            path.write_text(text)
            path.chmod(path.stat().st_mode | stat.S_IXUSR)
        self.object = self.build / (source_relative + ".o")
        self.elf = self.build / "firmware.elf"
        self.map = self.build / "firmware.map"
        if stale_object:
            self.object.parent.mkdir(parents=True)
            self.object.write_bytes(b"stale object")
        self.actions = self.project / ".test-actions"
        self.actions.mkdir()
        self.spawn_record_path = self.project / ".test-spawn-records.jsonl"
        self.change_header_during_compile = False
        self.change_identity_during_compile = False
        self.delete_header_during_compile = False
        self.omit_identity_from_elf = False
        self.restore_object_during_link: bytes | None = None
        self.original_spawn_calls = 0

    def session(
        self,
        *,
        capture_runtime=None,
        runtime_refresh=None,
    ) -> capture.CaptureSession:
        return capture.CaptureSession(
            project_root=self.project,
            build_root=self.build,
            output_root=self.output,
            selection_path=self.manifest,
            hook_path=self.hook,
            platformio_version="synthetic-platformio",
            scons_version="synthetic-scons",
            capture_runtime=capture_runtime,
            runtime_refresh=runtime_refresh,
        )

    def original_spawn(self, shell, escape, command, arguments, environment):
        del shell, escape, command, arguments, environment
        self.original_spawn_calls += 1
        raise AssertionError("C++ provenance step delegated to original SPAWN")

    @property
    def spawn_records(self) -> list[dict[str, object]]:
        if not self.spawn_record_path.exists():
            return []
        return [
            json.loads(line)
            for line in self.spawn_record_path.read_text().splitlines()
        ]

    @property
    def spawn_environments(self) -> list[dict[str, str]]:
        return [record["environment"] for record in self.spawn_records]

    def _run_in_project(self, operation) -> None:
        previous = Path.cwd()
        os.chdir(self.project)
        try:
            operation()
        finally:
            os.chdir(previous)

    @staticmethod
    def _escaped(arguments: list[str]) -> list[str]:
        return [capture._ordinary_scons_posix_word(value) for value in arguments]

    def environment(self) -> dict[str, str]:
        return {
            "PATH": os.environ["PATH"],
            "CPATH": "/untrusted/include",
            "CPLUS_INCLUDE_PATH": "/untrusted/cxx",
            "LIBRARY_PATH": "/untrusted/lib",
            "LD_LIBRARY_PATH": "/untrusted/runtime",
            "SOURCE_DATE_EPOCH": "untrusted",
            "SECRET_TOKEN": "must-not-be-recorded-or-forwarded",
        }

    def compile(self, session: capture.CaptureSession) -> None:
        if self.change_header_during_compile:
            (self.actions / "change-header").touch()
        if self.change_identity_during_compile:
            (self.actions / "change-identity").touch()
        if self.delete_header_during_compile:
            (self.actions / "delete-header").touch()
        arguments = [
            str(self.driver),
            "-march=rv32imafc_zicsr_zifencei_xesppie",
            "-o",
            str(self.object),
            "-c",
            str(self.source),
        ]
        escaped = self._escaped(arguments)
        self._run_in_project(
            lambda: session.spawn(
                self.original_spawn,
                "/bin/sh",
                lambda value: value,
                escaped[0],
                escaped,
                self.environment(),
            )
        )

    def compile_with_response(self, session: capture.CaptureSession) -> None:
        response = self.root / "compile.rsp"
        response_arguments = [
            "-march=rv32imafc_zicsr_zifencei_xesppie",
            "-o",
            str(self.object),
            "-c",
            str(self.source),
        ]
        response.write_text(
            " ".join(
                capture._ordinary_scons_posix_word(value)
                for value in response_arguments
            )
            + "\n"
        )
        arguments = [str(self.driver), "@" + str(response)]
        escaped = self._escaped(arguments)
        self._run_in_project(
            lambda: session.spawn(
                self.original_spawn,
                "/bin/sh",
                lambda value: value,
                escaped[0],
                escaped,
                self.environment(),
            )
        )

    def link(self, session: capture.CaptureSession) -> None:
        if self.omit_identity_from_elf:
            (self.actions / "omit-identity").touch()
        if self.restore_object_during_link is not None:
            (self.actions / "restore-object").write_bytes(
                self.restore_object_during_link
            )
        arguments = [
            str(self.driver),
            "-o",
            str(self.elf),
            f"-Wl,-Map={self.map}",
            str(self.object),
        ]
        escaped = self._escaped(arguments)
        self._run_in_project(
            lambda: session.spawn(
                self.original_spawn,
                "/bin/sh",
                lambda value: value,
                escaped[0],
                escaped,
                self.environment(),
            )
        )


class P4ActualStepProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def evidence(self, *, stale_object: bool = False) -> SyntheticCapture:
        return SyntheticCapture(
            Path(self.temporary.name), stale_object=stale_object
        )

    def test_unset_output_variable_leaves_qualification_environment_inert(
        self,
    ) -> None:
        class InertEnvironment:
            def subst(self, value):
                self_value = capture.ENVIRONMENT
                return self_value if value == "$PIOENV" else value

            def IsCleanTarget(self):  # pragma: no cover - must not be called
                raise AssertionError("inactive hook inspected the build target")

        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(capture.install(InertEnvironment()))

    def test_active_install_does_not_require_module_file_global(self) -> None:
        evidence = self.evidence()

        class FakeSession:
            output_root = evidence.output

            def spawn(self, *arguments):  # pragma: no cover - not invoked
                del arguments

            def finalize(self):  # pragma: no cover - not invoked
                return None

        class ActiveEnvironment:
            def __init__(self) -> None:
                self.spawn = object()
                self.replacements: dict[str, object] = {}
                self.preactions: list[tuple[str, object]] = []

            def subst(self, value):
                values = {
                    "$PIOENV": capture.ENVIRONMENT,
                    "$PROJECT_DIR": str(evidence.project),
                    "$BUILD_DIR": str(evidence.build),
                }
                return values.get(value, value)

            def IsCleanTarget(self):
                return False

            def __getitem__(self, key):
                if key != "SPAWN":
                    raise KeyError(key)
                return self.spawn

            def Replace(self, **values):
                self.replacements.update(values)

            def AddPreAction(self, target, action):
                self.preactions.append((target, action))

            def VerboseAction(self, action, message):
                return action, message

        fake_environment = ActiveEnvironment()
        fake_platformio = ModuleType("platformio")
        fake_platformio.__version__ = "synthetic-platformio"
        fake_scons = ModuleType("SCons")
        fake_scons.__version__ = "synthetic-scons"
        fake_scons.__path__ = []
        fake_scons_platform = ModuleType("SCons.Platform")
        fake_scons_subst = ModuleType("SCons.Subst")
        fake_scons.Platform = fake_scons_platform
        fake_scons.Subst = fake_scons_subst
        module_file = capture.__dict__.pop("__file__")
        try:
            with (
                mock.patch.dict(
                    os.environ,
                    {capture.OUTPUT_VARIABLE: str(evidence.output)},
                    clear=True,
                ),
                mock.patch.dict(
                    sys.modules,
                    {
                        "platformio": fake_platformio,
                        "SCons": fake_scons,
                        "SCons.Platform": fake_scons_platform,
                        "SCons.Subst": fake_scons_subst,
                    },
                ),
                mock.patch.object(
                    capture,
                    "_authenticate_piomaxlen_contract",
                    return_value=object(),
                ),
                mock.patch.object(
                    capture,
                    "_capture_runtime_identity",
                    return_value={"policy": "synthetic-runtime"},
                ),
                mock.patch.object(
                    capture,
                    "_persistent_tempfile_class",
                    return_value=object(),
                ),
                mock.patch.object(
                    capture,
                    "CaptureSession",
                    return_value=FakeSession(),
                ) as session_class,
            ):
                self.assertIsNotNone(capture.install(fake_environment))
        finally:
            capture.__dict__["__file__"] = module_file

        self.assertEqual(
            evidence.hook,
            session_class.call_args.kwargs["hook_path"],
        )
        self.assertIn("SPAWN", fake_environment.replacements)
        self.assertEqual(1, len(fake_environment.preactions))

    def test_authenticates_exact_loaded_platformio_piomaxlen_contract(
        self,
    ) -> None:
        runtime = Path(self.temporary.name) / "piomax-runtime"
        platformio_file = runtime / "platformio/__init__.py"
        piomaxlen_file = runtime / "platformio/builder/tools/piomaxlen.py"
        platformio_file.parent.mkdir(parents=True)
        piomaxlen_file.parent.mkdir(parents=True)
        platformio_file.write_text("# synthetic PlatformIO package\n")
        piomaxlen_file.write_text("# synthetic piomaxlen tool\n")
        build_root = runtime / "build"
        build_root.mkdir()

        def quote_spaces(argument):
            return f'"{argument}"' if " " in argument or "\t" in argument else argument

        class UpstreamTempFile:
            pass

        platformio = ModuleType("platformio")
        platformio.__version__ = capture.PINNED_PLATFORMIO_VERSION
        platformio.__file__ = str(platformio_file)
        piomaxlen = ModuleType("piomaxlen")
        piomaxlen.__file__ = str(piomaxlen_file)
        piomaxlen.quote_spaces = quote_spaces
        piomaxlen.IS_WINDOWS = False
        piomaxlen.MAX_LINE_LENGTH = capture.PINNED_PIOMAXLEN_MAX_LINE_LENGTH
        exec(
            "def tempfile_arg_esc_func(argument):\n"
            "    argument = quote_spaces(argument)\n"
            "    if not IS_WINDOWS:\n"
            "        return argument\n"
            "    raise AssertionError('Windows path is outside this test')\n",
            piomaxlen.__dict__,
        )
        self.assertIsNot(piomaxlen.tempfile_arg_esc_func, quote_spaces)
        scons = ModuleType("SCons")
        scons.__version__ = capture.PINNED_SCONS_VERSION
        scons_platform = ModuleType("SCons.Platform")
        scons_platform.TempFileMunge = UpstreamTempFile
        scons_subst = ModuleType("SCons.Subst")
        scons_subst.quote_spaces = quote_spaces
        scons_subst.SUBST_CMD = object()
        scons.Platform = scons_platform
        scons.Subst = scons_subst

        class ContractEnvironment(dict):
            def subst(self, value):
                values = {
                    "$MAXLINELENGTH": str(
                        capture.PINNED_PIOMAXLEN_MAX_LINE_LENGTH
                    ),
                    "$TEMPFILEPREFIX": "@",
                    "$TEMPFILESUFFIX": ".tmp",
                    "$TEMPFILEDIR": str(build_root),
                }
                return values[value]

        environment = ContractEnvironment(
            TEMPFILE=UpstreamTempFile,
            TEMPFILEARGESCFUNC=piomaxlen.tempfile_arg_esc_func,
            TEMPFILEARGJOIN=" ",
        )
        with mock.patch.dict(
            sys.modules,
            {
                "piomaxlen": piomaxlen,
                "SCons": scons,
                "SCons.Platform": scons_platform,
                "SCons.Subst": scons_subst,
            },
        ):
            contract = capture._authenticate_piomaxlen_contract(
                environment,
                platformio,
                scons,
                build_root,
            )
            self.assertIs(
                piomaxlen.tempfile_arg_esc_func,
                contract.escape_argument,
            )
            self.assertIs(scons_subst, contract.scons_subst_module)
            self.assertIs(scons_subst.SUBST_CMD, contract.subst_command_mode)

            environment["TEMPFILEARGESCFUNC"] = lambda value: quote_spaces(value)
            with self.assertRaisesRegex(
                capture.ProvenanceError,
                "authenticated PlatformIO piomaxlen TEMPFILEARGESCFUNC",
            ):
                capture._authenticate_piomaxlen_contract(
                    environment,
                    platformio,
                    scons,
                    build_root,
                )
            environment["TEMPFILEARGESCFUNC"] = (
                piomaxlen.tempfile_arg_esc_func
            )

            replacement_subst = ModuleType("SCons.Subst.replaced")
            with (
                mock.patch.dict(
                    sys.modules,
                    {"SCons.Subst": replacement_subst},
                ),
                self.assertRaisesRegex(
                    capture.ProvenanceError,
                    "authenticated SCons.Subst module was replaced",
                ),
            ):
                contract.validate_response_environment(environment)

            with (
                mock.patch.object(scons_subst, "SUBST_CMD", object()),
                self.assertRaisesRegex(
                    capture.ProvenanceError,
                    "authenticated SCons.Subst response state changed",
                ),
            ):
                contract.validate_response_environment(environment)

            with (
                mock.patch.object(scons_subst, "quote_spaces", lambda value: value),
                self.assertRaisesRegex(
                    capture.ProvenanceError,
                    "authenticated SCons.Subst response state changed",
                ),
            ):
                contract.validate_response_environment(environment)

            with (
                mock.patch.object(scons, "Subst", replacement_subst),
                self.assertRaisesRegex(
                    capture.ProvenanceError,
                    "authenticated SCons.Subst module was replaced",
                ),
            ):
                contract.validate_response_environment(environment)

    def test_platformio_wires_hook_only_into_qualification_environment(
        self,
    ) -> None:
        platformio = (ROOT / "vdp/platformio.ini").read_text()
        hook = "pre:pio/capture_p4_actual_steps.py"
        self.assertEqual(1, platformio.count(hook))
        start = platformio.index(
            "[env:p4-port008-nonrelease-qualification]"
        )
        end = platformio.index("\n[env:", start + 1)
        self.assertIn(hook, platformio[start:end])
        self.assertIn("pre:pio/build_identity.py", platformio[start:end])
        self.assertLess(
            platformio[start:end].index("pre:pio/build_identity.py"),
            platformio[start:end].index(hook),
        )
        self.assertLess(
            platformio[start:end].index("pre:pio/select_sources.py"),
            platformio[start:end].index(hook),
        )

    def test_qualification_identity_is_generated_locally_without_new_identity(
        self,
    ) -> None:
        evidence = self.evidence()

        class FakeEnvironment:
            append_calls: list[dict[str, object]] = []

            def subst(self, value):
                if value == "$PIOENV":
                    return capture.ENVIRONMENT
                if value == "$PROJECT_DIR":
                    return str(evidence.project)
                return value

            def Append(self, **values):
                self.append_calls.append(values)

            def StringifyMacro(self, value):
                return f'"{value}"'

        fake = FakeEnvironment()
        with mock.patch.dict(os.environ, {}, clear=True):
            generated = build_identity.install(fake)
        self.assertEqual(evidence.identity_header, generated)
        self.assertEqual([], fake.append_calls)
        content = evidence.identity_header.read_text()
        self.assertEqual(4, content.count(build_identity.MARKER))
        self.assertIn(
            "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY",
            content,
        )
        self.assertFalse(
            (
                evidence.project
                / f"pio/{capture.ENVIRONMENT}-identity.json"
            ).exists()
        )

    def test_qualification_composition_identity_is_exact_and_role_local(
        self,
    ) -> None:
        evidence = self.evidence()

        class FakeEnvironment:
            append_calls: list[dict[str, object]] = []

            def subst(self, value):
                if value == "$PIOENV":
                    return capture.ENVIRONMENT
                if value == "$PROJECT_DIR":
                    return str(evidence.project)
                return value

            def Append(self, **values):
                self.append_calls.append(values)

        approved = "port-008-forward-qualification-r01"
        with mock.patch.dict(
            os.environ,
            {build_identity.QUALIFICATION_COMPOSITION_VARIABLE: approved},
            clear=True,
        ):
            build_identity.install(FakeEnvironment())
        self.assertIn(
            "#define AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY "
            f'"{approved}"',
            evidence.identity_header.read_text(),
        )
        self.assertNotIn(
            "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY",
            build_identity._render_header("source", "build", "status"),
        )
        with self.assertRaisesRegex(RuntimeError, "qualification-only"):
            build_identity._qualification_composition_identity(
                "p4-browser-vdp",
                {build_identity.QUALIFICATION_COMPOSITION_VARIABLE: approved},
            )

    def test_generated_identity_rejects_symlinked_parent(self) -> None:
        evidence = self.evidence()
        evidence.identity_header.unlink()
        evidence.identity_header.parent.rmdir()
        real_parent = evidence.root / "untrusted-identity-parent"
        real_parent.mkdir()
        evidence.identity_header.parent.symlink_to(
            real_parent, target_is_directory=True
        )

        class FakeEnvironment:
            def subst(self, value):
                if value == "$PIOENV":
                    return capture.ENVIRONMENT
                if value == "$PROJECT_DIR":
                    return str(evidence.project)
                return value

            def Append(self, **values):  # pragma: no cover - must not run
                raise AssertionError(values)

        with mock.patch.dict(os.environ, {}, clear=True), self.assertRaisesRegex(
            RuntimeError, "unsafe parent component"
        ):
            build_identity.install(FakeEnvironment())

    def test_generated_identity_rejects_symlinked_destination(self) -> None:
        evidence = self.evidence()
        evidence.identity_header.unlink()
        external = evidence.root / "external-identity.hpp"
        external.write_text("external\n")
        evidence.identity_header.symlink_to(external)

        with self.assertRaisesRegex(RuntimeError, "unsafe existing node"):
            build_identity._write_if_changed(
                evidence.identity_header,
                build_identity._render_header("source", "build", "status"),
                evidence.project,
            )
        self.assertEqual("external\n", external.read_text())

    def test_identity_selection_and_boot_wrapper_paths_are_exact(self) -> None:
        cases = (
            (
                "p4-browser-vdp",
                "video/extender/boot/p4_browser_vdp.cpp",
            ),
            (
                capture.ENVIRONMENT,
                "video/extender/boot/p4_parallel_qualification_vdp.cpp",
            ),
        )
        for environment, consumer in cases:
            selection = json.loads(
                (ROOT / f"vdp/pio/{environment}-source-selection.json").read_text()
            )
            identity = selection["translation_unit_local_build_identity"]
            self.assertEqual(consumer, identity["consumer"])
            self.assertEqual(
                f".pio/build-identities/{environment}/build_identity.hpp",
                identity["generated_header"],
            )
            for definition in selection.get("component_compile_definitions", []):
                self.assertNotIn("AGON_EXTENDER_BUILD_ID", definition)
                self.assertNotIn("AGON_EXTENDER_SOURCE_IDENTITY", definition)
                self.assertNotIn("AGON_EXTENDER_ARTIFACT_STATUS", definition)
                self.assertNotIn(
                    "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY",
                    definition,
                )
        browser_bridge = (
            ROOT / "vdp/video/extender/boot/p4_browser_vdp.cpp"
        ).read_text()
        qualification_bridge = (
            ROOT / "vdp/video/extender/boot/p4_parallel_qualification_vdp.cpp"
        ).read_text()
        self.assertIn(
            ".pio/build-identities/p4-browser-vdp/build_identity.hpp",
            browser_bridge,
        )
        self.assertIn(
            ".pio/build-identities/"
            "p4-port008-nonrelease-qualification/build_identity.hpp",
            qualification_bridge,
        )
        self.assertNotIn(
            "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY",
            browser_bridge,
        )

    def test_local_identity_header_is_boot_only_and_durable_in_capture(
        self,
    ) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.compile(session)
        evidence.link(session)
        report = session.finalize()
        identity = report["translation_unit_local_build_identity"]
        self.assertEqual(
            "video/main.cpp", identity["consumer"]
        )
        self.assertEqual(
            evidence.identity_header.read_text(), identity["content_utf8"]
        )
        self.assertEqual(
            evidence.identity_values, identity["definitions"]
        )
        self.assertTrue(
            report["checked_claims"][
                "build_identity_local_to_boot_compile_proved"
            ]
        )
        self.assertTrue(
            all(
                item["ascii_occurrences"] >= 1
                for item in identity["final_elf_strings"].values()
            )
        )

    def test_complete_capture_binds_compile_link_tools_and_artifacts(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.compile(session)
        evidence.link(session)
        report = session.finalize()

        self.assertEqual("complete", report["status"])
        self.assertEqual(capture.EVIDENCE_KIND, report["evidence_kind"])
        self.assertEqual(1, len(report["capture"]["required_target_compiles"]))
        compile_step = report["capture"]["required_target_compiles"][0]
        link_step = report["capture"]["final_link"]
        self.assertEqual(
            "verified-before-and-after",
            compile_step["input_stability"],
        )
        self.assertEqual(
            "verified-before-and-after",
            link_step["input_stability"],
        )
        self.assertEqual([], compile_step["response_files"])
        self.assertEqual([], link_step["response_files"])
        self.assertTrue(link_step["producer_chaining"][0]["matched"])
        self.assertEqual(
            {"cc1plus", "as"},
            set(compile_step["driver_identity"]["compiler_subtools"]),
        )
        assembler = compile_step["driver_identity"]["compiler_subtools"]["as"]
        dispatch = assembler["dispatcher_backend"]
        self.assertEqual(
            "espressif-debug-trace-dispatch-v1", dispatch["policy"]
        )
        self.assertEqual(
            ["-march=rv32imafc_zicsr_zifencei_xesppie"],
            dispatch["selector_arguments"],
        )
        self.assertTrue(
            dispatch["backend"]["resolved_path"].endswith(
                "riscv32-esp-elf-as-xespv2p1"
            )
        )
        self.assertIn(
            dispatch["backend"]["resolved_path"],
            compile_step["dependencies"]["before"],
        )
        self.assertEqual(
            {"collect2", "ld"},
            set(link_step["driver_identity"]["link_subtools"]),
        )
        self.assertTrue(
            report["checked_claims"]["actual_scons_final_link_step_observed"]
        )
        self.assertEqual(
            "direct-subprocess-no-shell-v1", compile_step["execution_policy"]
        )
        self.assertEqual(
            "direct-subprocess-no-shell-v1", link_step["execution_policy"]
        )
        self.assertIsNone(compile_step["shell"])
        self.assertIsNone(link_step["shell"])
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_scons_argument_boundaries_preserve_paths_with_spaces(self) -> None:
        evidence = SyntheticCapture(Path(self.temporary.name), spaced_paths=True)
        session = evidence.session()
        evidence.compile(session)
        evidence.link(session)
        report = session.finalize()
        compile_step = report["capture"]["required_target_compiles"][0]
        self.assertIn(str(evidence.source), compile_step["actual_argument_vector"])
        self.assertIn(str(evidence.source), compile_step["expanded_argument_vector"])
        self.assertEqual(
            "pinned-scons-posix-shell-word-inverse-v1",
            compile_step["argument_boundary_policy"],
        )

    def test_pinned_scons_inverse_accepts_only_exact_round_trips(self) -> None:
        values = (
            "/tool/riscv32-esp-elf-g++",
            "/source tree/main file.cpp",
            '-DIDENTITY="value with space"',
            "literal$dollar",
            "literal\\backslash",
        )
        for value in values:
            ordinary = capture._ordinary_scons_posix_word(value)
            self.assertEqual(
                value,
                capture._decode_pinned_scons_posix_word(ordinary, "test"),
            )
            literal = capture._scons_posix_literal_escape(value)
            self.assertIsNotNone(literal)
            self.assertEqual(
                value,
                capture._decode_pinned_scons_posix_word(literal, "test"),
            )
        for unsafe in (
            "unescaped$variable",
            "*.cpp",
            "one;two",
            "'single-quoted'",
            r"dollar\\$word",
        ):
            with self.subTest(unsafe=unsafe), self.assertRaises(
                capture.ProvenanceError
            ):
                capture._decode_pinned_scons_posix_word(unsafe, "test")

    def test_driver_later_in_argv_is_rejected_without_delegation(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        arguments = [
            "/usr/bin/env",
            str(evidence.driver),
            "-o",
            str(evidence.object),
            "-c",
            str(evidence.source),
        ]
        escaped = evidence._escaped(arguments)
        with self.assertRaisesRegex(
            capture.ProvenanceError, r"driver appears at argv\[1\]"
        ):
            evidence._run_in_project(
                lambda: session.spawn(
                    evidence.original_spawn,
                    "/bin/sh",
                    lambda value: value,
                    escaped[0],
                    escaped,
                    evidence.environment(),
                )
            )
        self.assertEqual(0, evidence.original_spawn_calls)
        self.assertFalse(evidence.object.exists())

    def test_malformed_later_driver_token_is_rejected_without_delegation(
        self,
    ) -> None:
        evidence = self.evidence()
        session = evidence.session()
        arguments = ["/usr/bin/env", str(evidence.driver) + ";"]
        with self.assertRaisesRegex(
            capture.ProvenanceError, r"driver appears at argv\[1\]"
        ):
            session.spawn(
                evidence.original_spawn,
                "/bin/sh",
                lambda value: value,
                arguments[0],
                arguments,
                evidence.environment(),
            )
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_required_target_output_with_non_driver_prefix_is_rejected(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        for output, message in (
            (evidence.object, "required selected C\\+\\+ object"),
            (evidence.elf, "final firmware ELF"),
            (evidence.map, "final link map"),
        ):
            with self.subTest(output=output), self.assertRaisesRegex(
                capture.ProvenanceError, message
            ):
                arguments = ["/usr/bin/not-a-cxx-driver", "-o", str(output)]
                escaped = evidence._escaped(arguments)
                evidence._run_in_project(
                    lambda: session.spawn(
                        evidence.original_spawn,
                        "/bin/sh",
                        lambda value: value,
                        escaped[0],
                        escaped,
                        evidence.environment(),
                    )
                )
        self.assertEqual(0, evidence.original_spawn_calls)
        self.assertFalse(evidence.object.exists())
        self.assertFalse(evidence.elf.exists())

    def test_undecodable_output_after_non_driver_is_not_delegated(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        arguments = [
            "/usr/bin/not-a-cxx-driver",
            "-o",
            '"' + str(evidence.object),
        ]
        with self.assertRaisesRegex(
            capture.ProvenanceError, "output argument.*not canonically decodable"
        ):
            session.spawn(
                evidence.original_spawn,
                "/bin/sh",
                lambda value: value,
                arguments[0],
                arguments,
                evidence.environment(),
            )
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_empty_argv_is_rejected_without_delegation(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        with self.assertRaisesRegex(capture.ProvenanceError, "empty SCons argv"):
            session.spawn(
                evidence.original_spawn,
                "/bin/sh",
                lambda value: value,
                "",
                [],
                evidence.environment(),
            )
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_undecodable_argv0_fails_closed_with_bounded_context(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        malformed = [
            "<SCons.Script._persistent_tempfile_class.<locals>."
            "PersistentProvenanceTempFile",
            "object",
            "at",
            "0x1234>" + ("x" * 4096),
            *("surplus" for _ in range(100)),
        ]
        with self.assertRaises(capture.ProvenanceError) as raised:
            session.spawn(
                evidence.original_spawn,
                "/bin/sh",
                lambda value: value,
                malformed[0],
                malformed,
                evidence.environment(),
            )
        message = str(raised.exception)
        self.assertIn("cannot classify argv[0]", message)
        self.assertIn("callable expansion", message)
        self.assertIn("argc=104", message)
        self.assertLessEqual(
            len(capture._bounded_spawn_context(malformed[0], malformed)),
            capture.MAX_SPAWN_CONTEXT_CHARS,
        )
        self.assertLess(
            len(message), capture.MAX_SPAWN_CONTEXT_CHARS + 512
        )
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_non_cxx_shell_action_is_delegated_without_decoding(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        calls: list[tuple[object, ...]] = []

        def original(*values):
            calls.append(values)
            return 17

        arguments = ["/bin/sh", "-c", "printf test && true"]
        result = session.spawn(
            original,
            "/bin/sh",
            lambda value: value,
            arguments[0],
            arguments,
            evidence.environment(),
        )
        self.assertEqual(17, result)
        self.assertEqual(1, len(calls))
        self.assertFalse((evidence.output / "events.jsonl").exists())

    def test_cxx_step_outside_project_working_directory_is_rejected(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        arguments = [
            str(evidence.driver),
            "-o",
            str(evidence.object),
            "-c",
            str(evidence.source),
        ]
        escaped = evidence._escaped(arguments)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "working directory differs"
        ):
            session.spawn(
                evidence.original_spawn,
                "/bin/sh",
                lambda value: value,
                escaped[0],
                escaped,
                evidence.environment(),
            )
        self.assertEqual(0, evidence.original_spawn_calls)
        self.assertFalse(evidence.object.exists())

    def test_child_environment_is_minimal_recorded_and_injection_free(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.compile(session)
        evidence.link(session)
        report = session.finalize()
        expected_keys = {"PATH", "LANG", "LC_ALL", "TZ", "TMPDIR", "PWD"}
        for child in evidence.spawn_environments:
            self.assertEqual(expected_keys, set(child))
            self.assertEqual("C", child["LC_ALL"])
            self.assertEqual(str(evidence.project), child["PWD"])
            self.assertNotIn("SECRET_TOKEN", child)
            self.assertNotIn("CPATH", child)
        environment_record = report["capture"]["final_link"][
            "child_environment"
        ]
        self.assertEqual(
            "sanitized-deterministic-v1", environment_record["policy"]
        )
        self.assertEqual(expected_keys, set(environment_record["variables"]))
        self.assertEqual(
            str(evidence.project), environment_record["variables"]["PWD"]
        )
        self.assertEqual(
            "cleared", environment_record["source_date_epoch"]["disposition"]
        )

    def test_capture_runtime_binds_package_trees_and_fails_on_change(self) -> None:
        runtime_root = Path(self.temporary.name) / "runtime"
        platformio_root = runtime_root / "platformio"
        scons_root = runtime_root / "SCons"
        for package_root in (platformio_root, scons_root):
            package_root.mkdir(parents=True)
            (package_root / "__init__.py").write_text("# package\n")
            (package_root / "core.py").write_text("VALUE = 1\n")
            cache = package_root / "__pycache__"
            cache.mkdir()
            (cache / "core.pyc").write_bytes(b"mutable cache")
        platformio = SimpleNamespace(
            __file__=str(platformio_root / "__init__.py"),
            __version__="synthetic-platformio",
        )
        scons = SimpleNamespace(
            __file__=str(scons_root / "__init__.py"),
            __version__="synthetic-scons",
        )
        def runtime_identity():
            with mock.patch.object(
                capture.sys,
                "argv",
                [str(Path(capture.sys.executable).resolve())],
            ):
                return capture._capture_runtime_identity(platformio, scons)

        runtime = runtime_identity()
        self.assertEqual("capture-runtime-file-set-v1", runtime["policy"])
        self.assertEqual(
            {"__init__.py", "core.py", "__pycache__/core.pyc"},
            set(runtime["platformio"]["files"]),
        )

        evidence = self.evidence()
        session = evidence.session(
            capture_runtime=runtime,
            runtime_refresh=runtime_identity,
        )
        evidence.compile(session)
        evidence.link(session)
        (platformio_root / "core.py").write_text("VALUE = 2\n")
        with self.assertRaisesRegex(capture.ProvenanceError, "runtime changed"):
            session.finalize()

    def test_capture_runtime_rejects_symlinked_package_member(self) -> None:
        package_root = Path(self.temporary.name) / "linked-package"
        package_root.mkdir()
        module_file = package_root / "__init__.py"
        module_file.write_text("# package\n")
        external = Path(self.temporary.name) / "external.py"
        external.write_text("VALUE = 1\n")
        (package_root / "linked.py").symlink_to(external)
        module = SimpleNamespace(__file__=str(module_file), __version__="1")
        with self.assertRaisesRegex(capture.ProvenanceError, "symbolic link"):
            capture._runtime_package_identity(module, name="test", version="1")

    def test_missing_driver_selected_compile_subtool_fails_closed(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        (evidence.project / "tools/cc1plus").unlink()
        evidence.compile(session)
        evidence.link(session)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "selected cc1plus identity failed"
        ):
            session.finalize()

    def test_missing_selected_assembler_backend_fails_closed(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        (evidence.project / "tools/riscv32-esp-elf-as-xespv2p1").unlink()
        evidence.compile(session)
        evidence.link(session)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "assembler backend dispatch identity failed"
        ):
            session.finalize()

    def test_stale_object_is_rejected_before_any_spawn(self) -> None:
        evidence = self.evidence(stale_object=True)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "absent target outputs"
        ):
            evidence.session()
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_changed_transitive_dependency_fails_closed(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.change_header_during_compile = True
        evidence.compile(session)
        evidence.link(session)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "transitive compile input stability"
        ):
            session.finalize()

    def test_missing_transitive_dependency_fails_closed(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.delete_header_during_compile = True
        evidence.compile(session)
        evidence.link(session)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "transitive compile input stability"
        ):
            session.finalize()

    def test_changed_generated_identity_header_fails_closed(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.change_identity_during_compile = True
        evidence.compile(session)
        evidence.link(session)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "transitive compile input stability"
        ):
            session.finalize()

    def test_missing_identity_value_in_final_elf_fails_closed(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.compile(session)
        evidence.omit_identity_from_elf = True
        evidence.link(session)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "firmware.elf lacks local build-identity"
        ):
            session.finalize()

    def test_response_file_bytes_are_preserved_and_stable(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.compile_with_response(session)
        evidence.link(session)
        report = session.finalize()
        response_files = report["capture"]["required_target_compiles"][0][
            "response_files"
        ]
        self.assertEqual(1, len(response_files))
        self.assertTrue(response_files[0]["stable_before_and_after"])
        self.assertTrue(response_files[0]["byte_round_trip_verified"])
        self.assertEqual(
            "pinned-scons-quote-spaces-response-v1",
            response_files[0]["argument_boundary_policy"],
        )
        blob = evidence.output / response_files[0]["saved_blob"]
        self.assertEqual(response_files[0]["sha256"], capture.sha256_file(blob))

    def test_pinned_response_round_trip_preserves_spaces_and_defines(self) -> None:
        arguments = [
            "-o",
            "/build tree/output file.o",
            '-DIDENTITY="value with space"',
            "/source tree/input file.cpp",
        ]
        data = (
            " ".join(
                capture._ordinary_scons_posix_word(value) for value in arguments
            )
            + "\n"
        ).encode()
        decoded, encoded = capture._decode_pinned_scons_response(data, "test")
        self.assertEqual(arguments, decoded)
        self.assertEqual(
            [capture._ordinary_scons_posix_word(value) for value in arguments],
            encoded,
        )
        with self.assertRaisesRegex(
            capture.ProvenanceError, "live unquoted shell syntax|round-trip"
        ):
            capture._decode_pinned_scons_response(
                b"-o 'output file.o' -c input.cpp\n", "test"
            )

    def test_persistent_tempfile_requires_exact_scons_response_policy(
        self,
    ) -> None:
        scons = ModuleType("SCons")
        subst = ModuleType("SCons.Subst")

        def quote_spaces(argument):
            return f'"{argument}"' if " " in argument or "\t" in argument else argument

        subst.quote_spaces = quote_spaces
        subst.SUBST_CMD = object()
        scons.Subst = subst

        class FakeEnvironment(dict):
            def subst_list(self, command, mode, target, source):
                self.last_substitution = (mode, target, source)
                return [command]

            def subst(self, value):
                if value == "$MAXLINELENGTH":
                    return self.get("maximum", "1")
                if value == "$TEMPFILEPREFIX":
                    return self.get("prefix", "@")
                if value == "$TEMPFILESUFFIX":
                    return self.get("suffix", ".tmp")
                if value == "$TEMPFILEDIR":
                    return str(self["build_root"])
                raise AssertionError(value)

        response_root = Path(self.temporary.name) / "tempfile-evidence"
        (response_root / "responses").mkdir(parents=True)
        build_root = Path(self.temporary.name) / "tempfile-build"
        build_root.mkdir()
        piomaxlen = ModuleType("piomaxlen")
        piomaxlen.quote_spaces = quote_spaces
        piomaxlen.IS_WINDOWS = False
        piomaxlen.MAX_LINE_LENGTH = 1
        exec(
            "def tempfile_arg_esc_func(argument):\n"
            "    return quote_spaces(argument)\n",
            piomaxlen.__dict__,
        )
        scons_subst_mode = object()
        subst.SUBST_CMD = scons_subst_mode
        contract = capture._PiomaxlenContract(
            module=piomaxlen,
            scons_module=scons,
            scons_subst_module=subst,
            subst_command_mode=scons_subst_mode,
            escape_argument=piomaxlen.tempfile_arg_esc_func,
            quote_spaces=quote_spaces,
            build_root=build_root,
            maximum_line_length=1,
        )
        with mock.patch.dict(
            sys.modules,
            {
                "SCons": scons,
                "SCons.Subst": subst,
                "piomaxlen": piomaxlen,
            },
        ):
            tempfile_class = capture._persistent_tempfile_class(
                response_root,
                contract,
            )
            command = ["driver", "-o", "output file.o", "-c", "input.cpp"]
            self.assertEqual(
                ["target", "source", "env", "for_signature"],
                list(inspect.signature(tempfile_class(command)).parameters),
            )
            environment = FakeEnvironment(
                TEMPFILEARGESCFUNC=piomaxlen.tempfile_arg_esc_func,
                TEMPFILEARGJOIN=" ",
                build_root=build_root,
                prefix="@",
                suffix=".tmp",
            )
            result = tempfile_class(command)(None, None, environment, False)
            self.assertEqual("driver", result[0])
            response_path = Path(result[1][1:])
            decoded, _encoded = capture._decode_pinned_scons_response(
                response_path.read_bytes(), "synthetic persistent response"
            )
            self.assertEqual(command[1:], decoded)
            self.assertIs(
                scons_subst_mode,
                environment.last_substitution[0],
            )

            unsupported = (
                ({"TEMPFILEARGESCFUNC": lambda value: value}, "ARGESCFUNC"),
                ({"TEMPFILEARGJOIN": "\n"}, "ARGJOIN"),
                ({"prefix": "-via"}, "PREFIX"),
                ({"suffix": ".lnk"}, "SUFFIX"),
                ({"maximum": "2"}, "MAXLINELENGTH"),
                (
                    {"build_root": Path(self.temporary.name)},
                    "TEMPFILEDIR",
                ),
            )
            for changes, message in unsupported:
                with self.subTest(message=message):
                    rejected = FakeEnvironment(environment)
                    rejected.update(changes)
                    with self.assertRaisesRegex(capture.ProvenanceError, message):
                        tempfile_class(command)(
                            None, None, rejected, False
                        )

            with (
                mock.patch.object(subst, "SUBST_CMD", object()),
                self.assertRaisesRegex(
                    capture.ProvenanceError,
                    "authenticated SCons.Subst response state changed",
                ),
            ):
                tempfile_class(command)(None, None, environment, False)

            replacement_subst = ModuleType("SCons.Subst.replaced")
            with (
                mock.patch.dict(
                    sys.modules,
                    {"SCons.Subst": replacement_subst},
                ),
                self.assertRaisesRegex(
                    capture.ProvenanceError,
                    "authenticated SCons.Subst module was replaced",
                ),
            ):
                tempfile_class(command)(None, None, environment, False)

    def test_pinned_platformio_scons_long_response_executes_through_capture(
        self,
    ) -> None:
        scons_root = (
            ROOT
            / "vdp/.pio/packages/tool-scons/scons-local-4.8.1"
        )
        if not (scons_root / "SCons/__init__.py").is_file():
            self.skipTest("pinned SCons 4.8.1 package is not installed")
        if importlib.util.find_spec("platformio") is None:
            self.skipTest("pinned PlatformIO package is not installed")

        evidence = SyntheticCapture(
            Path(self.temporary.name),
            spaced_paths=True,
        )
        response_root = Path(self.temporary.name) / "real-scons-responses"
        response_root.joinpath("responses").mkdir(parents=True)
        build_root = Path(self.temporary.name) / "real-scons-build"
        build_root.mkdir()
        filler = [
            f"-DPROVENANCE_LONG_{index:03d}=" + ("X" * 1000)
            for index in range(132)
        ]
        command = [
            str(evidence.driver),
            "-march=rv32imafc_zicsr_zifencei_xesppie",
            "-o",
            str(evidence.object),
            "-c",
            str(evidence.source),
            *filler,
        ]
        self.assertGreater(
            sum(len(argument) for argument in command) + len(command) - 1,
            capture.PINNED_PIOMAXLEN_MAX_LINE_LENGTH,
        )
        command_path = Path(self.temporary.name) / "long-command.json"
        command_path.write_text(json.dumps(command), encoding="utf-8")
        script = r'''
import importlib.util
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
scons_root = Path(sys.argv[2])
response_root = Path(sys.argv[3])
build_root = Path(sys.argv[4])
command = json.loads(Path(sys.argv[5]).read_text(encoding="utf-8"))
sys.path.insert(0, str(scons_root))
import platformio
import SCons
import SCons.Platform
import SCons.Script
import SCons.Subst

spec = importlib.util.spec_from_file_location(
    "p4_actual_steps_real_scons",
    root / "vdp/pio/capture_p4_actual_steps.py",
)
assert spec and spec.loader
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
piomaxlen_path = (
    Path(platformio.__file__).resolve().parent
    / "builder/tools/piomaxlen.py"
)
piomaxlen_spec = importlib.util.spec_from_file_location(
    "piomaxlen", piomaxlen_path
)
assert piomaxlen_spec and piomaxlen_spec.loader
piomaxlen = importlib.util.module_from_spec(piomaxlen_spec)
sys.modules["piomaxlen"] = piomaxlen
piomaxlen_spec.loader.exec_module(piomaxlen)
env = SCons.Script.Environment(tools=[])
env.Replace(
    TEMPFILE=SCons.Platform.TempFileMunge,
    MAXLINELENGTH=piomaxlen.MAX_LINE_LENGTH,
    TEMPFILEARGESCFUNC=piomaxlen.tempfile_arg_esc_func,
    TEMPFILEARGJOIN=" ",
    TEMPFILEPREFIX="@",
    TEMPFILESUFFIX=".tmp",
    TEMPFILEDIR=str(build_root),
)
contract = capture._authenticate_piomaxlen_contract(
    env,
    platformio,
    SCons,
    build_root,
)
tempfile_class = capture._persistent_tempfile_class(response_root, contract)
env.Replace(TEMPFILE=tempfile_class(command))
result = env.subst_list(
    "$TEMPFILE",
    SCons.Subst.SUBST_CMD,
    target=[],
    source=[],
)
print(
    json.dumps(
        {
            "piomaxlen_escape_is_distinct": (
                piomaxlen.tempfile_arg_esc_func is not SCons.Subst.quote_spaces
            ),
            "scons_version": SCons.__version__,
            "result": [[str(item) for item in line] for line in result],
        }
    )
)
'''
        completed = subprocess.run(
            [
                sys.executable,
                "-B",
                "-c",
                script,
                str(ROOT),
                str(scons_root),
                str(response_root),
                str(build_root),
                str(command_path),
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual("4.8.1", result["scons_version"])
        self.assertTrue(result["piomaxlen_escape_is_distinct"])
        self.assertEqual(1, len(result["result"]))
        returned_arguments = result["result"][0]
        self.assertEqual(str(evidence.driver), returned_arguments[0])
        self.assertEqual(2, len(returned_arguments))
        self.assertTrue(returned_arguments[1].startswith("@"))
        response_path = Path(returned_arguments[1][1:])
        self.assertEqual(response_root / "responses", response_path.parent)
        expected_response = (
            " ".join(
                f'"{argument}"'
                if " " in argument or "\t" in argument
                else argument
                for argument in command[1:]
            )
            + "\n"
        ).encode("utf-8")
        self.assertEqual(expected_response, response_path.read_bytes())
        self.assertEqual(
            "scons-" + capture.sha256_bytes(expected_response) + ".rsp",
            response_path.name,
        )

        session = evidence.session()
        escaped_arguments = evidence._escaped(returned_arguments)
        evidence._run_in_project(
            lambda: session.spawn(
                evidence.original_spawn,
                "/bin/sh",
                lambda value: value,
                escaped_arguments[0],
                escaped_arguments,
                evidence.environment(),
            )
        )
        evidence.link(session)
        report = session.finalize()
        compile_record = report["capture"]["required_target_compiles"][0]
        self.assertEqual(
            command[1:],
            compile_record["expanded_argument_vector"][1:],
        )
        self.assertEqual(
            [str(evidence.driver), "@" + str(response_path)],
            evidence.spawn_records[0]["argv"],
        )
        self.assertEqual(1, len(compile_record["response_files"]))
        response_record = compile_record["response_files"][0]
        self.assertTrue(response_record["byte_round_trip_verified"])
        self.assertTrue(response_record["stable_before_and_after"])
        retained_blob = evidence.output / response_record["saved_blob"]
        self.assertEqual(expected_response, retained_blob.read_bytes())

    def test_nested_response_file_is_rejected_before_execution(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        nested = evidence.root / "nested.rsp"
        nested.write_text("-c ignored.cpp\n")
        outer = evidence.root / "outer.rsp"
        outer.write_text(
            shlex.join(
                [
                    "-o",
                    str(evidence.object),
                    "-c",
                    str(evidence.source),
                    "@" + str(nested),
                ]
            )
            + "\n"
        )
        arguments = [str(evidence.driver), "@" + str(outer)]
        escaped = evidence._escaped(arguments)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "nested response-file indirection"
        ):
            evidence._run_in_project(
                lambda: session.spawn(
                    evidence.original_spawn,
                    "/bin/sh",
                    lambda value: value,
                    escaped[0],
                    escaped,
                    evidence.environment(),
                )
            )
        self.assertFalse(evidence.object.exists())
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_link_tamper_then_restore_does_not_match_compile_producer(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.compile(session)
        produced = evidence.object.read_bytes()
        evidence.object.write_bytes(b"tampered before link")
        evidence.restore_object_during_link = produced
        evidence.link(session)
        with self.assertRaisesRegex(
            capture.ProvenanceError, "link input stability"
        ):
            session.finalize()

    def test_missing_actual_steps_fail_closed(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        with self.assertRaisesRegex(
            capture.ProvenanceError, r"executed C\+\+ compile"
        ):
            session.finalize()

    def test_multiline_shell_command_is_rejected_without_execution(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        with self.assertRaisesRegex(capture.ProvenanceError, "a newline"):
            session.spawn(
                evidence.original_spawn,
                "/bin/sh",
                lambda value: value,
                str(evidence.driver),
                [str(evidence.driver), "\nrm", "/tmp/anything"],
                evidence.environment(),
            )
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_shell_control_text_is_rejected_without_execution(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        with self.assertRaisesRegex(capture.ProvenanceError, "shell syntax"):
            session.spawn(
                evidence.original_spawn,
                "/bin/sh",
                lambda value: value,
                str(evidence.driver),
                [str(evidence.driver), "&&", "/tmp/anything"],
                evidence.environment(),
            )
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_unproved_nested_tool_selection_is_rejected_without_execution(
        self,
    ) -> None:
        evidence = self.evidence()
        session = evidence.session()
        with self.assertRaisesRegex(
            capture.ProvenanceError, "unproved nested tool"
        ):
            arguments = [
                str(evidence.driver),
                "-flto",
                "-o",
                str(evidence.object),
                "-c",
                str(evidence.source),
            ]
            escaped = evidence._escaped(arguments)
            evidence._run_in_project(
                lambda: session.spawn(
                    evidence.original_spawn,
                    "/bin/sh",
                    lambda value: value,
                    escaped[0],
                    escaped,
                    evidence.environment(),
                )
            )
        self.assertEqual(0, evidence.original_spawn_calls)

    def test_tampered_raw_event_log_fails_closed(self) -> None:
        evidence = self.evidence()
        session = evidence.session()
        evidence.compile(session)
        evidence.link(session)
        event_log = evidence.output / "events.jsonl"
        event_log.write_bytes(event_log.read_bytes() + b"{}\n")
        with self.assertRaisesRegex(
            capture.ProvenanceError, "differs from the in-memory"
        ):
            session.finalize()

    def test_symlinked_output_path_is_rejected(self) -> None:
        evidence = self.evidence()
        real_parent = evidence.root / "real-parent"
        real_parent.mkdir()
        linked_parent = evidence.root / "linked-parent"
        linked_parent.symlink_to(real_parent, target_is_directory=True)
        evidence.output = linked_parent / "evidence"
        with self.assertRaisesRegex(capture.ProvenanceError, "traverses a symlink"):
            evidence.session()


if __name__ == "__main__":
    unittest.main()
