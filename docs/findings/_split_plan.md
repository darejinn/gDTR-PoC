# PHASE1_FINDINGS.md split plan (2026-04-28)

The legacy file `PHASE1_FINDINGS.md` (873 lines) is mis-titled — sections 11–12
contain Phase 2/3/4/5 results that were appended after Phase 1 closed. This
document records exactly how its content was redistributed into the new
per-phase docs under `docs/findings/`.

| Source range (PHASE1_FINDINGS.md) | Topic | Destination |
|---|---|---|
| L1–10  | Front matter | `phase1_evo2_calibration.md` (front matter rewritten) |
| L11–22 (§0 TL;DR) | Phase 1 TL;DR | `phase1_evo2_calibration.md` (top, kept verbatim) |
| L23–131 (§§1–2) | Background, env, pipeline, per-substage results 1.0–1.7 | `phase1_evo2_calibration.md` |
| L132–198 (§3 Finding 1: L31 idle) | Architectural quirk | `phase1_evo2_calibration.md` (Finding 1) |
| L199–256 (§4 Finding 2: splice deep-thinking) | Splice-site signature on chr22 | `phase1_evo2_calibration.md` (Finding 2; chr17 replication is in Phase 2 doc) |
| L257–298 (§5 Finding 3: Gate B reversal + HP) | Direction reversal + HP transfer | `phase1_evo2_calibration.md` (Finding 3) |
| L299–390 (§§6–7) | Synthesis + decision-tree retrospective | `phase1_evo2_calibration.md` |
| L391–472 (§§8–10) | Phase-1 limitations, Phase 2 carry-over, open questions | `phase1_evo2_calibration.md` |
| L473–567 (Appendices A, B) | Statistical details + reproducibility | `phase1_evo2_calibration.md` (Phase-1-specific; covers only Phase 1 data) |
| L568–587 | End-of-document footer + pending sub-experiments list | `phase1_evo2_calibration.md` (footer trimmed) |
| L588–612 (§11.1 ClinVar pilot) | TP53+BRCA1 pilot, AUROC 0.831 | `phase3_variant_pathogenicity.md` (Pilot section) |
| L613–645 (§11.2 32-layer landscape) | Per-layer tuned-lens recovery (L=2..31) | `phase1_evo2_calibration.md` (Post-Phase-1 follow-up) |
| L646–648 (§11.3 chr17 prep marker) | One-line status note | `phase2_chr17_replication.md` (mentioned in section 1; full chr17 results from PHASE2_DECISION.md) |
| L649–716 (§11.4 Phase 3 main 15 genes) | Stratified + LOGO CV, ensemble | `phase3_variant_pathogenicity.md` |
| L717–750 (§11.5 Phase 5 Q2) | Q2 conservation discordance | `phase5_conservation_discordance.md` |
| L751–794 (§11.6 Phase 3 ensemble + DeLong) | CADD / AlphaMissense / DeLong refined narrative | `phase3_variant_pathogenicity.md` (Ensemble + DeLong section) |
| L795–860 (§11.7 Phase 4 cross-arch) | 4-model two-tier invariance | `phase4_cross_architecture.md` |
| L861–873 (§12 Final summary) | 5-finding rollup | `phase1_evo2_calibration.md` footer + cross-referenced from each phase |

Phase 0 calibration (`phase0_calibration.md`) is a thin pointer to the
existing `docs/PHASE0_FINDINGS.md`; Phase 0 was not part of the legacy file.

Tier 1 / Tier 2 docs (`tier1_extensions.md`, `tier2_extensions.md`) are NEW
and built from JSON/CSV under `results/tier1_*` and `results/tier2_*`.

After verification the legacy file is removed via `git mv` (see commit 1).
