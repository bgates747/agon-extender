from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("hw001_validate", ROOT / "validate.py")
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ElectricalModelValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.example_path = ROOT / "examples" / "topology-example.yaml"
        self.document = validator.load_yaml(self.example_path)

    def assert_model_error(self, document: dict) -> None:
        validator.validate_schema(document)
        with self.assertRaises(validator.ModelError):
            validator.validate_semantics(document)

    def test_example_passes(self) -> None:
        validated = validator.validate(self.example_path)
        self.assertFalse(validated["model"]["authority"])
        self.assertEqual(validated["model"]["status"], "illustrative")

    def test_unknown_terminal_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["nets"][0]["members"][0]["pin"] = "99"
        self.assert_model_error(document)

    def test_terminal_on_two_nets_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["nets"][1]["members"][0] = {"component": "C1", "pin": "2"}
        self.assert_model_error(document)

    def test_unaccounted_terminal_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["unconnected"].clear()
        self.assert_model_error(document)

    def test_duplicate_terminal_pin_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["components"][0]["terminals"][1]["pin"] = "1"
        self.assert_model_error(document)

    def test_noncanonical_net_order_is_rejected(self) -> None:
        document = copy.deepcopy(self.document)
        document["nets"][0], document["nets"][1] = document["nets"][1], document["nets"][0]
        self.assert_model_error(document)

    def test_polarized_component_requires_polarity_roles(self) -> None:
        document = copy.deepcopy(self.document)
        for terminal in document["components"][0]["terminals"]:
            terminal.pop("polarity_role")
        self.assert_model_error(document)


if __name__ == "__main__":
    unittest.main()
