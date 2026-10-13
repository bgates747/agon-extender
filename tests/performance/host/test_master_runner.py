import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("master", ROOT / "scripts/run_render_qualification.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MasterRunnerTests(unittest.TestCase):
    def plan(self, root):
        jobs = []
        for renderer in ("rgb888", "indexed"):
            for mode in m.MODES:
                for case in m.CASES:
                    for repeat in range(1, 4):
                        jobs.append(dict(id=f"{renderer}-{mode}-{case}-{repeat}",
                                         renderer=renderer, mode=mode, case=case, repeat=repeat,
                                         qualified_geometry=True,
                                         command=["fixture", "{receipt}"]))
        return dict(schema=1, ready=True, renderers=["rgb888", "indexed"],
                    jobs=jobs, cwd=str(root), inputs={str(Path(m.__file__)): m.sha(m.__file__)},
                    notification=dict(success=["green"], errors=["red"]))

    def exercise(self, failure=None, unsafe=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = self.plan(root)
            called = []

            def invoke(argv, log, cwd):
                log.write_text("mock adapter\n")
                called.append(argv)
                if argv[0] != "fixture":
                    return 0
                index = len(called) - 1
                job = plan["jobs"][index]
                receipt = {k: job[k] for k in ("id", "renderer", "mode", "case", "repeat")}
                receipt.update(validated=index != failure, bench_idle=not unsafe,
                               safe_to_continue=not unsafe)
                Path(argv[1]).write_text(json.dumps(receipt))
                return 1 if index == failure else 0

            out = root / "run"
            if unsafe:
                with self.assertRaises(RuntimeError):
                    m.run(plan, out, invoke)
            else:
                rc = m.run(plan, out, invoke)
                self.assertEqual(rc, 0 if failure is None else 1)
            summary = json.loads((out / "summary.json").read_text())
            if unsafe:
                self.assertEqual(summary["state"], "incomplete")
                self.assertEqual(len(called), 1)
            else:
                self.assertEqual(len(called), 241)
                self.assertEqual(called[-1], ["green" if failure is None else "red"])
                self.assertTrue(summary["all_jobs_finished"])
                self.assertEqual(summary["passed"], 240 if failure is None else 239)
                with self.assertRaises(FileExistsError):
                    m.run(plan, out, invoke)

    def test_complete_success(self):
        self.exercise()

    def test_recovered_failure_continues_and_reports_red(self):
        self.exercise(failure=7)

    def test_unknown_bench_state_stops_without_notification(self):
        self.exercise(unsafe=True)

    def test_missing_duplicate_or_unqualified_cases_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for mutation in (lambda p: p["jobs"].pop(),
                             lambda p: p["jobs"].append(p["jobs"][0]),
                             lambda p: p["jobs"][0].update(qualified_geometry=False),
                             lambda p: p.update(ready=False)):
                plan = self.plan(Path(tmp))
                mutation(plan)
                with self.assertRaises(ValueError):
                    m.validate_plan(plan)

    def test_display_commands_do_not_switch_modes_or_launch_programs(self):
        for success, color, text in ((True, 130, "ALL TESTS COMPLETE SUCCESS"),
                                     (False, 129, "TESTS COMPLETE WITH ERRORS")):
            data = m.banner(success).decode("ascii")
            self.assertTrue(data.startswith(f"VDU 17 {color}\r\nVDU 12\r\n"))
            self.assertNotIn("VDU 22", data)
            self.assertTrue(all(line.startswith("VDU ") for line in data.splitlines()))
            values = []
            for line in data.splitlines():
                nums = list(map(int, line.split()[1:]))
                if nums[0] >= 32:
                    values.extend(nums)
            self.assertEqual(bytes(values).decode("ascii"), text * 5)


if __name__ == "__main__":
    unittest.main()
