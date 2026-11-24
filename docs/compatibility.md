# Compatibility and verification

This document separates documented host support from evidence that a particular UAI release works in that host. UAI supplies instructions and reference material; the host supplies model behavior, skill discovery, context, permissions, and tools.

**Status for experimental 0.3.0:** the installation locations below were checked against official documentation on 2026-11-24. Claude Code 2.1.331 passed isolated local marketplace installation/discovery and cache-content verification. Four fresh collaboration-agent response checks were also reviewed. These do not establish automatic triggering or downstream tool behavior. Exact evidence and limitations are in [verification](verification.md).

## What each check establishes

| Evidence category | What a successful check establishes | What it does not establish |
| --- | --- | --- |
| Static conformance | Required files, frontmatter, references, and package structure satisfy the checks that were run. | Host installation, automatic selection, or useful behavior. |
| Installation and discovery | A named host version discovers the installed release. | That the host will select it for the right requests. |
| Explicit invocation | Deliberately invoking UAI loads the intended release. | Reliable automatic triggering. |
| Implicit triggering | In recorded positive and negative cases, the host selects or skips UAI as expected. | Correct completion after selection, or performance on untested prompts. |
| Output-level behavior | The assistant's response satisfies a stated rubric in a recorded environment. | That any claimed tool operation occurred. |
| Tool execution | Observed tool calls and resulting state satisfy the authorized task and its boundaries. | Behavior with other tools, permissions, models, or environments. |

A release report should name the category it tested. “Compatible,” “tested,” and “works” are otherwise too broad.

## Documented installation locations

| Host | Personal location | Project location | UAI verification status |
| --- | --- | --- | --- |
| Claude Code | `~/.claude/skills/understanding-ambiguous-intent/SKILL.md` | `.claude/skills/understanding-ambiguous-intent/SKILL.md` | Local marketplace installation/discovery verified in isolated configuration on 2.1.331. Manual-directory host discovery, triggering, and tool behavior remain unverified. |
| Codex local skill discovery | `$HOME/.agents/skills/understanding-ambiguous-intent/SKILL.md` | `.agents/skills/understanding-ambiguous-intent/SKILL.md` | Installation, discovery, triggering, behavior, and tools not yet verified here. |
| Other hosts or chat applications | Follow that host's own documented mechanism. | Host-dependent. | Not verified. Pasting instructions into a conversation is not evidence of native skill installation. |

Sources: [Claude Code skills documentation](https://code.claude.com/docs/en/skills) and [Codex / ChatGPT skills documentation](https://learn.chatgpt.com/docs/build-skills), inspected 2026-11-24. Local filesystem installation does not by itself install a skill into a separate cloud application.

### Proposed manual installation

These steps describe a manual installation procedure based on those documented locations. They are not a report of a completed installation.

1. Obtain the intended release. Its skill directory is `skills/understanding-ambiguous-intent/`, containing `SKILL.md` and its relative reference files.
2. Choose either the personal or project location for the target host.
3. Copy the complete skill directory to the destination named `understanding-ambiguous-intent`. Preserve relative paths. Inspect an existing installation before replacing it, and avoid ambiguous duplicate copies while testing.
4. Start or refresh the host's skill-discovery session according to its documentation.
5. Verify discovery and explicit invocation before testing automatic triggering. Record the release commit and the host's observed behavior.

Do not copy a repository wrapper containing another nested skill directory and assume the host will discover it. The destination must contain `SKILL.md` at the level shown in the table. The README also describes a local installer and Claude plugin loading. Each installation method requires its own discovery evidence; a test of one method does not establish the others.

## A useful verification session

Use a clean or clearly documented conversation so unrelated instructions do not silently change the result. Include at least:

- A clear request that needs no clarification.
- An ambiguous request where an available contextual fact resolves the ambiguity.
- A request with a consequential unknown that requires a focused question.
- A request to execute work and a separate request to rewrite a prompt.
- A user correction that changes the target or scope.
- A case with no external context or memory integration.
- A negative trigger case where loading UAI would add unnecessary process.

For tool tests, use a disposable task with explicitly defined permitted effects and inspect the resulting state. A response saying “done” is not execution evidence. Run output-only fixtures without tools when that is the intended test category.

## Recording results

A useful receipt includes:

- Date, UAI version and commit, host version, and model identifier.
- Installation method and whether invocation was explicit or implicit.
- Case identifiers, available context, other active instructions, and tool scopes.
- Exact local commands used where applicable.
- Redacted observable outputs, tool events, resulting state, and grading method.
- Failures, retries, untested categories, and environmental limitations.

Do not publish secrets, personal context, local identifiers, or raw private conversations as evidence. State whether a result comes from a real host session, a simulated actor, a static validator, or manual review. A result for one release does not automatically transfer to the next release.
