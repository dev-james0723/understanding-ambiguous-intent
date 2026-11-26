# Verification · experimental v0.4.0

This release adds an optional read-only Context Bridge, task-continuity guidance,
setup tools and public evaluation evidence. **The original 24-case comparison
does not show UAI outperforming baseline or a brief instruction.** All three
conditions met 21 of 24 original rubrics, with the same three nonpasses and no
observed critical failures. One fixture is ambiguously worded; two others
distinguish explicit from implicit handling. These are development observations,
not a general accuracy estimate.

The [v0.3.0 report](verification-v0.3.0.md) and
[initial candidate report](context-bridge-verification.md) remain historical.
This release's frozen `SKILL.md` SHA-256 is:

`5633377efaaa9b85fd9ed0fddfb62e45fe0b3f8d9db3c1cd7dcf8088c849b3fd`

This identifies the instruction file, not the entire repository. The final
public commit, released-file check, independent whole-change review and fresh
remote marketplace check are recorded in `release-verification.json` attached
to the [v0.4.0 prerelease](https://github.com/dev-james0723/understanding-ambiguous-intent/releases/tag/v0.4.0).
Tracked receipts below retain prepublication integration revisions; the release
is assembled from the reviewed file tree.

## Code, protocol and installation

| Check | Observed evidence | Limit |
| --- | --- | --- |
| Structure and skill validation | Repository checker and Skill Creator validator passed; four runtime files, consistent versions and separate evaluation material. | Static conformance is not model behavior. |
| Linux | Python 3.12.14, MCP SDK 1.29.0: 78 tests passed, including actual stdio protocol and the CLI/MCP demo. | SDK emitted a Pydantic forward-reference warning; protocol operations completed. |
| macOS ARM64 | Python 3.12.8, MCP SDK 1.30.0: the same 78 tests and CLI/MCP demo passed. | Other interpreter/SDK combinations remain unverified. |
| Source handling | Regression tests cover full-record matching and identity, expiry, changed metadata, keyed conflicts, symlinks, hardlinks, root replacement, unsafe files, limits and partial results. | Keyword retrieval does not prove completeness or truth. |
| Setup | Creates a private non-overwriting config and stores the resolved source root that was checked. An alias-retarget regression preserves that source. | Metadata-only setup does not certify source contents. |
| Claude Code 2.1.331 distribution | Strict plugin/marketplace validation, disposable local marketplace install, enabled listing, native inventory and exact installed runtime hash passed. | No native model invocation or automatic skill selection. |
| Codex CLI 0.171.0 discovery | Native app-server `skills/list` found the exact project-installed runtime, enabled with repo scope. | Discovery does not demonstrate model use. |
| Claude Code MCP | Disposable user config accepted the server; native `mcp list` and `mcp get` reported connected. | Health connection, not model-driven selection. |
| Codex MCP | A process-only override appeared enabled in native `mcp list --json`. | Configuration/listing only; not a health or model execution test. |
| Manual installer | Copied all four runtime files and refused overwrite. | Other host discovery mechanisms remain unverified. |

The [receipts and logs](../evals/results/2026-11-25/verification/README.md) record
these observations. Dependencies stayed in dedicated environments. Host checks
used disposable or process-only configuration. No existing personal UAI
installation was replaced. No GitHub Actions were introduced or run.

## Behavior and actual tool effects

### Original comparison

There are 72 completed samples: 24 original public cases under baseline, brief
instruction and UAI, one trial each. A fresh reviewer received the original
rubrics and answers with condition labels withheld. The integration agent
inspected every nonpass and the deletion-target borderline cases. This is agent
review, not human scoring.

| Condition | Original rubric passes | Paired outcome versus baseline |
| --- | --- | --- |
| Baseline | 21 / 24 | Reference |
| Brief instruction | 21 / 24 | 24 ties; no observed improvement or regression |
| UAI | 21 / 24 | 24 ties; no observed improvement or regression |

All three had zero flagged unnecessary questions, one missed required request
for information and zero observed critical failures. One interrupted attempt
was retried once before capture; both attempts remain recorded. Read the
[outputs, rubric concerns and methodology](../evals/results/2026-11-25/comparison/README.md)
before interpreting these counts.

### Additional development cases

Eight boundary pairs and four live multi-turn trajectories cover corrections,
status, cancellation, task replacement and stale context. Their recorded
responses and per-turn review are in the
[current results](../evals/results/2026-11-25/README.md). These are UAI-only
checks, separate from the three-condition comparison; they cannot establish
comparative improvement.

### Actual agent-assisted workflow

A fresh agent used the real CLI's `build_intent_context` and
`resolve_memory_conflicts` over a synthetic source, then wrote a two-sentence
Traditional Chinese announcement. Independent inspection verified the current
brand, corrected 11:00 time, Room 4/free-admission details, exact artifact bytes,
unchanged memory bytes and no extra work artifact. An instruction embedded in
retrieved text did not cause its requested extra file or external message.

The [request, source, trace, artifact and receipt](../evals/results/2026-11-25/tool-use/README.md)
are public. This establishes one explicitly instructed ChatGPT-agent CLI
workflow. It does not establish native Claude/Codex automatic tool selection,
cloud memory access or arbitrary workflow reliability.

## Review and limits

Independent component reviews identified and corrected source-alias binding,
explicit expiry, truncated-record identity/search, Unicode JSONL framing,
instruction-file classification and comparison-integrity
defects. Focused regressions failed before repair and passed after repair.
The final publication receipt records the separate whole-change review outcome
and exact public commit.

The actor harness requested gpt-6.2-sol at high effort. Resolved model/settings,
token use and provider latency were not exposed. Actors were fresh threads with
instruction text supplied explicitly; common host policies still applied.
Rubrics and future trajectory turns were withheld by the harness. Isolation
was prompt-enforced, not an operating-system restriction on file access.

Not established:

- Reliable native automatic skill triggering or model-driven MCP use.
- Benefit in task success, token cost, latency, user effort or satisfaction.
- Performance on independently held-out tasks, other models or broad languages.
- Human-validated reliability, security guarantees or universal host support.
- Windows Context Bridge support, semantic search, complete memory retrieval,
  account synchronization or cloud ChatGPT plugin installation.

## Reproduce and roll back

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
python3 scripts/demo_context.py
```

Install optional dependencies in an isolated environment as described in the
[Context Bridge guide](context-bridge.md) to include the actual MCP stdio test
and `python3 scripts/demo_context.py --mcp`. Without that SDK, the protocol test
is skipped; do not report a full MCP pass from that run.

The [comparison instructions](../evals/results/2026-11-25/comparison/README.md)
reproduce the report from exact responses and hash-linked judgments without
calling a model. New behavioral runs need a host, recorded settings and
separate grading; regenerating the report is not new behavioral evidence.

To roll back the optional extension, remove its MCP registration and private
grant file. It never writes the memory source. Tagged v0.3.0 remains available
for core rollback; inspect an existing installation before replacing it.
