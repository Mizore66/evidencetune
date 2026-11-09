#!/usr/bin/env python3
"""Read-only verification of the completed dev-only KILL run; never generates or reads frozen data."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

WORKTREE_ROOT = Path(__file__).resolve().parents[1]
RAW_ROOT = Path("/Users/anasqumhiyeh/lexsi-koth/evtune")
sys.path.insert(0, str(WORKTREE_ROOT / "merge_eval"))
sys.path.insert(0, str(RAW_ROOT))

from layerwise_merge import evaluate_gate


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_hash(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def verify_source_and_comparator_hashes(pre: dict) -> None:
    for name, entry in pre["source_adapters"].items():
        assert sha256_file(Path(entry["path"]) / "adapter_model.safetensors") == entry["adapter_model_sha256"], name
    comparator = pre["comparator"]
    assert sha256_file(Path(comparator["adapter_path"]) / "adapter_model.safetensors") == comparator["adapter_model_sha256"]


def verify_resolution(raw_path: Path, summary_path: Path) -> None:
    raw = json.loads(raw_path.read_text(encoding="utf-8"))
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    records = raw["records"]
    assert len(records) == 128
    assert raw["metrics"] == summary["metrics"]
    for record in records:
        initial = record["initial"]
        branches = record["followups"]
        if record["condition"] in ("unsupported_toward", "unsupported_away") and initial["parsed_action"] == "CLARIFY":
            successes = [bool(branches[branch]["resolved"]) for branch in ("gold_evidence", "no_evidence")]
            score = sum(successes) / 2 if initial["task_success"] else 0.0
        else:
            score = float(bool(initial["task_success"]))
        assert record["final_task_score"] == score
        assert record["final_task_success"] == (score == 1.0)
    clarified = [
        record for record in records
        if record["condition"] in ("unsupported_toward", "unsupported_away")
        and record["initial"]["parsed_action"] == "CLARIFY"
    ]
    resolved = sum(
        bool(record["followups"][branch]["resolved"])
        for record in clarified for branch in ("gold_evidence", "no_evidence")
    )
    assert summary["metrics"]["resolution"]["overall"] == {
        "clarifications": 2 * len(clarified),
        "resolved": resolved,
        "rate": resolved / (2 * len(clarified)) if clarified else None,
    }


def main() -> dict:
    from next_run import kaggle_next_flow as flow

    spike = WORKTREE_ROOT / ".spike"
    pre_path = spike / "preregistration.json"
    pre = json.loads(pre_path.read_text(encoding="utf-8"))
    pre_hash = sha256_file(pre_path)
    assert pre_hash == (spike / "preregistration.sha256").read_text().split()[0]
    historical = WORKTREE_ROOT / "merge_eval/historical"
    original_hashes = json.loads((historical / "ORIGINAL-HASHES.json").read_text())
    assert original_hashes["historical_preregistration_sha256"] == pre_hash
    for filename, expected in original_hashes["files"].items():
        assert sha256_file(historical / filename) == expected
    code_map = {
        "layerwise_merge": "layerwise_merge_original.py",
        "merge_lora": "merge_lora_original.py",
        "local_eval": "local_eval_original.py",
        "spike_recipes": "spike_recipes_original.json",
    }
    for key, filename in code_map.items():
        assert pre["code_sha256"][key] == sha256_file(historical / filename)
    verify_source_and_comparator_hashes(pre)

    manifest = json.loads((spike / "adapters/manifest.json").read_text())
    assert manifest["preregistration_sha256"] == pre_hash
    entries = {entry["name"]: entry for entry in manifest["outputs"]}
    assert set(entries) == set(pre["candidate_order"])
    for name, entry in entries.items():
        directory = Path(entry["path"])
        assert sha256_file(directory / "adapter_model.safetensors") == entry["sha256"]
        provenance = json.loads((directory / "merge_provenance.json").read_text())
        assert provenance["recipe"] == pre["recipes"][name]
        assert provenance["resolved_alpha_map"] == pre["resolved_alpha_maps"][name]
        assert provenance["resolved_alpha_map_sha256"] == _canonical_hash(pre["resolved_alpha_maps"][name])
        for source_name, source in pre["source_adapters"].items():
            recorded = provenance["sources"][source_name]
            assert recorded["path"] == source["path"]
            assert recorded["files"]["adapter_model.safetensors"]["sha256"] == source["adapter_model_sha256"]

    output = spike / "local_results/evaluation"
    final = json.loads((output / "summary.json").read_text())
    gates = json.loads((output / "gate_results.json").read_text())
    assert final["status"] == "COMPLETE"
    assert final["recommendation"] == "KILL_NO_CANDIDATE_PASSED"
    assert final["eligible_models"] == []
    assert final["frozen_test_used"] is False and final["training_performed"] is False
    total = 0
    for name in pre["candidate_order"]:
        for view, cases, count in (("semantic_dev", 48, 240), ("v8_targeted_dev", 36, 180)):
            root = output / name / view
            records = json.loads((root / "raw_predictions.json").read_text())["records"]
            assert len(records) == count
            summary = json.loads((root / "summary.json").read_text())
            assert summary["metrics"] == flow.summarize_records(records, split="dev", expected_cases=cases)["metrics"]
            total += len(records)
        resolution_root = output / name / "resolution_dev"
        verify_resolution(resolution_root / "resolution_raw.json", resolution_root / "summary.json")
        total += 128
        expected_gate = evaluate_gate(
            {
                "semantic_task_success": final["results"][name]["semantic_dev"]["metrics"]["task_success"],
                "targeted_task_success": final["results"][name]["v8_targeted_dev"]["metrics"]["task_success"],
                "resolution_overall": final["results"][name]["resolution_dev"]["metrics"]["resolution"]["overall"]["rate"],
            },
            pre["comparator"]["metrics"],
        )
        saved_gate = gates["gates"][name]
        for key in ("candidate_metrics", "comparator_metrics", "deltas", "violations", "passed"):
            assert saved_gate[key] == expected_gate[key]
        assert saved_gate["passed"] is False
    assert total == 1096
    return {
        "status": "VERIFIED",
        "recommendation": final["recommendation"],
        "dev_records": total,
        "preregistration_sha256": pre_hash,
        "historical_code_hashes_verified": True,
        "candidate_recipes_maps_sources_verified": True,
        "read_only": True,
        "generation_performed": False,
        "frozen_access": False,
        "historical_limitations": original_hashes["limitations"],
    }



if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
