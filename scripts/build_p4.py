#!/usr/bin/env python3
"""Build one manifest-selected P4 profile with native ESP-IDF; never flash."""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
from urllib.parse import urlsplit

from p4_board import DEFAULT_BOARD, apply_sdk_overrides, load_board, write_board_inputs


ROOT = Path(__file__).resolve().parents[1]
VDP = ROOT / "vdp"
MANIFEST = VDP / "build/p4-profiles.json"
IDF = ROOT / "agents/build001/native-tools/esp-idf"
TOOLS = ROOT / "agents/build001/native-tools/espressif"
PYTHON_ENV = ROOT / "agents/build001/native-tools/python-env"
IDF_COMMIT = "b774170ff46c393eeb5e495ea37936038d3f4f4f"
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9.-]*")
SAFE_DEFINITION = re.compile(r"[A-Z][A-Z0-9_]*(?:=[A-Za-z0-9_.-]+)?")
RGB888_SOURCE = "video/extender/display/p4_rgb888_controller.cpp"
EXPERIMENTAL_RGB_ID = re.compile(r"rgb-001-r[0-9]{2,}-b([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2})Z")
HDMI_SOURCE = "video/extender/display/hdmi_output.cpp"
HDMI_COMPONENT = "components/esp_lcd_lt8912b"
HDMI_GEOMETRIES = {"auto": (848, 480), "1280x720": (1280, 720), "848x480": (848, 480), "512x384": (512, 384), "684x384": (684, 384)}
EXPERIMENTAL_HDMI_ID = re.compile(r"hdmi-001-r[0-9]{2}-b([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2})Z")
EXPERIMENTAL_BENCH_ID = re.compile(r"bench-009-r[0-9]{2,}-b([0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2}-[0-9]{2})Z")
SOURCE_SCOPE = ("vdp", "scripts/build_p4.py", "scripts/validate_p4_build.py",
                "scripts/p4_board.py")


def check_build_identity(build_id: str, source_dirty: bool,
                         allow_dirty_experimental: bool, profile: str,
                         board: str, display_output: str, render_benchmark_output: str | None = None, direct_rgb888: bool = False) -> None:
    """Keep release-style IDs clean while admitting this explicit experiment."""
    if allow_dirty_experimental:
        match = (EXPERIMENTAL_RGB_ID if direct_rgb888 else EXPERIMENTAL_BENCH_ID if render_benchmark_output else EXPERIMENTAL_HDMI_ID).fullmatch(build_id)
        if not match or (profile, board, display_output) != ("p4-console", "p4-pc", "hdmi"):
            raise SystemExit("dirty experimental builds require an HDMI-001 ID and p4-pc / p4-console / hdmi")
        try:
            datetime.strptime(match.group(1), "%Y-%m-%d-%H-%M-%S")
        except ValueError as error:
            raise SystemExit("experimental build ID has an invalid UTC timestamp") from error
    elif build_id != "UNVERSIONED-DO-NOT-DEPLOY" and source_dirty:
        raise SystemExit("identified builds require clean committed inputs")


def source_paths() -> list[Path]:
    """Include maintained untracked inputs and exclude ignored build caches."""
    names = subprocess.check_output([
        "git", "-C", str(ROOT), "ls-files", "--cached", "--others",
        "--exclude-standard", "-z", "--", *SOURCE_SCOPE,
    ]).split(b"\0")
    paths = sorted({ROOT / os.fsdecode(name) for name in names if name})
    if any(not path.is_file() or path.is_symlink() for path in paths):
        raise SystemExit("source closure contains a missing input or symlink")
    return paths


def source_input_record() -> dict:
    files = [{"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size,
              "sha256": sha(path)} for path in source_paths()]
    return {"schema_version": 1, "scope": list(SOURCE_SCOPE), "files": files}


def freeze_source_inputs(output: Path) -> dict:
    """Archive the exact hash-recorded dirty experimental source bytes."""
    files = []
    with tarfile.open(output / "source.tar.gz", "w:gz", compresslevel=1) as archive:
        for path in source_paths():
            data = path.read_bytes()
            relative = str(path.relative_to(ROOT))
            files.append({"path": relative, "bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest()})
            member = tarfile.TarInfo(relative)
            member.size, member.mode = len(data), path.stat().st_mode & 0o777
            archive.addfile(member, io.BytesIO(data))
    record = {"schema_version": 1, "scope": list(SOURCE_SCOPE), "files": files}
    (output / "source-inputs.json").write_text(json.dumps(record, indent=2) + "\n")
    if source_input_record() != record:
        raise SystemExit("source inputs changed while preparing experimental snapshot")
    return record


def select_display_profile(document: dict, name: str, board: str,
                           display_output: str, render_benchmark_output: str | None = None, direct_rgb888: bool = False, hdmi_timing: str = "1280x720", rolling_scanout: bool = False, ppa_scale_320: bool = False) -> dict:
    """Select an output adapter without creating a second rendering owner."""
    if display_output not in {"browser", "hdmi"}:
        raise SystemExit("unsupported display output")
    if display_output == "hdmi" and (name != "p4-console" or board != "p4-pc"):
        raise SystemExit("HDMI output requires p4-pc / p4-console")
    if hdmi_timing not in HDMI_GEOMETRIES or (hdmi_timing != "1280x720" and display_output != "hdmi"):
        raise SystemExit("custom HDMI timing requires HDMI output")
    profile = deepcopy(document["profiles"][name])
    if display_output == "hdmi":
        if HDMI_SOURCE in profile["sources"] or HDMI_SOURCE in profile["forbidden_sources"]:
            raise SystemExit("HDMI adapter must be selected at the output boundary")
        profile["sources"].append(HDMI_SOURCE)
        profile["definitions"].append("AGON_EXTENDER_HDMI=1")
        if hdmi_timing == "auto":
            profile["definitions"].append("AGON_EXTENDER_HDMI_AUTO=1")
        elif hdmi_timing == "848x480":
            profile["definitions"].append("AGON_EXTENDER_HDMI_848X480=1")
        elif hdmi_timing == "512x384":
            profile["definitions"].append("AGON_EXTENDER_HDMI_512X384=1")
        elif hdmi_timing == "684x384":
            profile["definitions"].append("AGON_EXTENDER_HDMI_684X384=1")
        profile.setdefault("requires", []).extend([
            "esp_lcd", "esp_driver_i2c", "esp_driver_gpio", "esp_hw_support",
            "esp_lcd_lt8912b",
        ])
    else:
        if HDMI_SOURCE in profile["sources"]:
            raise SystemExit("browser profile selects HDMI adapter")
        if HDMI_SOURCE not in profile["forbidden_sources"]:
            profile["forbidden_sources"].append(HDMI_SOURCE)
    if render_benchmark_output:
        if display_output != "hdmi" or render_benchmark_output not in {"normal", "hold", "off", "convert-off"}:
            raise SystemExit("render benchmark requires HDMI and normal/hold/off/convert-off selection")
        profile["definitions"].append("AGON_EXTENDER_RENDER_BENCHMARK=1")
        if render_benchmark_output == "convert-off":
            profile["definitions"].extend(["AGON_EXTENDER_BENCH_OFF=1", "AGON_EXTENDER_BENCH_CONVERT_OFF=1"])
        elif render_benchmark_output != "normal":
            profile["definitions"].append("AGON_EXTENDER_BENCH_" + render_benchmark_output.upper() + "=1")
    if direct_rgb888:
        if (name,board,display_output) != ("p4-console","p4-pc","hdmi") or not render_benchmark_output:
            raise SystemExit("RGB-001 storage requires experimental p4-pc HDMI benchmark selection")
        profile["sources"].append(RGB888_SOURCE)
        profile["definitions"].append("AGON_EXTENDER_DIRECT_RGB888=1")
    else:
        profile["forbidden_sources"].append(RGB888_SOURCE)
    if hdmi_timing == "auto" and not rolling_scanout:
        raise SystemExit("automatic HDMI requires the explicit rolling/direct normal composition")
    if rolling_scanout:
        if not direct_rgb888 or hdmi_timing not in {"auto", "848x480", "512x384", "684x384"} or render_benchmark_output!="normal":
            raise SystemExit("rolling scanout requires experimental 848x480/512x384/684x384 direct RGB888 normal output")
        profile["sources"].append("video/extender/display/rolling/scene.cpp")
        profile["definitions"].append("AGON_EXTENDER_ROLLING_SCANOUT=1")
    if ppa_scale_320:
        if hdmi_timing != "auto" or not rolling_scanout:
            raise SystemExit("PPA 320 scaling requires the automatic rolling HDMI composition")
        profile["sources"].append("video/extender/display/hdmi_ppa_scaler.cpp")
        profile["definitions"].append("AGON_EXTENDER_HDMI_PPA_320=1")
        profile.setdefault("requires", []).extend(["esp_driver_ppa", "esp_mm"])
    return profile


def display_input_record(display_output: str, render_benchmark_output: str | None = None, direct_rgb888: bool = False, hdmi_timing: str = "1280x720", rolling_scanout: bool = False, ppa_scale_320: bool = False) -> dict:
    """Retain the selected adapter and exact vendored bridge source closure."""
    record = {"schema_version": 1, "display_output": display_output,
              "configuration": None, "adapter": None, "bridge": None}
    width, height = HDMI_GEOMETRIES[hdmi_timing]
    if rolling_scanout:
        record["scanout"]={"kind":"rolling-dma2d", "blocks":height//32,"rows_per_block":32,"sram_slots":3,
                           "snapshot":"deep-copy-at-task-publication", "refill_abort_us":1600,
                           "malloc_always_internal_bytes":0,
                           "primitive_queue_storage":"psram-payload-internal-control",
                           "malloc_reserved_internal_bytes":32768,
                           "sd_worker_stack_memory":"psram",
                           "video_and_network_worker_stack_memory":"psram",
                           "sram_allocation_width":width,
                           "sram_allocation_bytes":width*32*3*3}
        if hdmi_timing=="auto":
            # Both carriers now roll; blocks describes the maximum allocation,
            # not the active count of a684-pixel-wide runtime mode. Retained
            # r07/r08 manifests kept the old r06 descriptive fields; preserve
            # those frozen records and document the correction alongside them.
            record["scanout"].update(kind="mode-selected-rolling",blocks=15,
                sram_allocation_width=848,sram_allocation_bytes=244224,
                runtime_layouts=[{"geometry":[684,384],"blocks":12},
                                 {"geometry":[848,480],"blocks":15}])
        record["scanout_sources"]=[artifact_record(p) for p in sorted((VDP/"video/extender/display/rolling").glob("*")) if p.is_file()]
    if direct_rgb888:
        record["render_storage"] = "rgb888-panel-direct"
        record["logical_stride_bytes"] = width * 3
        record["presentation_copy_bytes"] = 0
        record["renderer"] = artifact_record(checked_path(RGB888_SOURCE))
    if render_benchmark_output:
        record["render_benchmark_output"] = render_benchmark_output
    if display_output == "hdmi":
        component = checked_dir(HDMI_COMPONENT)
        required = {"CMakeLists.txt", "esp_lcd_lt8912b.c",
                    "include/esp_lcd_lt8912b.h", "license.txt"}
        files = sorted(path for path in component.rglob("*") if path.is_file())
        relative = {str(path.relative_to(component)) for path in files}
        if not required.issubset(relative) or any(path.is_symlink() for path in files):
            raise SystemExit("incomplete or symlinked HDMI bridge component")
        record["configuration"] = {
            "width": width, "height": height, "refresh_hz_nominal": 60,
            "pixel_format": "RGB888", "placement": "centered-unscaled-cropped",
        }
        if hdmi_timing != "1280x720":
            record["configuration"]["timing"] = {
                "kind": "custom", "clock_source": "PLL240", "clock_divider": 7,
                "lane_mbps": 480, "h_front_sync_back": [1104-width-224,112,112],
                "v_front_sync_back": [517-height-31,8,23], "h_total": 1104, "v_total": 517,
                "refresh_hz_calculated": 240000000 / (7 * 1104 * 517), "vic": 0,
            }
        if hdmi_timing == "512x384":
            record["configuration"]["aspect_hint"] = "4:3"
        elif hdmi_timing == "684x384":
            record["configuration"]["aspect_hint"] = "16:9"
        if hdmi_timing == "auto":
            record["configuration"].update(selection="smallest-proven-carrier-at-mode-change", carriers=[[684,384],[848,480]])
            record["logical_stride_bytes"]="selected-output-width * 3"
        record["adapter"] = artifact_record(checked_path(HDMI_SOURCE))
        record["bridge"] = {
            "component": "esp_lcd_lt8912b", "path": str(component),
            "files": [{"path": str(path.relative_to(component)),
                       "bytes": path.stat().st_size, "sha256": sha(path)}
                      for path in files],
        }
    if ppa_scale_320:
        record["render_storage"] = "rgb888-panel-direct-except-private-320x240"
        record["logical_stride_bytes"] = "logical RGB888 rows for320x240; panel stride otherwise"
        record["presentation_copy_bytes"] = "320x240:230400 snapshot +921600 scaled output; zero otherwise"
        record["configuration"]["placement"] = "320x240 bilinear2x centered; other modes unscaled/cropped"
        record["configuration"]["selection"] = "320x240 uses848x480; otherwise smallest-proven-carrier"
        record["ppa_scale_320"] = {"source": [320, 240], "destination": [640, 480],
                                   "carrier": [848, 480], "filter": "bilinear",
                                   "storage": "decorated snapshot; independent DMA-owned HDMI pair"}
    return record


def checked_tools(tools: Path, python_env: Path) -> Path:
    """Reject migrated/incomplete host tools before creating a build output."""
    compilers = list(tools.glob("tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-gcc"))
    if len(compilers) != 1:
        raise SystemExit("expected exactly one pinned RISC-V toolchain under --tools-path")
    for executable in (python_env / "bin/python", compilers[0]):
        try:
            subprocess.run([str(executable), "--version"], check=True,
                           capture_output=True, timeout=15)
        except (OSError, subprocess.SubprocessError) as error:
            raise SystemExit(
                f"host tool cannot execute: {executable}; select native host tools "
                "with --tools-path and --python-env"
            ) from error
    return compilers[0]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_record(path: Path) -> dict:
    return {"path": str(path), "bytes": path.stat().st_size,
            "sha256": sha(path)}


def assemble_factory_image(build: Path) -> Path:
    """Assemble the exact IDF flash segments into one offset-zero image."""
    flash = json.loads((build / "flasher_args.json").read_text())
    segments = []
    for raw_offset, relative in flash["flash_files"].items():
        path = build / relative
        if not path.is_file():
            raise SystemExit(f"missing factory segment: {relative}")
        segments.append((int(raw_offset, 0), path))
    segments.sort()
    end = 0
    image = bytearray()
    for offset, path in segments:
        data = path.read_bytes()
        if offset < end:
            raise SystemExit(f"overlapping factory segment: {path.name}")
        image.extend(b"\xff" * (offset - len(image)))
        image.extend(data)
        end = offset + len(data)
    target = build / "agon_extender.factory.bin"
    target.write_bytes(image)
    return target


def checked_path(relative: str) -> Path:
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SystemExit(f"unsafe manifest path: {relative}")
    result = (VDP / relative).resolve()
    if VDP.resolve() not in result.parents or not result.is_file():
        raise SystemExit(f"missing manifest input: {relative}")
    return result


def checked_dir(relative: str) -> Path:
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise SystemExit(f"unsafe manifest directory: {relative}")
    result = (VDP / relative).resolve()
    if VDP.resolve() not in result.parents or not result.is_dir():
        raise SystemExit(f"missing manifest directory: {relative}")
    return result


def cmake_quote(value: str) -> str:
    return '"' + value.replace("\\", "/").replace('"', '\\"') + '"'


def checked_definition_groups(profile: dict) -> dict[str, list[str]]:
    """Return disjoint required/diagnostic/rejected compile definitions."""
    policy = profile.get("definition_policy", {})
    unexpected = set(policy) - {"diagnostic", "rejected"}
    if unexpected:
        raise SystemExit(f"unsupported definition policy groups: {sorted(unexpected)}")
    groups = {
        "required": list(profile["definitions"]),
        "diagnostic": list(policy.get("diagnostic", [])),
        "rejected": list(policy.get("rejected", [])),
    }
    owners: dict[str, str] = {}
    for group, definitions in groups.items():
        if len(definitions) != len(set(definitions)):
            raise SystemExit(f"duplicate {group} definition")
        for definition in definitions:
            if not SAFE_DEFINITION.fullmatch(definition):
                raise SystemExit(f"unsafe {group} definition: {definition}")
            previous = owners.setdefault(definition, group)
            if previous != group:
                raise SystemExit(
                    f"definition classified as both {previous} and {group}: {definition}"
                )
    return groups


def checked_display_ownership(document: dict) -> None:
    """Reject ambiguous product display ownership or mixed display families."""
    families = document.get("display_families", {})
    if not families:
        raise SystemExit("display family declaration is missing")
    family_sources: dict[str, set[str]] = {}
    all_family_sources: set[str] = set()
    for name, family in families.items():
        sources = list(family.get("sources", []))
        if not sources or len(sources) != len(set(sources)):
            raise SystemExit(f"display family {name} has missing or duplicate sources")
        overlap = all_family_sources.intersection(sources)
        if overlap:
            raise SystemExit(f"display family sources overlap: {sorted(overlap)}")
        for source in sources:
            checked_path(source)
        family_sources[name] = set(sources)
        all_family_sources.update(sources)

    owners = [name for name, family in families.items()
              if family.get("product_owner") is True]
    if len(owners) != 1:
        raise SystemExit(f"expected one product display family owner, found {owners}")

    product_profiles = []
    for name, profile in document.get("profiles", {}).items():
        selected = set(profile["sources"])
        forbidden = set(profile["forbidden_sources"])
        family_name = profile.get("display_family")
        role = profile.get("product_display_role")
        if role not in {"product-owner", "bounded-qualification", "none"}:
            raise SystemExit(f"profile {name} has unsupported product display role: {role}")
        if family_name is None:
            if role != "none" or selected.intersection(all_family_sources):
                raise SystemExit(f"profile {name} has an undeclared display family")
            continue
        if family_name not in families:
            raise SystemExit(f"profile {name} selects unknown display family: {family_name}")
        missing = family_sources[family_name] - selected
        if missing:
            raise SystemExit(f"profile {name} omits display family sources: {sorted(missing)}")
        alternatives = all_family_sources - family_sources[family_name]
        mixed = selected.intersection(alternatives)
        if mixed:
            raise SystemExit(f"profile {name} mixes display families: {sorted(mixed)}")
        unguarded = alternatives - forbidden
        if unguarded:
            raise SystemExit(f"profile {name} does not forbid alternate display sources: {sorted(unguarded)}")
        if role == "product-owner":
            product_profiles.append(name)
            if family_name != owners[0]:
                raise SystemExit(f"profile {name} does not select the product display family")
        elif role == "bounded-qualification":
            family = families[family_name]
            if family.get("product_owner") or profile.get("status") != "nonrelease-diagnostic":
                raise SystemExit(f"profile {name} is not a bounded nonrelease display profile")
            if not family.get("bounded_owner") or len(family.get("retirement_conditions", [])) < 2:
                raise SystemExit(f"display family {family_name} lacks a retirement contract")
        else:
            raise SystemExit(f"profile {name} selects a display family with role none")
    if len(product_profiles) != 1:
        raise SystemExit(f"expected one product display profile, found {product_profiles}")


def render_component(profile: dict, common: dict, generated: Path,
                     asset_overrides: dict[str, Path]) -> None:
    sources = [checked_path(item) for item in profile["sources"]]
    if len(sources) != len(set(sources)):
        raise SystemExit("duplicate selected source")
    forbidden = {checked_path(item) for item in profile["forbidden_sources"]}
    if forbidden.intersection(sources):
        raise SystemExit("selected source is also forbidden")
    assets = [asset_overrides.get(item, checked_path(item))
              for item in profile["embedded_text"]]
    include_dirs = [checked_dir(item) for item in common["include_dirs"]
                    if item != "video"]
    include_dirs.append(generated)
    options = ["-idirafter", str(VDP / "video"),
               # PlatformIO's hybrid application compile omitted -Wall and
               # -Wextra. Native IDF adds them; keep warnings visible without
               # converting inherited upstream diagnostics into build breaks.
               "-Wno-error=reorder", "-Wno-error=switch",
               "-Wno-error=parentheses", "-Wno-error=maybe-uninitialized"]
    if profile.get("force_stock_task_context"):
        options += ["-include",
                    str(VDP / "video/extender/port/stock_task_context.hpp")]
    if profile.get("force_vdp_architecture"):
        options += ["-include",
                    str(VDP / "video/extender/compat/p4_vdp_gl_architecture.hpp")]
    definitions = ["AGON_EXTENDER_NATIVE_BUILD=1",
                   *checked_definition_groups(profile)["required"]]
    text = "idf_component_register(\n  SRCS\n"
    text += "".join(f"    {cmake_quote(str(path))}\n" for path in sources)
    text += "  INCLUDE_DIRS\n"
    text += "".join(f"    {cmake_quote(str(path))}\n" for path in include_dirs)
    requires = [*common.get("requires", []), *profile.get("requires", [])]
    if requires:
        text += "  REQUIRES\n"
        text += "".join(f"    {item}\n" for item in requires)
    if assets:
        text += "  EMBED_TXTFILES\n"
        text += "".join(f"    {cmake_quote(str(path))}\n" for path in assets)
    text += ")\n"
    text += "target_compile_options(${COMPONENT_LIB} PRIVATE\n"
    text += '  "$<$<COMPILE_LANGUAGE:CXX>:-std=gnu++17>"\n'
    text += "".join(f"  {cmake_quote(item)}\n" for item in options)
    text += ")\ntarget_compile_definitions(${COMPONENT_LIB} PRIVATE\n"
    text += "".join(f"  {item}\n" for item in definitions)
    text += ")\n"
    (generated / "CMakeLists.txt").write_text(text)
    dependencies = dict(common["dependencies"])
    dependencies.update(profile["dependencies"])
    manifest = "dependencies:\n  idf: \"==5.5.5\"\n"
    manifest += "".join(
        f"  {name}: \"=={version}\"\n" for name, version in dependencies.items()
    )
    (generated / "idf_component.yml").write_text(manifest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--board", default=DEFAULT_BOARD,
                        help="tracked board name (default: p4-devkit)")
    parser.add_argument("--usb-fsls-only", action="store_true",
                        help="experimental P4-PC-only full/low-speed USB host backport")
    parser.add_argument("--display-output", choices=("browser", "hdmi"), default="browser",
                        help="presentation sink; HDMI requires p4-pc / p4-console")
    parser.add_argument("--hdmi-timing", choices=tuple(HDMI_GEOMETRIES), default="1280x720",
                        help="fixed HDMI timing or auto carrier selection; experimental custom 60.069Hz")
    parser.add_argument("--ppa-scale-320", action="store_true")
    parser.add_argument("--rolling-scanout",action="store_true",help="SPRITE-001 experimental DMA2D strip output")
    parser.add_argument("--abort-on-alloc-failure", action="store_true",
                        help="Experimental diagnosis: stop at the first failed heap allocation")
    parser.add_argument("--direct-rgb888", action="store_true", help="RGB-001 experimental CPU pixel storage; never production")
    parser.add_argument("--render-benchmark-output", choices=("normal", "hold", "off", "convert-off"),
                        help="BENCH-009 diagnostic windows and output controls")
    parser.add_argument("--tools-path", type=Path, default=TOOLS,
                        help="host-native ESP-IDF tools directory")
    parser.add_argument("--python-env", type=Path, default=PYTHON_ENV,
                        help="host-native ESP-IDF Python environment")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--dependencies-lock", type=Path,
                        help="reuse a retained dependency lock for a controlled comparison")
    parser.add_argument("--build-id", default="UNVERSIONED-DO-NOT-DEPLOY")
    parser.add_argument("--allow-dirty-experimental", action="store_true",
                        help="freeze HDMI-001 experimental source; never qualify a release")
    parser.add_argument("--mos", type=Path)
    parser.add_argument("--mos-sha256")
    parser.add_argument("--flash-agent", type=Path)
    parser.add_argument("--reset-url",
                        help="embed a machine-local HTTP(S) reset endpoint")
    args = parser.parse_args()
    if not SAFE_NAME.fullmatch(args.build_id):
        parser.error("build ID contains unsupported characters")
    source_commit = subprocess.check_output(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True
    ).strip()
    source_dirty = bool(subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--porcelain"], text=True
    ).strip())
    check_build_identity(args.build_id, source_dirty, args.allow_dirty_experimental,
                         args.profile, args.board, args.display_output, args.render_benchmark_output, args.direct_rgb888)
    if args.direct_rgb888 and not args.allow_dirty_experimental:
        parser.error("direct RGB888 requires an explicitly frozen experimental build")
    output = args.output.resolve()
    if output.exists() or output.is_symlink():
        parser.error("output must be a fresh nonexisting path")
    document = json.loads(MANIFEST.read_text())
    checked_display_ownership(document)
    try:
        profile = select_display_profile(document, args.profile, args.board,
                                         args.display_output, args.render_benchmark_output, args.direct_rgb888, args.hdmi_timing, args.rolling_scanout, args.ppa_scale_320)
    except KeyError:
        parser.error("unknown profile")
    board, board_path = load_board(args.board, args.profile)
    if args.usb_fsls_only and (args.board != "p4-pc" or args.profile != "p4-console"):
        parser.error("--usb-fsls-only requires p4-pc / p4-console")
    if args.abort_on_alloc_failure and not (args.rolling_scanout and args.allow_dirty_experimental):
        parser.error("--abort-on-alloc-failure requires an explicit experimental rolling build")
    payload_arguments = (args.mos, args.mos_sha256, args.flash_agent)
    if profile.get("mos_recovery_payload"):
        if not all(payload_arguments):
            parser.error("recovery profile requires --mos, --mos-sha256 and --flash-agent")
    elif any(payload_arguments):
        parser.error("recovery payload arguments require a recovery profile")
    if args.reset_url and args.profile != "p4-console":
        parser.error("--reset-url is supported only by p4-console")
    if args.reset_url and urlsplit(args.reset_url).scheme not in ("http", "https"):
        parser.error("reset URL must use HTTP(S)")
    if subprocess.check_output(["git", "-C", str(IDF), "rev-parse", "HEAD"],
                               text=True).strip() != IDF_COMMIT:
        raise SystemExit("wrong ESP-IDF checkout identity")
    tools, python_env = args.tools_path.resolve(), args.python_env.resolve()
    compiler = checked_tools(tools, python_env)
    display_record = display_input_record(args.display_output, args.render_benchmark_output, args.direct_rgb888, args.hdmi_timing, args.rolling_scanout, args.ppa_scale_320)
    output.mkdir(parents=True)
    source_record = freeze_source_inputs(output) if args.allow_dirty_experimental else None
    (output / "display.json").write_text(json.dumps(display_record, indent=2) + "\n")
    project = output / "project"
    project.mkdir()
    shutil.copyfile(VDP / "native/CMakeLists.txt", project / "CMakeLists.txt")
    generated = project / "components/agon_vdp"
    generated.mkdir(parents=True)
    board_record = write_board_inputs(board, board_path, output, generated)
    asset_overrides: dict[str, Path] = {}
    if args.reset_url or args.display_output == "hdmi":
        relative = "video/extender/web/index.html"
        page = generated / "embedded/index.html"
        page.parent.mkdir()
        source = checked_path(relative).read_text()
        if args.reset_url:
            marker = 'name="agon-reset-url" content=""'
            if source.count(marker) != 1:
                raise SystemExit("reset URL marker missing or ambiguous")
            source = source.replace(marker, 'name="agon-reset-url" content="' +
                                    html.escape(args.reset_url, quote=True) + '"')
        if args.display_output == "hdmi":
            marker = 'name="agon-video-output" content="browser"'
            if source.count(marker) != 1:
                raise SystemExit("video output marker missing or ambiguous")
            source = source.replace(marker, 'name="agon-video-output" content="hdmi"')
            if args.hdmi_timing != "1280x720":
                marker = 'name="agon-hdmi-timing" content="1280x720 60 Hz"'
                if source.count(marker) != 1:
                    raise SystemExit("HDMI timing metadata missing or ambiguous")
                source = source.replace(marker, f'name="agon-hdmi-timing" content="{("automatic carrier" if args.hdmi_timing == "auto" else args.hdmi_timing)} 60.07 Hz"')
        page.write_text(source)
        asset_overrides[relative] = page
    render_component(profile, document["common"], generated, asset_overrides)
    payload_artifacts = []
    if profile.get("mos_recovery_payload"):
        payload_header = generated / "generated/mos_recovery_payload.hpp"
        subprocess.run([
            sys.executable, str(ROOT / "scripts/prepare_mos_recovery.py"),
            "--mos", str(args.mos.resolve()),
            "--mos-sha256", args.mos_sha256,
            "--flash-agent", str(args.flash_agent.resolve()),
            "--output", str(payload_header),
        ], check=True)
        payload_artifacts = [payload_header, payload_header.with_suffix(".json")]
    header = (
        "// Generated by scripts/build_p4.py; do not edit.\n#pragma once\n"
        f'#define AGON_EXTENDER_SOURCE_IDENTITY "{args.profile}-native"\n'
        f'#define AGON_EXTENDER_BUILD_ID "{args.build_id}"\n'
        '#define AGON_EXTENDER_ARTIFACT_STATUS "experimental"\n'
        f'#define AGON_EXTENDER_DISPLAY_OUTPUT "{args.display_output}"\n'
    )
    if args.profile == "p4-port008-nonrelease-qualification":
        header += '#define AGON_EXTENDER_QUALIFICATION_COMPOSITION_IDENTITY "PORT-008-D002"\n'
    (generated / "agon_extender_build_identity.hpp").write_text(header)
    source_config = checked_path(document["common"]["sdkconfig"])
    config = source_config.read_text().replace(
        'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="partitions.csv"',
        f'CONFIG_PARTITION_TABLE_CUSTOM_FILENAME="{VDP / "partitions.csv"}"',
    )
    config = apply_sdk_overrides(config, board["sdkconfig_overrides"])
    if args.rolling_scanout:
        # HDMI02-M02c: even the 1KiB preference exhausted internal RAM during
        # Nurples bitmap loading (84-byte pthread semaphore allocation fails).
        # Prefer PSRAM for all ordinary allocations; IDF still explicitly keeps
        # RTOS objects and peripheral DMA in internal memory. Preserve the32KiB
        # reserve and three strip slots. This changes placement, not stock VDU
        # semantics or the libstdc++ mutex policy. See HDMI-002 memory results.
        config = apply_sdk_overrides(config, {
            "CONFIG_SPIRAM_MALLOC_ALWAYSINTERNAL":"0",
            "CONFIG_SPIRAM_MALLOC_RESERVE_INTERNAL":"32768"})
    sdkconfig = output / "sdkconfig"
    # HDMI02-M02c: diagnose the allocation itself before an unchecked upstream
    # mutex constructor fails later in destruction. This is not a runtime fix.
    if args.abort_on_alloc_failure:
        config = apply_sdk_overrides(config, {"CONFIG_HEAP_ABORT_WHEN_ALLOCATION_FAILS": "y"})
    sdkconfig.write_text(config)
    lock = output / "dependencies.lock"
    if args.dependencies_lock:
        shutil.copyfile(args.dependencies_lock.resolve(), lock)
    build = output / "build"
    env = os.environ.copy()
    env.update({
        "IDF_PATH": str(IDF), "IDF_TOOLS_PATH": str(tools),
        "IDF_PYTHON_ENV_PATH": str(python_env),
        # Normally exported by ESP-IDF's activate.py. The wrapper constructs a
        # hermetic environment instead of sourcing a shell, and esp_hosted's
        # Kconfig expands this variable directly.
        "ESP_IDF_VERSION": "5.5",
    })
    rom_dirs = list(tools.glob("tools/esp-rom-elfs/*"))
    if len(rom_dirs) == 1:
        env["ESP_ROM_ELF_DIR"] = str(rom_dirs[0])
    tool_bins = [str(path) for path in tools.glob("tools/**/bin") if path.is_dir()]
    env["PATH"] = os.pathsep.join([str(python_env / "bin"), *tool_bins, env["PATH"]])
    command = [str(python_env / "bin/python"), str(IDF / "tools/idf.py"),
               "-C", str(project), "-B", str(build),
               f"-DAGON_COMPONENT_DIR={generated}",
               f"-DAGON_DEPENDENCIES_LOCK={lock}",
               f"-DAGON_VDP_ROOT={VDP}",
               f"-DAGON_ROLLING_SCANOUT={'ON' if args.rolling_scanout else 'OFF'}",
               f"-DAGON_HDMI_TIMING={args.hdmi_timing}",
               f"-DSDKCONFIG={sdkconfig}",
               f"-DAGON_DSP_LIFETIME_FIX={'ON' if profile.get('dsp_lifetime_fix') else 'OFF'}",
               f"-DAGON_USB_FSLS_ONLY={'ON' if args.usb_fsls_only else 'OFF'}",
               *([f"-DAGON_HDMI_COMPONENT_DIR={checked_dir(HDMI_COMPONENT)}"]
                 if args.display_output == "hdmi" else []),
               "build"]
    with (output / "build.log").open("w") as log:
        completed = subprocess.run(command, env=env, stdout=log,
                                   stderr=subprocess.STDOUT)
    if completed.returncode:
        raise SystemExit(f"native build failed; inspect {output / 'build.log'}")
    if source_record is not None and source_input_record() != source_record:
        raise SystemExit("source inputs changed during experimental build; candidate is not validated")
    factory = assemble_factory_image(build)
    validation = [sys.executable, str(ROOT / "scripts/validate_p4_build.py"),
                  "--profile", args.profile, "--board", args.board,
                  "--display-output", args.display_output, "--hdmi-timing", args.hdmi_timing,
        *(["--render-benchmark-output", args.render_benchmark_output] if args.render_benchmark_output else []), "--output", str(output)]
    if args.ppa_scale_320:
        validation.append("--ppa-scale-320")
    if args.rolling_scanout:
        validation.append("--rolling-scanout")
    if args.abort_on_alloc_failure:
        validation.append("--abort-on-alloc-failure")
    if args.direct_rgb888:
        validation.append("--direct-rgb888")
    if args.usb_fsls_only:
        validation.append("--usb-fsls-only")
    subprocess.run(validation, check=True)
    size_tool = compiler.with_name("riscv32-esp-elf-size")
    elf = build / "agon_extender.elf"
    size_result = subprocess.run([str(size_tool), "-A", str(elf)],
                                 check=True, text=True, capture_output=True)
    (output / "size-sections.txt").write_text(size_result.stdout)
    artifact_paths = [
        elf, build / "agon_extender.bin", factory, build / "agon_extender.map",
        build / "bootloader/bootloader.bin",
        build / "partition_table/partition-table.bin",
        build / "ota_data_initial.bin", build / "flasher_args.json",
        build / "compile_commands.json", output / "validation.json",
        output / "size-sections.txt",
        output / "board.json", generated / "agon_extender_board_config.hpp",
        output / "display.json", generated / "agon_extender_build_identity.hpp",
        *payload_artifacts,
    ]
    if args.rolling_scanout:
        artifact_paths.append(build/"dsi-strip/esp_lcd_panel_dpi.c")
    if args.usb_fsls_only:
        artifact_paths.extend([VDP / "native/usb_fsls_only.cmake",
                               build / "agon-extender-usb/hcd_dwc.c"])
    if source_record is not None:
        artifact_paths.extend([output / "source.tar.gz", output / "source-inputs.json"])
    record = {
        "schema_version": 1, "profile": args.profile, "lcd": False,
        "board": args.board, "board_identity": board["identity"],
        "board_profile_sha256": board_record["profile_sha256"],
        "board_header_sha256": board_record["header_sha256"],
        "compiler": artifact_record(compiler),
        "display_family": profile["display_family"],
        "product_display_role": profile["product_display_role"],
        "build_id": args.build_id, "manifest_sha256": sha(MANIFEST),
        "idf_commit": IDF_COMMIT, "sdkconfig_sha256": sha(sdkconfig),
        "dependencies_lock_sha256": sha(lock),
        "source_commit": source_commit,
        "source_dirty": source_dirty,
        "artifact_status": "experimental",
        "allow_dirty_experimental": args.allow_dirty_experimental,
        "source_snapshot_verified": source_record is not None,
        "reset_url_configured": bool(args.reset_url),
        "usb_fsls_only": args.usb_fsls_only,
        "abort_on_alloc_failure": args.abort_on_alloc_failure,
        "display_output": args.display_output,
        "display_inputs": display_record,
        "reset_url_sha256": (hashlib.sha256(args.reset_url.encode()).hexdigest()
                             if args.reset_url else None),
        "artifacts": [artifact_record(path) for path in artifact_paths],
    }
    if source_record is not None and source_input_record() != source_record:
        raise SystemExit("source inputs changed during experimental validation; candidate is not validated")
    (output / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    print(f"native P4 build PASS: {output}")


if __name__ == "__main__":
    main()
