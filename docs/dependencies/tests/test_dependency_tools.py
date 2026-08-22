"""Regression tests for durable dependency and source-selection tooling."""

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
selection_builder = load_script_module("port002_selection_builder", "build-source-selection.py")
selection_projection = load_script_module(
    "port002_selection_projection", "project-source-selection.py"
)
validator = load_script_module("port001_validator", "validate-dependency-artifact.py")


class DependencyToolTests(unittest.TestCase):
    def test_generated_proof_slice_satisfies_formal_schema(self) -> None:
        schema = json.loads((TASK_ROOT / "schema/dependency-artifacts.schema.json").read_text())
        example = load_data(TASK_ROOT / "generated/commands/vdu-22.yaml")
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

    def test_schema_two_graph_has_unique_profile_subject_tuples(self) -> None:
        graph = load_data(TASK_ROOT / "generated/code-graph.yaml")
        tuples = [
            (record["build_profile_id"], record["subject_id"])
            for record in graph["selection_records"]
        ]
        self.assertEqual(len(tuples), len(set(tuples)))

    def test_reviewed_vdp_gl_patch_is_explicit_and_hash_distinct(self) -> None:
        graph = load_data(TASK_ROOT / "generated/code-graph.yaml")
        source = next(item for item in graph["sources"] if item["owner"] == "vdp-gl")
        self.assertEqual("vendored-patched", source["presence_class"])
        nodes = {node["id"]: node for node in graph["nodes"]}
        for path in ("src/displaycontroller.cpp", "src/displaycontroller.h"):
            properties = nodes[f"file:vdp-gl:{path}"]["properties"]
            self.assertEqual("PORT-003-D008", properties["source.patch_decision"])
            self.assertNotEqual(
                properties["source.sha256"], properties["source.repository_sha256"]
            )

    def test_six_case_port_002_proof_passes(self) -> None:
        proof_module = load_script_module("port002_proof", "verify-port-002-proof.py")
        report = proof_module.build_report(load_data(TASK_ROOT / "generated/code-graph.yaml"))
        self.assertEqual({"passed": 6, "failed": 0}, report["summary"])

    def test_new_upstream_file_defaults_to_unresolved(self) -> None:
        self.assertEqual(
            "unresolved",
            selection_builder.declared_target_status(
                "documentation", "not-applicable", [], True
            ),
        )

    def test_split_managed_import_maps_each_source_path_once(self) -> None:
        source = {
            "owner": "agon-vdp",
            "managed_import": {
                "mappings": [
                    {"source_prefix": "video/", "repository_path": "vdp/video/"},
                    {
                        "source_prefix": "",
                        "exclude_prefixes": ["video/"],
                        "repository_path": "vdp/vendor/agon-vdp-release/",
                    },
                ]
            },
        }
        repository = Path("/repository")
        self.assertEqual(
            repository / "vdp/video/agon_screen.h",
            selection_builder.managed_repository_path(
                repository, source, "video/agon_screen.h"
            ),
        )
        self.assertEqual(
            repository / "vdp/vendor/agon-vdp-release/platformio.ini",
            selection_builder.managed_repository_path(
                repository, source, "platformio.ini"
            ),
        )

    def test_projection_keeps_project_owned_build_boundaries_separate(self) -> None:
        graph = {
            "id": "graph:test:one",
            "build_profiles": [],
            "nodes": [
                {
                    "id": "build-unit:extender:canary",
                    "kind": "build-unit",
                    "owner": "extender",
                    "label": "Canary",
                    "evidence_ids": ["evidence:test:one"],
                    "properties": {
                        "project.path": "video/extender/canary.cpp",
                        "port.state": "diagnostic-canary",
                        "port.task": "PORT-003",
                    },
                }
            ],
            "selection_records": [],
        }
        projection = selection_projection.build_projection(graph)
        self.assertEqual(
            "build-unit:extender:canary",
            projection["project_boundaries"][0]["id"],
        )
        self.assertEqual([], projection["subjects"])

    def test_merge_attention_keeps_isolated_unselected_change(self) -> None:
        merge_module = load_script_module("merge_attention", "compare-tagged-releases.py")
        old = {
            "id": "graph:test:old",
            "nodes": [{"id": "file:test:README.md", "kind": "file", "owner": "test", "properties": {"source.path": "README.md", "source.sha256": "0" * 64, "source.role": "documentation"}}],
            "edges": [],
            "selection_records": [{"build_profile_id": "build-profile:extender:p4-default", "subject_id": "file:test:README.md", "status": "not-applicable"}],
        }
        new = {
            **old,
            "id": "graph:test:new",
            "nodes": [{**old["nodes"][0], "properties": {**old["nodes"][0]["properties"], "source.sha256": "1" * 64}}],
        }
        result = merge_module.compare(old, new, "build-profile:extender:p4-default")
        self.assertEqual(1, result["summary"]["changed_file_count"])
        self.assertEqual("D", result["changes"][0]["tier"])


if __name__ == "__main__":
    unittest.main()
