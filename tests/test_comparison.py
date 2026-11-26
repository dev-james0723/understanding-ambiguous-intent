"""Check comparison input integrity and public fixture separation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from compare_results import JUDGMENT_FLAGS, compare_results
from evaluate import read_cases


def response(sample, condition, case="demo", **fields):
    return {"sample_id": sample, "id": case, "condition": condition,
            "status": "ok", "response": "Draft – café\u2028next line\n", **fields}


def judgment(record, **fields):
    review = dict.fromkeys(JUDGMENT_FLAGS, False)
    review.update(sample_id=record["sample_id"], passed=True, rationale="Reviewed")
    review["response_sha256"] = hashlib.sha256(record["response"].encode("utf-8")).hexdigest()
    return {**review, **fields}


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


class ComparisonTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.responses = Path(work.name, "responses.jsonl")
        self.judgments = Path(work.name, "judgments.jsonl")
        self.grid = Path(work.name, "grid.json")
        self.baseline = response("baseline-1", "baseline", provenance={"model": "unknown"})
        self.candidate = response("uai-1", "uai", trial=1)
        self.plan = {"conditions": ["baseline", "uai"], "case_ids": ["demo"], "trials": [1]}

    def compare(self, responses, judgments, plan=None):
        write_jsonl(self.responses, responses)
        write_jsonl(self.judgments, judgments)
        if plan is not None:
            self.grid.write_text(json.dumps(plan), encoding="utf-8")
        return compare_results(self.responses, self.judgments, self.grid if plan is not None else None)

    def test_cli_help_describes_separately_supplied_judgments(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/compare_results.py"), "--help"],
                                capture_output=True, text=True, check=True)
        self.assertIn("separately supplied judgments", " ".join(result.stdout.split()))

    def test_counts_distinguish_ties_regressions_and_infrastructure(self):
        baseline = [self.baseline] + [response(f"baseline-{n}", "baseline", trial=n)
                                      for n in range(2, 6)]
        candidate = [self.candidate] + [response(f"uai-{n}", "uai", trial=n) for n in range(2, 5)]
        candidate.append({"sample_id": "uai-5", "condition": "uai", "id": "demo", "trial": 5,
                          "status": "timeout"})
        report = self.compare(baseline + candidate, [
            judgment(baseline[0]), judgment(baseline[1]), judgment(baseline[2], passed=False),
            judgment(baseline[3], passed=False), judgment(baseline[4]),
            judgment(candidate[0], unnecessary_question=True),
            judgment(candidate[1], passed=False, missed_necessary_question=True),
            judgment(candidate[2], passed=False, critical_failure=True), judgment(candidate[3]),
        ])
        self.assertEqual(report["coverage"], "observed-only")
        self.assertEqual(report["conditions"]["uai"], {
            "recorded": 5, "successful": 4, "infrastructure_errors": 1,
            "infrastructure_by_status": {"timeout": 1}, "judged": 4, "passes": 2,
            "behavior_failures": 2, "unnecessary_questions": 1,
            "missed_necessary_questions": 1, "critical_failures": 1,
        })
        case = report["vs_baseline"]["uai"]["demo"]
        self.assertEqual({key: value for key, value in case.items() if key != "trials"}, {
            "recorded_pairs": 5, "comparable_pairs": 4, "infrastructure_pairs": 1,
            "ties": 2, "improvements": 1, "regressions": 1, "new_critical_failures": 1,
        })
        self.assertEqual([trial["outcome"] for trial in case["trials"]], [
            "tie_pass", "regression", "tie_fail", "improvement", "infrastructure_error",
        ])
        self.assertTrue(case["trials"][2]["new_critical_failure"])
        self.assertEqual(case["trials"][-1]["status"], "timeout")

    def test_baseline_error_leaves_successful_comparator_unpaired(self):
        failed_baseline = {**self.baseline, "status": "provider-error"}
        report = self.compare([failed_baseline, self.candidate], [judgment(self.candidate)])
        self.assertEqual(report["conditions"]["baseline"]["judged"], 0)
        self.assertEqual(report["conditions"]["uai"]["passes"], 1)
        case = report["vs_baseline"]["uai"]["demo"]
        self.assertEqual(case["comparable_pairs"], 0)
        self.assertEqual(case["infrastructure_pairs"], 1)

    def test_all_infrastructure_errors_are_not_ties_or_passes(self):
        report = self.compare([{**self.baseline, "status": "missing"},
                               {**self.candidate, "status": "runner-error"}], [])
        self.assertEqual(report["conditions"]["uai"]["passes"], 0)
        self.assertEqual(report["conditions"]["uai"]["behavior_failures"], 0)
        case = report["vs_baseline"]["uai"]["demo"]
        self.assertEqual(case["ties"], 0)
        self.assertEqual(case["infrastructure_pairs"], 1)

    def test_requires_baseline(self):
        with self.assertRaisesRegex(ValueError, "must include a baseline condition"):
            self.compare([self.candidate], [judgment(self.candidate)])

    def test_rejects_baseline_only_observed_report(self):
        with self.assertRaisesRegex(ValueError, "must include a candidate condition"):
            self.compare([self.baseline], [judgment(self.baseline)])

    def test_expected_grid_rejects_an_absent_candidate(self):
        plan = {**self.plan, "conditions": ["baseline", "brief", "uai"]}
        with self.assertRaisesRegex(ValueError, r"missing \[\('brief', 'demo', 1\)\]"):
            self.compare([self.baseline, self.candidate], [], plan)

    def test_expected_grid_rejects_a_case_omitted_in_all_conditions(self):
        plan = {**self.plan, "case_ids": ["demo", "missing-case"]}
        with self.assertRaisesRegex(ValueError, "missing .*'baseline', 'missing-case'.*'uai', 'missing-case'"):
            self.compare([self.baseline, self.candidate], [], plan)

    def test_expected_grid_rejects_extra_slots(self):
        records = [self.baseline, self.candidate, response("baseline-2", "baseline", trial=2),
                   response("uai-2", "uai", trial=2)]
        with self.assertRaisesRegex(ValueError, "extra .*'baseline', 'demo', 2.*'uai', 'demo', 2"):
            self.compare(records, [], self.plan)

    def test_expected_grid_checks_case_and_trial_cross_product(self):
        plan = {**self.plan, "case_ids": ["demo", "other"], "trials": [1, 2]}
        records = [response(f"{condition}-{case}-{trial}", condition, case, trial=trial)
                   for condition in plan["conditions"] for case in plan["case_ids"] for trial in plan["trials"]]
        records[-1]["status"] = "missing"
        del records[-1]["response"]
        report = self.compare(records, [judgment(record) for record in records[:-1]], plan)
        self.assertEqual(report["coverage"], "expected-grid")
        self.assertEqual(report["conditions"]["uai"]["recorded"], 4)
        self.assertEqual(report["conditions"]["uai"]["infrastructure_by_status"], {"missing": 1})
        self.assertEqual(report["conditions"]["uai"]["passes"], 3)
        self.assertEqual(report["vs_baseline"]["uai"]["other"]["comparable_pairs"], 1)
        self.assertEqual(report["vs_baseline"]["uai"]["other"]["trials"][-1]["outcome"], "infrastructure_error")

    def test_rejects_invalid_expected_grid_values(self):
        for fields, error in [({"trials": [True]}, "invalid expected grid trials"),
                              ({"case_ids": ["demo", "demo"]}, "duplicate expected grid case_ids"),
                              ({"conditions": ["baseline"]}, "must include baseline and a candidate"),
                              ({"conditions": ["brief", "uai"]}, "must include baseline and a candidate"),
                              ({"case_ids": []}, "invalid expected grid case_ids")]:
            with self.subTest(fields=fields), self.assertRaisesRegex(ValueError, error):
                self.compare([self.baseline, self.candidate], [], {**self.plan, **fields})

    def test_rejects_duplicate_samples_and_duplicate_condition_slots(self):
        for changed, error in [
            ({**self.candidate, "sample_id": "baseline-1"}, "duplicate response sample_id"),
            ({**self.candidate, "condition": "baseline"}, "duplicate condition/id/trial"),
        ]:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                self.compare([self.baseline, changed], [])

    def test_rejects_grid_mismatch_even_with_equal_row_counts(self):
        for field, value in [("trial", 2), ("id", "different-case")]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "grid differs from baseline"):
                self.compare([self.baseline, {**self.candidate, field: value}], [])

    def test_rejects_invalid_response_record_fields(self):
        for fields, error in [({"trial": True}, "trial must be a positive integer"),
                              ({"trial": 0}, "trial must be a positive integer"),
                              ({"sample_id": ""}, "sample_id must be a nonempty string"),
                              ({"status": None}, "status must be a nonempty string"),
                              ({"response": " "}, "response must be a nonempty string")]:
            with self.subTest(fields=fields), self.assertRaisesRegex(ValueError, error):
                self.compare([self.baseline, {**self.candidate, **fields}], [])

    def test_rejects_missing_unknown_and_duplicate_judgments(self):
        base = judgment(self.baseline)
        candidate = judgment(self.candidate)
        for records, error in [([base], "Missing judgments.*uai-1"),
                               ([base, base, candidate], "duplicate judgment sample_id"),
                               ([base, {**candidate, "sample_id": "elsewhere"}], "unknown judgment sample_id")]:
            with self.subTest(error=error), self.assertRaisesRegex(ValueError, error):
                self.compare([self.baseline, self.candidate], records)

    def test_rejects_stale_hash_when_only_trailing_whitespace_changes(self):
        new_response = {**self.candidate, "response": self.candidate["response"].rstrip()}
        with self.assertRaisesRegex(ValueError, "response_sha256 mismatch for 'uai-1'"):
            self.compare([self.baseline, new_response], [judgment(self.baseline), judgment(self.candidate)])

    def test_rejects_invalid_boolean_flags_and_missing_rationale(self):
        for flag in JUDGMENT_FLAGS:
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, f"{flag} must be a Boolean"):
                self.compare([self.baseline, self.candidate],
                             [judgment(self.baseline), judgment(self.candidate, **{flag: 1})])
        with self.assertRaisesRegex(ValueError, "rationale must be a string"):
            self.compare([self.baseline, self.candidate],
                         [judgment(self.baseline), judgment(self.candidate, rationale=None)])

    def test_rejects_passing_judgments_with_disqualifying_flags(self):
        for flag in ("critical_failure", "missed_necessary_question"):
            with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, f"passed cannot be true when {flag} is true"):
                self.compare([self.baseline, self.candidate],
                             [judgment(self.baseline, passed=False), judgment(self.candidate, **{flag: True})])

    def test_rejects_a_judgment_on_an_unsuccessful_response(self):
        with self.assertRaisesRegex(ValueError, "judgment for unsuccessful response"):
            self.compare([self.baseline, {**self.candidate, "status": "timeout"}],
                         [judgment(self.baseline), judgment(self.candidate)])

    def test_cli_writes_report_and_exits_nonzero_on_invalid_input(self):
        expected = self.compare([self.baseline, self.candidate],
                                [judgment(self.baseline), judgment(self.candidate)], self.plan)
        out = self.responses.with_name("report.json")
        command = [sys.executable, str(ROOT / "scripts/compare_results.py"),
                   "--responses", str(self.responses), "--judgments", str(self.judgments),
                   "--expected-grid", str(self.grid)]
        result = subprocess.run(command + ["--out", str(out)], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8")), expected)

        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), expected)

        write_jsonl(self.judgments, [judgment(self.baseline)])
        failure = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(failure.returncode, 0)
        self.assertIn("Missing judgments", failure.stderr)
        self.assertEqual(failure.stdout, "")


class FixtureTests(unittest.TestCase):
    def read_rubrics(self, name):
        return [json.loads(line) for line in (ROOT / "evals" / name).read_text(encoding="utf-8").splitlines()]

    def test_boundary_pairs_have_matching_separate_rubrics(self):
        cases = read_cases(ROOT / "evals/boundary-cases.jsonl", "dev")
        rubrics = self.read_rubrics("boundary-rubrics.jsonl")
        self.assertEqual(sorted(case["id"] for case in cases), sorted(rubric["id"] for rubric in rubrics))
        categories = {case["category"] for case in cases}
        self.assertEqual(len(categories), 8)
        for category in categories:
            pair = [case["messages"] for case in cases if case["category"] == category]
            self.assertEqual(len(pair), 2)
            self.assertEqual(pair[0][:-1], pair[1][:-1])
            self.assertNotEqual(pair[0][-1], pair[1][-1])

    def test_trajectories_have_only_user_turns_and_separate_turn_rubrics(self):
        cases = read_cases(ROOT / "evals/trajectories.jsonl", "dev")
        self.assertEqual(len(cases), 4)
        expected = []
        for case in cases:
            self.assertGreaterEqual(len(case["messages"]), 3)
            for turn, message in enumerate(case["messages"], 1):
                self.assertEqual(message["role"], "user")
                expected.append((case["id"], turn))
        rubrics = self.read_rubrics("trajectory-rubrics.jsonl")
        self.assertEqual(sorted(expected), sorted((rubric["id"], rubric["turn"]) for rubric in rubrics))
