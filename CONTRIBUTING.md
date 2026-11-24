# Contributing

UAI is an experimental, portable skill for recovering the intended task from incomplete or ambiguous requests. Contributions should improve task fidelity and useful progress while keeping the core understandable and small.

## Start with the problem

For a proposed change, describe the concrete failure: what the user intended, what the assistant did, and why the difference matters. State the expected behavior and the smallest change that could produce it.

Changes to the portable interpretation policy, host packaging, optional adapter designs, and evaluation infrastructure have different responsibilities. Explain which part your contribution affects. External integrations should begin as a scoped proposal with explicit read, write, and authorization boundaries; the design document is not an implementation.

Do not add a mandatory service, account, secret, private directory, personal alias, or machine-specific assumption to the portable skill.

## Share safe, useful cases

Prefer synthetic cases that reproduce the failure without disclosing a person's conversation or work. If adapting real material, remove identifiers and sensitive details, confirm that you have the right to share it, and label the transformation accurately.

Do not include private transcripts, personal profiles, credentials, access tokens, confidential project details, internal endpoints, or unapproved third-party material. Replacing a name alone does not necessarily anonymize a case.

A useful case records:

- A stable identifier and whether it is synthetic, adapted, or publicly sourced.
- The user input and the context actually available to the actor.
- The intended deliverable, material constraints, and relevant ambiguity.
- Any existing authorization and the effects that remain outside its scope.
- The expected decision: proceed, ask a consequential question, explore, or provide a requested rewrite.
- Source and license information where relevant.

Use generic people, projects, and files. Preserve the causal feature that made the original interaction fail. Include clear requests and negative trigger cases, not only examples that encourage activation.

## Keep actor inputs separate from grading

The actor must not receive the hidden grading rubric or expected answer during an evaluation. Keep case inputs, expected properties, and scoring material in distinct files or data fields that the runner separates correctly.

Prefer observable properties over matching a single preferred wording. Examples include delivering the requested artifact, preserving a stated constraint, asking a necessary question, avoiding an invented requirement, and respecting authorized effects.

Label development and held-out cases. Do not tune the instructions repeatedly against a held-out set and continue to describe it as independent evidence. Record repetitions, failures, retries, and exclusions.

## Compare against a baseline

A stronger-looking response is not enough to establish an improvement. When making an effectiveness claim, compare the same task, context, model, host, and tool permissions with and without UAI. A minimal clarification instruction is also a useful comparison.

Report task success alongside costs: unnecessary questions, extra turns, unsupported additions, latency, and token use where available. Distinguish actual tool execution from response-only behavior. Identify the evaluator and disclose limits such as small samples or grading by the same model family.

Do not claim novelty, measured superiority, model-wide compatibility, or successful side effects without supporting evidence. A static validator, a simulated run, and a real host session are separate evidence categories.

## Run verification locally

Use the local verification procedure documented in the README and include the exact commands and relevant output in the contribution:

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
```

Consult `python3 scripts/evaluate.py --help` for the evaluation runner interface. Running a help command is not a behavioral test. If no documented check covers your change, explain what you inspected and what remains untested.

Keep CI-style checks runnable locally. Do not add hosted GitHub Actions workflows as part of routine contributions. Avoid checks that require uploading private material or using credentials merely to validate package structure.

Add behavioral cases when they test a real failure or a meaningful boundary. Documentation-only changes generally need link, consistency, and formatting review rather than redundant behavioral tests.

For host changes, use the evidence categories and receipt fields in [compatibility](docs/compatibility.md). A discovery check does not prove automatic selection or correct task completion.

## Licensing and provenance

Submit material you are entitled to contribute under this repository's license. Identify third-party text, code, fixtures, and datasets, including their source, applicable license, and modifications.

Preserve required notices and attribution. A public URL or an open repository does not by itself grant permission to copy its contents. Do not import material with missing or incompatible licensing without resolving that issue first.

Research links can establish prior art without copying another project's instructions. Prefer an independently written explanation of the relevant behavior.

## A reviewable pull request

Include:

- The concrete problem and resulting behavior.
- The scope of the change and any compatibility impact.
- Verification performed, baseline evidence where relevant, and remaining gaps.
- Provenance and licensing for externally derived material.
- Changes needed to examples or documentation.

Keep unrelated refactors and speculative integrations out of the same change. Do not include fabricated test results or a success claim based only on intended behavior. Publishing, deployment, and changes to external systems remain separate actions from preparing a contribution.
