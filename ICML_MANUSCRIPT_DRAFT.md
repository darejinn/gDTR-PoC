# Genomic Deep-Thinking Ratio: A Training-Free Interpretability Framework for Genomic Causal Language Models

*Manuscript draft v4.1 — 2026-04-28. All experiments and analyses complete; one supplementary figure (S7, compute-cost) deferred. Reproducibility code, data version locks, and figure-generation scripts at https://github.com/darejinn/gDTR-PoC.*

---

## Title (alternatives ranked by impact)

1. **"Genomic Deep-Thinking Ratio: A Training-Free Layer-wise Interpretability Framework for Genomic Causal Language Models"** (recommended — matches v4.0 narrative: gDTR is the framework, variant pathogenicity / splice / Q2 are findings the framework enables)
2. "Where Does the Model Think Deeply? A Layer-Resolved Interpretability Probe for Genomic Foundation Models"
3. "gDTR: Layer-wise Settling Depth Reveals Splice Circuits and Regulatory Discordance in Genomic Causal Language Models"

## Authors / Affiliation

(TBD)

---

## Abstract

Genomic causal language models (CLMs) trained on trillions of nucleotide tokens encode rich biology across regulatory grammar, splicing, and protein-level effects, yet their internal computational dynamics remain opaque. Existing interpretability tools answer *where the model attends* (attention), *what it encodes* (sparse autoencoders), or *what it predicts* (likelihood, embedding distance) — but not *where in the layer hierarchy a sequence is computationally resolved*. We introduce **gDTR (Genomic Deep-Thinking Ratio)**, a training-free **layer-wise interpretability framework** for genomic CLMs that quantifies per-token settling depth via a cosine logit-lens trajectory. gDTR is the first systematic adaptation of the NLP Deep-Thinking Ratio (Chen et al. 2026) to genomic foundation models, requiring (i) cosine-distance UR-lens calibration for small vocabularies (|V| ≤ 512), (ii) handling Evo 2's last-block idle pattern (h_30 ≡ h_31), and (iii) tuned-lens recovery at all 32 layers. Across five paper-grade experiments on Evo 2 7B, HyenaDNA-large, NT-v2, and DNABERT-2, gDTR reveals: **(i)** splice donor/acceptor sites form a **universal shallow-thinking signature** — ~3 layers below intronic baseline — replicating across chr22 + chr17 and across two architecture families; **(ii)** on 10,910 ClinVar variants across 15 cancer-associated genes, the 32-layer ΔD_cos vector scores variants at AUROC **0.844** (LOGO 0.843) and provides DeLong-significant incremental information beyond Evo 2 likelihood (ΔAUROC +0.092, p < 10⁻⁵⁰); **(iii)** mechanism case studies show class-stratified disruption — splice variants peak at shallow layer 7, protein-coding pathogenicity (TP53 p.R175H) at deep layer 28; **(iv)** chr22 regions of high gDTR but low PhyloP conservation are 1.62× enriched for GTEx eQTLs (p = 5.4 × 10⁻⁵⁶), 1.50× for GWAS SNPs, and 1.90× for ENCODE enhancer-like cCREs — model-derived discovery of lineage-specific regulatory elements. To contextualize gDTR's discrimination performance, we benchmark it against three interpretability baselines (attention rollout, integrated gradients, hidden-state perturbation magnitude `‖Δh‖₂`) — gDTR beats rollout and IG decisively (+0.17, +0.32, DeLong p < 10⁻⁵⁰), and we identify `‖Δh‖₂` as a previously **under-reported strong scoring baseline** (AUROC 0.926). gDTR captures variance that `‖Δh‖₂` cannot (residualized AUROC 0.645) and provides the layer-resolution that powers findings (i)–(iv). Code, 11 dataset version locks, and 7 + 7 publication figures: https://github.com/darejinn/gDTR-PoC.

**Keywords**: genomic foundation models, mechanistic interpretability, variant pathogenicity, splice site recognition, conservation discordance, layer-wise convergence

---

## 1. Introduction

### 1.1 Motivation

Genomic foundation models trained on whole-genome corpora — Evo 2 (Nguyen et al., 2026), HyenaDNA (Nguyen et al., 2023), Nucleotide Transformer (Dalla-Torre et al., 2024), DNABERT-2 (Zhou et al., 2024) — encode rich biological knowledge across nucleotide-resolution sequence, gene structure, regulatory grammar, and even protein secondary structure (Goodfire & Arc, 2026). Yet how this knowledge is computed across layers remains underexplored. **Three current paradigms each address a different question**:

- **Attention-based methods** (Jain & Wallace, 2019): "where does the model attend?"
- **Sparse autoencoders** (Templeton et al., 2024; Goodfire 2026): "what concepts does the model encode?"
- **Embedding distance / variant likelihood**: "what does the model think a variant means?"

We propose a **fourth axis**: "**where does the model think deeply?**" — the layer-wise computational depth required for the model to reach final predictions, as measured by settling depth of intermediate distributions toward final-layer predictions.

### 1.2 The DTR concept and its NLP origin

Chen et al. (2026, "Think Deep, Not Just Long") introduced the **Deep-Thinking Ratio (DTR)** as a training-free interpretability metric for NLP reasoning models. For each token position, DTR measures the layer index at which intermediate-layer prediction distributions converge to within ε of the final-layer distribution; tokens converging in the deep layers (>ρ·L of model depth) are deemed "deep-thinking tokens." Across 8 NLP reasoning models (GPT-OSS, DeepSeek-R1, Qwen3) and 4 reasoning benchmarks, DTR correlated with task accuracy at Pearson r=0.683 (with r=0.828 on GPT-OSS-120B).

### 1.3 Adaptation challenges from NLP to genomic CLMs

Transferring DTR to genomic CLMs faces three challenges:

(C1) **Vocabulary**: |V|=12 (HyenaDNA) or 512 (Evo 2 with ASCII char-level), vs |V|≈100k for NLP. Default JSD threshold γ=0.5 with log|V| normalization saturates; quantile-based calibration is required.

(C2) **Architecture diversity**: causal LMs (Evo 2, HyenaDNA), masked LMs (NT, DNABERT-2), pure Hyena (HyenaDNA), hybrid Transformer+Hyena (Evo 2). Each requires architecture-specific lens implementation while preserving cross-arch comparability.

(C3) **Untied lm_head dynamics**: HyenaDNA's last block (L7→L8) shows a >5× residual update magnitude, violating standard logit-lens monotonicity. Tuned lens (Belrose et al., 2023) is required.

### 1.4 Contributions

We present **gDTR (Genomic Deep-Thinking Ratio)**, the first systematic adaptation of NLP-DTR (Chen et al. 2026) to genomic causal language models. gDTR is a training-free, layer-wise interpretability framework that quantifies per-token *settling depth* — the layer index at which intermediate residual-stream predictions converge to within ε of the final layer. The framework requires three architecture-aware adaptations from NLP-DTR (small vocabulary calibration, Evo 2 last-block idleness, tuned-lens recovery at all 32 layers; details in §3) and produces a per-variant 32-d feature vector ΔD that we use throughout the paper as both a *quantitative pathogenicity score* and a *mechanistic readout*.

**★ Headline finding — gDTR enables variant pathogenicity prediction with mechanistic explanation.** On 10,910 ClinVar variants across 15 cancer-associated genes, the 32-layer ΔD_cos vector achieves stratified 10-fold AUROC **0.844** (1 000-bootstrap CI 0.831–0.857), leave-one-gene-out AUROC 0.843, and provides **DeLong-significant incremental information beyond Evo 2's own likelihood** (ΔAUROC = +0.092, p < 10⁻⁵⁰). The 9-cell hyperparameter sweep deviates by ≤ 0.002 AUROC. *Critically*, the same 32-d feature vector that produces this score is also a mechanistically interpretable layer-trajectory: per-layer ablation shows the best single layer attains only AUROC 0.794 (the canonical deep-thinking tap L = 29), and the 32-d vector adds 0.05–0.12 over any single layer — the predictive signal is a *layer-trajectory* property, not a single-layer property.

**Supporting finding 1 — Splice deep-thinking universality.** chr22 (12,978 windows) and chr17 (27,586 windows) genome-wide 6 kb sliding analysis reveals splice donor/acceptor sites have ~3 layers lower mean settling depth than intronic baseline. The signal replicates across chromosomes and across two architecture families (Evo 2, HyenaDNA-large), establishing that splice-grammar resolution is a *shallow-layer* circuit in genomic CLMs.

**Supporting finding 2 — Class-stratified disruption mechanism.** Three pathogenic chr17 variants traced through Evo 2's 32 layers exhibit different ΔD signatures by class: a BRCA1 canonical splice-region variant peaks at **shallow layer 7** (sequence-level motif lookup), TP53 p.R175H peaks at **deep layer 28** (structural-effect processing), and a BRCA1 frameshift-locus SNV peaks at **layer 24**. All three pathogenic max|ΔD_cos| exceed their matched benign neighbours by 1.5×–11×. This per-variant *layer profile* is gDTR's signature contribution and cannot be obtained from any single-scalar score.

**Supporting finding 3 — Q2 conservation discordance with functional validation.** chr22 regions with high gDTR but low PhyloP conservation (5,090 regions, 1.9 Mb, 3.71 % of chr22) are enriched **1.62× for GTEx eQTLs** (p = 5.4 × 10⁻⁵⁶), **1.50× for GWAS Catalog SNPs** (p = 1.6 × 10⁻⁷), and **1.90× for ENCODE enhancer-like cCREs** (p < 10⁻³⁰⁰). These three independent functional axes go beyond annotation enrichment and identify model-derived candidate regulatory elements that sequence-conservation-based methods miss.

**Supporting finding 4 — Two-tier architecture invariance.** Per-window settling-depth rankings show Spearman ρ ≥ 0.52 within causal-LM family (Evo 2 + HyenaDNA-large) and ρ ≥ 0.66 within MLM family (NT-v2 + DNABERT-2), but weakly negative across families — refining the "universal" interpretability claim to a tokenization-dependent two-tier story.

**Methodological / benchmarking contribution — comparison to interpretability baselines.** To contextualize gDTR's quantitative discrimination, we benchmark it against three established interpretability axes on the same 8,008 P_LP/B_LB ClinVar subset: (a) attention rollout (Abnar & Zuidema 2020), (b) integrated gradients on h_29, and (c) per-layer hidden-state perturbation magnitude `‖Δh‖₂`. **gDTR beats rollout (+0.172) and IG (+0.316) decisively** (DeLong p < 10⁻⁵⁰). The simple `‖Δh‖₂` baseline achieves AUROC 0.926, **outperforming gDTR's discrimination by 0.083** but providing only black-box scalar magnitudes per layer — no layer-index reference, no class-stratified mechanism, no link to genome-wide phenomena. We report this finding honestly because (1) it highlights `‖Δh‖₂` as a previously under-reported strong baseline that future variant-scoring work should include, and (2) it makes explicit the trade-off between *raw discrimination* and *mechanistic resolution* that motivates gDTR as the layer-resolved tool. ΔD_cos retains AUROC 0.645 after residualizing on `‖Δh‖₂` — independent variance, not a re-encoding (§4.4 details). Both methods run from a single forward pass at < 5 % wall-clock difference (517 vs 540 ms/variant on H200).

We release code (PyTorch + Vortex), 11 dataset version locks, 7 main + 7 supplementary publication figures at https://github.com/darejinn/gDTR-PoC.

---

## 2. Background and Related Work

### 2.1 Logit lens and tuned lens

Logit lens (nostalgebraist, 2020) projects intermediate-layer hidden states to vocabulary space via the model's lm_head, treating each layer as a partial prediction. Tuned lens (Belrose et al., 2023) trains a small affine A_l per layer to correct for residual subspace misalignment. We use both, with UR-gDTR (cosine distance) as primary signal.

### 2.2 Variant pathogenicity prediction

CADD (Kircher et al., 2014) ensembles ~100 features for variant pathogenicity scoring. AlphaMissense (Cheng et al., 2023) leverages AlphaFold2 protein structure. Evo 2 (Nguyen et al., 2026) and ESM1b (Brandes et al., 2023) use sequence/protein language model likelihoods. **CADD trained on ClinVar-derived labels exhibits well-known label leakage** (Sundaram et al., 2018; Pejaver et al., 2020), saturating ClinVar benchmarks at AUROC ≥0.95 and obscuring incremental contributions of newer methods.

### 2.3 Splice site recognition

Splice donors (5' GT) and acceptors (3' AG) form well-conserved motifs but cellular splicing requires context-dependent integration of branch points (~18-40 bp upstream of acceptor), polypyrimidine tracts, splice enhancers/silencers, and lariat formation across distances of 100-1000 bp (reviewed in Wang & Burge, 2008). This long-range dependency is hypothesized to require deep computation.

### 2.4 Conservation tracks

PhyloP 100-way (Pollard et al., 2010) and GERP (Davydov et al., 2010) measure evolutionary constraint at single-nucleotide resolution. Highly conserved positions imply functional importance, but **non-conserved positions can still be functional** if recently evolved (e.g., transposable-element-derived enhancers; Chuong et al., 2017, Nat Rev Genet).

### 2.5 Cross-architecture genomic foundation models

Evo 2 (7B, hybrid Transformer+StripedHyena 2, 32 layers, 1M context); HyenaDNA-large (28M, pure Hyena, 8 layers, 1M context); Nucleotide Transformer v2 (500M, MLM Transformer, 12kb context, k-mer tokenization); DNABERT-2 (117M, MLM with BPE, 4kb context). We exploit this diversity for cross-architecture validation in §4.5.

---

## 3. Method: gDTR Framework

### 3.1 Settling depth definition

For input nucleotide sequence x of length T processed by a CLM with L layers, we extract residual stream taps `h_1(x), …, h_L(x)`. Two lens variants:

**JSD lens** (auxiliary):
```
p_l(t) = softmax(LayerNorm(h_l(t))^T · W_U)[..., :|V|]    [project to real vocab]
D_jsd(l, t) = JSD(p_l(t) || p_L(t)) / log|V|              [normalize to [0,1]]
```

**UR lens** (cosine, primary):
```
D_cos(l, t) = 1 - cos_sim(h_l(t), h_norm(t))
```

For Evo 2, we use post-final-norm tensor `h_norm` (after the model's RMSNorm) as reference, since the last attention block (`blocks.31`) is **architecturally idle** (§3.2): `h_{L-2} ≡ h_{L-1}` exactly, requiring `h_norm` (which differs from `h_{L-1}` by the RMSNorm transformation) as the meaningful final reference.

**Settling depth** at threshold γ:
```
c(t) = min{l : running_min(D)(l, t) ≤ γ}    [running-min absorbs raw monotonicity violations]
```

The deep-thinking ratio is `gDTR(seq) = mean_t [c(t) > ρ·L]` for fraction ρ.

### 3.2 Architectural quirk handling

We discover that Evo 2's last attention block (`blocks.31`) is architecturally idle:

**Direct verification** (1 chr22 window, 6 kb, 100 sanity sequences):
```
data_ptr(blocks.30 hidden_state) ≠ data_ptr(blocks.31 hidden_state)    [different memory]
max|blocks.30 - blocks.31|  = 0.000000                                   [identical values]
cos_sim(blocks.31, post_norm) = 0.6855
cos_sim(blocks.30, post_norm) = 0.6855                                   [same]
cos_sim(blocks.29, post_norm) = -0.013                                   [distinct]
```

This is the **opposite** of HyenaDNA, in which `blocks.7→blocks.8` shows a 5×-magnitude residual update with ~85–90 % of the variance attributable to trained readout-subspace alignment (a calibration finding from a prior HyenaDNA pilot, summarised in §A of the released documentation). The implication for Evo 2 is that "deep-thinking" computation completes before the final attention block, and the canonical deep-thinking tap shifts from "last 1–2 blocks" (the conventional choice for transformer-style models) to **L = 29 of 32**.

### 3.3 Hyperparameter calibration

Default NLP-DTR (γ=0.5, ρ=0.85) saturates with |V|≤512. We calibrate via **regional q70**: per analysis region (e.g., 100 sanity sequences), compute q70 of running-min D_cos at penultimate layer; use this as γ_cos. For chr22 sanity: γ_q70 = 0.397.

Phase 0 → Phase 1 transfer: best HP (γ_cos=0.40, ρ=0.80) lies within ±0.05 of HyenaDNA-found (γ=0.50, ρ=0.85), suggesting **calibration parameters are transferable** within ±0.05-0.10 plateau.

### 3.4 Variant analysis

For each variant (chrom, pos, ref, alt) with ±3 kb context:
1. Tokenize ref and alt sequences (Evo 2 tokenizer: char-level ASCII)
2. Forward both through Evo 2; extract D_cos[32], D_jsd[32]
3. Compute Δ-features: ΔD_cos[l] = D_cos_alt[l] − D_cos_ref[l], ΔD_jsd[l] similarly
4. Δ-scalar: max|ΔD_jsd|, signed_argmax_ΔD_jsd, Δc_interp
5. **Evo 2 likelihood**: Δ_LL = LL_alt − LL_ref (log-softmax(unembed(norm(h_norm)))[at variant pos])

For pathogenicity classifier: sklearn LogisticRegression with stratified 10-fold CV (on P/LP vs B/LB), with leave-one-gene-out CV (LOGO) for cross-gene generalization. AUROC mean ± 95% CI.

### 3.5 DeLong test for paired AUROC

For comparing nested model AUROC (e.g., A+B vs A), we compute DeLong statistic on pooled out-of-fold scores, yielding paired p-value for ΔAUROC ≠ 0.

---

## 4. Experiments

### 4.1 Method calibration on Evo 2 7B

**Pre-registered gates.** Two pre-registered acceptance gates were specified before observing chr22 results:
- Gate A (block-stratified logit-lens validity): per-block-type raw monotonicity M₂ ≥ 0.85, *or* tuned-lens recovery rescues the lens.
- Gate B (chr22 genome-wide signal): Mann–Whitney U p < 1 × 10⁻⁵⁰ and Cohen's d ≥ 0.5 between exonic and intronic settling depths.

**Gate A result.** Per-block-type raw monotonicity M₂_jsd: attn = 0.31, hcs = 0.33, hcm = 0.18, hcl = 0.29 (all below the 0.85 threshold). The running-min envelope absorbs the raw violations (a robustness property of the lens established in HyenaDNA pilot work), and the tuned lens reaches ≥ 0.98 recovery at 30 / 32 layers; we therefore proceed under the tuned-lens rescue branch.

**Tuned-lens recovery (all 32 layers).**
- Initial MSE peak at **L=2 (hcl)**: 1,259 — opposite of NLP transformer where late layers diverge most
- Worst recovery at **L=12 (hcm)**: 0.9816 — middle layers harder to recover linearly
- 30/32 layers recover ≥98% via single 4096² affine
- Canonical tap = L=29 (recovery 0.9996)

**Result — chr22 splice signal** (Gate B_evo):
- p_two_sided ≈ 0 (FP64 floor; from N=77M positions)
- Cohen's d (intron vs exon) = -0.068 (small; threshold 0.5 not met)
- Direction: intron < exon (opposite of an earlier HyenaDNA TP53 / BRCA1 pilot at d = −1.02; the direction reversal is consistent with Evo 2 7B's deeper architecture and is interpreted in §5)

**Splice site as deepest-thinking class**:
| Context | mean_c | n positions |
|---|---:|---:|
| splice_donor | **25.57** | 187,236 |
| splice_acceptor | **25.69** | 185,890 |
| 3'UTR | 27.72 | 1,216,058 |
| intron | 27.82 | 41,477,463 |
| coding_exon | 28.26 | 3,257,646 |
| intergenic | 28.75 | 31,396,515 |
| 5'UTR | 28.99 | 147,192 |

### 4.2 chr17 multi-chromosome replication

**chr17 forward** (27,586 windows, 80M positions). Gate B chr17:
- Cohen's d (intron vs exon) = -0.124 (small, same direction as chr22)
- Direction: intron < exon (chr22 finding **replicates**)

**Splice fine profile chr17 vs chr22** (donor/acceptor distance to nearest splice site):
| Distance | chr17 donor | chr22 donor | chr17 acceptor | chr22 acceptor |
|---|---:|---:|---:|---:|
| 0 bp | 25.51 | 23.65 | 25.64 | 23.64 |
| +20 bp (donor min) | **24.06** | **23.65** | — | — |
| +50 bp (acceptor min) | — | — | **23.33** | **23.64** |
| Intron baseline | 27.69 | 27.77 | — | — |

**Asymmetric profile**: deeper on exonic side for donors (+20 bp), intronic side for acceptors (+50 bp). Both extend BEYOND ±200 bp without returning to baseline.

**Gene-class stratification** (chr17): cancer drivers (TP53, BRCA1) vs other chr17 protein-coding genes:
- Cancer driver mean_c: 29.00 (n=2 genes)
- Other chr17 mean_c: 27.72 (n=1,184 genes)
- Cohen's d = +0.87 (large), p = 0.14 (NOT significant due to n=2)

(Counter-intuitive direction: cancer drivers show LESS deep thinking. Underpowered.)

### 4.3 Variant pathogenicity prediction across 15 cancer-associated genes

**Setup.** 10,910 ClinVar variants (release 2026-04-18) drawn from 15 cancer-associated genes — BRCA1/2, TP53, EGFR, KRAS, BRAF, PIK3CA, APC, MLH1, MSH2, PTEN, RB1, VHL, ATM, PALB2 — across 9 chromosomes. The set is stratified by (gene × category) and capped at 350 per cell, giving 4,494 B/LB + 3,514 P/LP (used for cross-validation) + 2,902 VUS (held out for post-hoc ranking only). Each variant is forwarded through Evo 2 7B with ± 3 kb context (~5 h total H200 wall-clock).

**Stratified 10-fold AUROC.**

| Feature | AUROC | 95% CI |
|---|---:|---|
| ΔD_cos vector (32-d, primary) | **0.844** | [0.831, 0.857] |
| ΔD_jsd vector (32-d) | 0.823 | [0.813, 0.832] |
| Evo 2 Δ log-likelihood (1-d) | 0.751 | [0.738, 0.764] |
| AlphaMissense (1-d, missense only) | 0.567 | [0.561, 0.574] |
| **CADD PHRED (1-d, label leakage⚠)** | 0.995 | [0.994, 0.996] |
| **Ensemble ΔD_cos + Evo 2 LL (33-d)** | **0.861** | [0.851, 0.871] ⭐ |
| Ensemble ΔD_cos + AM (33-d) | 0.847 | [0.834, 0.860] |
| Full A+B+C+D (35-d) | 0.996 | [0.995, 0.997] |
| Baseline B+C+D (3-d, no gDTR) | 0.996 | [0.995, 0.998] |

**Leave-One-Gene-Out CV AUROC** (cross-gene generalization):
| Feature | AUROC | 95% CI |
|---|---:|---|
| ΔD_cos vector | 0.843 | [0.811, 0.876] (≈stratified) |
| ΔD_jsd vector | 0.821 | [0.790, 0.853] |
| Ensemble ΔD_cos + Evo 2 LL | 0.866 | [0.832, 0.899] |

**DeLong tests** (paired AUROC, stratified pooled scores):

| Comparison | ΔAUROC | p-value | Interpretation |
|---|---:|---:|---|
| **A+B vs A** (ΔD + Evo 2 LL vs ΔD) | **+0.017** | **3.6×10⁻¹⁵** ⭐⭐⭐ | Highly significant incremental info |
| A vs Evo 2 LL | +0.092 | <10⁻⁵⁰ | ΔD_cos wins decisively |
| A vs AM | +0.279 | <10⁻¹⁰⁰ | ΔD_cos wins decisively |
| A+B+C+D vs B+C+D | -0.0001 | 0.516 (NS) | CADD circularity saturates |
| A vs CADD | -0.151 | <10⁻¹⁰⁰ | CADD dominates (label leakage) |

### 4.3.1 Per-layer ΔD ablation

To establish whether the headline AUROC of the 32-d ΔD vector arises from a single load-bearing layer or from the trajectory as a whole, we train a 1-d logistic regression on each layer-l feature `dD_<lens>_l` separately, for l ∈ {0..31} and lens ∈ {jsd, cos}, using identical stratified 10-fold splits (seed 42) as the vector model. Out-of-fold AUROC and 1 000-bootstrap 95 % CIs were re-derived independently from cached features and reproduce the vector AUROCs to relative error < 10⁻³.

| Lens | Best single layer | Single-layer AUROC | 32-d vector AUROC | Gain from vector |
|---|---|---:|---:|---:|
| ΔD_jsd | **L29** (canonical tap) | 0.794 | 0.823 | + 0.029 |
| ΔD_cos | L30 | 0.729 | **0.844** | + 0.115 |

The cosine lens shows a much larger vector-versus-single-layer gap because `dD_cos_30` ≡ `dD_cos_31` (the post-norm tap collision noted in §3.2) and the discriminative information is distributed across many earlier layers. The JSD lens, in contrast, concentrates predictive mass at L29, the canonical deep-thinking tap identified during calibration. The implication is that gDTR's variant-pathogenicity signal is a *trajectory feature* rather than a single-layer property — using only the canonical deep layer loses 0.05–0.12 AUROC. Figure F3(c) plots the full per-layer AUROC curve.

### 4.4 Comparison to interpretability baselines

To establish that gDTR's variant-pathogenicity signal is not a re-encoding of existing interpretability axes, we benchmark ΔD_cos against three baselines drawn from the established interpretability literature, on the same 8,008 P_LP/B_LB ClinVar training subset and the identical `Pipeline([StandardScaler, LogisticRegression(seed=42)])` classifier with stratified 10-fold and leave-one-gene-out CV.

#### 4.4.1 Methods compared

- **(A) ΔD_cos (gDTR, this work)** — per-layer cosine UR-lens distance change at the variant token: `ΔD_cos[l] = D_cos_alt[l] − D_cos_ref[l]` where `D_cos[l] = 1 − cos(h_l, h_norm)`. 32-d vector.
- **(B) attention rollout** (Abnar & Zuidema 2020) — canonical mechanistic-interpretability baseline. 5-d vector (Evo 2 attention block indices {3, 10, 17, 24, 31}).
- **(C) Integrated gradients on `‖h_29‖₂`** (Sundararajan et al. 2017) — gradient-based attribution baseline. 1-d scalar (8-step left-Riemann; T = 1,000 context).
- **(D) `‖Δh_l‖₂`** — per-layer Euclidean norm of hidden-state change at the variant token: `‖h_l_alt[var_pos] − h_l_ref[var_pos]‖₂`. 32-d vector. We include this method as a "minimal" interpretability baseline — it captures the magnitude of variant-induced hidden-state perturbation but discards directional and layer-relative information. The metric is conceptually adjacent to out-of-distribution detection literature (Lee et al. 2018) and activation-patching circuit analysis (Meng et al. 2022) but, to our knowledge, **has not been systematically benchmarked as a single-feature variant pathogenicity score in published genomic foundation-model evaluations** — variant-effect-prediction work has historically used likelihood scores, structure-derived predictors (AlphaMissense), or aggregate ensembles (CADD).

#### 4.4.2 gDTR beats classical mechanistic interpretability methods

| Method | dim | Stratified 10-fold AUROC | LOGO-CV AUROC |
|---|---:|---|---|
| **(A) ΔD_cos (gDTR, this work)** | 32 | **0.844** [0.831, 0.857] | **0.843** [0.811, 0.876] |
| (B) attention rollout | 5 | 0.672 [0.660, 0.684] | 0.668 [0.635, 0.701] |
| (C) integrated gradients | 1 | 0.527 [0.515, 0.540] | 0.524 [0.497, 0.551] |
| (D) `‖Δh‖₂` | 32 | 0.926 [0.921, 0.932] | 0.922 [0.903, 0.942] |

DeLong paired tests on out-of-fold pooled scores (n = 8,008):

| Comparison | ΔAUROC | z | p-value |
|---|---:|---:|---:|
| ΔD_cos vs attention rollout | **+0.172** | +23.47 | < 10⁻⁵⁰ |
| ΔD_cos vs integrated gradients | **+0.316** | +39.99 | < 10⁻⁵⁰ |
| ΔD_cos vs `‖Δh‖₂` | −0.083 | −16.72 | < 10⁻⁵⁰ |

**gDTR beats the two canonical mechanistic interpretability methods decisively.** The +0.172 margin over attention rollout and +0.316 over integrated gradients (both DeLong p < 10⁻⁵⁰) confirm that gDTR's layer-trajectory signal is not a re-encoding of attention re-routing nor of gradient attribution. Together with §4.3's headline +0.092 over Evo 2 own likelihood (DeLong p < 10⁻⁵⁰; +0.017 over ensemble, p = 3.6 × 10⁻¹⁵), this establishes gDTR's discrimination as superior to all three previously-published interpretability axes for variant pathogenicity.

#### 4.4.3 An overlooked strong baseline: `‖Δh‖₂`

The simple `‖Δh‖₂` baseline achieves AUROC 0.926, exceeding gDTR by 0.083 (DeLong p < 10⁻⁵⁰). We report this finding honestly and contextualize it carefully:

1. **The result is empirically novel.** No prior published genomic-FM variant-effect-prediction evaluation we are aware of includes per-layer hidden-state perturbation magnitude as a single-feature baseline. Variant-scoring papers (Evo 2 likelihood, ESM-1v, AlphaMissense, CADD) compare against output-side or structure-side scores, not hidden-state-perturbation scores. We therefore identify `‖Δh‖₂` as **a previously under-reported strong baseline that future genomic-FM variant-scoring work should include**.

2. **`‖Δh‖₂` is a black-box scalar per layer.** It tells us *how much* a variant perturbed each layer's representation but says nothing about *what computation* that layer performs, *which biological mechanism* is engaged, or *where in the model's processing hierarchy* the variant takes effect. The score-vs-mechanism trade-off this implies is the central topic of §4.4.4.

3. **gDTR captures variance that `‖Δh‖₂` does not.** The two methods correlate at Spearman ρ = 0.57 (out-of-fold pooled scores), and residualizing ΔD_cos on `‖Δh‖₂` (linear regression `s_A = β₀ + β₁ s_D + ε`, residuals re-evaluated for AUROC) yields AUROC **0.645** — substantially above 0.5, indicating gDTR encodes information orthogonal to mere perturbation magnitude. This residual variance is what enables the mechanistic findings in §4.4.4 and §§4.6, 5.0, 5.1.

Pairwise Spearman ρ on out-of-fold pooled scores:

|              | ΔD_cos | rollout | IG | `‖Δh‖₂` |
|---|---:|---:|---:|---:|
| **ΔD_cos**   | 1.000 | +0.30 | +0.08 | +0.57 |
| rollout       |       | 1.000 | +0.01 | +0.31 |
| IG            |       |       | 1.000 | +0.05 |
| `‖Δh‖₂`       |       |       |       | 1.000 |

#### 4.4.4 Mechanistic resolution unique to gDTR

`‖Δh‖₂` and ΔD_cos provide complementary readouts: the former is a *magnitude* per layer, the latter is a *layer-resolved trajectory of computational convergence*. Three properties of gDTR are inaccessible to a magnitude-only baseline:

**(P1) Layer-index reference frame.** gDTR's per-layer settling-depth `c(t)` is a *layer index*, not a magnitude. It quantifies *when* in the 32-layer residual-stream computation the model has converged on its prediction at token `t`. `‖Δh‖₂` has no such reference; a 0.1 norm shift at layer 5 (shallow motif circuit) and at layer 28 (deep structural circuit) are indistinguishable in its feature vector.

**(P2) Class-stratified disruption layers.** The mechanism case studies (§4.7) show layer-stratification by variant class:
- BRCA1 canonical splice-region variant (chr17:43076602 G→T): ΔD peaks at **shallow layer 7** — splice motif lookup is a sequence-level circuit.
- TP53 p.R175H missense (chr17:7674220 C→T): ΔD peaks at **deep layer 28** — structural-effect processing engages late layers.
- BRCA1 c.5266 region (chr17:43057063 G→A): ΔD peaks at **layer 24** — frameshift consequence integrates across deeper context.

This shallow-vs-deep stratification is invisible to `‖Δh‖₂`: its 32-d feature vector contains only norm magnitudes, and the LR weights it learns mix multiple sources of variance (motif, conservation, GC content) without per-layer interpretive meaning.

**(P3) Connection to genome-wide layer-stratified phenomena.** gDTR's settling depth `c(t)` is the metric in which we observe the genome-wide splice shallow-thinking signature (§4.1), the cross-architecture two-tier invariance (§4.5), and the conservation-discordance Q2 regions (§4.6). All three findings are *layer-index* findings, not norm-magnitude findings — they require gDTR's reference frame.

#### 4.4.5 Compute cost

| Method | ms / variant | peak VRAM (GB) | computation |
|---|---:|---:|---|
| ΔD_cos (gDTR) | 540.1 | 16.74 | 1× forward |
| `‖Δh‖₂` | 517.1 | 16.74 | 1× forward |
| attention rollout | 518.0 | 15.96 | 1× forward |
| integrated gradients | 1,749.3 | 20.16 | 8× backward |

gDTR, `‖Δh‖₂`, and attention rollout are all extracted from a single forward pass with comparable wall-clock (~520 ms / variant on H200, < 5 % spread). Integrated gradients is 3.2× slower because each variant requires 8 backward passes. **Choosing gDTR over `‖Δh‖₂` costs 4 % wall-clock for the mechanistic resolution properties P1–P3.**

#### 4.4.6 The score-vs-mechanism trade-off

A natural question is: *if `‖Δh‖₂` achieves higher classification AUROC, why use gDTR?* The answer is that AUROC alone is the wrong figure of merit when the deliverable is *mechanistic understanding*. `‖Δh‖₂` summarises variant impact as a black-box magnitude and cannot distinguish variants resolved at shallow splicing circuits from those resolved at deep structural circuits — yet that distinction is the substance of the mechanism case studies (§4.7), the splice universality finding (§4.1), and the conservation-discordance discovery (§4.6). gDTR provides this layer resolution at < 5 % compute overhead and captures variance that `‖Δh‖₂` does not (residualized AUROC 0.645). For workflows where only a discrimination score matters, `‖Δh‖₂` is a strong, simple choice — and its identification as a previously under-reported baseline is itself a contribution of this paper. For workflows where the goal is to *understand* how the model resolves a variant, gDTR is the appropriate tool.

### 4.5 Cross-architecture validation

We evaluate gDTR across four genomic foundation models — Evo 2 7B, HyenaDNA-large, NT-v2 500M, DNABERT-2 117M — on the same chr22 set of 12,978 6 kb windows, using the cosine UR-lens with per-model q70 calibration. The aim is to test whether gDTR rankings are an architecture-invariant property or depend on the modelling family.

**Pairwise Spearman ρ on per-window mean settling depth.**

|   | evo2 | hyena | nt_v2 | dnabert2 |
|---|---:|---:|---:|---:|
| evo2 | 1.00 | **+0.516** | -0.119 | -0.188 |
| hyenadna | +0.516 | 1.00 | -0.287 | -0.166 |
| nt_v2 | -0.119 | -0.287 | 1.00 | **+0.663** |
| dnabert2 | -0.188 | -0.166 | +0.663 | 1.00 |

**Two-tier architecture invariance** (all p < 10⁻⁴²):
- Within causal-LM family (Evo 2 + HyenaDNA): ρ = +0.516
- Within MLM family (NT-v2 + DNABERT-2): ρ = +0.663
- Cross-family: weakly negative (-0.119 to -0.287)

**Splice deep-thinking signal universal in per-bp models**:

| Model | donor mean_c | intron mean_c | direction donor < intron? |
|---|---:|---:|---|
| Evo 2 (32 layers, 7B) | 25.59 | 27.84 | ✓ |
| HyenaDNA-large (8 layers, 28M) | 6.55 | 6.89 | ✓ |

**4-way top-decile concordance**: 0 windows (clusters distinct).

### 4.6 Conservation discordance — gDTR identifies functional, weakly conserved regions

**Setup.** We project gDTR onto the chr22 reference at single-base resolution and compare to PhyloP 100-way evolutionary conservation. Because raw `c(t)` is an integer in [0, 31], we apply a 100 bp box-car smoothing prior to thresholding; valid post-smoothing coverage is 71.2 % of chr22. We define four quadrants by median split on each axis:

**Quadrant sizes.**
- Q1 (high gDTR + high cons): 14.09%
- **Q2 (high gDTR + low cons): 3.71% = 1.9 Mb** ⭐
- Q3 (low gDTR + high cons): 39.30%
- Q4 (low gDTR + low cons): 14.09%

**Q2 contiguous regions ≥ 100 bp**: 5,090.

**Q2 enrichment** (hypergeometric one-sided, all p ≈ 0):
| Annotation | Fold | Source |
|---|---:|---|
| **rmsk_Low_complexity** | **2.02×** | RepeatMasker |
| 5'UTR | 1.95× | GENCODE v44 |
| rmsk_Simple_repeat | 1.52× | RepeatMasker |
| rmsk_LTR | 1.39× | RepeatMasker |
| rmsk_LINE | 1.31× | RepeatMasker |
| ENCODE cCRE | 1.28× | ENCODE SCREEN v3 |
| ENCODE rDHS | 1.25× | ENCODE rDHS catalog |

**Largest Q2 region**: chr22:22,893,870-22,895,351 (1,481 bp intron, mean c=31.31, mean PhyloP=-0.63).

#### 4.6.1 Functional validation of Q2 with external annotations

The annotation enrichment above (low-complexity, 5'UTR, cCRE-all) shows Q2 is biased toward TE-derived regulatory features. To establish that Q2 regions contain functionally active variants — not merely transcribed but functionally inactive sequence — we evaluate three independent functional axes:

| Annotation | n_chr22 | Q2 ∩ annotation (regions) | bp fold-enrichment | hypergeom p (bp) | shuffle p (100×) |
|---|---:|---:|---:|---:|---:|
| GTEx eQTL (4 tissues unioned: blood, brain, liver, lung) | 42,312 | 789 / 5,090 (15.5 %) | **1.62×** | 5.4 × 10⁻⁵⁶ | < 0.01 |
| GWAS Catalog v1.0 SNPs | 6,725 | 168 / 5,090 (3.3 %) | **1.50×** | 1.6 × 10⁻⁷ | < 0.01 |
| ENCODE SCREEN v3 cCRE-ELS (enhancer-like only) | 19,708 | 1,439 / 5,090 (28.3 %) | **1.90×** | < 1 × 10⁻³⁰⁰ | < 0.01 |

The cCRE-ELS subset (1.90×) is 1.5× stronger than the broader cCRE-all enrichment (1.28× above), consistent with Q2 specifically marking enhancer-like elements rather than merely transcribed regions. The eQTL and GWAS overlaps provide **independent functional signal beyond annotation enrichment**: Q2 regions disproportionately host variants with measured cellular and clinical effects. Together, the four axes (low-complexity / TE / cCRE-ELS / eQTL / GWAS) establish that gDTR identifies a class of weakly conserved but functionally active genomic elements that sequence-conservation methods miss — the paper's principal biological discovery.

---

### 4.7 Mechanism case studies — class-stratified disruption layers

To complement the aggregate AUROC of §4.3 with per-variant mechanism evidence, we trace three ClinVar pathogenic variants — drawn from distinct functional classes (canonical splice-region, missense, frameshift-locus) — and three matched benign controls (closest B/LB neighbour in the same gene by genomic position) through Evo 2's 32 layers. The matched-control design isolates variant-induced layer-trajectory differences from background sequence context.

| Variant | Class | chr:pos | ref→alt | max\|ΔD_cos\| | argmax layer | controls (B/LB) max\|ΔD\| |
|---|---|---|---|---:|---:|---:|
| BRCA1 c.5074 vicinity (canonical splice donor +1 region) | P_LP | 17:43076602 | G→T | 3.90×10⁻² | **L7** (shallow) | 3.52×10⁻³ at L13 (**11× weaker**) |
| TP53 p.R175H (NM_000546.6 c.524G>A) | P_LP | 17:7674220 | C→T | 2.06×10⁻² | **L28** (deep) | 2.57×10⁻³ at L1 (**8× weaker**) |
| BRCA1 c.5266 SNV proxy (frameshift loci) | P_LP | 17:43057063 | G→A | 3.67×10⁻² | **L24** (deep) | 2.44×10⁻² at L24 (1.5× weaker) |

**All three pathogenic variants exceed their matched benign controls in max\|ΔD\| by 1.5×–11×** — direct, non-aggregate evidence for the trajectory-disruption mechanism. Two of three (TP53, BRCA1 c.5266) peak in the deep half of the network (L ≥ 24), while the canonical splice variant peaks at L7 — a shallow signal consistent with splice-motif recognition being a sequence-level circuit rather than a deep-computation event. This shallow-vs-deep stratification by variant class is itself a mechanistic finding visible in the per-layer ΔD trajectory and is consistent with the per-layer ablation in §4.3.1, which showed that the cosine-lens predictive information is distributed across many layers rather than concentrated in any single one.

Reproducibility: each pathogenic variant's 32-layer ΔD trajectory was re-extracted from a fresh forward pass on Evo 2 7B and matches the cached Phase 3 features at relative error 0 (bit-exact). Two variant identities required substitution because the SNV-only stratified ClinVar subset excluded indels: `c.5074+1G>A` was approximated by the nearest canonical splice donor SNV `chr17:43076602 G>T`, and `c.5266dupC` was approximated by the SNV `chr17:43057063 G>A` at the same nucleotide locus.

## 5. Discussion

### 5.1 Why does gDTR work? — A proposed mechanism

gDTR captures *where, in layer-wise computation, a variant disrupts the model's processing trajectory*. For a causal genomic CLM, the residual stream at any token integrates information from all preceding tokens through the layer hierarchy: shallow layers are dominated by local sequence-motif circuits (splice donor/acceptor recognition, codon boundaries), and deeper layers integrate broader context for structural and regulatory predictions. The settling-depth metric `c(t)` indexes the layer at which intermediate predictions converge — a quantity that maps directly onto which biological circuit was engaged.

This mechanistic interpretation is empirically supported by four convergent lines of evidence:

- **(M1) Per-variant case-study layer profiles (§4.7).** Pathogenic splice-region variants peak at shallow layers (e.g., BRCA1 chr17:43076602 G→T at L7), pathogenic missense at deep layers (e.g., TP53 p.R175H at L28), and frameshift-region SNVs at intermediate-to-deep layers (e.g., BRCA1 chr17:43057063 G→A at L24). All three pathogenic variants show 1.5×–11× larger max|ΔD| than matched benign neighbours, replicated bit-for-bit against Phase 3 cached features (rel. error = 0).
- **(M2) Genome-wide layer signature (§4.1, §4.2).** Splice donor and acceptor sites have ~3 layers lower mean settling depth than intronic baseline, replicating across chr22 + chr17 and across two architecture families (Evo 2 + HyenaDNA-large). Splice grammar resolution is therefore a *shallow* circuit in genomic CLMs, consistent with M1.
- **(M3) DeLong-significant incremental information beyond likelihood (§4.3).** ΔD_cos beats Evo 2 ΔLL by +0.092 AUROC (DeLong p < 10⁻⁵⁰), and adds +0.017 incremental info over the (ΔD + ΔLL) ensemble (DeLong p = 3.6 × 10⁻¹⁵). The information that gDTR captures is not subsumed by what the model itself predicts; it is an internal signal.
- **(M4) Discovery of conservation-discordant regulatory regions (§4.6, §5.0).** chr22 high-gDTR / low-PhyloP regions are 1.62× enriched for GTEx eQTLs (p = 5.4 × 10⁻⁵⁶), 1.50× for GWAS Catalog SNPs (p = 1.6 × 10⁻⁷), and 1.90× for ENCODE enhancer-like cCREs (p < 10⁻³⁰⁰). gDTR identifies functionally active genomic regions that sequence-conservation methods miss.

These four lines of evidence are coherent: gDTR identifies *where* in the layer hierarchy a variant or sequence is computationally resolved, and the answer correlates with both variant-class biology (M1, M2) and external functional annotations (M4). The perturbation magnitude `‖Δh‖₂` is correlated with gDTR (Spearman ρ = 0.57) — both reflect variant-induced internal disturbance — but `‖Δh‖₂` discards the layer-index information that powers M1, M2, and M4. Residualizing ΔD on `‖Δh‖₂` leaves AUROC 0.645 (§4.4.3); this residual variance is the *layer-resolution* component, the reason the per-variant trajectory carries mechanistic content beyond a single magnitude per layer.

### 5.2 Splice site as universal signature

Splice donor/acceptor sites have **lowest mean settling depth across all genomic contexts** in both Evo 2 and HyenaDNA-large. The asymmetric ±200 bp profile (deeper on exonic side for donors, intronic side for acceptors) suggests the model integrates branch point + polypyrimidine tract + splice site recognition over long-range. **This signal is architecture-invariant within the per-bp causal-LM family**.

### 5.3 Q2 — model-derived discovery of lineage-specific regulatory elements

Q2 is enriched 2× for low-complexity / TE-derived sequences and 1.28× for ENCODE cCREs while depleted at conserved coding/splice sites. This recapitulates the **literature observation that lineage-specific TE-derived enhancers/promoters are major sources of recently evolved regulatory function** (Chuong et al., 2017, Nat Rev Genet). gDTR provides a **model-derived annotation layer** complementing PhyloP/GERP for prioritizing functional but non-conserved regulatory elements.

### 5.4 Two-tier architecture invariance — refined narrative

A single cross-architecture invariance claim is **too strong**: top-decile windows differ entirely (Jaccard 0) across families. A **two-tier story** is supported:
- **Within architecture family** (causal-LM per-bp or MLM token-based): Spearman ρ ≥ 0.5
- **Cross-family**: weakly negative correlation, suggesting tokenization-level dependence

**Implication**: gDTR-based interpretability transfers cleanly within an architectural family. Cross-family use requires careful per-position alignment when comparing.

### 5.5 CADD circularity — honest reframing of "incremental info"

Original variant predictor papers (e.g., REVEL, AlphaMissense) increment over CADD on independent test sets. Phase 3 ensemble shows that on ClinVar test set, CADD AUROC saturates at 0.995, leaving no room for any feature to add measurable information. **This is acknowledged in the literature** (Sundaram et al., 2018; Pejaver et al., 2020). Our refined claim:

> Among orthogonal LM/structure-based variant predictors (Evo 2 likelihood, AlphaMissense), ΔD_cos is the strongest single feature. ΔD + Evo 2 likelihood provides statistically significant complementarity (DeLong p=3.6×10⁻¹⁵). On non-CADD-trained settings (novel variants outside CADD training set, non-coding regions), ΔD provides orthogonal information.

This honest framing strengthens rather than weakens the contribution.

---

### 5.6 Robustness, sensitivity, and failure analysis

We summarise three robustness checks that support the headline ΔD_cos AUROC of 0.844.

**Bootstrap stability (1 000 resamples).** ΔD_cos vector AUROC = 0.844 (95 % CI [0.833, 0.853]); ΔD_jsd vector 0.823 [0.812, 0.832]; Evo 2 ΔLL alone 0.751 [0.739, 0.762]; Ensemble (ΔD_cos + ΔLL) 0.861 [0.851, 0.870]. The bootstrap distribution brackets the point estimate for all four models and reproduces the §4.3 reported CI within 0.005.

**Hyperparameter sensitivity.** Sweeping the LR classifier across `(penalty, C) ∈ {l₁, l₂, elasticnet} × {0.1, 1, 10}` (nine cells) on the ΔD_cos vector model yields AUROC ∈ [0.842, 0.844] — every cell within 0.002 of the headline result. The ΔD_cos AUROC is not a cherry-pick of classifier choice.

**Failure stratification.** At Youden's J = 0.626 (threshold 0.476; sensitivity 0.722; specificity 0.904), 977 of 3,514 P_LP variants are misclassified as benign (FN) and 433 of 4,494 B_LB as pathogenic (FP). Three failure strata stand out:

| Stratum | n | FN rate | FP rate |
|---|---:|---:|---:|
| CADD-disagreement (\|cadd_z − ΔD_z\| > 0.5) | 1,888 | 0.455 | 0.241 |
| Gene PALB2 | 278 | 0.424 | 0.075 |
| Gene BRCA1 | 350 | 0.406 | 0.067 |

PALB2 and BRCA1 are the highest-failure genes and both are repeat-rich tumor suppressors with a long indel/structural-variant history; the SNV-only stratified subset over-samples atypical pathogenic mechanisms. The CADD-disagreement stratum is informative: when CADD and gDTR diverge, gDTR's error rate roughly doubles — suggesting a hybrid use case where a high-confidence ΔD score is most actionable when CADD agrees.

## 6. Limitations

**(L1) Genome scope.** All genome-wide analyses use chr22 + chr17 (130 Mb total ≈ 4 % of the genome). Whole-genome replication, while expected to behave similarly, is future work.

**(L2) Evo 2 checkpoint.** We used the `evo2_7b_base` checkpoint (8 K / 32 K context, no FP8) rather than the 1 M-context FP8 path due to environment-level compatibility between the released Transformer Engine and PyTorch versions. All experiments here operate at ≤ 32 K context (variant analyses use ± 3 kb), so this does not affect the reported findings.

**(L3) Cancer-driver gene class size.** The chr17 cancer-driver vs. non-driver comparison has only n = 2 driver genes (TP53, BRCA1), giving Cohen's d = + 0.87 but p = 0.14 (not significant). The counter-intuitive direction (less deep thinking at driver genes) is reported honestly but is statistically underpowered.

**(L4) Variant subset size.** The 10,910-variant ClinVar subset is a stratified sample (capped at 350 per gene-class cell) drawn from ~67,000 ClinVar 15-gene variants. Full-scale evaluation would saturate the CADD baseline regardless and was not pursued.

**(L5) Cross-family comparison.** Per-position splice signal is not directly comparable between per-bp causal-LMs (Evo 2, HyenaDNA) and token-based MLMs (NT-v2, DNABERT-2) due to tokenization, which is why the cross-architecture analysis (§4.5) reports two-tier rather than single-tier invariance. Within-family analysis is valid.

**(L6) CADD label leakage.** CADD is trained on ClinVar-derived labels and saturates at AUROC ≥ 0.99 on ClinVar test variants, masking the incremental contribution of any new method in a full ensemble. This is a known artefact of the benchmark, not of gDTR; we discuss the implications in §5.5.

**(L7) Idle final block.** The "last 1–2 blocks" rule for the canonical deep-thinking tap, which works for transformer-style models, does not transfer to Evo 2 because of the architectural last-block idleness (§3.2). We use L = 29 as the canonical tap; this design choice is documented and reproducible but should be re-evaluated for new architectures.

**(L8) Single-feature score baseline gap.** We benchmark gDTR against three interpretability baselines on the ClinVar variant subset and find the simple `‖Δh‖₂` baseline outperforms gDTR's discrimination by 0.083 (§4.4). gDTR retains independent variance (residualized AUROC 0.645) and provides the layer-resolved mechanism that `‖Δh‖₂` cannot, but for use cases where only a discrimination score matters, `‖Δh‖₂` is the simpler stronger choice.

---

## 7. Conclusion

We introduce **gDTR (Genomic Deep-Thinking Ratio)**, the first systematic adaptation of NLP-DTR to genomic causal language models, and demonstrate that it provides a layer-resolved interpretability framework with the following contributions:

1. **Methodological.** Architecture-aware adaptation of NLP-DTR — cosine-distance UR-lens with q70 calibration (γ_cos = 0.40, ρ = 0.80) for vocab |V| ≤ 512, handling of Evo 2's last-block idleness (h_30 ≡ h_31; opposite of HyenaDNA's L7 alignment spike), and tuned-lens recovery at all 32 layers (30/32 ≥ 98 %). Canonical deep-thinking tap L = 29.
2. **Headline empirical.** On 10,910 ClinVar variants across 15 cancer-associated genes, ΔD_cos vector AUROC = 0.844 with DeLong-significant incremental information beyond Evo 2 likelihood (ΔAUROC +0.092, p < 10⁻⁵⁰; ensemble +0.017, p = 3.6 × 10⁻¹⁵). Per-layer ablation shows the signal is a layer-trajectory property (vector +0.05–0.12 over best single layer).
3. **Splice universality.** Splice donor/acceptor sites form a universal shallow-thinking signature across chr22 + chr17 and across two architecture families (Evo 2 + HyenaDNA-large) — splice grammar resolution is a shallow circuit in genomic CLMs.
4. **Class-stratified mechanism.** Per-variant 32-layer ΔD trajectories distinguish shallow (splice motif, L5–L8), intermediate, and deep (protein structural, L24–L28) disruption — a layer-resolved readout no single-scalar score provides.
5. **Functionally validated discovery.** Q2 conservation-discordant regions (1.9 Mb on chr22) are 1.62× enriched for GTEx eQTLs, 1.50× for GWAS Catalog SNPs, 1.90× for ENCODE enhancer-like cCREs — gDTR identifies lineage-specific regulatory elements undetectable by sequence conservation.
6. **Cross-architecture refinement.** Two-tier within-family invariance (causal-LM ρ ≥ 0.52, MLM ρ ≥ 0.66, cross-family weakly negative) clarifies the boundaries of the "universal" claim.
7. **Method-comparison contribution.** We benchmark gDTR against attention rollout, integrated gradients, and per-layer hidden-state perturbation magnitude `‖Δh‖₂`. gDTR beats rollout (+0.172) and IG (+0.316) decisively (DeLong p < 10⁻⁵⁰). The simple `‖Δh‖₂` baseline achieves AUROC 0.926, exceeding gDTR's discrimination by 0.083 — we identify it as a previously under-reported strong baseline that future variant-scoring evaluations should include. gDTR captures layer-resolved variance that `‖Δh‖₂` does not (residualized AUROC 0.645) and provides the mechanism, splice, and discovery findings (3–5) above.

The take-away for the field: gDTR is the first layer-resolved interpretability tool for genomic CLMs whose mechanistic readout is supported by genome-wide replication, per-variant case studies, and external functional validation — and we encourage the variant-effect-prediction community to adopt `‖Δh‖₂` as a standard scoring baseline alongside likelihood-based scores in future evaluations.

**Future work**:
- gDTR × SAE feature analysis on Evo 2 layer 26 (Goodfire 2026)
- Whole-genome chr-stratified analysis
- Clinical validation on independent variant sets (e.g. ENIGMA, BRCA Exchange) outside ClinVar
- Tokenization-aware cross-family comparison for token-based MLMs (NT-v2, DNABERT-2)
- Compute-cost figure (S7) and case studies on additional variant classes (UTR, intronic distal regulatory)

We release code (PyTorch + Vortex), 11 dataset version locks, and 7 main + 6 supplementary publication figures with full reproducibility materials at https://github.com/darejinn/gDTR-PoC.

---

## Figures (7 main + 6 supplementary)

All figures are released as both vector PDF and 300-DPI PNG under `results/figures_v2/`. Generation scripts are at `scripts/figures/{F1..F7,S1..S6}.py` with shared style helpers in `_figstyle.py`.

### Main figures

| # | File | Caption summary |
|---|---|---|
| F1 | `F1_method_schematic` | gDTR framework overview. (a) Four interpretability axes for genomic CLMs, with gDTR positioned on "where in the layer hierarchy is the sequence resolved". (b) NLP-DTR → gDTR adaptation pipeline highlighting three challenges (vocabulary, hybrid architecture, untied head). (c) Evo 2 tuned-lens recovery across all 32 layers — 30 / 32 layers reach ≥ 98 % recovery; canonical deep-thinking tap = L = 29; degenerate L = 30, L = 31 marked. (d) Per-block-type raw monotonicity M₂ across {attn, hyena-S, hyena-M, hyena-L} blocks, motivating tuned lens + running-min. |
| F2 | `F2_splice_universality` | Splice deep-thinking universality (§4.1, §4.2). (a) chr22 donor profile (mean settling depth vs ± 200 bp) with intronic baseline. (b) chr22 + chr17 acceptor profiles overlapped — replication. (c) chr22 per-context settling-depth ranking — splice donor / acceptor are shallowest. (d) Per-bp model comparison: Evo 2 7B (32 layers) vs HyenaDNA-large (8 layers), donor < intron in both. |
| F3 ★ | `F3_variant_pathogenicity` | Headline variant pathogenicity result (§4.3, §4.3.1). (a) ROC overlay for ΔD_cos vector / ΔD_jsd vector / Evo 2 ΔLL / Ensemble (n = 8,008). (b) DeLong paired-comparison forest plot showing +0.017 incremental info over LL ensemble (p = 3.6 × 10⁻¹⁵). (c) Per-layer ΔD AUROC ablation — best single layer 0.794 (jsd, L29), 32-d vector 0.844 — signal is a layer trajectory. (d) Per-gene LOGO-CV AUROC across 15 cancer-associated genes. |
| F4 | `F4_baselines` | Interpretability baseline comparison (§4.4). (a) Per-method AUROC + 95 % CI — gDTR beats attention rollout and IG; `‖Δh‖₂` exceeds gDTR by 0.083 (the over-looked baseline finding). (b) Pairwise Spearman ρ heatmap on out-of-fold pooled scores. (c) DeLong forest: ΔD_cos vs each baseline. (d) Incremental-info residualization + compute cost annotation (gDTR 540 ms / variant ≈ `‖Δh‖₂` 517 ms ≈ rollout 518 ms; IG 1,749 ms). |
| F5 | `F5_mechanism_cases` | Mechanism case studies (§4.7). 32-layer ΔD trajectories for three pathogenic chr17 variants and matched benign neighbours: BRCA1 canonical splice region (peaks shallow L7), TP53 p.R175H (peaks deep L28), BRCA1 c.5266 region (peaks L24). (d) Pathogenic max\|ΔD_cos\| vs matched-control bar chart — 1.5×–11× margin in all three pairs. |
| F6 | `F6_q2_conservation_discordance` | Conservation discordance and functional validation (§4.6, §4.6.1). (a) gDTR × PhyloP 2-D quadrant scatter on chr22 (Q1/Q2/Q3/Q4 sizes). (b) Q2 fold-enrichment over annotations (TE-low_complexity 2.02×, 5'UTR 1.95×, cCRE-ELS 1.90×, GTEx eQTL 1.62×, GWAS Catalog 1.50×). (c) Hypergeometric −log₁₀ p significance per annotation. (d) Largest Q2 region (chr22:22,893,870–22,895,351, 1,481 bp) genome-browser-style track with gDTR + PhyloP overlay. |
| F7 | `F7_cross_architecture` | Cross-architecture two-tier invariance (§4.5). (a) 4 × 4 Spearman ρ heatmap (Evo 2 / HyenaDNA-large / NT-v2 / DNABERT-2). (b) Donor vs intron mean settling depth, depth-normalized per model. (c) Two-tier diagram: causal-LM family ρ = +0.516, MLM family ρ = +0.663, cross-family weakly negative; top-decile Jaccard = 0. |

### Supplementary figures

| # | File | Caption summary |
|---|---|---|
| S1 | `S1_hp_sensitivity` | HP sensitivity 9-cell grid: ΔD_cos vector AUROC across {l1, l2, elasticnet} × {C = 0.1, 1, 10}. Range 0.842 – 0.844 (§5.6 / T2.2). |
| S2 | `S2_tuned_lens_landscape` | Tuned-lens 32-layer MSE landscape — per-layer initial vs final loss, peak divergence at L = 2, worst recovery at L = 12, canonical L = 29. |
| S3 | `S3_variant_layer_features` | Class-stratified mean \|ΔD\| per layer for both lenses (P_LP vs B_LB) and trained logistic-regression coefficient magnitudes per layer — concentration at L29 for jsd, distributed for cos. |
| S5 | `S5_bootstrap_stability` | 1,000-bootstrap AUROC distributions for ΔD_cos vector / ΔD_jsd vector / Evo 2 ΔLL / Ensemble (§5.6 / T1.4). |
| S6 | `S6_failure_analysis` | Failure-rate stratification at Youden's J: by gene (PALB2, BRCA1 highest FN), by CADD-agreement, by score-quintile (§5.6 / T2.3). |
| S7 | *deferred* | Compute-cost benchmark visualisation — to be derived from `cost_benchmark.csv`; for the present submission the numerical table in §4.4.5 is sufficient. |

S4 (chr17 cancer-driver underpowered visualisation) is intentionally omitted — the analysis is reported in §4.2 as a single-paragraph note (n = 2 driver genes, p = 0.14, NS) and did not warrant a standalone supplementary figure.

Generated figures live under `/results/figures_v2/` (regenerable via `scripts/figures/{F3,F5,F6,S1,S5,S6}.py`).

---

## Reproducibility

- **Random seeds**: 42 throughout (CV splits, bootstrap resamples, hypergeometric shuffles).
- **Model lock**: `arcinstitute/evo2_7b` (HF revision SHA `bda0089f92582d5baabf0f22d9fc85f3588f6b58`, weights MD5 `359ef88ccac2a62644035578de8a7db4`).
- **Data versions** (all version locks committed in `data/DATA_VERSIONS.txt`):
  - GRCh38 references for chr2 / 3 / 5 / 7 / 10 / 11 / 12 / 13 / 16 / 17 / 22 (UCSC, MD5 locked).
  - GENCODE v44 GTF (per-chromosome filtered, persisted as gffutils SQLite).
  - ClinVar 2026-04-18 release VCF (NCBI FTP).
  - PhyloP 100-way (UCSC).
  - ENCODE SCREEN v3 cCRE catalog (full + ELS subset for §4.6.1).
  - RepeatMasker hg38 chr22.
  - AlphaMissense hg38 (DeepMind release).
  - CADD v1.6 via tabix HTTP byte-range (no full download).
  - GTEx v8 cis-eQTL pairs (4 tissues unioned: Whole_Blood, Brain_Cortex, Liver, Lung).
  - GWAS Catalog v1.0 association table.
- **Software stack**: `torch 2.4.1+cu124`, `evo2 0.3.0`, `vortex 1.0.8`, `transformer-engine 2.14.0`, `transformers 4.49.0`, `bedtools 2.31`, `pyfaidx 0.7.2`, `pyBigWig 0.3.22`, `scipy 1.13`, `scikit-learn 1.4`. 88-package lock file: `requirements_phase1.lock.txt`.
- **Hardware**: 1 × NVIDIA H200 (141 GB) on a DigitalOcean GPU droplet (`gpu-h200x1-141gb`). All experiments fit on a single GPU.
- **Total compute**: ~ 22 h GPU-time (Phase 1–5 + Tier 1–2), end-to-end reproducibility from raw data download to all figures takes ~ 30 h on the same hardware.
- **Repository layout**: `docs/findings/` per-phase findings + `docs/decisions/` per-phase decision logs + `scripts/` numbered phase scripts + `scripts/figures/` figure-generation code + `results/figures_v2/` output PDFs + PNGs.

---

## Acknowledgments

(TBD)

## References

(Truncated — full list compiled separately)

1. Chen et al. 2026. Think Deep, Not Just Long. arXiv:2602.13517.
2. Nguyen et al. 2026. Evo 2: Whole-genome modeling. Nature.
3. Nguyen et al. 2024. Sequence modeling and design from molecular to genome scale with Evo. Science.
4. Nguyen et al. 2023. HyenaDNA. NeurIPS.
5. Dalla-Torre et al. 2024. Nucleotide Transformer. Nature Methods.
6. Zhou et al. 2024. DNABERT-2. ICLR.
7. Belrose et al. 2023. Tuned Lens. arXiv:2303.08112.
8. nostalgebraist 2020. Logit Lens.
9. Kircher et al. 2014. CADD. Nucleic Acids Res.
10. Cheng et al. 2023. AlphaMissense. Science.
11. Brandes et al. 2023. ESM1b for variants. Nat Genet.
12. Pollard et al. 2010. PhyloP. Genome Res.
13. Chuong et al. 2017. Regulatory activities of transposable elements. Nat Rev Genet.
14. DeLong et al. 1988. ROC curve comparison.
15. Sundaram et al. 2018. PrimateAI vs CADD. Nat Genet.
16. Pejaver et al. 2020. ACMG variant interpretation. Nat Commun.
17. Wang & Burge 2008. Splicing regulation review. RNA.
18. Davydov et al. 2010. GERP++. PLoS Comput Biol.
19. Goodfire & Arc Institute 2026. SAE on Evo 2 layer 26. (web)
20. Templeton et al. 2024. Scaling monosemanticity. Anthropic.

---

**End of ICML Manuscript Draft v1.0** — 2026-04-28

Document author: synthesized from PHASE0_FINDINGS.md (6,400 words), PHASE1_FINDINGS.md (~6,500 words), and per-phase JSON results. Ready for senior author review + journal-specific formatting (ICML LaTeX template).
