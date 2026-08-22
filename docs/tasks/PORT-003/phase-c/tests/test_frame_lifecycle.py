from pathlib import Path
import importlib.util
import sys
import unittest


ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "docs/dependencies/scripts"))
from dependency_model import load_data, sha256_file  # noqa: E402


ARTIFACT = ROOT / "docs/tasks/PORT-003/phase-c/evidence/frame-lifecycle.yaml"


class FrameLifecycleArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data(ARTIFACT)

    def test_identity_tuples_are_unique(self):
        keys = [
            (item["owner"], item["span"]["path"], item["span"]["start_line"], item["symbol"])
            for item in self.data["records"]
        ]
        self.assertEqual(len(keys), len(set(keys)))

    def test_all_source_and_span_hashes_match(self):
        roots = {"agon-vdp": ROOT / "vdp", "vdp-gl": ROOT / "vdp/vendor/vdp-gl"}
        for item in self.data["sources"]:
            self.assertEqual(item["sha256"], sha256_file(roots[item["owner"]] / item["path"]))
        for item in self.data["records"]:
            span = item["span"]
            lines = (roots[item["owner"]] / span["path"]).read_bytes().splitlines(keepends=True)
            payload = b"".join(lines[span["start_line"] - 1:span["end_line"]])
            import hashlib
            self.assertEqual(span["span_sha256"], hashlib.sha256(payload).hexdigest())

    def test_critical_contract_and_exclusion_records_exist(self):
        by_symbol = {}
        for item in self.data["records"]:
            by_symbol.setdefault(item["symbol"], set()).add(item["disposition"])
        self.assertIn("adapt-common-sequence", by_symbol["primitivesExecutionWait"])
        self.assertIn("adapt-common-sequence", by_symbol["addPrimitive"])
        self.assertIn("adapt-logical-swap", by_symbol["swapBuffers"])
        self.assertIn("exclude-physical-trigger", by_symbol["VSyncInterrupt"])
        self.assertIn("retain-facade-contract", by_symbol["checkForVSYNC"])

    def test_findings_make_queue_race_and_override_limit_explicit(self):
        findings = self.data["findings"]
        self.assertIn("dequeued", findings["queue_empty_race"])
        self.assertIn("non-virtual", findings["derived_override_limit"])


if __name__ == "__main__":
    unittest.main()
