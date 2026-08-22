#!/usr/bin/env python3
"""Generate independent PORT-003 Phase C logical-frame event traces.

The model below implements only the written Phase C contracts.  It does not
import, execute, inspect output from, or share code with the production frame
service.  Generated traces are therefore expectations, not self-comparisons.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
from pathlib import Path
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import canonical_yaml, write_canonical  # noqa: E402


class ContractModel:
    def __init__(self, initial: dict[str, Any]):
        self.double = bool(initial.get("double_buffered", False))
        self.frame = int(initial.get("frame_counter", 0)) & 0xFFFFFFFF
        self.generation = int(initial.get("generation", 0))
        self.pending_ticks = 0
        self.submitted = 0
        self.started = 0
        self.completed = 0
        self.visible = 0
        self.drawing = 1 if self.double else 0
        self.queue: list[dict[str, Any]] = []
        self.active: dict[str, Any] | None = None
        self.stopped = False
        self.consumers: dict[str, dict[str, Any]] = {}
        self.metrics = {"elapsed_ticks": 0, "serviced_edges": 0}
        self.events: list[dict[str, Any]] = []

    def event(self, name: str, **fields: Any) -> None:
        self.events.append({"event": name, **fields})

    def submit(self, kind: str, dynamic: bool = False) -> None:
        if self.double and kind != "swap":
            self.event("immediate", kind=kind)
            return
        self.submitted += 1
        item = {"sequence": self.submitted, "kind": kind, "dynamic": dynamic}
        self.queue.append(item)
        self.event("submitted", sequence=self.submitted, kind=kind)

    def start_one(self) -> None:
        if self.active is not None or not self.queue:
            self.event("start-none")
            return
        self.active = self.queue.pop(0)
        self.started = self.active["sequence"]
        self.event("started", sequence=self.started, kind=self.active["kind"])

    def execute_active(self) -> dict[str, Any] | None:
        if self.active is None:
            self.event("finish-none")
            return None
        item = self.active
        if item["kind"] == "swap":
            self.visible, self.drawing = self.drawing, self.visible
            self.event("planes-swapped", sequence=item["sequence"], visible=self.visible, drawing=self.drawing)
        if item["dynamic"]:
            self.event("payload-released", sequence=item["sequence"])
        self.active = None
        return item

    def complete(self, item: dict[str, Any]) -> None:
        self.completed = item["sequence"]
        self.event("completed", sequence=self.completed, kind=item["kind"])

    def publish(self) -> None:
        self.generation += 1
        self.event("published", generation=self.generation, frame_counter=self.frame, visible=self.visible)
        for name in sorted(self.consumers):
            consumer = self.consumers[name]
            if not consumer["connected"]:
                continue
            if consumer["slot"] is not None:
                consumer["drops"] += 1
                self.event("consumer-drop", consumer=name, dropped_generation=consumer["slot"], drops=consumer["drops"])
            consumer["slot"] = self.generation
            self.event("consumer-notified", consumer=name, generation=self.generation)

    def service(self, budget: int) -> None:
        if self.pending_ticks == 0:
            self.event("service-idle")
            return
        self.pending_ticks -= 1
        self.frame = (self.frame + 1) & 0xFFFFFFFF
        self.metrics["elapsed_ticks"] += 1
        self.metrics["serviced_edges"] += 1
        self.event("frame-edge", elapsed=1, frame_counter=self.frame)
        for _ in range(budget):
            if not self.queue:
                break
            self.start_one()
            item = self.execute_active()
            if item is not None:
                self.complete(item)
        self.publish()

    def apply(self, operation: dict[str, Any]) -> None:
        op = operation["op"]
        if op == "submit":
            self.submit(operation["kind"], bool(operation.get("dynamic", False)))
        elif op == "tick":
            count = int(operation.get("count", 1))
            self.pending_ticks += count
            self.event("ticks-recorded", count=count, pending=self.pending_ticks)
        elif op == "service":
            self.service(int(operation.get("budget", 64)))
        elif op == "start-one":
            self.start_one()
        elif op == "finish-one":
            item = self.execute_active()
            if item is not None:
                self.complete(item)
        elif op == "wait":
            target = int(operation.get("sequence", self.submitted))
            result = "satisfied" if not self.queue else "blocked"
            self.event("wait-result", sequence=target, result=result)
        elif op == "write-frame-counter":
            self.frame = int(operation["value"]) & 0xFFFFFFFF
            self.event("frame-counter-written", value=self.frame)
        elif op == "register":
            name = operation["consumer"]
            self.consumers[name] = {"connected": True, "slot": None, "drops": 0}
            self.event("consumer-registered", consumer=name)
        elif op == "consume":
            consumer = self.consumers[operation["consumer"]]
            generation = consumer["slot"]
            consumer["slot"] = None
            self.event("consumer-consumed", consumer=operation["consumer"], generation=generation)
        elif op == "disconnect":
            consumer = self.consumers[operation["consumer"]]
            consumer["connected"] = False
            consumer["slot"] = None
            self.event("consumer-disconnected", consumer=operation["consumer"])
        elif op == "reconnect":
            self.consumers[operation["consumer"]]["connected"] = True
            self.event("consumer-reconnected", consumer=operation["consumer"])
        elif op == "stop":
            drained: list[int] = []
            if self.active is not None:
                drained.append(self.active["sequence"])
                item = self.execute_active()
                if item is not None:
                    self.complete(item)
            while self.queue:
                self.start_one()
                drained.append(self.active["sequence"])
                item = self.execute_active()
                if item is not None:
                    self.complete(item)
            self.pending_ticks = 0
            self.stopped = True
            self.event("stopped", drained=drained)
        else:
            raise ValueError(f"unknown operation {op}")

    def final(self) -> dict[str, Any]:
        return {
            "frame_counter": self.frame,
            "generation": self.generation,
            "pending_ticks": self.pending_ticks,
            "submitted_sequence": self.submitted,
            "started_sequence": self.started,
            "completed_sequence": self.completed,
            "queue_depth": len(self.queue),
            "active": None if self.active is None else self.active["sequence"],
            "visible_plane": self.visible,
            "drawing_plane": self.drawing,
            "metrics": self.metrics,
            "consumers": self.consumers,
        }


SCENARIOS = (
    ("sink-free-edge", {}, [{"op": "tick"}, {"op": "service"}]),
    ("three-distinct-frame-edges", {}, [{"op": "tick", "count": 3}, {"op": "service"}, {"op": "service"}, {"op": "service"}]),
    ("frame-counter-rollover", {"frame_counter": 0xFFFFFFFE}, [{"op": "tick", "count": 3}, {"op": "service"}, {"op": "service"}, {"op": "service"}]),
    ("writable-counter-continues", {}, [{"op": "write-frame-counter", "value": 0x1234FFFF}, {"op": "tick", "count": 2}, {"op": "service"}, {"op": "service"}]),
    ("dequeued-satisfies-upstream-queue-wait", {}, [{"op": "submit", "kind": "line"}, {"op": "start-one"}, {"op": "wait"}, {"op": "finish-one"}, {"op": "wait"}]),
    ("single-buffer-fifo-budget", {}, [{"op": "submit", "kind": "line"}, {"op": "submit", "kind": "glyph", "dynamic": True}, {"op": "tick"}, {"op": "service", "budget": 1}, {"op": "wait", "sequence": 2}, {"op": "tick"}, {"op": "service", "budget": 1}, {"op": "wait", "sequence": 2}]),
    ("single-buffer-flush-next-edge", {}, [{"op": "submit", "kind": "flush"}, {"op": "wait"}, {"op": "tick"}, {"op": "service"}, {"op": "wait"}]),
    ("double-immediate-and-swap", {"double_buffered": True}, [{"op": "submit", "kind": "line"}, {"op": "submit", "kind": "swap"}, {"op": "wait"}, {"op": "tick"}, {"op": "service"}, {"op": "wait"}]),
    ("slow-consumer-latest-only", {}, [{"op": "register", "consumer": "slow"}, {"op": "tick"}, {"op": "service"}, {"op": "tick"}, {"op": "service"}, {"op": "tick"}, {"op": "service"}, {"op": "consume", "consumer": "slow"}]),
    ("consumer-disconnect-reconnect", {}, [{"op": "register", "consumer": "mock"}, {"op": "disconnect", "consumer": "mock"}, {"op": "tick", "count": 2}, {"op": "service"}, {"op": "service"}, {"op": "reconnect", "consumer": "mock"}, {"op": "tick"}, {"op": "service"}]),
    ("tick-arrives-between-services", {}, [{"op": "tick"}, {"op": "service"}, {"op": "tick", "count": 2}, {"op": "service"}, {"op": "service"}]),
    ("stop-drains-and-releases", {}, [{"op": "submit", "kind": "path", "dynamic": True}, {"op": "submit", "kind": "transform", "dynamic": True}, {"op": "start-one"}, {"op": "stop"}, {"op": "wait", "sequence": 2}]),
)


def payload_hash(value: Any) -> str:
    return hashlib.sha256(canonical_yaml(value).encode("utf-8")).hexdigest()


def build_fixture(name: str, initial: dict[str, Any], operations: list[dict[str, Any]]) -> dict[str, Any]:
    model = ContractModel(initial)
    for operation in operations:
        model.apply(operation)
    fixture = {
        "id": name,
        "oracle_class": "independent upstream-derived contract state model",
        "initial": copy.deepcopy(initial),
        "operations": copy.deepcopy(operations),
        "expected_events": model.events,
        "expected_final": model.final(),
    }
    fixture["content_sha256"] = payload_hash(fixture)
    return fixture


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "docs/tasks/PORT-003/phase-c/fixtures/frame-traces.yaml")
    args = parser.parse_args()
    fixtures = [build_fixture(name, initial, operations) for name, initial, operations in SCENARIOS]
    artifact = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_c_frame_trace_fixtures",
        "generated_by": "docs/tasks/PORT-003/phase-c/scripts/generate-frame-traces.py",
        "source_profile": {"agon_vdp": "v2.16.0", "vdp_gl": "all-the-plots"},
        "prohibition": "production frame-service output is not an oracle input",
        "fixtures": fixtures,
        "fixture_set_sha256": payload_hash(fixtures),
    }
    write_canonical(args.output.resolve(), artifact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
