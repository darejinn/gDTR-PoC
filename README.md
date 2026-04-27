# gDTR — Genomic Deep-Thinking Ratio

**A training-free interpretability framework for genomic causal language models, based on layer-wise prediction convergence (settling depth).**

This repository contains the full method calibration (Phase 0–1), genome-wide replication (Phase 2), variant-level pathogenicity classification (Phase 3), cross-architecture validation (Phase 4), conservation discordance map (Phase 5), and Tier 1+2 robustness/diagnostic extensions for transferring Chen et al. (2026)'s NLP "Deep-Thinking Ratio" (DTR) to genomic CLMs.

---

## What's new (2026-04-28)

- **Headline finding**: gDTR ΔD_cos vector achieves AUROC **0.844** [0.831, 0.857] on 15 cancer-gene ClinVar variants (10K), with **statistically significant incremental information** over Evo 2 likelihood (DeLong p = **3.6e-15**, +0.017 AUROC). See [`docs/findings/phase3_variant_pathogenicity.md`](docs/findings/phase3_variant_pathogenicity.md).
- **Manuscript v2.0** with Tier 1+2 sections: [`ICML_MANUSCRIPT_DRAFT.md`](ICML_MANUSCRIPT_DRAFT.md).
- **Tier 1 extensions** (per-layer ablation, mechanism case studies, bootstrap stability): [`docs/findings/tier1_extensions.md`](docs/findings/tier1_extensions.md).
- **Tier 2 extensions** (Q2 functional validation against eQTL/GWAS/cCRE-ELS, HP sensitivity, failure analysis): [`docs/findings/tier2_extensions.md`](docs/findings/tier2_extensions.md).
- **Repo reorganization**: per-phase findings consolidated under [`docs/findings/`](docs/findings/) and pre-registered decisions / appendices under [`docs/decisions/`](docs/decisions/). The legacy `PHASE1_FINDINGS.md` (which actually covered Phases 1–5) has been split; see [`docs/findings/_split_plan.md`](docs/findings/_split_plan.md) for the redistribution table.

## Phase status table

| Phase | Topic | Status | Headline doc |
|---|---|---|---|
| 0 | HyenaDNA-medium-160k PoC | DONE | [`docs/findings/phase0_calibration.md`](docs/findings/phase0_calibration.md) |
| 1 | Evo 2 7B method calibration | DONE | [`docs/findings/phase1_evo2_calibration.md`](docs/findings/phase1_evo2_calibration.md) |
| 2 | chr17 multi-chromosome replication | DONE | [`docs/findings/phase2_chr17_replication.md`](docs/findings/phase2_chr17_replication.md) |
| 3 | ClinVar variant pathogenicity (15 genes, 10K variants, AUROC 0.844) | DONE | [`docs/findings/phase3_variant_pathogenicity.md`](docs/findings/phase3_variant_pathogenicity.md) |
| 4 | Cross-architecture validation (Evo 2 / HyenaDNA / NT-v2 / DNABERT-2) | DONE | [`docs/findings/phase4_cross_architecture.md`](docs/findings/phase4_cross_architecture.md) |
| 5 | Q2 conservation discordance | DONE | [`docs/findings/phase5_conservation_discordance.md`](docs/findings/phase5_conservation_discordance.md) |
| Tier 1 | Per-layer ablation, case studies, bootstrap stability, baselines | T1.1/T1.3/T1.4 DONE; T1.2 running | [`docs/findings/tier1_extensions.md`](docs/findings/tier1_extensions.md) |
| Tier 2 | Q2 functional validation, HP sensitivity, failure analysis, compute cost | T2.1/T2.2/T2.3 DONE; T2.4 running | [`docs/findings/tier2_extensions.md`](docs/findings/tier2_extensions.md) |

---

## Status

**Phase 0–5 + Tier 1+2 (excluding T1.2/T2.4 still on server): COMPLETE.**
See the Phase status table above and [`docs/findings/README.md`](docs/findings/README.md) for per-phase docs.

**Phase 0 (PoC on HyenaDNA-medium-160k)**: 14/14 tasks, 4 paper-grade findings, ~38 minutes compute on a single RTX 3090.

**Phase 1 (Evo 2 7B method calibration)**: 8/8 sub-stages PASS, ~90 min H200, three paper-grade findings (L31 idle / splice deep-thinking / HP transferability).

## Three (+1 causal) paper-grade findings

1. **Architectural — Layer 7 anomaly**: Pure-Hyena CLMs (HyenaDNA) exhibit a non-monotonic transformation at the penultimate block (L7→L8) that violates the standard logit-lens monotonicity assumption. Mechanistic decomposition (D1–D5 + E1) shows ~85–90% of this effect is explained by representation rotation into the **trained readout subspace** (not by lm_head untying as initially hypothesized; HyenaDNA's lm_head is in fact value-tied with the embedding matrix).

2. **Calibration — hyperparameter non-transferability**: NLP-DTR default hyperparameters (γ=0.5 with log\|V\| normalization for JSD, γ_cos=0.1 for cosine) DO NOT transfer to genomic CLMs with small vocabularies (\|V\|=12 for HyenaDNA). Effective JSD range was measured at 0.019 — far below the 0.30 threshold for log\|V\| normalization. Quantile-based calibration (γ_q70 of running-min D at the penultimate layer) is required and offered as a methodological contribution.

3. **Robustness — running-min absorbs monotonicity violations**: Despite both Gate A (JSD) and Gate A' (UR-cosine) failing strict per-layer monotonicity at Layer 7, **gDTR (running-min based settling depth) captures strong cross-gene biological signal**: TP53 coding-exon vs intron Mann-Whitney p = 4.88×10⁻²²⁴, Cohen's d = −1.018; replicated independently in BRCA1 (p ≈ 0, d = −0.78). Same direction (intron > coding exon settling depth) in two independent cancer driver genes.

4. **Causal — first-order linear mechanism**: A purely affine pre-rotation of layer-7 hidden states into the trained readout subspace (Belrose 2023-style tuned lens, two 256×256 affine matrices, 15 epochs of MSE loss) recovers JSD M2 at Layer 7 from 0.120 to **0.917** (well above the 0.85 threshold), with ‖A_7 − I‖_F ≈ top singular value 9.45 — i.e., the deviation from identity is concentrated in a single principal direction. This causally confirms the trained-readout-subspace mechanism and validates the Phase 1 tuned-lens design.

## Repository layout

```
.
├── README.md                       This file
├── LICENSE                         MIT
├── ICML_MANUSCRIPT_DRAFT.md        Manuscript v2.0 (Tier 1+2 integrated)
├── docs/
│   ├── phase0_design.md            Pre-registered Phase 0 design (locked) + Appendix C corrections
│   ├── PHASE0_FINDINGS.md          Comprehensive Phase 0 synthesis (~6,400 words)
│   ├── PHASE0_DECISION.md          Phase 0 gate verdicts + Phase 1 lock
│   ├── PHASE1_DECISIONS.md         Pre-registered Phase 1 plan
│   ├── PHASE1_EXECUTION_PLAN.md    Server-specific Phase 1 execution doc
│   ├── findings/                   Per-phase synthesis docs (NEW 2026-04-28)
│   │   ├── README.md               Phase status table + cross-reference index
│   │   ├── phase0_calibration.md
│   │   ├── phase1_evo2_calibration.md
│   │   ├── phase2_chr17_replication.md
│   │   ├── phase3_variant_pathogenicity.md
│   │   ├── phase4_cross_architecture.md
│   │   ├── phase5_conservation_discordance.md
│   │   ├── tier1_extensions.md
│   │   ├── tier2_extensions.md
│   │   └── _split_plan.md
│   └── decisions/                  Locked decisions / auto-generated gate verdicts
│       ├── phase1_decisions.md     (= legacy PHASE1_DECISION.md, auto-generated)
│       ├── phase1_appendix_c.md    Evo 2 7B architectural facts (smoke output)
│       ├── phase1_execution_plan.md
│       └── phase2_decisions.md     (= legacy PHASE2_DECISION.md, auto-generated)
├── src/                            10 modules: model_loader, logit_lens, ur_gdtr, gdtr, …
├── phase1/                         Phase 1 src + scripts + tests + lock files
├── tests/                          21 pytest tests (Phase 0)
├── scripts/                        Analysis scripts; figures/ subdir generates F1-F7 + S1-S6
├── results/
│   ├── figures/                    Phase 0 publication figures
│   ├── figures_v2/                 Manuscript v2.0 figures (F1-F7, S1-S6, ~5 MB)
│   ├── phase1.{1..6}*/             Per-phase JSONs + figures (Phase 1)
│   ├── phase2.*/                   Phase 2 (chr17) outputs
│   ├── phase3_main/, phase3_ensemble/
│   ├── phase4/                     Cross-arch (4 models) summaries + per-model figures
│   ├── phase5/                     Q2 BED + enrichment table
│   ├── tier1_per_layer/, tier1_bootstrap/, tier1_case_studies/
│   ├── tier2_q2_functional/, tier2_sensitivity/, tier2_failure/
│   ├── _verification/              Independent CPU bundle verification (cross-checked)
│   └── runs/                       Per-stage JSON logs (raw seeds, runtime, host info)
├── requirements.txt                Pinned package versions
├── env_setup.sh                    Idempotent env bootstrap (incl. apt deps for Linux/CUDA)
└── 260426_연구계획서.docx           Original Korean research proposal (full project context)
```

Large data files (FASTA, GENCODE, ClinVar VCFs) and `.npz` analysis caches are NOT committed (regenerable from `scripts/`). See `data/` setup in `env_setup.sh`.

## Quickstart (reproduction)

```bash
git clone https://github.com/darejinn/gDTR-PoC.git
cd gDTR-PoC
bash env_setup.sh                              # installs deps, downloads data, caches model
python scripts/00_smoke_test.py                # verify environment
python scripts/01_sanity_check.py              # Gate A
python scripts/01b_jsd_distribution.py         # JSD effective-range measurement
python scripts/01c_ur_sanity.py                # Gate A' (cosine lens)
python scripts/02_gene_structure.py            # Gate B (TP53)
python scripts/03_variant_pilot.py             # Gate C (TP53 hotspots)
python scripts/04_hp_sweep.py                  # Hyperparameter sensitivity
python scripts/05_brca1.py                     # Cross-gene replication
python scripts/L7_d1d2.py                      # Mechanistic D1+D2
python scripts/L7_d3d4d5.py                    # Mechanistic D3+D4+D5
python scripts/E1_tied_head_ablation.py        # Causal: tied vs untied vs random head
python scripts/E2_codon_gdtr.py                # Codon-position stratification
python scripts/E5_tuned_lens.py                # Tuned-lens prototype
```

Total runtime on a single RTX 3090: ~38 minutes for all stages.

## Key references

- Chen, W.-L. et al. (2026). *Think Deep, Not Just Long: Measuring LLM Reasoning Effort via Deep-Thinking Tokens.* arXiv:2602.13517.
- Nguyen, E., Poli, M., Durrant, M.G. et al. (2026). *Evo 2: Whole-genome modeling with context-length scaling.* Nature.
- Nguyen, E. et al. (2023). *HyenaDNA: Long-Range Genomic Sequence Modeling at Single Nucleotide Resolution.* NeurIPS 2023.
- Belrose, N. et al. (2023). *Eliciting Latent Predictions from Transformers with the Tuned Lens.* arXiv:2303.08112.
- nostalgebraist (2020). *Interpreting GPT: the Logit Lens.* AI Alignment Forum.

## Reproducibility

All randomization uses `seed=42`. HyenaDNA HF revision SHA `7ebf71773d22c0ede2cc55cb2be15ee8c289e1ce` is locked. Data versions (GRCh38 primary assembly, GENCODE v44, ClinVar 2026-04-18) are recorded in per-stage JSON sidecars at `results/runs/`.

## Contact

For questions or collaboration: yoonjincho25@yonsei.ac.kr

---

*Phase 0 finalized 2026-04-26. Phase 1 (Evo 2 7B) entry pending.*
---

## Phase 1 (Evo 2 7B): COMPLETE (2026-04-27)

**8/8 sub-stages PASS verify** in ~90 min wall clock on DigitalOcean H200 141 GB. Full automated invariant checks via `phase1/scripts/verify_phase.py` (8 verifier functions). Pipeline orchestrated in two parallel tmux windows.

### Three paper-grade findings (Phase 1)

1. **Architectural — Evo 2 L31 idle (vs HyenaDNA L7 spike)**: The last attention block (`blocks.31`) of Evo 2 7B is effectively a no-op residual passthrough. Direct verification: `max|h_30 - h_31| = 0.000000` exactly across 100 sanity sequences × 6000 positions. This is the exact OPPOSITE of Phase 0 HyenaDNA's L7→L8 alignment SPIKE. Implication: Phase 0's "tuned lens at last 1-2 blocks" rule does NOT transfer to Evo 2; the meaningful tuned-lens depth shifts to **L=28** (deepest non-degenerate layer; follow-up showed initial MSE 822 → final 0.34, 99.96% drop). Architecture-specific deep-thinking patterns confirmed.

2. **Splice site as universal deep-thinking signature**: chr22 genome-wide profiling (12,978 windows × 6 kb, 77.9 M positions) shows splice donor (mean settling depth 25.57) and acceptor (25.69) substantially LOWER than all other contexts (intergenic 28.75, intron 27.82, coding_exon 28.26, 5'UTR 28.99, 3'UTR 27.72). Sub-analysis: splice signal extends BEYOND ±200 bp without returning to background, with asymmetric profile (deeper on exonic side for donors, intronic side for acceptors). Strongest pairwise Cohen's d = +0.540 (intergenic vs splice_donor). Mechanism candidates: branch point + polypyrimidine tract + splice site recognition requires long-range integration.

3. **Calibration transfers, biology direction context-dependent**: HP sweep best (γ_cos, ρ) = (0.40, 0.80), Cohen's d = 5.28 — Phase 0 lock (0.50, 0.85) carries cleanly with ±0.10/±0.05 plateau. However, Gate B chr22 exon-vs-intron Cohen's d = -0.068 (small) with **direction reversal** vs Phase 0 TP53/BRCA1 (d = -1.02 large, intron > exon). Now: intron < exon. Hypothesis: cancer-gene bias in Phase 0 + genome-wide chr22 effect dilution. Sub-analysis identified per-gene rank: top-3 deepest = CCDC188 (22.99), APOBEC3A (23.71), RGL4 (23.72).

### Phase 1 architecture (key facts in `PHASE1_APPENDIX_C.md`)

- Loaded variant: `evo2_7b_base` (8K/32K context; FP8 1M variant blocked by TE 2.14 + torch 2.4 incompat)
- 32 blocks: attn=[3,10,17,24,31], hcs=[0,4,7,11,14,18,21,25,28], hcm=[1,5,8,12,15,19,22,26,29], hcl=[2,6,9,13,16,20,23,27,30]
- Tied head: storage + value tied (clone before perturbation)
- VRAM: 6kb=16.6 GB, 16kb=22.5 GB, 32kb=31.9 GB

### Phase 1 layout (this repo)

```
.
├── PHASE1_FINDINGS.md          Comprehensive synthesis (~5,800 words, Phase 0 style)
├── PHASE1_DECISIONS.md         Pre-registered locked plan (in docs/)
├── PHASE1_APPENDIX_C.md        Architectural facts (smoke test output)
├── PHASE1_EXECUTION_PLAN.md    Server-specific execution doc
├── PHASE1_DECISION.md          Auto-generated gate verdicts
├── phase1/
│   ├── src/                    7 Phase 1 modules: constants_evo2, model_loader_evo2,
│   │                           logit_lens_evo2, ur_gdtr_evo2, tuned_lens, calibration, block_type
│   ├── scripts/                15 scripts: smoke (00), Gate A (10), tuned (12), tuned recheck (13),
│   │                           calibration (14), HP sweep (15), chr22 forward (16), Gate B (16b),
│   │                           Gate B sub-analyses (16c), write-up (17), follow-up tuned at L=15-28 (12b),
│   │                           plus prep scripts, verify_phase, master shells
│   ├── tests/                  Phase 1 env + import sanity
│   ├── DATA_VERSIONS.txt       Locked: GRCh38, GENCODE v44, ClinVar 2026-04-18
│   ├── MODEL_REVISIONS.txt     Locked: HF revisions for Evo 2 + cross-arch models
│   └── requirements_phase1.lock.txt   88 pinned pip packages
├── results/
│   ├── phase1.{1..6}/          Per-phase JSONs + figures (committed)
│   ├── phase1.followup/        L=15/20/25/28 tuned lens checkpoints + curves
│   ├── phase1.6_sub/           Per-gene rank, splice fine profile, Cohen's d matrix
│   └── status/                 Per-phase verify status JSONs
```

### Phase 0 → Phase 1 transfer status

| Phase 0 Decision | Phase 1 Outcome |
|---|---|
| Primary lens = UR-gDTR (cosine) | ✅ Confirmed (Gate A_evo verify PASS) |
| Auxiliary lens = JSD-gDTR + quantile-γ | ✅ Confirmed (caveat: D_jsd[30]/D_jsd[31] ≡ 0 architectural quirk) |
| γ_cos = 0.50, ρ = 0.85 | ✅ Approximately (best 0.40/0.80, ±0.10 plateau) |
| Tuned lens target = last 1-2 blocks | ❌ Architectural mismatch (L31 idle); use L=28 |
| Block-stratified Gate A | Partial confirm (per-block-type M2 distinguishable, but all ≪ 0.85) |

### Reproducibility

- seed=42 everywhere
- HF revision SHA + weights MD5 locked in `PHASE1_APPENDIX_C.md` § C.1
- requirements_phase1.lock.txt (88 packages)
- All compute logged to per-phase status JSONs

