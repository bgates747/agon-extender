"""Regression tests for the durable hardware-object authority validator."""

from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_PATH = REPOSITORY_ROOT / "scripts/validate-hardware-objects.py"


def load_validator():
    spec = importlib.util.spec_from_file_location(
        "hardware_object_validator", VALIDATOR_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class HardwareObjectValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.record = validator.load_yaml(validator.OBJECTS_PATH)
        self.objects = self.record["objects"]

    def test_authority_satisfies_schema_and_semantic_checks(self) -> None:
        validator.validate_schema(self.record, validator.load_schema())
        validator.validate_authority_identity(self.record)
        by_id = validator.validate_unique_and_ordered(self.objects)
        validator.validate_containment(by_id)
        validator.validate_artifact_references(self.objects)
        self.assertEqual(41, len(by_id))

    def test_duplicate_object_id_is_rejected(self) -> None:
        objects = copy.deepcopy(self.objects)
        objects.insert(1, copy.deepcopy(objects[0]))
        with self.assertRaisesRegex(ValueError, "duplicate object_id"):
            validator.validate_unique_and_ordered(objects)

    def test_case_insensitive_duplicate_alias_is_rejected(self) -> None:
        objects = copy.deepcopy(self.objects)
        objects[0]["aliases"].append(objects[0]["aliases"][0].upper())
        with self.assertRaisesRegex(ValueError, "case-insensitive duplicate alias"):
            validator.validate_unique_and_ordered(objects)

    def test_unknown_parent_is_rejected(self) -> None:
        objects = copy.deepcopy(self.objects)
        objects[0]["parent_object_id"] = "missing-parent"
        by_id = {item["object_id"]: item for item in objects}
        with self.assertRaisesRegex(ValueError, "unknown parent_object_id"):
            validator.validate_containment(by_id)

    def test_containment_cycle_is_rejected(self) -> None:
        objects = copy.deepcopy(self.objects)
        first = objects[0]
        second = objects[1]
        first["parent_object_id"] = second["object_id"]
        second["parent_object_id"] = first["object_id"]
        by_id = {item["object_id"]: item for item in objects}
        with self.assertRaisesRegex(ValueError, "containment cycle"):
            validator.validate_containment(by_id)

    def test_unknown_artifact_reference_is_rejected(self) -> None:
        objects = copy.deepcopy(self.objects)
        objects[0]["related_artifact_ids"] = ["missing-artifact"]
        with self.assertRaisesRegex(ValueError, "unknown artifact_id"):
            validator.validate_artifact_references(objects)


if __name__ == "__main__":
    unittest.main()
