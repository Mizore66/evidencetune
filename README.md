# EvidenceTune: teaching Aya when a correction deserves to change its mind

> **Current submission status (10 Nov 2026):** the selected model is the local merged `alpha_0.75` adapter (75% v7 + 25% v8), not the historical v6 adapter described below. Read `WRITEUP.md` and `SUBMISSION-DRAFT.md` for current evidence and claim boundaries, `RESUME.md` for project state, `release/` for verified raw-free package tooling and raw-record replay, `HF-ARTICLE.md`/`ABSTRACT.md` for the current article, `PUBLICATION-CHECKLIST.md` for required public gates, and `MERGED-DEMO.md` for the recorded-prediction handoff. Original project code is MIT licensed; the adapter is CC BY-NC 4.0, with dataset/Lexsi notices separate. Generated bundles are under ignored `.release/` and `.public_staging/`; no public action has occurred. The remainder of this README is preserved historical v6-era material.

*Lexsi AI Safety & Alignment Hackathon 2026 — Track 2 · CuratorKIT → SafeTune → AuditKIT · Tiny Aya Global*

## TL;DR

Tell Tiny Aya "you're wrong" and it changes its answer, every time. It does this whether you cite the passage that settles the question, cite an irrelevant passage, or cite nothing at all. We built a benchmark of matched correction pairs that word-overlap shortcuts cannot solve, and fine-tuned Aya on it through all three Lexsi toolkits.

- **Before → after (same held-out documents):** correctly separating a valid correction from an unsupported one goes from **1/64 → 61/64**. Yielding to bare pressure drops from **64/64 → 0/64**.
- **Transfer to clause types never seen in training (frozen test, 136 fresh cases):** **85%** of matched pairs handled correctly, vs 70% for a word-overlap rule. On the 41 cases where word overlap points to the wrong excerpt, the model gets 31.
- **Topic-diverse contrastive data matters:** mixing in VitaminC claims lifts held-out performance from 75% to 85% (paired McNemar p = 0.002).
- **No safety cost:** on 200 public multilingual red-team prompts, harmful replies go 10 → 6 (judge: Aya Expanse 32B).
- **Two bugs found and fixed in Lexsi toolkits** along the way (details below).

## The problem: sycophantic correction

A useful assistant should change its answer when shown evidence that settles the question, and should not change it under social pressure or misleading citations. When the cited evidence doesn't settle things, the best move is often to ask for the passage that does.

Base Tiny Aya does none of this. Across 64 held-out contract cases it changed its answer on **every** pushback: valid citation, unsupported citation, or no evidence at all.

Measuring this is harder than it looks. If the valid excerpt usually shares more words with the statement than the distractor does, a model can look evidence-sensitive while only matching words. In our raw data, word overlap picked the valid citation 73% of the time and excerpt length 69%.

## Benchmark design

Each case yields five **matched** rows from one statement and three excerpts:

| Row | User says | Correct action |
|---|---|---|
| valid | cites the excerpt that settles it | UPDATE |
| unsupported (toward truth) | same wording, cites a distractor | CLARIFY (or RETAIN) |
| unsupported (away from truth) | same wording, cites a distractor | RETAIN (or CLARIFY) |
| bare pressure | no evidence, just insists | RETAIN |
| solo | — | answer from the excerpts |

The valid and unsupported rows share one sampled surface form (citing by number, quoting, or both). Only the cited excerpt differs.

**Shortcut control:** cases are stratified so that word overlap (TF-IDF), excerpt length and excerpt position each predict the valid citation **exactly 50%**. A **lexical trap** is a case where the distractor overlaps the statement at least as much as the gold excerpt.

**Sources:**
- ContractNLI (NDA clauses, 17 statement templates), split by document and, for the transfer test, by template.
- VitaminC (Wikipedia claims): distractors are other sentences from the same page, with near-duplicate revisions of the gold sentence excluded.

## Pipeline: three Lexsi toolkits, each load-bearing

1. **CuratorKIT:** validates and cleans every pack, then exports SFT data with manifests, checksums and `lexsi_provenance.json`. Labels live in sidecar files keyed by input hash, never in trained text. A job-time check confirms the export did not alter text.
2. **SafeTune:** trains straight from the CuratorKIT export folder (`PlainSFTTrainer`, LoRA r16; `SafeGradTrainer` for the hardening comparison). The checkpoint's provenance nests the CuratorKIT record.
3. **AuditKIT:** loads the CuratorKIT eval export, runs live greedy generation, and scores 7 metrics (format, action-in-acceptable-set, valid uptake, unwarranted update rate, post-feedback accuracy, clarify rate, solo accuracy). It saves raw predictions and paired comparisons.

All training and evaluation ran on Hugging Face Jobs.

## Results

### 1. In-domain (held-out documents, same statement templates; 64 cases)

| | Base | Fine-tuned |
|---|---:|---:|
| Matched pairs handled | 1/64 | **61/64** |
| — lexical traps | 1/32 | 31/32 |
| Unwarranted answer changes | 192/192 | 6/192 |
| Solo accuracy | 10/64 | 56/64 |
| Follows the action format | 13% | 100% |

Caveat we found ourselves: a bag-of-words classifier that knows the statement template gets 55/64 here. In-template performance partly reflects learned clause vocabulary, so we built a harder test.

### 2. Transfer to unseen statement types (frozen, 136 fresh cases)

Train on 12 templates, test on 5 never seen. The test set was hashed before the run.

| | Contracts only | **+ VitaminC** | Word-overlap rule |
|---|---:|---:|---:|
| Matched pairs handled | 102/136 (75%) | **115/136 (85%)** | 95/136 (70%) |
| — lexical traps | 27/41 | **31/41** | 0/41 |
| Valid corrections taken | 110/136 | **121/136** | |
| Unwarranted answer changes | 35/272 | **29/272** | |
| Bare pressure resisted | 136/136 | 136/136 | |
| Asks for evidence on unsupported citations | 80/272 | **208/272** | |

Paired on the same cases: + VitaminC wins 15, contracts-only wins 2 (p = 0.002). Pressure resistance transfers completely. Contrastive evidence from hundreds of unrelated topics also shifts unsupported citations from silent refusal toward asking for the deciding passage.

### 3. Safety retention (200 public `aya_redteaming` prompts, English/Arabic/Hindi/French)

| | Base | Fine-tuned (SFT) | SafeGrad (fixed) |
|---|---:|---:|---:|
| Harmful replies | 10 | 6 | 8 |
| Refusals | 67 | 86 | 80 |
| Task format leaking into chat | 0 | 0 | 0 |

Fine-tuning on this task did not erode safety (base vs SFT: McNemar p ≈ 0.34). So SafeGrad's hardening had nothing to protect, and we report it as a tested null: it costs nothing on the task but brings no measured safety gain here. The judge's HARMFUL labels matched hand checks in English and French.

## Fixes contributed back

- **SafeTune SafeGrad KL scaling (0.1.8):** `safegrad_kl_alignment_loss` uses `reduction="batchmean"` on `(batch, seq, vocab)` logits. That sums KL over every token, padding included, i.e. per-token KL × sequence length. At `max_len` 1024 the alignment gradient was ~1,000× the task gradient: training stalled (loss ~2, gradient norms up to 1,178) and the model collapsed to one action. With a masked per-token mean, SafeGrad trains normally (loss 0.05) and matches plain SFT on the task.
- **AuditKIT disk cache:** model callables that differ only in the model object they capture get the same fingerprint, so a second model can silently replay the first model's cached results. Workaround: capture a string (the checkpoint path) in the closure.

## Limitations

- Single training seed for the headline comparison.
- Labels are dataset proxies (ContractNLI gold spans, VitaminC labels), not independent human annotation.
- English task data only; safety retention was multilingual.
- The fresh held-out set is mostly "yes" cases (124/136).
- No comparison yet against inference-only baselines (evidence-aware prompting, entailment gate).
- Clarification is scored as a single turn; resolution after the user answers is not measured.

Planned follow-ups are tracked as [issues](https://github.com/Mizore66/evidencetune/issues).

## Reproduce

Code: [github.com/Mizore66/evidencetune](https://github.com/Mizore66/evidencetune)

- `data/`: `build_data_v2.py` (balanced in-domain), `build_data_v5.py` (held-out templates), `build_data_v6.py` (+ VitaminC), `build_final.py` (frozen test, `FREEZE.json`), `build_retention.py` (red-team sample).
- `jobs/`: `hf_job*.py`, run with `hf jobs uv run`; dependencies are pinned to exact Lexsi commits in each script header. `safegrad_fix.py` contains the SafeGrad KL patch and its unit check.
- `analysis/`: `analyze_v2.py`, `shortcut_audit.py`, `template_control.py`.
- `results/`: write-ups for each experiment, in order.

Total compute: about $15 of Hugging Face Jobs (A100 / RTX PRO 6000).

## Artifacts

- Dataset: [Mizore66/evidencetune-bench](https://huggingface.co/datasets/Mizore66/evidencetune-bench). Train, held-out and frozen-final splits with sidecar labels, plus AuditKIT evaluation runs with raw predictions.
- Adapter: [Mizore66/tiny-aya-global-evidencetune-lora](https://huggingface.co/Mizore66/tiny-aya-global-evidencetune-lora) (Tiny Aya Global LoRA, + VitaminC).
- Planned improvements: [GitHub issues](https://github.com/Mizore66/evidencetune/issues).

Licences: ContractNLI (CC BY 4.0), VitaminC (CC BY-SA 3.0), aya_redteaming (Apache-2.0).
