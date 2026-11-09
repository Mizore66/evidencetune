from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

MERGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MERGE_ROOT))

from layerwise_dev import extract_metrics, load_preregistration  # noqa: E402


class PreregistrationLoadingTests(unittest.TestCase):
    def test_loads_only_hash_locked_dev_preregistration(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temporary:
            root = Path(temporary)
            spike = root / ".spike"
            spike.mkdir()
            path = spike / "preregistration.json"
            payload = {
                "status": "PREREGISTERED_NO_CANDIDATE_DEV_GENERATION",
                "frozen_test_used": False,
                "training_performed": False,
                "candidate_order": ["attention_v8", "late_v8"],
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            (spike / "preregistration.sha256").write_text(digest + "  preregistration.json\n", encoding="utf-8")
            self.assertEqual(load_preregistration(root)["candidate_order"], ["attention_v8", "late_v8"])
            path.write_text(json.dumps(dict(payload, candidate_order=["late_v8"])), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "preregistration SHA-256"):
                load_preregistration(root)


class MetricExtractionTests(unittest.TestCase):
    def test_extracts_exact_dev_gate_metrics(self):
        results = {
            "attention_v8": {
                "semantic_dev": {"metrics": {"task_success": 0.96}},
                "v8_targeted_dev": {"metrics": {"task_success": 0.90}},
                "resolution_dev": {"metrics": {"resolution": {"overall": {"rate": 0.82}}}},
            }
        }
        self.assertEqual(
            extract_metrics(results, "attention_v8"),
            {"semantic_task_success": 0.96, "targeted_task_success": 0.90, "resolution_overall": 0.82},
        )


if __name__ == "__main__":
    unittest.main()
