"""Focused regression tests for PORT-001 graph invariants and lexical safety."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


TASK_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = TASK_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from dependency_model import canonical_yaml, edge_id, load_data  # noqa: E402


def load_script_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_script_module("port001_builder", "build-code-graph.py")
validator = load_script_module("port001_validator", "validate-dependency-artifact.py")


class DependencyToolTests(unittest.TestCase):
    def test_review_example_satisfies_formal_schema(self) -> None:
        schema = json.loads((TASK_ROOT / "schema/dependency-artifacts.schema.json").read_text())
        example = load_data(TASK_ROOT / "schema/examples/representative-slice.yaml")
        Draft202012Validator.check_schema(schema)
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(example)))

    def test_canonical_yaml_disables_aliases_and_is_stable(self) -> None:
        shared = {"id": "value"}
        first = canonical_yaml({"left": shared, "right": shared})
        second = canonical_yaml(yaml.safe_load(first))
        self.assertNotIn("&id", first)
        self.assertEqual(first, second)

    def test_edge_identity_is_tuple_deterministic(self) -> None:
        first = edge_id("function:owner:a()", "calls", "function:owner:b()")
        second = edge_id("function:owner:a()", "calls", "function:owner:b()")
        changed = edge_id("function:owner:a()", "reads", "function:owner:b()")
        self.assertEqual(first, second)
        self.assertNotEqual(first, changed)

    def test_duplicate_values_reports_each_duplicate_once(self) -> None:
        self.assertEqual(["a", "b"], validator.duplicate_values(["a", "b", "a", "b", "b"]))

    def test_member_access_is_not_bare_name_resolved(self) -> None:
        text = "controller->get()"
        self.assertTrue(builder.is_member_access(text, text.index("get")))

    def test_unqualified_resolution_never_crosses_owner(self) -> None:
        candidate = "function:other:run()"
        metadata = {candidate: {"owner": "other", "name": "run"}}
        caller = {"owner": "project", "name": "caller"}
        self.assertEqual([], builder.resolve_unqualified_call(caller, [candidate], metadata))


if __name__ == "__main__":
    unittest.main()
