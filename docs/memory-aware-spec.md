# UAI 0.4.0 — Memory-aware release specification

## Outcome

Make the existing portable intent skill usable with relevant local agent memory,
preserve task intent through corrections and continuation, and publish evidence
that distinguishes instruction behavior, tool effects, installation and discovery.
This release builds on the existing Context Bridge candidate; it does not replace
another author's work or claim comparative superiority without measured evidence.

## Product requirements and acceptance

| ID | Requirement | Acceptance |
|---|---|---|
| R1 | Optional read-only memory retrieval | Shared CLI and MCP engine discovers granted sources, searches bounded excerpts and rereads records with source, scope and freshness metadata. All eight existing operations work over synthetic files; source bytes remain unchanged. |
| R2 | Relevant, accurate source handling | Tests cover stale identifiers, changed metadata, conflicts, long text, Unicode queries, unavailable sources, exact source boundaries and partial results. Source text never becomes permission. |
| R3 | Usable setup | A documented first-run demonstration works in a fresh checkout. Public config examples are synthetic. Host registration examples use absolute paths and preserve existing installations. |
| R4 | Task continuity | The skill preserves goals and unaffected constraints after corrections, answers status without cancelling authorized work, and stops stale objectives after explicit cancellation. A lightweight handoff reference supports hosts that persist task state. |
| R5 | Comparative evidence | Evaluate the original 24 response cases under baseline, brief and UAI instructions, with fresh sessions, separate rubrics and raw outputs. Record host/model metadata limitations, ties, failures and missing runs. Add boundary pairs and multi-turn trajectories. |
| R6 | Observable real effects | Run the bridge through real MCP stdio and command-line clients. Exercise agent-assisted retrieval and a harmless artifact change in an isolated fixture, checking tool evidence and final bytes. Never infer tool success from a written answer. |
| R7 | Distribution | Verify package/manifest/version consistency, fresh remote installation where supported, and native discovery without changing personal installations. Clearly distinguish loaded, triggered and behavior-verified states. |
| R8 | Public usability | English and Traditional Chinese quick starts, three concrete examples, a reproducible local demo and a structured failure-report template. No private paths, memory, transcripts, credentials or required hosted service. |
| R9 | Release | Local checks, independent review and verified public GitHub release. Preserve v0.3.0 and document rollback. Update the existing private library's public-release pointer in an isolated worktree. |

## Architecture

The portable runtime remains in `skills/understanding-ambiguous-intent/`.
The optional `context_bridge/` package implements a fixed launch-time project
and explicit source grants. `scripts/uai_context_bridge.py` exposes its CLI and
optional MCP transport. The bridge reads selected files; it has no memory writer,
network retrieval, database, background collector or scheduler. The invoking host
supplies persistence and actual task execution.

The existing eight operations and config schema remain compatible. Defects found
by review receive focused regression tests before repair. Provenance must identify
full source changes, even when the returned excerpt is bounded. Truncated content
and malformed metadata cannot silently acquire current or verified status.

Evaluation generation inputs stay separate from answer rubrics. Public static
fixtures are development/regression cases, not held-out evidence. ChatGPT fresh
agent sessions may provide an exploratory matched-harness comparison; unexposed
model/sampling metadata must be recorded as unknown. No paid external fallback or
other subscription model is invoked for this release workflow.

## Scope and decisions

- Python 3.10+ for the optional CLI; the core needs no runtime.
- POSIX filesystem implementation; macOS and Linux are tested separately.
- Existing optional MCP dependency remains isolated and explicitly declared.
- Local tests only; do not add or dispatch GitHub Actions.
- No personal UAI installation is overwritten by a distribution check.
- No benchmark winner, universal host support or semantic search claim.
- Existing user authorization covers implementation, integration and publication.
- The current ChatGPT session owns integration; independent agents review artifacts.

## Delivery and rollback

Ship an experimental v0.4.0 release after relevant gates pass. Pin published
evidence to the tested source revision or content hashes. Keep missing native
model-host checks visible rather than substituting protocol success. Consumers
can return to v0.3.0; removing the optional MCP registration removes the bridge
without changing their memory files. Existing private plugin releases are separate.
