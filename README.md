# UAI · Understanding Ambiguous Intent

**Turn imperfect instructions into the right next action.**

[繁體中文](README.zh-Hant.md) · [Runtime skill](skills/understanding-ambiguous-intent/SKILL.md) · [Verification](docs/verification.md) · [Research](docs/research.md)

UAI is a small, open-source instruction skill for agents handling rough,
incomplete, evolving, or multilingual requests. It helps the agent recover
the requested result, use relevant context, preserve constraints, and decide
when a question is actually needed.

**v0.4.0 is experimental.** The project does not claim to outperform a native
model or another skill. Read the published checks, outputs, and limitations
before deciding whether it helps your workflow.

The release includes optional local memory tools, correction and cancellation
guidance, and reproducible checks. Start with the core skill; add the Context
Bridge when your agent needs relevant information from selected local files.

## What changes in a conversation

| You say | Intended behavior |
|---|---|
| "Can you shorten this email?" | Return a shorter email. |
| "Polish this prompt: delete old backups." | Improve the prompt; do not delete files. |
| "Why do you prefer B?" | Explain the recommendation without treating it as approval. |
| "Do the same for mobile, keep everything else." | Recover the earlier change and retain the stated limits. |
| "幫我寫得自然啲，keep the technical terms." | Rewrite naturally while preserving the terms. |
| "Continue." | Continue the established, authorized task using available context. |

These are design examples, not measured results.

## Install

For Claude Code (distribution checked with 2.1.331), run:

```sh
claude plugin marketplace add dev-james0723/understanding-ambiguous-intent
claude plugin install understanding-ambiguous-intent@uai-public
```

For a manual or host-neutral installation, use the steps below.

The core needs no API key, account, server, Python runtime, or persistent memory.
Use any host that supports the Agent Skills folder format. The optional
installer below uses Python 3.10+ and never overwrites an existing installation.

Clone the repository and select the release:

```sh
git clone https://github.com/dev-james0723/understanding-ambiguous-intent.git
cd understanding-ambiguous-intent
git checkout v0.4.0
```

For a host that reads your user-level `.agents/skills` directory:

```sh
python3 scripts/install.py --target "$HOME/.agents/skills" --dry-run
python3 scripts/install.py --target "$HOME/.agents/skills"
```

For Claude Code's user-level skills directory:

```sh
python3 scripts/install.py --target "$HOME/.claude/skills"
```

Alternatively, copy **only**
`skills/understanding-ambiguous-intent/` into your host's documented skills
directory. Do not copy the repository root or evaluation folder into a skills directory.
If a UAI folder already exists, review and back it up separately; the
installer refuses to replace it. Do not install two competing UAI copies.

For a session-local Claude Code plugin, this repository also includes a
plugin manifest:

```sh
claude --plugin-dir /absolute/path/to/understanding-ambiguous-intent
```

Host loading, explicit invocation, automatic triggering, and behavior are
separate checks. See [compatibility](docs/compatibility.md). A folder copied
successfully does not prove that your host selected or followed it.

## Use

Ask your agent to use **Understanding Ambiguous Intent**, or invoke it through
your host's skill selector. Hosts supporting dollar-style skill invocation
can use:

```text
Use $understanding-ambiguous-intent to interpret this request and carry it out:
[request and relevant context]
```

UAI should stay unobtrusive on clear requests. It should not require a fixed
questionnaire, an intent worksheet, or a rewritten prompt before ordinary work.

## How it works

1. Identify the requested deliverable and the target.
2. Use relevant available context before asking for more.
3. Distinguish stated instructions/assertions, verified facts, inferences, and gaps.
4. Proceed, state a bounded assumption, or ask a material question.
5. Preserve scope, corrections, identifiers, and applicable authorization.
6. Deliver the requested result and report evidence proportionately.

It is designed for writing, research, planning, design, spreadsheets, and engineering.
The examples cover these domains; broad effectiveness across them remains
something to measure.

## Optional context

The core works from the current conversation. It does not collect background
sessions, access all history, write memories, or synchronize accounts.
A host can provide scoped context through its existing authorized tools.
The optional [UAI Context Bridge](docs/context-bridge.md)
adds a local, read-only CLI and eight MCP tools over explicitly granted files.
The core still works without it. It does not collect transcripts, synchronize
accounts or access cloud memory. The owner selects exact source roots and
project scope; candidate discovery is metadata only. See the existing
[adapter design contract](docs/context-adapters.md) and
[verification](docs/verification.md).

Try all eight operations against disposable synthetic memory:

```sh
python3 scripts/demo_context.py
```

To connect one selected memory folder, create a private configuration:

```sh
python3 scripts/configure_context.py --project demo --adapter claude-memory \
  --root /absolute/path/to/project/memory --out /absolute/path/to/private/uai.json
python3 scripts/uai_context_bridge.py --config /absolute/path/to/private/uai.json \
  build_intent_context demo "previous design decision"
```

Setup checks source availability without reading its contents and refuses to
overwrite an existing config. The eight retrieval operations remain read-only.
For a host to call them automatically when relevant, register the optional MCP
server using the [setup guide](docs/context-bridge.md). Host discovery and model
tool selection are separate verification categories.

## Corrections, continuation and examples

UAI preserves the active goal and unaffected constraints when you revise a
detail. A status question during ongoing work should not silently end the task;
an explicit cancellation should stop its pending actions. Hosts can use the
optional [handoff reference](skills/understanding-ambiguous-intent/references/task-continuity.md)
with their existing task state.

See [three worked examples](docs/examples.md) for multilingual corrections,
task continuation and a current instruction that supersedes an old memory.

## Check and evaluate locally

```sh
python3 scripts/check.py
python3 -m unittest discover -s tests -v
python3 scripts/evaluate.py --help
python3 scripts/compare_results.py --help
```

The evaluation fixtures keep prompts separate from rubrics. Compare the
same model and host without UAI, with a short instruction, and with UAI.
Save actual responses, judge task completion and user effort, and retain
ties and regressions. See [evaluation instructions](evals/README.md) and
[verification](docs/verification.md).

The [published development comparison](evals/results/2026-11-25/comparison/README.md)
recorded 21/24 original-rubric passes for each condition, with all paired
outcomes tied. It does not establish an advantage for UAI.

A structural check is not an agent behavior test. A response-only test is
not an end-to-end tool-use test. Public cases are not a held-out benchmark.

## Project layout

- `skills/understanding-ambiguous-intent/`: the installable runtime skill.
- `scripts/`: local install, package checks, and opt-in evaluation utilities.
- `context_bridge/`: optional local retrieval engine, CLI and MCP transport.
- `evals/`: synthetic prompts, separate rubrics, and reviewed evidence.
- `docs/`: research, compatibility, context design, and verification.
- `tests/`: tests for retrieval, protocol, setup, distribution and evaluation utilities.

## Contribute

Share a sanitized request, the minimum relevant context, intended result,
actual result, and host/model/version. Do not submit private chat histories.
The repository's issue template walks through these fields. See [CONTRIBUTING](CONTRIBUTING.md). Research and prior art are acknowledged
in [the research note](docs/research.md).

## License

[MIT](LICENSE), copyright James Au. Research links acknowledge related work;
third-party skills are not bundled. No claim of being the first or best intent
skill is made.
