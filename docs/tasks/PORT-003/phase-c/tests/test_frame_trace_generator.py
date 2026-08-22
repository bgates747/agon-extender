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
            self.assertEqual(fixture["oracle_class"], "independent written-contract state model")
        self.assertEqual(
            self.data["fixture_set_sha256"],
            hashlib.sha256(canonical_yaml(self.data["fixtures"]).encode("utf-8")).hexdigest(),
        )

    def test_required_scenario_families_exist(self):
        required = {
            "sink-free-edge", "coalesced-three-ticks", "frame-counter-rollover",
            "writable-counter-continues", "dequeued-is-not-complete",
            "single-buffer-fifo-budget", "single-buffer-flush-next-edge",
            "double-immediate-and-swap", "slow-consumer-latest-only",
            "consumer-disconnect-reconnect", "tick-arrives-between-services",
            "stop-cancels-and-releases",
        }
        self.assertEqual(required, set(self.fixtures))

    def test_dequeued_wait_is_blocked_until_finish(self):
        results = [event["result"] for event in self.fixtures["dequeued-is-not-complete"]["expected_events"] if event["event"] == "wait-result"]
        self.assertEqual(results, ["blocked", "satisfied"])

    def test_swap_visibility_precedes_publication_and_completion(self):
        events = [event["event"] for event in self.fixtures["double-immediate-and-swap"]["expected_events"]]
        self.assertLess(events.index("planes-swapped"), events.index("published"))
        self.assertLess(events.index("published"), events.index("completed"))

    def test_slow_consumer_is_bounded_and_reports_drops(self):
        final = self.fixtures["slow-consumer-latest-only"]["expected_final"]
        self.assertIsNone(final["consumers"]["slow"]["slot"])
        self.assertEqual(final["consumers"]["slow"]["drops"], 2)

    def test_coalescing_accounts_time_but_publishes_once(self):
        final = self.fixtures["coalesced-three-ticks"]["expected_final"]
        self.assertEqual(final["frame_counter"], 3)
        self.assertEqual(final["generation"], 1)
        self.assertEqual(final["metrics"]["coalesced_ticks"], 2)


if __name__ == "__main__":
    unittest.main()
