# gDTR — Genomic Deep-Thinking Ratio

**A training-free, layer-wise interpretability probe for genomic causal language models, based on prediction-trajectory settling depth.**

This repo ports Chen et al. (2026)'s NLP "Deep-Thinking Ratio" (DTR) to genomic CLMs (HyenaDNA, Evo 2, NT-v2, DNABERT-2) and ships the ICML 2026 workshop short paper plus a separated companion benchmark. Everything below is organised around the actual experiments and the numbers they produced.

---

## Read this first

- **Canonical paper (Paper 1, ICML 2026 workshop, v11.6)**: [`ICML_0429_v3/gdtr_paper_ICML.pdf`](ICML_0429_v3/gdtr_paper_ICML.pdf) — 4-page main + 9-page appendix. Build/regen instructions in [`ICML_0429_v3/README.md`](ICML_0429_v3/README.md).
- **Top-level version map** (which folder = which version): [`VERSIONS.md`](VERSIONS.md).
- **Per-experiment write-ups**: [`docs/findings/`](docs/findings/).
- **Companion paper (Paper 2, ΔH scorer benchmark)**: [`Paper2_DeltaH.docx`](Paper2_DeltaH.docx).

## Two-paper split (2026-04-29)

| | Paper 1 — gDTR (this repo's headline) | Paper 2 — ΔH benchmark (companion) |
|---|---|---|
| Contribution | Layer-wise mechanistic probe: settling depth `c(t)`, ΔD_cos | Single-feature VEP scorer: per-layer hidden-state perturbation `‖Δh‖₂` |
| Headline result | Splice sites are universal shallow-thinking sites; signal survives entropy + motif controls; replicates across 4 CLMs | AUROC **0.926** [0.921, 0.932] on 10,910 ClinVar variants |
| Status | ICML 2026 workshop short paper (v11.6 built, 2026-05-05) | Standalone DOCX skeleton (`Paper2_DeltaH.docx`) |

Paper 1 keeps `‖Δh‖₂` only as a non-headline sanity check; the headline ‖Δh‖₂ benchmark belongs to Paper 2 and **must not be merged back**.

---

## Experiments and results

Numbers below are the actual measurements stored in the repository. Each row points to (i) the script(s) that produced it, (ii) the on-disk artifact you can re-load, and (iii) the per-experiment write-up.

### E0 · Phase 0 — HyenaDNA-medium-160k PoC (2026-04-26)

- **Setup**: HyenaDNA-medium-160k, 8 blocks, |V|=12, single RTX 3090, ~38 min wall clock.
- **Result — Layer 7 anomaly is real and mechanistically explained**: penultimate-block alignment spike violates monotonicity at L7→L8. D1–D5 + E1 decomposition shows ~85–90% is **representation rotation into the trained readout subspace** (lm_head is value-tied to the embedding, so it is not "untying"). A 256×256 affine tuned-lens prototype recovers M2 from 0.120 → **0.917** (top singular value 9.45), causally confirming the mechanism.
- **Result — TP53 / BRCA1 cross-gene replication**: TP53 coding-exon vs intron Mann–Whitney p = 4.88×10⁻²²⁴, Cohen's d = −1.018; BRCA1 d = −0.78 in the same direction.
- **Scripts**: `scripts/01–05_*.py`, `scripts/L7_d{1,2,3,4,5}.py`, `scripts/E1_tied_head_ablation.py`, `scripts/E5_tuned_lens.py`.
- **Write-up**: [`docs/findings/phase0_calibration.md`](docs/findings/phase0_calibration.md).

### E1 · Phase 1 — Evo 2 7B method calibration (2026-04-27)

- **Setup**: Evo 2 7B (`evo2_7b_base`), 32 blocks (attn=[3,10,17,24,31], hcs/hcm/hcl interleaved), DigitalOcean H200 141 GB, 8K/32K context, ~90 min wall clock, 8/8 stages PASS verifier.
- **Result — L31 is architecturally idle**: `max|h_30 − h_31| = 0.000000` exactly across 100 sequences × 6000 positions. Phase 0's "tuned lens at last 1–2 blocks" rule does **not** transfer; the deepest non-degenerate layer is **L=28** (tuned-lens MSE 822 → 0.34, 99.96 % drop).
- **Result — splice as universal deep-thinking signature**: chr22 12,978 windows × 6 kb, 77.9 M positions. Mean settling depth: splice donor 25.57, splice acceptor 25.69, intron 27.82, coding_exon 28.26, 5′UTR 28.99, 3′UTR 27.72, intergenic 28.75. Strongest pairwise Cohen's d = +0.540 (intergenic vs splice_donor). Splice signal extends beyond ±200 bp with asymmetric profile.
- **Result — HP transferability + cancer-gene bias**: best (γ_cos, ρ) on Evo 2 = (0.40, 0.80), Cohen's d = 5.28; Phase 0 lock (0.50, 0.85) sits on a ±0.10/±0.05 plateau. Genome-wide chr22 exon-vs-intron d = −0.068 — direction reversal vs Phase 0's TP53/BRCA1 d ≈ −1.0, exposing a cancer-gene bias in the original cohort.
- **Scripts**: `phase1/scripts/*` (stages 10 → 17), `phase1/scripts/verify_phase.py`.
- **Artifacts**: `results/phase1.{1..6}*/`, `results/phase1.followup{,_full}/`.
- **Write-up**: [`docs/findings/phase1_evo2_calibration.md`](docs/findings/phase1_evo2_calibration.md).

### E2 · Phase 2 — chr17 multi-chromosome replication

- **Setup**: chr17 forward pass, gene-class stratification, splice profile, cross-chromosome comparison vs chr22.
- **Result**: splice shallow-thinking direction replicates on chr17 (independent chromosome), confirming the chr22 result is not a single-chromosome artifact.
- **Scripts**: `scripts/2{0..6}_phase2_*.py`. **Artifacts**: `results/phase2.{0..6}/`.
- **Write-up**: [`docs/findings/phase2_chr17_replication.md`](docs/findings/phase2_chr17_replication.md).

### E3 · Phase 3 — ClinVar variant pathogenicity (15 cancer genes, 10K variants)

- **Setup**: 15 cancer-gene panel, 10,910 ClinVar variants, ΔD_cos vector (32-dim) as feature, 10-fold stratified CV.
- **Result (Paper 1, non-headline App. C)**: ΔD_cos AUROC **0.844** [0.831, 0.857]. DeLong vs Evo 2 likelihood: p = 3.6×10⁻¹⁵, +0.017 AUROC — statistically significant *incremental* information over likelihood.
- **Result (Paper 2 headline)**: per-layer hidden-state perturbation `‖Δh‖₂` AUROC **0.926** [0.921, 0.932]. Reported in Paper 2; in Paper 1 it appears only as a sanity check.
- **Scripts**: `scripts/3{0..3}_phase3_*.py`. **Artifacts**: `results/phase3_main/`, `results/phase3_ensemble/`.
- **Write-up**: [`docs/findings/phase3_variant_pathogenicity.md`](docs/findings/phase3_variant_pathogenicity.md).

### E4 · Phase 4 — Cross-architecture validation (4 CLMs)

- **Setup**: same 12,978 chr22 windows × 6 kb run on Evo 2 (32 layers), HyenaDNA-large (8), NT-v2 (29), DNABERT-2 (12). Per-model γ_q70 calibration.
- **Result — splice shallowness reproduces in every model** (mean settling depth, splice donor / intron):
  - Evo 2: 25.59 / 27.84
  - HyenaDNA-large: 6.55 / 6.89
  - NT-v2: see `results/phase4/per_model_summary.json`
  - DNABERT-2: see same file
- **Result — Spearman concordance matrix** (per-position settling depths between models):
  - Evo 2 ↔ HyenaDNA: ρ = **+0.516** (causal LM cluster)
  - NT-v2 ↔ DNABERT-2: ρ = **+0.663** (MLM cluster)
  - Across causal–MLM boundary: ρ ∈ [−0.29, −0.12] — opposite sign, i.e. the *positions* the two architectures find shallow are different even when the splice ordering replicates.
- **Scripts**: `scripts/4{0..3}_phase4_*.py`, `ICML_0429_v3/scripts/make_v3_figures_remote.py::fig_crossarch`.
- **Artifacts**: `results/phase4/per_model_summary.json`, `results/phase4/concordance_matrix.json`.
- **Write-up**: [`docs/findings/phase4_cross_architecture.md`](docs/findings/phase4_cross_architecture.md).

### E5 · Phase 5 — Q2 conservation discordance

- **Setup**: settling depth vs phyloP/phastCons on chr22, intersected with cCRE-ELS / eQTL / GWAS BED.
- **Result**: shallow-thinking sites enrich in cCRE-ELS regions even when conservation alone does not flag them — gDTR carries information complementary to evolutionary conservation.
- **Scripts**: `scripts/p3b3_*.py`. **Artifacts**: `results/phase5/`.
- **Write-up**: [`docs/findings/phase5_conservation_discordance.md`](docs/findings/phase5_conservation_discordance.md).

### E6 · Tier 1 — per-layer ablation + baseline head-to-head

- **Setup**: 4 single-feature methods compared on the same 8,008-variant ClinVar split, 10-fold stratified CV.
- **Result — head-to-head AUROC** (`results/tier1_baselines/baseline_auroc.json`):
  | Method | Features | AUROC | 95 % CI |
  |---|---|---|---|
  | A · ΔD_cos (gDTR layer-wise) | 32 | **0.844** | [0.831, 0.857] |
  | B · ‖Δh‖₂ (Paper 2) | 32 | **0.926** | [0.921, 0.932] |
  | C · attention rollout | 5 | 0.672 | [0.660, 0.684] |
  | D · integrated gradients | 1 | 0.527 | [0.515, 0.540] |
- **Result — per-layer ablation, bootstrap stability, mechanism case studies**: see `results/tier1_per_layer/per_layer_auroc.csv`, `results/tier1_bootstrap/`, `results/tier1_case_studies/`.
- **Write-up**: [`docs/findings/tier1_extensions.md`](docs/findings/tier1_extensions.md).

### E7 · Tier 2 — Q2 functional / sensitivity / failure / compute cost

- **Setup**: shallow-thinking sites cross-referenced with eQTL / GWAS / cCRE-ELS; HP sensitivity sweep; failure-mode taxonomy; per-stage GPU-hour cost.
- **Result**: Q2 enrichment confirmed; HP plateau ±0.10/±0.05 around the lock; documented failure modes (low-coverage windows, repeat-rich regions); compute-cost table.
- **Artifacts**: `results/tier2_q2_functional/`, `results/tier2_sensitivity/`, `results/tier2_failure/`, `results/tier2_compute/`.
- **Write-up**: [`docs/findings/tier2_extensions.md`](docs/findings/tier2_extensions.md).

### E8 · v11 control — entropy decoupling (NEW, 2026-05-04)

- **Question**: is the splice shallow-thinking signal just per-position entropy in disguise?
- **Setup**: chr22 120 windows × 6 kb = 720 k positions; Spearman ρ between settling depth `c` and per-position entropy `H`, plus a residualised Cohen's d (`scripts/exp1_entropy_correlation.py`).
- **Result — signal *strengthens* after partialling out entropy**:
  - Overall ρ(c, H) = **−0.079** (p ≈ 0).
  - Splice donor vs intron: raw d = **−0.452** → entropy-residualised d = **−0.583** (deeper effect after removing the entropy axis).
- **Artifact**: `results/exp1_entropy_meta.json`. **Used in**: paper §3.1 control panel + App. A.4 table.

### E9 · v11 control — motif-flank perturbation (NEW, 2026-05-04)

- **Question**: is the splice signal driven by the canonical 2-nt GT/AG motif, or by the broader cis-regulatory flanks?
- **Setup**: 1,000 chr22 splice donors, 5 shuffles each, ±100 bp flank shuffle keeping the GT motif, vs a GT→AA point mutation keeping the flanks (`scripts/exp2_shuffled_motif_control.py`).
- **Result — context >> motif**:
  - Real flanks: c̄ = **26.77** (median 28.90).
  - Flank-shuffled, GT preserved: c̄ = 23.59 → real-vs-shuffled Cohen's d = **+0.515** (real is *deeper* — i.e. shuffling the flanks loses the signal). Paired Wilcoxon p = 4.1×10⁻⁵⁹.
  - GT → AA, flanks preserved: c̄ = 27.24 → real-vs-mut Cohen's d = **−0.086** (essentially unchanged). Paired Wilcoxon p = 2.3×10⁻³² (one-sided).
- **Artifact**: `results/exp2_shuffled_meta.json`. **Used in**: paper §3.2 + App. D.3 motif-flank table.

### Summary of headline numbers (Paper 1)

| Claim | Number | Source |
|---|---|---|
| Splice donor mean settling depth (Evo 2 chr22) | **25.57** | E1 / `phase1.6` |
| Intron mean settling depth (Evo 2 chr22) | 27.82 | E1 / `phase1.6` |
| Strongest splice contrast Cohen's d | **+0.540** (intergenic vs donor) | E1 |
| Entropy-residualised donor-vs-intron d | **−0.583** (was −0.452 raw) | E8 |
| Flank-shuffle vs real Cohen's d | **+0.515** | E9 |
| GT→AA mutation vs real Cohen's d | −0.086 (n.s.) | E9 |
| Cross-arch causal-LM concordance ρ | +0.516 (Evo 2↔HyenaDNA) | E4 |
| Cross-arch MLM concordance ρ | +0.663 (NT-v2↔DNABERT-2) | E4 |
| ΔD_cos variant AUROC (App. C only) | 0.844 [0.831, 0.857] | E3 / E6 |

---

## Repository layout

```
.
├── README.md                       This file
├── VERSIONS.md                     Top-level paper/version map
├── LICENSE                         MIT
│
├── ICML_0429_v3/                   Canonical ICML 2026 workshop submission (v11.6)
│   ├── gdtr_paper_ICML.pdf         Built PDF (4-page main + 9-page appendix)
│   ├── gdtr_paper_ICML.tex         LaTeX source
│   ├── README.md, MANIFEST.md      Build + per-figure provenance
│   ├── figures/                    All figures used by the build
│   └── scripts/                    Local + remote figure regen scripts
├── ICML_0429_v1 2/                 v1 (8-page Nature-style) source backup
│
├── Paper1_gDTR*.docx               DOCX writing path for Paper 1 (v0 → v7)
├── Paper2_DeltaH.docx              Standalone DOCX skeleton for Paper 2 (split)
├── ICML_MANUSCRIPT_DRAFT.md        Earlier integrated markdown draft (pre-split)
│
├── docs/findings/                  Per-experiment synthesis docs (canonical narrative)
├── docs/decisions/                 Locked pre-registration + auto-generated gate verdicts
│
├── src/                            Phase 0 modules
├── phase1/                         Phase 1 src + scripts + tests + lock files
├── scripts/                        ~109 analysis scripts (Phase 0 → Tier 2 + v11 controls)
├── tests/                          21 pytest tests (Phase 0)
│
├── results/
│   ├── exp1_entropy/, exp1_entropy_meta.json    E8 entropy decoupling (v11)
│   ├── exp2_shuffled/, exp2_shuffled_meta.json  E9 motif-flank perturbation (v11)
│   ├── phase1.{1..6}*/, phase1.followup{,_full}/  E1
│   ├── phase2.{0..6}/                              E2
│   ├── phase3_main/, phase3_ensemble/              E3
│   ├── phase4/                                     E4 (per_model_summary, concordance_matrix)
│   ├── phase5/                                     E5
│   ├── tier1_baselines/, tier1_per_layer/, tier1_bootstrap/, tier1_case_studies/   E6
│   ├── tier2_q2_functional/, tier2_sensitivity/, tier2_failure/, tier2_compute/    E7
│   ├── figures/, figures_v2/, figures_v3/          Per-paper-version figure caches
│   ├── _verification/, runs/, status/              Per-stage logs + CPU verification bundles
│
├── requirements.txt                Pinned packages (Phase 0 baseline)
├── requirements_phase1.lock.txt    88 pinned packages for Phase 1
├── env_setup.sh                    Idempotent env bootstrap
└── 260426_연구계획서.docx           Original Korean research proposal
```

Multi-GB hidden-state caches (`results/phase1.6/chr22_cache.h5` etc.) are H200-only; see [`ICML_0429_v3/MANIFEST.md`](ICML_0429_v3/MANIFEST.md) for the LOCAL/REMOTE split per figure.

## Quickstart

### Build the paper PDF (no GPU)

```bash
cd ICML_0429_v3
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

### Reproduce E0 / Phase 0 (HyenaDNA, single RTX 3090, ~38 min)

```bash
git clone https://github.com/darejinn/gDTR-PoC.git
cd gDTR-PoC
bash env_setup.sh
python scripts/00_smoke_test.py
python scripts/01_sanity_check.py        # Gate A
python scripts/02_gene_structure.py      # Gate B (TP53)
python scripts/05_brca1.py               # Cross-gene replication
python scripts/L7_d1d2.py                # Mechanistic D1+D2
python scripts/E5_tuned_lens.py          # Causal tuned-lens prototype
```

### Reproduce E1 / Phase 1 (Evo 2 7B, H200 141 GB, ~90 min)

```bash
cd phase1
python scripts/00_smoke_evo2.py
bash scripts/run_phase1_chain.sh         # Stages 10 → 17 with verify_phase.py
```

### Re-run the v11 controls (E8 / E9, H200)

```bash
python scripts/exp1_entropy_correlation.py     # → results/exp1_entropy_meta.json
python scripts/exp2_shuffled_motif_control.py  # → results/exp2_shuffled_meta.json
```

### Regenerate paper figures

Local-only regen (no H200, schematics + cached summaries) and full real-data regen (H200) are both supported; see [`ICML_0429_v3/README.md`](ICML_0429_v3/README.md) and [`ICML_0429_v3/MANIFEST.md`](ICML_0429_v3/MANIFEST.md).

## Architecture facts (Phase 1 calibration)

- Loaded variant: `evo2_7b_base` (8K/32K context; FP8 1M variant blocked by TE 2.14 + torch 2.4 incompat).
- 32 blocks: attn=[3,10,17,24,31]; hcs=[0,4,7,11,14,18,21,25,28]; hcm=[1,5,8,12,15,19,22,26,29]; hcl=[2,6,9,13,16,20,23,27,30].
- Tied head: storage + value tied (clone before perturbation).
- VRAM: 6 kb = 16.6 GB, 16 kb = 22.5 GB, 32 kb = 31.9 GB.
- Smoke output: [`docs/decisions/phase1_appendix_c.md`](docs/decisions/phase1_appendix_c.md).

## Key references

- Chen, W.-L. et al. (2026). *Think Deep, Not Just Long: Measuring LLM Reasoning Effort via Deep-Thinking Tokens.* arXiv:2602.13517.
- Nguyen, E., Poli, M., Durrant, M.G. et al. (2026). *Evo 2: Whole-genome modeling with context-length scaling.* Nature.
- Nguyen, E. et al. (2023). *HyenaDNA.* NeurIPS 2023.
- Belrose, N. et al. (2023). *Eliciting Latent Predictions from Transformers with the Tuned Lens.* arXiv:2303.08112.
- nostalgebraist (2020). *Interpreting GPT: the Logit Lens.* AI Alignment Forum.

## Reproducibility

- `seed=42` everywhere.
- HF revisions locked: HyenaDNA SHA `7ebf71773d22c0ede2cc55cb2be15ee8c289e1ce`; Evo 2 + cross-arch revisions in `phase1/MODEL_REVISIONS.txt`.
- Data: GRCh38 primary assembly, GENCODE v44, ClinVar 2026-04-18 (`phase1/DATA_VERSIONS.txt`).
- Pinned packages: `requirements_phase1.lock.txt` (88 packages).
- Per-stage JSON sidecars (raw seeds, runtime, host info) at `results/runs/` and `results/status/`.

## Contact

For questions or collaboration: yoonjincho25@yonsei.ac.kr

---

*Phase 0 finalized 2026-04-26. Phase 1 (Evo 2 7B) finalized 2026-04-27. Two-paper split decided 2026-04-29. v11 entropy + motif-flank controls added 2026-05-04. Paper 1 ICML workshop submission v11.6 built 2026-05-05.*
