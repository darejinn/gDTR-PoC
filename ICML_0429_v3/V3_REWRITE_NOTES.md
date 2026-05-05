# v3 rewrite notes

This folder is a rewritten ICML workshop version derived from
`ICML_0429_v1 2`. The original folder was left untouched.

## Main narrative change

The paper is now framed around one central claim:

> gDTR is a layer-wise interpretability axis showing where biological grammar
> stabilizes in genomic foundation models.

The rewrite de-emphasizes variant scoring and broad universality claims, and
instead foregrounds three workshop-scale results:

1. Splice sites and enhancer-like cCREs settle earlier than intronic/coding
   contexts.
2. Motif and flank perturbations separate central motif detection from
   flanking-context integration.
3. ClinVar molecular-consequence classes show population-level shifts in the
   layer where variant-induced residual disruption peaks.

## Claim-strength changes

- Removed headline promotion of 5' UTR because it is partly entropy-confounded.
- Reframed eQTL/GWAS as directionally consistent but biologically small.
- Reframed cross-architecture evidence as replication in two per-bp causal LMs
  plus tokenization limits for MLMs.
- Softened tuned-lens wording from proof of information-content stabilization
  to a sanity check against gross frame mismatch.
- Reworded variant analysis as a depth probe, not a clinical scorer.

## Consistency fixes

- Harmonized the hyperparameter sweep SD to `0.06`.
- Removed/softened wording around universal invariance and causal mechanism.
- Clarified that lower `c(t)` means earlier stabilization.
- Shortened figure captions and made variant traces explicitly qualitative.

## Build

Built successfully with:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error gdtr_paper_ICML.tex
```

Output:

- `gdtr_paper_ICML.pdf`

## Figure regeneration

Main and appendix figures were regenerated on `digitalocean-gpu` using the full
remote cache and matplotlib:

```bash
cd /root/gDTR
GDTR_ROOT=/root/gDTR /root/gDTR/venv/bin/python scripts/make_v3_figures_remote.py
```

The local copy of the script is:

- `scripts/make_v3_figures_remote.py`

Generated figures copied into `figures/`:

- `fig1_v10.{png,pdf}`: simplified method schema plus real chr22 trajectories.
- `fig_shallowness.{png,pdf}`: cleaner splice/cCRE/eQTL/GWAS effect-size figure.
- `fig_variants.{png,pdf}`: main-text boxplot only; trace-heavy old figure removed
  from the main path.
- `fig_crossarch.{png,pdf}`: appendix-style tokenization/readout-granularity figure.
