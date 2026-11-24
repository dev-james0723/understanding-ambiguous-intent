import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


installer = module("install")
evaluation = module("evaluate")


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text("test runtime")
        (self.source / "references").mkdir()
        (self.source / "references" / "example.md").write_text("test example")

    def tearDown(self):
        self.temp.cleanup()

    def test_install_copies_runtime_exactly(self):
        result = installer.install(self.root / "target", self.source)
        destination = Path(result["destination"])
        self.assertEqual((destination / "SKILL.md").read_text(), "test runtime")
        self.assertEqual((destination / "references" / "example.md").read_text(), "test example")
        self.assertFalse(result["host_loading_verified"])

    def test_dry_run_has_no_side_effects(self):
        target = self.root / "missing-parent"
        result = installer.install(target, self.source, dry_run=True)
        self.assertFalse(target.exists())
        self.assertFalse(result["written"])

    def test_existing_install_is_preserved(self):
        installer.install(self.root / "target", self.source)
        marker = self.root / "target" / installer.NAME / "SKILL.md"
        marker.write_text("owner customization")
        with self.assertRaises(FileExistsError):
            installer.install(self.root / "target", self.source)
        self.assertEqual(marker.read_text(), "owner customization")

    def test_destination_symlink_is_refused(self):
        target = self.root / "target"
        target.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        (target / installer.NAME).symlink_to(outside, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            installer.install(target, self.source)
        self.assertEqual(list(outside.iterdir()), [])

    def test_source_symlink_is_refused(self):
        (self.source / "external").symlink_to(self.root)
        with self.assertRaises(ValueError):
            installer.install(self.root / "target", self.source)
        self.assertFalse((self.root / "target").exists())


class EvaluationIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "cases.jsonl"
        self.case = {"id": "x", "split": "smoke", "category": "writing",
                     "messages": [{"role": "user", "content": "Shorten this sentence."}]}

    def tearDown(self):
        self.temp.cleanup()

    def write(self, cases):
        self.path.write_text("\n".join(json.dumps(c) for c in cases))

    def test_answer_key_field_is_rejected(self):
        self.case["expected"] = "the answer"
        self.write([self.case])
        with self.assertRaises(ValueError):
            evaluation.read_cases(self.path)

    def test_duplicate_ids_are_rejected(self):
        self.write([self.case, self.case])
        with self.assertRaises(ValueError):
            evaluation.read_cases(self.path)

    def test_non_user_final_turn_is_rejected(self):
        self.case["messages"][-1]["role"] = "assistant"
        self.write([self.case])
        with self.assertRaises(ValueError):
            evaluation.read_cases(self.path)

    def test_prepared_request_contains_no_rubric(self):
        self.write([self.case])
        request = evaluation.make_request(evaluation.read_cases(self.path)[0], "baseline", "system")
        self.assertEqual(set(request), {"id", "split", "category", "condition", "system", "prompt"})
        self.assertNotIn("expected", request)

    def test_non_object_provider_json_is_recorded(self):
        request = evaluation.make_request(self.case, "baseline", "system")
        fake = SimpleNamespace(returncode=0, stdout="[]")
        with patch.object(evaluation.subprocess, "run", return_value=fake):
            result = evaluation.run_one("unused", request, "default", 1, self.temp.name, "test")
        self.assertEqual(result["status"], "invalid-result")

    def test_null_model_usage_does_not_lose_valid_response(self):
        request = evaluation.make_request(self.case, "baseline", "system")
        fake = SimpleNamespace(returncode=0, stdout=json.dumps({"result": "Response", "modelUsage": None}))
        with patch.object(evaluation.subprocess, "run", return_value=fake):
            result = evaluation.run_one("unused", request, "default", 1, self.temp.name, "test")
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["reported_models"], [])

    def test_custom_comparator_requires_explicit_source(self):
        with self.assertRaises(ValueError):
            evaluation.instruction("custom")


if __name__ == "__main__":
    unittest.main()
