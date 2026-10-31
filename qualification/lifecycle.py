"""Pi coordination of ordinary CLI invocation and read-only startup preservation.

Supported entry is an operator-confirmed Legacy CLI with single-buffered modes.
No claim is made for double-buffered CLI cleanup; those entries fail closed.
Only the separately invoked hardware runner creates a session, never an offline
receipt/build/check command. Every SD operation requires checksum-free protocol2.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import time
import uuid
from urllib.request import urlopen

from hardware_validation import atomic_json, keyboard_status, sha256, type_line, wait_sd_service


class UnsafeForeground(RuntimeError):
    """Do not reset, notify, inject input or continue dispatch after this error."""


def require_absent(client, path: str) -> None:
    from sdcard import RemoteError
    try:
        client.stat_entry(path)
    except RemoteError as error:
        if error.status != 6:
            raise
    else:
        raise ValueError("refusing to replace an existing SD file: " + path)


def stage_new_file(client, path: str, data: bytes) -> None:
    require_absent(client, path)
    client.upload(path, data, True, fast=True)
    if client.download(path) != data:
        raise ValueError("staged SD file readback mismatch: " + path)


def require_normal_startup(data: bytes) -> None:
    lines = [line.strip().lower() for line in data.decode("ascii").splitlines()
             if line.strip() and not line.lstrip().startswith("#")]
    if "emos keyinput extender" not in lines or "emos keyinput mainboard" in lines:
        raise ValueError("normal startup must select the admitted Extender keyboard")
    # Deliberately conservative. Unknown startup commands need separate review;
    # the runner never repairs startup or assumes an IF/alias cannot launch work.
    prefixes = ("set keyboard ", "emos keyinput extender", "cd ", "load ", "echo ", "vdu ")
    if any(not line.startswith(prefixes) for line in lines):
        raise ValueError("startup contains execution or an unreviewed command; no reset permitted")


def mode_record(value: dict) -> dict:
    result = {k: value[k] for k in ("mode", "width", "height", "colors")}
    if (any(type(v) is not int for v in result.values()) or
            not 0 <= result["mode"] < 128 or min(result[k] for k in ("width", "height", "colors")) < 1 or
            value.get("double_buffered", False)):
        raise ValueError("single-buffered mode and visible CLI cleanup required")
    return result


def verify_fixtures(path: Path) -> dict:
    document = json.loads(path.read_text())
    if document.get("fixture_contract") != "explicit-cli-no-startup-write":
        raise ValueError("qualification fixtures have the obsolete startup contract")
    for name in ("qstate", "raw_sd"):
        item = document["fixtures"][name]
        binary = Path(item["binary"]).resolve(strict=True)
        if sha256(binary) != item["sha256"] or b"/autoexec.txt" in binary.read_bytes():
            raise ValueError("qualification fixture changed or contains a startup path")
        work = binary.parents[1]
        for relative, digest in item["source_files"].items():
            if sha256(work / relative) != digest:
                raise ValueError("qualification fixture source changed")
    return document


class Session:
    def __init__(self, config: dict, output: Path, fixtures: dict):
        self.url, self.output, self.config = config["extender_url"], output, config
        self.fixtures = fixtures
        self.boot = keyboard_status(self.url)["boot"]
        self.route = "legacy"
        self.sequence = 0
        self.owned_paths = []
        self.original_startup = None
        self.entry = None
        self.probe = "/extender/.qstate-" + uuid.uuid4().hex[:16] + ".bin"
        self.unsafe = False

    def read(self, path: str) -> dict:
        with urlopen(self.url.rstrip("/") + path, timeout=5) as response:
            return json.load(response)

    def check_boot(self) -> None:
        if keyboard_status(self.url)["boot"] != self.boot:
            self.unsafe = True
            raise UnsafeForeground("Agon reset interrupted the run; no automatic resume or next test")

    def command(self, journal: Path, line: str) -> dict:
        if self.unsafe:
            raise UnsafeForeground("foreground is uncertain; input dispatch is blocked")
        self.check_boot()
        value = type_line(self.url, journal, line)
        self.check_boot()
        return value

    def journal(self, label: str) -> Path:
        self.sequence += 1
        return self.output / f"lifecycle-{self.sequence:03d}-{label}.json"

    def service(self):
        self.check_boot()
        if not self.read("/sd/status").get("online"):
            self.command(self.journal("listener"), "EMOS sdserve --fast /")
        try:
            client = wait_sd_service(self.url, self.journal("sd"), timeout=30, require_fast=True)
            self.check_boot()
            return client
        except BaseException as error:
            self.unsafe = True
            raise UnsafeForeground("listener handback was not established; foreground uncertain") from error

    def startup(self, client) -> None:
        data = client.download("/autoexec.txt")
        require_normal_startup(data)
        if self.original_startup is None:
            self.original_startup = data
            (self.output / "startup-before.txt").write_bytes(data)
        elif data != self.original_startup:
            self.unsafe = True
            raise UnsafeForeground("startup changed; no repair or reset attempted")

    def verify_startup(self) -> None:
        # Caller must already have positive CLI/service handback; no resets are
        # used to get this evidence. The raw-I/O uncertain path never calls here.
        self.select_route("legacy")
        client = self.service()
        try:
            self.startup(client)
            client.rpc(11)
        finally:
            client.lock.close()

    def probe_mainboard(self, restore: dict | None = None) -> dict:
        self.select_route("legacy")
        token = uuid.uuid4().hex[:16].upper()
        result_path = "/agents/extender/results/qstate-" + token + ".txt"
        script = "/extender/.qstate-" + token + ".txt"
        args = ("capture " + token if restore is None else
                "restore {mode} {width} {height} {colors} ".format(**restore) + token)
        command_file = (f"LOAD {self.probe}\r\nRUN . {args}\r\n"
                        "EMOS sdserve --fast /\r\n").encode("ascii")
        client = self.service()
        try:
            self.startup(client)
            self.owned_paths.append(script)
            stage_new_file(client, script, command_file)
            client.rpc(11)
        finally:
            client.lock.close()
        self.command(self.journal("state-exec"), "EXEC " + script)
        # This listener is a line after the application in the explicit EXEC.
        # It cannot run recursively while the application still owns foreground.
        try:
            client = wait_sd_service(self.url, self.journal("state-result"), timeout=30,
                                     require_fast=True)
        except BaseException as error:
            self.unsafe = True
            raise UnsafeForeground("state appliance did not hand back; no recovery input sent") from error
        try:
            self.check_boot()
            fields = dict(line.split("=", 1) for line in client.download(result_path).decode("ascii").splitlines())
            if fields.get("token") != token or fields.get("schema") != "1":
                raise ValueError("fresh mode-query token mismatch")
            value = mode_record({k: int(fields["colours" if k == "colors" else k])
                                 for k in ("mode", "width", "height", "colors")})
            self.owned_paths.append(result_path)
            self.startup(client)
            client.rpc(11)
        finally:
            client.lock.close()
        atomic_json(self.journal("mode-receipt"), {"target": "mainboard", "mode": value,
                                                  "boot": self.boot, "token": token})
        if restore is not None and value != restore:
            raise ValueError("mainboard mode restoration mismatch")
        return value

    def prepare(self) -> None:
        display = self.read("/display/status")
        if not display.get("available"):
            raise ValueError("P4 display is unavailable")
        native = display.get("output") == "hdmi"
        if native != (self.config["output_profile"] == "native-hdmi"):
            raise ValueError("declared qualification profile does not match installed P4 output")
        extender = mode_record(display)
        client = self.service()
        try:
            self.startup(client)
            for directory in ("/extender", "/agents/extender/results"):
                if not client.stat_entry(directory)[1] & 16:
                    raise ValueError("required qualification directory missing: " + directory)
            binary = Path(self.fixtures["fixtures"]["qstate"]["binary"]).read_bytes()
            self.owned_paths.append(self.probe)
            stage_new_file(client, self.probe, binary)
            client.rpc(11)
        finally:
            client.lock.close()
        mainboard = self.probe_mainboard()
        self.entry = {"route": "legacy", "mainboard": mainboard, "extender": extender}
        atomic_json(self.output / "entry-state.json", self.entry)
        self.command(self.journal("clear-old-cue"), "VDU 12")

    def select_route(self, route: str) -> None:
        if route != self.route:
            self.command(self.journal("route"), "EMOS " + route.upper() + " --keep-display")
            self.route = route

    def select_extender_mode(self, wanted: dict) -> dict:
        self.select_route("excom")
        actual = self.read("/display/status")
        if mode_record(actual) != wanted:
            self.command(self.journal("mode"), "VDU 22 " + str(wanted["mode"]))
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                actual = self.read("/display/status")
                if mode_record(actual) == wanted:
                    time.sleep(1.0)
                    self.check_boot()
                    return actual
                time.sleep(0.2)
            raise RuntimeError("Extender mode selection did not commit")
        return actual

    def after_reset(self, status: dict) -> None:
        if status["boot"] == self.boot:
            raise RuntimeError("reset did not produce a fresh admission epoch")
        self.boot, self.route = status["boot"], "legacy"
        # EMOS admits Extender input inside normal startup, before later CD/LOAD
        # commands and the final prompt. Keys injected during LOAD can be lost.
        # This bounded allowance is for the reviewed setup-only startup, never
        # a completion claim: the actual listener/read/EXIT below must pass.
        settle = self.config.get("reset_settle_seconds", 2.0)
        if isinstance(settle, bool) or not isinstance(settle, (int, float)) or not 2 <= settle <= 30:
            raise ValueError("reset_settle_seconds must be between 2 and 30")
        started = time.monotonic()
        time.sleep(settle)
        self.check_boot()
        atomic_json(self.journal("post-reset-settling"), {
            "boot": self.boot, "minimum_seconds": settle,
            "elapsed_seconds": time.monotonic() - started,
            "clock": "host monotonic seconds; startup allowance, not CLI proof"})
        # Fresh service/read/EXIT, not a ready flag or serial mirror, proves CLI.
        self.verify_startup()

    def verify_emos_rom(self, receipt: dict) -> None:
        token = uuid.uuid4().hex[:16].upper()
        script = "/extender/.rom-" + token + ".txt"
        target = "/agents/extender/results/rom-" + token + ".bin"
        commands = (f"SAVE {target} &0 &20000\r\nEMOS sdserve --fast /\r\n").encode("ascii")
        client = self.service()
        try:
            self.startup(client)
            require_absent(client, target)
            stage_new_file(client, script, commands)
            self.owned_paths.append(script)
            client.rpc(11)
        finally:
            client.lock.close()
        self.command(self.journal("save-rom"), "EXEC " + script)
        try:
            # EXEC already queues its own listener. Do not inject another
            # command while SAVE may still own the foreground.
            client = wait_sd_service(self.url, self.journal("rom-result"), timeout=60,
                                     require_fast=True)
        except BaseException as error:
            self.unsafe = True
            raise UnsafeForeground("ROM-save batch did not hand back; no additional input sent") from error
        try:
            data = client.download(target)
            self.check_boot()
            (self.output / "current-emos-rom.bin").write_bytes(data)
            if len(data) != 131072 or hashlib.sha256(data).hexdigest() != receipt["installed_readback_sha256"]:
                raise ValueError("current complete EMOS ROM differs from the accepted installation")
            self.owned_paths.append(target)
            client.rpc(11)
        finally:
            client.lock.close()
        atomic_json(self.output / "current-emos-identity.json", {
            "status": "verified", "boot": self.boot, "bytes": len(data),
            "installed_rom_sha256": hashlib.sha256(data).hexdigest()})

    def restore(self) -> None:
        if self.unsafe or self.entry is None:
            raise UnsafeForeground("entry state or foreground unproven; restoration blocked")
        self.select_extender_mode(self.entry["extender"])
        self.select_route("legacy")
        self.probe_mainboard(self.entry["mainboard"])
        self.verify_startup()
        atomic_json(self.output / "restoration.json", {
            "status": "verified", "entry": self.entry, "boot": self.boot,
            "startup_unchanged": True,
            "startup_sha256": hashlib.sha256(self.original_startup).hexdigest(),
            "cli_handback": "explicit mode-query application and listener read/EXIT"})

    def cleanup(self, paths: list[str] | None = None) -> None:
        # Old sdserve has no DELETE operation. MOS owns deletion; the separate
        # listener readback proves only these run-owned support paths absent.
        # Execute the file commands synchronously inside MOS: acknowledged key
        # events do not establish that a preceding FAT operation has returned.
        # Retain the command file as result evidence, never delete an open EXEC.
        from sdcard import RemoteError
        paths = ([p for p in self.owned_paths if p.startswith("/extender/.")]
                 if paths is None else list(paths))
        if any(p not in self.owned_paths or not p.startswith("/extender/.") for p in paths):
            raise ValueError("cleanup is limited to this session's owned support files")
        script = "/agents/extender/results/cleanup-" + uuid.uuid4().hex[:16] + ".txt"
        client = self.service()
        try:
            self.startup(client)
            commands = "".join("DELETE -f " + path + "\r\n" for path in paths)
            stage_new_file(client, script, (commands + "EMOS sdserve --fast /\r\n").encode("ascii"))
            self.owned_paths.append(script)
            client.rpc(11)
        finally:
            client.lock.close()
        self.command(self.journal("cleanup-exec"), "EXEC " + script)
        try:
            client = wait_sd_service(self.url, self.journal("cleanup-result"), timeout=60,
                                     require_fast=True)
        except BaseException as error:
            self.unsafe = True
            raise UnsafeForeground("cleanup command file did not hand back; no additional input sent") from error
        try:
            self.check_boot()
            self.startup(client)
            for path in paths:
                try:
                    client.download(path)
                except RemoteError as error:
                    if error.status != 6:
                        raise
                else:
                    raise RuntimeError("temporary qualification file survived DELETE: " + path)
            client.rpc(11)
        finally:
            client.lock.close()
        self.owned_paths = [p for p in self.owned_paths if p not in paths]
        record = {"status": "verified", "removed": paths,
                  "retained_results": self.owned_paths.copy()}
        atomic_json(self.journal("cleanup-receipt"), record)
        atomic_json(self.output / "support-cleanup.json", record)

    def verify_entry(self) -> None:
        # In particular, never repair modes after the terminal spoken cue: a
        # mode reset would clear that new completion output. A player which
        # changes modes fails the gate and needs its own lifecycle correction.
        if mode_record(self.read("/display/status")) != self.entry["extender"]:
            raise ValueError("attention player changed the Extender entry mode")
        if self.probe_mainboard() != self.entry["mainboard"]:
            raise ValueError("attention player changed the mainboard entry mode")
