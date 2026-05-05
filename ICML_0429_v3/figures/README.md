# `figures/` — figure asset catalog

Every PNG / PDF / TikZ-source under this directory, with provenance and
the script that regenerates it. Matches the LaTeX includes in
`../gdtr_paper_ICML.tex`.

For the figure → script → upstream-data mapping, see
[`../MANIFEST.md`](../MANIFEST.md).

---

## Used by the v11.5 build

### Fig 1(a) — gDTR pipeline schematic
- `fig1_combined.tex` — single TikZ source containing **both** Fig 1(a)
  pipeline schema (top half) and Fig 1(b) example trajectories (bottom
  half), pinned in one `tikzpicture` so the two panels share font
  family / weight / glyph size.
- `fig1_schema.tex` — earlier TikZ-only version of panel (a),
  superseded by `fig1_combined.tex`. Kept for diff.

### Fig 1(b) — example trajectories
- Rendered **inside** `fig1_combined.tex` as TikZ in the v11.5 build
  (no raster).
- `fig1_panel_b.{pdf,png}` — equivalent matplotlib version produced by
  `../scripts/make_fig1_panel_b_local.py` (schematic, definition-faithful).
  NOT included by the LaTeX build — provided for cross-reference and as
  a drop-in replacement if you'd rather use raster.
- `fig1_trajectory.tex` — standalone TikZ source for panel (b) only,
  kept as a reference (the in-`fig1_combined.tex` version mirrors
  this layout 1:1 with adjusted scale).
- `fig1_trajectory.png` — legacy v10 raster, kept for diff.

### Fig 2 — splice / cCRE shallowness (`fig:shallowness`)
- `fig_shallowness.{pdf,png}` — `\includegraphics` target.
- Regen: `../scripts/regen_fig_shallowness_local.py` (local) or
  `../scripts/make_v3_figures_remote.py::fig_shallowness` (H200, full
  per-position).

### Fig 3 — variant consequence boxplot (`fig:variants`)
- `fig_variants_local.{pdf,png}` — currently included by the LaTeX
  build. Bold + 14-pt title, summary-form box layout (median + fixed
  half-width).
- `fig_variants.{pdf,png}` — full per-variant boxplot from the v9 H200
  render. Smaller normal-weight title. Switch the `\includegraphics`
  to this if you re-sync H200 with the new bold-title style.
- Regen: `../scripts/regen_fig_variants_local.py` (local summary) or
  `../scripts/make_v3_figures_remote.py::fig_variants` (H200, full).

### Fig 4 — per-context bars across four FMs (`fig:cross-arch-context`)
- `fig_appendix_b.png` — currently included by the LaTeX build (carried
  over from v9 commit `e5c8617`).
- `fig_appendix_b_local.{pdf,png}` — fresh local regen from
  `phase4/per_model_summary.json`.
- Regen: `../scripts/regen_fig_appendix_b_local.py` (local).

### Fig 5 — cross-architecture two-tier (`fig:cross-arch`)
- `fig_crossarch.{pdf,png}` — `\includegraphics` target.
- Regen: `../scripts/make_v3_figures_remote.py::fig_crossarch` (works
  locally too — only reads `phase4/concordance_matrix.json`).

### Fig 6 — variant AUROC four-panel diagnostic (`fig:auroc`)
- `fig_auroc.png` — currently included by the LaTeX build (carried over
  from v9 commit `e5c8617`).
- `fig_auroc_local.{pdf,png}` — fresh local regen from
  `tier1_baselines/baseline_auroc.json` + `tier1_per_layer/per_layer_auroc.csv`.
- Regen: `../scripts/regen_fig_auroc_local.py` (local).
- Note: panel (a) of the local regen substitutes a bar chart for the
  raw ROC curves (per-variant scores not vendored locally). Panels
  (b)-(d) match the paper.

### Fig (App. D.1) — splice positional fine-profile (`fig:splice-fine`)
- `fig_splice_fine.{pdf,png}` — copied from
  `../../results/phase1.6_sub/F_splice_distance_profile.{pdf,png}`
  (rendered upstream during phase 1.6 sub-analysis; not regenerated
  by any script in this folder).

---

## Legacy assets — NOT referenced by the v11.5 build

Kept under version control for diff / audit; safe to delete if the
folder needs to slim down (see `MANIFEST.md` §6 for full list and
provenance).

| File | Last referenced | Replaced by |
|---|---|---|
| `fig_disruption.{pdf,png}` | v8 | `fig_variants*` |
| `fig_funcshallow.{pdf,png}` | v8 | merged into `fig_shallowness` |
| `fig_splice.{pdf,png}` | v8 | merged into `fig_shallowness` |
| `fig_q2.png` | v8 | dropped in v11 (Q2 paragraph removed) |
| `fig_schematic.png` | v9 | replaced by `fig1_combined.tex` (TikZ) |
| `fig_variants_full_v1.png` | v10 | superseded by `fig_variants*` |
| `fig1_v10.{pdf,png}` | v10 | split into `fig1_combined.tex` + `fig1_panel_b` |
| `fig1_v10_source_with_panel_b.png` | v10 | crop intermediate |
| `fig2_v11.png` | v11 (early) | superseded by `fig_shallowness` |

---

## Edit policy

- TikZ panel (a) inside `fig1_combined.tex` is the canonical source —
  edit only this for Fig 1(a) styling changes.
- TikZ panel (b) inside `fig1_combined.tex` is **synced** with
  `../scripts/make_fig1_panel_b_local.py` — if you change the example
  coordinates in one, change them in the other (and re-run the Python
  to verify the self-test prints `splice c = 22 / intron c = 31`).
- Raster figures (`*.png` / `*.pdf`) should be regenerated from the
  scripts under `../scripts/` rather than edited in place; replacing
  PNGs by hand will desync the captioned numbers from the result
  artifacts.
- The `*_local.{png,pdf}` naming convention indicates "produced from
  the locally-vendored summary JSON/CSV without H200 access". The
  unmarked names refer to the H200-rendered version.
