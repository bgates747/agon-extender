#!/usr/bin/env python3
"""Build INPUT-004's inert native USB baseline; never flash or contact a bench.

This bounded diagnostic deliberately omits Extender services and its HCD cache,
register and USBH logging derivatives. Keep only the FS/LS root-reset backport.
The installed SDK, HID package, board and relevant SDK settings remain pinned.
It is not an ordinary product profile or a production installation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
IDF = ROOT / "agents/build001/native-tools/esp-idf"
IDF_COMMIT = "b774170ff46c393eeb5e495ea37936038d3f4f4f"
HCD_SHA = "33fea9059ee546d1c773fc5e86ed0c294e600e645c4c14e0788ce879f596280b"
USBH_SHA = "0c6e108d5ce61e7325da6b5d33fff603a0644bd033426e52ba8506fc7067a061"
PREFIXES = ("CONFIG_ESP32P4_", "CONFIG_ESPTOOLPY_", "CONFIG_ESP_CONSOLE_",
            "CONFIG_FREERTOS_", "CONFIG_USB_HOST_", "CONFIG_CACHE_",
            "CONFIG_ESP_DEFAULT_CPU_FREQ", "CONFIG_SPIRAM",
            "CONFIG_ESP_MAIN_TASK_", "CONFIG_ESP_TASK_WDT_",
            "CONFIG_COMPILER_OPTIMIZATION")


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def inventory(directory):
    return [{"path": str(p.relative_to(directory)), "bytes": p.stat().st_size,
             "sha256": sha(p)} for p in sorted(directory.rglob("*")) if p.is_file()]


def settings(text):
    result = {}
    for line in text.splitlines():
        match = re.fullmatch(r"(CONFIG_[A-Z0-9_]+)=(.*)", line)
        if match:
            result[match[1]] = match[2]
        match = re.fullmatch(r"# (CONFIG_[A-Z0-9_]+) is not set", line)
        if match:
            result[match[1]] = "n"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--hid-source", required=True, type=Path)
    parser.add_argument("--tools-path", required=True, type=Path)
    parser.add_argument("--python-env", required=True, type=Path)
    args = parser.parse_args()
    require(re.fullmatch(r"input004-usb-minimal-r[0-9]{2,}-b[0-9-]{19}Z", args.build_id),
            "Explicit diagnostic build identity required")
    source_commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    require(not subprocess.check_output(["git", "-C", str(ROOT), "status", "--porcelain"]),
            "Commit all reviewed source before an identified build")
    require(subprocess.check_output(["git", "-C", str(IDF), "rev-parse", "HEAD"], text=True).strip() == IDF_COMMIT,
            "Pinned ESP-IDF revision differs")
    require(sha(IDF / "components/usb/hcd_dwc.c") == HCD_SHA and
            sha(IDF / "components/usb/usbh.c") == USBH_SHA, "Pinned USB source differs")
    baseline = args.baseline.resolve()
    baseline_manifest = json.loads((baseline / "manifest.json").read_text())
    require(baseline_manifest["source_commit"] == "632d35c0fe464f8bbde7d511d481f3355a176627",
            "Expected installed baseline differs")
    hid = args.hid_source.resolve()
    checksums = json.loads((hid / "CHECKSUMS.json").read_text())
    require(sha(hid / "hid_host.c") == "a2a19d0d1c0af2cdc81ef76c9e0c9df4d20094cee5dd84e034f7c040c4ebb143",
            "Unreviewed HID source")
    require("version: 1.2.1" in (hid / "idf_component.yml").read_text(), "HID version differs")
    for item in checksums["files"]:
        path = hid / item["path"]
        require(path.resolve().is_relative_to(hid) and path.stat().st_size == item["size"] and
                sha(path) == item["hash"], "HID package checksum mismatch: " + item["path"])
    hid_inventory = inventory(hid)
    package_digest = hashlib.sha256()
    for item in hid_inventory:
        if item["path"] not in {"CHECKSUMS.json", ".component_hash"}:
            package_digest.update(item["path"].encode())
            package_digest.update(item["sha256"].encode())
    require(package_digest.hexdigest() == "74b9c84cd2921a5e987f504c1713ca7819f7e8be80565e5253e9e9c7e07ab881",
            "HID package aggregate differs from the pinned vendor package")
    fixture = ROOT / "vdp/fixtures/usb_minimal"
    source_paths = [*sorted(p for p in fixture.rglob("*") if p.is_file()),
                    Path(__file__).resolve(), ROOT / "vdp/partitions.csv",
                    ROOT / "vdp/build/boards/p4-pc.json"]
    source_record = [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size,
                      "sha256": sha(p)} for p in source_paths]
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    project = output / "project"
    shutil.copytree(fixture, project)
    shutil.copytree(hid, project / "components/usb_host_hid")
    write_json(output / "source-inputs.json", {"source_commit": source_commit, "files": source_record})
    write_json(output / "hid-inputs.json", {"version": "1.2.1", "source": str(hid), "files": hid_inventory})
    with tarfile.open(output / "source.tar.gz", "w:gz", compresslevel=1) as archive:
        for path in source_paths:
            archive.add(path, arcname=str(path.relative_to(ROOT)), recursive=False)
    with tarfile.open(output / "hid-source.tar.gz", "w:gz", compresslevel=1) as archive:
        for item in hid_inventory:
            archive.add(hid / item["path"], arcname=item["path"], recursive=False)
    board = json.loads((ROOT / "vdp/build/boards/p4-pc.json").read_text())
    write_json(output / "board.json", board)
    original_settings = settings((baseline / "sdkconfig").read_text())
    selected = {key: value for key, value in original_settings.items() if key.startswith(PREFIXES)}
    # Flash coredumps could overwrite retained non-app bytes after a panic.
    # Disable them only in this isolated fixture; original product is untouched.
    selected.update({"CONFIG_IDF_TARGET": '"esp32p4"', "CONFIG_IDF_TARGET_ESP32P4": "y",
                     "CONFIG_PARTITION_TABLE_CUSTOM": "y",
                     "CONFIG_PARTITION_TABLE_CUSTOM_FILENAME": json.dumps(str(ROOT / "vdp/partitions.csv")),
                     "CONFIG_PARTITION_TABLE_OFFSET": "0x8000",
                     "CONFIG_ESP_COREDUMP_ENABLE_TO_NONE": "y",
                     "CONFIG_ESP_COREDUMP_ENABLE_TO_FLASH": "n",
                     "CONFIG_ESP_COREDUMP_ENABLE_TO_UART": "n",
                     "CONFIG_ESP_SYSTEM_PANIC_PRINT_HALT": "y",
                     "CONFIG_ESP_SYSTEM_PANIC_PRINT_REBOOT": "n",
                     "CONFIG_ESP_SYSTEM_PANIC_SILENT_REBOOT": "n"})
    sdkconfig = output / "sdkconfig"
    sdkconfig.write_text("".join(f"# {key} is not set\n" if value == "n" else f"{key}={value}\n"
                                for key, value in sorted(selected.items())))
    write_json(output / "sdkconfig-selection.json", {"baseline": str(baseline), "selected": selected,
               "limits": "Relevant baseline settings retained; absent product components and defaults are not a complete configuration match."})
    tools, python_env = args.tools_path.resolve(), args.python_env.resolve()
    env = os.environ.copy()
    env.update(IDF_PATH=str(IDF), IDF_TOOLS_PATH=str(tools), IDF_PYTHON_ENV_PATH=str(python_env),
               ESP_IDF_VERSION="5.5", IDF_COMPONENT_MANAGER="0")
    env["PATH"] = os.pathsep.join([str(python_env / "bin"),
        *[str(p) for p in tools.glob("tools/**/bin") if p.is_dir()], env["PATH"]])
    rom = list(tools.glob("tools/esp-rom-elfs/*"))
    if len(rom) == 1:
        env["ESP_ROM_ELF_DIR"] = str(rom[0])
    build = output / "build"
    command = [str(python_env / "bin/python"), str(IDF / "tools/idf.py"), "-C", str(project),
               "-B", str(build), "-DIDF_TARGET=esp32p4", f"-DSDKCONFIG={sdkconfig}",
               f"-DUSB_MINIMAL_BUILD_ID={args.build_id}", f"-DUSB_MINIMAL_SOURCE_COMMIT={source_commit}",
               f"-DUSB_MINIMAL_HUB_RESET_GPIO={board['usb']['hub_reset']}",
               f"-DUSB_MINIMAL_HUB_ASSERT_MS={board['usb']['reset_assert_ms']}",
               f"-DUSB_MINIMAL_HUB_RECOVERY_MS={board['usb']['reset_recovery_ms']}", "build"]
    write_json(output / "command.json", {"argv": command, "environment": {k: env[k] for k in
        ("IDF_PATH", "IDF_TOOLS_PATH", "IDF_PYTHON_ENV_PATH", "ESP_IDF_VERSION", "IDF_COMPONENT_MANAGER")}})
    start = time.monotonic_ns()
    with (output / "build.log").open("x") as log:
        result = subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT)
    write_json(output / "duration.json", {"start_monotonic_ns": start, "end_monotonic_ns": time.monotonic_ns(),
               "clock": "host monotonic nanoseconds; scheduling elapsed, not USB operation time", "returncode": result.returncode})
    require(result.returncode == 0, "Native build failed; inspect build.log")
    require(source_record == [{"path": str(p.relative_to(ROOT)), "bytes": p.stat().st_size,
            "sha256": sha(p)} for p in source_paths], "Source changed during build")
    require(inventory(hid) == hid_inventory, "HID input changed during build")
    actual = settings(sdkconfig.read_text())
    # SDK compatibility aliases need not survive Kconfig regeneration. All
    # installed USB, silicon, clock/cache, console and PSRAM settings must agree.
    aliases = {"CONFIG_COMPILER_OPTIMIZATION_LEVEL_DEBUG", "CONFIG_COMPILER_OPTIMIZATION_DEFAULT",
               "CONFIG_COMPILER_OPTIMIZATION_LEVEL_RELEASE", "CONFIG_ESP_CONSOLE_UART_NONE",
               "CONFIG_ESPTOOLPY_FLASHMODE_DOUT", "CONFIG_ESPTOOLPY_FLASHFREQ_120M"}
    exceptions = []
    # Kconfig removes these when their owning component/debug feature is absent.
    # Record the actual change rather than claiming complete configuration equality.
    # IDF5.5.5 freertos/Kconfig:362 depends on debug/coredump/GDB support;
    # usb/ext_port.c:22-26 falls back to exactly one reset attempt.
    no_coredump = not any("/espcoredump/" in c["file"] for c in
                         json.loads((build / "compile_commands.json").read_text()))
    for key, expected, reason in (
            ("CONFIG_FREERTOS_TASK_FUNCTION_WRAPPER", "y", "Task wrapper absent with removed debug/coredump support; deliberate diagnostic configuration difference"),
            ("CONFIG_USB_HOST_EXT_PORT_RESET_ATTEMPTS", "1", "Experimental menu absent; pinned ext_port.c fallback remains one attempt"),
            ("CONFIG_ESP_COREDUMP_ENABLE_TO_NONE", "y", "No espcoredump component is selected at all")):
        if key not in actual:
            require(selected.get(key) == expected and no_coredump, "Unexpected configuration exception: " + key)
            aliases.add(key)
            exceptions.append({"key": key, "baseline_or_requested": expected, "actual": "absent", "reason": reason})
    diffs = [{"key": k, "expected": v, "actual": actual.get(k)} for k, v in selected.items()
             if k not in aliases and k in actual and actual[k] != v]
    missing = [k for k in selected if k not in actual and k not in aliases and selected[k] != "n"]
    require(not diffs and not missing, "Selected SDK configuration differs: " + str((diffs, missing)))
    layout = json.loads((build / "flasher_args.json").read_text())
    old_layout = json.loads((baseline / "build/flasher_args.json").read_text())
    require(layout["app"]["offset"] == "0x20000", "Wrong fixture app offset")
    require((build / layout["partition-table"]["file"]).read_bytes() ==
            (baseline / "build" / old_layout["partition-table"]["file"]).read_bytes(), "Partition bytes differ")
    commands = json.loads((build / "compile_commands.json").read_text())
    hcd_actions = [c for c in commands if Path(c["file"]).name == "hcd_dwc.c"]
    usbh_actions = [c for c in commands if Path(c["file"]).name == "usbh.c"]
    hid_actions = [c for c in commands if Path(c["file"]).name == "hid_host.c"]
    require(len(hcd_actions) == len(usbh_actions) == len(hid_actions) == 1, "Unexpected USB translation units")
    require(Path(usbh_actions[0]["file"]).resolve() == (IDF / "components/usb/usbh.c").resolve(), "USBH is not pristine SDK")
    require(Path(hid_actions[0]["file"]).resolve() == project / "components/usb_host_hid/hid_host.c", "Wrong HID source")
    require(not any("/vdp/video/" in c["file"] or "arduino" in c["file"].lower() for c in commands), "Extender/Arduino source selected")
    derivative = Path(hcd_actions[0]["file"])
    upstream = (IDF / "components/usb/hcd_dwc.c").read_text()
    needle = "    usb_dwc_hal_port_toggle_reset(port->hal, true);"
    # The fixture recipe must use this exact, sole required backport. No cache,
    # logging, diagnostic snapshot or transfer-stage alteration is admitted.
    replacement = ("    if (port->hal->constant_config.hsphy_type != 0) {\n"
                   "        usb_dwc_ll_hcfg_set_fsls_supp_only(port->hal->dev);\n"
                   "    }\n" + needle)
    replacement = "    // Extender USB-only reproducer: FSLS root-reset backport, no other HCD changes.\n" + replacement
    require(upstream.count(needle) == 1 and derivative.read_text() == upstream.replace(needle, replacement),
            "HCD differs beyond the sole FSLS root-reset backport")
    require(sha(derivative) == "e26a6ecaac14fd67814b00722d8d1df39305006905fd9362c889f17cfbfd1625",
            "Unreviewed HCD derivative hash")
    app = build / layout["app"]["file"]
    elf = next(build.glob("*.elf"))
    require(args.build_id.encode() in app.read_bytes() and source_commit.encode() in app.read_bytes(), "Missing embedded identities")
    validation = {"passed": True, "source_commit": source_commit,
                  "selected_settings_match_with_documented_exceptions": True,
                  "configuration_exceptions": exceptions, "coredump_component_absent": no_coredump,
                  "partition_bytes_equal": True, "pristine_usbh": True, "pristine_hid": True,
                  "sole_fsls_hcd_backport": True, "hcd_sha256": sha(derivative),
                  "compile_actions": len(commands), "usb_compile_actions": hcd_actions + usbh_actions + hid_actions,
                  "image_bytes": app.stat().st_size, "image_sha256": sha(app),
                  "limits": "Compilation and source/config checks only; root separately reviews archive/ELF selection and physical outcomes."}
    write_json(output / "validation.json", validation)
    artifacts = [app, elf, build / "flasher_args.json", build / "compile_commands.json", sdkconfig,
                 derivative, output / "validation.json", output / "source.tar.gz", output / "hid-source.tar.gz"]
    write_json(output / "manifest.json", {"build_id": args.build_id, "source_commit": source_commit,
        "source_dirty": False, "idf_commit": IDF_COMMIT, "fixture": "input004-usb-minimal-r01",
        "baseline": str(baseline), "app_offset": 0x20000, "hid_version": "1.2.1", "artifacts": [
            {"path": str(p), "bytes": p.stat().st_size, "sha256": sha(p)} for p in artifacts]})
    print("Minimal USB native build PASS: " + str(output), flush=True)


if __name__ == "__main__":
    main()
