import importlib.util
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from context_bridge.core import Bridge, BridgeError, load_config

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("configure_context", ROOT / "scripts/configure_context.py")
configuration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(configuration)


@unittest.skipUnless(os.name == "posix", "POSIX bridge required")
class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.memory = self.root / "memory"
        self.memory.mkdir()
        self.note = self.memory / "MEMORY.md"
        self.note.write_text("The display accent is silver.")
        self.output = self.root / "private/demo.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_setup_creates_private_usable_grant_without_reading_source(self):
        with patch("context_bridge.core.read_regular", side_effect=AssertionError("setup read memory")):
            result = configuration.configure(self.output, self.memory, "demo", "hermes")
        self.assertFalse(result["memory_content_read"])
        self.assertFalse(result["host_registered"])
        self.assertEqual(stat.S_IMODE(self.output.stat().st_mode), 0o600)
        bridge = Bridge(load_config(self.output))
        self.assertIn("silver", bridge.search_memory("demo", "silver")["records"][0]["content"])
        self.assertEqual(self.note.read_text(), "The display accent is silver.")

    def test_existing_config_and_symlink_are_preserved(self):
        self.output.parent.mkdir()
        self.output.write_text("owner configuration")
        with self.assertRaises(FileExistsError):
            configuration.configure(self.output, self.memory, "demo", "hermes")
        self.assertEqual(self.output.read_text(), "owner configuration")
        link = self.root / "link.json"
        link.symlink_to(self.output)
        with self.assertRaises(FileExistsError):
            configuration.configure(link, self.memory, "demo", "hermes")
        self.assertEqual(self.output.read_text(), "owner configuration")

    def test_retargeted_source_alias_does_not_change_grant(self):
        alias = self.root / "selected-memory"
        alias.symlink_to(self.memory, target_is_directory=True)
        configuration.configure(self.output, alias, "demo", "hermes")
        other = self.root / "other-memory"
        other.mkdir()
        (other / "MEMORY.md").write_text("The display accent is unapproved gold.")
        alias.unlink()
        alias.symlink_to(other, target_is_directory=True)

        result = subprocess.run([sys.executable, str(ROOT / "scripts/uai_context_bridge.py"),
            "--config", str(self.output), "search_memory", "demo", "accent"],
            text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        records = json.loads(result.stdout)["records"]
        self.assertTrue(records)
        self.assertTrue(all("silver" in record["content"] for record in records))
        self.assertEqual(json.loads(self.output.read_text())["sources"][0]["root"],
                         str(self.memory))

    def test_invalid_or_unavailable_source_does_not_create_output(self):
        for adapter, root in (("unknown", self.memory), ("hermes", self.root / "missing")):
            with self.assertRaises(BridgeError):
                configuration.configure(self.output, root, "demo", adapter)
            self.assertFalse(self.output.exists())

    def test_custom_files_and_instruction_context_are_explicit(self):
        (self.memory / "AGENTS.md").write_text("Use concise project summaries.")
        with self.assertRaises(BridgeError):
            configuration.configure(self.output, self.memory, "demo", "custom", ["AGENTS.md"])
        configuration.configure(self.output, self.memory, "demo", "custom", ["AGENTS.md"], True)
        data = json.loads(self.output.read_text())
        self.assertTrue(data["sources"][0]["include_instruction_context"])
        record = Bridge(data).search_memory("demo", "summaries")["records"][0]
        self.assertEqual(record["source_kind"], "instruction_context")


if __name__ == "__main__":
    unittest.main()
