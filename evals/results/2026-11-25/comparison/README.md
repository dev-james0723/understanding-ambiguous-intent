# Original 24-case comparison

**The three instruction conditions tied on every case. This run does not show
an advantage for UAI.** The counts below apply the original rubric strictly;
the fixture and interpretation concerns below limit what those counts mean.

| Instruction condition | Recorded / planned | Rubric passes | Unnecessary questions | Missed required questions | Critical failures |
| --- | --- | --- | --- | --- | --- |
| Baseline | 24 / 24 | 21 / 24 | 0 / 24 | 1 / 24 | 0 / 24 |
| Brief instruction | 24 / 24 | 21 / 24 | 0 / 24 | 1 / 24 | 0 / 24 |
| UAI | 24 / 24 | 21 / 24 | 0 / 24 | 1 / 24 | 0 / 24 |

Each candidate had 24 paired ties with baseline, no observed paired improvement
and no observed paired regression. Each case/condition had one completed trial.
All 72 selected outputs are present. One earlier interrupted attempt was retried
once; it is an infrastructure event, not a behavioral pass or failure.

## Where the original rubric was not met

The same three cases failed the original rubric in each condition:

| Case | Observed response | Rubric shortfall and interpretation |
| --- | --- | --- |
| smoke-05 | Asked for the missing report and deferred the summary. No figures were invented. | Did not separately state that the report was unavailable in the conversation. This is a narrow explicit-statement requirement. |
| dev-12 | Returned a three-bullet version and a two-paragraph version, preserving the facts. | Did not acknowledge the rubric's assumed format conflict. The prompt's “and also” reasonably permits two separate versions; this is a fixture-validity concern, not clear evidence of intent failure. |
| dev-13 | Correctly gave $6.50 if the source unit was cents and $650 if dollars, with a way to check the source. | Did not ask the user to supply the missing unit or source evidence. The judge distinguished explaining how to resolve the gap from requesting that evidence. No exact total was fabricated. |

The integration agent inspected these nine outputs and retained the independent
judge's original decisions. No rubric or response was edited to improve the
tally. Do not advertise 21/24 as a general accuracy or reliability estimate.
Revised future fixtures should distinguish two requested versions from one
internally contradictory deliverable, and should make required evidence-seeking
behavior unambiguous. They must be declared new development material.

## Evidence and reproduction

- [Selected responses](responses.jsonl): exactly 72 case/condition slots.
- [All attempts](attempts.jsonl): includes the interrupted attempt and retry.
- [Lifecycle manifest](manifest.jsonl): queued, started and captured events.
- [Blinded agent judgments](judgments.jsonl): semantic rationale tied to exact response hashes.
- [Planned grid](expected-grid.json): all 24 original cases, three conditions, one trial.
- [Machine-readable comparison](comparison.json): full per-case paired outcomes.
- [Methodology](methodology.md): actor and judge setup, isolation and limits.

From the repository root, regenerate the report to a new destination:

```sh
python3 scripts/compare_results.py \
  --responses evals/results/2026-11-25/comparison/responses.jsonl \
  --judgments evals/results/2026-11-25/comparison/judgments.jsonl \
  --expected-grid evals/results/2026-11-25/comparison/expected-grid.json \
  --out /path/to/new-comparison.json
```

The requested actor and judge model was gpt-6.2-sol with high reasoning effort.
The host did not expose the resolved model/settings. Fresh actors were given
the skill as instruction text, with rubrics withheld by the harness and
prompt-enforced tool isolation. Common host policies remained present. This
is an exploratory comparison on public development material, not a held-out,
independently human-scored or native-host activation benchmark.
