from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


WORKTREE_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = Path("/Users/anasqumhiyeh/lexsi-koth/evtune")
STAGING_ROOT = WORKTREE_ROOT / "public_staging"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


staging = load_module("public_staging_for_tests", STAGING_ROOT / "build_staging.py")


class PublicStagingTests(unittest.TestCase):
    def test_korean_rows_and_credential_files_are_rejected(self):
        # Catches unresolved-license rows or credentials entering publishable staging.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            korean = root / "responses.jsonl"
            korean.write_text('{"language":"ko","prompt":"raw"}\n', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Korean"):
                staging.assert_publishable_file("responses.jsonl", korean)
            credential = root / "credentials.json"
            credential.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "credential"):
                staging.assert_publishable_file("credentials.json", credential)

    def test_wrong_selected_adapter_is_rejected_before_copying(self):
        # Catches staging an adapter whose bytes differ from the selected merged artifact.
        with tempfile.TemporaryDirectory() as temporary:
            raw = Path(temporary)
            adapter = raw / "merge_eval/adapters/alpha_0.75/adapter_model.safetensors"
            adapter.parent.mkdir(parents=True)
            adapter.write_bytes(b"wrong adapter")
            with self.assertRaisesRegex(ValueError, "selected adapter"):
                staging.verify_selected_adapter(raw)

    def test_complete_staging_has_portable_split_collections_and_hashes(self):
        # Catches incomplete evidence, absolute manifest paths, and mixed model/dataset collections.
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "staging"
            staging.build_staging(WORKTREE_ROOT, RAW_ROOT, destination)
            cache = destination / "__pycache__/ignored.pyc"
            cache.parent.mkdir()
            cache.write_bytes(b"cache")
            result = staging.verify_staging(destination)
            self.assertGreater(result["files_verified"], 100)
            self.assertGreater(result["model_files"], 10)
            self.assertGreater(result["dataset_files"], 20)
            manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
            self.assertNotIn(str(RAW_ROOT), json.dumps(manifest))
            self.assertEqual(manifest["korean_xstest_raw_rows"], "excluded_unresolved_license")
            self.assertEqual(manifest["collections"], ["dataset_collection", "model_collection"])
            self.assertEqual(len(manifest["source_adapters"]), 2)
            self.assertEqual(manifest["selected_adapter"]["sha256"], staging.ADAPTER_SHA256)
            self.assertEqual(manifest["selected_adapter"]["formula"], "0.75 * v7 + 0.25 * v8")
            card = (destination / "model_collection/README.md").read_text(encoding="utf-8")
            self.assertIn("license: cc-by-nc-4.0", card)
            self.assertNotIn("adapter/adapter_model.safetensors", card)
            self.assertIn("../docs/REPRODUCE.md", card)
            self.assertTrue((destination / "model_collection/LICENSE-MODEL").is_file())
            self.assertTrue((destination / "docs/REPRODUCE.md").is_file())
            self.assertTrue((destination / "LICENSE").is_file())
            review = destination / "model_collection/evidence/overrefusal/review_summary.en_it.json"
            review_text = review.read_text(encoding="utf-8")
            self.assertNotIn("ko-410", review_text)
            self.assertNotIn("ko-260", review_text)
            self.assertNotIn("review-052", review_text)
            self.assertNotIn("review-081", review_text)
            self.assertNotIn("review/review_summary.json", {entry["path"] for entry in manifest["files"]})
            replay = load_module("staged_replay_for_tests", destination / "code/release/replay_evidence.py")
            replay_result = replay.replay_all(staging_root=destination)
            self.assertEqual(replay_result["selected_model"], "merge_alpha_0.75")
            self.assertTrue(replay_result["staged_replay"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
