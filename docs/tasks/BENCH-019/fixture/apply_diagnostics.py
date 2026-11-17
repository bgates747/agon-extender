#!/usr/bin/env python3
"""Add the three diagnostics to BENCH-019's disposable source copies."""

import argparse
from pathlib import Path


def insert_before(path: Path, anchor: str, fragment: str) -> None:
    source = path.read_bytes()
    newline = b"\r\n" if b"\r\n" in source else b"\n"
    encoded_anchor = anchor.encode()
    encoded_fragment = fragment.encode().replace(b"\n", newline)
    if source.count(encoded_anchor) != 1 or encoded_fragment in source:
        raise ValueError(f"Unexpected source or diagnostic already present: {path}")
    path.write_bytes(source.replace(encoded_anchor, encoded_fragment + encoded_anchor))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("emos", type=Path)
    parser.add_argument("p4", type=Path)
    parser.add_argument("vdplet", type=Path)
    args = parser.parse_args()

    insert_before(
        args.emos / "src/emos.c",
        '    if (!strcasecmp(operation, "keyinput"))',
        '    /* BENCH-019 rehearsal only. */\n'
        '    if (!strcasecmp(operation, "bench019"))\n'
        '        return args && !strcasecmp(args, "probe") ? FR_OK : FR_INVALID_PARAMETER;\n',
    )
    insert_before(
        args.p4 / "vdp/video/extender/network/display_status.hpp",
        "  display::ModeStatus value{};",
        r'''  // BENCH-019 rehearsal only. Use the existing status route and leave its default response alone.
  char query[sizeof("bench019=0")];
  if (httpd_req_get_url_query_str(request, query, sizeof(query)) == ESP_OK &&
      std::strncmp(query, "bench019=", 9) == 0 &&
      query[9] >= '0' && query[9] <= '9' && query[10] == '\0') {
    const unsigned digit = query[9] - '0';
    char output[32];
    std::snprintf(output, sizeof(output), "{\"bench019_p4\":%u}", digit * digit);
    httpd_resp_set_type(request, "application/json");
    httpd_resp_set_hdr(request, "Cache-Control", "no-store");
    return httpd_resp_sendstr(request, output);
  }
''',
    )
    insert_before(args.p4 / "vdp/video/extender/network/display_status.hpp", "#include <cstdio>",
                  "#include <cstring>\n")
    insert_before(
        args.vdplet / "video/vdu_sys.h",
        "        case VDP_GP:",
        "        case 0xB8: { // BENCH-019 rehearsal only. No payload or display changes.\n"
        "            uint8_t response[] = {0x56};\n"
        "            send_packet(PACKET_SCRCHAR, sizeof response, response);\n"
        "        } break;\n",
    )


if __name__ == "__main__":
    main()
