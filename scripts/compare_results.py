#!/usr/bin/env python3
"""Compare matched response trials using separately supplied judgments. Runs offline."""
import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import product
import json
from pathlib import Path


JUDGMENT_FLAGS = (
    "passed", "unnecessary_question", "missed_necessary_question", "critical_failure",
)


def read_records(path):
    with Path(path).open(encoding="utf-8") as source:
        for number, line in enumerate(source, 1):
            if not line.strip():
                continue
            location = f"{path}:{number}"
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{location}: invalid JSON ({exc.msg})") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{location}: expected an object")
            yield location, record


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def positive_trial(value):
    return type(value) is int and value > 0


def require_text(record, field, location):
    value = record.get(field)
    if not nonempty_text(value):
        raise ValueError(f"{location}: {field} must be a nonempty string")
    return value


def load_responses(path):
    samples = {}
    conditions = defaultdict(dict)
    for location, response in read_records(path):
        sample = require_text(response, "sample_id", location)
        case = require_text(response, "id", location)
        condition = require_text(response, "condition", location)
        status = require_text(response, "status", location)
        trial = response.get("trial", 1)
        if not positive_trial(trial):
            raise ValueError(f"{location}: trial must be a positive integer")
        if status == "ok":
            require_text(response, "response", location)
        if sample in samples:
            raise ValueError(f"{location}: duplicate response sample_id {sample!r}")
        key = case, trial
        if key in conditions[condition]:
            raise ValueError(f"{location}: duplicate condition/id/trial {condition!r}, {key!r}")
        samples[sample] = response
        conditions[condition][key] = response
    return samples, conditions


def load_expected_grid(path):
    with Path(path).open(encoding="utf-8") as source:
        plan = json.load(source)
    fields = {"conditions": nonempty_text, "case_ids": nonempty_text, "trials": positive_trial}
    if not isinstance(plan, dict) or plan.keys() != fields.keys():
        raise ValueError(f"{path}: expected a grid object with conditions, case_ids, and trials")
    for field, validate_value in fields.items():
        values = plan[field]
        if not isinstance(values, list) or not values or not all(map(validate_value, values)):
            raise ValueError(f"{path}: invalid expected grid {field} values")
        if len(set(values)) != len(values):
            raise ValueError(f"{path}: duplicate expected grid {field} values")
    if "baseline" not in plan["conditions"] or len(plan["conditions"]) < 2:
        raise ValueError(f"{path}: expected grid must include baseline and a candidate condition")
    return set(product(plan["conditions"], plan["case_ids"], plan["trials"]))


def validate_coverage(conditions, expected_grid_path):
    if expected_grid_path is not None:
        expected = load_expected_grid(expected_grid_path)
        recorded = {(condition, case, trial) for condition, responses in conditions.items()
                    for case, trial in responses}
        missing = sorted(expected - recorded)
        extra = sorted(recorded - expected)
        if missing or extra:
            raise ValueError(f"Recorded condition/id/trial slots differ from expected grid: "
                             f"missing {missing!r}; extra {extra!r}")
        return "expected-grid"
    if "baseline" not in conditions:
        raise ValueError("Responses must include a baseline condition")
    if len(conditions) < 2:
        raise ValueError("Responses must include a candidate condition alongside baseline")
    baseline_grid = conditions["baseline"].keys()
    for condition, responses in conditions.items():
        missing = sorted(baseline_grid - responses.keys())
        extra = sorted(responses.keys() - baseline_grid)
        if missing or extra:
            raise ValueError(f"{condition!r} case/trial grid differs from baseline: "
                             f"missing {missing!r}; extra {extra!r}")
    return "observed-only"


def load_judgments(path, samples):
    judgments = {}
    for location, judgment in read_records(path):
        sample = require_text(judgment, "sample_id", location)
        if sample in judgments:
            raise ValueError(f"{location}: duplicate judgment sample_id {sample!r}")
        if sample not in samples:
            raise ValueError(f"{location}: unknown judgment sample_id {sample!r}")
        response = samples[sample]
        if response["status"] != "ok":
            raise ValueError(f"{location}: judgment for unsuccessful response {sample!r}")
        expected = hashlib.sha256(response["response"].encode("utf-8")).hexdigest()
        if judgment.get("response_sha256") != expected:
            raise ValueError(f"{location}: response_sha256 mismatch for {sample!r}")
        for field in JUDGMENT_FLAGS:
            if type(judgment.get(field)) is not bool:
                raise ValueError(f"{location}: {field} must be a Boolean")
        for field in ("critical_failure", "missed_necessary_question"):
            if judgment["passed"] and judgment[field]:
                raise ValueError(f"{location}: passed cannot be true when {field} is true")
        if not isinstance(judgment.get("rationale"), str):
            raise ValueError(f"{location}: rationale must be a string")
        judgments[sample] = judgment

    missing = sorted(sample for sample, response in samples.items()
                     if response["status"] == "ok" and sample not in judgments)
    if missing:
        raise ValueError(f"Missing judgments for successful samples: {missing!r}")
    return judgments


def summarize_condition(responses, judgments):
    statuses = Counter(record["status"] for record in responses.values())
    successful = statuses.pop("ok", 0)
    reviewed = [judgments[record["sample_id"]] for record in responses.values()
                if record["status"] == "ok"]
    passes = sum(review["passed"] for review in reviewed)
    return {
        "recorded": len(responses),
        "successful": successful,
        "infrastructure_errors": len(responses) - successful,
        "infrastructure_by_status": dict(statuses),
        "judged": len(reviewed),
        "passes": passes,
        "behavior_failures": len(reviewed) - passes,
        "unnecessary_questions": sum(review["unnecessary_question"] for review in reviewed),
        "missed_necessary_questions": sum(review["missed_necessary_question"] for review in reviewed),
        "critical_failures": sum(review["critical_failure"] for review in reviewed),
    }


def compare_trial(trial, baseline, candidate, judgments):
    baseline_id = baseline["sample_id"]
    candidate_id = candidate["sample_id"]
    result = {
        "trial": trial,
        "baseline_sample_id": baseline_id,
        "sample_id": candidate_id,
        "baseline_status": baseline["status"],
        "status": candidate["status"],
    }
    if baseline["status"] != "ok" or candidate["status"] != "ok":
        return {**result, "outcome": "infrastructure_error"}
    before, after = judgments[baseline_id], judgments[candidate_id]
    if before["passed"] == after["passed"]:
        outcome = "tie_pass" if after["passed"] else "tie_fail"
    else:
        outcome = "improvement" if after["passed"] else "regression"
    return {**result, "outcome": outcome,
            "new_critical_failure": after["critical_failure"] and not before["critical_failure"]}


def compare_condition(baseline, candidate, judgments):
    cases = defaultdict(list)
    for case, trial in sorted(baseline):
        key = case, trial
        cases[case].append(compare_trial(trial, baseline[key], candidate[key], judgments))

    summaries = {}
    for case, trials in cases.items():
        counts = Counter(result["outcome"] for result in trials)
        errors = counts["infrastructure_error"]
        summaries[case] = {
            "recorded_pairs": len(trials),
            "comparable_pairs": len(trials) - errors,
            "infrastructure_pairs": errors,
            "ties": counts["tie_pass"] + counts["tie_fail"],
            "improvements": counts["improvement"],
            "regressions": counts["regression"],
            "new_critical_failures": sum(result.get("new_critical_failure", False) for result in trials),
            "trials": trials,
        }
    return summaries


def compare_results(responses_path, judgments_path, expected_grid_path=None):
    samples, conditions = load_responses(responses_path)
    coverage = validate_coverage(conditions, expected_grid_path)
    judgments = load_judgments(judgments_path, samples)
    baseline = conditions["baseline"]
    return {
        "coverage": coverage,
        "conditions": {condition: summarize_condition(responses, judgments)
                       for condition, responses in conditions.items()},
        "vs_baseline": {condition: compare_condition(baseline, responses, judgments)
                        for condition, responses in conditions.items() if condition != "baseline"},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--responses", type=Path, required=True, help="Response records in JSONL")
    parser.add_argument("--judgments", type=Path, required=True, help="Independent judgments in JSONL")
    parser.add_argument("--expected-grid", type=Path, help="Planned conditions, case IDs, and trials in JSON")
    parser.add_argument("--out", type=Path, help="New JSON report file, or omit for stdout")
    args = parser.parse_args()
    try:
        report = compare_results(args.responses, args.judgments, args.expected_grid)
        output = json.dumps(report, indent=2, sort_keys=True)
        if args.out is None:
            print(output)
        else:
            with args.out.open("x", encoding="utf-8") as handle:
                handle.write(output + "\n")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
