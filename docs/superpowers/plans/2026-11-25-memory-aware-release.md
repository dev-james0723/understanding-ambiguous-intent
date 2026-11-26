# Memory-aware UAI Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for isolated implementation and review tasks. The user has authorized immediate execution through release; continue without a new plan-approval pause.

**Goal:** Ship the existing Context Bridge with reliable retrieval, task continuity, comparative evidence and a usable public installation path.

**Architecture:** Preserve the existing read-only bridge and portable skill. Keep generation inputs, judgments and tool-effect evidence separate. A single integration owner assembles independent file changes and release receipts.

**Tech Stack:** Python 3.10+, optional MCP Python SDK, Markdown, JSON/JSONL, local Git and unittest.

**Spec:** `docs/memory-aware-spec.md`

## Global constraints

- No GitHub Actions, external model subscription invocation or paid fallback.
- Preserve the existing candidate and unrelated worktrees.
- Core runtime remains concise and host-neutral; no private memory is published.
- Keep 24 original cases and their rubrics unchanged.
- Treat model metadata and untested host features honestly.

## Review focus

- A memory changes only beyond its displayed excerpt or in status metadata: stale record identifiers must not read as unchanged evidence.
- A relevant term appears late in a long paragraph: bounded search must not silently lose the entire later portion.
- A cancellation follows a status question: the old task must not resume.
- A successful tool result appears among partial or missing sources: report the remaining gaps accurately.
- A public installer is invoked twice or beside a private installation: preserve prior files and report the conflict.

## Task 1: Review and harden the existing bridge

**Files:** `context_bridge/core.py`, `context_bridge/mcp_server.py`, `tests/test_context_bridge.py`, `tests/test_context_bridge_mcp.py`.

**Interface:** Preserve `Bridge(config)` and its eight existing operations. CLI/server both consume the same launch-time config.

- [x] Independently inspect candidate behavior and reproduce concrete issues.
- [x] Add focused failing tests for confirmed source, metadata or retrieval defects.
- [x] Repair each defect without broadening file access or adding source writes.
- [x] Run `python3 -m unittest discover -s tests -v`, including actual MCP stdio.

## Task 2: Add continuity and evaluation coverage

**Files:** runtime `SKILL.md`, `references/task-continuity.md`, `evals/boundary-cases.jsonl`, `evals/boundary-rubrics.jsonl`, `evals/trajectories.jsonl`, `evals/trajectory-rubrics.jsonl`, `scripts/compare_results.py`, `tests/test_comparison.py`.

**Interface:** Original response cases remain `{id, split, category, messages}`. New generation files contain no expected answers. Comparison accepts response records and separate judgments, rejecting missing, duplicate or mismatched records.

- [x] Define boundary-pair and multi-turn fixtures with separate semantic rubrics.
- [x] Add concise continuation/cancellation and optional context instructions.
- [x] Test comparison integrity and report separate task, clarification and regression measures.
- [x] Run 24 existing cases in fresh sessions for each of baseline, brief and UAI; retain all results and methodological limits.
- [x] Exercise real multi-turn corrections and cancellation independently.

## Task 3: Make setup and tool behavior reproducible

**Files:** `scripts/demo_context.py`, `tests/test_demo.py`, `docs/context-bridge.md`, README files, compatibility guide, contribution template.

**Interface:** `python3 scripts/demo_context.py` uses temporary synthetic files, performs real CLI/protocol operations where available, and exits nonzero on incorrect final state. It never reads real personal memory.

- [x] Add and run a deterministic demo with retrieval, stale record handling and unchanged source hashes.
- [x] Have a fresh agent use actual bridge operations to produce a bounded fixture artifact; inspect final bytes independently.
- [x] Verify clean host distribution paths and register/list MCP in disposable host config where supported.
- [x] Publish three examples and a failure-report template that requests no private chat history.

## Task 4: Review, release and verify public delivery

**Files:** version/manifests, changelog, verification documents and result artifacts.

- [x] Reconcile version strings and links; run check.py, unittest and skill validation.
- [x] Obtain independent whole-change review; fix blockers and retest affected gates.
- Publication gate: Commit and push the reviewed branch, integrate through the repository workflow and publish v0.4.0.
- Publication gate: Retrieve released files and verify hashes; verify fresh remote installation.
- Publication gate: Update the private library's public submodule pointer without touching dirty personal work.
- Publication gate: Record passed, unverified and blocked categories separately, and provide the public release link.

The final release asset records these downstream publication gates against the
public commit and remote artifacts.
