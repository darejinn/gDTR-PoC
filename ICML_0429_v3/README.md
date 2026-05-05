# ICML 2026 workshop short paper — gDTR (revision v11, 2026-05-05)

This folder is the **current canonical** ICML 2026 workshop submission for
**Paper 1 — gDTR (mechanistic probe)**.

> **Title.** gDTR: Layer-wise Settling Depth Reveals Biological Grammar in
> Genomic Foundation Models.
> **Length.** 4-page main body + references + appendix (12 pages total).

For the version-history map of the whole repository (including the original
`ICML_0429_v1 2/` folder, the DOCX iterations, and the companion Paper 2
ΔH split), see the top-level [`VERSIONS.md`](../VERSIONS.md).

## Files

| Path | Purpose |
|---|---|
| `gdtr_paper_ICML.tex` | Main LaTeX source (single file). |
| `gdtr_paper_ICML.pdf` | Built PDF (12 pages). |
| `gdtr_paper.bib` | Bibliography. |
| `figures/fig1_schema.tex` | TikZ source for Fig. 1(a) pipeline schematic. |
| `figures/fig1_trajectory.png` | Pre-rendered Fig. 1(b) trajectory plot. |
| `figures/fig_shallowness.{png,pdf}` | Fig. 2 — splice/cCRE shallowness. |
| `figures/fig_variants.{png,pdf}` | Fig. 3 — variant consequence depth shifts. |
| `figures/fig_appendix_b.png` | Fig. 4 — per-context bars across four models. |
| `figures/fig_crossarch.{png,pdf}` | Fig. 5 — cross-architecture two-tier structure. |
| `figures/fig_auroc.png` | Fig. 6 — variant AUROC four-panel diagnostics. |
| `MANIFEST.md` | **Per-figure / per-table mapping** (what produces what). Start here. |
| `scripts/make_v3_figures_remote.py` | Master figure regeneration (runs on H200). |
| `scripts/regen_fig_shallowness_local.py` | Fig. 2 — local regen from `fig_v9_meta.json`. |
| `scripts/regen_fig_variants_local.py` | Fig. 3 — local summary regen from `fig_v9_meta.json`. |
| `scripts/regen_fig_appendix_b_local.py` | Fig. 4 — local regen from `phase4/per_model_summary.json`. |
| `scripts/regen_fig_auroc_local.py` | Fig. 6 — local regen from Tier-1 baseline JSON / per-layer CSV. |
| `scripts/make_fig1_trajectory_local.py` | Crops the Fig. 1(b) trajectory PNG locally. |
| `scripts/redraw_fig1_panel_a_local.py` | Legacy raster schematic (superseded by `fig1_schema.tex`). |
| `icml2026.sty`, `icml2026.bst` | ICML 2026 style files (do not modify). |
| `algorithm.sty`, `algorithmic.sty`, `fancyhdr.sty` | Style dependencies. |
| `gdtr_paper_all_sources/` | Original v1 source backup, kept for diff/audit. |
| `gdtr_paper_manuscript.tex`, `gdtr_paper_manuscript_plaintext.tex`, `gdtr_paper.tex` | Earlier-revision drafts kept for diff. |
| `V3_REWRITE_NOTES.md` | Narrative log of the v1→v3 rewrite (2026-04-28). |

## Build

```bash
cd ICML_0429_v3
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

The build is self-contained: TeX Live 2024+ with `pdftex`, the included
ICML 2026 style files, and standard packages (`microtype`, `graphicx`,
`subcaption`, `booktabs`, `siunitx`, `tikz`, `hyperref`, `cleveref`).
No internet or model weights required for the build itself.

## Reproducibility — figure regeneration

See `MANIFEST.md` for the canonical figure-by-figure mapping (script →
input data → output path). Two domains:

**Local (no GPU).** Five of the six raster figures rebuild from the
JSON/CSV summaries vendored under `../results/`:

```bash
python scripts/regen_fig_shallowness_local.py   # Fig 2
python scripts/regen_fig_variants_local.py      # Fig 3 (summary form)
python scripts/regen_fig_appendix_b_local.py    # Fig 4
python scripts/regen_fig_auroc_local.py         # Fig 6
python scripts/make_fig1_trajectory_local.py    # Fig 1(b) crop
```

Fig. 1(a) is pure TikZ (`figures/fig1_combined.tex`) and rebuilds with
`latexmk`. Fig. 5 (`fig_crossarch`) is also locally renderable via
`make_v3_figures_remote.py::fig_crossarch()` — it reads only the small
`results/phase4/concordance_matrix.json`.

**Remote (H200, full per-position regen).**

```bash
ssh digitalocean-gpu
cd ~/gDTR
GDTR_ROOT=$PWD ./venv/bin/python scripts/make_v3_figures_remote.py
# → results/figures_v3_workshop/{fig1_v10,fig_shallowness,fig_variants,fig_crossarch}.{png,pdf}
```

The H200 path consumes the full feature caches described in Appendix E
(GENCODE v44, ENCODE SCREEN cCRE-ELS, ClinVar 2026-04-18, etc.).

## Font conventions

- Body text: Times (icml2026.sty -> `ptm`).
- Fig. 1(a) TikZ schematic: `\sffamily` (sans-serif), chosen to match
  the matplotlib raster panel (b) without requiring a remote regen.
- Fig. 1(b) and all other matplotlib outputs: `font.family: serif` is
  set in `make_v3_figures_remote.py`. Re-running the script will produce
  serif-matched panels; the currently shipped PNG predates that change.

## What changed in v11 (vs v10 / v3 first build)

See `V3_REWRITE_NOTES.md` for the v1→v3 narrative restructure
(2026-04-28). The 2026-05-05 v11 polish on top of v3:

- Removed forced `\clearpage` between §3.2 and §3.3 (eliminates a
  half-page whitespace on body p.4).
- Repositioned the "first crossing" arrow in `fig1_schema.tex` so it
  no longer collides with the right-column legend.
- Reorganised the appendix from 9 sections (A–I, several orphan
  headings) to 5 narrative-anchored sections (A method / B cross-arch
  / C variant AUROC / D splice anatomy / E reproducibility).
- Added explicit numerical disclosures to the abstract (94.6% effect
  retention, 3.18 layers shallowing, $p\!=\!3.0\!\times\!10^{-10}$).
- Audited content for accuracy: replaced the inaccurate "blocks 30–31
  acting as bookkeeping" wording with the empirically faithful
  "block 30 is a rotation, block 31 is residual passthrough"
  description (see Table~\ref{tab:idle-block} cosine values).
- Ensured every figure (1–6) is referenced from at least one body
  paragraph; appendix figures gained explicit body-text pointers.

## Data dependencies (not in this folder)

The figures were generated from `results/` artifacts at the repository
root (`results/exp1_entropy/`, `results/exp2_shuffled/`,
`results/figures_v3/`, `results/phase4/per_model_summary.json`, etc.).
See the top-level `README.md` for the per-phase data layout.
