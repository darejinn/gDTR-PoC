# ICML_0429_v3 — Figure & Table Manifest

Single source of truth mapping every figure and table in
`gdtr_paper_ICML.tex` (v11.3) → the script that renders it → the upstream
analysis pipeline that produced its inputs → the on-disk artifacts the
script reads.

Two execution domains are referenced throughout:

- **LOCAL** — this Mac repository (`/Users/yoonjincho/Project/ICML/`).
  Contains `results/figures_v3/*` summary JSONs, `results/tier1_*` AUROC
  artifacts, `results/phase4/per_model_summary.json`,
  `results/phase1.6_sub/chr22_position_c.npy`, and the LaTeX build chain.
  Does **not** contain the multi-GB hidden-state caches
  (`chr22_cache.h5`), per-bp annotation labels
  (`data/annotation/chr22_position_labels.npy`), or the
  `results/p1a|p1b|p2|p2_indel|p3b1` directories.
- **REMOTE (H200)** — `digitalocean-gpu`, `~/gDTR/`. Contains
  Evo 2 weights, all hidden-state caches, and the full
  `results/<phase>/` tree referenced in Appendix~E of the paper.

Each row of the table below uses a one-letter location code:
`L` = local-only, `R` = remote-only (must run on H200), `B` = both.

---

## 1. Main-text figures

### Fig. 1 — gDTR pipeline schematic + chr22 example trajectories
- **TeX label.** `fig:schematic` (line 126 of `gdtr_paper_ICML.tex`).
- **Source.** `figures/fig1_combined.tex` (TikZ, single `tikzpicture`).
  `figures/fig1_schema.tex` is the panel-(a) source kept for diff;
  `figures/fig1_trajectory.png` is panel-(b) baked in by
  `\node[inner sep=0pt]{\includegraphics{...}}`.
- **Build domain.** Panel (a) is pure TikZ (rebuilds with `latexmk`).
  Panel (b) is a pre-rendered PNG; regen requires the H200.
- **Regen scripts.**
  - Remote (preferred): `scripts/make_v3_figures_remote.py` →
    `fig1()` writes `results/figures_v3_workshop/fig1_v10.{png,pdf}`.
  - Older equivalent on the H200: `scripts/make_fig_v10_fig1.py`
    (the v10 build, kept for reference; same outputs path
    `results/figures_v3/fig1_v10.{png,pdf}`).
  - Local crop helper: `scripts/make_fig1_trajectory_local.py`
    (extracts panel (b) from a rendered v10 PNG).
- **Upstream pipeline.**
  1. `scripts/16_phase1_6_chr22_forward.py` → `results/phase1.6/chr22_cache.h5`
  2. `scripts/16c_phase1_6_gate_b_sub.py` → `results/phase1.6_sub/chr22_position_c.npy`
  3. `scripts/p1a_calib_val_split.py` → `results/p1a/calib_val_table.csv`
  4. `scripts/p3b1_functional_positive_control.py` → `results/p3b1/p3b1_func_pos.json`
- **Input artifacts read by the figure script.**

  | path | status |
  |---|---|
  | `results/phase1.6/chr22_cache.h5` (D_cos[12978, 32, 6000]) | R |
  | `data/annotation/chr22_position_labels.npy` | R |
  | `results/p1a/calib_val_table.csv` | R |
  | `results/p3b1/p3b1_func_pos.json` | R |
- **Numerical sanity record.**
  `results/figures_v3/fig1_v10_meta.json` (donor pos 10 950 055,
  c=22; intron pos 10 940 328, c=31; pooled hierarchy values).

### Fig. 2 — Splice / cCRE shallowness (`fig:shallowness`)
- **Output.** `figures/fig_shallowness.{png,pdf}`.
- **Regen scripts.**
  - Remote: `scripts/make_v3_figures_remote.py::fig_shallowness()`.
  - Local (rebuilds from cached summary): `scripts/regen_fig_shallowness_local.py`.
    Reads only `../results/figures_v3/fig_v9_meta.json` (≈4 kB) — works
    completely offline. **This is the canonical local regen path.**
- **Build domain.** B (local-only fast path is supported).
- **Upstream pipeline.**
  1. `scripts/16c_phase1_6_gate_b_sub.py` → `chr22_position_c.npy`
  2. `scripts/p1a_calib_val_split.py` → `calib_val_table.csv`
  3. `scripts/p3b1_functional_positive_control.py` → `p3b1_func_pos.json`
  4. `scripts/make_fig_v9.py` → `results/figures_v3/fig_v9_meta.json`
     (the cached summary that the local regen consumes)
- **Input artifacts.**

  | path | status |
  |---|---|
  | `results/figures_v3/fig_v9_meta.json` | L |
  | `results/p1a/calib_val_table.csv` | R |
  | `results/p3b1/p3b1_func_pos.json` | R |
  | `results/phase1.6_sub/chr22_position_c.npy` (CIs only) | L |
  | `data/annotation/chr22_position_labels.npy` | R |
  | `data/external/ccre_els_chr22.bed` | R |

### Fig. 3 — Variant consequence depth boxplot (`fig:variants`)
- **Output.** `figures/fig_variants.{png,pdf}`.
- **Regen.**
  - Remote (full per-variant distribution):
    `scripts/make_v3_figures_remote.py::fig_variants()`.
  - Local (median + n + p-value summary):
    `scripts/regen_fig_variants_local.py` →
    `figures/fig_variants_local.{png,pdf}`. Reads only
    `../results/figures_v3/fig_v9_meta.json::variants`.
- **Build domain.** B (the local script renders an information-equivalent
  summary; it does not replicate the per-variant whisker shape).
- **Upstream pipeline.**
  1. `scripts/prep_clinvar_15gene.py` → ClinVar 15-gene cohort
  2. `scripts/p2_snv_class_join.py` → `results/p2/variants_features_classed.csv`
  3. `scripts/p2_indel_select.py` + `scripts/p2_indel_forward.py` →
     `results/p2_indel/variants_features_indel.csv`
- **Input artifacts.**

  | path | status |
  |---|---|
  | `results/p2/variants_features_classed.csv` | R |
  | `results/p2_indel/variants_features_indel.csv` | R |

---

## 2. Appendix figures

### Fig. 4 — Per-context bars across four FMs (`fig:cross-arch-context`)
- **Output.** `figures/fig_appendix_b.png` (carried over from v9 commit
  `e5c8617`); local regen → `figures/fig_appendix_b_local.{png,pdf}`.
- **Regen.** `scripts/regen_fig_appendix_b_local.py` renders a 1×4
  small-multiples bar chart from
  `../results/phase4/per_model_summary.json`. Runs entirely locally.
- **Upstream pipeline.**
  1. `scripts/40_phase4_hyenadna_large.py`, `41_phase4_nt_v2.py`,
     `42_phase4_dnabert2.py` (per-model forward passes)
  2. `scripts/43_phase4_concordance.py` → `concordance_matrix.json`,
     `per_model_summary.json`
- **Input artifact.** `results/phase4/per_model_summary.json` (L).

### Fig. 5 — Cross-architecture two-tier (`fig:cross-arch`)
- **Output.** `figures/fig_crossarch.{png,pdf}`.
- **Regen.** `scripts/make_v3_figures_remote.py::fig_crossarch()`.
  Hard-codes the locked 4×4 ρ matrix (matches
  `results/phase4/concordance_matrix.json`).
- **Upstream pipeline.** Same as Fig. 4 (`43_phase4_concordance.py`).
- **Input artifact.** `results/phase4/concordance_matrix.json` (L).
- **Build domain.** B — also runs locally because the script does not
  open any large cache.

### Fig. 6 — Variant AUROC four-panel diagnostic (`fig:auroc`)
- **Output.** `figures/fig_auroc.png` (carried over from v9 commit
  `e5c8617`); local regen → `figures/fig_auroc_local.{png,pdf}`.
- **Regen.** `scripts/regen_fig_auroc_local.py` renders all four panels
  from the Tier-1 baseline JSON / per-layer CSV vendored in this repo.
  Runs entirely locally. The original v9 PNG draws raw ROC curves in
  panel (a); the local regen replaces it with an information-equivalent
  AUROC bar chart (the per-variant scores needed for raw ROC are not
  vendored). Panels (b)–(d) match the paper exactly.
  An older script `scripts/figures/F4.py` writes a related 2-panel
  baseline figure into `results/figures_v2/F4_baselines.{png,pdf}` from
  the same JSON.
- **Upstream pipeline.**
  1. `scripts/45_t12_delta_h.py`, `46_t12_rollout.py`, `47_t12_ig.py` →
     baseline feature CSVs
  2. `scripts/48_t12_compare_pipeline.py` →
     `results/tier1_baselines/baseline_auroc.json`,
     `delong_pairs.csv`, `baseline_spearman.csv`
  3. `scripts/40_t11_per_layer_ablation.py` →
     `results/tier1_per_layer/per_layer_auroc.csv`,
     `summary.json`
  4. `scripts/41_t14_bootstrap.py` →
     `results/tier1_bootstrap/auroc_distributions.csv`,
     `summary.json`
- **Input artifacts (all local).**

  | path |
  |---|
  | `results/tier1_baselines/baseline_auroc.json` |
  | `results/tier1_baselines/baseline_spearman.csv` |
  | `results/tier1_baselines/delong_pairs.csv` |
  | `results/tier1_per_layer/per_layer_auroc.csv` |
  | `results/tier1_per_layer/summary.json` |
  | `results/tier1_bootstrap/summary.json` |

---

## 3. Tables

| TeX label | Caption topic | Source of numbers | Hardcoded? |
|---|---|---|---|
| `tab:cross-arch-summary` | Causal-LM vs MLM matrix (yes/no) | summary of §3.4 + Phase 4 | yes (qualitative) |
| `tab:idle-block` | Evo 2 idle final block evidence | Phase 1.4 calibration / sanity | yes (5 measured constants) |
| `tab:gamma-sweep` | (γ_cos, ρ) plateau values | `results/phase1.5/hp_sweep.csv` | yes (transcribed from CSV) |
| `tab:tuned-lens` | Tuned-lens MSE recovery | `results/phase1.followup_full/recovery_curve.json` | yes (5 representative layers) |
| `tab:fm-specs` | Architectures + γ_q70 + tokens/window | `results/phase4/per_model_summary.json` + `_*_ckpt.json` | yes |
| `tab:cross-arch-context` | Per-context $\bar c$ for 4 models | `results/phase4/per_model_summary.json::splice_signal.data` | yes (transcribed) |
| `tab:cross-arch-rho` | 4×4 Spearman ρ | `results/phase4/concordance_matrix.json` | yes (transcribed) |
| `tab:auroc` | AUROC + 95% CI | `results/tier1_baselines/baseline_auroc.json` + `auroc_distributions.csv` | yes |
| `tab:per-layer` | Per-layer AUROC at 9 taps | `results/tier1_per_layer/per_layer_auroc.csv` | yes |

All tables are **manually transcribed** from the JSON/CSV files listed
above — none are programmatically generated at LaTeX-build time. Any
re-run of the upstream pipeline therefore requires hand-syncing those
numbers back into `gdtr_paper_ICML.tex`. The CSV/JSON files are the
authoritative source.

---

## 4. Local vs. remote regeneration cheat-sheet

```
                                          Local script                    Remote script
────────────────────────────────────────────────────────────────────────────────────────
Fig. 1(a) — TikZ pipeline schema     figures/fig1_combined.tex                —
Fig. 1(b) — chr22 trajectories       scripts/make_fig1_trajectory_local.py    make_v3_figures_remote.py::fig1
Fig. 2  — shallowness                scripts/regen_fig_shallowness_local.py   make_v3_figures_remote.py::fig_shallowness
Fig. 3  — variant boxplot            scripts/regen_fig_variants_local.py      make_v3_figures_remote.py::fig_variants
Fig. 4  — per-context 4-FM bars      scripts/regen_fig_appendix_b_local.py    —
Fig. 5  — cross-arch two-tier        make_v3_figures_remote.py::fig_crossarch make_v3_figures_remote.py::fig_crossarch
Fig. 6  — variant AUROC              scripts/regen_fig_auroc_local.py         —
LaTeX build                          latexmk -pdf gdtr_paper_ICML.tex          —
```

Local regen scripts only need the JSONs/CSVs vendored under
`../results/`; nothing more. Remote regen of Figs. 1(b), 2, 3 reproduces
the full per-position distributions from the H200 caches. The local
fallbacks render information-equivalent summaries (median+n+CI rather
than raw distributions for Fig. 3 and Fig. 6 panel (a)).

---

## 5. One-shot reproduction commands

### Local (Mac, no GPU required)

```bash
cd /Users/yoonjincho/Project/ICML/ICML_0429_v3

# Five rasters that can be rebuilt locally:
python scripts/regen_fig_shallowness_local.py   # Fig 2
python scripts/regen_fig_variants_local.py      # Fig 3 (summary form)
python scripts/regen_fig_appendix_b_local.py    # Fig 4
python scripts/regen_fig_auroc_local.py         # Fig 6
python scripts/make_fig1_trajectory_local.py    # Fig 1(b) crop helper

# Final PDF (Fig 1(a) is pure TikZ; Fig 5 stays as the cached PNG):
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

### Remote (H200, full feature regen)

```bash
ssh digitalocean-gpu
cd ~/gDTR
GDTR_ROOT=$PWD ./venv/bin/python scripts/make_v3_figures_remote.py
# → results/figures_v3_workshop/{fig1_v10,fig_shallowness,fig_variants,fig_crossarch}.{png,pdf}

# Sync regenerated figures back to the laptop's ICML_0429_v3/figures/
rsync -avz digitalocean-gpu:~/gDTR/results/figures_v3_workshop/ \
            /Users/yoonjincho/Project/ICML/ICML_0429_v3/figures/
```

## 6. Legacy figures kept for diff (not referenced by the current TeX)

These PNGs/PDFs exist under `figures/` but are **not** included by
`gdtr_paper_ICML.tex` v11.3 — they trace back to earlier v8/v9/v10
builds. Kept intentionally so a reviewer / future-you can diff against
the current versions; safe to delete if the v3 folder needs to slim
down.

| File | Provenance |
|---|---|
| `fig_disruption.png` | v8 — predecessor of `fig_variants` |
| `fig_funcshallow.png` | v8 — merged into `fig_shallowness` |
| `fig_splice.png` | v8 — merged into `fig_shallowness` |
| `fig_q2.png` | v8 — Q2 conservation panel, dropped in v11 |
| `fig_schematic.png` | v9 — schematic raster, replaced by `fig1_combined.tex` |
| `fig_variants_full_v1.png` | v10 — earlier 6-class variant boxplot |
| `fig1_v10.{png,pdf}` | v10 — 2×2 master Fig 1 (now split into 1(a) TikZ + 1(b) crop) |
| `fig1_v10_source_with_panel_b.png` | v10 — intermediate raster for crop |
| `fig2_v11.png` | v11 — early "centerpiece" attempt, replaced by `fig_shallowness` |

The `gdtr_paper_all_sources/` subdirectory is the v1 source backup kept
for diff and is also not part of the v3 build chain.

---

### Note on the shipped PNGs

`figures/fig_appendix_b.png` and `figures/fig_auroc.png` are the v9
artwork still cited by the LaTeX build. The local regen scripts emit
`*_local.{png,pdf}` to make the regen explicit and avoid silently
mutating the shipped figures. To switch the LaTeX build to the local
regens, replace the `\includegraphics{...}` paths in
`gdtr_paper_ICML.tex` (lines 507 and 629).
