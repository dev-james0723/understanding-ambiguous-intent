#!/usr/bin/env python3
"""Offline repository and fixture checks. Does not score model behavior."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evaluate import read_cases


def check(root=ROOT):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    skill = root / "skills" / "understanding-ambiguous-intent" / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    match = re.match(r"\A---\nname: ([a-z0-9-]+)\ndescription: >-\n((?:  [^\n]*\n)+)---\n", text)
    require(bool(match), "Core must use the documented minimal name/description frontmatter")
    if match:
        require(match.group(1) == skill.parent.name, "Skill name and directory differ")
        require(len(" ".join(match.group(2).split())) <= 1024, "Description exceeds 1024 characters")
    require(len(text.splitlines()) < 500, "Runtime core exceeds 500 lines")
    require(len(text.split()) <= 1600, "Runtime core exceeds the project's 1600-word budget")
    version = (root / "VERSION").read_text().strip()
    require(bool(re.fullmatch(r"\d+\.\d+\.\d+", version)), "Invalid VERSION")
    manifest = json.loads((root / ".claude-plugin" / "plugin.json").read_text())
    require(manifest.get("version") == version, "Plugin and VERSION differ")
    require(manifest.get("name") == "understanding-ambiguous-intent", "Plugin identity mismatch")
    marketplace = json.loads((root / ".claude-plugin" / "marketplace.json").read_text())
    plugins = marketplace.get("plugins", [])
    require(len(plugins) == 1, "Marketplace must contain exactly the UAI plugin")
    if len(plugins) == 1:
        require(plugins[0].get("name") == manifest["name"], "Marketplace identity mismatch")
        require(plugins[0].get("version") == version, "Marketplace and VERSION differ")
    require("Copyright (c) 2026 James Au" in (root / "LICENSE").read_text(), "Missing license notice")
    required = ["README.md", "README.zh-Hant.md", "CHANGELOG.md", "CONTRIBUTING.md",
                "docs/research.md", "docs/compatibility.md", "docs/context-adapters.md",
                "docs/verification.md", "evals/README.md",
                "skills/understanding-ambiguous-intent/agents/openai.yaml"]
    for relative in required:
        require((root / relative).is_file(), f"Missing {relative}")
    cases = read_cases(root / "evals" / "cases.jsonl", "all")
    rubrics = [json.loads(x) for x in (root / "evals" / "rubrics.jsonl").read_text().splitlines() if x.strip()]
    case_ids = {c["id"] for c in cases}
    rubric_ids = [r["id"] for r in rubrics]
    require(len(set(rubric_ids)) == len(rubric_ids), "Duplicate rubric id")
    require(set(rubric_ids) == case_ids, "Rubric IDs do not match case IDs")
    require(len(cases) >= 24, "Expected at least 24 diverse public fixtures")
    require(sum(c["split"] == "smoke" for c in cases) >= 8, "Expected at least 8 smoke fixtures")
    for rubric in rubrics:
        require(rubric.get("clarification") in ("required", "unnecessary", "conditional"),
                f"Invalid clarification policy: {rubric['id']}")
        require(bool(rubric.get("required")) and bool(rubric.get("forbidden")),
                f"Missing behavior criteria: {rubric['id']}")
    for path in skill.parent.rglob("*"):
        require(not path.is_symlink(), f"Runtime symlink: {path.relative_to(root)}")
        if path.is_file():
            require(path.name in {"SKILL.md", "examples.md", "task-continuity.md", "openai.yaml"},
                    f"Unexpected runtime file: {path.relative_to(root)}")
    for path in root.rglob("*.md"):
        if any(part in {".git", ".tools", ".local-eval", ".superpowers"} for part in path.relative_to(root).parts):
            continue
        content = path.read_text(encoding="utf-8")
        for destination in re.findall(r"\[[^\]]*\]\(([^)]+)\)", content):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", destination) or destination.startswith("#"):
                continue
            destination = destination.split("#", 1)[0]
            require((path.parent / destination).exists(),
                    f"Broken relative link in {path.relative_to(root)}: {destination}")
    return errors


def main():
    try:
        errors = check()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"FAIL: {exc}")
        return 1
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print("PASS: runtime structure, version consistency, documentation links, fixture separation")
    print("This check makes no claim about model behavior or installation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
