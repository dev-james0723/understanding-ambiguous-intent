# Research and positioning

Research snapshot: **2026-11-24**. Recent-evidence window: **2026-10-26 through 2026-11-24**, inclusive. This document informs the experimental 0.3.0 release; it does not establish a measured advantage for Understanding Ambiguous Intent (UAI).

## Comparable work

These are selected primary sources, not an exhaustive inventory. Repository contents can change after this snapshot. License observations describe the inspected repositories and do not replace checking the license of any material proposed for reuse.

| Project | Observed approach and overlap | Date and limits |
| --- | --- | --- |
| [IntentPreter](https://github.com/Sumama-Jameel/intentpreter/blob/main/SKILL.md) | Interprets ambiguous requests using conversation context, corrections, desired outcomes, constraints, and focused clarification. Separates interpreting a request from authority to execute it. This is close prior art for UAI's central purpose. | Its [changelog](https://github.com/Sumama-Jameel/intentpreter/blob/main/CHANGELOG.md) dates both 0.1.0 and 0.2.0 to **2026-08-09**, outside the recent window. MIT. Its README says it has no project-specific benchmark suite; external research does not validate this skill. |
| [Superpowers brainstorming](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md) | Inspects project context, asks consequential unresolved questions, presents options, and develops a design before implementation. More explicitly a design workflow than a general request interpreter. | [v7.0.2](https://github.com/obra/superpowers/releases/tag/v7.0.2), **2026-11-03**, includes clarification and workflow refinements. MIT. Its maintainer tests and issue discussions are useful design evidence, not representative market research. |
| [Prompt Optimizer Skill](https://github.com/Samuel-Shek/prompt-optimizer-skill/blob/main/SKILL.md) | Preserves original intent, separates suggested additions, distinguishes user-requested rewriting from internal clarification, and returns internally clarified requests to the original task. Its routing and fidelity concerns overlap with UAI. | The [changelog](https://github.com/Samuel-Shek/prompt-optimizer-skill/blob/main/CHANGELOG.md) records a **2026-11-05** evaluation and **2026-11-13** version 4.1.3. MIT. The small evaluation reported no stable downstream benefit and additional overhead, with acknowledged evaluation limitations. This is evidence about that experiment, not UAI. |
| [ECC intent-driven-development](https://github.com/affaan-m/ECC/blob/main/skills/intent-driven-development/SKILL.md) | Uses context, proportional intent briefs, material clarifying questions, and observable acceptance criteria to connect an underspecified request to implementation. | Current inspected prior art; an in-window change date was **not verified**. Repository license: MIT. Software development is its main setting. |

## What the evidence suggests

**People want useful progress with less repeated explanation.** November discussion in a [Superpowers issue](https://github.com/obra/superpowers/issues/2530) describes frustration with repeated specifications and excessive process. The issue began before the window; only its November discussion is recent evidence. These are selected users' experiences, not a prevalence estimate. The design implication is to separate the depth of investigation from the amount of interaction required.

**The deliverable matters as much as clearer wording.** The optimizer's explicit handling of rewriting versus internal clarification suggests a useful distinction: a user asking for an action should receive progress on that action; a user asking for a reusable prompt should receive a prompt. UAI should evaluate wrong-deliverable failures directly.

**More clarification is not automatically better.** The optimizer's reported evaluation makes overhead and unintended added requirements material risks to test. UAI should not claim that a longer interpretation step improves results merely because its instructions appear more thorough.

## Proposed position

UAI's proposed focus is a small, portable interpretation layer: recover the intended deliverable from available context, distinguish stated facts from inferences, ask only when the answer would materially change the work, and preserve the task's authorization boundary.

Context corrections, incomplete wording, code-switched language, and noisy transcripts are candidate evaluation areas. They are **not demonstrated advantages** of this release. Many comparators already address parts of this problem; neither novelty nor superiority should be claimed without narrower evidence.

## Evaluation priorities

Compare the same host, model, task, context, and tool permissions under:

1. Native host behavior without UAI.
2. A minimal instruction to resolve consequential ambiguity.
3. UAI.
4. A relevant comparator where its intended workflow matches the task.

Separate development cases from held-out evaluation cases. Keep actor-visible inputs separate from grading criteria. Record task completion, deliverable match, constraint preservation, unsupported additions, unnecessary questions, missed necessary questions, and latency or token cost where available. Record failures and partial results, not only successful examples.

Report language groups and ambiguity types separately. Distinguish tests of response text from tasks with actual tool execution and observed side effects. A static package check, a passing synthetic case, and a successful installation each establish different things. See [compatibility](compatibility.md) for the evidence categories.
