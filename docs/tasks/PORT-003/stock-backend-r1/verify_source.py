#!/usr/bin/env python3
"""Check that the R1 source selection preserves otherwise compilable stock code."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = "a773b19"
GL = "vdp/vendor/vdp-gl/"
CONTROLLERS = ["vga2", "vga4", "vga8", "vga16", "vga64", "vgapaletted", "vgabase"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def original(path):
    return subprocess.check_output(["git", "show", f"{BASE}:{path}"], cwd=ROOT)


def classic_selection(source):
    """Remove only R1 conditional directives, retaining the original branch.

    Other upstream preprocessor directives remain byte-for-byte input. This
    allows comparison without preprocessing away unused upstream method bodies.
    """
    source = re.sub(
        r"#if defined\(AGON_EXTENDER_STOCK_ROWS_PROOF\)\n"
        r"#define AGON_EXTENDER_VGA_ISR\(handler\) nullptr\n#else\n"
        r"#define AGON_EXTENDER_VGA_ISR\(handler\) handler\n#endif\n", "", source)
    output, stack = [], []
    for line in source.splitlines(keepends=True):
        directive = line.strip()
        if directive in ("#if defined(AGON_EXTENDER_STOCK_ROWS_PROOF)",
                         "#if !defined(AGON_EXTENDER_STOCK_ROWS_PROOF)"):
            stack.append((True, "!defined" in directive))
        elif re.match(r"#\s*(if|ifdef|ifndef)\b", directive):
            if all(value for _, value in stack):
                output.append(line)
            stack.append((False, True))
        elif directive == "#else" and stack and stack[-1][0]:
            stack[-1] = (True, not stack[-1][1])
        elif directive == "#endif" and stack:
            special, _ = stack.pop()
            if not special and all(value for _, value in stack):
                output.append(line)
        elif all(value for _, value in stack):
            output.append(line)
    assert not stack, "unterminated conditional"
    return "".join(output).replace("AGON_EXTENDER_VGA_ISR(ISRHandler)", "ISRHandler")


def tokens(source):
    # Keep strings/character literals intact; ignore comments and whitespace
    # only. Renaming/re-expressing any body or changing a literal fails.
    pattern = r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\w+|[^\s]'
    return [t for t in re.findall(pattern, source, re.S) if not t.startswith(("//", "/*"))]


def verify():
    records = []
    for stem in CONTROLLERS:
        for extension in ("cpp", "h"):
            path = f"{GL}src/dispdrivers/{stem}controller.{extension}"
            before, after = original(path), (ROOT / path).read_bytes()
            if extension == "h":
                assert before == after, path
            else:
                assert tokens(before.decode()) == tokens(classic_selection(after.decode())), path
            records.append({"path": path, "upstream_sha256": sha(before),
                            "selected_sha256": sha(after),
                            "check": "byte-identical" if extension == "h" else "original branch token-identical"})
    for name in ("canvas.cpp", "canvas.h", "displaycontroller.cpp", "displaycontroller.h",
                 "codepages.cpp", "fabfonts.cpp", "fabfonts.h", "fabutils.cpp", "fabutils.h"):
        path = f"{GL}src/{name}"
        before, after = original(path), (ROOT / path).read_bytes()
        assert before == after, path
        records.append({"path": path, "upstream_sha256": sha(before),
                        "selected_sha256": sha(after), "check": "byte-identical"})
    utility = json.loads((HERE / "utility-spans.json").read_text())
    source = original(GL + utility["path"]).decode().splitlines(keepends=True)
    selection = (ROOT / "vdp/video/extender/port/stock_render_utils.cpp").read_text()
    for span in utility["spans"]:
        body = "".join(source[span["first"] - 1:span["last"]])
        assert sha(body.encode()) == span["sha256"] and body in selection, span
    oracle = (HERE / "oracle.hpp").read_text()
    for item in json.loads((HERE / "oracle-spans.json").read_text()):
        source = original(GL + item["source"]).decode()
        match = re.search(r"static inline[^\n]* " + item["symbol"] + r"\([^\n]*\) \{.*?\n\}", source, re.S)
        assert match and sha(match[0].encode()) == item["sha256"] and match[0] in oracle, item
    # Production source selectors must continue to select their identified
    # existing build, not accidentally pick up the new utility TU as well.
    for path in (ROOT / "vdp/platformio.ini", ROOT / "vdp/pio/select_sources.py"):
        assert "stock_render_utils.cpp" not in path.read_text(), path
    return {"upstream": "ac2dd5986daf496c43ae8e7fe41836274aec54a0",
            "project_checkpoint": BASE, "files": records,
            "utility_groups": len(utility["spans"]), "oracle_accessors": 8}


if __name__ == "__main__":
    result = verify()
    print(json.dumps(result, indent=2))
