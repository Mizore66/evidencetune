from __future__ import annotations

import hashlib
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from safetensors.numpy import load_file, save_file

MERGE_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MERGE_ROOT))

from layerwise_merge import evaluate_gate, merge_layerwise_adapters, resolve_alpha_map  # noqa: E402


SELF_ATTN = "base_model.model.model.layers.0.self_attn.q_proj.lora_A.weight"
MLP = "base_model.model.model.layers.1.mlp.up_proj.lora_A.weight"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def config() -> dict:
    return {
        "peft_type": "LORA",
        "r": 16,
        "lora_alpha": 32,
        "target_modules": ["q_proj", "up_proj"],
        "bias": "none",
        "modules_to_save": None,
        "use_dora": False,
        "use_qalora": False,
        "use_rslora": False,
        "use_bdlora": False,
        "lora_ga_config": None,
    }


class LayerwiseRecipeTests(unittest.TestCase):
    def test_resolves_exact_per_tensor_v7_weights(self):
        recipe = {
            "default_alpha": 0.75,
            "rules": [{"module": "self_attn", "alpha": 0.5}],
        }
        self.assertEqual(resolve_alpha_map([SELF_ATTN, MLP], recipe), {SELF_ATTN: 0.5, MLP: 0.75})

    def test_rejects_overlapping_rules_and_unrecognized_tensors(self):
        recipe = {
            "default_alpha": 0.75,
            "rules": [
                {"module": "self_attn", "alpha": 0.5},
                {"module": "self_attn", "layers": [0], "alpha": 0.25},
            ],
        }
        with self.assertRaisesRegex(ValueError, "multiple rules"):
            resolve_alpha_map([SELF_ATTN], recipe)
        with self.assertRaisesRegex(ValueError, "tensor name"):
            resolve_alpha_map(["unexpected.weight"], {"default_alpha": 0.75, "rules": []})



class LayerwiseMergeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.root = Path(self.temporary.name)
        self.v7 = self.root / "v7"
        self.v8 = self.root / "v8"
        for path, self_value, mlp_value in ((self.v7, 0.0, 0.0), (self.v8, 8.0, 4.0)):
            path.mkdir()
            (path / "adapter_config.json").write_text(json.dumps(config()), encoding="utf-8")
            (path / "README.md").write_text("source adapter\n", encoding="utf-8")
            save_file(
                {
                    SELF_ATTN: np.full((2, 2), self_value, dtype=np.float32),
                    MLP: np.full((2, 2), mlp_value, dtype=np.float32),
                },
                str(path / "adapter_model.safetensors"),
                metadata={"format": "pt"},
            )
        self.recipe = {
            "name": "attention_v8",
            "default_alpha": 0.75,
            "rules": [{"module": "self_attn", "alpha": 0.5}],
        }

    def tearDown(self):
        self.temporary.cleanup()

    def test_merge_applies_exact_weights_and_preserves_sources(self):
        before = {path: sha256(path / "adapter_model.safetensors") for path in (self.v7, self.v8)}
        output = self.root / "candidate"
        result = merge_layerwise_adapters(self.v7, self.v8, output, self.recipe)
        tensors = load_file(str(output / "adapter_model.safetensors"))
        np.testing.assert_array_equal(tensors[SELF_ATTN], np.full((2, 2), 4.0, dtype=np.float32))
        np.testing.assert_array_equal(tensors[MLP], np.full((2, 2), 1.0, dtype=np.float32))
        self.assertEqual({path: sha256(path / "adapter_model.safetensors") for path in (self.v7, self.v8)}, before)
        self.assertEqual(result["sha256"], sha256(output / "adapter_model.safetensors"))
        provenance = json.loads((output / "merge_provenance.json").read_text())
        self.assertEqual(provenance["resolved_alpha_map"], {SELF_ATTN: 0.5, MLP: 0.75})
        self.assertEqual(provenance["recipe"], self.recipe)
        self.assertEqual(provenance["sources"]["v7"]["files"]["adapter_model.safetensors"]["sha256"], before[self.v7])
        self.assertFalse(provenance["training_performed"])

    def test_merge_refuses_to_overwrite_a_candidate(self):
        output = self.root / "candidate"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("keep", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            merge_layerwise_adapters(self.v7, self.v8, output, self.recipe)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep")



class PreregisteredGateTests(unittest.TestCase):
    def setUp(self):
        self.comparator = {
            "semantic_task_success": 0.9625,
            "targeted_task_success": 0.90,
            "resolution_overall": 0.7941176470588235,
        }

    def test_exact_two_point_resolution_gain_with_retained_tasks_passes(self):
        candidate = dict(self.comparator, resolution_overall=self.comparator["resolution_overall"] + 0.02)
        result = evaluate_gate(candidate, self.comparator)
        self.assertTrue(result["passed"])
        self.assertEqual(result["violations"], [])

    def test_any_retention_or_resolution_shortfall_fails_closed(self):
        candidates = [
            dict(self.comparator),
            dict(self.comparator, resolution_overall=self.comparator["resolution_overall"] + 0.02, semantic_task_success=0.962499),
            dict(self.comparator, resolution_overall=self.comparator["resolution_overall"] + 0.02, targeted_task_success=0.899999),
        ]
        for candidate in candidates:
            with self.subTest(candidate=candidate):
                self.assertFalse(evaluate_gate(candidate, self.comparator)["passed"])

    def test_missing_nonfinite_or_out_of_range_metrics_fail_closed(self):
        for key in self.comparator:
            for value in (None, float("nan"), float("inf"), -0.01, 1.01, True):
                with self.subTest(key=key, value=value):
                    candidate = dict(self.comparator, resolution_overall=self.comparator["resolution_overall"] + 0.02)
                    candidate[key] = value
                    with self.assertRaises(ValueError):
                        evaluate_gate(candidate, self.comparator)


if __name__ == "__main__":
    unittest.main()
