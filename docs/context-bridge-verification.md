# Context Bridge candidate verification

Historical record of the initial unshipped candidate. The subsequent release
repairs and current evidence are in [release verification](verification.md).
The limitations below describe that candidate at the time, not the final release.

2026-11-25, experimental 0.4.0 candidate, based on v0.3.0 commit 8beb419.
The previous published v0.3.0 report remains historical evidence only.

## Observed local results

- macOS ARM64, Python 3.15.2: original 12 distribution/evaluation-integrity
  tests passed; dependency-free structure/version/link check passed.
- Python 3.12.8 with isolated MCP SDK 1.30.0: 34 tests passed, comprising
  12 original tests, 21 bridge tests, and one real MCP stdio protocol test.
- The protocol test launched the absolute-path entry point in a separate
  working directory, initialized an SDK client session, listed eight read-only
  tools, exercised all eight operations and rejected an out-of-scope project.
- Synthetic fixtures exercised all eight named adapter layouts and custom
  Markdown/text/JSON/JSONL, source provenance, Unicode keywords, expiry,
  conflicts, bounded requests, credential patterns, symlink/hardlink and
  directory replacement, FIFO, bad input, unavailable sources and no source
  mutations. No real user memory, credentials or live history were used.
- git diff --check passed. No GitHub Actions added.

## Not established

The SDK protocol test is not a Claude Code, Codex, Gemini CLI, Cursor,
OpenClaw, Hermes or cloud ChatGPT native host test. No automatic host
triggering, broad semantic search, model performance improvement, cross-host
account synchronization, Linux/Windows runtime validation or production
release is claimed. Independent review is a separate gate; its outcome is
not established by these tests. Do not publish this candidate as verified
across all hosts. The release remains untagged.

## Independent reviewer attempts

Codex was unavailable because the existing subscription reached its usage
limit. Claude's isolated minimal-mode attempt did not authenticate; the
existing subscription's default model had reached its model limit, and the
Sonnet fallback did not produce a review within the bounded 60-second
invocation. No reviewer verdict was obtained. Independent review remains
unverified; no paid credits were purchased and no release tag was created.
