"""Real stdio MCP protocol smoke test; optional SDK, synthetic memory only."""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from context_bridge.core import OPERATIONS

ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(os.name == "posix" and importlib.util.find_spec("mcp"),
                     "optional MCP SDK and POSIX required")
class MCPTransportTests(unittest.TestCase):
    def test_real_stdio_all_tools(self):
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client

        async def check(config_path):
            params = StdioServerParameters(
                command=sys.executable,
                args=[str(ROOT / "scripts/uai_context_bridge.py"), "--config", str(config_path), "serve"],
                cwd=str(config_path.parent),
            )
            async with stdio_client(params) as (reader, writer):
                async with ClientSession(reader, writer) as session:
                    await session.initialize()
                    tools = (await session.list_tools()).tools
                    self.assertEqual({t.name for t in tools}, set(OPERATIONS))
                    self.assertTrue(all(t.annotations.readOnlyHint for t in tools))
                    self.assertTrue(all("root" not in t.inputSchema.get("properties", {}) for t in tools))
                    async def call(name, **args):
                        result = await session.call_tool(name, {"project": "demo", **args})
                        self.assertFalse(result.isError, str(result))
                        data = result.structuredContent
                        if data is None:
                            data = json.loads(result.content[0].text)
                        if "result" in data and isinstance(data["result"], dict):
                            data = data["result"]
                        return data
                    self.assertEqual(len((await call("discover_memory_sources"))["records"]), 1)
                    self.assertEqual(len((await call("list_memory_sources"))["records"]), 1)
                    record = (await call("search_memory", query="violet"))["records"][0]
                    self.assertTrue((await call("read_memory", record_id=record["record_id"]))["found"])
                    self.assertTrue((await call("get_user_preferences", query="violet"))["records"])
                    self.assertTrue((await call("get_project_context", query="violet"))["records"])
                    self.assertEqual((await call("resolve_memory_conflicts", query="violet"))["conflicts"], [])
                    self.assertTrue((await call("build_intent_context", query="violet"))["records"])
                    denial = await session.call_tool("search_memory", {"project": "other", "query": "violet"})
                    data = denial.structuredContent or json.loads(denial.content[0].text)
                    if "result" in data and isinstance(data["result"], dict):
                        data = data["result"]
                    self.assertEqual(data["status"], "error")
                    self.assertEqual(data["records"], [])
                    self.assertNotIn("synthetic violet", json.dumps(data))

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            memory = root / "memory"
            memory.mkdir()
            (memory / "MEMORY.md").write_text("synthetic build uses violet")
            (memory / "USER.md").write_text("synthetic violet preference")
            config = root / "grants.json"
            config.write_text(json.dumps({"schema_version": 1, "user": "tester", "workspace": "demo",
                "project": "demo", "sources": [{"id": "fixture", "adapter": "hermes",
                "root": str(memory), "scope": "project:demo"}]}))
            config.chmod(0o600)
            asyncio.run(asyncio.wait_for(check(config), timeout=30))

if __name__ == "__main__":
    unittest.main()
