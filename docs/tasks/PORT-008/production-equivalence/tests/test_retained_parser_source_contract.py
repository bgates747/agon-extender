"""Structural guards for the retained-parser/production-Stream boundary.

These tests inspect the maintained sources.  They do not instantiate or run
VDUStreamProcessor and therefore are not parser, display, or target evidence.
The durable limitation and removal test live in retained-parser/README.md.
"""

from __future__ import annotations

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[5]
VIDEO = ROOT / "vdp/video"


def function_region(source: str, signature: str) -> str:
    """Return one C++ function/constructor region using balanced braces."""

    start = source.index(signature)
    opening = source.index("{", start)
    depth = 0
    for offset in range(opening, len(source)):
        character = source[offset]
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return source[start : offset + 1]
    raise AssertionError(f"unterminated function after {signature!r}")


class RetainedParserSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.processor = (VIDEO / "vdu_stream_processor.h").read_text()
        cls.system = (VIDEO / "vdu_sys.h").read_text()
        cls.protocol = (VIDEO / "agon.h").read_text()
        cls.top_level = (VIDEO / "video.ino").read_text()
        cls.qualification = (
            VIDEO / "extender/transport/p4_parallel_qualification.cpp"
        ).read_text()

    def test_parser_adopts_the_raw_stream_pointer(self) -> None:
        constructor = function_region(
            self.processor, "VDUStreamProcessor(Stream *input)"
        )
        self.assertIn(
            "inputStream(std::shared_ptr<Stream>(input))", constructor
        )
        self.assertIn("outputStream(inputStream)", constructor)
        self.assertIn("originalOutputStream(inputStream)", constructor)

    def test_parser_ignores_each_stream_write_result(self) -> None:
        write_byte = function_region(
            self.processor, "inline void writeByte(uint8_t b)"
        )
        self.assertIn("outputStream->write(b);", write_byte)
        self.assertNotIn("TransportFault", write_byte)
        self.assertNotRegex(write_byte, r"return\s+outputStream->write")

    def test_packet_encoder_writes_header_and_payload_byte_by_byte(self) -> None:
        send_packet = function_region(
            self.processor, "void VDUStreamProcessor::send_packet"
        )
        ordered_fragments = (
            "writeByte(code + 0x80);",
            "writeByte(len);",
            "for (int i = 0; i < len; i++)",
            "writeByte(data[i]);",
        )
        positions = [send_packet.index(item) for item in ordered_fragments]
        self.assertEqual(sorted(positions), positions)

    def test_general_poll_sets_initialised_only_after_sending_echo(self) -> None:
        poll_dispatch = function_region(
            self.system, "void VDUStreamProcessor::vdu_sys_video()"
        )
        self.assertRegex(
            poll_dispatch,
            r"case\s+VDP_GP\s*:\s*\{[^}]*sendGeneralPoll\(\)",
        )

        poll = function_region(
            self.system, "void VDUStreamProcessor::sendGeneralPoll()"
        )
        self.assertIn("auto b = readByte_t();", poll)
        self.assertIn(
            "getVDPVariable(VDPVAR_GENERALPOLL_BYTE) & 0xFF", poll
        )
        self.assertIn("send_packet(PACKET_GP, sizeof packet, packet);", poll)
        self.assertIn("initialised = true;", poll)
        self.assertLess(
            poll.index("send_packet(PACKET_GP"),
            poll.index("initialised = true;"),
        )

    def test_startup_wait_sends_mode_information_after_wait_path(self) -> None:
        startup_wait = function_region(
            self.system, "void VDUStreamProcessor::wait_eZ80()"
        )
        self.assertIn("while (!initialised)", startup_wait)
        self.assertIn("vdu_sys();", startup_wait)
        self.assertIn("sendModeInformation();", startup_wait)
        self.assertGreater(
            startup_wait.index("sendModeInformation();"),
            startup_wait.index("while (!initialised)"),
        )

    def test_mode_packet_retains_all_eight_payload_fields(self) -> None:
        mode = function_region(
            self.system, "void VDUStreamProcessor::sendModeInformation()"
        )
        for fragment in (
            "canvasW & 0xFF",
            "(canvasW >> 8) & 0xFF",
            "canvasH & 0xFF",
            "(canvasH >> 8) & 0xFF",
            "context->getNormalisedViewportCharWidth()",
            "context->getNormalisedViewportCharHeight()",
            "getVGAColourDepth()",
            "videoMode",
            "send_packet(PACKET_MODE, sizeof packet, packet);",
        ):
            self.assertIn(fragment, mode)

    def test_packet_codes_remain_general_poll_80_and_mode_86(self) -> None:
        self.assertRegex(
            self.protocol, r"#define\s+PACKET_GP\s+0x00(?:\s|$)"
        )
        self.assertRegex(
            self.protocol, r"#define\s+PACKET_MODE\s+0x06(?:\s|$)"
        )
        self.assertRegex(self.protocol, r"#define\s+VDP_GP\s+0x80(?:\s|$)")

    def test_nonrelease_top_level_passes_heap_stream_to_real_parser(self) -> None:
        self.assertRegex(
            self.qualification,
            re.compile(
                r"new\s*\(std::nothrow\)\s+ExtenderVdpStream\s*\(",
                re.MULTILINE,
            ),
        )
        self.assertIn(
            "beginP4ParallelNonreleaseQualification();", self.top_level
        )
        self.assertIn(
            "processor = new VDUStreamProcessor(qualificationVDPStream);",
            self.top_level,
        )

    def test_nonrelease_owner_retries_cleanup_before_revoking_epoch(self) -> None:
        cleanup = function_region(
            self.qualification, "void stopAndRevokeQualificationEpoch("
        )
        self.assertIn("while (!qualification.plane.stop())", cleanup)
        self.assertLess(
            cleanup.index("qualification.plane.stop()"),
            cleanup.index("qualification.authority.revoke(qualification.lease)"),
        )
        service = function_region(self.qualification, "void serviceTask(")
        self.assertIn("stopAndRevokeQualificationEpoch(qualification);", service)
        begin = function_region(
            self.qualification,
            "ExtenderVdpStream *beginP4ParallelNonreleaseQualification()",
        )
        self.assertEqual(
            begin.count("stopAndRevokeQualificationEpoch(qualification);"), 3
        )
        self.assertNotIn("(void)qualification.plane.stop()", begin + service)

    def test_process_task_failure_stops_before_false_live_boot(self) -> None:
        setup = function_region(self.top_level, "void setup()")
        failed_create = function_region(
            setup, "if (processTaskResult != pdPASS)"
        )
        self.assertIn(
            "requestP4ParallelNonreleaseQualificationStop();", failed_create
        )
        self.assertIn("return;", failed_create)
        self.assertLess(
            setup.index("if (processTaskResult != pdPASS)"),
            setup.index("boot_screen();"),
        )


if __name__ == "__main__":
    unittest.main()
