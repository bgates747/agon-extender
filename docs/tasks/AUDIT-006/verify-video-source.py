#!/usr/bin/env python3
"""Read-only source binding for the video audit; does not build or touch devices."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
VDP_COMMIT = "c7ac293d2aa81ddfa693390549bcd909069c8fc3"
GL_COMMIT = "ac2dd5986daf496c43ae8e7fe41836274aec54a0"
EDP_COMMIT = "047ffe8"


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock-vdp", type=Path, required=True)
    parser.add_argument("--vdp-gl-repo", type=Path, required=True)
    args = parser.parse_args()
    assert git(args.stock_vdp, "rev-parse", "HEAD").decode().strip() == VDP_COMMIT
    assert git(args.stock_vdp, "rev-parse", "v2.16.0^{commit}").decode().strip() == VDP_COMMIT
    assert not git(args.stock_vdp, "status", "--porcelain")

    selection_path = "vdp/pio/p4-console-source-selection.json"
    selection_bytes = (ROOT / selection_path).read_bytes()
    selection = json.loads(selection_bytes)
    selected = set(selection["project_translation_units"] +
                   selection["vendored_translation_units"] +
                   selection["embedded_text_files"] +
                   selection["header_defined_official_implementation"])
    selected.update(str(p.relative_to(ROOT / "vdp"))
                    for p in (ROOT / "vdp/video/extender/display").glob("*.*"))
    selected.update(["video/extender/boot/p4_browser_vdp.cpp",
                     "video/extender/compat/p4_vdp_gl.hpp", "pio/select_sources.py"])
    hashes = {}
    for name in sorted(selected):
        path = "vdp/" + name
        data = (ROOT / path).read_bytes()
        assert data == git(ROOT, "show", f"{EDP_COMMIT}:{path}"), path
        hashes[path] = sha(data)
    assert selection_bytes == git(ROOT, "show", f"{EDP_COMMIT}:{selection_path}")

    official = []
    for path in sorted((args.stock_vdp / "video").rglob("*")):
        if path.suffix not in {".h", ".cpp", ".ino"}:
            continue
        name = str(path.relative_to(args.stock_vdp))
        local = ROOT / "vdp" / name
        data = path.read_bytes()
        assert data == git(args.stock_vdp, "show", f"{VDP_COMMIT}:{name}")
        official.append({"file": name, "stock_sha256": sha(data),
                         "edp_sha256": sha(local.read_bytes()) if local.exists() else None,
                         "byte_identical": local.exists() and data == local.read_bytes()})

    names = ["canvas.cpp", "canvas.h", "codepages.cpp", "displaycontroller.cpp",
             "displaycontroller.h", "fabutils.cpp", "fabutils.h", "fabglconf.h"]
    names += [f"dispdrivers/{stem}.{ext}" for stem in
              ["vgabasecontroller", "vgapalettedcontroller", "vga2controller",
               "vga4controller", "vga8controller", "vga16controller", "vga64controller"]
              for ext in ["cpp", "h"]]
    vendor = []
    for name in names:
        path = "src/" + name
        original = git(args.vdp_gl_repo, "show", f"{GL_COMMIT}:{path}")
        local = (ROOT / "vdp/vendor/vdp-gl" / path).read_bytes()
        vendor.append({"file": path, "stock_sha256": sha(original),
                       "edp_sha256": sha(local), "byte_identical": local == original})

    cmake_path = ROOT / "vdp/video/CMakeLists.txt"
    cmake = cmake_path.read_text()
    cmake_units = re.findall(r'"\$\{CMAKE_CURRENT_LIST_DIR\}/([^"\n]+\.cpp)"', cmake)
    actual = {(cmake_path.parent / p).resolve() for p in cmake_units}
    expected = {(ROOT / "vdp" / p).resolve() for p in selection["project_translation_units"]}
    assert actual == expected, "Generated application CMake list differs from selection"
    print(json.dumps({
        "edp_commit": git(ROOT, "rev-parse", EDP_COMMIT).decode().strip(),
        "official_vdp_commit": VDP_COMMIT, "vdp_gl_commit": GL_COMMIT,
        "source_selection_sha256": sha(selection_bytes),
        "selected_source_files_unchanged_since_checkpoint": True,
        "generated_application_cmake_matches_selection": True,
        "qualification": "Source correspondence only; excluded concrete controllers are not linked. No build or runtime test.",
        "selected_source_sha256": hashes, "official_video_files": official,
        "vendor_comparison": vendor,
    }, indent=2))


if __name__ == "__main__":
    main()
