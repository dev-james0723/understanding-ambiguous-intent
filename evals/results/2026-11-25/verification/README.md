# Code and native-host receipts

These receipts record prepublication checks of the integration source and
frozen runtime. The final exact public commit and publication-time checks are
in `release-verification.json` attached to the GitHub v0.4.0 prerelease.
The release is assembled from the reviewed file tree, so internal integration
commit IDs need not appear in the public commit history.

| Receipt | Scope |
| --- | --- |
| [Linux](linux.json) | 78 tests, repository and skill validators, CLI/MCP demo, diff check; Python 3.12.14 and MCP 1.29.0. |
| [macOS](macos.json) | 78 tests, repository checker, CLI/MCP demo, diff check; Python 3.12.8 and MCP 1.30.0. |
| [Claude local distribution](claude-local-distribution.json) | Disposable local marketplace install, manifest checks, enabled listing, native inventory and runtime hash. |
| [Codex discovery](codex-discovery.json) | Native app-server project skill discovery and enabled repo scope. |
| [Native MCP configuration](native-mcp-registration.json) | Claude connection and Codex process-only configuration/listing. |

Linux/macOS receipts identify their adjacent logs by SHA-256. All bridge sources
were synthetic. Native checks did not invoke a model. Listing, connection and
model selection are distinct. Temporary paths in the MCP receipt use descriptive
placeholders; the recorded response meaning is unchanged.
