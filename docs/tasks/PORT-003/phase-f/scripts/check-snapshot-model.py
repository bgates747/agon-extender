#!/usr/bin/env python3
"""Execute and exhaustively check the independent Phase F snapshot model.

This task oracle deliberately imports no production header, source, or binary.
It validates the frozen state machine before the C++ implementation exists.
"""

from __future__ import annotations

import argparse
from collections import deque
from dataclasses import dataclass
from pathlib import Path

import yaml


FREE = "free"
PRODUCER = "producer"
LATEST = "latest"
LEASED = "leased"


@dataclass
class Slot:
    state: str = FREE
    generation: int | None = None


class Model:
    def __init__(self, count: int = 3) -> None:
        self.slots = [Slot() for _ in range(count)]
        self.generation = 0
        self.producer_no_slot = 0
        self.producer_busy = 0
        self.consumer_no_new = 0
        self.consumer_generation = 0

    def clone(self) -> Model:
        other = Model(len(self.slots))
        other.slots = [Slot(slot.state, slot.generation) for slot in self.slots]
        other.generation = self.generation
        other.producer_no_slot = self.producer_no_slot
        other.producer_busy = self.producer_busy
        other.consumer_no_new = self.consumer_no_new
        other.consumer_generation = self.consumer_generation
        return other

    def operate(self, operation: str) -> None:
        if operation == "begin_produce":
            free = self.find(FREE)
            if free is None:
                self.producer_no_slot += 1
                return
            if self.find(PRODUCER) is not None:
                self.producer_busy += 1
                return
            self.slots[free] = Slot(PRODUCER)
        elif operation == "publish":
            producer = self.require(PRODUCER)
            old_latest = self.find(LATEST)
            if old_latest is not None:
                self.slots[old_latest] = Slot()
            self.generation += 1
            self.slots[producer] = Slot(LATEST, self.generation)
        elif operation == "cancel":
            self.slots[self.require(PRODUCER)] = Slot()
        elif operation == "acquire_latest":
            if self.find(LEASED) is not None:
                self.consumer_no_new += 1
                return
            latest = self.find(LATEST)
            if latest is None or self.slots[latest].generation <= self.consumer_generation:
                self.consumer_no_new += 1
                return
            self.consumer_generation = int(self.slots[latest].generation)
            self.slots[latest].state = LEASED
        elif operation == "release":
            leased = self.require(LEASED)
            latest = self.find(LATEST)
            if latest is None or int(self.slots[leased].generation) > int(self.slots[latest].generation):
                self.slots[leased].state = LATEST
            else:
                self.slots[leased] = Slot()
        else:
            raise ValueError(f"unknown operation: {operation}")
        self.check()

    def find(self, state: str) -> int | None:
        return next((index for index, slot in enumerate(self.slots) if slot.state == state), None)

    def require(self, state: str) -> int:
        result = self.find(state)
        if result is None:
            raise ValueError(f"operation requires {state}")
        return result

    def check(self) -> None:
        allowed = {FREE, PRODUCER, LATEST, LEASED}
        assert all(slot.state in allowed for slot in self.slots)
        for state in (PRODUCER, LATEST, LEASED):
            assert sum(slot.state == state for slot in self.slots) <= 1
        assert all(
            (slot.generation is None) == (slot.state in {FREE, PRODUCER})
            for slot in self.slots
        )
        latest = self.find(LATEST)
        leased = self.find(LEASED)
        if latest is not None and leased is not None:
            assert int(self.slots[latest].generation) > int(self.slots[leased].generation)

    def state_key(self) -> tuple[object, ...]:
        # Generation values are normalized relative to the current generation;
        # counters are excluded because they do not affect transitions.
        return tuple(
            (slot.state, None if slot.generation is None else self.generation - slot.generation)
            for slot in self.slots
        ) + (self.generation - self.consumer_generation,)


def run_scenarios(spec: dict[str, object]) -> list[dict[str, object]]:
    results = []
    for scenario in spec["scenarios"]:
        model = Model(spec["capacity"]["slot_count"])
        for operation in scenario["operations"]:
            model.operate(operation)
        actual_states = [slot.state for slot in model.slots]
        assert actual_states == scenario["expected_states"], scenario["id"]
        assert model.generation == scenario["expected_generation"], scenario["id"]
        assert model.producer_no_slot == scenario.get("expected_producer_no_slot", 0), scenario["id"]
        assert model.producer_busy == scenario.get("expected_producer_busy", 0), scenario["id"]
        results.append(
            {
                "id": scenario["id"],
                "states": actual_states,
                "generation": model.generation,
                "producer_no_slot": model.producer_no_slot,
                "producer_busy": model.producer_busy,
            }
        )
    return results


def exhaustive(spec: dict[str, object], depth: int) -> tuple[int, int]:
    operations = ["begin_produce", "publish", "cancel", "acquire_latest", "release"]
    initial = Model(spec["capacity"]["slot_count"])
    queue = deque([(initial, 0)])
    seen = {initial.state_key()}
    valid_transitions = 0
    while queue:
        model, level = queue.popleft()
        model.check()
        if level == depth:
            continue
        for operation in operations:
            candidate = model.clone()
            try:
                candidate.operate(operation)
            except ValueError:
                continue
            valid_transitions += 1
            key = candidate.state_key()
            if key not in seen:
                seen.add(key)
                queue.append((candidate, level + 1))
    return len(seen), valid_transitions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--depth", type=int, default=12)
    args = parser.parse_args()
    spec = yaml.safe_load(args.input.read_text(encoding="utf-8"))
    capacity = spec["capacity"]
    assert capacity["maximum_stride_bytes"] == capacity["maximum_width"] * capacity["bytes_per_pixel"]
    assert capacity["bytes_per_slot"] == capacity["maximum_stride_bytes"] * capacity["maximum_height"]
    assert capacity["total_pixel_bytes"] == capacity["bytes_per_slot"] * capacity["slot_count"]
    scenarios = run_scenarios(spec)
    states, transitions = exhaustive(spec, args.depth)
    output = {
        "schema_version": "1.0.0",
        "artifact_kind": "port_003_phase_f_snapshot_model_check",
        "generated_by": "docs/tasks/PORT-003/phase-f/scripts/check-snapshot-model.py",
        "oracle_independence": "no production source, header, or binary imported",
        "exhaustive_depth": args.depth,
        "normalized_states_checked": states,
        "valid_transitions_checked": transitions,
        "scenario_results": scenarios,
        "result": "pass",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(output, sort_keys=False), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
