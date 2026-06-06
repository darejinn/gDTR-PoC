# ICML_0509_v4 — Figure & Table Manifest

Single source of truth mapping every figure and table in
`gdtr_paper_ICML.tex` (v11.6 + 0509 corrections, see
[`corrections_applied.md`](corrections_applied.md)) → the script that
renders it → the upstream analysis pipeline that produced its inputs →
the on-disk artifacts the script reads.

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

**v4 changes vs v3:**
1. **Positional figure file names.** Every figure file is now prefixed
   with its position in the rendered PDF: main-text figures are
   `fig_1_*.png`, `fig_2_*.png`, `fig_3_*.png`; appendix figures are
   `fig_A1_*.png` … `fig_A4_*.png`. Old non-positional files removed
   (originals preserved in `../ICML_0429_v3/figures/`).
2. **Appendix A-prefixed numbering.** `\renewcommand{\thefigure}{A\arabic{figure}}`
   and the matching `\thetable` redefinition (with counter resets) added
   right after `\appendix`, so appendix figures/tables print as
   Fig A1–A4 and Tab A1–A12 while the main text stays Fig 1–3, Tab 1.
3. **Fig 1 swap.** The v11.5/v11.6 TikZ source `fig1_combined.tex`
   (two-trajectory example $c\!=\!22 / c\!=\!31$) was replaced by an
   externally-authored single-panel raster `fig_1_final.png` (worked
   example $c(t)\!=\!30$). LaTeX trims top/bottom whitespace via the
   `trim={0 35 0 55}` includegraphics option (PNG itself preserved).
4. **Times-New-Roman titles.** Every regen-script title (Fig 2, 3, A1,
   A2, A3) now sets `fontfamily="Times New Roman"` on `set_title(...)` /
   `suptitle(...)`. Fig A4 is copied from upstream and inherits the
   upstream title font.
5. **New local script for Fig A2.** `scripts/regen_fig_A2_cross_arch_two_tier_local.py`
   mirrors the `make_v3_figures_remote.py::fig_crossarch` logic so the
   appendix figure can rebuild locally without H200 access.

---

## 1. Main-text figures

### Fig. 1 — gDTR pipeline schematic (single-panel worked example, $c(t)\!=\!30$)

| Field | Value |
|---|---|
| **TeX label** | `fig:schematic` |
| **TeX include** | `\includegraphics{figures/fig_1_final.png}` *(v4: replaces the v3 TikZ `\input{figures/fig1_combined.tex}`)* |
| **Output file** | `figures/fig_1_final.png` (rasterised externally, e.g. Keynote / draw.io / Figma) |
| **Re-edit path** | edit the source design file → re-export PNG → drop in over `figures/fig_1_final.png` |
| **Build domain** | self-contained raster (no script regen) |
| **Legacy assets retained for diff** | `figures/fig1_combined.tex` (TikZ source for v11.5/v11.6 Fig 1 with the $c\!=\!22 / c\!=\!31$ two-trajectory example), `figures/fig1_panel_b.{png,pdf}`, `figures/fig1_schema.tex`, `figures/fig1_trajectory.{png,tex}`, `figures/fig1_v10*.{png,pdf}` — none on the v4 build path |
| **Legacy regen scripts** | `scripts/make_fig1_panel_b_local.py`, `scripts/make_fig1_trajectory_local.py`, `scripts/redraw_fig1_panel_a_local.py`, and `scripts/make_v3_figures_remote.py::fig1` — all kept for diff; not invoked by the v4 build chain |

The new schematic walks through the algorithm pipeline end-to-end:
residual-stream states $h_\ell(t)$ (rows: layers 1..32) → cosine UR
lens applied per layer → $\Dcos(\ell)\!=\!1\!-\!\cos(h_L, h_\ell)$ to
the final layer ($L\!=\!32$) → running minimum $m_\ell$ → threshold
check $m_\ell(t)\!\le\!\gamma$ → settling depth $c(t)\!=\!30$ in the
worked example. The crossed-out arrow on the layer-31 row marks the
running-minimum step that refuses to increase: layer~30 carries the
smaller value forward.

### Fig. 2 — Splice / cCRE shallowness

| Field | Value |
|---|---|
| **TeX label** | `fig:shallowness` (prints as **Figure 2**) |
| **TeX include** | `\includegraphics{figures/fig_2_shallowness.png}` |
| **Output files** | `figures/fig_2_shallowness.{png,pdf}` |
| **Local regen** | `scripts/regen_fig_shallowness_local.py` (canonical local path; reads `results/figures_v3/fig_v9_meta.json`, ≈4 kB; titles in Times New Roman) |
| **Remote regen** | `scripts/make_v3_figures_remote.py::fig_shallowness` (full per-position arrays + Mann–Whitney resampling on H200; emits `fig_shallowness.*` upstream — rename to `fig_2_shallowness.*` when copying back) |
| **Build domain** | B |

**Upstream pipeline.**
1. `scripts/16c_phase1_6_gate_b_sub.py` → `chr22_position_c.npy`
2. `scripts/p1a_calib_val_split.py` → `calib_val_table.csv`
3. `scripts/p3b1_functional_positive_control.py` → `p3b1_func_pos.json`
4. `scripts/make_fig_v9.py` → `results/figures_v3/fig_v9_meta.json` (cached summary consumed by the local regen)

**Input artefacts.**

| path | status |
|---|---|
| `results/figures_v3/fig_v9_meta.json` | L |
| `results/p1a/calib_val_table.csv` | R |
| `results/p3b1/p3b1_func_pos.json` | R |
| `results/phase1.6_sub/chr22_position_c.npy` (CIs only) | L |
| `data/annotation/chr22_position_labels.npy` | R |
| `data/external/ccre_els_chr22.bed` | R |

### Fig. 3 — Variant consequence depth boxplot

| Field | Value |
|---|---|
| **TeX label** | `fig:variants` (prints as **Figure 3**) |
| **TeX include** | `\includegraphics{figures/fig_3_variants.png}` |
| **Output files (local summary)** | `figures/fig_3_variants.{png,pdf}` |
| **Local regen** | `scripts/regen_fig_variants_local.py` (median + n + p-value summary; reads `results/figures_v3/fig_v9_meta.json::variants`; title in Times New Roman) |
| **Remote regen** | `scripts/make_v3_figures_remote.py::fig_variants` (full per-variant whisker shape; emits `fig_variants.*` upstream — rename to `fig_3_variants.*` when copying back) |
| **Build domain** | B (the local script renders an information-equivalent summary) |

**Upstream pipeline.**
1. `scripts/prep_clinvar_15gene.py` → ClinVar 15-gene cohort
2. `scripts/p2_snv_class_join.py` → `results/p2/variants_features_classed.csv`
3. `scripts/p2_indel_select.py` + `scripts/p2_indel_forward.py` → `results/p2_indel/variants_features_indel.csv`

**Input artefacts.**

| path | status |
|---|---|
| `results/p2/variants_features_classed.csv` | R |
| `results/p2_indel/variants_features_indel.csv` | R |

---

## 2. Appendix figures

### Fig. A1 — Per-context bars across four FMs

| Field | Value |
|---|---|
| **TeX label** | `fig:cross-arch-context` (prints as **Figure A1**) |
| **TeX include** | `\includegraphics{figures/fig_A1_cross_arch_context.png}` |
| **Output files** | `figures/fig_A1_cross_arch_context.{png,pdf}` |
| **Local regen** | `scripts/regen_fig_cross_arch_context_local.py` (titles + suptitle in Times New Roman) |
| **Build domain** | L |
| **Renders** | 1×4 small-multiples bar chart of $\bar c$ per context, one panel per model (Evo 2, HyenaDNA-large, NT-v2, DNABERT-2). |

**Upstream pipeline.**
1. `scripts/40_phase4_hyenadna_large.py`, `41_phase4_nt_v2.py`, `42_phase4_dnabert2.py` (per-model forward passes)
2. `scripts/43_phase4_concordance.py` → `concordance_matrix.json`, `per_model_summary.json`

**Input artefact.** `results/phase4/per_model_summary.json` (L).

### Fig. A2 — Cross-architecture two-tier

| Field | Value |
|---|---|
| **TeX label** | `fig:cross-arch` (prints as **Figure A2**) |
| **TeX include** | `\includegraphics{figures/fig_A2_cross_arch_two_tier.png}` |
| **Output files** | `figures/fig_A2_cross_arch_two_tier.{png,pdf}` |
| **Local regen** | `scripts/regen_fig_A2_cross_arch_two_tier_local.py` (standalone equivalent of the upstream `fig_crossarch` function, with Times-titled panels) |
| **Remote regen** | `scripts/make_v3_figures_remote.py::fig_crossarch` (legacy upstream entry point; emits `fig_crossarch.*` — rename to `fig_A2_cross_arch_two_tier.*` if copying back) |
| **Build domain** | B (the local script reads only the vendored `concordance_matrix.json`) |
| **Renders** | Pairwise Spearman ρ heatmap + two-tier schema (within-family +ρ block-diagonal vs cross-family weakly-negative). |

**Upstream pipeline.** Same as Fig. 4 (`43_phase4_concordance.py`).

**Input artefact.** `results/phase4/concordance_matrix.json` (L).

### Fig. A3 — Variant AUROC four-panel diagnostic

| Field | Value |
|---|---|
| **TeX label** | `fig:auroc` (prints as **Figure A3**) |
| **TeX include** | `\includegraphics{figures/fig_A3_auroc.png}` |
| **Output files** | `figures/fig_A3_auroc.{png,pdf}` |
| **Local regen** | `scripts/regen_fig_auroc_local.py` (all four panel titles in Times New Roman) |
| **Build domain** | L |
| **Renders** | (a) AUROC bars 95% CI, (b) Paired-DeLong significance, (c) per-layer single-tap AUROC (cosine vs JSD), (d) leave-one-gene-out AUROC. |
| **Notes** | Panel (a) of the local regen substitutes a bar chart for the original ROC curves (per-variant scores not vendored locally); panels (b)–(d) match the paper exactly. |

**Upstream pipeline.**
1. `scripts/45_t12_delta_h.py`, `46_t12_rollout.py`, `47_t12_ig.py` → baseline feature CSVs
2. `scripts/48_t12_compare_pipeline.py` → `results/tier1_baselines/baseline_auroc.json`, `delong_pairs.csv`, `baseline_spearman.csv`
3. `scripts/40_t11_per_layer_ablation.py` → `results/tier1_per_layer/per_layer_auroc.csv`, `summary.json`
4. `scripts/41_t14_bootstrap.py` → `results/tier1_bootstrap/auroc_distributions.csv`, `summary.json`

**Input artefacts (all local).**

| path |
|---|
| `results/tier1_baselines/baseline_auroc.json` |
| `results/tier1_baselines/baseline_spearman.csv` |
| `results/tier1_baselines/delong_pairs.csv` |
| `results/tier1_per_layer/per_layer_auroc.csv` |
| `results/tier1_per_layer/summary.json` |
| `results/tier1_bootstrap/summary.json` |

### Fig. A4 — Splice positional fine-profile

| Field | Value |
|---|---|
| **TeX label** | `fig:splice-fine` (prints as **Figure A4**) |
| **TeX include** | `\includegraphics{figures/fig_A4_splice_fine.png}` |
| **Output files** | `figures/fig_A4_splice_fine.{png,pdf}` |
| **Provenance** | Copied from `results/phase1.6_sub/F_splice_distance_profile.{png,pdf}` (rendered upstream during phase 1.6 sub-analysis; not regenerated by any script in `scripts/`) |
| **Build domain** | R (rasters are vendored; pipeline lives on the H200) |
| **Title font** | Inherited from upstream render (the only figure whose title font is not Times New Roman; regenerate upstream and copy back if camera-ready needs full consistency) |

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
| `tab:entropy-decoup` | Per-context Spearman ρ(c, H_t) | `results/figures_v3/fig_v9_meta.json::entropy_decoup` | yes (transcribed) |
| `tab:splice-fine` | Per-side minima of splice fine-profile | `results/phase1.6_sub/splice_distance_profile.json` | yes (transcribed) |
| `tab:splice-canonical` | Donor motif breakdown | `results/phase1.6_sub/splice_canonical_breakdown.json` | yes (transcribed) |
| `tab:motif-flank` | Motif-edit vs flank-shuffle | `results/exp2_shuffled_meta.json` | yes |

All tables are **manually transcribed** from the JSON/CSV files listed
above — none are programmatically generated at LaTeX-build time. Any
re-run of the upstream pipeline therefore requires hand-syncing those
numbers back into `gdtr_paper_ICML.tex`. The CSV/JSON files are the
authoritative source.

---

## 4. Local vs. remote regeneration cheat-sheet

```
                                          Local script                                 Remote script
────────────────────────────────────────────────────────────────────────────────────────────────────
Fig. 1   — pipeline schematic            figures/fig_1_final.png (raster; edit upstream)         —
Fig. 2   — shallowness                   scripts/regen_fig_shallowness_local.py                  make_v3_figures_remote.py::fig_shallowness
Fig. 3   — variant boxplot               scripts/regen_fig_variants_local.py                     make_v3_figures_remote.py::fig_variants
Fig. A1  — per-context 4-FM bars         scripts/regen_fig_cross_arch_context_local.py           —
Fig. A2  — cross-arch two-tier           scripts/regen_fig_A2_cross_arch_two_tier_local.py       make_v3_figures_remote.py::fig_crossarch
Fig. A3  — variant AUROC                 scripts/regen_fig_auroc_local.py                        —
Fig. A4  — splice fine-profile           figures/fig_A4_splice_fine.png (vendored; upstream)     phase1.6_sub
LaTeX build                              latexmk -pdf gdtr_paper_ICML.tex                        —
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
cd /Users/yoonjincho/Project/ICML/ICML_0509_v4

# Five rasters that can be rebuilt locally:
python scripts/regen_fig_shallowness_local.py            # Fig 2
python scripts/regen_fig_variants_local.py               # Fig 3 (summary form)
python scripts/regen_fig_cross_arch_context_local.py     # Fig 4 (renamed in v4)
python scripts/regen_fig_auroc_local.py                  # Fig 6
# Fig 1 (figures/fig_1_final.png) is a raster authored externally — no script regen.

# Final PDF (Fig 1 is a self-contained PNG; Fig 5 stays as the cached PNG):
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

### Remote (H200, full feature regen)

```bash
ssh digitalocean-gpu
cd ~/gDTR
GDTR_ROOT=$PWD ./venv/bin/python scripts/make_v3_figures_remote.py
# → results/figures_v3_workshop/{fig1_v10,fig_shallowness,fig_variants,fig_crossarch}.{png,pdf}

# Sync regenerated figures back to the laptop's ICML_0509_v4/figures/
rsync -avz digitalocean-gpu:~/gDTR/results/figures_v3_workshop/ \
            /Users/yoonjincho/Project/ICML/ICML_0509_v4/figures/
```

## 6. Legacy figures kept for diff (not referenced by the current TeX)

These PNGs/PDFs exist under `figures/` but are **not** included by
`gdtr_paper_ICML.tex` v4 — they trace back to earlier v8/v9/v10 builds.
Kept intentionally so a reviewer / future-you can diff against the
current versions; safe to delete if the v4 folder needs to slim down.

| File | Provenance |
|---|---|
| `fig_disruption.png` | v8 — predecessor of `fig_variants` |
| `fig_funcshallow.png` | v8 — merged into `fig_shallowness` |
| `fig_splice.png` | v8 — merged into `fig_shallowness` |
| `fig_q2.png` | v8 — Q2 conservation panel, dropped in v11 |
| `fig_schematic.png` | v9 — schematic raster, replaced by `fig1_combined.tex` |
| `fig_variants_full_v1.png` | v10 — earlier 6-class variant boxplot |
| `fig1_v10.{png,pdf}` | v10 — 2×2 master Fig 1 (now split into 1(a) TikZ + 1(b) panel_b) |
| `fig1_v10_source_with_panel_b.png` | v10 — intermediate raster for crop |
| `fig2_v11.png` | v11 — early "centerpiece" attempt, replaced by `fig_shallowness` |

The `gdtr_paper_all_sources/` subdirectory is the v1 source backup kept
for diff and is also not part of the v4 build chain.

---

### Note on the shipped PNGs (v4)

In v4 the shipped figures are the local-regen Times-titled outputs
themselves: every appendix figure that has a regen script
(`fig_A1_cross_arch_context.png`, `fig_A2_cross_arch_two_tier.png`,
`fig_A3_auroc.png`) is the file the LaTeX build includes; there is no
parallel `_local` copy. The previous v9-shipped versions
(`fig_cross_arch_context.png`, `fig_auroc.png` carried over from
commit `e5c8617`) were retired when the local regen acquired
Times-titled panels. They are recoverable from
`../ICML_0429_v3/figures/` if needed for diff.
