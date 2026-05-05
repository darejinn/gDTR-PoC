# ICML 2026 workshop short paper — gDTR (v11.5, 2026-05-05)

> **Title.** gDTR: Layer-wise Settling Depth Reveals Biological Grammar
> in Genomic Foundation Models.
> **Length.** 4-page main body + references + 9-page appendix
> (= 13 pages total).
> **Status.** Canonical ICML 2026 workshop submission, Paper 1 of the
> two-paper split.

This folder is self-contained for the LaTeX build; figure regeneration
is described below and in detail in [`MANIFEST.md`](MANIFEST.md).

---

## Quick start

### Build the PDF

```bash
cd ICML_0429_v3
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

Self-contained build: TeX Live 2024+ with `pdftex`, the included ICML
2026 style files, and standard packages (`microtype`, `graphicx`,
`subcaption`, `booktabs`, `siunitx`, `tikz`, `afterpage`, `hyperref`,
`cleveref`). No model weights or internet required for the build.

### Regenerate every figure locally (no GPU)

```bash
python scripts/make_fig1_panel_b_local.py    # Fig 1(b) — schematic trajectories
python scripts/regen_fig_shallowness_local.py # Fig 2 — splice/cCRE shallowness
python scripts/regen_fig_variants_local.py    # Fig 3 — variant boxplot summary
python scripts/regen_fig_appendix_b_local.py  # Fig 4 — per-context FM bars
python scripts/regen_fig_auroc_local.py       # Fig 6 — variant AUROC panels
```

Fig 1(a) is pure TikZ (rebuilds with `latexmk`). Fig 5 reads only the
locally-vendored `phase4/concordance_matrix.json` and rebuilds via
`make_v3_figures_remote.py::fig_crossarch()` — works without H200.

### Regenerate from real per-position data (H200 only)

```bash
ssh digitalocean-gpu
cd ~/gDTR
GDTR_ROOT=$PWD ./venv/bin/python scripts/make_v3_figures_remote.py
# → results/figures_v3_workshop/{fig1_v10,fig_shallowness,fig_variants,fig_crossarch}.{png,pdf}
rsync -avz digitalocean-gpu:~/gDTR/results/figures_v3_workshop/ figures/
```

---

## "Where is the code that produced X?"

| Output (in PDF) | Render script | Upstream pipeline |
|---|---|---|
| Fig 1(a) pipeline schema | [`figures/fig1_combined.tex`](figures/fig1_combined.tex) (TikZ) | — |
| Fig 1(b) example trajectories | [`scripts/make_fig1_panel_b_local.py`](scripts/make_fig1_panel_b_local.py) (schematic) / [`scripts/make_v3_figures_remote.py::fig1`](scripts/make_v3_figures_remote.py) (real, H200) | `phase1.6/chr22_cache.h5` (H200) |
| Fig 2 splice/cCRE shallowness | [`scripts/regen_fig_shallowness_local.py`](scripts/regen_fig_shallowness_local.py) | `p1a/calib_val_table.csv`, `p3b1/p3b1_func_pos.json` |
| Fig 3 variant boxplot | [`scripts/regen_fig_variants_local.py`](scripts/regen_fig_variants_local.py) (summary) / [`make_v3_figures_remote.py::fig_variants`](scripts/make_v3_figures_remote.py) (full) | `p2/variants_features_classed.csv`, `p2_indel/variants_features_indel.csv` |
| Fig 4 per-context FM bars | [`scripts/regen_fig_appendix_b_local.py`](scripts/regen_fig_appendix_b_local.py) | `phase4/per_model_summary.json` |
| Fig 5 cross-arch two-tier | [`scripts/make_v3_figures_remote.py::fig_crossarch`](scripts/make_v3_figures_remote.py) | `phase4/concordance_matrix.json` |
| Fig 6 variant AUROC | [`scripts/regen_fig_auroc_local.py`](scripts/regen_fig_auroc_local.py) | `tier1_baselines/baseline_auroc.json`, `tier1_per_layer/per_layer_auroc.csv` |
| Fig (App.D.1) splice fine-profile | rendered PDF copied: `figures/fig_splice_fine.{pdf,png}` | `phase1.6_sub/F_splice_distance_profile.{pdf,png}` |

For per-table data sources and the local-vs-H200 split, see
[`MANIFEST.md`](MANIFEST.md).

For a script catalog with inputs/outputs, see [`scripts/README.md`](scripts/README.md).

For figure provenance per file, see [`figures/README.md`](figures/README.md).

---

## Honest disclosure: Fig 1(b)

The Fig 1(b) trajectories shown in the PDF are **schematic** (synthetic
curves designed to satisfy the manuscript's settling-trajectory
definition: $D_{\cos}(\ell{=}1)\!\approx\!1$, run-min is the actual
running minimum of raw, splice $c{=}22$ and intron $c{=}31$). The
underlying real per-layer cache (`phase1.6/chr22_cache.h5`,
$\sim\!4{-}8$\,GB) lives only on the H200 and is not vendored.

To swap in the real trajectories, run `make_v3_figures_remote.py` on
the H200 and copy `fig1_v10.png` over `figures/fig1_panel_b.png`. The
TikZ panel (`figures/fig1_combined.tex`) hard-codes the schematic
coordinates; for the real-data version you would either:

1. Set `\includegraphics{figures/fig1_v10.png}` (synced from H200) and
   delete the TikZ panel-(b) block, OR
2. Have H200 dump the two 32-vectors as a tiny NPZ
   (`fig1b_real_traj.npz`) and edit both `make_fig1_panel_b_local.py`
   and `fig1_combined.tex` to read from it.

The current panel (b) caption already reads "Two chr22 example
trajectories" — verify against the real data before camera-ready.

---

## Top-level file map

```
ICML_0429_v3/
├── README.md                       ← you are here
├── MANIFEST.md                     ← per-figure / per-table source-of-truth
├── V3_REWRITE_NOTES.md             ← v1 → v3 narrative restructure log
│
├── gdtr_paper_ICML.tex             ← main LaTeX source (single file)
├── gdtr_paper_ICML.pdf             ← built PDF (13 pages)
├── gdtr_paper.bib                  ← bibliography
│
├── icml2026.sty / icml2026.bst     ← ICML 2026 style (do not modify)
├── algorithm.sty / algorithmic.sty / fancyhdr.sty
│                                   ← style dependencies
│
├── figures/                        ← every figure used by the build
│   └── README.md                   ← per-figure provenance + regen script
│
├── scripts/                        ← regen scripts for every raster figure
│   └── README.md                   ← per-script catalog
│
├── gdtr_paper_all_sources/         ← v1 source backup, kept for diff/audit
└── gdtr_paper_manuscript*.tex      ← earlier-revision drafts kept for diff
```

---

## Data dependencies (NOT in this folder)

Figures consume artifacts under `../results/` at the repository root:

| Path | Used by |
|---|---|
| `../results/figures_v3/fig_v9_meta.json` | Fig 2 (local), Fig 3 (local) |
| `../results/phase4/per_model_summary.json` | Fig 4, App. B tables |
| `../results/phase4/concordance_matrix.json` | Fig 5 |
| `../results/tier1_baselines/baseline_auroc.json` | Fig 6 |
| `../results/tier1_per_layer/per_layer_auroc.csv` | Fig 6, Tab. 9 |
| `../results/exp1_entropy_meta.json` | App. A.4 entropy table |
| `../results/exp2_shuffled_meta.json` | App. D.3 motif-flank table |
| `../results/phase1.6_sub/splice_distance_profile.json` | App. D.1 |
| `../results/phase1.6/chr22_cache.h5` (H200 only, $\sim\!4$ GB) | Fig 1(b) real, Fig 2 full |
| `../results/p1a/`, `../results/p2/`, `../results/p2_indel/`, `../results/p3b1/` (H200 only) | Fig 2 / Fig 3 full per-position |

See `MANIFEST.md` for the full mapping plus exact column names per CSV
and per-key paths inside each JSON.

---

## Versioning

This is **v11.5** (committed `c8d639a`, 2026-05-05). For the
version-history map of the whole repository (Paper 1 v0–v11, Paper 2
ΔH split, DOCX iterations), see the top-level
[`../VERSIONS.md`](../VERSIONS.md). For the `v1 → v3` narrative
restructure log (2026-04-28), see [`V3_REWRITE_NOTES.md`](V3_REWRITE_NOTES.md).

### What changed in v11.5 (latest)

- **Fig 1(b)** — definition-faithful redesign: raw starts at $D_{\cos}\!\approx\!1$,
  run-min is the actual running min, settled-zone shading + below-axis
  $c{=}22$ / $c{=}31$ callouts (pedagogical schematic).
- **Appendix audit** — added 4 missing tables (entropy decoupling,
  splice-fine minima, canonical/non-canonical motif, motif-flank
  perturbation) + 1 figure (splice positional fine-profile).
- **Fig 2** moved from page 4 → page 3 via `\afterpage{\clearpage}`
  + relaxed `\topfraction`.
- **Fig 3** title set to bold, fontsize 14 (was 11).
- New scripts: `make_fig1_panel_b_local.py`. New figure assets:
  `fig_splice_fine.{pdf,png}`, `fig1_panel_b.{pdf,png}`,
  `fig_variants_local.{pdf,png}`.

### What changed in v11 (vs v10)

- Removed forced `\clearpage` between §3.2 and §3.3.
- Repositioned the "first crossing" arrow in `fig1_schema.tex`.
- Reorganised the appendix from 9 sections (A–I) to 5 narrative-anchored
  sections (A method / B cross-arch / C variant AUROC / D splice anatomy
  / E reproducibility).
- Added explicit numerical disclosures to the abstract.
- Audited Evo 2 idle-final-block wording for accuracy.
