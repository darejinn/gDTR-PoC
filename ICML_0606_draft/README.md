# ICML 2026 workshop short paper — gDTR (v11.6 + 0509 corrections, 2026-05-09)

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
cd ICML_0509_v4
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

Self-contained build: TeX Live 2024+ with `pdftex`, the included ICML
2026 style files, and standard packages (`microtype`, `graphicx`,
`subcaption`, `booktabs`, `siunitx`, `tikz`, `afterpage`, `hyperref`,
`cleveref`). No model weights or internet required for the build.

### Regenerate every figure locally (no GPU)

```bash
# Fig 1 (figures/fig_1_final.png) is a self-contained PNG authored externally — no script.
python scripts/regen_fig_shallowness_local.py              # Fig 2 — splice/cCRE shallowness
python scripts/regen_fig_variants_local.py                 # Fig 3 — variant boxplot summary
python scripts/regen_fig_cross_arch_context_local.py       # Fig A1 — per-context FM bars
python scripts/regen_fig_A2_cross_arch_two_tier_local.py   # Fig A2 — cross-arch two-tier
python scripts/regen_fig_auroc_local.py                    # Fig A3 — variant AUROC panels
# Fig A4 (figures/fig_A4_splice_fine.png) is copied from upstream phase 1.6_sub — no script.
```

### Regenerate from real per-position data (H200 only)

```bash
ssh digitalocean-gpu
cd ~/gDTR
GDTR_ROOT=$PWD ./venv/bin/python scripts/make_v3_figures_remote.py
# → results/figures_v3_workshop/{fig1_v10,fig_shallowness,fig_variants,fig_crossarch}.{png,pdf} (legacy upstream names)
rsync -avz digitalocean-gpu:~/gDTR/results/figures_v3_workshop/ figures/
```

---

## "Where is the code that produced X?"

| Output (in PDF) | File name (positional) | Render script | Upstream pipeline |
|---|---|---|---|
| Fig 1 pipeline schematic | `figures/fig_1_final.png` | externally-authored raster (Keynote / draw.io / Figma) | — |
| Fig 2 splice/cCRE shallowness | `figures/fig_2_shallowness.{pdf,png}` | [`scripts/regen_fig_shallowness_local.py`](scripts/regen_fig_shallowness_local.py) | `p1a/calib_val_table.csv`, `p3b1/p3b1_func_pos.json` |
| Fig 3 variant boxplot | `figures/fig_3_variants.{pdf,png}` | [`scripts/regen_fig_variants_local.py`](scripts/regen_fig_variants_local.py) (summary) / [`make_v3_figures_remote.py::fig_variants`](scripts/make_v3_figures_remote.py) (full) | `p2/variants_features_classed.csv`, `p2_indel/variants_features_indel.csv` |
| Fig A1 per-context FM bars | `figures/fig_A1_cross_arch_context.{pdf,png}` | [`scripts/regen_fig_cross_arch_context_local.py`](scripts/regen_fig_cross_arch_context_local.py) | `phase4/per_model_summary.json` |
| Fig A2 cross-arch two-tier | `figures/fig_A2_cross_arch_two_tier.{pdf,png}` | [`scripts/regen_fig_A2_cross_arch_two_tier_local.py`](scripts/regen_fig_A2_cross_arch_two_tier_local.py) | `phase4/concordance_matrix.json` |
| Fig A3 variant AUROC | `figures/fig_A3_auroc.{pdf,png}` | [`scripts/regen_fig_auroc_local.py`](scripts/regen_fig_auroc_local.py) | `tier1_baselines/baseline_auroc.json`, `tier1_per_layer/per_layer_auroc.csv` |
| Fig A4 splice fine-profile | `figures/fig_A4_splice_fine.{pdf,png}` | copied from upstream `phase1.6_sub/F_splice_distance_profile.{pdf,png}` | — (rendered upstream) |

For per-table data sources and the local-vs-H200 split, see
[`MANIFEST.md`](MANIFEST.md).

For a script catalog with inputs/outputs, see [`scripts/README.md`](scripts/README.md).

For figure provenance per file, see [`figures/README.md`](figures/README.md).

---

## Honest disclosure: Fig 1 (v4)

Fig 1 in v4 is the externally-authored raster `figures/fig_1_final.png`,
a single-panel pedagogical schematic that walks through the gDTR
pipeline on one worked example with $c(t)\!=\!30$. It is illustrative
of the algorithm's mechanics (residual states → cosine UR lens →
$D_{\cos}$ → running minimum → threshold check → settling depth) and
not a plot of real chr22 data. The previous v11.5/v11.6 panel (b),
which showed two real-coordinate-derived trajectories with splice
$c\!=\!22$ and intron $c\!=\!31$, lives in
`figures/fig1_combined.tex` (TikZ) and `figures/fig1_panel_b.{pdf,png}`
(matplotlib) and is retained for diff/audit only.

To revise Fig 1, edit the upstream design source (Keynote / draw.io /
Figma / etc.), re-export to `figures/fig_1_final.png`, and rebuild.
The settling-depth example value ($c(t)\!=\!30$) shown on the figure
should be kept consistent with whatever wording the caption uses; the
v4 caption is parameterised on $c(t)\!=\!30$.

---

## Top-level file map

```
ICML_0509_v4/
├── README.md                       ← you are here
├── MANIFEST.md                     ← per-figure / per-table source-of-truth
├── corrections_applied.md          ← v3 → v4 corrections applied (this revision)
├── correction.md                   ← review punch-list that drove v4
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

This is **v11.6 + 0509 corrections** (2026-05-09). The text/citation
corrections vs v11.6 (the v3 folder) are recorded in
[`corrections_applied.md`](corrections_applied.md) and the
review-punch-list source is [`correction.md`](correction.md). The
pre-v4 baseline is v11.5 / v11.6 in `ICML_0429_v3/` (committed `c8d639a`,
2026-05-05). For the version-history map of the whole repository
(Paper 1 v0–v11, Paper 2 ΔH split, DOCX iterations), see the top-level
[`../VERSIONS.md`](../VERSIONS.md). For the `v1 → v3` narrative
restructure log (2026-04-28), see [`V3_REWRITE_NOTES.md`](V3_REWRITE_NOTES.md).

### What changed in v4 (vs v11.5/v11.6 in `ICML_0429_v3/`)

- **Logic skeleton (§2/§3.2/§3.3/§4/§5):** explicit "settling depth is
  two-sided" / "bidirectional" framing in §2; §3.2 reframed as a
  dissociation experiment that exploits the two-sidedness;
  synonymous-deepest mechanistic interpretation added in §3.3;
  bidirectional + correlational/interventional split + composition
  confounder strengthened in §4; §5 conclusion re-organised into three
  numbered messages.
- **Citation/factual fixes:** Dunn citation (Dunn 1964 instead of
  Mann–Whitney + BH-FDR); body Cohen's $d{=}{-}0.086$ matches Tab.~9;
  $|\rho|\!\le\!0.16$ throughout (was 0.15, conflicted with Tab.~3
  splice-acceptor 0.152); analysed-position count 719,000 (was 720,000,
  conflicted with Tab.~3 row); new App. C paragraph on why $L^{\star}{=}29$
  vs $\ell{=}30$ are consistent; Fig.~6 caption now lists best taps for
  both lenses.
- **Style:** "shallows" replaced by "lifts ... to a shallower value";
  Title Case across all sections/subsections; "Paired DeLong tests"
  standard wording; "100 windows of 6 kb each" disambiguation;
  tuned-lens 98% threshold flagged as descriptive.
- **Figures (v4 housekeeping):** (a) every figure file is now prefixed
  with its position in the PDF — `fig_1_*.png`, `fig_2_*.png`,
  `fig_3_*.png` for main text; `fig_A1_*.png` … `fig_A4_*.png` for the
  appendix (matching the A-prefixed numbering enabled in
  `gdtr_paper_ICML.tex` after `\appendix`). (b) Fig 1 swapped from the
  v11.5/v11.6 TikZ source `fig1_combined.tex` (two-trajectory example)
  to the externally-authored single-panel raster `fig_1_final.png`,
  which walks through the algorithm end-to-end on one worked example
  with $c(t)\!=\!30$. Caption rewritten to match.
  (c) Every regen script's output now writes the positional file name;
  the old non-positional copies were removed (originals preserved in
  `../ICML_0429_v3/figures/` for diff).
- **Appendix numbering A1, A2 …:** added
  `\renewcommand{\thefigure}{A\arabic{figure}}` and the matching
  `\thetable` redefinition (plus counter resets) right after `\appendix`,
  so appendix figures/tables now print as Fig A1–A4 / Tab A1–A12 while
  the main text stays Fig 1–3 / Tab 1.
- **Figure title fonts:** every regen-script title (Fig 2/3/A1/A2/A3)
  now sets `fontfamily="Times New Roman"` on `set_title(...)` and
  `suptitle(...)` calls. Body text remains DejaVu Sans (matches the
  LaTeX `\sffamily`). Fig A4 is the lone exception — it is copied from
  upstream and its title font is inherited.
- **Bib:** added `@article{dunn1964multiple, ...}` (was only in the
  master bib at repo root, missing from the v3 folder bib).

### What changed in v11.5

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
