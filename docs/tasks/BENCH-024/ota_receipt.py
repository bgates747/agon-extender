"""Validate the snapshots in the Agon Flash verified-OTA SD receipt."""
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import struct


SNAPSHOT = struct.Struct("<BBHIQBBBBII32s16s4s")
IDLE, VERIFIED, ACTIVATED = 0, 3, 4


@dataclass(frozen=True)
class Snapshot:
    state: int
    error: int
    transaction: int
    boot: int
    running: int
    configured: int
    target: int
    digest_valid: int
    accepted: int
    length: int
    digest: str
    build: str

    @classmethod
    def parse(cls, raw):
        if len(raw) != SNAPSHOT.size:
            raise ValueError("Expected one complete 80-byte VDP snapshot")
        version, *fields, digest, build, reserved = SNAPSHOT.unpack(raw)
        if version != 1 or reserved != bytes(4) or not fields[3]:
            raise ValueError("Invalid VDP snapshot version, reserved bytes or boot nonce")
        return cls(*fields, digest.hex(), build.hex())

    @property
    def identity(self):
        return self.boot, self.running, self.build

    def evidence(self):
        data = asdict(self)
        data["boot"] = f"{self.boot:016x}"
        data["transaction"] = f"{self.transaction:08x}"
        return data


def snapshot_pair(raw):
    if len(raw) != 2 * SNAPSHOT.size:
        raise ValueError("Expected complete before and after snapshots")
    return Snapshot.parse(raw[:SNAPSHOT.size]), Snapshot.parse(raw[SNAPSHOT.size:])


def verify_write(raw, transaction, source_slot, source_build, image):
    before, after = snapshot_pair(raw)
    if (before.state != IDLE or before.error or before.transaction
            or before.running != source_slot or before.configured != source_slot
            or before.build != source_build):
        raise ValueError("Write did not begin on the pinned running app and boot selection")
    target = 1 - source_slot
    if (after.identity != before.identity or after.configured != before.configured
            or after.target != target or after.state != VERIFIED or after.error
            or after.transaction != transaction or after.digest_valid != 1
            or after.accepted != len(image) or after.length != len(image)
            or after.digest != sha256(image).hexdigest()):
        raise ValueError("Write receipt failed flash hash, extent, transaction or pre-reboot checks")
    return before, after


def verify_selection(raw, verified):
    before, after = snapshot_pair(raw)
    if (before != verified
            or after != replace(verified, state=ACTIVATED, configured=verified.target)):
        raise ValueError("Activation failed the verified write binding or boot-selector checks")
    return before, after


def verify_candidate_boot(raw, selected, expected_build):
    boot = Snapshot.parse(raw)
    if (boot.state != IDLE or boot.error or boot.transaction or boot.boot == selected.boot
            or boot.running != selected.target or boot.configured != selected.target
            or boot.build != expected_build):
        raise ValueError("Candidate boot was not fresh or did not match the selected app")
    return boot
