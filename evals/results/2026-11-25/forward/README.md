# Additional UAI development checks

| Set | Planned / captured | Agent-reviewed passes | Critical failures |
| --- | --- | --- | --- |
| Eight boundary pairs | 16 / 16 | 16 / 16 | 0 / 16 |
| Four live trajectories | 13 / 13 turns | 13 / 13 turns | 0 / 13 turns |

There were no retries, infrastructure failures, flagged unnecessary questions
or missed required questions. Each boundary case used a fresh actor. Each
trajectory used one actor throughout; the next user turn was sent only after
the prior answer was captured. Future turns and rubrics were withheld.

The trajectories cover progress followed by a corrected time, cancellation and
an ambiguous continuation, advice followed by an explicit execution request,
and a temporary location correction that leaves the usual location intact.
The integration agent verified all 13 replay prefixes against the original
user turns and recorded answers, and inspected all trajectory outputs plus
the boundary reviewer’s borderline cases.

These are one-trial, UAI-only public development checks. They provide no
baseline comparison, population reliability estimate, human validation or
native skill-triggering evidence. The actor used instruction text, with
prompt-enforced tool isolation. Resolved model/settings were not exposed.

## Retained records

- [Boundary responses](boundary-responses.jsonl) and [judgments](boundary-judgments.jsonl).
- [Per-turn responses](trajectory-responses.jsonl) and [judgments](trajectory-judgments.jsonl).
- [Unmodified trajectory attempt ledger](trajectory-attempts.jsonl).
- [Lifecycle manifest](manifest.jsonl) and [methodology](methodology.md).
- [Validated coverage and counts](summary.json).

Per-turn publication IDs append `#turn-N` to the raw trajectory identifiers;
the original identifiers are retained as metadata. Answer bytes and hashes
are unchanged. Judgments bind to exact decoded UTF-8 response hashes.
