"""Select the exact application and vendored closure for an active P4 target.

PlatformIO's normal library discovery would compile vdp-gl's broad classic-
ESP32 implementation family. This recurring build hook instead consumes a
tracked, machine-readable allowlist and adds only the named translation units.
It deliberately does not infer a source closure or edit vendored code.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re

Import("env")  # type: ignore[name-defined]  # Provided by PlatformIO/SCons.


environment = env.subst("$PIOENV")  # type: ignore[name-defined]
project_dir = Path(env.subst("$PROJECT_DIR"))  # type: ignore[name-defined]
environment_selection = project_dir / f"pio/{environment}-source-selection.json"
selection_path = (
    environment_selection
    if environment_selection.is_file()
    else project_dir / "pio/source-selection.json"
)
selection = json.loads(selection_path.read_text(encoding="utf-8"))
if environment != selection["environment"]:
    raise RuntimeError(
        f"{selection_path}: describes {selection['environment']}, not {environment}"
    )
if selection.get("retired") is True:
    raise RuntimeError(
        f"{selection_path}: source selection is rejected and superseded; "
        "it is retained only as historical inventory"
    )

project_translation_units = selection["project_translation_units"]
if len(project_translation_units) != len(set(project_translation_units)):
    raise RuntimeError(f"{selection_path}: duplicate project translation unit")
forbidden_translation_units = set(
    selection.get("forbidden_project_translation_units", [])
)
selected_forbidden = forbidden_translation_units.intersection(
    project_translation_units
)
if selected_forbidden:
    raise RuntimeError(
        f"{selection_path}: selects forbidden translation units: "
        + ", ".join(sorted(selected_forbidden))
    )

local_identity = selection.get("translation_unit_local_build_identity")
if local_identity is not None:
    if not isinstance(local_identity, dict) or set(local_identity) != {
        "consumer",
        "generated_header",
    }:
        raise RuntimeError(
            f"{selection_path}: translation_unit_local_build_identity must "
            "contain exactly consumer and generated_header"
        )
    if local_identity["consumer"] not in project_translation_units:
        raise RuntimeError(
            f"{selection_path}: local build-identity consumer is not a "
            "selected translation unit"
        )
    expected_identity_header = (
        f".pio/build-identities/{environment}/build_identity.hpp"
    )
    if local_identity["generated_header"] != expected_identity_header:
        raise RuntimeError(
            f"{selection_path}: local build-identity header must be "
            f"{expected_identity_header}"
        )

definition_pattern = re.compile(r"^[A-Z][A-Z0-9_]*(?:=[A-Za-z0-9_]+)?$")
component_compile_definitions = selection.get(
    "component_compile_definitions", []
)
qualification_local_definition = (
    "AGON_EXTENDER_PORT008_NONRELEASE_QUALIFICATION"
)
translation_unit_local_definitions = {
    qualification_local_definition,
    "AGON_EXTENDER_SOURCE_IDENTITY",
    "AGON_EXTENDER_BUILD_ID",
    "AGON_EXTENDER_ARTIFACT_STATUS",
    "AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY",
}
for definition in component_compile_definitions:
    if not definition_pattern.fullmatch(definition):
        raise RuntimeError(
            f"{selection_path}: unsupported component definition {definition!r}"
        )
    definition_name = definition.partition("=")[0]
    if definition_name in translation_unit_local_definitions:
        raise RuntimeError(
            f"{selection_path}: {definition_name} must be defined only by "
            "its owning translation unit"
        )

# Hybrid Arduino/ESP-IDF builds intentionally ignore PlatformIO's source
# filter and use the application component's CMake source list. Render that
# ignored generated boundary from the same allowlist so the two build systems
# cannot disagree about which project translation units enter the diagnostic.
component_sources = []
for relative in project_translation_units:
    source = project_dir / relative
    if not source.is_file():
        raise FileNotFoundError(source)
    # The retained component is rooted at video/, while explicitly vendored
    # single-file libraries such as ESP32Time remain under vendor/. Preserve
    # that ownership and render a reviewed relative CMake path rather than
    # copying the source into the official VDP-shaped tree.
    component_sources.append(
        Path(os.path.relpath(source, project_dir / "video")).as_posix()
    )

embedded_text_files = []
for relative in selection.get("embedded_text_files", []):
    source = project_dir / relative
    if not source.is_file():
        raise FileNotFoundError(source)
    embedded_text_files.append(source.relative_to(project_dir / "video").as_posix())

cmake_path = project_dir / selection["generated_build_files"][0]
cmake_text = """# Generated by pio/select_sources.py for an allowlisted P4 target.
# Hybrid Arduino/ESP-IDF ignores PlatformIO build_src_filter; do not hand-edit.
idf_component_register(
  SRCS
"""
cmake_text += "".join(f'    "${{CMAKE_CURRENT_LIST_DIR}}/{path}"\n' for path in component_sources)
if embedded_text_files:
    # PlatformIO's board_build.embed_txtfiles hook generates assembly but does
    # not link it into this pinned Arduino/ESP-IDF hybrid build. Registering the
    # same authoritative files with the application component uses ESP-IDF's
    # native mechanism and gives the linker one unambiguous owner.
    cmake_text += "  EMBED_TXTFILES\n"
    cmake_text += "".join(
        f'    "${{CMAKE_CURRENT_LIST_DIR}}/{path}"\n'
        for path in embedded_text_files
    )
cmake_text += ")\n"
# ESP-IDF 5.5 defaults C++ application components to gnu++2b and the hybrid
# CMake path does not inherit PlatformIO's build_flags. Extender-owned code is
# normatively C++17 (ADR-0011), so pin the generated application component at
# its actual compiler boundary. Without this line the visible platformio.ini
# setting is silently ineffective.
cmake_text += 'target_compile_options(${COMPONENT_LIB} PRIVATE "-std=gnu++17")\n'
if component_compile_definitions:
    cmake_text += "target_compile_definitions(${COMPONENT_LIB} PRIVATE\n"
    cmake_text += "".join(
        f"  {definition}\n" for definition in component_compile_definitions
    )
    cmake_text += ")\n"
cmake_path.write_text(cmake_text, encoding="utf-8", newline="\n")

# Managed dependencies belong to a selected target, not every historical P4
# composition. JSON is valid YAML; exact versions and the resolved lock are
# captured by the identified build preparation script. Remove only our own
# generated manifest when switching back to a target without dependencies.
manifest_path = project_dir / "video/idf_component.yml"
marker = "# Generated by pio/select_sources.py; do not hand-edit.\n"
if manifest_path.exists() and not manifest_path.read_text().startswith(marker):
    raise RuntimeError(f"Refusing to replace a non-generated {manifest_path}")
dependencies = selection.get("managed_dependencies", {})
for name, version in dependencies.items():
    if not re.fullmatch(r"[a-z][a-z0-9_-]*/[a-z][a-z0-9_-]*", name) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise RuntimeError(f"{selection_path}: dependency must name an exact managed version")
if dependencies:
    manifest_path.write_text(marker + json.dumps({"dependencies": {
        name: {"version": "==" + version} for name, version in dependencies.items()
    }}, indent=2) + "\n")
elif manifest_path.exists():
    manifest_path.unlink()

# PlatformIO generates the three-line root entry point only when absent. A
# target with additional managed components needs its own tracked lock, or the
# IDF resolver rewrites the ordinary EDP lock and updates unrelated packages.
# Keep both CMake's variable and IDF's build property set: 5.5.5 reads each at
# a different stage of dependency preparation. Restore the ordinary entry point
# when selecting another target; never overwrite a hand-maintained root.
root_path = project_dir / "CMakeLists.txt"
ordinary_root = ('cmake_minimum_required(VERSION 3.16.0)\n'
                 'include($ENV{IDF_PATH}/tools/cmake/project.cmake)\n'
                 'project(vdp)\n')
if root_path.exists() and root_path.read_text() != ordinary_root and not root_path.read_text().startswith(marker):
    raise RuntimeError(f"Refusing to replace a non-generated {root_path}")
lock = selection.get("dependency_lock")
if lock:
    if lock != f"pio/{environment}-dependencies.lock" or not (project_dir / lock).is_file():
        raise RuntimeError(f"{selection_path}: missing target dependency lock")
    root_path.write_text(marker + ordinary_root.replace('project(vdp)\n',
        f'set(DEPENDENCIES_LOCK "${{CMAKE_CURRENT_LIST_DIR}}/{lock}")\n'
        'idf_build_set_property(DEPENDENCIES_LOCK "${DEPENDENCIES_LOCK}")\n'
        'project(vdp)\n'))
else:
    root_path.write_text(ordinary_root)

# Original depth controllers live in dispdrivers/. Keep exact file allowlisting;
# never discover or enable the rest of the classic-ESP32 driver family.
vendored_root = project_dir / "vendor/vdp-gl/src"
selected_names = []
for relative in selection["vendored_translation_units"]:
    source = project_dir / relative
    if source.resolve().parent not in (vendored_root.resolve(), (vendored_root / "dispdrivers").resolve()):
        raise RuntimeError(f"vendored source is outside the reviewed root: {source}")
    if not source.is_file():
        raise FileNotFoundError(source)
    selected_names.append(source.relative_to(vendored_root).as_posix())

env.BuildSources(  # type: ignore[name-defined]
    env.subst("$BUILD_DIR") + "/selected-vdp-gl",  # type: ignore[name-defined]
    str(vendored_root),
    src_filter=["-<*>", *(f"+<{name}>" for name in selected_names)],
)
