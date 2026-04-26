# gDTR — Genomic Deep-Thinking Ratio

**A training-free interpretability framework for genomic causal language models, based on layer-wise prediction convergence (settling depth).**

This repository contains the Phase 0 proof-of-concept work: methodology, code, results, figures, and pre-registered Phase 1 plan for transferring Chen et al. (2026)'s NLP "Deep-Thinking Ratio" (DTR) to genomic CLMs.

---

## Status

**Phase 0 (PoC on HyenaDNA-medium-160k): COMPLETE** — 14/14 tasks, 4 paper-grade findings, ~38 minutes compute on a single RTX 3090 (no cloud cost).

**Phase 1 (Evo 2 7B main experiment): pre-registered, ready to start.** See `PHASE1_DECISIONS.md`.

## Three (+1 causal) paper-grade findings

1. **Architectural — Layer 7 anomaly**: Pure-Hyena CLMs (HyenaDNA) exhibit a non-monotonic transformation at the penultimate block (L7→L8) that violates the standard logit-lens monotonicity assumption. Mechanistic decomposition (D1–D5 + E1) shows ~85–90% of this effect is explained by representation rotation into the **trained readout subspace** (not by lm_head untying as initially hypothesized; HyenaDNA's lm_head is in fact value-tied with the embedding matrix).

2. **Calibration — hyperparameter non-transferability**: NLP-DTR default hyperparameters (γ=0.5 with log\|V\| normalization for JSD, γ_cos=0.1 for cosine) DO NOT transfer to genomic CLMs with small vocabularies (\|V\|=12 for HyenaDNA). Effective JSD range was measured at 0.019 — far below the 0.30 threshold for log\|V\| normalization. Quantile-based calibration (γ_q70 of running-min D at the penultimate layer) is required and offered as a methodological contribution.

3. **Robustness — running-min absorbs monotonicity violations**: Despite both Gate A (JSD) and Gate A' (UR-cosine) failing strict per-layer monotonicity at Layer 7, **gDTR (running-min based settling depth) captures strong cross-gene biological signal**: TP53 coding-exon vs intron Mann-Whitney p = 4.88×10⁻²²⁴, Cohen's d = −1.018; replicated independently in BRCA1 (p ≈ 0, d = −0.78). Same direction (intron > coding exon settling depth) in two independent cancer driver genes.

4. **Causal — first-order linear mechanism**: A purely affine pre-rotation of layer-7 hidden states into the trained readout subspace (Belrose 2023-style tuned lens, two 256×256 affine matrices, 15 epochs of MSE loss) recovers JSD M2 at Layer 7 from 0.120 to **0.917** (well above the 0.85 threshold), with ‖A_7 − I‖_F ≈ top singular value 9.45 — i.e., the deviation from identity is concentrated in a single principal direction. This causally confirms the trained-readout-subspace mechanism and validates the Phase 1 tuned-lens design.

## Repository layout

```
.
├── README.md                  This file
├── LICENSE                    MIT
├── docs/
│   ├── phase0_design.md       Pre-registered Phase 0 design (locked) + Appendix C corrections
│   ├── PHASE0_FINDINGS.md     Comprehensive Phase 0 synthesis (~6,400 words)
│   ├── PHASE0_DECISION.md     Gate verdicts + Phase 1 lock (chain-agent finalized)
│   └── PHASE1_DECISIONS.md    Pre-registered Phase 1 plan
├── src/                       10 modules: model_loader, logit_lens, ur_gdtr, gdtr,
│                              variant_delta, controls, viz, stats, constants
├── tests/                     21 pytest tests (all passing)
├── scripts/                   13 analysis scripts (00 smoke → E5 tuned lens)
├── results/
│   ├── figures/               16+ publication-quality figures (PDF + PNG)
│   ├── tables/                15 result CSVs
│   └── runs/                  Per-stage JSON logs (raw seeds, runtime, host info)
├── requirements.txt           Pinned package versions
├── env_setup.sh               Idempotent env bootstrap (incl. apt deps for Linux/CUDA)
└── 260426_연구계획서.docx       Original Korean research proposal (full project context)
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
