import hashlib
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import canonical_yaml, load_data  # noqa: E402


class FrameTraceFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data(ROOT / "docs/tasks/PORT-003/phase-c/fixtures/frame-traces.yaml")
        cls.fixtures = {item["id"]: item for item in cls.data["fixtures"]}

    def test_hashes_and_independent_oracle_metadata(self):
        for fixture in self.fixtures.values():
            expected = fixture["content_sha256"]
            payload = dict(fixture)
            del payload["content_sha256"]
            self.assertEqual(expected, hashlib.sha256(canonical_yaml(payload).encode("utf-8")).hexdigest())
            self.assertEqual(fixture["oracle_class"], "independent upstream-derived contract state model")
        self.assertEqual(
            self.data["fixture_set_sha256"],
            hashlib.sha256(canonical_yaml(self.data["fixtures"]).encode("utf-8")).hexdigest(),
        )

    def test_required_scenario_families_exist(self):
        required = {
            "sink-free-edge", "three-distinct-frame-edges", "frame-counter-rollover",
            "writable-counter-continues", "dequeued-satisfies-upstream-queue-wait",
            "single-buffer-fifo-budget", "single-buffer-flush-next-edge",
            "double-immediate-and-swap", "slow-consumer-latest-only",
            "consumer-disconnect-reconnect", "tick-arrives-between-services",
            "stop-drains-and-releases",
        }
        self.assertEqual(required, set(self.fixtures))

    def test_dequeued_item_satisfies_upstream_queue_depth_wait(self):
        results = [event["result"] for event in self.fixtures["dequeued-satisfies-upstream-queue-wait"]["expected_events"] if event["event"] == "wait-result"]
        self.assertEqual(results, ["satisfied", "satisfied"])

    def test_swap_completion_precedes_publication(self):
        events = [event["event"] for event in self.fixtures["double-immediate-and-swap"]["expected_events"]]
        self.assertLess(events.index("planes-swapped"), events.index("published"))
        self.assertLess(events.index("completed"), events.index("published"))

    def test_slow_consumer_is_bounded_and_reports_drops(self):
        final = self.fixtures["slow-consumer-latest-only"]["expected_final"]
        self.assertIsNone(final["consumers"]["slow"]["slot"])
        self.assertEqual(final["consumers"]["slow"]["drops"], 2)

    def test_each_tick_produces_a_distinct_edge(self):
        final = self.fixtures["three-distinct-frame-edges"]["expected_final"]
        self.assertEqual(final["frame_counter"], 3)
        self.assertEqual(final["generation"], 3)
        self.assertEqual(final["metrics"]["serviced_edges"], 3)


if __name__ == "__main__":
    unittest.main()
