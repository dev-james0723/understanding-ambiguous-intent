#!/usr/bin/env python3
"""Exercise UAI Context Bridge using disposable synthetic memory only."""
import argparse
import asyncio
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "scripts" / "uai_context_bridge.py"


def require(value, message):
    if not value:
        raise RuntimeError(message)


def cli(config, operation, *args):
    run = subprocess.run([sys.executable, str(ENTRY), "--config", str(config),
                          operation, "demo", *args], cwd=config.parent,
                         text=True, capture_output=True, timeout=20)
    require(run.returncode == 0, "CLI operation failed: " + operation)
    return json.loads(run.stdout)


async def protocol(config):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    params = StdioServerParameters(command=sys.executable,
        args=[str(ENTRY), "--config", str(config), "serve"], cwd=str(config.parent))
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            require(len(tools) == 8, "MCP did not expose all eight operations")
            result = await session.call_tool("build_intent_context",
                {"project": "demo", "query": "brand", "limit": 4})
            require(not result.isError, "MCP context request failed")
            data = result.structuredContent or json.loads(result.content[0].text)
            data = data.get("result", data)
            require(any("Aurora Notes" in r["content"] for r in data["records"]),
                    "MCP did not retrieve the current brand")
            return {"tools_discovered": len(tools), "retrieval_verified": True}


def run_demo(use_mcp=False):
    with tempfile.TemporaryDirectory(prefix="uai-synthetic-demo-") as directory:
        root = Path(directory).resolve()
        memory = root / "memory"
        memory.mkdir()
        records = [
            {"content": "The project brand is Aurora Notes.", "key": "brand",
             "status": "active", "evidence_type": "user_correction"},
            {"content": "The project brand was Ember Notes.", "key": "brand",
             "status": "expired", "evidence_type": "stated_preference"},
            {"content": "The meeting time is 11:00.", "key": "meeting-time", "status": "active"},
            {"content": "The meeting time is 12:00.", "key": "meeting-time", "status": "active"},
            {"content": "Neutral context. " * 100 + "The accent is copper.",
             "status": "active"},
        ]
        notes = memory / "decisions.json"
        notes.write_text(json.dumps(records), encoding="utf-8")
        config = root / "grants.json"
        config.write_text(json.dumps({"schema_version": 1, "user": "demo-user",
            "workspace": "demo-workspace", "project": "demo", "sources": [{
                "id": "notes", "adapter": "custom", "root": str(memory),
                "scope": "project:demo", "files": ["decisions.json"]}]}), encoding="utf-8")
        config.chmod(0o600)
        original_hash = hashlib.sha256(notes.read_bytes()).hexdigest()
        checks = {}
        for operation in ("discover_memory_sources", "list_memory_sources"):
            require(cli(config, operation)["records"][0]["available"], "Source unavailable")
        checks["granted_source_discovery"] = True
        search = cli(config, "search_memory", "brand")
        current = next(r for r in search["records"] if "Aurora Notes" in r["content"])
        require(cli(config, "read_memory", current["record_id"])["found"], "Record reread failed")
        require(cli(config, "get_user_preferences", "brand")["records"], "Preference lookup failed")
        require(cli(config, "get_project_context", "brand")["records"], "Project lookup failed")
        checks["search_read_preferences_project"] = True
        intent = cli(config, "build_intent_context", "brand")
        require(any(r["status"] == "active" and "Aurora Notes" in r["content"]
                    for r in intent["records"]), "Intent did not retrieve the current brand")
        require(all(r["status"] != "expired" for r in intent["records"]), "Expired context escaped")
        require(any(r["status"] == "expired" for r in search["records"]), "Historical search lost expiry")
        checks["expired_history_excluded_from_intent"] = True
        conflicts = cli(config, "resolve_memory_conflicts", "meeting")
        require(len(conflicts["conflicts"]) == 1, "Keyed conflict was hidden")
        checks["conflict_reported"] = True
        tail = cli(config, "search_memory", "copper")["records"]
        require(tail and "copper" in tail[0]["content"], "Long-record tail was lost")
        require(all(len(r["content"]) <= 1200 for r in tail), "Excerpt budget exceeded")
        checks["bounded_tail_search"] = True
        mcp_result = asyncio.run(asyncio.wait_for(protocol(config), timeout=30)) if use_mcp else None
        require(hashlib.sha256(notes.read_bytes()).hexdigest() == original_hash, "Retrieval changed source bytes")
        checks["retrieval_left_source_unchanged"] = True
        # The demo owner changes its own synthetic fixture, not the retrieval engine.
        records[0]["status"] = "archived"
        notes.write_text(json.dumps(records), encoding="utf-8")
        edited_hash = hashlib.sha256(notes.read_bytes()).hexdigest()
        require(not cli(config, "read_memory", current["record_id"])["found"], "Changed metadata retained stale ID")
        checks["changed_metadata_invalidates_record_id"] = True
        config_data = json.loads(config.read_text())
        config_data["sources"].append({"id": "missing", "adapter": "claude-memory",
            "root": str(root / "unavailable"), "scope": "project:demo"})
        config.write_text(json.dumps(config_data), encoding="utf-8")
        partial = cli(config, "search_memory", "copper")
        require("missing: root unavailable or unsafe" in partial["warnings"], "Missing source diagnostic was not reported")
        require(partial["status"] == "partial" and any(
            r["source_id"] == "notes" and "The accent is copper." in r["content"]
            for r in partial["records"]), "Partial retrieval discarded useful evidence")
        checks["unavailable_source_reported_with_useful_results"] = True
        require(hashlib.sha256(notes.read_bytes()).hexdigest() == edited_hash, "Retrieval changed source bytes after fixture edit")
        checks["post_edit_retrieval_left_source_unchanged"] = True
        return {"status": "passed", "scope": "synthetic-local-cli-and-optional-mcp",
                "checks": checks, "cli_operations_exercised": 8,
                "mcp": mcp_result, "real_user_memory_read": False,
                "native_host_triggering_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp", action="store_true", help="Also exercise the optional MCP SDK stdio transport")
    args = parser.parse_args()
    try:
        print(json.dumps(run_demo(args.mcp), ensure_ascii=False, indent=2))
        return 0
    except (ImportError, OSError, RuntimeError, ValueError, subprocess.SubprocessError):
        print(json.dumps({"status": "failed", "error": "Demo operation failed; install the optional SDK for --mcp and run the test suite for diagnostics."}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
