"""Four-arm evidence/rate contracts; synthetic data is never a bench result."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from compare_rates import ARMS, load_campaign, markdown, summarize
from test_contract import csv_text, dumps, rows


def campaign(directory):
    spec = {"schema": 1, "direction": "ez80-to-p4", "parallel_format": 4, "arms": {}}
    for name, route in ARMS.items():
        records = rows(route)
        for r in records:
            # Deliberately distinct elapsed times and warm-up outliers.
            wire = r["wire_bytes"] // (32 if name == "P1" else 16)
            if r["repeat"] == 0:
                wire *= 10
            r.update(wire_prt=wire, submit_prt=wire // 2,
                     receipt_prt=wire if route == "excom" else wire + 5,
                     reply_prt=wire + 10)
        (directory / (name + ".csv")).write_text(csv_text(records))
        (directory / (name + ".log")).write_text(dumps(records))
        image = "1" if name.endswith("0") else "2"
        spec["arms"][name] = dict(route=route, emos_sha256=image * 64,
            fixture_sha256=image * 64, p4_sha256="3" * 64,
            environment_sha256="4" * 64, results=[name + ".csv"], captures=[name + ".log"])
    path = directory / "campaign.json"
    path.write_text(json.dumps(spec))
    return path, spec


class Rates(unittest.TestCase):
    def test_rates_and_independent_endpoint_tables(self):
        with tempfile.TemporaryDirectory() as d:
            path, _ = campaign(Path(d))
            loaded = load_campaign(path)
            result = summarize(loaded)
            self.assertEqual([r["wire_bytes"] for r in result], [8192, 4097, 4096, 256])
            for r in result:
                self.assertEqual(r["comparison"]["P1_vs_P0_drain_time_percent"], -50)
                self.assertEqual(r["comparison"]["P1_vs_P0_stream_rate_percent"], 100)
                self.assertEqual(r["comparison"]["P1_over_U1_stream_rate"], 2)
                m = r["variants"]["P1"]
                self.assertAlmostEqual(m["upload_bytes_per_second"]["median"] /
                    m["stream_bytes_per_second"]["median"], (r["wire_bytes"] - 11) / r["wire_bytes"])
            report = markdown(result)
            self.assertIn("Local parallel completion", report)
            self.assertIn("| 8192 | — |", report)
            self.assertEqual(sum(v["integrity"]["verified_bytes"] for v in loaded.values()), 96 * 8192)

    def test_reject_mixed_components_routes_and_reused_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            path, spec = campaign(Path(d))
            for field, value in (("p4_sha256", "5" * 64), ("environment_sha256", "5" * 64),
                                 ("emos_sha256", "5" * 64), ("fixture_sha256", "5" * 64),
                                 ("route", "excom"), ("results", ["U0.csv"])):
                changed = copy.deepcopy(spec)
                changed["arms"]["P1"][field] = value
                path.write_text(json.dumps(changed))
                with self.subTest(field=field), self.assertRaises(ValueError):
                    load_campaign(path)

    def test_reject_phase_timing_and_missing_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            path, _ = campaign(Path(d))
            csv = Path(d) / "P1.csv"
            original = csv.read_text()
            # Set the wire column directly rather than depend on formatting.
            import csv as csv_module
            r = list(csv_module.DictReader(original.splitlines()))
            r[0]["wire_prt"] = 0
            csv.write_text(csv_text(r))
            with self.assertRaises(ValueError):
                load_campaign(path)
            csv.write_text(original)
            log = Path(d) / "P1.log"
            log.write_text(log.read_text()[:-80])
            with self.assertRaises(ValueError):
                load_campaign(path)

    def test_reject_duplicate_missing_or_identical_arms(self):
        with tempfile.TemporaryDirectory() as d:
            path, spec = campaign(Path(d))
            for changed in (dict(spec, arms={k: v for k, v in spec["arms"].items() if k != "U1"}),
                            dict(spec, direction="p4-to-ez80")):
                path.write_text(json.dumps(changed))
                with self.assertRaises(ValueError):
                    load_campaign(path)
            for arm in ("U1", "P1"):
                spec["arms"][arm]["emos_sha256"] = "1" * 64
            path.write_text(json.dumps(spec))
            with self.assertRaises(ValueError):
                load_campaign(path)


if __name__ == "__main__":
    unittest.main()
