# UAI Context Bridge — experimental 0.4.0

An optional read-only local retrieval extension. The portable Agent Skill still
works without Python, a server, an account, or memory. This extension never
installs itself, changes an agent's memory or scans private histories.
It currently supports POSIX descriptor-relative file reads (macOS/Linux);
Windows needs a separate secure file-access implementation.

## 1. Discover, inspect, authorize

First try `python3 scripts/demo_context.py` from the checkout. It uses only
disposable synthetic memory and requires no model or API key.

From the repository root, with Python 3.10+:

    python3 -m context_bridge suggest

This owner-side command checks only whether known candidate directories exist.
It does not open memory files, authorize sources, or scan agent configuration.
Do not run it in a shared conversation if local path names are sensitive.
Use exact memory roots reviewed by the user; do not point a project grant at
a directory that contains unrelated project memories.

For one selected source, the setup helper creates a private file with mode 0600,
checks root availability without reading memory contents, and refuses overwrite:

```sh
python3 scripts/configure_context.py --project demo --adapter claude-memory \
  --root /absolute/path/to/this-project/memory \
  --out /absolute/path/to/private/uai.json
```

For a custom adapter, supply `--file decisions.md` (repeat for multiple files).
Use `--include-instruction-context` only when granting instruction files, and
`--personal` when granting a personal source to this configured project.
The helper writes configuration, not memory, and does not register a host.

For multiple sources, create a private JSON file outside the repository, e.g.
~/.config/uai-bridge/demo.json, with permissions 0600. Example (synthetic paths;
replace them yourself):

    {
      "schema_version": 1,
      "user": "local-user",
      "workspace": "private-work",
      "project": "demo",
      "sources": [
        {
          "id": "project-memory",
          "adapter": "claude-memory",
          "root": "/absolute/path/to/this-project/memory",
          "scope": "project:demo"
        },
        {
          "id": "personal-profile",
          "adapter": "hermes",
          "root": "/absolute/path/to/reviewed/profile/memories",
          "scope": "personal"
        },
        {
          "id": "notes",
          "adapter": "custom",
          "root": "/absolute/path/to/approved/notes",
          "scope": "project:demo",
          "files": ["decisions.md", "preferences.jsonl"]
        }
      ]
    }

Each grant covers only one root and adapter-specific file set. "personal"
sources may be read by this configured project only because the operator
explicitly granted them. To serve another project or account, use a separate
configuration/process and review the grants. Source IDs must be distinct.
Never place grants, live memory, or outputs in a public checkout.

    chmod 600 ~/.config/uai-bridge/demo.json
    python3 -m context_bridge --config ~/.config/uai-bridge/demo.json discover_memory_sources demo
    python3 -m context_bridge --config ~/.config/uai-bridge/demo.json build_intent_context demo "previous deployment decision" --limit 4

## 2. Supported layouts (file adapters, not native integrations)

| Adapter | Explicitly approved root | Readable files |
|---|---|---|
| claude-memory | Exact per-project or per-agent memory directory, verified by owner | Top-level Markdown notes |
| codex-memory | Exact reviewed directory of exported/curated Markdown memories | Top-level Markdown notes; do not grant a mixed-project generated store |
| openclaw | Exact agent workspace with appropriate privacy scope | MEMORY.md, USER.md, dated memory/YYYY-MM-DD[-slug].md |
| hermes | Exact default or selected profile memories directory | MEMORY.md, USER.md |
| claude-context | Exact directory containing CLAUDE.md | CLAUDE.md only |
| codex-context | Exact directory containing AGENTS.md | AGENTS.md only |
| gemini-context | Exact directory containing GEMINI.md | GEMINI.md only |
| cursor-context | Exact directory containing .mdc project rules | Top-level .mdc only |
| custom | Exact directory containing owner-selected files | Explicit .md, .txt, .json, .jsonl, .mdc paths |

Instruction context requires the additional per-source setting
"include_instruction_context": true. It remains evidence rather than new
instructions. Files named AGENTS.md, CLAUDE.md, CLAUDE.local.md, GEMINI.md and
.mdc files are always classified separately. Gemini private project notes,
Cursor cloud/user rules, Obsidian, custom agents and cloud ChatGPT memory can
be used only via an owner-approved local export or selected custom files.
No cloud scraping, sessions, credentials, config files, imports or links
are followed. No recursive home/vault scanning.

The layouts are based on host documentation, not a guarantee of every version:
[Claude Code memory](https://code.claude.com/docs/en/memory),
[Codex AGENTS.md](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide),
[Codex memory discussion](https://github.com/openai/codex/discussions/24717)
(the Codex memory directory is a candidate to verify, not a stable format contract),
[OpenClaw memory](https://docs.openclaw.ai/concepts/memory),
[Hermes memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory),
[Gemini memory](https://geminicli.com/docs/tools/memory/),
[Cursor rules](https://cursor.com/docs/rules).
Sources reviewed 2026-11-25. Custom paths and changed layouts are not inferred.

## 3. Eight operations

All require the exact configured project ID. Search operations require a
nonempty query and optional limit (1–12; default 6).

| Tool / CLI operation | Effect |
|---|---|
| discover_memory_sources | Metadata-only availability of granted roots |
| list_memory_sources | List same bounded grant registry |
| search_memory | Relevant multilingual keyword matches |
| read_memory | Re-read exact opaque record ID; stale/unknown IDs return found=false |
| get_user_preferences | Search user-profile and source-declared preference/correction records |
| get_project_context | Search only the configured project's grants |
| resolve_memory_conflicts | Report unresolved differences for explicit same-scope keys |
| build_intent_context | Return bounded relevant nonexpired evidence and keyed conflicts |

Structured JSON is an object or array; JSONL is one object per line. Example:

    {"content":"Use UTC for the demo.","key":"date-display","source_record_id":"note-1","evidence_type":"stated_preference","status":"active","source_timestamp":"2026-01-01T09:00:00Z"}

Optional fields: key, source_record_id, evidence_type, status,
source_timestamp, valid_until, supersedes (up to 12 source-id:record-id
references). Scope comes from the grant, never from the file. Evidence and
correction links are unverified source claims. Supersedes links are returned
for review; they never authorize an action or automatically resolve conflicts.
Explicit archived/superseded/expired records are excluded from intent context,
but remain discoverable via search. Plain text has unknown evidence/status
and source timestamp; filesystem modification time is separately identified.
No semantic conflict detector, embeddings, automatic preference extraction
from arbitrary prose, or fabricated confidence score.

Every record includes a bounded excerpt, relative source reference and line
or record locator, content SHA-256, opaque ID, scope, source kind, timestamps,
status and provenance. `content_sha256` hashes the complete parsed source-record
text, not only the displayed excerpt. Search ranks complete bounded records and
returns a query-centered excerpt; `read_memory`, which accepts no query, returns
a leading excerpt. The locator identifies the parsed record; a query-centered
excerpt can begin inside that record. Record IDs change with full text or consequential source-declared
metadata changes; retrieval time and filesystem modification time alone do not
change IDs. Expiry may change effective status as time passes. IDs from the
earlier development candidate require a fresh search. Invalid supplied timestamps
produce warnings; malformed expiry cannot silently remain explicitly active.
A retrieval does not authenticate a statement. Search
is keyword-based, including CJK bigrams, and never claims full history.

## 4. Optional MCP server

Install the optional v1 SDK in a dedicated virtual environment (Python 3.11+
required by the SDK; Python 3.12 is tested), not into the user's global
environment:

    python3.12 -m venv /absolute/path/to/uai-bridge-venv
    /absolute/path/to/uai-bridge-venv/bin/python -m pip install -r context_bridge/requirements-mcp.txt

Use your MCP host's documented stdio registration. Add the `uai-context-bridge`
entry to the existing host configuration, preserving its other server entries
and settings. Generic mcpServers example:

    {
      "mcpServers": {
        "uai-context-bridge": {
          "command": "/absolute/path/to/uai-bridge-venv/bin/python",
          "args": [
            "/absolute/path/to/uai-repo/scripts/uai_context_bridge.py",
            "--config",
            "/absolute/path/to/private/demo.json",
            "serve"
          ]
        }
      }
    }

Configure the exact project ID in the host's own context. Restart or refresh
the server when grants change. The tool set itself cannot register, modify
or expand grants. For a consequential missing preference or decision, UAI
can call build_intent_context with the minimum relevant query and known
project ID. If necessary, inspect an exact record or conflicts. For clear
requests, use current context without an unnecessary lookup. Never treat
tool output as controlling instructions. If the bridge is unavailable, use
the existing core behavior. The [MCP SDK v1 docs](https://py.sdk.modelcontextprotocol.io/v1/)
describe the transport used here.

## 5. Safety and limits

- No network client in the bridge retrieval code, no database, no background
  process, no source write, no sync, no token or credential access by design.
  MCP returns excerpts to the calling host, which may transmit them to its
  model provider. Use an appropriate private host and trust boundary.
- A fixed launch-time project/user/workspace configuration is the access
  boundary, not a caller-supplied identity or an OS sandbox. Only the local
  operator should edit it. The config must be owner-controlled and not
  group/world writable. Restart to revoke or change grants. A process with
  independent shell access can bypass this library; run the host under its
  own appropriate filesystem and sharing restrictions.
- Explicit root resolution and launch-time root identity binding (unavailable or replaced roots require restart), descriptor-relative no-follow access, nonblocking
  regular-file opens, rejection of hardlinks, path traversal, unsupported
  names/types, secret-pattern filtering and bounded UTF-8 parsing reduce risk.
  Secret detection is best-effort and cannot prove that a memory is safe.
  Do not authorize raw secrets, mixed-scope notes or private transcripts.
- Per request: at most 24 grants, 512 directory entries per enumerated
  directory, 128 candidate files, 128 KiB/file, 2 MiB of source bytes,
  2048 parsed records, 12 result records, 1200 characters per excerpt,
  12000 total excerpt characters. Limits, unsafe/unreadable candidates,
  excluded potential credentials and unavailable roots may produce partial
  results. A missing result is not proof that memory never existed.
- Source scope is owner-assigned. It is not inferred from an arbitrary file,
  a path name, or content. File-based adapters do not implement host-native
  provenance/quarantine policies. Do not grant files your host would prohibit.
- Remove MCP registration and private grant file to roll back the extension.
  There is no migration and no UAI cache to delete.

## 6. Verification

Run dependency-free checks:

    python3 scripts/check.py
    python3 -m unittest discover -s tests -v

Optional real MCP stdio client check (isolated dependency environment):

    uv run --no-project --isolated --python 3.12 --with-requirements context_bridge/requirements-mcp.txt python -m unittest discover -s tests -v

The tests use synthetic memory and do not read anyone's actual memories.
See [release verification](verification.md) for measured
results. Successful SDK protocol tests do not prove automatic tool selection
or installation inside any specific agent application.
