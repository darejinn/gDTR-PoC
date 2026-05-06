# gDTR — Genomic Deep-Thinking Ratio

**A training-free, layer-wise interpretability probe for genomic causal language models, based on prediction-trajectory settling depth.**

This repository hosts the full Phase 0–5 + Tier 1/2 pipeline that ports Chen et al. (2026)'s NLP "Deep-Thinking Ratio" (DTR) to genomic CLMs (HyenaDNA, Evo 2, NT-v2, DNABERT-2), together with the ICML 2026 workshop short paper (Paper 1: gDTR) and the companion benchmark manuscript (Paper 2: ΔH).

---

## Read this first

- **Canonical paper (Paper 1, ICML 2026 workshop, v11.6)**: [`ICML_0429_v3/gdtr_paper_ICML.pdf`](ICML_0429_v3/gdtr_paper_ICML.pdf) — 4-page main + 9-page appendix. Build/regen instructions in [`ICML_0429_v3/README.md`](ICML_0429_v3/README.md).
- **Top-level version map** (which folder = which version, DOCX path, paper-split notes): [`VERSIONS.md`](VERSIONS.md).
- **Per-phase findings index**: [`docs/findings/README.md`](docs/findings/README.md).
- **Companion paper (Paper 2, ΔH scorer benchmark)**: [`Paper2_DeltaH.docx`](Paper2_DeltaH.docx) — kept as a separate manuscript per the 2026-04-29 split.

## Two-paper split (2026-04-29)

The original "two complementary tools in one paper" structure was split into two standalone manuscripts:

| | Paper 1 — gDTR (this repo's headline) | Paper 2 — ΔH benchmark (companion) |
|---|---|---|
| Contribution | Layer-wise mechanistic probe: settling depth `c(t)`, ΔD_cos | Single-feature VEP scorer: per-layer hidden-state perturbation `‖Δh‖₂` |
| Headline result | Splice sites are universal shallow-thinking sites; cross-architecture replication on 4 CLMs | AUROC **0.926** on 10,910 ClinVar variants |
| Status | ICML 2026 workshop short paper (v11.6 built) | Standalone DOCX skeleton (`Paper2_DeltaH.docx`) |

Paper 1 keeps `‖Δh‖₂` only as a non-headline sanity check (AUROC 0.844 in App. C). The headline ‖Δh‖₂ benchmark belongs to Paper 2 and **must not be merged back into Paper 1**.

---

## Phase status table

| Phase | Topic | Status | Headline doc |
|---|---|---|---|
| 0 | HyenaDNA-medium-160k PoC | DONE | [`docs/findings/phase0_calibration.md`](docs/findings/phase0_calibration.md) |
| 1 | Evo 2 7B method calibration | DONE | [`docs/findings/phase1_evo2_calibration.md`](docs/findings/phase1_evo2_calibration.md) |
| 2 | chr17 multi-chromosome replication | DONE | [`docs/findings/phase2_chr17_replication.md`](docs/findings/phase2_chr17_replication.md) |
| 3 | ClinVar variant pathogenicity (15 genes, 10K variants) | DONE | [`docs/findings/phase3_variant_pathogenicity.md`](docs/findings/phase3_variant_pathogenicity.md) |
| 4 | Cross-architecture validation (Evo 2 / HyenaDNA / NT-v2 / DNABERT-2) | DONE | [`docs/findings/phase4_cross_architecture.md`](docs/findings/phase4_cross_architecture.md) |
| 5 | Q2 conservation discordance | DONE | [`docs/findings/phase5_conservation_discordance.md`](docs/findings/phase5_conservation_discordance.md) |
| Tier 1 | Per-layer ablation, case studies, bootstrap stability, baselines | DONE | [`docs/findings/tier1_extensions.md`](docs/findings/tier1_extensions.md) |
| Tier 2 | Q2 functional validation, HP sensitivity, failure analysis, compute cost | DONE | [`docs/findings/tier2_extensions.md`](docs/findings/tier2_extensions.md) |
| v11 supporting | Entropy decoupling control + flank-shuffle motif perturbation | DONE | `results/exp1_entropy_meta.json`, `results/exp2_shuffled_meta.json` |

---

## Paper 1 — Headline findings (gDTR mechanistic probe)

1. **Splice sites are universal shallow-thinking sites.** chr22 genome-wide profiling on Evo 2 7B (12,978 windows × 6 kb, 77.9 M positions) shows splice donor (mean settling depth 25.57) and acceptor (25.69) substantially lower than all other contexts (intron 27.82, coding_exon 28.26, intergenic 28.75). Replicated independently across HyenaDNA-large, NT-v2, and DNABERT-2 (Phase 4 concordance matrix).

2. **Settling depth is not driven by per-position entropy.** Entropy-decoupling control (`results/exp1_entropy/`) reports raw splice-vs-other Cohen's d = −0.452 → entropy-residualised d = −0.583, i.e. the splice signature *strengthens* after partialling out token entropy. Motif-flank perturbation (`results/exp2_shuffled/`) further shows real flanks vs shuffled flanks d = +0.51, while a GT→GC point mutation barely moves it (d = −0.09): the signal lives in the broader cis-regulatory context, not the canonical 2-nt motif.

3. **HyenaDNA L7 and Evo 2 L31 are architecturally idle in opposite ways.** HyenaDNA's penultimate block exhibits a non-monotonic alignment spike that violates the standard logit-lens monotonicity assumption; mechanistic decomposition (D1–D5 + E1) shows ~85–90% is explained by representation rotation into the trained readout subspace (causally confirmed by a 256×256 affine tuned-lens prototype: M2 0.120 → 0.917). Evo 2 7B's last block is the exact opposite — `max|h_30 − h_31| = 0.000000` across 100 sequences × 6000 positions: a pure residual passthrough. The "tuned lens at last 1–2 blocks" rule does **not** transfer; meaningful tuned-lens depth shifts to L=28.

4. **Hyperparameters transfer; biology direction is context-dependent.** Phase 0 lock (γ_cos, ρ) = (0.50, 0.85) sits on a ±0.10/±0.05 plateau; Phase 1 best on Evo 2 is (0.40, 0.80), Cohen's d = 5.28. But chr22 exon-vs-intron Cohen's d = −0.068 (small) reverses direction vs Phase 0 cancer-gene results (TP53/BRCA1 d ≈ −1.0), exposing a cancer-gene bias in the original cohort.

Full per-finding write-ups in [`docs/findings/`](docs/findings/) and the paper §3.

---

## Repository layout

```
.
├── README.md                       This file
├── VERSIONS.md                     Top-level paper/version map (read this for "which folder = which paper")
├── LICENSE                         MIT
│
├── ICML_0429_v3/                   Canonical ICML 2026 workshop submission (Paper 1, v11.6)
│   ├── gdtr_paper_ICML.pdf         Built PDF (4-page main + 9-page appendix)
│   ├── gdtr_paper_ICML.tex         LaTeX source
│   ├── README.md                   Build + figure-regen instructions
│   ├── MANIFEST.md                 Per-figure / per-table source-of-truth
│   ├── figures/                    All figures used by the build
│   └── scripts/                    Local + remote figure regen scripts
├── ICML_0429_v1 2/                 v1 (8-page Nature-style) source backup, kept for diff
│
├── Paper1_gDTR*.docx               DOCX writing path for Paper 1 (v0 → v7)
├── Paper2_DeltaH.docx              Standalone DOCX skeleton for Paper 2 (split, do not merge)
├── ICML_MANUSCRIPT_DRAFT.md        Earlier integrated markdown draft (pre-split, kept for diff)
│
├── docs/
│   ├── findings/                   Per-phase synthesis docs (canonical narrative)
│   │   ├── README.md               Phase status table + cross-reference index
│   │   ├── phase0_calibration.md
│   │   ├── phase1_evo2_calibration.md
│   │   ├── phase2_chr17_replication.md
│   │   ├── phase3_variant_pathogenicity.md
│   │   ├── phase4_cross_architecture.md
│   │   ├── phase5_conservation_discordance.md
│   │   ├── tier1_extensions.md
│   │   └── tier2_extensions.md
│   ├── decisions/                  Locked pre-registration + auto-generated gate verdicts
│   ├── phase0_design.md, PHASE0_FINDINGS.md, PHASE0_DECISION.md
│   └── PHASE1_DECISIONS.md, PHASE1_EXECUTION_PLAN.md
│
├── src/                            Phase 0 modules (model_loader, logit_lens, ur_gdtr, gdtr, …)
├── phase1/                         Phase 1 src + scripts + tests + lock files
├── scripts/                        ~109 analysis scripts (Phase 0 → Tier 2 + v11 controls)
├── tests/                          21 pytest tests (Phase 0)
│
├── results/
│   ├── figures/, figures_v2/, figures_v3/   Per-paper-version figure caches
│   ├── phase1.{1..6}*/             Phase 1 per-stage JSONs + figures
│   ├── phase2.*/                   Phase 2 (chr17) outputs
│   ├── phase3_main/, phase3_ensemble/
│   ├── phase4/                     Cross-arch (4 models) summaries + per-model figures
│   ├── phase5/                     Q2 BED + enrichment table
│   ├── tier1_*, tier2_*/           Tier 1+2 extensions
│   ├── exp1_entropy/, exp1_entropy_meta.json   Entropy-decoupling control (v11)
│   ├── exp2_shuffled/, exp2_shuffled_meta.json Motif-flank perturbation (v11)
│   ├── _verification/              Independent CPU bundle verification
│   └── runs/, status/              Per-stage JSON logs (seeds, runtime, host info)
│
├── requirements.txt                Pinned packages (Phase 0 baseline)
├── requirements_phase1.lock.txt    88 pinned pip packages for Phase 1 (Evo 2)
├── env_setup.sh                    Idempotent env bootstrap (apt deps for Linux/CUDA)
└── 260426_연구계획서.docx           Original Korean research proposal (full project context)
```

Large data files (FASTA, GENCODE, ClinVar VCFs) and `.npz`/`.h5` analysis caches are NOT committed (regenerable from `scripts/`). Multi-GB hidden-state caches (e.g. `results/phase1.6/chr22_cache.h5`) live only on the H200 server; see [`ICML_0429_v3/MANIFEST.md`](ICML_0429_v3/MANIFEST.md) for the LOCAL/REMOTE split per figure.

## Quickstart

### Build the paper PDF (no GPU needed)

```bash
cd ICML_0429_v3
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

Self-contained build: TeX Live 2024+ with the included ICML 2026 style files.

### Reproduce Phase 0 (HyenaDNA, single RTX 3090, ~38 min)

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
python scripts/E5_tuned_lens.py                # Tuned-lens prototype
```

### Reproduce Phase 1+ (Evo 2 7B, H200 141 GB)

Phase 1 runs in two parallel tmux windows (~90 min wall clock). Pipeline + verifier orchestration:

```bash
cd phase1
python scripts/00_smoke_evo2.py                # Architectural facts (Appendix C)
bash scripts/run_phase1_chain.sh               # Stages 10 → 17 with per-stage verify_phase.py
```

For variant-level (Phase 3), cross-architecture (Phase 4), conservation (Phase 5), Tier 1+2 extensions, and v11 controls, see the per-script header comments and [`docs/findings/`](docs/findings/) for the matching write-ups.

### Regenerate paper figures

Local-only regen (no H200, schematics + cached summaries) and full real-data regen (H200) are both supported; see [`ICML_0429_v3/README.md`](ICML_0429_v3/README.md) and [`ICML_0429_v3/MANIFEST.md`](ICML_0429_v3/MANIFEST.md).

## Architecture facts (Phase 1 calibration)

- Loaded variant: `evo2_7b_base` (8K/32K context; FP8 1M variant blocked by TE 2.14 + torch 2.4 incompat)
- 32 blocks: attn=[3,10,17,24,31], hcs=[0,4,7,11,14,18,21,25,28], hcm=[1,5,8,12,15,19,22,26,29], hcl=[2,6,9,13,16,20,23,27,30]
- Tied head: storage + value tied (clone before perturbation)
- VRAM: 6 kb = 16.6 GB, 16 kb = 22.5 GB, 32 kb = 31.9 GB
- Smoke output → [`docs/decisions/phase1_appendix_c.md`](docs/decisions/phase1_appendix_c.md)

## Key references

- Chen, W.-L. et al. (2026). *Think Deep, Not Just Long: Measuring LLM Reasoning Effort via Deep-Thinking Tokens.* arXiv:2602.13517.
- Nguyen, E., Poli, M., Durrant, M.G. et al. (2026). *Evo 2: Whole-genome modeling with context-length scaling.* Nature.
- Nguyen, E. et al. (2023). *HyenaDNA: Long-Range Genomic Sequence Modeling at Single Nucleotide Resolution.* NeurIPS 2023.
- Belrose, N. et al. (2023). *Eliciting Latent Predictions from Transformers with the Tuned Lens.* arXiv:2303.08112.
- nostalgebraist (2020). *Interpreting GPT: the Logit Lens.* AI Alignment Forum.

## Reproducibility

- `seed=42` everywhere.
- HF revisions locked: HyenaDNA SHA `7ebf71773d22c0ede2cc55cb2be15ee8c289e1ce`; Evo 2 + cross-arch revisions in `phase1/MODEL_REVISIONS.txt`.
- Data versions: GRCh38 primary assembly, GENCODE v44, ClinVar 2026-04-18 (`phase1/DATA_VERSIONS.txt`).
- 88 pinned pip packages in `requirements_phase1.lock.txt`.
- Per-stage JSON sidecars (raw seeds, runtime, host info) at `results/runs/` and `results/status/`.

## Contact

For questions or collaboration: yoonjincho25@yonsei.ac.kr

---

*Phase 0 finalized 2026-04-26. Phase 1 (Evo 2 7B) finalized 2026-04-27. Two-paper split decided 2026-04-29. Paper 1 ICML workshop submission v11.6 built 2026-05-05.*
