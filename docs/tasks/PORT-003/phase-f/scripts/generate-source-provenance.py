#!/usr/bin/env python3
"""Generate the bounded PORT-003 Phase F source/provenance inventory.

This deliberately inventories only the accepted Phase F entry points. It is
not another whole-tree source graph. External checkouts and installed framework
packages are inputs; generated records contain repository-relative identities,
versions, hashes, and roles but never machine-local absolute paths.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml


PROJECT_SOURCES = {
    "official-port": [
        "vdp/video/video.ino",
        "vdp/video/agon.h",
        "vdp/video/vdu_stream_processor.h",
        "vdp/video/vdu.h",
        "vdp/video/vdu_sys.h",
        "vdp/video/vdu_context.h",
        "vdp/video/vdu_fonts.h",
        "vdp/video/vdu_sprites.h",
        "vdp/video/vdu_buffered.h",
        "vdp/video/context.h",
        "vdp/video/buffers.h",
        "vdp/video/agon_screen.h",
        "vdp/video/agon_ttxt.h",
        "vdp/video/vdu_layers.h",
        "vdp/video/vdp_variables.h",
        "vdp/video/agon_fonts.h",
        "vdp/video/sprites.h",
        "vdp/video/context/cursor.h",
        "vdp/video/context/fonts.h",
        "vdp/video/context/graphics.h",
        "vdp/video/context/viewport.h",
    ],
    "p4-display": [
        "vdp/video/extender/display/logical_frame_service.hpp",
        "vdp/video/extender/display/logical_frame_service.cpp",
        "vdp/video/extender/display/p4_frame_service.hpp",
        "vdp/video/extender/display/p4_frame_service.cpp",
        "vdp/video/extender/display/p4_display_controller.hpp",
        "vdp/video/extender/display/p4_display_controller.cpp",
        "vdp/video/extender/display/presentation_compositor.hpp",
        "vdp/video/extender/display/presentation_compositor.cpp",
        "vdp/video/extender/display/screen_facade_adapter.hpp",
        "vdp/video/extender/display/screen_facade_adapter.cpp",
        "vdp/video/extender/display/screen_facade_p4_binding.cpp",
        "vdp/video/extender/display/plane_storage.hpp",
        "vdp/video/extender/display/plane_storage.cpp",
        "vdp/video/extender/display/palette_state.hpp",
        "vdp/video/extender/display/palette_state.cpp",
        "vdp/video/extender/display/native_pixel_codec.hpp",
        "vdp/video/extender/display/native_pixel_codec.cpp",
        "vdp/video/extender/display/cursor_position_adapter.hpp",
        "vdp/video/extender/display/cursor_position_adapter.cpp",
        "vdp/video/extender/display/presentation_snapshot_pool.hpp",
        "vdp/video/extender/display/presentation_snapshot_pool.cpp",
    ],
    "p4-boot-and-bindings": [
        "vdp/video/extender/boot/p4_browser_vdp.cpp",
        "vdp/video/extender/compat/p4_vdp_gl.hpp",
        "vdp/video/extender/audio/unavailable_audio_adapter.hpp",
        "vdp/video/extender/input/unavailable_input_adapter.hpp",
        "vdp/video/extender/maintenance/unavailable_maintenance_adapter.hpp",
        "vdp/video/extender/transport/disconnected_stream.hpp",
        "vdp/video/extender/transport/disconnected_stream.cpp",
        "vdp/video/extender/port/fabutils_port.cpp",
    ],
    "browser-video": [
        "vdp/video/extender/web/browser_video_provider.hpp",
        "vdp/video/extender/web/browser_video_provider.cpp",
        "vdp/video/extender/web/embedded_assets.hpp",
        "vdp/video/extender/web/embedded_assets.cpp",
        "vdp/video/extender/web/index.html",
        "vdp/video/extender/web/style.css",
        "vdp/video/extender/web/app.js",
        "vdp/video/extender/web/frame_protocol.js",
        "vdp/video/extender/web/webgl2_presenter.js",
    ],
    "wired-network": [
        "vdp/video/extender/network/opaque_message.hpp",
        "vdp/video/extender/network/opaque_message.cpp",
        "vdp/video/extender/network/browser_video_service_core.hpp",
        "vdp/video/extender/network/browser_video_service_core.cpp",
        "vdp/video/extender/network/wired_network_service.hpp",
        "vdp/video/extender/network/wired_network_service.cpp",
    ],
    "build-boundary": [
        "vdp/platformio.ini",
        "vdp/sdkconfig.defaults",
        "vdp/pio/select_sources.py",
        "vdp/pio/p4-browser-vdp-source-selection.json",
        "vdp/pio/p4-browser-vdp-identity.json",
    ],
}

DOC_SOURCES = [
    "docs/vdp/VDU-Commands.md",
    "docs/vdp/Screen-Modes.md",
    "docs/vdp/System-Commands.md",
]

LEGACY_SOURCES = {
    "legacy-browser": [
        "web/presentation/README.md",
        "web/presentation/protocol.md",
        "web/presentation/index.html",
        "web/presentation/style.css",
        "web/presentation/app.js",
        "web/presentation/frame_protocol.js",
        "web/presentation/webgl2_presenter.js",
    ],
    "legacy-firmware-proof": [
        "vdp/common/video_presentation_contract.h",
        "vdp/common/video_frame_protocol.h",
        "src/modules/vdp/vdp_web.c",
        "src/modules/vdp/vdp_web.h",
        "sdkconfig.defaults",
    ],
}

IDF_SOURCES = {
    "idf-ethernet": [
        "components/esp_eth/include/esp_eth.h",
        "components/esp_netif/include/esp_netif.h",
        "components/esp_netif/include/esp_netif_defaults.h",
        "examples/ethernet/basic/main/ethernet_example_main.c",
        "examples/ethernet/basic/components/ethernet_init/ethernet_init.c",
        "examples/ethernet/basic/components/ethernet_init/ethernet_init.h",
    ],
    "idf-http-websocket": [
        "components/esp_http_server/include/esp_http_server.h",
        "components/esp_http_server/src/httpd_ws.c",
        "examples/protocols/http_server/ws_echo_server/main/ws_echo_server.c",
    ],
}

ARDUINO_SOURCES = {
    "arduino-stream": [
        "cores/esp32/Stream.h",
        "cores/esp32/Print.h",
    ],
    "arduino-ethernet": [
        "libraries/Ethernet/src/ETH.h",
        "libraries/Ethernet/src/ETH.cpp",
        "libraries/Network/src/Network.h",
        "libraries/Network/src/NetworkEvents.h",
    ],
}

EMOS_SOURCES = {
    "emos-mode-adapter": [
        "docs/emos-v1-contract.md",
        "research/initial-implementation-handoff.md",
        "src/emos.c",
        "projects/emos/emos_module.py",
    ]
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args])


def git_commit(root: Path, ref: str = "HEAD") -> str:
    return git(root, "rev-parse", f"{ref}^{{commit}}").decode().strip()


def project_source_ref(root: Path, commit: str) -> tuple[str, str]:
    """Describe scoped worktree provenance without mislabeling dirty bytes.

    Item 14 runs before the candidate commit by design. Only the bounded files
    inventoried here affect this state; generated evidence elsewhere must not
    make an otherwise committed source closure appear dirty.
    """

    paths = sorted({path for group in PROJECT_SOURCES.values() for path in group})
    status = git(root, "status", "--porcelain=v1", "--", *paths).decode().strip()
    if status:
        return "working-tree", "modified"
    return commit, "committed"


def package_version(root: Path) -> str:
    metadata = json.loads((root / ".piopm").read_text(encoding="utf-8"))
    return str(metadata["version"])


def file_record(
    *, group: str, repository: str, ref: str, path: str, data: bytes, role: str
) -> dict[str, Any]:
    return {
        "id": f"{repository}:{path}",
        "group": group,
        "repository": repository,
        "ref": ref,
        "path": path,
        "role": role,
        "bytes": len(data),
        "sha256": sha256(data),
    }


def add_files(
    records: list[dict[str, Any]],
    *,
    root: Path,
    repository: str,
    ref: str,
    groups: dict[str, list[str]],
    role: str,
) -> None:
    for group, paths in groups.items():
        for path in paths:
            data = (root / path).read_bytes()
            records.append(
                file_record(
                    group=group,
                    repository=repository,
                    ref=ref,
                    path=path,
                    data=data,
                    role=role,
                )
            )


def render_markdown(document: dict[str, Any]) -> str:
    lines = [
        "# PORT-003 Phase F bounded source provenance",
        "",
        "Generated by `scripts/generate-source-provenance.py`; do not edit.",
        "This is a Phase F entry-point inventory, not a whole-tree graph.",
        "",
        "## Authorities",
        "",
    ]
    for authority in document["authorities"]:
        lines.append(
            f"- `{authority['repository']}` `{authority['ref']}` — "
            f"{authority['purpose']}"
        )
    lines.extend(["", "## Files", "", "| Group | Repository | Path | Role | SHA-256 |", "|---|---|---|---|---|"])
    for record in document["records"]:
        lines.append(
            f"| {record['group']} | `{record['repository']}` | "
            f"`{record['path']}` | {record['role']} | `{record['sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary conclusions",
            "",
            "1. Official VDP parser and boot code remains the behavior authority; Phase F adds no command vocabulary.",
            "2. Current P4 display code publishes metadata only and exposes only a quiescent borrowed-state compositor; immutable pixel leases are genuinely new Phase F work.",
            "3. Legacy `EVF1` and WebGL code is bounded reuse evidence. Its fixed 320-by-240 server and one-frame request behavior are not current authority.",
            "4. ESP-IDF/Arduino framework files establish maintained Ethernet, DHCP, HTTP/WebSocket, and `Stream` seams; example initialization remains evidence rather than product source.",
            "5. EMOS already owns mode and route state, but the physical forward adapter is absent and remains PORT-008 work.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--agon-docs-root", type=Path, required=True)
    parser.add_argument("--legacy-root", type=Path, required=True)
    parser.add_argument("--emos-root", type=Path, required=True)
    parser.add_argument("--idf-root", type=Path, required=True)
    parser.add_argument("--arduino-root", type=Path, required=True)
    parser.add_argument("--output-yaml", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()

    project_base_commit = git_commit(args.project_root)
    project_ref, project_state = project_source_ref(args.project_root, project_base_commit)
    docs_ref = git_commit(args.agon_docs_root)
    legacy_ref = git_commit(args.legacy_root, "f33b9dd")
    emos_ref = git_commit(args.emos_root)
    idf_ref = package_version(args.idf_root)
    arduino_ref = package_version(args.arduino_root)

    records: list[dict[str, Any]] = []
    add_files(
        records,
        root=args.project_root,
        repository="agon-extender",
        ref=project_ref,
        groups=PROJECT_SOURCES,
        role="current implementation and build boundary",
    )
    add_files(
        records,
        root=args.agon_docs_root,
        repository="agon-docs",
        ref=docs_ref,
        groups={"official-docs": DOC_SOURCES},
        role="official VDP behavior authority",
    )
    for group, paths in LEGACY_SOURCES.items():
        for path in paths:
            data = git(args.legacy_root, "show", f"{legacy_ref}:{path}")
            records.append(
                file_record(
                    group=group,
                    repository="agon-extender-legacy",
                    ref=legacy_ref,
                    path=path,
                    data=data,
                    role="bounded legacy reuse evidence",
                )
            )
    add_files(
        records,
        root=args.idf_root,
        repository="esp-idf",
        ref=idf_ref,
        groups=IDF_SOURCES,
        role="pinned maintained framework authority",
    )
    add_files(
        records,
        root=args.arduino_root,
        repository="arduino-esp32",
        ref=arduino_ref,
        groups=ARDUINO_SOURCES,
        role="pinned Arduino integration authority",
    )
    add_files(
        records,
        root=args.emos_root,
        repository="agon-emos",
        ref=emos_ref,
        groups=EMOS_SOURCES,
        role="current EMOS mode and adapter boundary",
    )
    records.sort(key=lambda item: (item["group"], item["repository"], item["path"]))
    ids = [record["id"] for record in records]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate provenance record id")

    document = {
        "schema": 1,
        "task": "PORT-003",
        "phase": "F",
        "scope": "bounded parser, display, browser, network, and EMOS entry points",
        "authorities": [
            {
                "repository": "agon-extender",
                "ref": project_ref,
                "base_commit": project_base_commit,
                "state": project_state,
                "purpose": "current bounded Phase F source closure",
            },
            {"repository": "agon-docs", "ref": docs_ref, "purpose": "official VDP command and screen behavior"},
            {"repository": "agon-vdp", "ref": "v2.16.0", "purpose": "vendored official parser and lifecycle provenance"},
            {"repository": "agon-extender-legacy", "ref": legacy_ref, "purpose": "bounded web presentation proof"},
            {"repository": "esp-idf", "ref": idf_ref, "purpose": "Ethernet, DHCP/netif, HTTP, and WebSocket facilities"},
            {"repository": "arduino-esp32", "ref": arduino_ref, "purpose": "Arduino Stream and hybrid Ethernet integration"},
            {"repository": "agon-emos", "ref": emos_ref, "purpose": "mode, route, and qualification-adapter seam"},
        ],
        "records": records,
    }
    yaml_text = yaml.safe_dump(document, sort_keys=False, width=1000)
    markdown_text = render_markdown(document)
    args.output_yaml.parent.mkdir(parents=True, exist_ok=True)
    args.output_yaml.write_text(yaml_text, encoding="utf-8", newline="\n")
    args.output_markdown.write_text(markdown_text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
