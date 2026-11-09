#!/usr/bin/env python3
"""Immutable, per-tensor v7/v8 LoRA interpolation for the dev-only spike."""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import safetensors
from safetensors.numpy import load_file, save_file

from merge_lora import (
    CONFIG_NAME,
    MODEL_NAME,
    PROVENANCE_NAME,
    README_NAME,
    _source_description,
    _validate_sources,
    sha256_file,
    validate_safetensors_file,
)

TENSOR_RE = re.compile(
    r"\Abase_model\.model\.model\.layers\.(\d+)\.(self_attn|mlp)\."
    r"(?:q_proj|k_proj|v_proj|o_proj|gate_proj|up_proj|down_proj)\."
    r"lora_[AB]\.weight\Z"
)


def _alpha(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("alpha must be a finite number in [0, 1]")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("alpha must be a finite number in [0, 1]")
    return value


def _rule_matches(rule: dict[str, Any], layer: int, module: str) -> bool:
    if rule.get("module") not in (None, module):
        return False
    layers = rule.get("layers")
    if layers is not None:
        if (
            not isinstance(layers, list)
            or any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in layers)
        ):
            raise ValueError("rule layers must be nonnegative integers")
        if layer not in layers:
            return False
    return True


def resolve_alpha_map(tensor_names: Iterable[str], recipe: dict[str, Any]) -> dict[str, float]:
    """Resolve every source tensor to its exact v7 multiplier, rejecting ambiguity."""
    default_alpha = _alpha(recipe.get("default_alpha"))
    rules = recipe.get("rules")
    if not isinstance(rules, list) or any(not isinstance(rule, dict) for rule in rules):
        raise ValueError("recipe rules must be a list of objects")
    resolved = {}
    for name in sorted(tensor_names):
        match = TENSOR_RE.fullmatch(name)
        if match is None:
            raise ValueError(f"unrecognized LoRA tensor name: {name}")
        layer, module = int(match.group(1)), match.group(2)
        matches = [rule for rule in rules if _rule_matches(rule, layer, module)]
        if len(matches) > 1:
            raise ValueError(f"tensor matches multiple rules: {name}")
        resolved[name] = _alpha(matches[0]["alpha"]) if matches else default_alpha
    if not resolved:
        raise ValueError("recipe resolved no tensors")
    return resolved


def merge_layerwise_adapters(
    v7_dir: str | Path,
    v8_dir: str | Path,
    output_dir: str | Path,
    recipe: dict[str, Any],
) -> dict[str, Any]:
    """Merge exact per-tensor weights without modifying sources or existing outputs."""
    v7_dir, v8_dir, output_dir = Path(v7_dir), Path(v8_dir), Path(output_dir)
    if output_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing merge output: {output_dir}")
    structure = _validate_sources(v7_dir, v8_dir)
    sources = {"v7": _source_description(v7_dir), "v8": _source_description(v8_dir)}
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=output_dir.parent))
    try:
        v7_tensors = load_file(str(v7_dir / MODEL_NAME))
        v8_tensors = load_file(str(v8_dir / MODEL_NAME))
        alpha_map = resolve_alpha_map(v7_tensors.keys(), recipe)
        if set(alpha_map) != set(v8_tensors):
            raise ValueError("resolved tensor map differs from v8 source")
        merged = {}
        for key in sorted(v7_tensors):
            left, right = v7_tensors[key], v8_tensors[key]
            if not np.issubdtype(left.dtype, np.floating):
                raise ValueError(f"cannot interpolate non-floating tensor {key}")
            alpha = alpha_map[key]
            value = alpha * left.astype(np.float64) + (1.0 - alpha) * right.astype(np.float64)
            value = np.ascontiguousarray(value.astype(left.dtype))
            if not bool(np.isfinite(value).all()):
                raise ValueError(f"non-finite merged values for {key}")
            merged[key] = value

        model_path = temporary / MODEL_NAME
        metadata = validate_safetensors_file(v7_dir / MODEL_NAME)["metadata"]
        save_file(merged, str(model_path), metadata=metadata)
        byte_validation = validate_safetensors_file(model_path)
        reloaded = load_file(str(model_path))
        for key, expected in merged.items():
            actual = reloaded[key]
            if actual.dtype != expected.dtype or actual.shape != expected.shape or not np.array_equal(actual, expected):
                raise ValueError(f"reloaded output differs for {key}")
        shutil.copyfile(v7_dir / CONFIG_NAME, temporary / CONFIG_NAME)
        if (v7_dir / README_NAME).is_file():
            shutil.copyfile(v7_dir / README_NAME, temporary / README_NAME)
        canonical_map = json.dumps(alpha_map, sort_keys=True, separators=(",", ":")).encode()
        provenance = {
            "schema_version": 1,
            "operation": "per_tensor_lora_weight_interpolation",
            "formula": "merged[t] = alpha[t] * v7[t] + (1 - alpha[t]) * v8[t]",
            "recipe": recipe,
            "resolved_alpha_map": alpha_map,
            "resolved_alpha_map_sha256": hashlib.sha256(canonical_map).hexdigest(),
            "arithmetic": "float64 interpolation, cast once to each source tensor dtype",
            "adapter_config_preserved_from": "v7",
            "readme_preserved_from": "v7",
            "sources": sources,
            "structure": structure,
            "output": {
                MODEL_NAME: {"sha256": sha256_file(model_path), "size_bytes": model_path.stat().st_size},
            },
            "validation": {
                **structure,
                "complete_output_bytes": byte_validation["complete"],
                "full_tensor_values_verified": True,
                "all_merged_values_finite": True,
            },
            "training_performed": False,
            "frozen_test_used": False,
            "tool": {
                "implementation": "merge_eval/layerwise_merge.py",
                "safetensors_version": safetensors.__version__,
                "numpy_version": np.__version__,
                "device": "CPU only",
            },
        }
        (temporary / PROVENANCE_NAME).write_text(
            json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        os.replace(temporary, output_dir)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise
    return {
        "name": output_dir.name,
        "path": str(output_dir.resolve()),
        "sha256": provenance["output"][MODEL_NAME]["sha256"],
        "size_bytes": provenance["output"][MODEL_NAME]["size_bytes"],
        "resolved_alpha_map_sha256": provenance["resolved_alpha_map_sha256"],
        "tensor_count": structure["tensor_count"],
        "validation": provenance["validation"],
    }


def _rate(metrics: dict[str, Any], key: str) -> float:
    value = metrics.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"missing finite gate metric: {key}")
    value = float(value)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError(f"gate metric outside [0,1] or nonfinite: {key}")
    return value


def evaluate_gate(candidate: dict[str, Any], comparator: dict[str, Any]) -> dict[str, Any]:
    """Require +2pp resolution and zero task-success decline versus alpha=.75."""
    keys = ("semantic_task_success", "targeted_task_success", "resolution_overall")
    candidate_rates = {key: _rate(candidate, key) for key in keys}
    comparator_rates = {key: _rate(comparator, key) for key in keys}
    deltas = {key: candidate_rates[key] - comparator_rates[key] for key in keys}
    epsilon = 1e-12
    violations = []
    if deltas["resolution_overall"] < 0.02 - epsilon:
        violations.append("resolution_dev_gain_below_2pp")
    if deltas["semantic_task_success"] < -epsilon:
        violations.append("semantic_dev_task_success_declined")
    if deltas["targeted_task_success"] < -epsilon:
        violations.append("targeted_dev_task_success_declined")
    return {
        "schema_version": 1,
        "comparison_baseline": "merge_alpha_0.75",
        "selection_split": "dev_only",
        "minimum_resolution_delta": 0.02,
        "maximum_allowed_task_success_drop": 0.0,
        "candidate_metrics": candidate_rates,
        "comparator_metrics": comparator_rates,
        "deltas": deltas,
        "violations": violations,
        "passed": not violations,
        "frozen_test_used": False,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v7", type=Path, required=True)
    parser.add_argument("--v8", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recipe", type=Path, required=True)
    arguments = parser.parse_args()
    result = merge_layerwise_adapters(
        arguments.v7, arguments.v8, arguments.output,
        json.loads(arguments.recipe.read_text(encoding="utf-8")),
    )
    print(json.dumps(result, indent=2, sort_keys=True))
