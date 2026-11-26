# v0.4.0 development evidence · 25–26 November 2026

The original three-condition comparison showed **no observed UAI advantage**.
Baseline, brief instruction and UAI each met 21/24 original rubrics, with the
same three nonpasses. One fixture has ambiguous wording; see its report before
using those counts. Public development cases are not a held-out benchmark.

| Evidence | Observed result | What it establishes |
| --- | --- | --- |
| [Original comparison](comparison/README.md) | 72 responses; 21/24 rubric passes per condition; all 24 paired outcomes tied. | One exploratory instruction-text comparison with agent review. |
| [Boundary and live-turn checks](forward/README.md) | 16/16 boundary responses and 13/13 live-turn responses passed the supplied rubrics. | UAI-only development behavior, with future turns withheld. |
| [Actual retrieval workflow](tool-use/README.md) | Real CLI calls, correct announcement, unchanged synthetic source and only requested artifact. | One explicitly instructed agent-assisted workflow. |
| [Code and host checks](verification/README.md) | 78 tests on Linux and macOS, real MCP stdio, native installation/discovery checks. | Code behavior and named installation/connection surfaces. |

Do not combine these different evidence categories into one accuracy percentage.
No human evaluation, native automatic skill selection, token saving, latency
improvement or general superiority is claimed. All fixtures are synthetic.

The [release verification](../../../docs/verification.md) connects these results
to versioned code and publication-time receipts.
