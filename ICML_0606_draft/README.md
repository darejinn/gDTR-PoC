# ICML 0606 Draft

Minimal source package for the current ICML draft.

## Build

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

## Contents

- `gdtr_paper_ICML.tex` - canonical LaTeX source.
- `gdtr_paper_ICML.pdf` - built draft PDF.
- `gdtr_paper.bib` - bibliography.
- `icml2026.sty`, `icml2026.bst`, `algorithm.sty`, `algorithmic.sty`, `fancyhdr.sty` - local style files needed by the ICML build.
- `figures/` - seven PNG figures referenced by `gdtr_paper_ICML.tex`.
- `scripts/` - current figure regeneration scripts.

Keep detailed provenance outside this minimal draft folder, preferably under `docs/`.
