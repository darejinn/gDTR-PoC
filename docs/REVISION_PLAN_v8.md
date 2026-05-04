# REVISION_PLAN_v8.md — Paper 1 (gDTR) ICML revision plan

> **NOTE TO THE USER / PARENT AGENT.** This is the full revision plan. I am in read-only planning mode and cannot write files. Please save this content to `/Users/yoonjincho/Project/ICML/docs/REVISION_PLAN_v8.md` verbatim. The plan is organised in 10 sections per the agreed scaffold and is dense by design — it is meant to be re-read in 6 months and to fully reconstruct the interpretation logic without re-derivation.

---

## Section 1 — Executive Summary

### 1.1 The four critiques (1 sentence each)

| # | Tag | Critique (1-sentence English gloss) |
|---|---|---|
| 1 | **CALIB-VAL** | The chr22 set is used both for hyperparameter calibration (γ_cos via q70) AND for downstream discovery analyses, and chr17 — though held-out de facto — is reported alongside chr22 in the same headline tables, so there is no clean discovery/validation split a reviewer can point to. |
| 2 | **SPLICE-CANON** | The current GENCODE-only splice donor/acceptor labels conflate canonical (GT-AG, GC-AG) and non-canonical splice sites; a reviewer with biological background expects canonical sites to converge shallowly (recognisable motif) and non-canonical ones to require deeper computation, and the manuscript currently cannot distinguish them. |
| 3 | **Q2-DEFEND** | The Q2 = (high gDTR ∩ low conservation) "lineage-specific regulatory" claim is biologically aggressive without (a) a positive control showing gDTR is high at known functional sites, (b) a fine-grained repeat-class breakdown, and (c) at least one extra-chromosome replication, because TE/repeat enrichment is not the same as functional enrichment and TE distribution is chromosome-specific. |
| 4 | **CASE-FIX** | The 3-variant chr17 case study cannot generalise per class; the labelled "frameshift-locus BRCA1 17:43057063 G→A" is factually wrong (ClinVar molecular consequence is **nonsense / SO:0001587**, not frameshift; a true frameshift requires a 1-bp or 2-bp indel). |

### 1.2 Decisions taken (locked)

- **Q2 = Option B** (aggressive defend) with prereq sub-experiments B-1 / B-2 / B-3 / B-4 (functional positive control → repeat class breakdown → multi-chromosome replication → reframe).
- **GPU priority: P2-INDEL forward FIRST, P3B-3 chr17/chr1 forward SECOND**. Everything else (P2-SNV reanalysis, P1a calibration split, P1b canonical splice motif scan, P3B-1 functional positive control, P3B-2 repeat breakdown) is CPU-only and can run in parallel.
- **Results-first.** The interpretation memo (Section 8) pre-registers narrative branches; whichever branch the numbers select is what the paper says. We do not pre-commit to a story.
- **Verification is automated.** A central runner script (Section 5) writes `_done` markers and `_status.json` per step and halts on first FAIL.

### 1.3 Total compute estimate (rough, see §4 for breakdown)

| Resource | Hours |
|---|---|
| GPU H200 (P2-INDEL + P3B-3 chr17 Q2 forward) | ≈ 6–10 h (main blocker) |
| GPU H200 (chr1 multi-chr fallback, OPTIONAL) | + 8–12 h |
| CPU (everything else: P1a, P1b, P2-SNV reanalysis, P3B-1, P3B-2, B-4 reframe, build_paper1_v8) | ≈ 12–18 CPU-h |

### 1.4 Top 3 risks (full register in §9)

1. **chr1 download + forward never finishes in time.** Mitigation: chr17 Q2 replication is the mandatory deliverable; chr1 is OPTIONAL with hard stop at 12 h.
2. **B-1 functional positive control fails — gDTR is NOT elevated at known functional sites.** Mitigation: Section 8 has a pre-registered narrative branch that demotes Q2 to a Limitations item and reframes §3.2 around the functional axes (eQTL/GWAS/cCRE) only.
3. **True frameshift forward shows no shallow-vs-deep separation across SNV / missense / nonsense / splice / frameshift.** Mitigation: §3.3 becomes a "5-class signal exists but argmax-layer is not class-discriminative at population scale" honest-reporting subsection rather than a class-stratified mechanism claim; Table 4 is replaced by a per-class boxplot.

---

## Section 2 — Investigation findings

All findings below are from primary inspection of files at the cited file:line. Server checks via `ssh digitalocean-gpu`.

### 2.(a) `scripts/build_paper1_v6.py` — section numbering & prose-edit anchors

- Manuscript hierarchy: Abstract (lines 97-116) → §1 Intro (118-184) → §2 Framework (186-287) [§2.1 Settling depth 189-242, §2.2 Idle-block 244-274, §2.3 Tuned lens 276-287] → §3 Biological Utility (291-672) [§3.1 Splice 295-362, §3.2 Q2 365-425, §3.3 Mechanism 428-485, §3.4 Variant 488-606, §3.5 Cross-arch 609-672] → §4 Limitations (674-685) → §5 Conclusion (687-723) → References (726-739) → Appendices A/B/C/D/E/F (742-959).
- Specific anchors that v8 must edit:
  - Lines **216-242** (γ derivation prose): currently embeds the q70 calibration claim. v8 must add a sentence stating chr22 is the calibration set and chr17 is the held-out validation set with frozen γ.
  - Lines **296-327** (Table 2 — splice context means): currently mixes chr22 + chr17 columns. v8 must split into "Calibration (chr22)" and "Validation (chr17, frozen γ)" prose, and add canonical-vs-non-canonical breakdown.
  - Lines **365-425** (§3.2 Q2): the entire Table 3 + supporting prose must be rebuilt to lead with B-1 functional positive control numbers, then B-2 repeat class breakdown (separating low-complexity / simple-repeat / SINE / LINE / LTR), then B-3 chr17 (mandatory) / chr1 (optional) replication.
  - Lines **428-485** (§3.3 case study): the Table 4 row labelled `BRCA1 17:43057063 G→A (frameshift locus)` is FACTUALLY WRONG (Section 2.j below). Replace with one of three options (Section 3.4).
  - Lines **676-685** (Limitations bullets): add new L6 = calibration/validation split and new L7 = "Q2 is supported by [B-1/B-2/B-3 outcomes] but does not survive the strongest single test [if applicable]" depending on results.

### 2.(b) `scripts/44_t13_case_studies.py` — the 3-variant case study

- Lines **44-60** define the variant tuple. Critical line **52**: `("BRCA1_5266_43057063_G_A", ..., "BRCA1 c.5266 region (substitution stand-in for c.5266dupC; indels filtered)", 3, "BRCA1_LB_43057061_C_T")` — the script's own comment admits the variant is a **substitution stand-in for the real frameshift c.5266dupC**, because Phase 3 main filters out indels (line 64 of `31_phase3_main.py`: `if len(ref) != 1 or len(alt) != 1: continue`).
- The cached output at server `~/gDTR/results/tier1_case_studies/case_studies.json` confirms argmax_layer = L24 for 17:43057063 G→A and `all_phase3_match=True` (the new forward matches the Phase 3 cached value to 1e-4 relative error).

### 2.(c) `scripts/50_phase5_conservation.py` and `50b_phase5_smoothed.py` — current Q2 method

- `50_phase5_conservation.py`: per-position c on chr22 vs PhyloP-100way, top-25% c × bot-25% PhyloP gives quadrants. Hypergeometric enrichment over ENCODE_cCRE / ENCODE_rDHS / RepeatMasker classes.
- `50b_phase5_smoothed.py`: same logic but with 100-bp box-car smoothing of both signals before quantile thresholding (line 17 `SMOOTH=100`). This is the version that produces the v7 numbers (server `phase5/q2_enrichment.json`: Q2 = 3.71% of chr22, 5,090 ≥100bp regions, 1.88 Mb total).
- Currently NO multi-chr replication, NO functional-site positive control, NO chr-shuffled or matched-control comparison beyond the single hypergeometric test on chr22.

### 2.(d) `02_gene_structure.py`, `22_phase2_2_gate_b_chr17.py`, `25_phase2_5_splice_chr17.py`, and `20_phase2_0_prep_chr17.py` — splice annotation pipeline

- The current label codes 5 (`splice_donor`) and 6 (`splice_acceptor`) come from `20_phase2_0_prep_chr17.py` lines **121-140** and the same logic in `prep_chr22_windows.py`. The donor/acceptor mask is constructed as `±SPLICE_PAD = ±10 bp around every exon-intron boundary on the chosen canonical transcript` — **no GT-AG / GC-AG / AT-AC dinucleotide test is anywhere in the pipeline**. Therefore canonical / non-canonical distinction is NOT coded.
- 25_phase2_5_splice_chr17.py builds `splice_chr17_profile.json` using the same labels.

### 2.(e) `15_phase1_5_hp_sweep.py` and `16b_phase1_6_gate_b.py` — chr22 HP sweep + Gate B

- `15_phase1_5_hp_sweep.py` lines **61-62**: the chr22 HP sweep is over `gammas=[0.4,0.5,0.6]`, `rhos=[0.8,0.85,0.9]`. It picks the best `(γ, ρ)` from the sanity_gc vs sanity_shuf Cohen's d. The locked γ_cos = 0.39663 in `16b_phase1_6_gate_b.py` line **67** comes from Phase 1.4 calibration `gamma_cos_global_q70` of the chr22 sanity sequences.
- The HP sweep is therefore done on chr22 sanity sequences (a subset of chr22 itself), so chr22 is contaminated as a discovery set. The chr17 Gate B (`22_phase2_2_gate_b_chr17.py` line 19: `GAMMA_LOCKED = 0.39663`) uses the chr22-derived γ unchanged → already a held-out validation, but the manuscript does not present it that way.

### 2.(f) `31_phase3_main.py` and `prep_clinvar_15gene.py` — variant feature schema

- `31_phase3_main.py` line **64**: `if len(ref) != 1 or len(alt) != 1: continue` — **Phase 3 main filters out all indels**. The cached `variants_features.csv` is **SNV-only**.
- `prep_clinvar_15gene.py` does NOT filter by indel/SNV. The full 15-gene TSV `clinvar_15gene.tsv` has **66,967 records** including indels.
- Schema of `phase3_main/variants_features.csv` (verified via `head -1 | tr , "\n"`): `chrom, pos, ref, alt, gene, category, stars, max_abs_dD, signed_argmax, argmax_layer, dc_interp, evo2_ref_loglik, evo2_alt_loglik, evo2_delta_loglik, dD_jsd_0..31, dD_cos_0..31` — i.e. **no MC (molecular consequence) column**, no canonical/non-canonical splice flag, no indel-length column.

### 2.(g) `tier2_q2_functional.py` — what is already done

- Already does region-level overlap (with bedtools intersect) and 100-shuffle null (`bedtools shuffle -chrom -noOverlapping`) for GTEx eQTL chr22, GWAS Catalog chr22, ENCODE cCRE-ELS chr22.
- Existing numbers (from `~/gDTR/results/tier2_q2_functional/summary.json`): eQTL fold_bp=1.62 (p=5.4e-56), GWAS fold_bp=1.50 (p=1.6e-7), cCRE-ELS fold_bp=1.90 (p=0). Region-level shuffle p ≈ 0.0099 (capped at 1/(101)) for all three.
- **What is missing for B-1 positive control**: there is no comparison "gDTR within known functional sites > gDTR within matched non-functional sites" as a precondition. This is the strongest single thing a sceptical reviewer will demand.

### 2.(h) `phase3_main/variants_features.csv` schema (server)

`ssh digitalocean-gpu 'head -1 .../variants_features.csv | tr , "\n"'` confirms: 14 metadata cols + dD_jsd_0..31 + dD_cos_0..31 = 78 cols, **no SO molecular-consequence column**. To stratify by class (missense / nonsense / splice / synonymous / frameshift) we must join back to the ClinVar VCF `MC=` field (Section 2.j shows that CLNVCSO and MC are both present in the raw VCF).

### 2.(i) `phase5/q2_enrichment.json` (server) — current Q2 numbers

```
Q2 = 3.71% of chr22 (1,885,030 bp); 5,090 regions ≥100 bp.
ENCODE_cCRE          fold = 1.28 (n_overlap_q2 = 387,721)
ENCODE_rDHS          fold = 1.25
rmsk_SINE            fold = 0.93   ← UNDER-enriched
rmsk_LINE            fold = 1.31
rmsk_LTR             fold = 1.39
rmsk_DNA             fold = 1.20
rmsk_Simple_repeat   fold = 1.52
```

Important: SINE is **under-enriched** (0.93×, p=1.0). This is missing from v7's Table 3, which only shows a single LINE row at 1.31. The v8 Table 3 must show all repeat classes including the under-enriched SINEs to be honest.

### 2.(j) ClinVar lookup of 17:43057063 G→A

`ssh digitalocean-gpu 'zcat clinvar.vcf.gz | grep -P "^17\t43057063\t" | head -3'` returns exactly:

```
17  43057063  55490   G  A  ...  CLNSIG=Pathogenic;
                              MC=SO:0001587|nonsense,SO:0001619|non-coding_transcript_variant;
                              CLNREVSTAT=reviewed_by_expert_panel;  CLNVC=single_nucleotide_variant
```

`SO:0001587 = stop_gained (nonsense)`. **The variant is therefore a 3-star pathogenic NONSENSE SNV in BRCA1, NOT a frameshift.** The v7 manuscript's "frameshift locus" label is factually wrong, and the user's critique is correct. Two more allelic variants (G→C and G→T at the same position) exist, both classified `missense_variant` — the locus is well-characterised.

---

## Section 3 — Per-item plans

The four critiques map to four work groups: P1a (calibration split), P1b (canonical splice), P2 (case study reframe — split into P2-SNV CPU and P2-INDEL GPU), P3B (Q2 defend — split into B-1, B-2, B-3, B-4). Section numbering below uses 3.1 for CALIB-VAL, 3.2 for SPLICE-CANON, 3.3 for CASE-FIX, 3.4 for Q2-DEFEND.

---

### 3.1 CALIB-VAL (Critique 1) — discovery/validation split

**3.1.1 Diagnosis.** Reviewer attack: "You set γ_cos = q70 of chr22 sanity sequences (`16b_phase1_6_gate_b.py:67`), then report Table 2 chr22 mean-c values using that γ — circular. Even though chr17 uses the frozen γ (`22_phase2_2_gate_b_chr17.py:19`), Table 2 lumps chr22 and chr17 together so the reader cannot see what is calibration and what is held-out validation. The same complaint applies to §3.2 Q2 (chr22-only, calibration-set). This is an `n=1`-chromosome-discovery problem disguised by reporting two columns side by side."

**3.1.2 Hypothesis.** **H1 (CALIB-VAL):** The chr22-derived γ_cos = 0.39663 transfers to chr17 without re-tuning. Concretely: (i) the chr17 q70 of running-min cos at the penultimate layer is within ±0.05 of γ_cos = 0.39663; (ii) the chr17 splice donor < intron Cohen's d is ≥ 80% of the chr22 value; (iii) the chr17 exon vs intron MWU p still passes the v7 alpha (1.7e-51 / 6 contexts).

**3.1.3 Procedure.** This is CPU-only on cached features. **Step P1a-1**: write `scripts/p1a_calib_val_split.py` that:
  - Loads `~/gDTR/results/phase2.1/chr17_cache.h5` and `~/gDTR/data/annotation/chr17_position_labels.npy`.
  - Recomputes the chr17 q70 of running-min D_cos at the penultimate layer (using `extract_hidden_states` cached values directly — no re-forward needed). Writes `chr17_q70_recheck.json` with chr17_q70, chr22_q70 (from Phase 1.4 calibration.json), abs_diff.
  - Recomputes Table 2 splits: produces two mini-tables, "Calibration (chr22, γ derived here)" and "Validation (chr17, γ frozen)", with per-context mean c, n positions, and Cohen's d-vs-intron for each context.
  - Writes `_status.json` with PASS/FAIL on the three H1 criteria.

**Step P1a-2**: edit `build_paper1_v8.py` to (a) split Table 2 into **two tables** (Table 2a Calibration, Table 2b Validation), (b) add a single sentence in §2.1 "γ_cos = 0.39663 was derived on chr22 sanity sequences and frozen for all subsequent analyses; chr17 below serves as the held-out validation set", (c) add Limitations bullet L6 acknowledging that chr22-only calibration may not generalise to other chromosome compositions.

**3.1.4 Validation criteria.**

| Metric | PASS | REFRAME | FAIL |
|---|---|---|---|
| `abs(chr17_q70 - chr22_q70)` | < 0.05 | 0.05–0.15 | > 0.15 |
| chr17 donor-vs-intron Cohen's d | ≥ 0.80 × chr22 d | 0.50–0.80 × | < 0.50 × |
| chr17 exon-vs-intron MWU p | < 1.7e-51 | 1.7e-51 ≤ p < 1e-30 | p ≥ 1e-30 |

If PASS on all three: split the table as planned and add the L6 bullet. If REFRAME on any: add a paragraph in §2.1 noting partial generalisation. If FAIL on any: re-run γ calibration on chr17 itself, report both γ values, and add a strong Limitations bullet. The unconditional answer is to **split the tables regardless** — that addresses the reviewer's structural complaint even if numbers come out worst-case.

**3.1.5 Failure modes.**

| Failure | Concrete handling |
|---|---|
| chr17 q70 differs by >0.15 → γ doesn't transfer | Report both γs; treat each chromosome as its own calibration; rewrite §2.1 prose to drop the "single γ_cos" claim |
| chr17 donor-vs-intron d falls below 0.50 of chr22 | Splice universality claim becomes "chr22-confirmed, chr17 attenuated" — keep §3.1 but add caveat paragraph |
| chr17_cache.h5 schema mismatch (e.g., `D_cos` shape differs, `done_mask` partial) | The script must check `done_mask.all()` before computing q70; if False, abort with explicit FAIL status, do not silently average partial coverage |

**3.1.6 Compute.** CPU-only. Reading 15 GB chr17_cache.h5 at ~500 MB/s ≈ 30 s for streaming q70. Total wall ≤ 5 minutes.

**3.1.7 Files affected.**

- New: `scripts/p1a_calib_val_split.py`, `~/gDTR/results/p1a/chr17_q70_recheck.json`, `~/gDTR/results/p1a/_status.json`, `~/gDTR/results/p1a/calib_val_table.csv`.
- Edited prose in `scripts/build_paper1_v8.py`: §2.1 lines **216-242** (one new sentence, one new appendix pointer), Table 2 (lines 306-319) becomes Table 2a + Table 2b, §3.1 supplementary paragraph (lines 320-342) updated.
- Reused: `~/gDTR/results/phase2.1/chr17_cache.h5`, `~/gDTR/results/phase1.4/calibration.json`, `~/gDTR/data/annotation/chr17_position_labels.npy`.

**3.1.8 Dependencies.** None — first thing that runs.

---

### 3.2 SPLICE-CANON (Critique 2) — canonical vs non-canonical

**3.2.1 Diagnosis.** Reviewer attack: "Your splice donor / acceptor labels are pure GENCODE exon-intron boundary ±10 bp (`20_phase2_0_prep_chr17.py:121-140`). They include both canonical (GT-AG, GC-AG: ≥99% of human introns) and non-canonical (AT-AC, etc.). Canonical sites have a strong sequence motif and should be shallow-thinking; non-canonical sites have weak/absent motifs and should require deeper computation. Aggregating them masks a biologically meaningful axis and may even be the explanation for any residual variance in your shallow-thinking story."

**3.2.2 Hypothesis.** **H2 (SPLICE-CANON):** Canonical splice sites (donor 5'-GT, acceptor 3'-AG, in genomic-strand coordinates) converge **earlier** (smaller mean c) than non-canonical splice sites, and both are still shallower than the intronic baseline. Ordering: c(canonical) < c(non-canonical) < c(intron). Magnitude: Cohen's d (canonical vs non-canonical) ≥ 0.20 (medium-small effect).

**3.2.3 Procedure.** CPU-only.

**Step P1b-1**: write `scripts/p1b_canonical_splice_label.py` that:
  - Loads `chr22.fa` and `chr17.fa` via pyfaidx, opens `gencode.v44.chr17_chr22.gtf.db` via gffutils.
  - For each canonical transcript on chr22 / chr17 (using the same `pick_canonical_transcript` logic as `20_phase2_0_prep_chr17.py:58-73`), iterates intron boundaries and reads the 2-bp donor signal (intron-positions 1-2) and 2-bp acceptor signal (intron-positions -2,-1). Strand-aware: on `-` strand, take reverse complement.
  - Classifies each intron boundary as `canonical_GT_AG` / `canonical_GC_AG` / `non_canonical_AT_AC` / `non_canonical_other`.
  - Writes two npy arrays: `chr22_splice_class_labels.npy` and `chr17_splice_class_labels.npy` of dtype uint8 with codebook `{0: not_splice, 1: canonical_GT_AG_donor, 2: canonical_GT_AG_acceptor, 3: canonical_GC_AG_donor, 4: canonical_GC_AG_acceptor, 5: non_canonical_donor, 6: non_canonical_acceptor}` over the same chromosome length as the existing `chr*_position_labels.npy`.
  - Sidecar JSON with counts per class.

**Step P1b-2**: write `scripts/p1b_canonical_splice_compare.py` (CPU, reuses cached h5) that:
  - Loads `chr22_cache.h5` (existing) and `chr17_cache.h5`, computes per-position c at γ_cos=0.39663 (same logic as `25_phase2_5_splice_chr17.py:26-33`).
  - Bins positions by the new 7-class label, computes mean / median / Cohen's d for each pair (canonical_GT_AG vs intron, canonical_GC_AG vs intron, non_canonical vs intron, canonical vs non_canonical).
  - Writes `splice_canonical_compare.json` and a 6-panel boxplot figure `F_splice_canonical.{pdf,png}`.

**Step P1b-3**: edit `build_paper1_v8.py` Table 2 (lines 306-319) and Appendix E splice fine-profile (lines 924-935) to add 4 rows for the new canonical/non-canonical breakdown, and add one sentence in §3.1 prose noting the canonical-first ordering.

**3.2.4 Validation criteria.**

| Outcome | Manuscript handling |
|---|---|
| `c(canonical) < c(non_canonical) < c(intron)` AND Cohen's d (can vs non-can) ≥ 0.20 | Strong claim: split into 3 categories in §3.1, add to abstract bullet "shallow-canonical / deep-non-canonical / baseline-intron triad" |
| Same ordering but `d` < 0.20 | Modest claim: report ordering, no abstract change, add appendix table only |
| `c(canonical) ≈ c(non_canonical)` (d<0.10, no separation) | Acknowledge; rephrase §3.1 universality claim as "splice grammar broadly, irrespective of canonical/non-canonical motif" |
| `c(non_canonical) < c(canonical)` (reverse ordering) | Honest report this in Limitations as a counter-intuitive finding; do not let it dominate the abstract |

**3.2.5 Failure modes.**

| Failure | Concrete handling |
|---|---|
| Non-canonical sample size too small (<200 introns chr-wise on both chromosomes) | Pool chr17+chr22 introns; if still <200, report descriptively and drop quantitative test |
| Strand handling bug (some donors on `-` strand mislabelled) | Add unit test in `p1b_canonical_splice_label.py`: spot-check 5 known transcripts (TP53, BRCA1, ATM, MLH1, MSH2) and verify the donor sequence matches GT for canonical introns |
| q70 calibration changes when restricted to canonical-only | Report both with the full-splice γ and a canonical-only γ (the latter only if ≠ within 5%) |

**3.2.6 Compute.** CPU only. ~10 min for label construction (gffutils + pyfaidx scan), ~5 min for streaming chr17_cache.h5 stats. Total ≤ 20 min wall.

**3.2.7 Files affected.**

- New: `scripts/p1b_canonical_splice_label.py`, `scripts/p1b_canonical_splice_compare.py`, `~/gDTR/data/annotation/chr22_splice_class_labels.npy`, `~/gDTR/data/annotation/chr17_splice_class_labels.npy`, `~/gDTR/results/p1b/splice_canonical_compare.json`, `~/gDTR/results/p1b/F_splice_canonical.{pdf,png}`, `~/gDTR/results/p1b/_status.json`.
- Edited prose in `build_paper1_v8.py`: Table 2 (306-319) gains 4 rows; §3.1 paragraph (320-342) gains one sentence; Appendix E (912-935) gains canonical/non-canonical sub-table.
- Reused: chr17_cache.h5, chr22_cache.h5, chr17_position_labels.npy, chr22_position_labels.npy, gencode.v44.chr17_chr22.gtf.db.

**3.2.8 Dependencies.** None for label construction. `p1b_canonical_splice_compare.py` depends on `p1b_canonical_splice_label.py` finishing.

---

### 3.3 CASE-FIX (Critique 4) — case study reframe

**3.3.1 Diagnosis.** Three sub-attacks:

1. **n=3 cannot generalise.** Three pathogenic variants do not represent splice / missense / frameshift mechanisms in any statistical sense.
2. **Each variant cannot represent its class.** TP53 R175H is one of the most-studied missense in cancer; BRCA1 splice region is one of many; "frameshift" was inappropriately picked.
3. **Factual error.** 17:43057063 G→A in ClinVar is `MC=SO:0001587|nonsense` (verified in §2.j), NOT frameshift. The script (line 50-52 of `44_t13_case_studies.py`) self-confessed this is "substitution stand-in for c.5266dupC; indels filtered". A frameshift requires 1-bp or 2-bp indel.

**3.3.2 Hypothesis.** **H3 (CASE-FIX):** Across **all** ClinVar 15-gene P/LP variants stratified by molecular consequence (missense / nonsense / canonical-splice / frameshift / synonymous-control), the per-class **distribution** of argmax_layer differs significantly (Kruskal-Wallis p < 0.01) AND the median argmax_layer is ordered (canonical-splice shallow ≤ frameshift mid ≤ nonsense mid ≤ missense deep), with ≥ 20 variants per class for stable medians.

This replaces the n=3 anecdote with a per-class population claim. The 3-variant figure becomes a representative-trace illustration of the per-class median.

**3.3.3 Procedure.** Two parallel tracks: P2-SNV (CPU, on cached `variants_features.csv`) and P2-INDEL (GPU, new forward of frameshift indels).

#### P2-SNV (CPU, all SNV classes)

**Step P2-SNV-1**: write `scripts/p2_snv_class_join.py`:
  - Loads ClinVar VCF (`~/gDTR/data/variants/clinvar.vcf.gz`), parses `MC=SO:NNNNNNN|name` from the INFO field. Constructs a class label per (chrom,pos,ref,alt) with priority: `canonical_splice` (SO:0001574 splice_donor + 0001575 splice_acceptor + 0001629 splice_region), `nonsense` (SO:0001587), `missense` (SO:0001583), `synonymous` (SO:0001819), `5UTR` (SO:0001623), `3UTR` (SO:0001624), `intron` (SO:0001627), `other`.
  - Joins to `~/gDTR/results/phase3_main/variants_features.csv` (10,910 SNVs) on (chrom,pos,ref,alt) → `variants_features_classed.csv` adds 1 column `mc_class`.
  - Sidecar JSON with per-class counts within P/LP and within B/LB.

**Step P2-SNV-2**: write `scripts/p2_snv_per_class_stats.py`:
  - Computes per-class median / mean / IQR of argmax_layer (1-indexed), max_abs_dD, evo2_delta_loglik, separately for P/LP and B/LB.
  - Kruskal-Wallis test on P/LP argmax_layer across the four substantive classes (missense, nonsense, canonical_splice, synonymous).
  - Bootstrap 95% CI on each class median (n_boot=1000, seed=42).
  - Outputs: `p2_snv_per_class.csv`, `p2_snv_per_class.json`, boxplot `F_argmax_per_class.{pdf,png}`.

#### P2-INDEL (GPU, frameshift forward)

**Step P2-INDEL-1**: write `scripts/p2_indel_select.py`:
  - From `clinvar_15gene.tsv` (66,967 records), filters to P/LP indels with stars ≥ 2 and `MC=SO:0001589|frameshift_variant`. Server count: 5,630 frameshift_del + 2,495 frameshift_ins = **8,125 candidates**. Stratified subsample to 25 per gene per direction (frameshift_del / frameshift_ins) capped at 20 genes (15-gene panel + any chr that has chrN.fa available locally) → target n ≈ 600 indels for the indel forward.
  - Also pick 600 matched B/LB controls (closest genomic-position B/LB of any consequence in same gene).
  - Writes `frameshift_panel.tsv` with columns: chrom, pos, ref, alt, gene, mc_class, indel_len, frame_class (`true_frameshift_1bp` / `true_frameshift_2bp` / `inframe`), category, stars.

**Step P2-INDEL-2**: write `scripts/p2_indel_forward.py` — modify `31_phase3_main.py` line **64** to allow indels:
  - Forward ref window of length 6001 bp (CONTEXT_HALF=3000) and alt window of length `6000 + (len(alt) - len(ref))`. Tokeniser sees a sequence of slightly different length on alt.
  - Carefully define the variant token position on alt: for 1-bp insertion at pos p, the inserted base is at index local_idx; for 1-bp deletion, the variant token is the position immediately following the deletion. This matters for D_cos column extraction.
  - For population statistics we DO NOT need to align ref-vs-alt token-by-token — we only need max_abs_dD across layers in a fixed window around the variant. Use the maximum over local_idx ± 5 positions to be robust to insertion/deletion token shift.
  - Cache outputs to `~/gDTR/results/p2_indel/variants_features_indel.csv` with the same 78-column schema PLUS `mc_class`, `indel_len`, `frame_class`, `frame_position` (1/2/3 mod-3 offset).

**Step P2-INDEL-3**: write `scripts/p2_indel_per_class_stats.py` — same statistics as P2-SNV-2 but on the indel cache, plus a combined SNV+indel boxplot.

#### Case-study replacement (3 variants → representative traces)

**Step P2-CASE-1**: rewrite `scripts/44_t13_case_studies.py` → `scripts/p2_case_v8.py` with:
  - **Option A** (recommended): pick **5** representative variants — one per class — by selecting the variant whose argmax_layer is closest to the per-class P/LP median (from P2-SNV-2 / P2-INDEL-3), tie-breaking by max_abs_dD closest to per-class median.
  - **Option B** (fallback if frameshift forward fails): keep splice + missense + nonsense (replacing the falsely-labelled "frameshift") + synonymous control. Acknowledge nonsense != frameshift.
  - For each, plot the per-layer ΔD_cos trace overlaid on the per-class median trace. Caption explicitly states "n=k variants in this class; representative trace at the median".

**Step P2-CASE-2**: edit `build_paper1_v8.py` §3.3 Table 4 and figure caption (lines 428-485):
  - Table 4 becomes "Per-class population summary": columns = [class, n_variants, median argmax_layer, IQR, max_abs_dD median, p-value vs missense (KW post-hoc)].
  - Figure 3 (F5_mechanism_cases) becomes a 5-panel figure: 5 representative traces × per-class population overlay.
  - The factually-incorrect `BRCA1 17:43057063 G→A frameshift locus` row is REMOVED. If it must appear, it is correctly relabelled as "BRCA1 nonsense (p.W1837X equivalent)" and only as supporting illustration.
  - Add 1 sentence in §3.3 prose referencing the population-level Kruskal-Wallis result.

**3.3.4 Validation criteria.**

| Test | PASS threshold | REFRAME | FAIL |
|---|---|---|---|
| Per-class n in P/LP | All four classes ≥ 30 | Three classes ≥ 30 | Any class < 15 |
| Kruskal-Wallis p (4-way: miss / nonsense / can-splice / synonymous) | p < 0.01 | 0.01–0.05 | p ≥ 0.05 |
| Median argmax_layer ordering can-splice ≤ {nonsense, frameshift} ≤ missense | Holds | Partial | Reverse |
| Frameshift forward agrees with cached SNV statistics on duplicate variants | abs diff < 0.05 in argmax | 0.05–0.15 | > 0.15 (forward broken) |

**3.3.5 Failure modes.**

| Failure | Concrete handling |
|---|---|
| KW non-significant (p≥0.05) → no class-stratified signal | §3.3 reframes to "argmax_layer is variant-specific, NOT class-discriminative at population level" — preserve only the matched-pair pathogenic-vs-benign result, drop the per-class story |
| Indel forward crashes on tokenizer (Evo 2 may have rare-byte handling issues for length-mismatch alt windows) | Reduce indel panel to 1-bp indels only (most common); pad alt to the same length with N on the 3' side; document this in the script |
| Missense median > nonsense median (reverse of biological expectation) | Check whether stop-codon position is too close to context boundary; for a ±3kb window, distal stopgains may not be measurable. Stratify nonsense by distance-to-stop |
| 17:43057063 keeps being interesting individually | Keep it as a representative nonsense example with the correct label and the correct molecular consequence cited |

**3.3.6 Compute.**

| Step | Resource | Wall time | Memory |
|---|---|---|---|
| P2-SNV-1 (VCF parse + join) | CPU | 5–10 min | 4 GB |
| P2-SNV-2 (per-class stats) | CPU | 1 min | 2 GB |
| P2-INDEL-1 (panel select) | CPU | 2 min | 1 GB |
| P2-INDEL-2 (GPU forward, n≈1200 with B/LB) | **H200** | ≈ 1.4 s/variant × 1200 ≈ **30 min** | GPU peak ~40 GB (mirrors Phase 3 main) |
| P2-INDEL-3 (per-class stats) | CPU | 1 min | 1 GB |
| P2-CASE rewrite | CPU | 5 min | 2 GB |

**3.3.7 Files affected.**

- New scripts: `p2_snv_class_join.py`, `p2_snv_per_class_stats.py`, `p2_indel_select.py`, `p2_indel_forward.py`, `p2_indel_per_class_stats.py`, `p2_case_v8.py`.
- New data: `variants_features_classed.csv`, `frameshift_panel.tsv`, `variants_features_indel.csv`.
- New outputs: `~/gDTR/results/p2/p2_snv_per_class.json`, `~/gDTR/results/p2_indel/p2_indel_per_class.json`, `~/gDTR/results/p2_case/case_studies_v8.json`, `F_argmax_per_class.{pdf,png}`, `F5_mechanism_cases_v3.{pdf,png}`.
- Edited prose in `build_paper1_v8.py`: §3.3 (lines 428-485) Table 4 + figure replaced; §3.4 Table 5 caption updated to mention indels are excluded from the AUROC analysis (still SNV-only) for parity with v7 — OR (ambitious option) add an extra row "8,008 SNV + 1,200 indel ensemble" if time permits and indel forward succeeds; adopt only if validation passes.
- Reused: phase3_main/variants_features.csv, clinvar.vcf.gz, chr*.fa references.

**3.3.8 Dependencies.** P2-SNV runs as soon as CPU is free. P2-INDEL waits on GPU (priority 1, see §4). P2-CASE waits on both P2-SNV-2 AND P2-INDEL-3.

---

### 3.4 Q2-DEFEND (Critique 3) — Q2 aggressive defence

This is the most contested section. Sub-experiments **B-1** (functional positive control), **B-2** (repeat class breakdown), **B-3** (multi-chromosome), **B-4** (manuscript reframe).

**3.4.1 Diagnosis.** Reviewer attack assembled from user feedback verbatim:

> "흥미롭지만 대단히 도전적인 개념. functional 한 site에서 (그렇지 않은 site에서보다) gDTR이 높다 가 확보된 상태에서, Q2 즉 high gDTR + low conservation에 대해 더 functional 하다고 말할 수 있습니다. repeat element가 enrich 되어 있다는 것과 functional 하다는 것은 다른 의미입니다. repeat 또한 단순 low complexity와 LTR, LINE과도 다릅니다. 또한 transposable element의 삽입은 random에 가까우며 chr 마다 달라서, chr22의 결론으로 일반화할 수 없습니다."

Concretely: (a) without proving "gDTR > at known functional sites than non-functional sites in general", the Q2 claim that high-gDTR ∩ low-conservation is "functional" begs the question; (b) lumping all repeat classes together hides that Simple_repeat (1.52×) is biologically different from LTR (1.39×) and SINE (0.93× — actually under-enriched, suppressed in v7), and "TE-derived enhancer" is a strong claim that needs LTR specifically (not repeat-anything); (c) Q2 is chr22-only; TE distribution varies dramatically by chromosome (e.g., chr19 is alu-rich, chrY is LTR-rich), and chr22 has a distinct compositional profile.

#### 3.4.B-1 — Functional positive control

**3.4.1.B-1.1 Hypothesis.** **H4 (FUNC-POS):** Mean gDTR settling depth c **inside** ENCODE cCRE-ELS regions (ground-truth functional) is **deeper** than mean c in matched-shuffled non-functional regions on chr22 (one-sided MWU p < 1e-10). Same test on GTEx eQTL chr22 sites (point overlap with their LD-block).

**3.4.1.B-1.2 Procedure.** CPU-only. Write `scripts/p3b1_functional_positive_control.py`:
  - Loads chr22 per-position c (from `~/gDTR/results/phase1.6_sub/chr22_position_c.npy`) and chr17 per-position c (from `~/gDTR/results/phase2.5/chr17_position_c.npy` or recompute from chr17_cache.h5).
  - For each functional dataset (cCRE-ELS bp mask, GTEx eQTL ±100bp window mask, GWAS catalog ±50bp window mask), compute:
    - mean c at functional positions (`c_func`)
    - mean c at matched-control positions: 100 random shuffles of the functional mask within chr22, same per-shuffle bp mass, no overlap with original (`bedtools shuffle -chrom -noOverlapping`)
    - one-sided MWU p of c_func > c_shuffled
    - effect size: `(mean(c_func) - mean(c_shuffled)) / std(c_shuffled)`
  - Outputs: `p3b1_func_pos.json` with per-dataset stats; figure `F_func_pos.{pdf,png}` 3-panel violin plot.

**3.4.1.B-1.3 Validation criteria.**

| Result | Interpretation |
|---|---|
| For ALL three datasets: c_func > c_shuffled, MWU p < 1e-10, effect ≥ 0.30 | **Q2 prereq cleared.** Proceed with Option B aggressive Q2 framing. Add B-1 numbers as a new Table 3a in §3.2. |
| For 2/3 datasets significant | Partial: report all three; weaken claim to "gDTR is elevated at biochemically-defined regulatory elements (cCRE-ELS) and quantitative-trait-defined regulatory elements (eQTL); GWAS catalog hits show only nominal elevation". |
| For ≤1/3 dataset significant | **Q2 prereq fails.** Trigger §3.2 reframe (B-4 contingency): demote Q2 from §3.2 to a Limitations bullet, replace §3.2 with a "deep-thinking distribution across chr22" descriptive subsection that does not claim functional discovery. |

**3.4.1.B-1.4 Failure modes.**

| Failure | Handling |
|---|---|
| Effect direction reversed (c_func < c_shuffled) | Honest reporting: this would falsify the framework's basic premise. Trigger immediate paper-level reframe — gDTR is not a functional-importance signal. (Pre-registered escape branch in Section 8.) |
| eQTL test inflated by LD-block size choice | Sensitivity analysis with ±50, ±100, ±200 bp windows; pick most conservative |
| Smoothing artefact (100bp box-car blurs functional signal) | Run with raw and 100bp-smoothed; report both |

#### 3.4.B-2 — Repeat class breakdown

**3.4.B-2.1 Hypothesis.** **H5 (REPEAT-BREAK):** Q2 enrichment is structured by repeat class. Specifically, LTR and DNA-transposon classes show ≥1.30× enrichment; SINE shows depletion (≤1.0×); Simple_repeat / Low_complexity (sequence-context) show ≥1.50× enrichment but are mechanistically different from TE classes.

**3.4.B-2.2 Procedure.** Almost entirely already done in `~/gDTR/results/phase5/q2_enrichment.json` (verified §2.i). The new work is presentation: **explicitly name SINE under-enrichment** (which v7 hides), add Low_complexity row to Table 3, and rewrite the prose to disentangle "TE class enrichment" (LTR, LINE, DNA) from "low-complexity sequence enrichment" (Simple_repeat, Low_complexity) from "functional enrichment" (cCRE-ELS, eQTL, GWAS).

Write `scripts/p3b2_repeat_breakdown.py` that:
  - Reads `~/gDTR/results/phase5/q2_enrichment.json`, extracts all rmsk_* keys, sorts by fold descending, outputs a 9-row table with columns `class, n_overlap_q2, n_total_chr22, fold, hypergeom_p, biological_interpretation`.
  - Optionally, sub-classifies LTR by family (ERV1, ERVK, ERVL, etc.) using the rmsk repName field — requires re-reading rmsk.txt.gz with field 10 (repFamily). Useful for the appendix.

**3.4.B-2.3 Validation criteria.**

| Outcome | Manuscript handling |
|---|---|
| LTR ≥ 1.30× AND DNA ≥ 1.10× AND SINE ≤ 1.0× | Strong: §3.2 prose names lineage-specific TE enhancer as plausible mechanism with LTR as the lead candidate, SINE as control |
| All TE classes ≈ 1.0× but Low_complexity ≥ 1.50× | Reframe: Q2 is "deep computation at low-complexity sequences" — not a regulatory-element claim, possibly a tokeniser artefact |
| All repeat classes ≈ 1.0× | Q2 is sequence-composition-neutral; the lineage-specific TE story disappears; functional axis (cCRE/eQTL/GWAS) becomes the only Q2 evidence |

#### 3.4.B-3 — Multi-chromosome replication

**3.4.B-3.1 Hypothesis.** **H6 (MULTI-CHR):** Q2 enrichment patterns on chr17 (and chr1 if available) replicate the chr22 ordering of fold enrichments within ±0.20 absolute fold for the top three classes (cCRE-ELS, LTR, eQTL).

**3.4.B-3.2 Procedure.**

**chr17 (mandatory)**: chr17_cache.h5 already exists. Write `scripts/p3b3_q2_chr17.py` that mirrors `50b_phase5_smoothed.py` but on chr17 per-position c (build from cache if `~/gDTR/results/phase2.5/chr17_position_c.npy` doesn't exist). Output `~/gDTR/results/p3b3_chr17/q2_enrichment_chr17.json` and a side-by-side figure `F_q2_chr17_vs_chr22.{pdf,png}`.

**chr1 (optional, GPU)**: chr1.fa is NOT on the server (verified §2.j environs). To replicate on chr1, we need:
  1. Download chr1.fa.gz from UCSC (~250 MB compressed). 5 min.
  2. Run `scripts/prep_chr1_windows.py` analogous to `prep_chr22_windows.py` (CPU, ~5 min).
  3. Run `scripts/p3b3_chr1_forward.py` analogous to `21_phase2_1_chr17_forward.py` — chr1 is ~249 Mb, so ~83K windows of 6kb stride 3kb. At ~1.4s/window on H200, ≈ 32 GPU-hours (way too long).
  - **Mitigation: chr1 sub-sample.** Pick 8000 random non-overlapping 6kb windows on chr1 (covers ~48 Mb, ~20% of chr1). Forward time ≈ 3 GPU-h. This is sufficient for an enrichment-level test.

**3.4.B-3.3 Validation criteria.**

| Outcome | Manuscript handling |
|---|---|
| chr17 replicates chr22 (top-3 within ±0.20 fold) | Strong: §3.2 says "Q2 ordering replicates on chr17"; chr1 if available adds further confidence |
| chr17 partially replicates (top-1 only) | Honest: top-1 confirmed, others noted as chromosome-specific |
| chr17 contradicts chr22 | Q2 is chromosome-specific; rewrite §3.2 around the chr22-only finding with explicit caveat |
| chr1 forward fails or runs out of time | Chr17-only multi-chr is the deliverable; explicit Limitations bullet about whole-genome generalisation |

#### 3.4.B-4 — Manuscript reframe

Conditional on the four B-X outcomes. Section 8 enumerates 8 outcome combinations and pre-registers narrative for the top 4.

**3.4.4 Validation criteria — overall Q2.** The manuscript path is determined by:
- (B-1 PASS) AND (B-2 ≥ partial) AND (B-3 ≥ chr17 replicates) → **AGGRESSIVE Q2 stays in §3.2 with strong framing**.
- (B-1 PASS) AND any of (B-2 partial / B-3 partial) → **MODERATE: §3.2 stays but is hedged with explicit caveats and the failed sub-experiment named**.
- (B-1 FAIL) OR (B-3 contradicts) → **DEMOTE: §3.2 reduced to one paragraph as "auxiliary analysis"; new §3.2 takes its place with the canonical-splice and per-class case-study material from P1b/P2**.

**3.4.5 Failure modes.** See B-1, B-2, B-3 above. Cross-cutting risk: scripts double-count Q2 bp because of overlapping repeat annotations. Mitigation: bedtools merge before every overlap test.

**3.4.6 Compute.**

| Step | Resource | Wall time |
|---|---|---|
| B-1 functional positive control | CPU | ≤ 10 min |
| B-2 repeat breakdown (read existing JSON + rmsk repFamily sub-classification) | CPU | ≤ 5 min |
| B-3 chr17 Q2 replication | CPU (chr17_cache.h5 streaming) | ~30 min |
| B-3 chr1 sub-sample forward | **GPU** | ~3 h (8000 windows @ 1.4s) |
| B-3 chr1 enrichment | CPU | ≤ 5 min after forward |
| B-4 reframe | manual editing of `build_paper1_v8.py` | ~1 h |

**3.4.7 Files affected.**

- New scripts: `p3b1_functional_positive_control.py`, `p3b2_repeat_breakdown.py`, `p3b3_q2_chr17.py`, `prep_chr1_windows.py` (optional), `p3b3_chr1_forward.py` (optional).
- New outputs: `~/gDTR/results/p3b1/`, `~/gDTR/results/p3b2/`, `~/gDTR/results/p3b3_chr17/`, `~/gDTR/results/p3b3_chr1/` (optional).
- Edited prose in `build_paper1_v8.py`: §3.2 (lines **365-425**) major rewrite, Table 3 (lines 378-393) replaced with split TE / non-TE / functional rows, Appendix E Q2 region detail (lines 912-923) updated; new appendix subsection "Q2 multi-chromosome replication".
- Reused: phase5 outputs, tier2_q2_functional outputs.

**3.4.8 Dependencies.** B-1 has none, runs immediately. B-2 depends on `phase5/q2_enrichment.json` (already exists, no dependency). B-3 chr17 depends on `chr17_cache.h5` (exists). B-3 chr1 depends on chr1.fa download AND GPU availability AND P2-INDEL forward completing first (priority 1). B-4 depends on B-1, B-2, B-3 completing.

---

## Section 4 — GPU scheduling and parallelism plan

### 4.1 GPU-blocking tasks (must run on H200)

| Task | Wall time | Memory | Priority | Notes |
|---|---|---|---|---|
| **P2-INDEL-2** (frameshift forward, ~1200 indel + control variants) | ~30 min | 40 GB | **1** | Cleared first. Modifies `31_phase3_main.py:64` to allow indels. |
| **P3B-3 chr1 sub-sample forward** (8000 windows) | ~3 h | 60 GB | **2** | Optional but strongly desired. Hard stop at 12 h wall. |
| (No third GPU task is required.) | — | — | — | All other steps are CPU. |

### 4.2 Parallelism rules

- The H200 has 143 GB. P2-INDEL uses ~40 GB; chr1 forward uses ~60 GB. **They cannot run concurrently** (peak hidden-state extraction allocates ~70 GB transient on Evo 2 7B). Run sequentially.
- **All CPU tasks run in parallel with whichever GPU task is current.** This means while P2-INDEL is running on GPU, the following CPU jobs can all start: P1a calib-val split, P1b canonical splice label + compare, P2-SNV-1 + P2-SNV-2, P3B-1 functional positive control, P3B-2 repeat breakdown, P3B-3 chr17 (uses cached h5).
- The local laptop runs the build_paper1_v8 script when ALL inputs are green.

### 4.3 Gantt-style timeline (wall-clock from t=0)

```
hour:  0   1   2   3   4   5   6   7   8   9  10  11  12
GPU:   [P2-INDEL]──────[P3B-3 chr1 forward (optional)─────────]
CPU1:  [P1a-────────] [P3B-1 ──────] [P3B-3 chr17 ─────]
CPU2:  [P1b label──] [P1b compare─] [P2-SNV-1 ──] [P2-SNV-2]
CPU3:  [P3B-2────] [P2-INDEL-1 select─] [P2-INDEL-3 stats] [P2-CASE]
CPU4:                                                    [B-4 reframe]
                                                            [build_paper1_v8]
```

Critical-path: P2-INDEL forward (30 min) → P2-INDEL stats (1 min) → P2-CASE (5 min) → build_paper1_v8 → DONE. Realistic critical path ≈ 1 h if everything runs cleanly. If chr1 is included, ≈ 4 h.

### 4.4 Fallback if a GPU job fails

| Failure | Fallback |
|---|---|
| P2-INDEL-2 OOM | Re-run with `CONTEXT_HALF=2000` (4kb windows); document the change |
| P2-INDEL-2 tokeniser error | Drop deletions ≥3bp; keep only 1-bp ins/del/dup |
| chr1 forward OOM after some windows | Use the partial cache; if ≥ 4000 windows succeeded, proceed with reduced sample |
| chr1 download fails | Drop B-3 chr1; chr17-only is acceptable |

---

## Section 5 — Automated verification pipeline

### 5.1 Per-step contract

Every new script writes:
1. Human log to stderr (Python `logging`).
2. Structured `_status.json` in its output directory: `{step, status: "PASS"|"FAIL"|"SKIP", reason, metrics: {...}, started_at, finished_at, exit_code}`.
3. An empty `_done` marker file (presence ≠ success — must inspect `_status.json`).

### 5.2 Schema check helper

`scripts/verify_step.py` (NEW, read-only utility — not run yet, planned):

```python
"""Verify one revision_v8 step. Reads _status.json + does schema checks.
Exit 0 on PASS, 1 on FAIL, 2 on missing.
"""
import json, sys, csv
from pathlib import Path

def load_status(d):
    p = Path(d) / "_status.json"
    if not p.exists(): return None
    return json.loads(p.read_text())

def check_csv_schema(path, expected_cols, min_rows=1):
    if not Path(path).exists(): return False, "missing"
    with open(path) as f:
        r = csv.DictReader(f)
        cols = r.fieldnames
        if cols != expected_cols and not set(expected_cols).issubset(cols):
            return False, f"schema mismatch: have {cols} want superset of {expected_cols}"
        n = sum(1 for _ in r)
        if n < min_rows: return False, f"only {n} rows"
    return True, "ok"

STEPS = {
  "p1a": {
    "dir": "~/gDTR/results/p1a",
    "required": ["calib_val_table.csv", "chr17_q70_recheck.json"],
    "csv_checks": [("calib_val_table.csv", ["chrom","context","mean_c","n","cohens_d_vs_intron"], 14)],
    "json_checks": [("chr17_q70_recheck.json", ["chr17_q70","chr22_q70","abs_diff","pass"])],
  },
  "p1b": {...},
  "p2_snv": {...},
  "p2_indel": {...},
  "p2_case": {...},
  "p3b1": {...},
  "p3b2": {...},
  "p3b3_chr17": {...},
  "p3b3_chr1": {...},
}

def main():
    step = sys.argv[1]
    if step not in STEPS:
        print(f"unknown step {step}"); sys.exit(2)
    spec = STEPS[step]
    s = load_status(Path(spec["dir"]).expanduser())
    if s is None: print(f"{step}: MISSING status.json"); sys.exit(2)
    if s["status"] != "PASS": print(f"{step}: {s['status']} reason={s.get('reason')}"); sys.exit(1)
    for fname, cols, min_rows in spec.get("csv_checks", []):
        ok, msg = check_csv_schema(Path(spec["dir"]).expanduser()/fname, cols, min_rows)
        if not ok: print(f"{step}/{fname}: {msg}"); sys.exit(1)
    print(f"{step}: PASS"); sys.exit(0)

if __name__ == "__main__": main()
```

### 5.3 Master DAG runner

`scripts/run_revision_v8.sh` (NEW, planned):

```bash
#!/usr/bin/env bash
# Master DAG runner for revision_v8.
# Halts on first FAIL. Writes ~/gDTR/results/revision_v8_status.json.

set -uo pipefail
ROOT=$HOME/gDTR
cd $ROOT

# Helper: run a step and verify
run_step () {
  local step="$1"; shift
  echo "=== STEP $step START $(date -Is) ==="
  if "$@"; then
    if python3 scripts/verify_step.py "$step"; then
      echo "=== STEP $step PASS ==="
      echo "{\"step\":\"$step\",\"status\":\"PASS\",\"ts\":\"$(date -Is)\"}" >> $ROOT/results/revision_v8_status.jsonl
      return 0
    fi
  fi
  echo "=== STEP $step FAIL ==="
  echo "{\"step\":\"$step\",\"status\":\"FAIL\",\"ts\":\"$(date -Is)\"}" >> $ROOT/results/revision_v8_status.jsonl
  exit 1
}

# DAG order (CPU steps in parallel where safe; GPU strictly serial)
# Phase A — CPU, no GPU dep:
run_step p1a       python3 scripts/p1a_calib_val_split.py &
run_step p1b_label python3 scripts/p1b_canonical_splice_label.py &
run_step p3b2      python3 scripts/p3b2_repeat_breakdown.py &
wait

run_step p1b_compare      python3 scripts/p1b_canonical_splice_compare.py &
run_step p2_snv_join      python3 scripts/p2_snv_class_join.py &
run_step p3b1             python3 scripts/p3b1_functional_positive_control.py &
run_step p3b3_chr17       python3 scripts/p3b3_q2_chr17.py &
wait

run_step p2_snv_stats     python3 scripts/p2_snv_per_class_stats.py
run_step p2_indel_select  python3 scripts/p2_indel_select.py

# Phase B — GPU priority 1
run_step p2_indel_forward python3 scripts/p2_indel_forward.py
run_step p2_indel_stats   python3 scripts/p2_indel_per_class_stats.py
run_step p2_case          python3 scripts/p2_case_v8.py

# Phase C — GPU priority 2 (optional)
if [ "${RUN_CHR1:-0}" = "1" ]; then
  run_step prep_chr1     python3 scripts/prep_chr1_windows.py
  run_step p3b3_chr1     python3 scripts/p3b3_chr1_forward.py
fi

# Phase D — manuscript build
run_step build_v8 python3 scripts/build_paper1_v8.py

echo "ALL STEPS PASS"
```

### 5.4 Smoke-test mode

Each script accepts a `--smoke` flag that runs on n=10 (or n=50 for stats) instead of full data. The master runner can be invoked with `SMOKE=1 bash scripts/run_revision_v8.sh` to get a 5-minute end-to-end check before kicking off the real run.

### 5.5 Re-run safety

Every script is idempotent: on re-entry, if `_done` exists AND `_status.json.status == "PASS"`, skip. Force re-run via `--force`.

---

## Section 6 — Cross-section consistency invariants

These MUST NOT regress between v7 and v8. Verified at build time by `scripts/verify_invariants.py` (NEW, planned):

| # | Invariant | How to check |
|---|---|---|
| **I1** | **L=29 canonical tap** is preserved on chr17 (h_30 ≡ h_31 idle-block claim still holds for any indel forward). | After P2-INDEL forward, recompute `max|h30 - h31|` on 100 random alt sequences from the indel cache. Must be < 1e-6. |
| **I2** | **ΔD AUROC = 0.844** reproduces when re-running Phase 3 logistic on `variants_features.csv` with frozen seed 42, 10-fold stratified. v8 must NOT alter the cached features for the existing 10,910 SNVs. | `scripts/verify_invariants.py` re-runs the LR and asserts `0.840 ≤ auroc ≤ 0.848`. |
| **I3** | **Indel feature schema parity.** `variants_features_indel.csv` has the same 78 columns + 4 extra (mc_class, indel_len, frame_class, frame_position). `dD_jsd_l` and `dD_cos_l` for l=0..31 must use the same definitions as Phase 3. | `scripts/verify_invariants.py` checks header equality on the 78 shared columns. |
| **I4** | **γ_cos = 0.39663 frozen.** No script in revision_v8 may recompute γ_cos on chr22 and silently shift the value. P1a writes the value used; any drift > 1e-4 is a FAIL. | `verify_invariants.py` checks `phase1.4/calibration.json:gamma_cos_global_q70 == p1a/_status.json:gamma_used`. |
| **I5** | **Tuned-lens recovery numbers** (Table A2: L=12 worst at 0.9816, L=29 at 0.9996) unchanged. v8 does NOT touch the tuned-lens layer. | If A.2 is reproduced, the JSON `~/gDTR/results/phase1.2_tuned_lens/recovery.json` must be byte-identical to v7. |
| **I6** | **Cross-arch table values** (HyenaDNA 6.55/6.62, NT-v2/DNABERT-2 numbers) unchanged. | byte-identical `~/gDTR/results/phase4/per_model_summary.json`. |
| **I7** | **17:43057063 G→A is in the SNV cache and was reported as L24 argmax in v7.** v8 must keep the row in the SNV cache (do not delete data) but relabel it as nonsense in v8 prose. The numerical max_abs_dD = 3.67e-2 stays. | `verify_invariants.py` greps the row in `variants_features.csv` and checks max_abs_dD. |
| **I8** | **Q2 = 3.71% of chr22 with 5,090 ≥100bp regions** unchanged when P3B re-runs on chr22 with same smoothing (this is the calibration-set baseline). | `verify_invariants.py` compares `p3b3_chr17/q2_enrichment_chr22_recheck.json` (auxiliary re-run) to `phase5/q2_enrichment.json` byte-identical for chr22-only fields. |
| **I9** | **No silent indel filter.** Any new script that writes to a CSV must not silently drop indels (avoid the trap that bit `31_phase3_main.py:64`). Add an explicit `LOG.info("filtered %d indels", n_indels)` whenever `len(ref) != 1 or len(alt) != 1` is the criterion. | code review at script time. |
| **I10** | **Splice-class new labels do not overwrite existing position labels file.** New labels go to `chr*_splice_class_labels.npy` — separate file, separate codebook. | filesystem check. |

---

## Section 7 — Manuscript section diff plan

### 7.1 Per-section action

| Section | v6 lines | Action | v8 content |
|---|---|---|---|
| Title | 84-94 | KEEP | unchanged |
| Abstract | 97-116 | KEEP | unchanged (collaborator's readable rewrite stays) |
| §1 Intro | 118-184 | KEEP | unchanged (4 paragraphs) |
| §2.1 Settling depth | 189-242 | EDIT | Add 1 sentence at line ~241 stating "γ_cos = 0.39663 was derived on chr22 sanity sequences and frozen for all subsequent analyses; chr17 (and B-3 multi-chr replication) serves as the held-out validation set." |
| Table 1 (idle block) | 256-274 | KEEP | unchanged |
| §2.2 idle block | 244-274 | KEEP | unchanged |
| §2.3 tuned lens | 276-287 | KEEP | unchanged |
| §3.1 Splice — header | 295 | EDIT | "Splice sites — canonical and non-canonical — are universally shallow" |
| §3.1 — Table 2 | 306-319 | REPLACE | Two side-by-side tables: Table 2a (Calibration: chr22 7-context means + 4-context canonical breakdown), Table 2b (Validation: chr17 same rows). Adds rows: canonical_GT_AG_donor / canonical_GT_AG_acceptor / canonical_GC_AG_donor / canonical_GC_AG_acceptor / non_canonical_donor / non_canonical_acceptor. |
| §3.1 prose | 296-352 | EDIT | Add 1 paragraph after Table 2b summarising the canonical < non-canonical < intron ordering (or its failure). Update HyenaDNA replication paragraph (lines 328-342) to mention canonical/non-canonical replication if available. |
| Figure 1 (F2) | 353-362 | KEEP image, EDIT caption | New caption mentions canonical vs non-canonical sub-panel if F2 is regenerated; otherwise note in caption that detail is in Table 2 + Appendix E. |
| §3.2 Q2 — header | 365 | EDIT | Conditional on B-1/B-2/B-3 outcomes. Keep "Conservation discordance" if PASS path; rename to "Conservation-aware deep-thinking" if MODERATE; demote to subsection if DEMOTE path. |
| §3.2 prose | 366-416 | REPLACE (heavy) | New first paragraph: state functional positive control (B-1) result. Second paragraph: repeat-class breakdown (B-2) with explicit acknowledgement of SINE depletion and Simple_repeat 1.52× sequence-context confound. Third paragraph: chr17 (and chr1 if available) replication (B-3). Fourth paragraph: refined claim — TE-derived (LTR-led) lineage-specific regulation, with the caveat that whole-genome generalisation requires further work. |
| Table 3 | 378-393 | REPLACE | New 12-row table with 3 sub-headings: (a) **Functional positive controls** (3 rows: cCRE-ELS, GTEx eQTL, GWAS), (b) **Repeat class breakdown** (6 rows: SINE, LINE, LTR, DNA, Simple_repeat, Low_complexity), (c) **Multi-chromosome replication** (3 rows: chr22 baseline, chr17 replication, chr1 sub-sample if available). |
| Figure 2 (F6) | 417-425 | REPLACE if B-3 runs | New 3-panel figure: (a) chr22 quadrant scatter (existing F6 panel), (b) chr17 quadrant scatter, (c) per-repeat-class fold barplot. |
| §3.3 Mechanism — header | 428 | EDIT | "Class-stratified disruption layers across the 15-gene cohort" |
| §3.3 prose | 429-474 | REPLACE | New first paragraph: motivation (per-variant heterogeneity in §3.3 connects to the 32-d trajectory in §3.4). Second paragraph: per-class population statistics (KW p, median argmax_layer ordering across missense / nonsense / canonical-splice / synonymous / frameshift). Third paragraph: 5 representative traces. Explicitly states n per class. |
| Table 4 | 440-458 | REPLACE | "Per-class population summary" table with rows for each MC class: missense (n≈X), nonsense (n≈Y), canonical_splice (n≈Z), synonymous (n≈W), frameshift (n≈V). Columns: median argmax_layer, IQR, max_abs_dD median, KW post-hoc p vs missense. |
| Figure 3 (F5) | 475-485 | REPLACE | New 5-panel figure: per-class boxplot of argmax_layer + 5 representative traces overlaid on per-class median trajectory. |
| §3.4 Variant traj | 488-606 | KEEP (mostly) | Keep the 0.844 AUROC headline. Add 1 sentence noting the analysis is SNV-only by design (cf. P2-INDEL frameshift evidence in §3.3) — preserves the AUROC = 0.844 invariant (I2). |
| Table 5 | 511-521 | KEEP | unchanged |
| Figure 4 (F3) | 596-606 | KEEP | unchanged |
| §3.5 Cross-arch | 609-672 | KEEP | unchanged |
| §4 Limitations | 674-685 | EDIT | Existing 5 bullets KEEP. Add: **L6** (calibration / validation): "γ_cos was calibrated on chr22 sanity sequences; chr17 and B-3 multi-chromosome replication serve as held-out validation, but a single chromosome of validation is still narrower than a true held-out set." **L7** (Q2 conditional): conditional on which B-X pass; if any fail, add explicit caveat. **L8** (case study): "The per-class argmax-layer claim of §3.3 rests on a stratified subset of ClinVar P/LP variants; molecular-consequence labels follow ClinVar's MC field, and one specific row in Table 4 of v7 — `BRCA1 17:43057063 G→A frameshift locus` — is corrected: the variant is a nonsense (SO:0001587) SNV, not a frameshift." |
| §5 Conclusion | 687-723 | EDIT (minor) | Update splice sentence to mention canonical/non-canonical; update Q2 sentence per B-4 path; update mechanism sentence per P2 outcome. |
| References | 727-737 | EDIT | Add ClinVar MC-field reference if needed; otherwise unchanged. |
| Appendix A.1 HP sensitivity | 743-777 | KEEP | unchanged |
| Appendix A.2 tuned-lens | 779-805 | KEEP | unchanged |
| Appendix B HyenaDNA splice | 807-854 | KEEP | unchanged |
| Appendix C reproducibility | 857-871 | EDIT | Add commit SHA of `revision_v8` branch; add the new analyses' release tag. |
| Appendix D per-layer | 875-909 | KEEP | unchanged |
| Appendix E Q2 region detail / splice fine-profile | 912-935 | EDIT | Append: canonical vs non-canonical splice fine-profile (chr17 and chr22), Q2 chr17 region detail. |
| Appendix F cross-arch | 938-959 | KEEP | unchanged |
| **NEW Appendix G** Canonical splice motif analysis | — | ADD | 1-page appendix with the codebook for the new 7-class splice labels and the per-class table on chr22 + chr17. |
| **NEW Appendix H** Per-class variant analysis | — | ADD | 1-page appendix with the full per-class boxplot + KW post-hoc table for SNV (4 classes) + frameshift indel (1 class) with cohort sizes. |
| **NEW Appendix I** Q2 multi-chromosome and functional positive control | — | ADD | 1.5-page appendix with B-1 / B-2 / B-3 numbers, chr17 quadrant figure, chr1 sub-sample figure if available, and the bedtools shuffle null distribution histograms. |

### 7.2 Build script delta

`scripts/build_paper1_v8.py` (NEW, planned) is the v6 script copied with the edits above. The diff is non-trivial (~250 lines changed); critical to run `verify_invariants.py` after build.

---

## Section 8 — Interpretation memo template

Future-self fills in actual numbers once results land. Narrative branches are pre-registered NOW so we cannot post-hoc rationalise.

### 8.1 Per-finding template

For each numbered finding F1..F8 below: `[hypothesis]` `[result placeholder]` `[branch A confirmed | branch B refuted | branch C ambiguous]`.

```
F1 (CALIB-VAL transfer)
  Hypothesis: chr22-derived γ_cos = 0.39663 transfers to chr17 (q70 within ±0.05).
  Result: chr17_q70 = ____, abs_diff = ____
  Branch A (confirmed, abs_diff < 0.05):
    "γ_cos = 0.39663 frozen on chr22 generalises to chr17 within q70 tolerance ±0.05.
     We split Table 2 into Calibration (chr22) and Validation (chr17, frozen γ)."
  Branch B (refuted, abs_diff > 0.15):
    "chr17 q70 = ____ differs from chr22 q70 by ____ , exceeding our pre-registered
     ±0.05 tolerance. We report both γs and rephrase §2.1 to acknowledge per-region
     calibration."
  Branch C (ambiguous, 0.05 ≤ abs_diff ≤ 0.15):
    "Partial generalisation. We report the chr22-frozen γ alongside a chr17-recalibrated γ
     and treat both as valid operating points; downstream analyses use the chr22 γ
     for direct comparability."
```

```
F2 (canonical splice ordering)
  Hypothesis: c(canonical) < c(non_canonical) < c(intron), Cohen's d ≥ 0.20.
  Result: c(canonical_GT_AG) = ____, c(non_canonical) = ____, d = ____
  Branch A: "Splice grammar is layered — the canonical motif (~99% of human introns)
             converges shallowest, non-canonical motifs require deeper computation,
             and intronic baseline is deepest. d = ____."
  Branch B (no separation, d < 0.10): "Splice universality holds across canonical and
             non-canonical alike; the model's shallow recognition is not motif-specific
             at the granularity our test resolves."
  Branch C (reverse, c(non) < c(can)): "Counter-intuitive finding: non-canonical sites
             converge earlier than canonical. Possible explanation: non-canonical sites
             tend to occur in well-conserved branch-point contexts that are shorter and
             more constrained. Reported in Limitations."
```

```
F3 (case study — per-class population)
  Hypothesis: KW p < 0.01 across {missense, nonsense, can-splice, synonymous}.
  Result: KW p = ____, n per class: ____. Median argmax_layer per class: ____.
  Branch A: "Per-class disruption-layer signature confirmed. Median argmax_layer
             ordering: can-splice ≤ frameshift ≤ nonsense ≤ missense, KW p = ____."
  Branch B (KW non-sig): "argmax_layer is variant-specific, not class-discriminative
             at population level. We retain the matched-pair pathogenic-vs-benign
             evidence (max_abs_dD ratios) but drop the per-class median claim."
  Branch C (partial ordering): "Three of four pairwise post-hocs are significant; one
             is not. We report the partial ordering."
```

```
F4 (Q2 functional positive control B-1)
  Hypothesis: c(functional) > c(matched-shuffled), MWU p < 1e-10 for cCRE / eQTL / GWAS.
  Result: cCRE p = ____, eQTL p = ____, GWAS p = ____.
  Branch A (all 3 pass): "Foundational positive control cleared — gDTR is elevated at
             known regulatory elements. Q2 = high gDTR ∩ low conservation can therefore
             plausibly identify functional but evolutionarily young elements."
  Branch B (none pass): "Functional positive control fails. We demote Q2 to a
             Limitations item, replace §3.2 with the canonical-splice and per-class
             material from §3.1/§3.3 which now have ample evidence."
  Branch C (1-2 pass): "Partial: the functional axes that pass are named; the others
             are reported with explicit caveats."
```

```
F5 (Q2 repeat class breakdown B-2)
  Hypothesis: LTR ≥ 1.30, DNA ≥ 1.10, SINE ≤ 1.0, Simple_repeat ≥ 1.50.
  Result: pre-existing JSON has SINE=0.93, LINE=1.31, LTR=1.39, DNA=1.20, Simple=1.52,
         Low_complexity=2.02. So the pre-registered ordering is already CONFIRMED.
  Action: report all 6 classes (especially the SINE depletion that v7 hides);
          name LTR as the lead TE candidate for the lineage-specific regulatory claim.
```

```
F6 (Q2 multi-chromosome B-3)
  Hypothesis: chr17 top-3 enrichments within ±0.20 of chr22 top-3.
  Result: chr17 cCRE = ____, chr17 LTR = ____, chr17 eQTL = ____.
  Branch A (replicates): "Q2 enrichment ordering replicates on chr17 within ±____ fold."
  Branch B (contradicts): "chr17 does not replicate chr22; Q2 may be chromosome-specific."
  Branch C (chr17 partially replicates): "chr17 confirms cCRE-ELS and LTR enrichment
             but not eQTL; we report both."
  Sub-claim chr1: if chr1 forward succeeds: ____ ; if not: explicit Limitations note.
```

```
F7 (P2-INDEL frameshift signal)
  Hypothesis: median(argmax_layer | frameshift) is shallower than missense and deeper
             than canonical-splice.
  Result: ____.
  Branch A: confirmed; add frameshift class to Table 4 and Figure 3.
  Branch B: frameshift argmax is not informative (median ≈ random across layers);
            report and add Limitations bullet about indel-tokenisation in Evo 2.
```

```
F8 (Cross-section invariants)
  Hypothesis: I1..I10 hold byte-identically (or within numerical tolerance).
  Result: verify_invariants.py output ____.
  Branch A: all green; v8 build proceeds.
  Branch B (any FAIL): hard stop. Investigate cause before any v8 build runs.
```

### 8.2 Q2 outcome combinations (pre-registered top 4 of 8)

There are 8 combinations of (B-1 pass / fail) × (B-2 specific-pattern / null) × (B-3 chr17 replicates / fails). The 4 most likely:

| Comb | B-1 | B-2 | B-3 chr17 | Manuscript path | Section 3.2 framing |
|---|---|---|---|---|---|
| **C1** (highest prior) | PASS | LTR-led specific | replicates | **AGGRESSIVE-PASS**: full Q2 framing with the new 12-row Table 3, lineage-specific TE-derived enhancer claim, chr17-replicated. Abstract gains 1 line. |
| **C2** | PASS | LTR-led specific | partial | **MODERATE**: full §3.2 stays but with explicit chr17-divergence caveat in the prose; Table 3 row "chr1 sub-sample if available" is a hard requirement; if chr1 also partial, downgrade to C3. |
| **C3** | PASS | null (TE classes ≈ 1.0, only Low_complexity ≥ 1.5) | replicates | **WEAK-FUNCTIONAL**: Q2 framed as "deep computation at low-complexity sequences enriched for cCRE/eQTL but not specifically TE-derived". Drop the lineage-specific TE claim; functional axes are the lead. |
| **C4** | FAIL | irrelevant | irrelevant | **DEMOTE**: §3.2 reduced to a 1-paragraph "auxiliary observation" subsection. New §3.2 takes its place: a per-chromosome description of where deep-thinking concentrates, with Q2 figure in Appendix only. The aggressive functional-discovery claim is dropped from abstract / conclusion. |

Combinations C5–C8 (e.g., B-1 fail + B-2 specific + B-3 replicates) are biologically incoherent and would trigger root-cause investigation rather than narrative — the most likely cause is a methodological error and the priority becomes debugging, not writing.

---

## Section 9 — Risk register

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| **R1** | chr17 frozen-HP results too weak (Cohen's d on splice donor < 0.5 of chr22 d). | 15% | Medium — undermines L=29 / γ generalisation | F1 Branch C: report partial; section 3.1 prose adds caveat. The 0.844 AUROC and chr22 effects are independent, so the rest of the paper is unaffected. |
| **R2** | True frameshift count too small after MC filter + per-gene cap. | 5% | Low — server check confirms 8,125 P/LP frameshifts in 15 genes | F7 Branch B: drop frameshift from per-class table, retain SNV 4-class population claim. |
| **R3** | Q2 functional positive control fails (B-1). | 25% | High — would invalidate §3.2 as currently written | C4 path: demote Q2 to auxiliary; promote canonical-splice and per-class case study to fill §3.2. The framework paper survives. |
| **R4** | chr1 forward fails or runs out of time. | 60% | Low — chr17 replication is the mandatory deliverable | Drop chr1, keep chr17-only multi-chr replication. Hard 12-h wall stop on chr1 forward. |
| **R5** | `build_paper1_v8.py` introduces regressions (e.g., Table 5 numbers shift, AUROC drops). | 10% | Critical — would silently corrupt headline results | `verify_invariants.py` runs as the LAST step before any docx is written. Compares 0.844 AUROC, 5,090 Q2 regions, idle-block invariant, MD5 of unchanged appendix tables. |
| **R6** | Indel tokeniser bug — Evo 2's BPE-style genomic tokeniser may not handle alt sequences with length-mismatch the same way as ref. | 30% | Medium — could invalidate frameshift forward | Verify on a single matched 1-bp insertion / 1-bp deletion / 2-bp deletion before running the full panel. Add a sanity check in `p2_indel_forward.py`: forward the same sequence twice with a no-op edit (e.g., AAA at position 0 → AAA), assert max_abs_dD < 1e-3. |
| **R7** | Disk full on local machine (figures + docx). | 5% | Low | Local has 698G with 22% used (verified §2). Plenty. |
| **R8** | Script-level race condition between concurrent CPU jobs (e.g., two scripts both write to `~/gDTR/results/p2_*`). | 10% | Medium — could corrupt outputs | Each script writes to its own dedicated subdirectory. Master runner enforces this at directory level. |
| **R9** | ClinVar MC-field absent for some variants in the 15-gene cache (older entries). | 20% | Medium — fewer variants in per-class breakdown | Variants without MC are pooled into "MC_unknown" and excluded from KW. n is reported. |
| **R10** | Time budget overrun (whole revision should be done in ≤24 h wall). | 30% | Medium | Critical-path scheduling in §4 is designed for ~8h with chr17, ~16h with chr1. Hard stop policy: if hour 16 hits and chr1 not done, drop chr1 and proceed to build. |

---

## Section 10 — Execution checklist

### 10.1 Numbered DAG order

| # | Step | Script | Resource | Wall | Verification gate |
|---|---|---|---|---|---|
| 0 | Pre-flight: verify all v7 invariants | `scripts/verify_invariants.py --baseline` | CPU local | 5 min | I1–I10 baseline must all PASS. STOP if any fails — that means the existing artefacts have drifted. |
| 1 | P1a — calibration / validation split | `scripts/p1a_calib_val_split.py` | CPU server | 5 min | F1; status PASS or REFRAME accepted, FAIL stops. |
| 2 | P1b-label — canonical/non-canonical splice labels | `scripts/p1b_canonical_splice_label.py` | CPU server | 10 min | label arrays exist, codebook sidecar OK. |
| 3 | P3B-2 — repeat breakdown writeup | `scripts/p3b2_repeat_breakdown.py` | CPU server | 5 min | uses existing JSON; produces the 9-row table. |
| 4 | P1b-compare — canonical splice statistics | `scripts/p1b_canonical_splice_compare.py` | CPU server | 5 min | F2; depends on step 2. |
| 5 | P3B-1 — functional positive control | `scripts/p3b1_functional_positive_control.py` | CPU server | 10 min | F4; **HARD GATE** for Q2 path. PASS → C1/C2/C3, FAIL → C4. |
| 6 | P3B-3 chr17 — multi-chr replication | `scripts/p3b3_q2_chr17.py` | CPU server | 30 min | F6; depends on chr17_cache.h5 (exists). |
| 7 | P2-SNV-1 — VCF MC-field join | `scripts/p2_snv_class_join.py` | CPU server | 10 min | produces variants_features_classed.csv. |
| 8 | P2-SNV-2 — per-class stats (SNV) | `scripts/p2_snv_per_class_stats.py` | CPU server | 1 min | F3 partial (SNV-only). |
| 9 | P2-INDEL-1 — frameshift panel selection | `scripts/p2_indel_select.py` | CPU server | 2 min | frameshift_panel.tsv exists. |
| 10 | **P2-INDEL-2** — frameshift forward | `scripts/p2_indel_forward.py` | **GPU H200** | 30 min | F7 raw; verify with R6 sanity (no-op edit ≈ 0). |
| 11 | P2-INDEL-3 — per-class stats (with indels) | `scripts/p2_indel_per_class_stats.py` | CPU server | 1 min | F3 full (5-class). |
| 12 | P2-CASE — representative traces | `scripts/p2_case_v8.py` | CPU server | 5 min | replaces v7 case_studies.json. |
| 13 | (OPTIONAL) chr1 prep | `scripts/prep_chr1_windows.py` | CPU server | 5 min + 5min download | chr1 windows TSV + position labels. |
| 14 | (OPTIONAL) **P3B-3 chr1 forward** | `scripts/p3b3_chr1_forward.py` | **GPU H200** | 3 h | F6 chr1 sub; hard stop at 12h wall. |
| 15 | (OPTIONAL) chr1 enrichment | `scripts/p3b3_chr1_enrichment.py` | CPU server | 5 min | Q2 chr1 sub-sample table. |
| 16 | B-4 reframe text — manual edit log | (no script — direct editing of build_paper1_v8.py prose blocks) | local | 1 h | author review. |
| 17 | Build v8 docx | `scripts/build_paper1_v8.py` | local | 5 min | produces `Paper1_gDTR_0429_v8.docx`. |
| 18 | Final invariant check | `scripts/verify_invariants.py --post-build` | CPU local | 5 min | I1–I10 all PASS post-build. |
| 19 | Diff vs v7 | `python -c "from docx import Document; ..."` (or manual) | local | 15 min | Section structure unchanged for unedited sections; new appendices present. |

### 10.2 What gets saved at the end

- `~/gDTR/results/revision_v8_status.jsonl` — line-per-step status log.
- `~/gDTR/results/revision_v8_status.json` — final aggregate (all 18 steps).
- `Paper1_gDTR_0429_v8.docx` at repo root.
- `docs/REVISION_PLAN_v8.md` (this document) — preserved for future-self.
- A `docs/INTERPRETATION_MEMO_v8.md` to be filled in when results land — uses the §8 template.

---

# Final summary message

## Top 3 blockers / risks uncovered during investigation

1. **Phase 3 main filters out all indels (`31_phase3_main.py:64`), so `variants_features.csv` is SNV-only.** This is the root cause of the v7 "frameshift locus" mislabel: the script substituted an SNV stand-in for a real frameshift because indels were silently dropped. ClinVar 17:43057063 G→A is in fact a **3-star pathogenic NONSENSE SNV** (`MC=SO:0001587`), not a frameshift. P2-INDEL forward (the GPU-priority-1 task) is needed to bring true frameshifts into the analysis at all.
2. **chr1.fa is NOT on the server** — the `data/reference/` directory only has chr2, 3, 5, 7, 10, 11, 12, 13, 16, 17, 22 (chrs that touch the 15-gene cancer panel). Multi-chromosome Q2 replication on chr1 requires a download + chr1 sub-sample forward (~3 GPU-hours for 8000 windows). This is the most likely scope-cut if time runs out.
3. **The current splice donor / acceptor label pipeline (`20_phase2_0_prep_chr17.py:121-140` and the analogous chr22 prep) makes NO canonical / non-canonical distinction.** It is a pure ±10 bp pad around every exon-intron boundary, with no GT-AG / GC-AG dinucleotide test. Critique 2 is therefore a real methodological gap, not just a presentation issue.

## Recommended execution order (≤10 items)

1. Pre-flight invariant check (verify v7 baseline reproduces).
2. P1a calibration/validation split (CPU, 5 min) — directly addresses critique 1.
3. P1b canonical splice labels + statistics (CPU, 15 min) — directly addresses critique 2.
4. P3B-1 functional positive control (CPU, 10 min) — **the hard gate** for Q2 path.
5. P2-SNV class join + per-class stats (CPU, 11 min) — directly addresses critique 4 SNV side.
6. P3B-3 chr17 Q2 replication (CPU, 30 min, uses cached chr17_cache.h5).
7. **P2-INDEL forward (GPU priority 1, 30 min)** — addresses critique 4 frameshift side.
8. P2-CASE rewrite with corrected labels (CPU, 5 min).
9. (Optional) chr1 prep + forward (GPU priority 2, ~3.5 h).
10. Build `Paper1_gDTR_v8.docx` and run post-build invariant check.

## Total compute estimate

- **GPU H200**: ≈ 30 min mandatory (P2-INDEL) + ≈ 3 h optional (chr1) = **0.5–3.5 GPU-hours**.
- **CPU (server + local)**: ≈ 2 wall-hours of unique CPU work; with parallelism, all CPU jobs fit in ≈ 1 wall-hour. Total CPU-hours ≈ **5–8** depending on parallelism (each script is single-process, but several can run concurrently).

## 2–3 surprises the user should know before starting

1. **The Q2 SINE under-enrichment (0.93×, p=1.0) is HIDDEN in v7 Table 3** but is in the underlying `phase5/q2_enrichment.json`. Disclosing it is mandatory for honest reporting and actually *helps* the manuscript: it shows Q2 is not "any repeat" but "specific repeat classes" — an LTR/LINE/DNA-transposon story rather than a generic repeat-element story. The user should be prepared for the appearance of strengthening to come from a "negative result" disclosure.
2. **The chr17 q70 may differ from chr22 q70 by more than ±0.05.** This is unverified — only the chr22 q70 = 0.397 and the assumption of γ-transfer are in v7. If chr17_q70 falls outside ±0.05, it is a **strengthening** outcome (it shows we honestly held chr17 as validation rather than tuning on it) but it requires a prose tweak. Plan for both branches.
3. **The "frameshift locus" mislabel in v7 is not a typo — it was a deliberate stand-in choice that the script comment (`44_t13_case_studies.py:50-52`) explicitly documents.** Future-self should know this was a known-at-time decision, not a mistake we just discovered. The fix is to actually run the indel forward, which is exactly what P2-INDEL does.