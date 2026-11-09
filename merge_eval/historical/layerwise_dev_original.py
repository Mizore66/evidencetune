#!/usr/bin/env python3
"""Evaluate exactly the preregistered layer-wise candidates on dev only."""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from layerwise_merge import evaluate_gate, sha256_file

WORKTREE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW_ROOT = Path("/Users/anasqumhiyeh/lexsi-koth/evtune")
DEFAULT_OUTPUT = WORKTREE_ROOT / ".spike/local_results"


def load_preregistration(worktree_root: Path = WORKTREE_ROOT) -> dict[str, Any]:
    root = worktree_root / ".spike"
    path = root / "preregistration.json"
    actual = sha256_file(path)
    expected = (root / "preregistration.sha256").read_text(encoding="utf-8").split()[0]
    if actual != expected:
        raise ValueError("preregistration SHA-256 mismatch")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("status") != "PREREGISTERED_NO_CANDIDATE_DEV_GENERATION":
        raise ValueError("unexpected preregistration status")
    if payload.get("frozen_test_used") is not False or payload.get("training_performed") is not False:
        raise ValueError("spike must remain dev-only and training-free")
    return payload


def extract_metrics(results: dict[str, Any], name: str) -> dict[str, float]:
    current = results[name]
    return {
        "semantic_task_success": current["semantic_dev"]["metrics"]["task_success"],
        "targeted_task_success": current["v8_targeted_dev"]["metrics"]["task_success"],
        "resolution_overall": current["resolution_dev"]["metrics"]["resolution"]["overall"]["rate"],
    }


def main(raw_root: Path, output_root: Path, batch_size: int) -> dict[str, Any]:
    if batch_size < 1:
        raise ValueError("batch_size must be >= 1")
    preregistration = load_preregistration()
    if sha256_file(raw_root / "merge_eval/local_eval.py") != preregistration["code_sha256"]["local_eval"]:
        raise ValueError("local evaluation implementation differs from preregistration")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    sys.path.insert(0, str(raw_root / "merge_eval"))
    import local_eval

    local_eval.BACKEND = preregistration["generation"]["backend"]
    import torch
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.backends.mps.is_available():
        raise RuntimeError("local MPS is unavailable")
    manifest_path = WORKTREE_ROOT / ".spike/adapters/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["preregistration_sha256"] != sha256_file(WORKTREE_ROOT / ".spike/preregistration.json"):
        raise ValueError("adapter manifest is not bound to preregistration")
    output_entries = {entry["name"]: entry for entry in manifest["outputs"]}
    order = preregistration["candidate_order"]
    if set(output_entries) != set(order) or len(order) != 2:
        raise ValueError("spike requires exactly the two preregistered candidates")
    models = {
        name: {
            "adapter_path": output_entries[name]["path"],
            "adapter_model_sha256": output_entries[name]["sha256"],
        }
        for name in order
    }
    plan = {"models": models, "datasets": preregistration["datasets"]}
    local_eval._verify_dev_inputs(plan)
    datasets, resolution_cases = local_eval._load_dev_data(plan)
    run_plan = {
        "schema_version": 1,
        "experiment": preregistration["experiment"],
        "preregistration_sha256": sha256_file(WORKTREE_ROOT / ".spike/preregistration.json"),
        "base_model": local_eval.MODEL,
        "candidate_order": order,
        "models": models,
        "datasets": preregistration["datasets"],
        "generation": preregistration["generation"],
        "gate": preregistration["gate"],
        "selection_rule": preregistration["selection_rule"],
        "training_performed": False,
        "frozen_test_used": False,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    local_eval._write_leaf_plan(output_root, run_plan)
    local_eval.atomic_write_json(output_root / "progress.json", {"event": "inputs_validated", "completed_models": []})

    print(json.dumps({"event": "loading_base_and_adapters", "models": order}), flush=True)
    tokenizer = AutoTokenizer.from_pretrained(local_eval.MODEL, local_files_only=True)
    tokenizer.padding_side = "left"
    base = AutoModelForCausalLM.from_pretrained(
        local_eval.MODEL, dtype=torch.bfloat16, local_files_only=True,
    ).to("mps").eval()
    model = None
    adapter_names = {name: f"spike_{index}" for index, name in enumerate(order)}
    for name in order:
        adapter = models[name]["adapter_path"]
        adapter_name = adapter_names[name]
        if model is None:
            model = PeftModel.from_pretrained(base, adapter, adapter_name=adapter_name, is_trainable=False)
        else:
            model.load_adapter(adapter, adapter_name=adapter_name)
    model.eval()
    results = {}
    gates = {}
    try:
        for name in order:
            started = time.perf_counter()
            model.set_adapter(adapter_names[name])
            print(json.dumps({"event": "model_started", "model": name}), flush=True)
            results[name] = {}
            for view, (rows, labels) in datasets.items():
                generator = local_eval.MPSGenerator(tokenizer, model, batch_size=batch_size, label=f"{name}/{view}")
                results[name][view] = local_eval.run_single_turn(
                    name, view, rows, labels, generator, output_root,
                    expected_cases=preregistration["datasets"][view]["cases"],
                    source_sha256=preregistration["datasets"][view]["source_sha256"],
                    labels_sha256=preregistration["datasets"][view]["labels_sha256"],
                )
                print(json.dumps({
                    "event": "view_complete", "model": name, "view": view,
                    "task_success": results[name][view]["metrics"]["task_success"],
                }), flush=True)
            generator = local_eval.MPSGenerator(tokenizer, model, batch_size=batch_size, label=f"{name}/resolution_dev")
            results[name]["resolution_dev"] = local_eval.run_resolution(
                name, resolution_cases, generator, output_root,
                source_sha256=preregistration["datasets"]["resolution_dev"]["source_sha256"],
                labels_sha256=preregistration["datasets"]["resolution_dev"]["labels_sha256"],
            )
            gates[name] = evaluate_gate(
                extract_metrics(results, name), preregistration["comparator"]["metrics"],
            )
            gates[name]["seconds"] = round(time.perf_counter() - started, 3)
            local_eval.atomic_write_json(output_root / "evaluation/gate_results.json", {
                "schema_version": 1,
                "preregistration_sha256": run_plan["preregistration_sha256"],
                "gates": gates,
                "completed_models": list(results),
                "frozen_test_used": False,
            })
            local_eval.atomic_write_json(output_root / "progress.json", {
                "event": "model_complete", "completed_models": list(results), "results": results,
            })
            print(json.dumps({"event": "model_complete", "model": name, "gate": gates[name]}), flush=True)
    finally:
        del model
        del base
        gc.collect()
        torch.mps.empty_cache()

    source_hashes_after = {
        key: sha256_file(Path(value["path"]) / "adapter_model.safetensors")
        for key, value in preregistration["source_adapters"].items()
    }
    expected_hashes = {
        key: value["adapter_model_sha256"] for key, value in preregistration["source_adapters"].items()
    }
    if source_hashes_after != expected_hashes:
        raise ValueError("raw source adapter hash changed during spike")
    final = {
        "schema_version": 1,
        "status": "COMPLETE",
        "preregistration_sha256": run_plan["preregistration_sha256"],
        "backend": preregistration["generation"]["backend"],
        "results": results,
        "gates": gates,
        "eligible_models": [name for name in order if gates[name]["passed"]],
        "recommendation": "NEW_INDEPENDENT_CONFIRMATION_REQUIRED" if any(gate["passed"] for gate in gates.values()) else "KILL_NO_CANDIDATE_PASSED",
        "source_hashes_after": source_hashes_after,
        "training_performed": False,
        "frozen_test_used": False,
    }
    local_eval.atomic_write_json(output_root / "evaluation/summary.json", final)
    print(json.dumps({"event": "spike_complete", "recommendation": final["recommendation"], "gates": gates}), flush=True)
    return final


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, default=DEFAULT_RAW_ROOT)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--batch-size", type=int, default=8)
    arguments = parser.parse_args()
    main(arguments.raw_root, arguments.output_root, arguments.batch_size)
