from __future__ import annotations

import copy
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "docs" / "qualification" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from qualification_model import build_matrix, dump_yaml, parse_vdu_inventory, validate_matrix  # noqa: E402


class QualificationModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.matrix = build_matrix()

    def errors_for(self, mutator) -> list[str]:
        candidate = copy.deepcopy(self.matrix)
        mutator(candidate)
        return validate_matrix(candidate)

    def test_canonical_model_is_valid(self) -> None:
        self.assertEqual([], validate_matrix(self.matrix))

    def test_exact_inventory_and_complete_mode_cross_product(self) -> None:
        self.assertEqual(211, len(parse_vdu_inventory()))
        self.assertEqual(211, len(self.matrix["interfaces"]))
        self.assertEqual(633, len(self.matrix["mode_expectations"]))
        self.assertEqual(25, len(self.matrix["obligations"]))

    def test_build_is_byte_deterministic(self) -> None:
        self.assertEqual(dump_yaml(build_matrix()), dump_yaml(build_matrix()))

    def test_duplicate_global_identity_is_rejected(self) -> None:
        errors = self.errors_for(lambda matrix: matrix["capabilities"].__setitem__(0, {**matrix["capabilities"][0], "id": matrix["interfaces"][0]["id"]}))
        self.assertTrue(any("duplicate global ID" in error for error in errors), errors)

    def test_missing_mode_tuple_is_rejected(self) -> None:
        errors = self.errors_for(lambda matrix: matrix["mode_expectations"].pop())
        self.assertTrue(any("missing 1 interface/mode expectations" in error for error in errors), errors)

    def test_blocked_without_blocker_is_rejected(self) -> None:
        def mutate(matrix):
            item = next(item for item in matrix["obligations"] if item["qualification_state"] == "blocked")
            item["blocker_refs"] = []

        errors = self.errors_for(mutate)
        self.assertTrue(any("blocked state requires blocker_refs" in error for error in errors), errors)

    def test_dangling_repository_reference_is_rejected(self) -> None:
        def mutate(matrix):
            matrix["obligations"][0]["owner_task_ids"] = ["GUIDED-MISSILE-001"]

        errors = self.errors_for(mutate)
        self.assertTrue(any("dangling repository reference GUIDED-MISSILE-001" in error for error in errors), errors)

    def test_secondary_evidence_cannot_support_compatibility(self) -> None:
        def mutate(matrix):
            evidence = matrix["evidence"][0]
            evidence["scope"] = "secondary-capability"

        errors = self.errors_for(mutate)
        self.assertTrue(any("evidence scope cannot satisfy obligation scope" in error for error in errors), errors)

    def test_qualified_requires_basis_and_accepted_support(self) -> None:
        def mutate(matrix):
            item = matrix["obligations"][0]
            item["qualification_state"] = "qualified"

        errors = self.errors_for(mutate)
        self.assertTrue(any("qualified state requires qualification_basis" in error for error in errors), errors)
        self.assertTrue(any("qualified state lacks accepted supporting evidence" in error for error in errors), errors)

    def test_tracked_generation_is_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPTS / "regenerate-qualification.py"), "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
