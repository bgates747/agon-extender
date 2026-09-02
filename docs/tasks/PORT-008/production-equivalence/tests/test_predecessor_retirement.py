"""Fail-closed guards for rejected PORT-008 predecessor entry points."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[5]
FORWARD_ROOT = ROOT / "docs/tasks/PORT-008/forward-r01"


class PredecessorRetirementTests(unittest.TestCase):
    def test_candidate_lifecycle_is_machine_readable(self) -> None:
        candidate = yaml.safe_load(
            (FORWARD_ROOT / "candidate.yaml").read_text(encoding="utf-8")
        )
        self.assertEqual(candidate["status"], "rejected")
        self.assertEqual(candidate["historical_status"], "candidate-input")
        self.assertIs(candidate["retired"], True)
        self.assertIn("production-equivalence", candidate["superseded_by"])

    def test_historical_entry_points_fail_before_argument_processing(self) -> None:
        for name in (
            "stage-forward-build.py",
            "stage-emos-build.py",
            "validate-forward-build.py",
            "capture-visible-frame.py",
        ):
            with self.subTest(script=name):
                completed = subprocess.run(
                    [sys.executable, "-B", str(FORWARD_ROOT / "scripts" / name)],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    check=False,
                    timeout=10,
                )
                self.assertEqual(completed.returncode, 2)
                self.assertEqual(completed.stdout, "")
                self.assertIn("rejected and superseded", completed.stderr)
                self.assertNotIn("usage:", completed.stderr)

    def test_retired_pio_selectors_are_rejected_before_source_rendering(self) -> None:
        for name in (
            "p4-forward-vdp-source-selection.json",
            "p4-zdi-probe-source-selection.json",
            "p4-zdi-mos-recovery-source-selection.json",
        ):
            with self.subTest(selector=name):
                selection = json.loads(
                    (ROOT / "vdp/pio" / name).read_text(encoding="utf-8")
                )
                self.assertIs(selection["retired"], True)
                disposition = selection["diagnostic_status"].lower()
                self.assertIn("historical", disposition)
                self.assertTrue(
                    "rejected" in disposition or "retired" in disposition
                )

        hook = (ROOT / "vdp/pio/select_sources.py").read_text(encoding="utf-8")
        self.assertLess(
            hook.index('selection.get("retired") is True'),
            hook.index('project_translation_units = selection['),
        )

    def test_retired_zdi_payload_generator_fails_before_arguments(self) -> None:
        generator = (
            ROOT
            / "docs/tasks/PORT-008/emos-hardware-diagnostic/"
            "generate-recovery-payload.py"
        )
        completed = subprocess.run(
            [sys.executable, "-B", str(generator)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=10,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "")
        self.assertIn("retired", completed.stderr)
        self.assertNotIn("usage:", completed.stderr)

        for name in ("p4_zdi_probe.cpp", "p4_zdi_mos_recovery.cpp"):
            source = (
                ROOT / "vdp/video/extender/diagnostic" / name
            ).read_text(encoding="utf-8")
            self.assertIn("RETIRED PORT-008", source[:300])


if __name__ == "__main__":
    unittest.main()
