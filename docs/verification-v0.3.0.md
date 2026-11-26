# Verification · v0.3.0

Date: 2026-11-24. This is an experimental release with explicit evidence limits.

## Completed checks

| Check | Observed evidence |
|---|---|
| Skill frontmatter | Skill Creator quick_validate.py returned "Skill is valid!" on the public runtime folder. |
| Agent UI metadata | Generated with the matching Skill Creator helper using explicit interface values. |
| Distribution/evaluation utilities | 12 unittest cases passed, including existing-install preservation, symlink refusal, dry-run behavior, rubric-field rejection, duplicate IDs, malformed provider JSON, and nullable model metadata. |
| Public fixture integrity | 24 cases and 24 matching rubrics; eight smoke and sixteen development cases. |
| Independent code and documentation review | No release blocker found; three concrete robustness/wording findings were corrected before release. |
| Fresh-session forward checks | Four response artifacts met an independent agent's semantic rubric review; outputs are published. |
| Runtime/public privacy review | Reviewed content contains no owner conversation history, personal machine paths, authentication data, or required private service integrations. |

See [actual responses and limitations](../evals/results/2026-11-24/README.md).
These checks are different kinds of evidence and should not be combined into
a single accuracy percentage.

## Final distribution checks

| Distribution check | Observed result |
|---|---|
| Repository structure, version consistency, internal links, fixture separation | Passed scripts/check.py. |
| Claude Code 2.1.331 plugin manifest | Strict validation passed with zero manifest errors or warnings. |
| Claude Code 2.1.331 marketplace manifest | Strict validation passed with zero manifest errors or warnings. |
| Isolated local marketplace installation | Add, install, and list all exited 0; the plugin was listed as enabled at version 0.3.0. |
| Installed Claude cache content | The installed SKILL.md matched the source byte-for-byte. |
| Manual installer with the actual release folder | All three runtime files matched their source hashes exactly. |

Installation used a disposable configuration directory and was removed after
verification. It did not replace an existing personal UAI installation.
This checks installation/discovery from a local marketplace; automatic
triggering, cloud installation, and remote marketplace fetching are separate.

[Machine-readable distribution receipt](verification-v0.3.0.json) records the checks.
The runtime SKILL.md SHA-256 is
`9b8003d52e3e2dcf4265c86a7c3a497d87710eae6174c5297687953ed9e33eb6`.

## Not established

- No controlled no-skill / short-instruction / UAI / IntentPreter comparison.
- No measured benefit in task success, token cost, latency, or user effort.
- No broad multilingual or cross-model reliability claim.
- No automatic triggering test in Codex or Claude Code.
- No downstream live-tool execution test.
- No implemented context adapter, background memory collector, or synchronization.
- No end-to-end ChatGPT plugin-directory installation test.

The attempted automated CLI comparison was unavailable because of provider
quota limits. This was not counted as behavioral success or failure.

## Reproduce

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
python3 scripts/evaluate.py prepare --condition uai --split smoke --out /path/to/new-requests.jsonl
```

With a supported, authenticated Claude CLI and available quota:

```sh
python3 scripts/evaluate.py run --condition baseline --split smoke --model YOUR_MODEL --out /path/to/baseline.jsonl
python3 scripts/evaluate.py run --condition brief --split smoke --model YOUR_MODEL --out /path/to/brief.jsonl
python3 scripts/evaluate.py run --condition uai --split smoke --model YOUR_MODEL --out /path/to/uai.jsonl
```

Run each condition under the same model and environment; record the resolved
model, repeat cases, and judge against rubrics withheld from generation.
The runner disables ordinary Claude customizations and tools; managed host
policy can still apply. It has no fallback model configuration.

For a pinned external comparator, use `--condition custom --label NAME --skill FILE`
and record its repository commit, file hash, and license. That file is not
installed by the runner and should not be copied into the public runtime.
