#!/usr/bin/env python3
"""Prepare isolated requests or collect opt-in, response-only Claude CLI results.

No answer rubrics are loaded by this program. No automatic quality score is
assigned. Each case starts a fresh process with tools and customizations off.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
BASE = "You are a helpful assistant. Continue the provided conversation and respond to its final user message. No tools are available in this session."
BRIEF = "Use relevant available context. Preserve explicit constraints and corrections. Proceed when clear enough; ask only for unresolved information that would materially change the result."
REQUIRED_FLAGS = ("--safe-mode", "--tools", "--strict-mcp-config",
                  "--no-session-persistence", "--disable-slash-commands")
ALLOWED_CASE_FIELDS = {"id", "split", "category", "messages"}


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_cases(path, split="smoke"):
    cases, ids = [], set()
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        case = json.loads(line)
        if set(case) != ALLOWED_CASE_FIELDS:
            raise ValueError(f"Case line {number}: unexpected fields (rubrics must stay separate)")
        if not isinstance(case["id"], str) or not case["id"] or case["id"] in ids:
            raise ValueError(f"Case line {number}: invalid or duplicate id")
        ids.add(case["id"])
        messages = case["messages"]
        if not isinstance(messages, list) or not messages or messages[-1].get("role") != "user":
            raise ValueError(f"Case {case['id']}: final turn must be user")
        for msg in messages:
            if set(msg) != {"role", "content"} or msg["role"] not in ("user", "assistant"):
                raise ValueError(f"Case {case['id']}: invalid message shape")
            if not isinstance(msg["content"], str) or not msg["content"]:
                raise ValueError(f"Case {case['id']}: empty message")
        if split == "all" or case["split"] == split:
            cases.append(case)
    if not cases:
        raise ValueError("No matching cases")
    return cases


def instruction(condition, skill=None):
    if condition == "baseline":
        return BASE
    if condition == "brief":
        return BASE + "\n\n" + BRIEF
    if condition == "uai":
        skill = ROOT / "skills" / "understanding-ambiguous-intent" / "SKILL.md"
    if skill is None:
        raise ValueError("custom condition requires --skill")
    return BASE + "\n\n" + Path(skill).read_text(encoding="utf-8")


def prompt(case):
    return "Conversation to continue (JSON):\n" + json.dumps(case["messages"], ensure_ascii=False)


def make_request(case, condition, system):
    return {"id": case["id"], "split": case["split"], "category": case["category"],
            "condition": condition, "system": system, "prompt": prompt(case)}


def supported_cli(executable):
    result = subprocess.run([executable, "--help"], capture_output=True, text=True, timeout=20)
    if result.returncode or any(flag not in result.stdout for flag in REQUIRED_FLAGS):
        raise ValueError("Claude CLI lacks required isolation flags; update it or use prepare mode")
    version = subprocess.run([executable, "--version"], capture_output=True, text=True,
                             timeout=20, check=True).stdout.strip()
    return version


def run_one(executable, request, model, timeout, cwd, version):
    command = [executable, "--print", "--safe-mode", "--disable-slash-commands",
               "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
               "--no-session-persistence", "--output-format", "json",
               "--system-prompt", request["system"]]
    if model != "default":
        command.extend(["--model", model])
    record = {k: request[k] for k in ("id", "split", "category", "condition")}
    record.update({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                   "surface": "response-only-reconstructed-conversation",
                   "host": "Claude Code CLI", "host_version": version,
                   "model_requested": model, "system_sha256": sha(request["system"]),
                   "prompt_sha256": sha(request["prompt"]),
                   "tools_enabled": False, "rubric_provided": False})
    started = time.monotonic()
    try:
        result = subprocess.run(command, input=request["prompt"], capture_output=True,
                                text=True, timeout=timeout, cwd=cwd)
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        if result.returncode:
            # Never publish unreviewed stderr, which can contain machine paths or account data.
            record.update(status="provider-error", exit_code=result.returncode,
                          error="CLI failed; no quality score assigned")
            return record
        data = json.loads(result.stdout)
        if not isinstance(data, dict):
            record.update(status="invalid-result", error="Provider JSON is not an object")
            return record
        if data.get("is_error") or data.get("subtype") not in (None, "success"):
            record.update(status="provider-error", error="CLI returned an error result; no score assigned")
            return record
        if not isinstance(data.get("result"), str) or not data["result"].strip():
            record.update(status="invalid-result", error="No text response returned")
            return record
        models = data.get("modelUsage") or {}
        if not isinstance(models, dict):
            record.update(status="invalid-result", error="Provider model usage is malformed")
            return record
        record.update(status="ok", response=data["result"],
                      usage=data.get("usage", {}),
                      reported_models=sorted(models.keys()),
                      reported_api_cost_usd=data.get("total_cost_usd"),
                      provider_duration_ms=data.get("duration_ms"))
    except subprocess.TimeoutExpired:
        record.update(status="timeout", elapsed_seconds=round(time.monotonic() - started, 3))
    except (ValueError, OSError) as exc:
        record.update(status="runner-error", error=type(exc).__name__)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("prepare", "run"))
    parser.add_argument("--condition", choices=("baseline", "brief", "uai", "custom"), required=True)
    parser.add_argument("--label", help="Record label for a custom comparator")
    parser.add_argument("--skill", type=Path, help="Custom comparator file, not installed globally")
    parser.add_argument("--cases", type=Path, default=ROOT / "evals" / "cases.jsonl")
    parser.add_argument("--split", default="smoke", choices=("smoke", "dev", "all"))
    parser.add_argument("--ids", help="Comma-separated subset of case IDs")
    parser.add_argument("--out", type=Path, required=True, help="New JSONL file; existing files refused")
    parser.add_argument("--model", default="default", help="Claude model id/alias; no fallback is configured")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    try:
        if args.timeout <= 0:
            raise ValueError("--timeout must be positive")
        cases = read_cases(args.cases, args.split)
        if args.ids:
            selected = set(args.ids.split(","))
            found = {c["id"] for c in cases}
            if not selected <= found:
                raise ValueError("Requested case IDs do not match the selected split")
            cases = [c for c in cases if c["id"] in selected]
        system = instruction(args.condition, args.skill)
        label = args.label or args.condition
        requests = [make_request(case, label, system) for case in cases]
        executable, version = None, None
        if args.mode == "run":
            executable = shutil.which("claude")
            if not executable:
                raise ValueError("Claude CLI not found; use prepare mode with your own evaluation host")
            version = supported_cli(executable)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        failed = False
        with args.out.open("x", encoding="utf-8") as output:
            if args.mode == "prepare":
                for request in requests:
                    output.write(json.dumps(request, ensure_ascii=False) + "\n")
            else:
                # Isolate cwd from the repository and answer keys. Safe mode disables user customizations.
                with tempfile.TemporaryDirectory(prefix="uai-eval-", dir=args.out.parent) as work:
                    for request in requests:
                        record = run_one(executable, request, args.model, args.timeout, work, version)
                        output.write(json.dumps(record, ensure_ascii=False) + "\n")
                        output.flush()
                        print(json.dumps({"id": record["id"], "condition": label,
                                          "status": record["status"]}), flush=True)
                        if record["status"] != "ok":
                            failed = True
                            break
        if failed:
            parser.exit(1, "Run stopped at the first provider/runner failure. This is not a behavior failure.\n")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
