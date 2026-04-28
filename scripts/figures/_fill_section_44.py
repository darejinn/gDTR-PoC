"""Fill ICML_MANUSCRIPT_DRAFT.md §4.4 placeholders from T1.2 + T2.4 outputs.

Reads:
  - results/tier1_baselines/baseline_auroc.json
  - results/tier1_baselines/baseline_spearman.csv
  - results/tier1_baselines/delong_pairs.csv
  - results/tier2_compute/cost_benchmark.csv (optional)

Replaces all `[A_strat]`, `[A_logo]`, `[ρ_AB]`, `[Δ_AB]`, `[A_ms]` etc. tokens
in §4.4 with the actual numbers, in-place. Idempotent — re-running on already-
filled section is a no-op (no [TOKENS] left to replace).
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results"
MANUSCRIPT = ROOT / "ICML_MANUSCRIPT_DRAFT.md"

AUROC_P = RES / "tier1_baselines" / "baseline_auroc.json"
SPEAR_P = RES / "tier1_baselines" / "baseline_spearman.csv"
DELONG_P = RES / "tier1_baselines" / "delong_pairs.csv"
COST_P = RES / "tier2_compute" / "cost_benchmark.csv"

NAME_TO_LETTER = {"A_dD_cos": "A", "B_delta_h": "B", "C_rollout": "C", "D_ig": "D"}
LETTER_TO_NAME = {v: k for k, v in NAME_TO_LETTER.items()}


def must(p: Path):
    if not p.exists():
        print(f"[fill] required {p} missing — abort.")
        sys.exit(1)


def fmt(v, fmt_str=".3f"):
    if v is None:
        return "—"
    try:
        return format(float(v), fmt_str)
    except Exception:
        return str(v)


def fmt_p(p):
    if p is None:
        return "—"
    p = float(p)
    if p < 1e-200:
        return "< 1e-200"
    if p < 1e-3:
        return f"{p:.2g}"
    return f"{p:.3f}"


def main():
    must(AUROC_P); must(SPEAR_P); must(DELONG_P)

    auroc = json.loads(AUROC_P.read_text())
    spear = pd.read_csv(SPEAR_P, index_col=0)
    delong = pd.read_csv(DELONG_P)
    cost = pd.read_csv(COST_P) if COST_P.exists() else None

    text = MANUSCRIPT.read_text()
    repl = {}

    # ---- Per-method AUROC (4.4.1) -----
    for letter, name in LETTER_TO_NAME.items():
        sr = auroc["results_stratified"][name]
        lr = auroc["results_logo"][name]
        repl[f"[{letter}_strat]"] = fmt(sr["mean_auroc"])
        repl[f"[{letter}_strat_ci]"] = (
            f"[{fmt(sr['ci95_lo'])}, {fmt(sr['ci95_hi'])}]"
        )
        repl[f"[{letter}_logo]"] = fmt(lr["mean_auroc"])
        repl[f"[{letter}_logo_ci]"] = (
            f"[{fmt(lr['ci95_lo'])}, {fmt(lr['ci95_hi'])}]"
        )

    # ---- Spearman ρ (4.4.2) -----
    pairs = [("A", "B"), ("A", "C"), ("A", "D"), ("B", "C"), ("B", "D"), ("C", "D")]
    for x, y in pairs:
        nx, ny = LETTER_TO_NAME[x], LETTER_TO_NAME[y]
        try:
            v = float(spear.loc[nx, ny])
            repl[f"[ρ_{x}{y}]"] = f"{v:+.2f}"
        except Exception:
            repl[f"[ρ_{x}{y}]"] = "—"

    # ---- DeLong (4.4.3) -----
    for _, row in delong.iterrows():
        b_letter = NAME_TO_LETTER.get(row["feat_b"])
        if b_letter is None:
            continue
        repl[f"[Δ_A{b_letter}]"] = f"{row['delta']:+.4f}"
        repl[f"[z_A{b_letter}]"] = fmt(row["z"], ".2f")
        repl[f"[p_A{b_letter}]"] = fmt_p(row["p_value"])

    # ---- Incremental info (4.4.4) -----
    incr_map = {r["baseline"]: r for r in auroc.get("incremental_info", [])}
    for letter, name in LETTER_TO_NAME.items():
        if letter == "A":
            continue
        if name in incr_map:
            r = incr_map[name]
            repl[f"[resA_{letter}]"] = fmt(r["auroc_residual_dD_minus_baseline"])
            repl[f"[{letter}_alone]"] = fmt(r["auroc_baseline_alone"])

    # ---- Cost (4.4.5) — keys may differ between T2.4 conventions -----
    if cost is not None:
        # Cost csv method names may not match A_dD_cos format; try fuzzy mapping
        cost_keys = list(cost["method"])
        method_disp = {"A": ["gdtr", "ΔD", "dD", "dd", "evo2", "Evo2", "gDTR", "delta_d", "ΔD_cos"],
                       "B": ["delta_h", "Δh", "‖Δh‖", "delta_h_norm", "delta-h"],
                       "C": ["rollout", "attn_rollout", "attention_rollout", "attn"],
                       "D": ["ig", "IG", "integrated_gradients"]}
        for letter, candidates in method_disp.items():
            found = None
            for c in candidates:
                for k in cost_keys:
                    if c.lower() in str(k).lower():
                        found = k; break
                if found:
                    break
            if found is not None:
                row = cost[cost["method"] == found].iloc[0]
                repl[f"[{letter}_ms]"] = fmt(row["mean_per_variant_ms"], ".1f")
                repl[f"[{letter}_vram]"] = fmt(row["peak_vram_gb"], ".1f")
            else:
                repl[f"[{letter}_ms]"] = "—"
                repl[f"[{letter}_vram]"] = "—"

    # Apply replacements
    n_replaced = 0
    for token, value in repl.items():
        if token in text:
            text = text.replace(token, value)
            n_replaced += 1

    # Update banner status
    text = text.replace(
        "- 🔄 T1.2 interpretability baseline comparison (running on H200, ETA ~3 h)",
        "- ✅ T1.2 interpretability baseline comparison",
    )
    text = text.replace(
        "- ⏳ T2.4 compute cost benchmark (after T1.2)",
        "- ✅ T2.4 compute cost benchmark" if cost is not None
        else "- 🔄 T2.4 compute cost benchmark (deferred)",
    )

    MANUSCRIPT.write_text(text)
    print(f"[fill] replaced {n_replaced} placeholders in §4.4")
    # Report any leftover placeholders
    leftover = re.findall(r"\[(?:[A-D]_[a-z_]+|ρ_[A-D]{2}|Δ_[A-D]{2}|z_[A-D]{2}|p_[A-D]{2}|resA_[A-D]|[A-D]_alone)\]", text)
    if leftover:
        print(f"[fill] WARN: {len(leftover)} unfilled tokens (some may be legitimately N/A): {sorted(set(leftover))[:10]}")


if __name__ == "__main__":
    main()
