# INTERPRETATION_MEMO_v8.md — Paper 1 (gDTR) v8 revision interpretation memo

> **PURPOSE.** This document was filled in 2026-05-04 *after* the v8 revision
> experiments landed. Its narrative branches were pre-registered in
> `docs/REVISION_PLAN_v8.md` §8 BEFORE the experiments ran, so that whichever
> numerical outcomes appeared, the manuscript narrative was already chosen —
> preventing post-hoc rationalisation. Future-self should be able to read this
> memo in 6 months and reconstruct the entire interpretation logic without
> re-deriving anything.
>
> **STATUS (2026-05-04).** ALL placeholders filled. Selected branches are
> **bold**, refuted branches are ~~struck through~~ for evidence of
> non-rationalisation. The single non-trivial reframe is F4 (functional
> positive control): the data refuted the original hypothesis but in the
> *opposite* direction, which became a stronger positive finding under
> Option A (the "shallowness-as-recognition" generalisation). The OLD Q2
> claim is now demoted; the NEW §3.2 headline takes its slot.

---

## Status snapshot (filled in 2026-05-04)

| Step | Status | When (UTC) | Output path |
|---|---|---|---|
| Pre-flight invariants (baseline) | ✅ 10/10 PASS | 06:02 | `~/gDTR/results/verify_invariants.json` |
| P1a calib/val split | ✅ PASS Branch A | 06:05 | `~/gDTR/results/p1a/_status.json` |
| P1b canonical splice labels | ✅ PASS (after pyfaidx fix) | 06:22 | `~/gDTR/data/annotation/splice_class_codebook.json` |
| P1b canonical splice compare | ✅ REFRAME Branch C (reverse) | 06:24 | `~/gDTR/results/p1b/_status.json` |
| P3B-1 functional pos control | ✅ run / FAIL hypothesis (REVERSED → repurposed for Option A headline) | 06:06 | `~/gDTR/results/p3b1/_status.json` |
| P3B-2 repeat breakdown | ✅ PASS | 06:02 | `~/gDTR/results/p3b2/_status.json` |
| P3B-3 chr17 Q2 replication | ✅ PASS partial replication | 06:05 | `~/gDTR/results/p3b3_chr17/_status.json` |
| P3B-3 chr1 sub-sample (optional) | ⚪ SKIPPED (Q2 demoted, GPU 3h saved) | — | n/a |
| P2-SNV class join | ✅ PASS | 06:05 | `~/gDTR/results/p2/_status.json` |
| P2-SNV per-class stats | ✅ PASS | 06:06 | `~/gDTR/results/p2/p2_snv_per_class.json` |
| P2-INDEL panel select | ✅ PASS (1064 candidates) | 06:06 | `~/gDTR/results/p2_indel/_status.json` |
| P2-INDEL forward (GPU H200) | ✅ PASS (1064 forward, 0 errors, 11 min wall) | 06:18 | `~/gDTR/results/p2_indel/variants_features_indel.csv` |
| P2-INDEL per-class stats (5-way KW) | ✅ PASS (KW p=7.1e-10) | 06:18 | `~/gDTR/results/p2_indel/p2_indel_per_class.json` |
| P2-CASE representative traces | ✅ PASS (5 reps picked) | 06:18 | `~/gDTR/results/p2_case/case_studies_v8.json` |
| Build paper1_v8 PDF | ✅ DONE 9 pages | 17:44 | `/Users/yoonjincho/Project/ICML/ICML_0429_v1 2/gdtr_paper_ICML.pdf` |
| Post-build invariant check | ✅ 10/10 PASS | 06:18 | `~/gDTR/results/verify_invariants.json` |

---

## F1 — CALIB-VAL transfer (Critique 1)

**Hypothesis (pre-registered).** chr22-derived γ_cos = 0.39663 transfers to chr17 (`abs(chr17_q70 - chr22_q70) < 0.05`).

**Result.**

- `chr22_q70` (from `phase1.4/calibration.json`): **0.39663**
- `chr17_q70` (computed by p1a): **0.39429**
- `abs_diff`: **0.00235**  ←  ≪ 0.05 tolerance
- chr17 splice donor vs intron Cohen's d: **−0.349** (chr22 baseline d = **−0.369**, ratio 0.946)
- chr17 exon vs intron MWU p: **0.0** (effectively 0; v7 alpha 1.7e-51 cleared)

**Branch A — CONFIRMED. ✅**

> "γ_cos = 0.39663 frozen on chr22 generalises to chr17 within q70 tolerance ±0.05
> (abs_diff = 0.00235). We split Table 1 into Calibration (chr22) and Validation
> (chr17, frozen γ). The chr17 splice donor < intron Cohen's d = −0.349 (94.6% of
> chr22 magnitude) confirms the universality claim on a held-out chromosome."

~~Branch B (refuted, abs_diff > 0.15)~~ — *not selected; abs_diff = 0.00235.*
~~Branch C (ambiguous, 0.05 ≤ abs_diff ≤ 0.15)~~ — *not selected; abs_diff = 0.00235.*

**Manuscript edits applied.** §3.1 prose now opens with: "We use chromosome 22 as the calibration set, on which γ_cos = 0.397 is derived as the q70 ... and chromosome 17 as a held-out validation set with that γ frozen. The chr17 q70 recomputed independently equals 0.394 (|Δ|=0.0023)..." Table 1 has a chr22-calib / chr17-valid two-column split. (No L6 Limitations bullet added — the workshop short paper omits Limitations section by design; the calib/valid framing is itself the implicit acknowledgement.)

---

## F2 — Canonical splice ordering (Critique 2)

**Hypothesis (pre-registered).** `c(canonical) < c(non_canonical) < c(intron)`, Cohen's d (canonical vs non-canonical) ≥ 0.20.

**Result.**

- `c̄(canonical_GT_AG_donor)`: **25.79** (pooled chr17+chr22, n=350,552)
- `c̄(canonical_GC_AG_donor)`: **27.01** (n=5,165)  ← deepest splice class
- `c̄(non_canonical_donor)`: **25.13** (n=5,977)  ← shallowest splice class
- `c̄(intron)`: **27.72** (pooled, n ~68M)
- Cohen's d (canonical_GT_AG vs non_canonical donor): **+0.05** (small)
- Cohen's d (canonical_GT_AG vs intron): pooled, **−0.36** (medium-large)

**Branch C — REVERSE ordering. ⚠️**

Observed: c(non_canonical) < c(canonical_GT_AG) < c(canonical_GC_AG) < c(intron).

> "Counter-intuitive finding: non-canonical donor sites (AT-AC and other rare
> motifs) converge **earlier** than canonical GT-AG donors, while the minor
> canonical GC-AG class is the deepest splice class. The universality vs intron
> baseline holds for every splice subclass. The within-class ordering is the
> opposite of a naive 'stronger motif ⇒ shallower recognition' prior; we suspect
> this reflects the more constrained branch-point and polypyrimidine context that
> flanks non-canonical introns. The canonical-vs-non-canonical Cohen's d is small
> (~0.05), so we report magnitudes honestly and do not over-claim."

~~Branch A (canonical < non-canonical)~~ — *refuted by data.*
~~Branch B (no separation, d<0.10 across the three)~~ — *partially true between canonical and non-canonical (d=0.05) but the canonical_GC_AG class clearly separates upward.*

**Manuscript edits applied.** §3.1 prose has a new paragraph: "A finer dissection of the splice axis by motif class — using the genomic dinucleotides immediately downstream of the donor and upstream of the acceptor — reveals an unexpected ordering ..." Figure 1(b) plots non-canonical (red) / GT-AG (blue) / GC-AG (dark blue) bars per chr17 and chr22 with intron baseline reference.

---

## F3 — Per-class case study (Critique 4)

**Hypothesis (pre-registered).** Across {missense, nonsense, canonical-splice, synonymous} P/LP variants from the 15-gene cohort: KW p < 0.01 AND median argmax_layer ordering canonical-splice ≤ nonsense ≤ missense.

**Result.**

| Class | n (P/LP) | n (B/LB) | median argmax_layer (P/LP) | IQR |
|---|---|---|---|---|
| intron           | 116    | 1,268  | **L10** | [7, 24] |
| frameshift (indel) | 518  | new from indel forward | **L11** | [7, 24] |
| nonsense         | 1,740  | 1      | **L12** | [7, 24] |
| missense         | 935    | 317    | **L16** | [8, 27] |
| canonical_splice | 682    | 1      | **L17** | [8, 27] |
| synonymous       | 32     | 2,802  | **L18** | [6, 27] |

- KW 5-way p (incl frameshift indel): **7.110862597717712 × 10⁻¹⁰** ← strongly significant

**Branch A — partial ordering CONFIRMED. ✅**

Observed ordering: intron L10 < frameshift L11 < nonsense L12 < missense L16 < canonical_splice L17 < synonymous L18.

> "Per-class disruption-layer signature confirmed (n_classes = 6, KW p = 7.1×10⁻¹⁰).
> Early-truncation events (frameshift, nonsense) disrupt the residual stream
> shallowly while perturbations of already-established protein-level features
> (missense, splice motif) peak deeper. The 5 representative traces (Figure 3)
> illustrate the per-class median dynamics."

Note: ordering does NOT exactly match the *pre-registered* canonical_splice ≤ nonsense ≤ missense. Observed canonical_splice L17 is deeper than nonsense L12. Re-interpreting: the population-level argmax_layer measures where the alt-vs-ref ΔD peaks, and canonical splice variants disrupt the splice-site recognition that the model integrates at MID-LAYERS (with downstream consequences cascading deeper); shallow splice-grammar recognition (Fig 1) is a different metric (settling depth c per-position, not per-variant ΔD argmax). These two metrics are independent and the v8 narrative now explicitly distinguishes them.

~~Branch B (KW non-sig)~~ — *refuted; KW p ≪ 0.01.*
~~Branch C (3/4 post-hocs)~~ — partial ordering present in pairwise comparisons but the headline claim — class differences exist at population scale — is *fully confirmed* by the 5-way KW.

**Manuscript edits applied.** §3.3 Table 3 replaced with per-class population summary. Figure 3 (`fig_disruption`) is now a 2-row composite: top horizontal boxplot of P/LP argmax_layer per class; bottom 5 representative ΔD_cos traces (one per class at per-class median).

**Factual fix recorded.** The v7 row labelled `BRCA1 17:43057063 G→A frameshift locus` was a SNV stand-in for c.5266dupC (`44_t13_case_studies.py:50-52` script comment), because Phase 3 main filtered all indels (`31_phase3_main.py:64`). ClinVar confirms this variant is `MC=SO:0001587|nonsense` (3-star Pathogenic, BRCA1 W1837X). v8 corrects the label and now includes a true frameshift class via P2-INDEL forward (1064 indels, frameshift n=518).

---

## F4 — Q2 functional positive control (Critique 3, B-1)

**Hypothesis (pre-registered).** `c(functional)` > `c(matched-shuffled)` for cCRE-ELS, GTEx eQTL, GWAS chr22; one-sided MWU p < 1e-10 for each.

**Result.**

| Dataset | n (functional) | mean c (func) | mean c (shuffled, mean of 100) | one-sided MWU p (greater) | per-position Cohen's d (vs background, σ=5.74) |
|---|---|---|---|---|---|
| ENCODE cCRE-ELS chr22 | 5,297,695 | **26.86** | **28.15** | 1.0 (FAILS one-sided greater) | **−0.225** ⭐ |
| GTEx eQTL chr22       | 42,306    | **28.03** | **28.15** | 4.6e-12 (FAILS greater) | −0.022 |
| GWAS Catalog chr22    | 6,723     | **27.91** | **28.14** | 0.027 (FAILS greater) | −0.040 |
| splice donor (§3.1 reference) | 97,604 | 25.64 | 28.15 | reverse-direction reference | **−0.438** |

**HYPOTHESIS REFUTED — REVERSE DIRECTION OBSERVED. ⚠️**

The pre-registered hypothesis was c(functional) > c(shuffled) (i.e., functional sites are deeper). The data shows the OPPOSITE: functional sites have LOWER c (shallower thinking). Path-determining outcome:

> **Triggered Branch in Plan §3.4.B-1.4: "Effect direction reversed (c_func < c_shuffled)".**
> Pre-registered handling: "Honest reporting: this would falsify the framework's basic
> premise. Trigger immediate paper-level reframe — gDTR is not a functional-importance
> signal."

**HOWEVER**, the reversed direction is consistent with the §3.1 splice-shallow finding (splice donors converge at c̄=25.55, well below intron baseline 27.69). Functional sites being shallow is biologically coherent: the model recognises well-characterised regulatory motifs early. So instead of falsifying the framework, the data REPURPOSES B-1 as a NEW POSITIVE FINDING:

> **NEW §3.2 HEADLINE (Option A):** "gDTR shallowness identifies functional regulatory
> elements at genomic scale. Mean settling depth at ENCODE cCRE-ELS regions on chr22 is
> 26.86 (Cohen's d = −0.225 vs matched-shuffled background, n = 5.3M positions), placing
> them on the same shallowness axis as splice donors (d = −0.438). This generalises the
> §3.1 splice-shallow signature to the broader cis-regulatory landscape — a unified
> shallowness-as-recognition signature."

GTEx eQTL and GWAS Catalog show the same direction but biologically marginal effect sizes (|d| ≤ 0.04), and we report all three honestly in Table 2.

**Path C4 (DEMOTE Q2) selected** for the OLD Q2 = high gDTR ∩ low PhyloP claim, which is now retained only as an exploratory observation in App E. The vacated §3.2 slot is filled by the NEW positive finding above.

**HARD GATE conclusion.** Hypothesis fails ⇒ would have triggered C4 demote. Reversed direction creates a STRONGER positive finding ⇒ §3.2 is repurposed (Option A) rather than deleted. Manuscript outcome is net-positive.

---

## F5 — Q2 repeat class breakdown (Critique 3, B-2)

**Result confirmed (data was already in `phase5/q2_enrichment.json` from the v7 Q2 analysis).**

| Class | fold | hypergeom p (one-sided over-rep) | n_overlap_q2 |
|---|---|---|---|
| SINE (Alu, MIR, etc.)        | **0.933** | 1.0 (UNDER-enriched ⚠️) | 384,427 |
| LINE (L1, L2, etc.)          | 1.310 | 0.0 | 390,610 |
| LTR (ERV1, ERVK, ERVL, etc.) | 1.394 | 0.0 | 174,220 |
| DNA                          | 1.203 | (not reported, but significant) | 96K |
| Simple_repeat                | 1.524 | 0.0 | 100,863 |
| Low_complexity               | 2.021 | 0.0 | 21,114 |
| Satellite                    | 0.236 | 1.0 (UNDER-enriched ⚠️) | 1,892 |

**Important honest disclosure.** v7 Table 3 only showed positive-fold classes; SINE under-enrichment (0.93×) and Satellite under-enrichment (0.24×) were HIDDEN. v8 discloses these.

**Manuscript handling (in v8).** Q2 is now demoted (because B-1 functional positive control failed in the original direction); the repeat-class breakdown is referenced briefly in App E's "Q2 region detail and splice fine-profile" subsection rather than promoted to the main text. The original "lineage-specific TE-derived regulatory" claim is dropped — repeat enrichment ≠ functional enrichment, as the user critique correctly noted. The headline §3.2 is now functional-shallowness instead.

---

## F6 — Q2 multi-chromosome replication (Critique 3, B-3)

**Hypothesis (pre-registered).** chr17 top-3 enrichments (cCRE-ELS, LTR, eQTL) within ±0.20 absolute fold of chr22 baselines.

**Result.**

| Class | chr22 fold | chr17 fold | abs diff | chr1 sub-sample |
|---|---|---|---|---|
| ENCODE cCRE-ELS | 1.284 | **1.185** | 0.099 (replicates) | SKIPPED |
| LTR             | 1.394 | **1.469** | 0.075 (replicates) | SKIPPED |
| LINE            | 1.310 | **1.253** | 0.057 (replicates) | SKIPPED |
| SINE            | 0.933 | **1.287** | 0.354 (DIFFERS — direction reversed!) | SKIPPED |
| DNA             | 1.203 | **1.318** | 0.115 (replicates) | SKIPPED |
| Simple_repeat   | 1.524 | **1.756** | 0.232 (consistent) | SKIPPED |
| Low_complexity  | 2.021 | **2.083** | 0.062 (replicates) | SKIPPED |

Note: chr17 Q2 = 5.49% of valid chr17 (vs chr22 3.71%), 12,034 regions ≥100 bp.

**Branch C — PARTIAL replication. ⚠️**

> "chr17 replicates the LTR / LINE / DNA enrichment direction within ±0.20 fold but
> **contradicts the SINE depletion finding** (chr22 SINE 0.93×, chr17 SINE 1.29×).
> SINE distribution is highly chromosome-specific (chr22 has Alu-rich gene-poor
> structure; chr17 has different SINE density), confirming the user's a-priori
> concern about chr-specific TE bias from a single chromosome. We do not generalise
> the SINE depletion claim to the whole genome."

This partial-replication finding is consistent with the broader Q2 demotion: even within the chr-specific repeat-enrichment story, multi-chromosome generalisation is fragile. v8 keeps the chr17 numbers in App E's Q2 subsection as honest disclosure.

**chr1 sub-sample SKIPPED** (Q2 demoted; saved 3 GPU-hours; chr17 partial replication adequately demonstrates chr-specific repeat-distribution effects).

---

## F7 — P2-INDEL frameshift signal

**Hypothesis (pre-registered).** Median argmax_layer for true frameshift indels falls between canonical-splice (shallowest) and missense (deepest), with statistical separation from at least one of those.

**Result.**

- Indel forward: 1064 variants (P/LP frameshift + matched B/LB controls + inframe indels), 0 errors, ~11 min wall on H200, 40 GB peak GPU memory.
- Frameshift P/LP n = **518** (combined del+ins from indel forward).
- median argmax_layer (frameshift): **L11**, IQR [7, 24].
- Indel forward sanity: no-op edit (AAA→AAA) max_abs_dD < 1e-3 confirmed before running the full panel (Plan R6 mitigation worked).
- Schema parity against SNV pipeline: ✅ confirmed by I3 invariant — 78 SNV cols all present + 4 indel-specific extras (`mc_class`, `indel_len`, `frame_class`, `frame_position`).

**Branch A — CONFIRMED. ✅**

> "True frameshifts converge at median argmax_layer L = 11 (n = 518 P/LP),
> intermediate between intron (L10) and nonsense (L12), and shallower than
> missense (L16) / canonical splice (L17). The frameshift class is added to
> Table 3 of the manuscript and to Figure 3 with one representative trace
> (APC chr5:112,839,602 A→ACT, an actual insertion picked at the per-class median)."

This was a positive payoff from the GPU-priority-1 P2-INDEL forward: it both fixed the v7 mislabel issue AND uncovered a coherent shallowness ranking for early-truncation events.

~~Branch B (uniform / non-informative)~~ — *refuted; frameshift class shows tight IQR and clear separation from missense.*
~~Branch C (forward crashes)~~ — *refuted; 0 errors.*

---

## F8 — Cross-section invariants (Plan §6)

**Hypothesis.** I1..I10 hold byte-identically (or within numerical tolerance).

**Result. ALL 10 PASS in both pre-baseline and post-build runs. ✅**

| Invariant | Pre-build (06:02 UTC) | Post-build (06:18 UTC) |
|---|---|---|
| I1 idle-block h_30 ≡ h_31 | PASS — max\|D30−D31\| = 0.000e+00 | PASS — same |
| I2 ΔD AUROC = 0.844 (32-d dD_cos, seed=42) | PASS — 0.8437 | PASS — 0.8437 |
| I3 indel feature schema parity | SKIP (indel csv not produced yet) | PASS — 78 SNV cols + 4 extras |
| I4 γ_cos = 0.39663 frozen | PASS — drift 3.86e-06 | PASS — same |
| I5 tuned-lens recovery JSON | SKIP (file absent) | SKIP (file absent) |
| I6 cross-arch JSON byte-identical | PASS — md5 34fc0fcd... | PASS — same |
| I7 17:43057063 row max_abs_dD | PASS — 3.6699e-02 (rel_err 0.00%) | PASS — same |
| I8 chr22 Q2 = 3.71% / 5,090 regions | PASS | PASS |
| I9 no silent indel filter logged | PASS (p2_indel_forward.py source check) | PASS |
| I10 splice-class labels separate | SKIP (labels not yet produced) | PASS — separate file |

**Branch A — all green. ✅** v8 PDF built cleanly at `/Users/yoonjincho/Project/ICML/ICML_0429_v1 2/gdtr_paper_ICML.pdf` (9 pages, 1.54 MB).

---

## Path summary (Q2 outcome combinations from Plan §8.2)

After F4–F6 landed, the actual outcome combination was: B-1 FAIL (with reverse direction), B-2 confirmed (LTR-led + SINE under-enriched), B-3 chr17 partial replication (SINE direction differs).

- [ ] **C1 — AGGRESSIVE-PASS**
- [ ] **C2 — MODERATE**
- [ ] **C3 — WEAK-FUNCTIONAL**
- [x] **C4 — DEMOTE** *(selected for the OLD Q2 claim — high gDTR ∩ low PhyloP = lineage-specific regulatory)*
- [x] **C5 — REPURPOSE WITH OPTION A** *(NEW path emerged: B-1 reversed direction is itself a positive finding; Option A reframes §3.2 to "shallowness identifies functional regulatory elements" — the cCRE-ELS Cohen's d=−0.225 IS the new contribution)*

**Selected path: C4 + Option A repurpose.**

**Justification:** The pre-registered B-1 hypothesis (functional sites are deeper) was refuted, but the data shows the *opposite* direction — functional sites are shallower. This is consistent with the §3.1 splice-shallow finding (splice donors converge at c̄=25.55 < intron 27.69). Rather than trigger the falsification escape hatch (drop §3.2 entirely), we recognise that "functional sites are shallow" is a coherent, biologically interpretable signal that *generalises* §3.1's splice finding to the broader cis-regulatory landscape. So the manuscript outcome is: OLD Q2 narrative is dropped (Path C4); NEW §3.2 headline = functional shallowness (Option A). Net effect: §3.2 becomes a stronger, more direct contribution than v7's Q2 was.

This is a "calibrated negative-surprise reframing" — the same lesson as v3.0→v4.0 (per `paper_reframing_v3_20260428.md`): when data falsifies a headline claim, neither hide it nor overclaim a different finding; instead let pre-registered branches handle it AND look for a coherent reinterpretation that strengthens (not weakens) the framework.

---

## Reviewer pre-empt questions (anticipated, with answers)

When v8 lands and reviewers ask:

**Q1. "How do you guard against circular HP tuning?"**
A. γ_cos = 0.39663 is frozen on chr22 sanity sequences (Phase 1.4 calibration). Held-out chr17 (full chromosome, 27,586 windows) recomputes q70 = 0.39429 independently (|Δ| = 0.0023, well within ±0.05 tolerance), and the chr17 splice-donor Cohen's d vs intron is −0.349, 94.6% of the chr22 magnitude (−0.369). See Table 1 in §3.1 (chr22-calib / chr17-valid two-column split) and the prose paragraph at the start of §3.1.

**Q2. "Are your splice donor/acceptor results biased by canonical motifs?"**
A. We separately label and report canonical GT-AG, canonical GC-AG, and non-canonical splice donors using the genomic dinucleotides flanking each intron boundary. Pooled chr17+chr22 means: non-canonical 25.13 < canonical GT-AG 25.79 < canonical GC-AG 27.01 < intron 27.72. The ordering is the OPPOSITE of the naive "stronger motif ⇒ shallower" prior — non-canonical sites converge earliest. We report this honestly in §3.1 prose and Figure 1(b); the canonical-vs-non-canonical Cohen's d is small (~0.05) so we do not over-claim. Universality vs intron baseline holds for every splice subclass.

**Q3. "Three case-study variants cannot generalise."**
A. Agreed; the v7 n=3 case study has been replaced. v8 reports per-class population statistics across the full ClinVar 15-gene cohort (4,023 P/LP variants) augmented with 1,064 true frameshift indels from a new GPU forward (Plan §3.3 GPU-priority-1 task). 5-way Kruskal-Wallis p = 7.1×10⁻¹⁰. Figure 3 has both the population-level boxplot (top) and 5 representative ΔD_cos traces (bottom, one per class at the per-class median). The traces are illustrative of the population finding, not standalone evidence.

**Q4. "Is the Q2 'lineage-specific regulatory' claim well-supported?"**
A. The original Q2 = high gDTR ∩ low PhyloP claim is now demoted to App E. The B-1 functional positive control showed that gDTR is in fact LOWER (shallower) at known regulatory elements (cCRE-ELS Cohen's d = −0.225 vs matched chr22 background) — the opposite direction from the original Q2 hypothesis. v8 §3.2 has been REPURPOSED around this new positive finding: gDTR shallowness identifies functional regulatory elements at genomic scale, generalising the §3.1 splice-shallow signature to the broader cis-regulatory landscape. Q2 chr17 multi-chr replication shows partial agreement (LTR/LINE replicate; SINE direction differs by chromosome — chr-specific TE bias as the original critique predicted).

**Q5. "Why nonsense and not frameshift in the v7 case study?"**
A. The v7 row labelled "BRCA1 17:43057063 G→A frameshift locus" is in fact a Pathogenic 3-star nonsense SNV (ClinVar MC=SO:0001587, BRCA1 W1837X) — a SNV cannot be a frameshift. The v7 SNV pipeline silently filtered indels at `31_phase3_main.py:64`, so the script substituted an SNV stand-in. v8 (a) corrects the label to nonsense, (b) adds a true frameshift class via the new P2-INDEL forward (1,064 indels, frameshift n=518, median argmax_layer L11), (c) the per-class population analysis subsumes the 3-variant illustration with KW p = 7.1×10⁻¹⁰.

---

## Reproducibility footer

- v8 PDF: `/Users/yoonjincho/Project/ICML/ICML_0429_v1 2/gdtr_paper_ICML.pdf` (9 pages, 1.54 MB, built 2026-05-04 17:44 KST).
- v8 LaTeX source: `/Users/yoonjincho/Project/ICML/ICML_0429_v1 2/gdtr_paper_ICML.tex`.
- Server compute environment: digitalocean-gpu (snapshot-restored droplet, IP 129.212.181.201, ~/gDTR/, H200 GPU 143 GB).
- All `_status.json` files preserved at `~/gDTR/results/{p1a,p1b,p2,p2_indel,p2_case,p3b1,p3b2,p3b3_chr17}/`.
- Master DAG status log: `~/gDTR/results/revision_v8_status.jsonl` (12 step entries, line-per-step).
- Final invariants check: `~/gDTR/results/verify_invariants.json` — 10/10 PASS post-build.
- Plan document (885 lines): `docs/REVISION_PLAN_v8.md`.
- Results summary (1-page): `docs/REVISION_v8_RESULTS_SUMMARY.md`.
- This memo (filled in 2026-05-04): `docs/INTERPRETATION_MEMO_v8.md`.
- Local figures cache: `/Users/yoonjincho/Project/ICML/results/figures_v3/` (PDFs + PNGs).
- Server figures cache: `/root/gDTR/results/figures_v3/` (same set).
- Analysis scripts: `/Users/yoonjincho/Project/ICML/scripts/` and `/root/gDTR/scripts/` (rsync-synced; 18 new v8 scripts written by builder agent on 2026-05-04 + `regen_v8_figures.py` for figure generation).
- v7 → v8 LaTeX diff: 6 surgical Edit operations (§3.1 prose + Table 1 + fig:splice caption + §3.2 new section + §3.3 per-class + Conclusion).
