# Compatibility and verification

This document separates documented host support from evidence that a particular UAI release works in that host. UAI supplies instructions and reference material; the host supplies model behavior, skill discovery, context, permissions, and tools.

**Status for experimental 0.4.0:** Claude Code 2.1.331 passed strict manifest checks, isolated marketplace installation, enabled-plugin listing, native inventory and installed-content verification. Codex CLI 0.171.0's native app-server `skills/list` discovered and enabled the project-installed runtime at its exact file path and hash. Neither operation invoked a model. Automatic triggering and native model tool selection remain separate checks. Exact behavior and protocol evidence are in [verification](verification.md).

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
| Claude Code | `~/.claude/skills/understanding-ambiguous-intent/SKILL.md` | `.claude/skills/understanding-ambiguous-intent/SKILL.md` | Isolated local marketplace installation, listing, inventory and runtime hash verified on 2.1.331. Manual-directory discovery and automatic model triggering remain unverified. |
| Codex local skill discovery | `$HOME/.agents/skills/understanding-ambiguous-intent/SKILL.md` | `.agents/skills/understanding-ambiguous-intent/SKILL.md` | Project installation and native discovery verified on 0.171.0 through `skills/list`. Automatic model triggering and model-driven execution in Codex remain unverified. |
| Other hosts or chat applications | Follow that host's own documented mechanism. | Host-dependent. | Not verified. Pasting instructions into a conversation is not evidence of native skill installation. |

Sources: [Claude Code skills documentation](https://code.claude.com/docs/en/skills) and [Codex / ChatGPT skills documentation](https://learn.chatgpt.com/docs/build-skills), inspected 2026-11-24. Local filesystem installation does not by itself install a skill into a separate cloud application.

### Manual installation

These steps describe the manual procedure. The table above identifies which specific paths were actually exercised.

1. Obtain the intended release. Its skill directory is `skills/understanding-ambiguous-intent/`, containing `SKILL.md` and its relative reference files.
2. Choose either the personal or project location for the target host.
3. Copy the complete skill directory to the destination named `understanding-ambiguous-intent`. Preserve relative paths. Inspect an existing installation before replacing it, and avoid ambiguous duplicate copies while testing.
4. Start or refresh the host's skill-discovery session according to its documentation.
5. Verify discovery and explicit invocation before testing automatic triggering. Record the release commit and the host's observed behavior.

Do not copy a repository wrapper containing another nested skill directory and assume the host will discover it. The destination must contain `SKILL.md` at the level shown in the table. The README also describes a local installer and Claude plugin loading. Each installation method requires its own discovery evidence; a test of one method does not establish the others.

## Optional memory tool compatibility

The Context Bridge CLI requires Python 3.10+ and the implemented POSIX filesystem
operations. Its optional MCP transport requires the SDK listed in
`context_bridge/requirements-mcp.txt` and a compatible Python interpreter.
Linux CLI/stdio tests and macOS distribution checks are reported separately.
Windows file access is not implemented.

The named Claude, Codex, OpenClaw, Hermes, Gemini and Cursor adapters recognize
selected local file layouts. They are not native account integrations. An MCP
host must be configured separately to expose the eight tools, and the calling
model decides whether to use them. A successful SDK client/server exchange does
not establish automatic tool selection in a named application.

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
