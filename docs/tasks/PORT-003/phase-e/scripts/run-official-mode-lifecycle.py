#!/usr/bin/env python3
"""Exercise exact pinned VDU mode functions against controlled host seams.

This runner deliberately extracts the two official function bodies into a
temporary harness. It does not copy them into production and does not let the
production implementation generate its independent fixture oracle.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import sha256_file, write_canonical  # noqa: E402

EXPECTED_VDP_COMMIT = "c7ac293d2aa81ddfa693390549bcd909069c8fc3"
FIXTURES = ROOT / "docs/tasks/PORT-003/phase-e/fixtures/modes-and-lifecycle.yaml"
PROVENANCE = ROOT / "docs/tasks/PORT-003/phase-e/evidence/mode-provenance.yaml"
DEFAULT_OUTPUT = ROOT / "docs/tasks/PORT-003/phase-e/evidence/official-mode-lifecycle-results.yaml"


def git_commit(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def extract_function_text(path: Path, name: str) -> tuple[str, int, int, str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        rf"(?:^|\n)[^\n;]*\b{re.escape(name)}\s*\([^;]*?\)\s*\{{",
        text,
    )
    if match is None:
        raise ValueError(f"{path}: function not found: {name}")
    start = match.start() + (1 if text[match.start():].startswith("\n") else 0)
    brace = text.find("{", start, match.end())
    depth = 0
    in_string = False
    escaped = False
    index = brace
    while index < len(text):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                snippet = text[start:end]
                return (
                    snippet,
                    text.count("\n", 0, start) + 1,
                    text.count("\n", 0, end - 1) + 1,
                    hashlib.sha256(snippet.encode()).hexdigest(),
                )
        index += 1
    raise ValueError(f"{path}: unterminated function: {name}")


def define_value(path: Path, name: str) -> int:
    text = path.read_text(encoding="utf-8")
    match = re.search(rf"^#define\s+{re.escape(name)}\s+(0x[0-9A-Fa-f]+|\d+)\b", text, re.MULTILINE)
    if match is None:
        raise ValueError(f"{path}: define not found: {name}")
    return int(match.group(1), 0)


HARNESS = r'''// Generated only in a temporary directory by PORT-003 Phase E.
#include <cstdarg>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>
#include <utility>
#include <vector>

constexpr std::uint16_t CALLBACK_VSYNC = @CALLBACK_VSYNC@;
constexpr std::uint16_t CALLBACK_MODE_CHANGE = @CALLBACK_MODE_CHANGE@;
constexpr std::uint16_t CALLBACK_SENDING_VDPP = @CALLBACK_SENDING_VDPP@;
constexpr std::uint8_t PACKET_MODE = @PACKET_MODE@;

std::vector<std::string> events;
std::vector<std::pair<std::uint8_t, int>> scriptedAttempts;
std::size_t attemptIndex = 0;
std::uint8_t finalMode = 0;
std::uint16_t finalWidth = 0;
std::uint16_t finalHeight = 0;
std::uint8_t finalDepth = 0;
bool finalDoubleBuffered = false;
std::vector<std::uint8_t> sentPacket;

std::uint16_t canvasW = 0;
std::uint16_t canvasH = 0;
std::uint8_t videoMode = 0;
std::uint8_t colourDepth = 0;
bool mouseVisible = false;
bool doubleBuffered = false;

struct TraceTeletextMode {
  bool value = false;
  TraceTeletextMode &operator=(bool next) {
    value = next;
    if (!next) events.emplace_back("teletext.disable");
    return *this;
  }
  operator bool() const { return value; }
};
TraceTeletextMode ttxtMode;

struct FakeController {};
std::unique_ptr<FakeController> _VGAController(new FakeController());

struct Context {
  std::uint8_t charWidth = 0;
  std::uint8_t charHeight = 0;
  void cls() { events.emplace_back("context.cls"); }
  std::uint8_t getNormalisedViewportCharWidth() const { return charWidth; }
  std::uint8_t getNormalisedViewportCharHeight() const { return charHeight; }
};

void debug_log(char const *, ...) {}
void waitPlotCompletion(bool waitForVSync) {
  if (!waitForVSync) std::abort();
  events.emplace_back("display.wait-vsync");
}
int changeMode(std::uint8_t mode) {
  if (attemptIndex >= scriptedAttempts.size() || scriptedAttempts[attemptIndex].first != mode) {
    std::cerr << "unexpected changeMode attempt " << unsigned(mode) << '\n';
    std::exit(90);
  }
  int result = scriptedAttempts[attemptIndex++].second;
  events.emplace_back("facade.change-mode:" + std::to_string(unsigned(mode)) + ":" + std::to_string(result));
  if (result == 0) {
    videoMode = mode;
    if (mode == 7) ttxtMode = true;
    if (mode == finalMode) {
      canvasW = finalWidth;
      canvasH = finalHeight;
      colourDepth = finalDepth;
      doubleBuffered = finalDoubleBuffered;
    }
  }
  return result;
}
bool isDoubleBuffered() { return doubleBuffered; }
void switchBuffer() { events.emplace_back("display.swap"); }
void showMouseCursor() { events.emplace_back("cursor.show"); }
bool resetMousePositioner(std::uint16_t width, std::uint16_t height, FakeController *controller) {
  if (controller == nullptr || width != canvasW || height != canvasH) std::abort();
  events.emplace_back("cursor-positioner.reset");
  return true;
}
std::uint8_t getVGAColourDepth() { return colourDepth; }

class VDUStreamProcessor {
 public:
  explicit VDUStreamProcessor(Context *value) : context(value) {}
  void vdu_mode(std::uint8_t mode);
  void sendModeInformation();
  void resetAllContexts() { events.emplace_back("contexts.reset-all"); }
  void updateMouseVars(void *) { events.emplace_back("mouse-variables.update"); }
  void bufferRemoveCallback(std::uint16_t id, std::uint16_t type) {
    if (id != 65535 || type != CALLBACK_VSYNC) std::abort();
    events.emplace_back("callbacks.remove-all-vsync");
  }
  void bufferCallCallbacks(std::uint16_t type) {
    if (type == CALLBACK_MODE_CHANGE) {
      events.emplace_back("callbacks.call-mode-change");
    } else if (type == (CALLBACK_SENDING_VDPP | PACKET_MODE)) {
      events.emplace_back("callbacks.call-sending-mode-packet");
    } else {
      std::cerr << "unexpected callback " << type << '\n';
      std::exit(91);
    }
  }
  void send_packet(std::uint8_t code, std::uint16_t length, std::uint8_t data[]) {
    if (code != PACKET_MODE) std::abort();
    sentPacket.assign(data, data + length);
    events.emplace_back("packet.send-mode");
  }
  Context *context;
};

@VDU_MODE@

@SEND_MODE_INFORMATION@

int parse(char const *text) { return std::stoi(text); }

int main(int argc, char **argv) {
  if (argc < 15) return 80;
  int arg = 1;
  std::uint8_t requested = static_cast<std::uint8_t>(parse(argv[arg++]));
  videoMode = static_cast<std::uint8_t>(parse(argv[arg++]));
  ttxtMode.value = parse(argv[arg++]) != 0;
  mouseVisible = parse(argv[arg++]) != 0;
  int count = parse(argv[arg++]);
  if (argc != 13 + count * 2) return 81;
  for (int index = 0; index < count; ++index) {
    std::uint8_t mode = static_cast<std::uint8_t>(parse(argv[arg++]));
    int result = parse(argv[arg++]);
    scriptedAttempts.emplace_back(mode, result);
  }
  finalMode = static_cast<std::uint8_t>(parse(argv[arg++]));
  finalDoubleBuffered = parse(argv[arg++]) != 0;
  finalWidth = static_cast<std::uint16_t>(parse(argv[arg++]));
  finalHeight = static_cast<std::uint16_t>(parse(argv[arg++]));
  finalDepth = static_cast<std::uint8_t>(parse(argv[arg++]));
  Context context;
  context.charWidth = static_cast<std::uint8_t>(parse(argv[arg++]));
  context.charHeight = static_cast<std::uint8_t>(parse(argv[arg++]));

  VDUStreamProcessor processor(&context);
  processor.vdu_mode(requested);
  if (attemptIndex != scriptedAttempts.size()) return 82;
  for (auto const &event : events) std::cout << "E\t" << event << '\n';
  std::cout << "P";
  for (auto value : sentPacket) std::cout << '\t' << unsigned(value);
  std::cout << '\n';
  std::cout << "S\t" << unsigned(videoMode) << '\t' << unsigned(static_cast<bool>(ttxtMode))
            << '\t' << canvasW << '\t' << canvasH << '\t'
            << unsigned(colourDepth) << '\t' << unsigned(doubleBuffered) << '\n';
  return 0;
}
'''


def harness_source(agon_vdp: Path) -> tuple[str, list[dict[str, Any]]]:
    vdu_path = agon_vdp / "video/vdu.h"
    sys_path = agon_vdp / "video/vdu_sys.h"
    agon_path = agon_vdp / "video/agon.h"
    vdu, vdu_start, vdu_end, vdu_hash = extract_function_text(
        vdu_path, "VDUStreamProcessor::vdu_mode"
    )
    packet, packet_start, packet_end, packet_hash = extract_function_text(
        sys_path, "VDUStreamProcessor::sendModeInformation"
    )
    source = HARNESS
    replacements = {
        "@CALLBACK_VSYNC@": str(define_value(agon_path, "CALLBACK_VSYNC")),
        "@CALLBACK_MODE_CHANGE@": str(define_value(agon_path, "CALLBACK_MODE_CHANGE")),
        "@CALLBACK_SENDING_VDPP@": str(define_value(agon_path, "CALLBACK_SENDING_VDPP")),
        "@PACKET_MODE@": str(define_value(agon_path, "PACKET_MODE")),
        "@VDU_MODE@": vdu,
        "@SEND_MODE_INFORMATION@": packet,
    }
    for marker, value in replacements.items():
        source = source.replace(marker, value)
    return source, [
        {
            "path": "video/vdu.h",
            "function": "VDUStreamProcessor::vdu_mode",
            "start_line": vdu_start,
            "end_line": vdu_end,
            "sha256": vdu_hash,
            "file_sha256": sha256_file(vdu_path),
        },
        {
            "path": "video/vdu_sys.h",
            "function": "VDUStreamProcessor::sendModeInformation",
            "start_line": packet_start,
            "end_line": packet_end,
            "sha256": packet_hash,
            "file_sha256": sha256_file(sys_path),
        },
    ]


def case_arguments(case: dict[str, Any]) -> list[str]:
    result = case["result"]
    values: list[int] = [
        case["requested_mode"],
        case["initial"]["video_mode"],
        int(case["initial"]["teletext"]),
        int(case["initial"]["mouse_visible"]),
        len(case["attempts"]),
    ]
    for attempt in case["attempts"]:
        values.extend([attempt["mode"], attempt["result"]])
    values.extend(
        [
            result["video_mode"],
            int(result["double_buffered"]),
            result["width"],
            result["height"],
            result["colours"],
            result["char_width"],
            result["char_height"],
        ]
    )
    return [str(value) for value in values]


def parse_output(output: str) -> tuple[list[str], list[int], dict[str, int]]:
    events: list[str] = []
    packet: list[int] | None = None
    state: dict[str, int] | None = None
    for line in output.splitlines():
        fields = line.split("\t")
        if fields[0] == "E" and len(fields) == 2:
            events.append(fields[1])
        elif fields[0] == "P":
            packet = [int(value) for value in fields[1:]]
        elif fields[0] == "S" and len(fields) == 7:
            state = {
                "video_mode": int(fields[1]),
                "teletext": int(fields[2]),
                "width": int(fields[3]),
                "height": int(fields[4]),
                "colours": int(fields[5]),
                "double_buffered": int(fields[6]),
            }
        else:
            raise ValueError(f"unexpected harness output: {line!r}")
    if packet is None or state is None:
        raise ValueError("incomplete harness output")
    return events, packet, state


def verify_provenance(regions: list[dict[str, Any]]) -> None:
    data = yaml.safe_load(PROVENANCE.read_text(encoding="utf-8"))
    by_function = {record["function"]: record for record in data["source_regions"]}
    for region in regions:
        expected = by_function.get(region["function"])
        if expected is None or any(
            expected[field] != region[field]
            for field in ("path", "start_line", "end_line", "sha256", "file_sha256")
        ):
            raise ValueError(f"provenance mismatch for {region['function']}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agon-vdp", type=Path, default=ROOT.parents[1] / "agon-vdp")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    agon_vdp = args.agon_vdp.resolve()
    if git_commit(agon_vdp) != EXPECTED_VDP_COMMIT:
        raise ValueError("agon-vdp root is not checked out at v2.16.0")

    fixtures = yaml.safe_load(FIXTURES.read_text(encoding="utf-8"))
    source, regions = harness_source(agon_vdp)
    verify_provenance(regions)
    compiler = subprocess.run(
        ["g++", "--version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]
    results = []
    with tempfile.TemporaryDirectory(prefix="port-003-phase-e-") as directory:
        temporary = Path(directory)
        source_path = temporary / "official_mode_lifecycle.cpp"
        binary_path = temporary / "official_mode_lifecycle"
        source_path.write_text(source, encoding="utf-8")
        subprocess.run(
            [
                "g++", "-std=c++17", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                str(source_path), "-o", str(binary_path),
            ],
            check=True,
        )
        environment = os.environ.copy()
        environment["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
        environment["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"
        for case in fixtures["lifecycle_cases"]:
            process = subprocess.run(
                [str(binary_path), *case_arguments(case)],
                check=True,
                capture_output=True,
                text=True,
                env=environment,
            )
            events, packet, state = parse_output(process.stdout)
            expected_state = case["result"]
            expected_teletext = int(expected_state["video_mode"] == 7)
            if events != case["expected_events"]:
                raise ValueError(
                    f"{case['id']}: event trace differs; "
                    f"expected={case['expected_events']!r}, observed={events!r}"
                )
            if packet != case["expected_mode_packet"]:
                raise ValueError(f"{case['id']}: mode packet differs")
            if state != {
                "video_mode": expected_state["video_mode"],
                "teletext": expected_teletext,
                "width": expected_state["width"],
                "height": expected_state["height"],
                "colours": expected_state["colours"],
                "double_buffered": int(expected_state["double_buffered"]),
            }:
                raise ValueError(f"{case['id']}: final state differs: {state}")
            results.append(
                {
                    "id": case["id"],
                    "status": "pass",
                    "events": events,
                    "mode_packet": packet,
                    "final_state": state,
                }
            )

    artifact = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_e_official_mode_lifecycle_results",
        "generated_by": "docs/tasks/PORT-003/phase-e/scripts/run-official-mode-lifecycle.py",
        "source_identity": {"identity": "v2.16.0", "commit": EXPECTED_VDP_COMMIT},
        "source_regions": regions,
        "fixture_sha256": sha256_file(FIXTURES),
        "compiler": compiler,
        "sanitizers": ["address", "undefined"],
        "leak_sanitizer": "disabled under managed tracing; harness owns no dynamic test allocation beyond standard-library process lifetime",
        "cases": results,
        "summary": {"passed": len(results), "failed": 0},
    }
    write_canonical(args.output.resolve(), artifact)
    print(f"official mode lifecycle: {len(results)} cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
