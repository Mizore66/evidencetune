# Frontier-guided layer-wise merge spike — 10 Nov 2026

**Status: COMPLETE — KILL. Neither preregistered candidate passed the dev gate. Uniform α=0.75 remains the submission model.**

## Question

Can one of two fixed, frontier-proposed per-tensor v7/v8 interpolation recipes improve resolution over the uniform `merge_alpha_0.75` comparator without reducing semantic or targeted dev task success?

This is weight-space arithmetic directed by a frontier model, not direct generation of tensor values by an LLM. NumPy performs the interpolation; no training occurred.

## Locked protocol

Preregistration: `.spike/preregistration.json`
SHA-256: `49b39a7261ca1d6e2641d4266c2d17663e65bbfd97f526b206a9ec73f6e50dee`

The preregistration contains the exact resolved v7 multiplier for every one of the 504 tensors in each candidate, both source hashes, all dev-input hashes, the comparator metrics, code hashes, generation settings, gate, and selection rule. It was written and hashed before candidate dev generation.

- Selection split: existing semantic, targeted, and 32-case resolution dev packs only.
- Backend: local Apple MPS bf16 Transformers, greedy generation, at most 80 new tokens, batch size 8.
- Frozen evaluation: none. No frozen predictions or metrics were used to design recipes.
- Training, external model APIs, paid jobs, and network model loading: none.
- Maximum experiment scope: two candidates and one dev evaluation per candidate; no recipe changes after generation.

## Candidates

Both use `merged[t] = alpha[t] * v7[t] + (1 - alpha[t]) * v8[t]`, with float64 arithmetic and one cast back to each source dtype.

| Candidate | Exact rule | v7 weight elsewhere | Adapter SHA-256 |
|---|---|---:|---|
| `attention_v8` | α=0.50 for every `self_attn` tensor | 0.75 | `06b7c349a01f28b2fbb003dec4711bf2cd7d53c829b888ae6d7603d063f78312` |
| `late_v8` | α=0.50 for every tensor in layers 24–35 | 0.75 | `2da608616beeef57fb4c043fb5ff464372bf5553cf98ec366c594ca8ece78fc1` |

The hypotheses were fixed from dev behavior alone: attention-specific v8 emphasis might transfer two-turn interaction behavior while v7-dominant MLP weights retain single-turn behavior; late-layer v8 emphasis might transfer dialogue behavior while leaving earlier representations closer to the uniform winner.

## Preregistered gate versus uniform α=0.75

Comparator dev metrics:

- Semantic task success: **0.9625**
- Targeted task success: **0.9000**
- Resolution overall: **0.7941176470588235**

A candidate passes only if:

1. Resolution overall improves by **at least 0.02** (2 percentage points).
2. Semantic dev task success does not decline.
3. Targeted dev task success does not decline.

If neither passes, the experiment is killed. A passing candidate would be dev-only promising and require a **new independent confirmation set**; it would not automatically replace the submission model.

## Implementation and verification

### Historical run preservation

- Exact original runner, merge, evaluator, and recipe files are preserved under `merge_eval/historical/`; `ORIGINAL-HASHES.json` records their hashes and limitations.
- The historical preregistration and raw artifacts were not modified.
- `merge_eval/verify_historical.py` is self-contained and performs read-only dev verification: original code hashes, candidate recipes/maps/sources, raw counts, single-turn rescoring, resolution final-score and overall-rate recomputation, raw-summary consistency, gate recomputation, and KILL outcome.
- Historical limitations are explicit: no runner hash lock, no adapter-config lock in the candidate manifest, no recorded full base commit or tokenizer hashes, and no per-call timing/usage evidence.
- The optional new-run hardening prototype was excluded as out of scope for this spike/negative result. It is preserved only in ignored `.spike/throwaway-new-run/`, is not a tracked deliverable, and has no retained tests or execution claims.

### Requirements retained from prototype review

Excluding the prototype does not discard its review findings. Any future candidate run must satisfy all of these before generation:

1. Bind each candidate cryptographically: preregister its model/config hashes or independently reconstruct and compare every tensor and validate config semantics. A matching recipe name or self-declared provenance record is insufficient.
2. Hash every inference-relevant base-model and tokenizer file, including weights, indexes, configs, chat templates, and special-token files; load directly from the verified snapshot.
3. Hash-lock the runner, merge/gate logic, transitive scorers, resolved recipes/maps, adapter configs, and effective generation settings; reject unmatched/no-op rules and batch-size overrides.
4. Rescore saved initial and follow-up outputs before resume, and preserve per-call content/token usage with timing labeled at its actual invocation or batch scope.
5. Keep dev-only selection, immutable preregistration, explicit tie-breaking, and a new independent confirmation set for any passing candidate.

These are requirements for a future protocol, not claims that the excluded prototype satisfies them.

### Current verification

- **10 retained spike/historical tests passed**: exact recipe/tensor merging, provenance, immutable outputs, gate behavior, original preregistration loading, metric extraction, and read-only historical verification.
- **14 original non-frozen tests passed**. The 3 original frozen-fixture tests were not rerun under the no-frozen-access constraint; all 17 had passed before the hardening review.
- Both candidates: all 504 output tensors independently recomputed and compared exactly; all values finite; source hashes unchanged.

Candidate adapters and the full resolved maps are under `.spike/adapters/`; this directory is intentionally ignored by Git. Only historical code, exact recipes, merge utilities, retained tests, read-only verification, and this report are tracked.

## Results

| Model | Semantic task success | Targeted task success | Resolution overall | Gate |
|---|---:|---:|---:|---|
| Uniform α=0.75 comparator | 96.25% | 90.00% | **79.41%** | comparator |
| `attention_v8` | 97.08% (+0.83pp) | 90.00% (+0.00pp) | 71.43% (−7.98pp) | **FAIL** |
| `late_v8` | 97.08% (+0.83pp) | 90.00% (+0.00pp) | 74.07% (−5.34pp) | **FAIL** |

`attention_v8` resolved 30/42 follow-ups in 1,559.018 seconds. `late_v8` resolved 40/54 follow-ups in 1,544.363 seconds. Total candidate evaluation time was **3,103.381 seconds (51 minutes 43 seconds)**.

Both candidates retained targeted performance and gained 0.83pp semantic task success, but neither met the required +2pp resolution improvement; both materially regressed resolution. The correct action under the locked protocol is to stop. No new independent confirmation is justified, no frozen evaluation was run, and the submission adapter was not replaced.

All **1,096 preserved dev records** are present: 240 semantic, 180 targeted, and 128 resolution records per candidate. Single-turn metrics were independently recomputed with the original scorer. Resolution final scores and overall rates were recomputed from raw records; complete saved resolution metric objects were checked for raw-summary equality. Aggregate token usage and timing are covered by that saved-object consistency check only and are **not per-call reconstructable** for the historical run. Source v7/v8, uniform comparator, and original selection hashes remain unchanged.

## Limitations

- This rejects only the two preregistered recipes on the existing dev packs; it does not prove that every layer-wise recipe would fail.
- The dev sets are small synthetic/proxy evaluations. The semantic gain is not independent confirmation of an improvement.
- All arms used the same Apple MPS bf16 backend. Single-turn summary metadata inherits the original runner's generic `dev-only five-arm evaluation` backend label, while the top-level run plan and resolution summaries correctly record the two-candidate spike. Actual generation settings and backend were unchanged, so no backend mixing occurred.
- The historical preregistration did not lock the runner, adapter config, full base snapshot revision, or tokenizer hashes. Those limitations are documented, not repaired retroactively.
- Historical per-call timing and usage cannot be reconstructed from aggregate stage/batch fields.
- Ignored `.spike/` artifacts occupy approximately 236 MB, including both candidate adapters, full resolved maps, raw predictions, batches, logs, and provenance.

## Reproduce

### Read-only historical verification and retained tests

These commands perform no model generation and read no frozen data:

```bash
PY=/Users/anasqumhiyeh/lexsi-koth/tools/evtune-local-venv/bin/python
ROOT=/Users/anasqumhiyeh/.claude/worktrees/evtune-merge-spike
RAW=/Users/anasqumhiyeh/lexsi-koth/evtune

$PY -m unittest discover -s "$ROOT/merge_eval/tests" -v
$PY "$ROOT/merge_eval/verify_historical.py"
(cd "$RAW/merge_eval/tests" && \
  $PY -m unittest -v test_local_eval.DevSelectionTests test_local_eval.RawRecordTests test_merge_lora)
```

The last command runs the **14 original non-frozen tests**. To run the complete **original 17-test suite**, use the separate command below. It reads three frozen fixtures and was therefore not used during this no-frozen-access hardening pass:

```bash
$PY -m unittest discover -s "$RAW/merge_eval/tests" -v
```

No new-run execution path is included. The optional prototype is excluded under ignored `.spike/throwaway-new-run/` as described above.
