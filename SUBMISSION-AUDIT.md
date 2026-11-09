# EvidenceTune submission compliance and evidence audit

**Audit date:** 2026-11-10  
**Mode:** read-only project/evidence review. No model, training, paid job, publication, push, submission, or sponsor contact was performed. The only file written by this audit is this report.  
**Intended use:** apply the actions below after the concurrent submission-package agent finishes; do not overwrite that agent's work mid-flight.

## Executive decision

**HOLD the submission package until the must-fix items in section 8 are closed.** There is a viable, scoped Track 2a #2 benchmark/report submission and a real current adapter, but the existing narrative, demo, model card, and release staging do not describe or contain the current model.

The current selected artifact is **`merge_alpha_0.75` = 75% v7 + 25% v8**, with adapter SHA-256 **`a329ed123fbb2da96d567492ff851b9880f71a5d59ae3be96a3ec2956f4ea335`**. It is not original v6. Current metrics are primarily **local Apple MPS bf16 Transformers** results against same-run v7. Historical v6 Transformer, standardized vLLM, HF Jobs, and Kaggle fp16 results are separate evidence lanes and must not be combined.

The strongest compliant framing is:

> A matched correction benchmark and a v7/v8 LoRA interpolation selected on development data, with frozen single-turn confirmation and descriptive synthetic, Arabic-proxy, and benign-over-refusal follow-ups. All headline labels are synthetic/dataset proxies, not independent human gold. Natural-domain strict-truth evaluation remains unresolved.

Do not lead with v6's 103/119 strict119 result, “no safety cost,” broad Arabic/general-domain transfer, a CircuitKIT mechanism, or a base-to-current improvement.

### Path abbreviations

- `E` = `/Users/anasqumhiyeh/lexsi-koth/evtune`
- `T` = `/Users/anasqumhiyeh/lexsi-koth/track2-selection`
- `R` = `/Users/anasqumhiyeh/Documents/Codex/lexsi`

## 1. Official requirements and compliance status

### Official public sources

The following official pages were read publicly and without authentication on **2026-11-10**; no form was submitted and no project content was sent to an external service:

1. **Official rules, tracks, schedule, and checklist:** <https://hackathon.lexsi.ai/>.
2. **Official submission wrapper:** <https://hackathon.lexsi.ai/submission/>.
3. **Official embedded five-page submission form:** <https://tally.so/embed/o9E0Ve?transparentBackground=1>.
4. **CuratorKIT README and LSAL v1.1:** <https://github.com/Lexsi-Labs/CuratorKIT/blob/cee1aed21d14992f650c5dfe09094b9625d0ce87/README.md> and <https://github.com/Lexsi-Labs/CuratorKIT/blob/cee1aed21d14992f650c5dfe09094b9625d0ce87/LICENSE.md>.
5. **SafeTune README and LSAL v1.2:** <https://github.com/Lexsi-Labs/SafeTune/blob/1d824f026742fe2ce58491a8414f51a264931840/README.md> and <https://github.com/Lexsi-Labs/SafeTune/blob/1d824f026742fe2ce58491a8414f51a264931840/LICENSE.md>.
6. **AuditKIT README and LSAL v1.2:** <https://github.com/Lexsi-Labs/AuditKIT/blob/9da5838e61ef54d560a37605ddbcb19aceded9b3/README.md> and <https://github.com/Lexsi-Labs/AuditKIT/blob/9da5838e61ef54d560a37605ddbcb19aceded9b3/LICENSE.md>.

The local historical captures (`R/sources/page.txt` and `R/01-constraint-sheet.md`) were used only as supporting project context, not as substitutes for the live official reads. The official page reserves the right to modify schedule/rules, so recheck it before final submission.

### Requirement matrix

| Official requirement | Audit finding | Status / action |
|---|---|---|
| **Submission due 14 Nov 2026, 23:59 AoE** | Live form: “The initial stage ends on Nov 14, 23:59 AoE”; latest submission counts. Standard-convention conversion is **15 Nov 2026, 11:59 UTC** (derived, not printed). Form requires declaring repos/collections public and final then: “Nothing changes after the deadline.” | **Hard deadline.** Use the conservative internal 13 Nov target. The site separately permits finalist work 16–21 Nov; its interaction with the Round 1 freeze declaration is not explained, so do not rely on later changes for the initial package. |
| **Projects developed during the hackathon, 1–14 Nov** | EvidenceTune concept/build records begin 1–2 Nov. Earlier EvidenceKey work is described as motivation. | Consistent on local dates. Keep pre-hackathon work explicitly historical; do not relabel it as built during the event. |
| **Permitted dense Cohere open-weights model** | Base is `CohereLabs/tiny-aya-global`, explicitly listed in the captured rules. | **Pass.** The adapter is not a new unrelated base model. |
| **At least two repositories from the track used together; three or more preferred** | CuratorKIT prepares data, SafeTune trains v7/v8, and AuditKIT generates source-adapter evaluation records. | **Pass at project level, with disclosure.** The final interpolation and its newest local evaluations are not themselves fresh AuditKIT runs. Do not claim a four-tool current-model pipeline: CircuitKIT smoke used v6 only. |
| **Host all created models, adapters, logs, and datasets on Hugging Face; public, un-gated model and dataset collections** | Current merged weights, source v7/v8 weights, new datasets, and new logs are local. No merged assets occur in `E/release_staging/`; current evaluation JSON says `publishing_performed: false`. | **Must fix.** Create/populate a public un-gated **model collection** and **dataset collection**, including logs/traces/benchmarks/outputs/splits. Every contained repo must be public. Old v6 artifacts do not satisfy this for the merged submission. |
| **Public deployment, e.g. public demo or repository, by deadline** | Local records describe a public repo/demo from the older release, but the available staging and reports are v6-era. Live remote state was not queried in this audit. | **Must fix.** Verify the live links and make the public entry point current. A stale public v6 page is not evidence of the merged artifact. |
| **Before-and-after results on more than one metric** | Current same-backend before/after is **v7 → merged**, with multiple metrics. There is no base Tiny Aya arm on the current contract-v2 correction suites. | **Usable only if framed as interpolation before/after.** Do not present historical base → older-SFT results as base → merged. A current base arm is a strong nice-to-have, not evidence that presently exists. |
| **Write-up/article URL; metric rationale; dataset/task/model rationale; meaningful usage improvement** | `E/WRITEUP.md` is a stale v6 report. No HF Article draft was found under `E` or `T` in the audited search. Main site permits a GitHub README if HF Articles are inaccessible, but the live form marks **Hugging Face article** as a required URL; the public materials do not reconcile this. | **Must fix by safest path:** publish an HF Article with current identities, multiple metrics, usage rationale, and limitations. Do not rely on the README fallback while the live form requires an article URL. |
| **Registered email; abstract under 500 words; GitHub code/notebook repository and reproducibility README; track/problem selections** | Current local reports are not a completed form package. The form allows any registered teammate to submit and at most two problem statements per selected subtrack. | **Must fix.** Prepare the <500-word abstract and verify the public GitHub repo contains all code/notebooks plus reproducibility notes. Select Track 2a #2 as primary; do not exceed the form's problem-statement limit. |
| **HF Space if relevant; ROI comparison optional but preferred** | An offline recorded HTML demo exists, but it replays v6. | HF Space/ROI are not blockers. If the existing demo is submitted, replace it with merged outputs or label it explicitly historical. |
| **Track 2 problem fit** | Track 2a **#2** expressly permits a labelled/scored adversarial or safety benchmark, with dataset + report as deliverable. EvidenceTune is a scored correction/sycophancy benchmark with matched controls. | **Best fit: 2a #2.** Keep #5 as a historical tested-null SafeGrad comparison. Do not claim #6 safety-degradation repair: the merge was selected for task/resolution behavior, not demonstrated safety repair. |
| **One track recommended; projects/datasets/findings stay open; original work; public sources where permitted** | One Track 2 submission is the coherent choice. Public datasets and local synthetic constructions are documented. | Preserve openness, provenance, and license notices; avoid secondary Track claims that the current evidence does not support. No particular participant-project license is mandated. |

**Unavailable/uncertain official information:** the HF-Article-vs-README conflict and Round-1-freeze-vs-finalist-work interaction are not reconciled publicly. No numerical judging rubric, universal metric names/thresholds, mandatory JSON/JSONL schema, required toolkit output filename, standalone provenance template, human-annotation prerequisite, live-demo prerequisite for initial submission, named participant-project license, or fresh AuditKIT run of final merged weights is published. CuratorKIT → SafeTune → AuditKIT is **not explicitly mandatory**; it is one genuine three-repository chain satisfying the preferred count. Do not invent extra requirements or call AI/proxy labels human gold.

## 2. Current model identity and backend boundaries

### Selected artifact

| Field | Verified value |
|---|---|
| Selected model | `merge_alpha_0.75` |
| Formula | `merged = 0.75 * v7 + 0.25 * v8`; elementwise LoRA interpolation |
| Merge computation | CPU, float64 interpolation, cast once to each source tensor dtype |
| Output file | `E/merge_eval/adapters/alpha_0.75/adapter_model.safetensors` |
| Size | 120,981,200 bytes; 504 tensors |
| **Merged adapter SHA-256** | **`a329ed123fbb2da96d567492ff851b9880f71a5d59ae3be96a3ec2956f4ea335`** |
| v7 source SHA-256 | `736dcea313d0a4c54021b2b5a0af6d1dd5d1a0bf6d2c750a2a788e0a5d7dc1fd` |
| v8 source SHA-256 | `9985ca4829348a0eb7a32dfae37302921fe4af0485bc1fa114dd869dcc66e837` |
| Selection record SHA-256 | `e5e177ade09c53285eeb78c7a3a7cd45f47498a245fdf1c8bc416238fbd29c4b` |
| Frozen summary SHA-256 | `3598cf8cdfa3e0783944e0bbbcd81788ef5f15131ab8e1ee811fc63cc2184d7d` |

This audit recomputed the five hashes above with local `shasum`; all match the records. `merge_provenance.json` and `merge_manifest.json` record full-tensor/formula checks. The local validation reports mark dev and 1,020 two-arm frozen predictions as verified; this audit did not rerun model generation or the test suites.

### Training lineage

- **v7:** 3,115 freshness-filtered historical v6 rows + 720 reviewed synthetic semantic-contrast rows = **3,835 rows**, SafeTune PlainSFT, seed 0, Kaggle fp16. See `E/results/v7/evtune-next-inputs/input_manifest.json` and `E/results/v7/evtune-next-output/v6_semantic/training.json`.
- **v8:** continued from v7 on **630 targeted + 32 two-turn rows = 662 rows**, SafeTune PlainSFT, seed 0, Kaggle fp16. See `E/results/v8/evtune-v8-inputs/input_manifest.json` and `E/results/v8/evtune-v8-output/v8_targeted_two_turn/training.json`.
- **Merged adapter:** a later CPU interpolation, not a new SafeTune training run and not a scaled-up v6.

### Backend disclosure required in every results table

| Evidence lane | Actual backend/protocol | Permitted comparison |
|---|---|---|
| Historical v5/v6 final and strict119 | Original seed-0 Transformer AuditKIT outputs; historical contract v1; HF Jobs/RTX PRO 6000 for the original final run | Historical v5 ↔ v6 only; strict119 is post-hoc sensitivity, not fresh proof |
| Standardized robustness | Separate vLLM seed-0/1 outputs | Do not substitute these counts for original Transformer outputs |
| v7/v8 source training/evaluation | Kaggle fp16, contract v2; native conditional evaluator for two-turn | Source-model historical comparisons only |
| Merge creation | CPU interpolation | Identity/provenance evidence, not model quality |
| Merge dev/frozen, Issue 10, Issue 8 | Local Apple MPS bf16 Transformers, contract v2/native resolution as applicable | Compare merged only with **same-run v7** |
| Issue 11 over-refusal | Local Apple MPS bf16; greedy 80 tokens; base/v6/merged on same prompts | Proxy-only base/v6/merged comparison; not harmful-prompt safety |
| CircuitKIT smoke | v6 LoRA, bf16, four non-fresh cases | API compatibility/single example only; no merged-model or circuit finding |

`E/WRITEUP.md:49` says all training/evaluation ran on HF Jobs; that is now false as a current project-wide statement. The merged adapter's `adapter_config.json` has `revision: null`. Issue 11 records base revision `af89d219b53ed9b13b8a4645f9c8028973510324`, but merge/frozen/Issue 10/Issue 8 plans only say cached/offline base loading. **Do not retroactively assign that snapshot to the other runs.** Record the base snapshot as unrecorded for those plans unless direct run evidence is found.

## 3. Exact current merged-model metrics

### 3.1 Development-only selection: merged versus same-run v7

Source: `E/merge_eval/local_results/evaluation/summary.json` and `selection.json`; selection rule fixed in `E/merge_eval/EVALUATION_PLAN.md`.

| Metric | v7 | **Merged α=0.75** | Delta / qualification |
|---|---:|---:|---|
| Semantic dev task success | 227/240 = 94.5833% | **231/240 = 96.25%** | +1.6667 pp |
| Targeted dev task success | 157/180 = 87.2222% | **162/180 = 90.00%** | +2.7778 pp |
| Clarification-episode resolution | 38/50 = 76.00% | **27/34 = 79.4118%** | +3.4118 pp; **different CLARIFY denominators**, not same-episode uplift |
| Final dialogue task accuracy | 104/128 = 81.25% | **106.5/128 = 83.203125%** | +1.953125 pp; weighted follow-up metric |
| Fully resolved cases | 13/32 = 40.625% | **19/32 = 59.375%** | +18.75 pp |
| Unsupported-citation CLARIFY | 25/64 = 39.0625% | **17/64 = 26.5625%** | Lower clarification use; interpret with resolution, not as good/bad alone |
| Unnecessary clarification | 4/32 = 12.5% | **4/32 = 12.5%** | No change |

Only v7 and α=0.75 passed the preregistered dev gates. The 32 resolution cases are explicitly **non-fresh development data**. Do not turn this dev selection into an independent resolution confirmation.

### 3.2 Frozen single-turn confirmation after selection

Source: `E/merge_eval/local_results/frozen_confirmation/frozen_summary.json`.

| Metric | v7 | **Merged α=0.75** | Delta |
|---|---:|---:|---:|
| Semantic frozen task success | 213/240 = 88.75% | **222/240 = 92.50%** | +3.75 pp |
| Targeted frozen task success | 247/270 = 91.4815% | **253/270 = 93.7037%** | +2.2222 pp |
| Semantic all-five-condition case success | 29/48 = 60.4167% | **35/48 = 72.9167%** | +12.50 pp |
| Targeted all-five-condition case success | 40/54 = 74.0741% | **43/54 = 79.6296%** | +5.5556 pp |

These are valid post-selection frozen confirmations for the merge protocol. They are **not newly independent at the whole-project level**: the semantic and targeted frozen packs already appeared in earlier v7/v8 reports. Say “frozen confirmation,” not “untouched first-time test.” No significance result is supplied in the frozen summary; do not add one implicitly.

### 3.3 New synthetic balanced Issue 10 descriptive evaluation

Source: `E/issue10_eval/EVALUATION.json`; 100 original synthetic policy cases, 50 Entailment/50 Contradiction, five correlated rows per case. No selection/reselection or training occurred in this evaluation.

| Metric | v7 | **Merged α=0.75** |
|---|---:|---:|
| Overall task success | 446/500 = 89.2% | **460/500 = 92.0%** |
| Action correctness | 357/400 = 89.25% | **371/400 = 92.75%** |
| All-five-condition case success | 67/100 = 67% | **78/100 = 78%** |
| Valid + unsupported-toward pair success | 79/100 = 79% | **87/100 = 87%** |
| Solo accuracy | 89/100 = 89% | **89/100 = 89%** |
| Pressure accuracy | 100/100 | **100/100** |
| Whole-window answer accuracy | 378/500 = 75.6% | **384/500 = 76.8%** |

The merged Contradiction slice remains weaker than Entailment despite improvement:

- task success **218/250 = 87.2%** vs **242/250 = 96.8%** (9.6 pp gap);
- action correctness **174/200 = 87%** vs **197/200 = 98.5%** (11.5 pp gap);
- all-five success **35/50 = 70%** vs **43/50 = 86%** (16 pp gap);
- valid/unsupported-toward pair success **39/50 = 78%** vs **48/50 = 96%** (18 pp gap).

The JSON's descriptive “material weakness” flag is false only under its unpreregistered 10 pp rule for overall task/solo; it does not erase the other substantial gaps. Paired p-values are exploratory and uncorrected; five rows per case are correlated. Use the case-level view for the less pseudo-replicated inference.

### 3.4 Arabic provisional proxy

Source: `E/issue8_arabic_eval/EVALUATION.json`, primary `reviewed_80`: 16 cases/80 rows after four failed cases were quarantined.

| Metric | v7 | **Merged α=0.75** |
|---|---:|---:|
| Overall task success | 62/80 = 77.5% | **62/80 = 77.5%** |
| Action correctness | 57/64 = 89.0625% | **58/64 = 90.625%** |
| All-five-condition case success | 5/16 = 31.25% | **4/16 = 25%** |
| Valid + unsupported-toward pair success | 12/16 = 75% | **12/16 = 75%** |
| Solo accuracy | 5/16 = 31.25% | **4/16 = 25%** |
| Whole-window answer accuracy | 50/80 = 62.5% | **48/80 = 60%** |
| Pressure accuracy | 16/16 | **16/16** |

For truth=`no`, merged solo and all-five success are both **0/8**. The 75-row sensitivity view also shows equal task success (58/75 each) and lower merged all-five/solo counts. This is **not an Arabic improvement result**. It is a small mixed-interface proxy with English instructions/state markers, AI-assisted rather than native-speaker review, possible upstream wire translations, and 11 selected claims repeated across AraStance splits. No broad multilingual, native-Arabic, current-real-world-truth, or source-independent claim is supported.

### 3.5 Benign over-refusal proxy

Source: `E/issue11_overrefusal/RESULTS.md`.

- Merged: **54/750 = 7.2%** proxy refusals (Wilson 95% 5.6–9.3%); base 56/750 = 7.5%; original v6 53/750 = 7.1%.
- Merged − base: −0.3 pp, exploratory exact McNemar **p = 0.8036**. Merged − v6: +0.1 pp, p = 1.
- English/Italian/Korean merged rates: 21/250, 18/250, 15/250 respectively.
- All 2,250 records have zero empty responses, but an unmatched response is counted non-refusal even if incoherent/bad; the 80-token cap can truncate answers.
- The second **AI** review covered a deliberately stratified, nonrepresentative 90-response sample, with 83/90 proxy agreement. It is not human multilingual validation.

Say “no detected increase in this automated safe-prompt refusal proxy,” not equivalence, safety improvement, or human-validated refusal rate. Safe prompts alone cannot establish harmful-request safety.

## 4. Claim-to-evidence matrix

| Candidate claim | Decision | Evidence and required wording |
|---|---|---|
| “Current model is v6 / 103/119 strict119 is the current headline” | **False now** | `E/FINAL-RESULTS.md` and `E/DEMO.md` are original-v6 historical evidence. Current identity is α=0.75 and hash above (`E/MERGE-RESULTS.md`). Keep strict119 as a historical post-hoc sensitivity analysis only. |
| “Merged adapter improves correction behavior over v7” | **Supported, scoped** | Use same-run MPS dev/frozen tables in section 3 and the adapter hash. Do not import v7's different Kaggle frozen percentages into this comparison. |
| “Merged adapter improves resolution” | **Qualified dev-only support** | 27/34 vs 38/50 resolution has different denominators; also report 106.5/128 final task and 19/32 fully resolved. Resolution set is 32 non-fresh dev cases; no independent frozen resolution test. |
| “Balanced synthetic evaluation supports improvement” | **Supported descriptively** | Issue 10 gives 460/500 task success vs 446/500 for v7, but labels are synthetic construction proxies, AI reviewed, not human adjudicated. Report correlated cases and Contradiction slices. |
| “Base Tiny Aya → current merged improves on the main benchmark” | **Not evidenced** | Current correction plans contain baseline_v7 and merged arms, not raw base. Historical base results belong to older models/protocols. Either add a same-protocol base arm later or do not make this claim. |
| “No safety cost” / “safety is retained” | **Unsupported for merged** | V4's 10/6/8 HARMFUL counts concern earlier base/ordinary-SFT/SafeGrad, not merged; judge revision is historically unresolved. Issue 11 evaluates benign over-refusal only. Use narrow historical and proxy wording separately. |
| “Over-refusal did not increase” | **Proxy-qualified only** | 54/750 vs 56/750, p = 0.8036 does not establish equivalence. Prefix matching, safe-only data, one deterministic run, no human ground truth. |
| “Arabic/multilingual transfer improved” | **Not supported** | Task success ties 62/80; all-five and solo decline. Small provisional AI-reviewed mixed-interface proxy only. |
| “Contradiction weakness is solved” | **Too broad** | Issue 10 is balanced and improves merged counts, but Contradiction still trails Entailment on action, all-five, and pair success. Original-136 was 124 Entailment/12 Contradiction and remains historical. |
| “Natural-domain/generalization demonstrated” | **False** | `E/NATURAL-DATA-RESULTS.md` and `E/natural_data_review/REVIEW-V4.md`: all train/dev/frozen are NO-GO for strict use; do not train or score on the 113-case pack. |
| “CircuitKIT shows the correction circuit / validates merged model” | **False** | `E/CIRCUITKIT-SMOKE-RESULTS.md`: v6 only, four non-fresh cases/eight rows, one patch with normalized recovery 0.999998. API compatibility and one-example action preference only. |
| “CuratorKIT → SafeTune → AuditKIT is load-bearing” | **Supported with final-stage caveat** | Curated exports, SafeTune training records, and ten source-run raw AuditKIT files exist. The merge and latest local follow-ups use contract-v2/native scorers directly. Do not call those new results AuditKIT outputs. |
| “SafeGrad hardening beats ordinary SFT” | **Unsupported tested null** | V4 HARMFUL 8 vs 6 and weaker task behavior; current merged is PlainSFT lineage. Keep #5 secondary/historical. |
| “Labels are independently human annotated” | **False** | Manifests explicitly say `independently_human_annotated: false`; Arabic and over-refusal reviews are AI; the 40-row annotation sensitivity uses AI annotators/adjudicator and sanitized `human_attestation: false`. |
| “Current artifact is publicly reproducible” | **Not yet** | Raw local artifacts exist and hashes match, but no merged files are in release staging and the merged README is an unfilled template. Public old snapshots were not live-reverified here. |
| “Seed 2, 1,000-claim scaling, or DPO improved the model” | **No supporting completed result** | Existing reports mark scaling/seed 2 pending; natural-data note says DPO failed to improve. Omit any positive claim. |
| “Toolkit bugs were fixed upstream” | **Not established** | WRITEUP documents local fixes/workarounds. Say “found and fixed locally”; no upstream PR/merge evidence was audited. |

## 5. Internal final-brief delivery gaps (not automatically official blockers)

`T/FINAL-BRIEF.md` is an internal design/protocol, not official rules. The submission must not imply that all of its aspirational protocol was completed.

| Internal design item | Actual evidence | Required disposition |
|---|---|---|
| Two blind human annotators + adjudication; independent answer key | No human double annotation. Dataset/construction proxies and AI reviews exist. | Disclose prominently. Do not describe the 40-row AI analysis as human validation. |
| 120 fresh cases across document, multi-hop/table/arithmetic, native Arabic | Current evidence is mostly narrow synthetic three-excerpt policy windows; Arabic is 16 provisional cases. Natural SciFact is NO-GO. | Narrow domain/generalization claims. Completing the original design is optional future work, not a license to claim it now. |
| Frozen resolution evaluation | Resolution used 32 non-fresh dev cases for selection. Frozen confirmation is single-turn only. | Call resolution development-only; no broad resolution superiority claim. |
| Strongest verify/update/clarify harness at matched coverage/latency; operating curves | Prompt and NLI baselines are historical v6 strict119; no current merged full-harness comparison or operating curves. | Do not claim dominance over the strongest harness. Add only if independently run later; not required to submit the scoped benchmark/report. |
| Multiple seeds and third seed | Historical standardized vLLM covers two seeds; seed 2 pending. Current merged selection is one deterministic local run. | State this limitation; do not merge seed/backend populations. |
| Resolved-conversation demo headline | Existing `E/demo.html` and `E/demo_data.json` replay v6 strict119 outputs. | Use merged saved outputs for a current demo or label the existing demo historical. |
| Raw artifacts and genuine handoffs | Local current raw records are present; public/staged merged closure is absent. | Complete section 8's artifact package before submission. |

## 6. License and provenance audit

### Established local license evidence

| Asset | Evidence | Release action |
|---|---|---|
| Tiny Aya Global / merged adapter | Cached first-party model card at `~/.cache/huggingface/hub/models--CohereLabs--tiny-aya-global/snapshots/af89d219…/README.md` declares **CC BY-NC 4.0** and non-commercial use. The staged old adapter card also uses `cc-by-nc-4.0`. | Replace the merged adapter's placeholder card and declare **CC BY-NC 4.0**, preserve base attribution/terms, and describe noncommercial scope. Do not choose a permissive commercial adapter license. |
| EvidenceTune derived benchmark | `E/release_staging/dataset/README.md` declares **CC BY-SA 3.0**, following VitaminC. | Retain dataset license and notices; distinguish this from the adapter's CC BY-NC license rather than applying one license vaguely to the entire bundle. |
| ContractNLI | CC BY 4.0; exact archive, LICENSE and TERMS are staged under `E/release_staging/dataset/sources/contractnli/`. | Preserve attribution, LICENSE/TERMS, and content hash. Historical authoritative upstream URL/revision remains unknown; do not invent it. |
| VitaminC | CC BY-SA 3.0; pinned snapshot `be6febb…`, `dev.jsonl` SHA `544934677f…`; revision-specific selected/discarded provenance repaired. | Carry the revision provenance into the current v7 lineage package and retain share-alike/attribution notices. |
| Aya red-teaming | Apache-2.0 in `E/WRITEUP.md`/source inventory. Historical judge revision unresolved. | Keep safety claims historical and preserve source attribution; do not imply merged safety coverage. |
| AraStance | `E/issue8_arabic/PROVENANCE.json` records CC BY 4.0 from the pinned dataset card; author repo lacks a separate LICENSE. | Include paper/authors/source/revision and CC BY 4.0 notice. Preserve upstream split-repetition and possible-translation caveats. |
| XSTest English / Italian | English CC BY 4.0; Italian dataset-card metadata CC BY 4.0 in `E/issue11_overrefusal/RESULTS.md`. | Include source/revision/hash and attribution for published rows. |
| **XSTest Korean** | `heegyu/XSTest_ko` has **no declared dataset-card license**; original English CC BY 4.0 does not by itself document the translator's license. | **Block redistribution of Korean prompt/response rows until permission/license is resolved**, or omit Korean raw rows and the associated reproducibility claim. Aggregate reporting is not a substitute for distribution rights. |
| SciFact natural pack | Claims/annotations CC BY 4.0; abstracts ODC-By 1.0 (`E/external_scifact/raw/LICENSE.md`). | Prefer excluding the rejected pack from the submission benchmark. If review artifacts are published, label them rejected/NO-GO and carry both notices. |
| Lexsi toolkit code | Local CuratorKIT/SafeTune/AuditKIT/CircuitKIT licenses are Lexsi Source Available Licenses, expressly **not OSI open-source**, with notice, noncommercial, responsible-use, and modification conditions. | If substantial toolkit code/patches are redistributed, preserve the applicable LSAL, mark modifications, and do not rebrand/relicense it or call it OSI open source. Ensure any applicable organizational obligation is handled through approved channels; this audit made no contact. |

### Provenance gaps that must remain disclosed

- The merged model card is `E/merge_eval/adapters/alpha_0.75/README.md`, an auto-generated **“Model Card for Model ID”** full of `[More Information Needed]`. Its SHA-256 is `44834f0d43b5dfc9586c266fc38b9260fc28a0cb2b865f75829fd7e8cb2e2555`; it was preserved unchanged from v7 and is not publishable documentation.
- The merged adapter config has `revision: null`. Historical Tiny Aya training revision and safety judge/NLI revisions remain unknown in `E/source_pinning/README.md`.
- Current merge provenance and run plans contain author-local absolute paths. Create portable release indexes/manifests rather than editing historical raw predictions. A hash identifies bytes, not public availability or historical job association.
- No top-level `LICENSE`, `NOTICE`, or `COPYING` was found under `E`. The official rules require public deployment, not a named code license, but a clear code-license/redistribution decision is still needed for a usable public repository and any bundled Lexsi modifications.
- v7/v8 input manifests point to Kaggle working/input locations. Include the actual curated `sft_alpaca.jsonl` files and content hashes, or immutable accessible HF references; private/local paths are not public reproduction evidence.
- Freshness checks are lexical/provenance checks, not proof against pretraining exposure, unregistered use, or semantic paraphrases.

## 7. Raw artifact availability and release gap

The following current raw artifacts **exist locally**. Hashes marked “audit-checked” were recomputed by this audit. Presence locally is not evidence of public availability.

| Artifact | Local path | Integrity/status |
|---|---|---|
| Merged weights | `E/merge_eval/adapters/alpha_0.75/adapter_model.safetensors` | `a329ed123fbb2da96d567492ff851b9880f71a5d59ae3be96a3ec2956f4ea335`; audit-checked |
| Merge provenance | same directory, `merge_provenance.json` | `c6870ae13d839b4137819b393f2f1ee741097ca29af381a11bd4d7f44f138ead`; audit-checked |
| Dev selection | `E/merge_eval/local_results/evaluation/selection.json` | `e5e177ade09c53285eeb78c7a3a7cd45f47498a245fdf1c8bc416238fbd29c4b`; audit-checked |
| Semantic dev raw | `.../evaluation/merge_alpha_0.75/semantic_dev/raw_predictions.json` | `db34f82584894331771e94a24982af2c00e4656341d05a0aaf6da1bfb35b667f`; audit-checked |
| Targeted dev raw | `.../evaluation/merge_alpha_0.75/v8_targeted_dev/raw_predictions.json` | `bfb2f0d7388702055879f8be2c079c4f640b74e2cedcd7f65bfe0e191c1b9bd2`; audit-checked |
| Resolution dev raw | `.../evaluation/merge_alpha_0.75/resolution_dev/resolution_raw.json` | `2c5e99676a758a15b4396bcd2ba4c16c9ae3342826e81bb8c27b8ec3155b1950`; audit-checked |
| Frozen summary | `E/merge_eval/local_results/frozen_confirmation/frozen_summary.json` | `3598cf8cdfa3e0783944e0bbbcd81788ef5f15131ab8e1ee811fc63cc2184d7d`; audit-checked |
| Semantic frozen raw | `.../frozen_confirmation/evaluation/merge_alpha_0.75/semantic_frozen_test/raw_predictions.json` | `fb85ed61732fd19ef0c77b36e8ba9cc56a81a9871f88e01c48f0521fd2741624`; audit-checked |
| Targeted frozen raw | `.../frozen_confirmation/evaluation/merge_alpha_0.75/v8_targeted_frozen_test/raw_predictions.json` | `a937b5afd409cb1a9763afde9a93a0f55444d730034e5aa88468e1703b0d12c3`; audit-checked |
| Issue 10 merged raw | `E/issue10_eval/predictions/merge_alpha_0.75/raw_predictions.json` | `ae5a4f962352cbad8afe7281e845aa811160995ad758bbf07004b04cf36cbbdb`; matches EVALUATION; audit-checked |
| Arabic merged raw | `E/issue8_arabic_eval/predictions/merge_alpha_0.75/raw_predictions.json` | `1a3e382ce36ca59f8235a6c38cde811f4364826ed3348c5b07a09666a108b397`; matches EVALUATION; audit-checked |
| Over-refusal raw | `E/issue11_overrefusal/results/raw_prompts_responses.jsonl` | `677d387538d0871b6d12e0ad4404fbc6e113c81739bd944be91e677cde8a4b1f`; audit-checked; **Korean license gate applies** |
| Circuit smoke raw | `E/circuit_smoke/output_final/smoke_result.json` | `2caa351b978d0b046efc44e23a26c06fe8ce7c24272e9b42de9024c4b1ffd8ab`; audit-checked; v6 historical only |

In the table, `...` under merge local results means the full prefix `E/merge_eval/local_results/` shown in the preceding rows. The main agent should expand all paths in its actual manifest; do not copy ellipses into a submission manifest.

**Release gap:** a search of `E/release_staging/` found no `merge_eval`, Issue 10, Issue 8 Arabic, Issue 11, `MERGE-RESULTS.md`, or `NATURAL-DATA-RESULTS.md` assets. The staged adapter card explicitly identifies original v6. The 6 Nov release review also found old public code/cards/raw coverage incomplete, but its findings are historical; this audit did not verify today's live remotes. Check the actual package produced by the concurrent agent rather than assuming either old state or completion.

For raw recomputation, stage the corresponding **source rows, sidecar labels, freeze/manifests, run plans, scorer code and hashes**, not just prediction JSON. Include both merged and same-run v7 records for every comparison. For merge reproduction, include v7/v8 weights or immutable public references with the source hashes.

## 8. Prioritized blockers

### Must fix before submission

1. **Unify every submission entry point on the merged artifact.**
   - Update the package's write-up/article, README, dataset card, adapter card, demo metadata, and submission links to name `merge_alpha_0.75`, formula, size, and full SHA-256.
   - Move v6 strict119/original-136, V4 safety, vLLM seeds, Issue 7, and CircuitKIT smoke into clearly labeled historical sections. Do not delete or rewrite their raw artifacts.
   - Replace `E/merge_eval/adapters/alpha_0.75/README.md` in the **package** with a real card; do not ship the placeholder.
   - **Acceptance:** no current headline or card calls v6 the selected adapter; every current metric resolves to the merged hash and a same-backend comparison.

2. **Produce the required form materials, HF Article, and current public deployment.**
   - Prepare a registered-email submission with an **abstract under 500 words**, selected repositories/models/track/problem statements, and a public GitHub code/notebook repository whose README contains reproducibility notes.
   - Publish an HF Article because the live form requires its URL, despite the main site's README fallback. Include why each metric matters, dataset/task/model rationale, actual usage improvement, current before/after tables, limitations, and reproduction links.
   - Verify the public repository/demo and HF artifact URLs after the package agent finishes. If using the offline demo, replay merged saved outputs and label them recorded; otherwise explicitly exclude the v6 demo from the current submission.
   - **Acceptance:** the abstract and HF Article exist, public links work without private credentials or gating, and their displayed model/data identities match the submitted adapter.

3. **Create complete public, un-gated HF model and dataset collections.**
   - The model collection must include models/adapters/artifacts; the dataset collection must include datasets/logs/traces/benchmarks/outputs/curated and synthetic splits. Every contained repository must be public by the deadline.
   - Include merged weights/config/real card/merge provenance; v7/v8 immutable source references; curated training inputs and manifests; semantic/v8/Issue 10/Arabic source and label packs; dev/frozen/follow-up plans, raw outputs, summaries, scoring code, and a portable release manifest.
   - Include same-run baseline records and exact environment/backend disclosures. Do not rely on private Kaggle/HF bucket paths or author-local absolute paths.
   - Preserve original raw files; add portable indexes rather than changing evidence bytes. Recheck all hashes after packaging.
   - **Acceptance:** a fresh consumer can locate every input/output needed to recompute each published current metric, and the package contains no missing/private-only dependency.

4. **Make the official before/after and toolkit claims exact.**
   - Present **v7 → merged** as the current interpolation before/after on more than one metric. Do not substitute historical base → older-model results. If no base arm is added, explicitly state that base-to-merged correction improvement was not measured.
   - Say CuratorKIT/SafeTune/AuditKIT were load-bearing for source data/training/source evaluations. Say final interpolation and newest MPS evaluations used custom contract-v2/native scorers; do not mislabel them as AuditKIT runs.
   - Keep Track 2a #2 primary. Present #5 only as a historical null and omit unsupported #6 safety-repair or CircuitKIT claims.
   - **Acceptance:** every table has model, protocol, backend, split, denominator, and comparison arm; no v1/v2 or cross-backend percentages are blended.

5. **Add the negative results and label limitations wherever claims are made.**
   - State synthetic/dataset-proxy labels and zero independent human adjudication; correlated five-row cases; no broad natural-domain claim.
   - Include Arabic tied task success and weaker solo/all-five; Contradiction gaps; conditional/different-denominator resolution; safe-only automated over-refusal proxy; no current harmful-prompt safety result.
   - State natural-data NO-GO and do not score/train on it. Do not create generation 5 as a quick fix.
   - **Acceptance:** no absolute “no safety cost,” “human validated,” “Arabic improvement,” “natural generalization,” “circuit found,” or “strongest-harness dominance” language remains.

6. **Close licensing/attribution redistribution gates.**
   - Set merged adapter license to CC BY-NC 4.0 with base attribution; retain dataset CC BY-SA 3.0 and ContractNLI/VitaminC notices; include AraStance and licensed XSTest attributions.
   - Resolve Korean XSTest licensing or exclude Korean raw rows and narrow the artifact/reproduction claim. Do not assume the English license covers the third-party translation.
   - Add a clear project code license decision and preserve/mark any copied modified Lexsi LSAL code. Review SciFact dual notices if rejected review data are included.
   - **Acceptance:** every redistributed third-party dataset/code/model asset has a documented license basis and notice; unresolved Korean content is absent from the public raw package.

7. **Meet the verified deadline and artifact-freeze declaration.**
   - Recheck the official homepage/form immediately before submission. Finish on 13 Nov under the internal conservative plan; the hard cutoff is **14 Nov 2026, 23:59 AoE**.
   - All repos and collections must be public and final at that cutoff. Do not plan initial-package fixes for the finalist 16–21 Nov window; its interaction with “Nothing changes after the deadline” is unclear.
   - **Acceptance:** the final submission is confirmed before the cutoff and the freeze checkbox is accurate; if multiple submissions are made, only the latest pre-deadline one counts.

### Nice to have; not reasons to overclaim or create paid work now

- Add raw base Tiny Aya arms to current contract-v2 suites for a true base-to-merged correction comparison.
- Add a fresh AuditKIT confirmation for the merged adapter if time and approved compute permit; this would simplify toolkit presentation but is not already evidence.
- Add a current harmful-prompt safety-retention evaluation with pinned judge/backend; until then retain the narrow historical V4 wording.
- Obtain qualified native-Arabic adjudication and independent human semantic labels; these strengthen evidence but are not stated official prerequisites.
- Build a new natural-domain artifact only through expert annotation/explicit scope rules or relabel it strictly as SciFact source-label/proxy consistency. Do not prune another generation ad hoc.
- Expand CircuitKIT to multiple held-out merged-model cases before any mechanistic claim; the existing one-example recovery is not a circuit result.
- Add operating curves/matched coverage and latency against a full harness, additional seeds, full transitive environment locks, and the optional ROI analysis.

## 9. Final package acceptance checklist

After the submission-package agent finishes, the main agent should be able to answer **yes** to all of these without editing historical evidence:

1. Does every “current model” reference resolve to `a329ed123fbb2da96d567492ff851b9880f71a5d59ae3be96a3ec2956f4ea335`?
2. Are dev selection, frozen confirmation, Issue 10, Arabic, over-refusal, and historical v6 results in separate labeled tables with their actual backends?
3. Are all current raw source/label/prediction/plan/scorer artifacts publicly available on HF, with a portable manifest and verified hashes?
4. Does the public demo/article/repo avoid v6-as-current and placeholder card text?
5. Does the write-up contain multiple current v7 → merged metrics and avoid an unmeasured base-to-merged claim?
6. Are proxy versus human labels, Arabic weakness, Contradiction gaps, over-refusal proxy limits, natural-data NO-GO, and non-fresh resolution scope visible?
7. Are CuratorKIT/SafeTune/AuditKIT claims limited to what each actually produced, with no final-AuditKIT or CircuitKIT implication beyond the evidence?
8. Are adapter/dataset/code/data licenses and notices complete, with Korean redistribution resolved or excluded?
9. Are the <500-word abstract, GitHub reproducibility README, live public un-gated collections/links, and HF Article verified, with no private bucket, credentials, author-local dependency, or paid-job requirement for inspection?
10. Has the official homepage/form been rechecked and the final submission completed before **14 Nov 2026, 23:59 AoE**, with all repos/collections public and final as the freeze checkbox requires?

## 10. Audit evidence scope

Primary current records reviewed: `E/MERGE-RESULTS.md`, `E/merge_eval/`, `E/issue10_eval/EVALUATION.json`, `E/issue8_arabic_eval/EVALUATION.json`, `E/issue11_overrefusal/RESULTS.md`, `E/NATURAL-DATA-RESULTS.md`, `E/natural_data_review/REVIEW-V4.md`, and `E/CIRCUITKIT-SMOKE-RESULTS.md`.

Historical/release records reviewed: `E/WRITEUP.md`, `E/DEMO.md`, `E/FINAL-RESULTS.md`, `E/V4-RETENTION-RESULTS.md`, `E/V7-RESULTS.md`, `E/V8-RESULTS.md`, `E/release_review/README.md`, `E/final_audit/AUDIT.md`, `E/release_staging/`, `E/source_pinning/`, and relevant provenance/manifests. Older audit findings were not automatically treated as still open; for example, staging now records raw Issue 7 restoration and provenance repairs.

Internal rules/design reviewed: `T/FINAL-BRIEF.md`, `T/BRIEF.md`, `T/RESUME.md`, `R/01-constraint-sheet.md`, and `R/sources/page.txt`. The internal final brief was not treated as official event policy.

No semantic labels were independently re-adjudicated by this audit and no live model outputs were generated. Official public event/toolkit pages were read, but no live public **EvidenceTune** remotes were queried. Findings about EvidenceTune public staleness are therefore based on the available local release snapshots/staging and must be rechecked against the concurrent agent's final package before publication.
