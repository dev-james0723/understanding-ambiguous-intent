# Context Bridge 0.4 candidate — requirements and implementation plan

## Product requirements
- R1: An owner can opt into a local, read-only, task-scoped bridge without changing the portable skill installation. Clear tasks and unavailable bridges still work normally.
- R2: Detect known candidate locations without reading content; require explicit source grants for retrieval. One server per user/workspace/project boundary. Personal grants are explicit; project grants never cross the boundary.
- R3: Search relevant bounded excerpts and retrieve an opaque record with source, timestamps, evidence kind, status and content hash. Do not treat instructions as authenticated user preferences or as new authority.
- R4: Provide eight read-only operations over a shared CLI and stdio MCP implementation. Explicitly identify incomplete scans, unavailable sources, stale records, conflicting keys and heuristic limits.
- R5: No writes to memory, telemetry, external calls or credential/config/session scraping. Fail closed on invalid scopes, unsafe paths and unsupported file types. No automatic cloud access.
- R6: Preserve the core's zero-runtime requirement, historical evidence and local CI. Publish synthetic fixtures only. Test the optional bridge in isolation; distinguish unit, protocol and actual host behavior.

## Engineering and ordered delivery
1. Preserve v0.3 baseline and branch; implement owner-supplied JSON grants with fixed scope, bounded adapter-specific file selection, descriptor-relative no-follow reads, size and scan limits. POSIX only initially. Candidate path suggestions are metadata only. Test R2/R5.
2. Parse Markdown/text and explicitly configured structured JSON/JSONL records; source content is untrusted. No transcripts, no automatic imports, no arbitrary recursive traversal. Preserve relative source refs, hashes, unknown timestamps, explicit status and logical keys. Keyword retrieval with Unicode/CJK support; no claimed semantic search. Test R3/R4.
3. Build CLI and optional MCP SDK stdio wrapper around same engine. MCP requests cannot grant paths or expand scope. Test all tools with synthetic fixtures, including a real SDK stdio client when the dependency is available.
4. Update core guidance, bilingual README, adapter documentation and candidate changelog/version consistency. Existing published verification remains scoped to v0.3.0. Run repository checker and test suite, review security boundaries and record actual evidence. No release tag or merge before verification.
5. Rollback: remove optional server registration and private config; the existing skill keeps working. No migration, source writes, daemon or persistence.

## Limitations and acceptance
Automatic discovery of private/custom locations is deliberately not inferred from other agents' configuration or logs. Claude/Codex private project memory roots must be explicitly supplied. Cloud memory requires host-native retrieval or a user-provided sanitized export. Adapter layouts are tested with synthetic fixtures, not proof of every host's native memory integration. Secret filtering is best-effort; grants and host isolation are the actual boundary. Local same-user arbitrary shell access is outside this boundary.
