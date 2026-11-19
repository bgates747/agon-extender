"""Offline regression cases for the discovered CLI and phase boundaries."""

from contextlib import contextmanager
from hashlib import sha256
from io import BytesIO
from itertools import count
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from olimex_bench import Bench, fixture_inputs, preflight
from olimex_cli import CliError, Observer, command_result, find_witness, rename_result
from olimex_flash import check_app0, check_extent, configure_flash_size, session_operations
import olimex_p4_app


class TestObserver(unittest.TestCase):
    LOAD = "LOAD /test/bench019/BENCH19.bin &040000"
    RUN = "RUN &040000"
    PROMPT = b"/ *"

    def test_root_and_working_directory_witness(self):
        for prompt in (b"/ *", b"/test/bench019 *", b"*"):
            with self.subTest(prompt=prompt):
                capture = b"/ *VDU 65 13 10\r\r\n\rA\r\n" + prompt
                self.assertEqual(find_witness(capture, "VDU 65 13 10", b"A"), prompt)
        self.assertIsNone(find_witness(b"A\r\n/ *", "VDU 65 13 10", b"A"))
        self.assertIsNone(find_witness(b"VDU 65 13 10\r\nB\r\n/ *", "VDU 65 13 10", b"A"))

    def test_fragmented_load_with_echo_and_fresh_prompt(self):
        capture = b"/ *" + self.LOAD.encode() + b"\r\n\r/ *"
        for end in range(len(capture)):
            self.assertFalse(command_result(capture[:end], self.LOAD, self.PROMPT))
        self.assertTrue(command_result(capture, self.LOAD, self.PROMPT))
        self.assertFalse(command_result(b"/ *", self.LOAD, self.PROMPT))

    def test_rejected_load_is_immediate(self):
        capture = self.LOAD.encode() + b"\r\n\rFile not found\r"
        with self.assertRaisesRegex(CliError, "File not found"):
            command_result(capture, self.LOAD, self.PROMPT)

    def test_rename_needs_the_expected_banner_and_returned_prompt(self):
        source, target = "/emos/sdserve.bin", "/test/previous.bin"
        command = f"RENAME {source} {target}"
        prefix = self.PROMPT + command.encode() + b"\r\n\r"
        banner = f"Moving {source} to {target}".encode() + b"\r\r\n"
        complete = prefix + banner + self.PROMPT
        for end in range(len(complete)):
            self.assertFalse(rename_result(complete[:end], command, self.PROMPT, source, target))
        self.assertTrue(rename_result(complete, command, self.PROMPT, source, target))
        with self.assertRaisesRegex(CliError, "File already exists"):
            rename_result(prefix + banner + b"File already exists\r\n" + self.PROMPT,
                          command, self.PROMPT, source, target)

    def result(self, captured):
        return command_result(captured, self.RUN, self.PROMPT, success=b"BENCH019 PASS",
                              failure=b"BENCH019 FAIL")

    def test_fixture_result_with_returned_mos_error(self):
        capture = b"RUN &040000\r\r\nBENCH019 FAIL; see result.txt\r\nError accessing SD card\r\n/ *"
        with self.assertRaisesRegex(CliError, "BENCH019 FAIL; see result.txt"):
            self.result(capture)
        with self.assertRaisesRegex(CliError, "Error accessing SD card"):
            self.result(capture.replace(b"BENCH019 FAIL; see result.txt\r\n", b""))

    def test_stale_marker_echo_and_success(self):
        self.assertFalse(self.result(b"BENCH019 PASS\r\n/ *"))
        self.assertFalse(self.result(b"RUN &040000\r\nBENCH019 PASS\r\n"))
        self.assertTrue(self.result(b"/ *RUN &040000\r\n\rBENCH019 PASS\r\n/ *"))

    def test_cd_requires_the_new_prompt_after_the_command(self):
        reader = MagicMock(in_waiting=0)
        reader.read.side_effect = [b"/ *CD /test/full\r\n/test/fu", b"ll *"]
        observer = Observer(reader, BytesIO(), MagicMock())
        self.assertEqual(observer.change_directory("enter-cwd", "/test/full", b"/ *"),
                         b"/test/full *")

    def test_run_retains_one_capture_through_later_terminated_uart_line(self):
        end = {"prefix": "PNT ", "line": "PNT end retained=128", "seconds": 30}
        prompt = b"/test/full *"
        head = prompt + b"RUN &040000\r\nPASS\r\n" + prompt
        diagnostics = b"PNT commit n=128\r\nPNT end retained=128"
        for chunks in ([head, diagnostics, b"\r\n"], [head + diagnostics, b"\r\n"],
                       [head.replace(b"PASS", b"PAPNT rows band=1\r\nSS"),
                        diagnostics, b"\r\n"],
                       [head[:-len(prompt)] + diagnostics + b"\r\n" + prompt]):
            with self.subTest(chunks=chunks):
                reader = MagicMock(in_waiting=0)
                reader.read.side_effect = chunks
                transcript = BytesIO()
                dispatch = MagicMock()
                Observer(reader, transcript, dispatch).run(
                    self.RUN, prompt, b"PASS", b"FAIL", 120, uart_end=end)
                self.assertEqual(transcript.getvalue(), b"".join(chunks))
                dispatch.assert_called_once_with("run", self.RUN)

    def test_stale_end_does_not_complete_the_run(self):
        end = {"prefix": "PNT ", "line": "PNT end retained=128", "seconds": 1}
        reader = MagicMock(in_waiting=0)
        reader.read.side_effect = [b"PNT end retained=128\r\nRUN &040000\r\nPASS\r\n/ *", b""]
        observer = Observer(reader, BytesIO(), MagicMock())
        with patch("olimex_cli.time.monotonic", side_effect=[0, 0, 1, 1, 2]):
            with self.assertRaisesRegex(CliError, "UART terminator"):
                observer.run(self.RUN, b"/ *", b"PASS", b"FAIL", 120, uart_end=end)

    def test_native_log_does_not_hide_a_mirrored_mos_error(self):
        end = {"prefix": "PNT ", "line": "PNT end retained=128", "seconds": 30}
        reader = MagicMock(in_waiting=0)
        reader.read.return_value = (
            b"RUN &040000\r\nPASS\r\nError accessing PNT end retained=128\r\nSD card\r\n/ *")
        observer = Observer(reader, BytesIO(), MagicMock())
        with self.assertRaisesRegex(CliError, "Error accessing SD card"):
            observer.run(self.RUN, b"/ *", b"PASS", b"Error accessing SD card", 120, uart_end=end)

    def test_separate_listener_and_native_witness_in_either_order(self):
        end = {"line": "PNT end retained=128", "seconds": 30}
        marker = b"PNT end retained=128\r\n"
        for chunks, statuses in (
            ([marker, b""], [False, True]),
            ([b"PNT end retained=", b"128", b"\r\n"], [True]),
        ):
            with self.subTest(chunks=chunks):
                reader = MagicMock(in_waiting=0)
                reader.read.side_effect = chunks
                transcript = BytesIO()
                dispatch = MagicMock()
                observer = Observer(reader, transcript, dispatch)
                clock = count(step=0.21)
                status = MagicMock(side_effect=[{"online": v} for v in statuses])
                with patch("olimex_cli.time.monotonic", side_effect=lambda: next(clock)):
                    self.assertTrue(observer.run_to_listener("/test/arm/run.txt", 120, end, status)["online"])
                self.assertEqual(transcript.getvalue(), b"".join(chunks))
                dispatch.assert_called_once_with("run", "EXEC /test/arm/run.txt")

    def test_either_witness_missing_stops_without_another_command(self):
        end = {"line": "PNT end retained=128", "seconds": 2}
        for data, online, message in (
            (b"PNT end retained=128\r\n", False, "post-RUN listener admission"),
            (b"PNT end retained=1280\r\n", True, "native UART terminator"),
        ):
            with self.subTest(data=data, online=online):
                reader = MagicMock(in_waiting=0)
                reader.read.return_value = data
                dispatch = MagicMock()
                observer = Observer(reader, BytesIO(), dispatch)
                clock = count(step=0.21)
                with patch("olimex_cli.time.monotonic", side_effect=lambda: next(clock)):
                    with self.assertRaisesRegex(CliError, message):
                        observer.run_to_listener("/test/arm/run.txt", 2, end,
                                                 lambda: {"online": online})
                dispatch.assert_called_once_with("run", "EXEC /test/arm/run.txt")


class TestOta(unittest.TestCase):
    def test_paired_restart_keeps_agon_held_until_p4_pad_release(self):
        events = []

        @contextmanager
        def actuator(_config):
            events.append("hold")
            yield
            events.append("release")

        with tempfile.TemporaryDirectory() as tmp:
            bench = MagicMock()
            bench.out = Path(tmp)
            with patch("olimex_p4_app.hold", actuator), \
                    patch("olimex_p4_app.reset_until_pads_release",
                          side_effect=lambda _bench: events.append("P4 ready")), \
                    patch("olimex_p4_app.wait_boot",
                          side_effect=lambda *_: events.append("Agon ready") or {"ready": True}):
                olimex_p4_app.reboot_pair(bench, 1414)
            self.assertEqual(events, ["hold", "P4 ready", "release", "Agon ready"])
            self.assertTrue((bench.out / "agon-admitted.json").is_file())

    def test_p4_uses_stock_keep_modes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            args = ("write-flash", "--flash-mode", "keep", "--flash-freq", "keep",
                    "--flash-size", "keep", "0x20000", folder / "write.bin")
            with patch("olimex_p4_app.subprocess.run") as run:
                olimex_p4_app.stock(folder, "write", "/dev/p4", "no-reset", *args)
            self.assertEqual(run.call_args.args[0], [
                sys.executable, "-m", "esptool", "--chip", "esp32p4", "--port", "/dev/p4",
                "--baud", "460800", "--before", "no-reset", "--after", "no-reset",
                *map(str, args)])
            self.assertTrue(run.call_args.kwargs["check"])

    def test_unknown_flash_size_keeps_programmer_defaults(self):
        loader = MagicMock()
        detected = MagicMock(return_value=None)
        converter = MagicMock(return_value=16 * 1024 * 1024)
        configure_flash_size(loader, detected, converter)
        loader.flash_set_parameters.assert_not_called()
        converter.assert_not_called()
        detected.return_value = "16MB"
        configure_flash_size(loader, detected, converter)
        converter.assert_called_once_with("16MB")
        loader.flash_set_parameters.assert_called_once_with(16 * 1024 * 1024)

    def selector(self, sequence, state):
        crc = zlib.crc32(struct.pack("<I", sequence), 0xffffffff)
        record = struct.pack("<I20xII", sequence, state, crc)
        return record + b"\xff" * (8192 - len(record))

    def test_commissioned_app0_only(self):
        check_app0(b"\xff" * 8192)
        check_app0(self.selector(1, 2))
        for data in (self.selector(2, 2), self.selector(1, 1), self.selector(1, 4), b"\0" * 8192):
            with self.subTest(head=data[:4]), self.assertRaises(ValueError):
                check_app0(data)

    def test_slot_bounds(self):
        image = b"\0" * 4096
        spec = {"offset": "0x20000", "partition_bytes": 0x700000, "write_bytes": len(image)}
        check_extent("p4", spec, image)
        with self.assertRaises(ValueError):
            check_extent("p4", dict(spec, offset="0x0"), image)

    def test_one_loader_supplies_both_metadata_reads_and_application_io(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            table = b"T" * 3072
            image = b"A" * 4096
            (path / "expected-partition-table.bin").write_bytes(table)
            (path / "write.bin").write_bytes(image)
            loader = MagicMock()
            loader.read_flash.side_effect = [table, self.selector(1, 2), image]
            sent = []

            def program(actual, offset, source):
                self.assertIs(actual, loader)
                self.assertTrue((path / "write-intent.json").is_file())
                sent.append((offset, source.read_bytes()))

            session_operations(loader, program, "mainboard", path)
            self.assertEqual(sent, [(0x10000, image)])
            self.assertEqual([call.args for call in loader.read_flash.call_args_list],
                             [(0x8000, 3072), (0xe000, 8192), (0x10000, len(image))])
            self.assertEqual((path / "readback.bin").read_bytes(), image)

    def test_wrong_live_layout_refuses_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / "expected-partition-table.bin").write_bytes(b"T" * 3072)
            loader = MagicMock()
            loader.read_flash.return_value = b"X" * 3072
            program = MagicMock()
            with self.assertRaisesRegex(RuntimeError, "pinned layout"):
                session_operations(loader, program, "p4", path)
            program.assert_not_called()
            self.assertFalse((path / "write-intent.json").exists())

    def test_retry_requires_exact_production_entry_before_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            table = b"T" * 3072
            (path / "expected-partition-table.bin").write_bytes(table)
            (path / "write.bin").write_bytes(b"A" * 4096)
            (path / "expected-entry.bin").write_bytes(b"P" * 4096)
            loader = MagicMock()
            loader.read_flash.side_effect = [table, self.selector(1, 2), b"X" * 4096]
            program = MagicMock()
            with self.assertRaisesRegex(RuntimeError, "production entry image"):
                session_operations(loader, program, "mainboard", path)
            self.assertEqual((path / "entry-readback.bin").read_bytes(), b"X" * 4096)
            program.assert_not_called()
            self.assertFalse((path / "write-intent.json").exists())


class TestBench(unittest.TestCase):
    def test_native_listener_handoff_packet_and_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            arm = "/test/demo/full"

            def pin(name, contents):
                path = root / name
                path.write_bytes(contents)
                return {"path": str(path), "bytes": len(contents),
                        "sha256": sha256(contents).hexdigest()}

            batch = b"RUN &040000\r\nEMOS sdserve --fast --parallel /\r\n"
            job = {
                "id": "full", "cwd": arm, "agon": pin("fixture.bin", b"program"),
                "sd_program": arm + "/fixture.bin",
                "results": [arm + "/report.txt", arm + "/trace.csv"],
                "address": "040000", "seconds": 120, "success": "PASS", "failure": "FAIL",
                "uart_end": {"prefix": "PNT ", "line": "PNT end retained=128", "seconds": 30},
                "listener_handoff": {"sd_path": arm + "/run.txt", "source": pin("run.txt", batch)},
            }
            kit = {"fixtures": [job], "namespace": "demo", "firmware": {},
                   "preserve": {"/autoexec.txt": "0" * 64, "/emos/sdserve.bin": "0" * 64}}
            self.assertEqual(preflight(kit), ["stage", "run-full", "handback"])
            job["listener_handoff"]["source"] = pin("invalid.txt", batch + b"VDU 12\r\n")
            with self.assertRaisesRegex(ValueError, "only the pinned RUN and listener"):
                preflight(kit)
            job["listener_handoff"]["source"] = pin("run.txt", batch)
            bench = Bench.__new__(Bench)
            bench.out, bench.kit = root, kit
            bench.c = {"ports": ["/dev/fixture"]}
            bench.validate_ports = bench.idle = bench.keyboard = MagicMock()
            events = []
            bench.type_line = MagicMock(side_effect=lambda label, _cmd: events.append(label))
            bench.collect_results = MagicMock(side_effect=lambda *_args, **_opts: events.append("collect"))
            with patch("olimex_bench.open_passive_serial") as port, patch("olimex_bench.Observer") as observe:
                observer = observe.return_value
                observer.witness.side_effect = [b"/ *", arm.encode() + b" *"]
                observer.change_directory.side_effect = [arm.encode() + b" *", b"/ *"]
                observer.run_to_listener.side_effect = lambda *_: events.append("run") or {"online": True}
                bench.invoke("run-full")
                port.assert_called_once()
            self.assertEqual(events, ["mirror-on", "run", "collect", "mirror-resume"])
            observer.run.assert_not_called()
            observer.mirror_off.assert_any_call(arm.encode() + b" *", "mirror-off-run")
            observer.witness.assert_any_call("post-run-witness")
            bench.collect_results.assert_called_once_with(job, root / "results", True,
                                                           listener_online=True)

    def test_named_pair_stages_once_and_collects_each_report_with_a_fresh_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "program.bin"
            marker = root / "GROUND.ON"
            artifact.write_bytes(b"program")
            marker.touch()

            def pin(path):
                data = path.read_bytes()
                return {"path": str(path), "bytes": len(data), "sha256": sha256(data).hexdigest()}

            fixtures = []
            for arm in ("full", "ground"):
                cwd = f"/test/demo/{arm}"
                fixtures.append({
                    "id": arm, "cwd": cwd, "agon": pin(artifact),
                    "sd_program": f"{cwd}/program.bin",
                    "results": [f"{cwd}/stats.txt", f"{cwd}/trace.csv"],
                    "address": "040000", "seconds": 120, "success": "PASS", "failure": "FAIL",
                    "uart_end": {"prefix": "PNT ", "line": "PNT end retained=128", "seconds": 30},
                })
            fixtures[1]["inputs"] = [
                {"sd_path": "/test/demo/ground/GROUND.ON", "source": pin(marker)},
            ]
            kit = {"fixtures": fixtures, "namespace": "demo", "firmware": {},
                   "preserve": {"/autoexec.txt": "0" * 64, "/emos/sdserve.bin": "0" * 64}}
            self.assertEqual(preflight(kit), ["stage", "run-full", "run-ground", "handback"])
            bench = Bench.__new__(Bench)
            bench.out = root
            bench.kit = kit
            bench.stage_parallel = MagicMock()
            bench.stage()
            payloads, results, _ = bench.stage_parallel.call_args.args
            self.assertEqual(payloads, {fixtures[0]["sd_program"]: b"program",
                                        fixtures[1]["sd_program"]: b"program",
                                        "/test/demo/ground/GROUND.ON": b""})
            self.assertEqual(results, fixtures[0]["results"] + fixtures[1]["results"])

            bench.url = "http://example.invalid"
            bench.c = {"ports": ["/dev/example"]}
            bench.validate_ports = bench.idle = bench.keyboard = MagicMock()
            bench.type_line = MagicMock()
            bench.start_listener = MagicMock()
            bench.exit_staged_listener = MagicMock()
            clients = [MagicMock(), MagicMock()]

            def collect(operation, path, *, destination, require_parallel):
                self.assertTrue(require_parallel)
                self.assertEqual(operation, "get")
                destination.write_bytes(path.encode())
                return {"payload_carrier": "parlio"}

            for client in clients:
                client.begin.side_effect = collect
            with patch("olimex_bench.open_passive_serial") as port, \
                    patch("olimex_bench.Observer") as observe, \
                    patch("olimex_bench.StagedClient", side_effect=clients):
                observer = observe.return_value
                observer.witness.return_value = b"/ *"
                observer.change_directory.side_effect = [b"/test/demo/full *", b"/ *"]
                bench.invoke("run-full")
                port.assert_called_once()
            observer.run.assert_called_once_with("RUN &040000", b"/test/demo/full *",
                                                 b"PASS", b"FAIL", 120,
                                                 uart_end=fixtures[0]["uart_end"])
            self.assertEqual(observer.change_directory.call_args_list[1].args,
                             ("restore-cwd", "/", b"/test/demo/full *"))
            for client, path in zip(clients, fixtures[0]["results"]):
                client.close.assert_called_once()
                self.assertEqual(client.begin.call_args.args, ("get", path))
                self.assertEqual((root / "results" / Path(path).name).read_bytes(), path.encode())
            self.assertTrue((root / "results/vdp-usb.bin").is_file())
            bench.exit_staged_listener.assert_called_once_with("collect")

    def test_parallel_staging_rejects_case_alias_of_input(self):
        job = {"sd_program": "/test/demo/program.bin", "sd_result": "/test/demo/result.txt",
               "agon": {}, "inputs": [{"sd_path": "/test/DEMO/PROGRAM.BIN", "source": {}}]}
        with self.assertRaisesRegex(ValueError, "Duplicate fixture or result path"):
            fixture_inputs(job)

    def test_parallel_stage_serializes_sessions_without_readback(self):
        from sdcard import RemoteError

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            bench = Bench.__new__(Bench)
            bench.out = folder
            bench.url = "http://example.invalid"
            bench.get = MagicMock(return_value={
                "parallel_required_supported": True, "parallel_get_required_supported": True,
            })
            bench.start_listener = MagicMock()
            bench.idle = MagicMock()
            bench.keyboard = MagicMock()
            direct = MagicMock()
            direct.rpc.return_value = struct.pack("<IHH", 1, 212, 0x180)
            direct.stat_entry.side_effect = RemoteError("absent", status=6, detail=b"\x04")
            exit_client = MagicMock()
            uploads = []

            def begin(operation, target, *, source, activate, require_parallel):
                direct.lock.close.assert_called_once()
                exit_client.connect.assert_not_called()
                self.assertEqual(operation, "put")
                self.assertTrue(activate and require_parallel)
                data = source.read_bytes()
                uploads.append((target, data))
                return {"payload_carrier": "parlio" if data else "empty-control"}

            bench.kit = {"firmware": {}, "fixture": {
                "sd_program": "/test/demo/program.bin", "sd_result": "/test/demo/result.txt",
                "inputs": [],
            }}
            for name, field, data in (("program.bin", "agon", b"program"),
                                      ("GROUND.ON", "inputs", b"")):
                local = folder / name
                local.write_bytes(data)
                spec = {"path": str(local), "bytes": len(data), "sha256": sha256(data).hexdigest()}
                if field == "agon":
                    bench.kit["fixture"][field] = spec
                else:
                    bench.kit["fixture"][field].append({"sd_path": f"/test/demo/{name}", "source": spec})

            with patch("olimex_bench.Client", side_effect=[direct, exit_client]), \
                    patch("olimex_bench.StagedClient", return_value=MagicMock(begin=begin)):
                bench.stage()
            self.assertEqual(uploads, [("/test/demo/program.bin", b"program"),
                                       ("/test/demo/GROUND.ON", b"")])
            direct.download.assert_not_called()
            exit_client.download.assert_not_called()
            exit_client.rpc.assert_called_once_with(11)
            self.assertEqual(len(list(folder.glob("*.receipt.json"))), 2)

    def test_parallel_stage_refuses_missing_listener_capability(self):
        with tempfile.TemporaryDirectory() as tmp:
            bench = Bench.__new__(Bench)
            bench.out = Path(tmp)
            bench.kit = {"schema": 3}
            bench.url = "http://example.invalid"
            bench.get = MagicMock(return_value={
                "parallel_required_supported": True, "parallel_get_required_supported": True,
            })
            bench.start_listener = MagicMock()
            direct = MagicMock()
            direct.rpc.return_value = struct.pack("<IHH", 1, 212, 0x80)
            with patch("olimex_bench.Client", return_value=direct), \
                    patch("olimex_bench.StagedClient") as staged:
                with self.assertRaisesRegex(RuntimeError, "lacks the required parallel capabilities"):
                    bench.stage_parallel({"/test/demo/a": b"a"}, [], MagicMock())
                direct.make_directory.assert_not_called()
                staged.assert_not_called()
            direct.lock.close.assert_called_once()

    def test_parallel_run_collects_result_through_required_get(self):
        with tempfile.TemporaryDirectory() as tmp:
            bench = Bench.__new__(Bench)
            bench.out = Path(tmp)
            bench.url = "http://example.invalid"
            bench.c = {"ports": ["/dev/example"]}
            bench.kit = {"fixture": {
                "sd_program": "/test/demo/program.bin", "sd_result": "/test/demo/result.txt",
                "address": "040000", "success": "PASS", "failure": "FAIL",
                "seconds": 5, "expected_agon": ["result"],
            }}
            bench.validate_ports = bench.idle = bench.keyboard = MagicMock()
            bench.type_line = MagicMock()
            bench.start_listener = MagicMock()
            bench.exit_staged_listener = MagicMock()
            bench.listener = MagicMock()
            staged = MagicMock()

            def download(operation, remote, *, destination, require_parallel):
                self.assertEqual((operation, remote, require_parallel),
                                 ("get", "/test/demo/result.txt", True))
                destination.write_bytes(b"result\n")
                return {"payload_carrier": "parlio"}

            staged.begin.side_effect = download
            with patch("olimex_bench.open_passive_serial"), patch("olimex_bench.Observer"), \
                    patch("olimex_bench.StagedClient", return_value=staged):
                bench.invoke()
            bench.listener.assert_not_called()
            bench.exit_staged_listener.assert_called_once_with("collect")
            staged.close.assert_called_once()
            self.assertIn("parlio", (bench.out / "sd-collect.receipt.json").read_text())

    def test_plain_production_plan_and_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            artifact = folder / "demo.bin"
            artifact.write_bytes(b"known")
            kit = {"schema": 1, "namespace": "demo", "firmware": {},
                   "fixture": {"agon": {"path": str(artifact), "bytes": 5,
                                        "sha256": sha256(b"known").hexdigest()},
                               "sd_program": "/test/demo/demo.bin", "sd_result": "/test/demo/results/out",
                               "address": "040000", "seconds": 30, "success": "PASS", "failure": "FAIL"},
                   "preserve": {"/autoexec.txt": "0" * 64, "/emos/sdserve.bin": "0" * 64}}
            self.assertEqual(preflight(kit), ["stage", "run", "handback"])
            bench = Bench.__new__(Bench)
            bench.out = folder
            bench.kit = kit
            client = MagicMock()
            from sdcard import RemoteError
            client.stat_entry.side_effect = RemoteError("absent", status=6, detail=b"\x04")
            client.download.return_value = artifact.read_bytes()
            with patch.object(bench, "listener", side_effect=lambda name, command, callback: callback(client)), \
                    patch.object(bench, "invoke") as invoke, patch.object(bench, "firmware") as firmware:
                bench.stage()
                firmware.assert_not_called()
                invoke.assert_not_called()
            client.make_directory.assert_any_call("/test/demo/results", parents=True)
            client.upload.assert_called_once_with("/test/demo/demo.bin", b"known", activate=True, fast=True)

    def test_keyboard_cancel_keeps_nonzero_session_id(self):
        bench = Bench.__new__(Bench)
        bench.url = "http://example.invalid"
        result = dict(ready=True, physical_neutral=True, pending=0, held=0, session=25, reason=1)
        with tempfile.TemporaryDirectory() as tmp, patch("olimex_bench.status", return_value=result) as read:
            bench.out = Path(tmp)
            self.assertEqual(bench.keyboard(), result)
            result["reason"] = 0
            with self.assertRaises(RuntimeError):
                bench.keyboard()
            import json
            self.assertEqual(json.loads(next(bench.out.glob("keyboard-refused-*.json")).read_text()), result)
            self.assertEqual(read.call_count, 2)


if __name__ == "__main__":
    unittest.main()
