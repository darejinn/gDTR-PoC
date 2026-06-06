# `scripts/` — figure regeneration catalog

Every script that produces a raster figure used in `gdtr_paper_ICML.tex`
lives here. Two execution domains:

- **Local** — runs on this Mac repository, no GPU, only reads JSON/CSV
  summaries vendored under `../results/`.
- **Remote (H200)** — runs on `digitalocean-gpu` (`~/gDTR/`), reads the
  multi-GB hidden-state caches.

For input/output paths and upstream pipelines, also see [`../MANIFEST.md`](../MANIFEST.md).

---

## Local regen scripts

### `make_fig1_panel_b_local.py`
- **Output.** `../figures/fig1_panel_b.{png,pdf}`
- **Renders.** Fig 1(b) example settling trajectories (schematic).
- **Inputs.** None (hard-coded raw splice/intron coordinates that match
  the manuscript's settling-trajectory definition: $D_{\cos}\!\approx\!1$
  at $\ell{=}1$, splice $c{=}22$, intron $c{=}31$).
- **Self-test.** Asserts `splice c = 22 (expected 22)` and
  `intron c = 31 (expected 31)` from `np.minimum.accumulate` over the
  raw curves. Runs as part of script.
- **Sync constraint.** The TikZ panel (b) inside
  `../figures/fig1_combined.tex` uses the same raw coordinates —
  edit BOTH if you change the example.

### `regen_fig_shallowness_local.py`
- **Output.** `../figures/fig_2_shallowness.{png,pdf}`
- **Renders.** Fig 2 — per-context mean settling depth (left panel) +
  Cohen's $d$ forest plot for splice donor / cCRE-ELS / GTEx eQTL /
  GWAS Catalog (right panel).
- **Inputs.** `../../results/figures_v3/fig_v9_meta.json` (compact summary;
  intron baseline, panel-b rows with d/p/n).
- **Title font.** Times New Roman.
- **Note.** Local-fast-path regen. The full per-position version (with
  Mann-Whitney resampling) lives at `make_v3_figures_remote.py::fig_shallowness`
  and needs the H200 caches.

### `regen_fig_variants_local.py`
- **Output.** `../figures/fig_3_variants.{png,pdf}`
- **Renders.** Fig 3 — variant consequence boxplot (summary form,
  median + box of fixed half-width).
- **Inputs.** `../../results/figures_v3/fig_v9_meta.json::variants`
  (per-class median, n, Kruskal-Wallis $p$).
- **Title.** Bold, fontsize 14, Times New Roman.

### `regen_fig_cross_arch_context_local.py`
- **Output.** `../figures/fig_A1_cross_arch_context.{png,pdf}`
- **Renders.** Fig A1 — per-context bars across four FMs
  (Evo 2 / HyenaDNA / NT-v2 / DNABERT-2), 1×4 small multiples.
- **Inputs.** `../../results/phase4/per_model_summary.json`.
- **Title font.** Times New Roman (per-panel + suptitle).

### `regen_fig_A2_cross_arch_two_tier_local.py`
- **Output.** `../figures/fig_A2_cross_arch_two_tier.{png,pdf}`
- **Renders.** Fig A2 — pairwise Spearman ρ heatmap (panel a) +
  two-tier card schematic (panel b).
- **Inputs.** `../../results/phase4/concordance_matrix.json`.
- **Title font.** Times New Roman.
- **Note.** Standalone local equivalent of
  `make_v3_figures_remote.py::fig_crossarch`, written for v4 so the
  appendix-A2 figure can rebuild without H200 access.

### `regen_fig_auroc_local.py`
- **Output.** `../figures/fig_A3_auroc.{png,pdf}`
- **Renders.** Fig A3 — variant AUROC four-panel diagnostic. (a) AUROC
  bars with 95% CI per method (stratified-10-fold and LOGO-CV);
  (b) DeLong paired comparisons; (c) per-layer single-tap AUROC (cos
  vs JSD); (d) leave-one-gene-out AUROC.
- **Inputs.** `../../results/tier1_baselines/baseline_auroc.json`,
  `../../results/tier1_per_layer/per_layer_auroc.csv`.
- **Title font.** Times New Roman (all four panel titles).
- **Note.** Panel (a) substitutes a bar chart for the original ROC
  curves because the raw per-variant scores are not vendored locally.
  Panels (b)-(d) match the paper exactly.

### `make_fig1_trajectory_local.py`
- **Output.** `../figures/fig1_trajectory.png` (cropped)
- **Renders.** Crop helper for the legacy v10 Fig 1(b) panel — kept
  for the v10/v11.0–v11.3 path that used a baked-in raster Fig 1(b).
- **Note.** v11.5 uses the TikZ-only Fig 1(b) inside
  `fig1_combined.tex` plus the Python schematic
  `make_fig1_panel_b_local.py`. This crop helper is no longer on the
  build path; kept for diff.

### `redraw_fig1_panel_a_local.py`
- **Output.** Legacy raster Fig 1(a)
- **Renders.** Pre-TikZ Fig 1(a) schema as a matplotlib raster.
- **Note.** Superseded by the TikZ source in
  `../figures/fig1_combined.tex`. Kept for diff/audit only.

---

## Remote (H200) regen script

### `make_v3_figures_remote.py`

Master figure generator that consumes the full H200 result tree.

```bash
ssh digitalocean-gpu
cd ~/gDTR
GDTR_ROOT=$PWD ./venv/bin/python scripts/make_v3_figures_remote.py
```

Outputs land at `../results/figures_v3_workshop/`:
- `fig1_v10.{png,pdf}` — Fig 1(b) real chr22 trajectories (real data,
  picked donor pos 10950055 c=22, intron pos 10940328 c=31; legacy v10
  asset, superseded by `fig_1_final.png` in v4)
- `fig_shallowness.{png,pdf}` — Fig 2 from full per-position arrays
  (upstream emits this name; copy back into `figures/` as
  `fig_2_shallowness.{png,pdf}` to swap into the v4 build)
- `fig_variants.{png,pdf}` — Fig 3 full per-variant boxplot (upstream
  name; copy back as `fig_3_variants.{png,pdf}`)
- `fig_crossarch.{png,pdf}` — Fig A2 (heatmap + two-tier schema;
  upstream name; copy back as `fig_A2_cross_arch_two_tier.{png,pdf}`)

Hidden-state caches required (all on H200, none in this repo):
- `results/phase1.6/chr22_cache.h5` — D_cos[12978, 32, 6000]
- `data/annotation/chr22_position_labels.npy` — context labels per bp
- `data/external/ccre_els_chr22.bed` — ENCODE cCRE-ELS chr22 entries
- `results/p1a/calib_val_table.csv`, `results/p1b/...`,
  `results/p2/variants_features_classed.csv`,
  `results/p2_indel/variants_features_indel.csv`,
  `results/p3b1/p3b1_func_pos.json`,
  `results/phase4/per_model_summary.json`

### Where Fig 5 is shared
`make_v3_figures_remote.py::fig_crossarch()` reads only
`results/phase4/concordance_matrix.json`, which IS vendored locally
(no caches needed). So Fig 5 can be regenerated locally too:

```bash
GDTR_ROOT=/Users/yoonjincho/Project/ICML python -c \
    "import sys; sys.path.insert(0,'scripts'); \
     from make_v3_figures_remote import setup_style, fig_crossarch; \
     setup_style(); fig_crossarch()"
```

(Output goes to `$GDTR_ROOT/results/figures_v3_workshop/`. To preview
only, run with `GDTR_ROOT=/tmp/gdtr_test`.)
