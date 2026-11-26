"""Exercise the public first-run path from an unrelated working directory."""
import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("demo_context", ROOT / "scripts/demo_context.py")
demo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(demo)


class DemoTests(unittest.TestCase):
    def test_public_demo_runs_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            before = list(Path(directory).iterdir())
            result = subprocess.run([sys.executable, str(ROOT / "scripts/demo_context.py")],
                cwd=directory, text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(data["status"], "passed")
            self.assertEqual(data["cli_operations_exercised"], 8)
            self.assertTrue(data["checks"]["changed_metadata_invalidates_record_id"])
            self.assertTrue(data["checks"]["retrieval_left_source_unchanged"])
            self.assertTrue(data["checks"]["unavailable_source_reported_with_useful_results"])
            self.assertFalse(data["real_user_memory_read"])
            self.assertEqual(list(Path(directory).iterdir()), before)

    def test_demo_rejects_empty_intent_results(self):
        original_cli = demo.cli

        def empty_intent(config, operation, *args):
            result = original_cli(config, operation, *args)
            if operation == "build_intent_context":
                result["records"] = []
            return result

        with patch.object(demo, "cli", side_effect=empty_intent):
            with self.assertRaisesRegex(RuntimeError, "current brand"):
                demo.run_demo()

    def test_demo_detects_source_changes_after_fixture_edit(self):
        original_cli = demo.cli

        def changing_retrieval(config, operation, *args):
            result = original_cli(config, operation, *args)
            if operation == "search_memory" and any(
                    source["id"] == "missing"
                    for source in json.loads(config.read_text())["sources"]):
                notes = config.parent / "memory" / "decisions.json"
                notes.write_text("changed by retrieval", encoding="utf-8")
            return result

        with patch.object(demo, "cli", side_effect=changing_retrieval):
            with self.assertRaisesRegex(RuntimeError, "Retrieval changed source bytes"):
                demo.run_demo()

    def test_demo_requires_missing_source_warning_even_with_truncation_warning(self):
        original_cli = demo.cli

        def hide_missing_source(config, operation, *args):
            result = original_cli(config, operation, *args)
            warning = "missing: root unavailable or unsafe"
            if warning in result["warnings"]:
                result["warnings"].remove(warning)
                result["status"] = "partial" if result["warnings"] else "ok"
                self.assertEqual(result["warnings"], ["notes: excerpt truncated"])
            return result

        with patch.object(demo, "cli", side_effect=hide_missing_source):
            with self.assertRaisesRegex(RuntimeError, "Missing source diagnostic"):
                demo.run_demo()

    def test_demo_requires_matching_record_from_available_source(self):
        original_cli = demo.cli

        def change_match(config, operation, *args):
            result = original_cli(config, operation, *args)
            if "missing: root unavailable or unsafe" in result["warnings"]:
                for record in result["records"]:
                    record["content"] = record["content"].replace("copper", "bronze")
            return result

        with patch.object(demo, "cli", side_effect=change_match):
            with self.assertRaisesRegex(RuntimeError, "Partial retrieval discarded useful evidence"):
                demo.run_demo()


if __name__ == "__main__":
    unittest.main()
