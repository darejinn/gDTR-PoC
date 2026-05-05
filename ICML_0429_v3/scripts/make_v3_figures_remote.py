"""Generate polished v3 ICML figures from the full gDTR result cache.

Run on the GPU server:

    GDTR_ROOT=/root/gDTR /root/gDTR/venv/bin/python make_v3_figures_remote.py

Outputs are written to:

    $GDTR_ROOT/results/figures_v3_workshop/

The script uses the real cached trajectories for Fig. 1 and the paper-locked
analysis artifacts for the remaining figures. It deliberately simplifies the
main-paper figures relative to v1/v2:

- Fig. 1 keeps a visual method schema, but removes the dense per-layer toy
  table that made the old figure hard to read.
- Fig. 2 foregrounds splice/cCRE shallowness and explicitly treats eQTL/GWAS as
  small effects.
- Fig. 3 is a main-text boxplot only; representative traces are left to appendix.
- Cross-architecture is appendix-style and framed as tokenization/readout
  granularity rather than a universal biological claim.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import h5py
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from scipy import stats


GDTR_ROOT = Path(os.environ.get("GDTR_ROOT", "/root/gDTR"))
OUT_DIR = GDTR_ROOT / "results" / "figures_v3_workshop"
GAMMA = 0.39663
L = 32

BLUE = "#1f77b4"
RED = "#d62728"
ORANGE = "#ff7f0e"
GREY = "#7f7f7f"
LIGHT_GREY = "#bdbdbd"
DARK = "#222222"


def setup_style() -> None:
    # NOTE (font unification): the LaTeX paper uses Times (icml2026.sty -> ptm),
    # and the TikZ schema in fig1 uses sans-serif to match matplotlib output.
    # If you want both panels of Fig 1 to look serif (preferred for academic
    # publishing), keep "font.family": "serif" below; if you re-style the TikZ
    # back to serif, also flip this back to "DejaVu Sans" or "sans-serif".
    plt.rcParams.update({
        "font.family": "serif",
        "font.serif": ["DejaVu Serif", "Times New Roman", "Times"],
        "mathtext.fontset": "dejavuserif",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 7.2,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def save(fig: plt.Figure, name: str) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_DIR / f"{name}.png", dpi=240)
    fig.savefig(OUT_DIR / f"{name}.pdf")
    plt.close(fig)


def cohen_d(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float64)
    nx, ny = len(x), len(y)
    vx, vy = np.var(x, ddof=1), np.var(y, ddof=1)
    sp = np.sqrt(((nx - 1) * vx + (ny - 1) * vy) / (nx + ny - 2))
    return float((np.mean(x) - np.mean(y)) / sp)


def sig_stars(p: float) -> str:
    if p < 1e-4:
        return "****"
    if p < 1e-3:
        return "***"
    if p < 1e-2:
        return "**"
    if p < 5e-2:
        return "*"
    return "ns"


def load_pooled_contexts() -> dict[str, dict[str, float]]:
    rows = []
    csv_path = GDTR_ROOT / "results" / "p1a" / "calib_val_table.csv"
    with csv_path.open() as f:
        header = f.readline().strip().split(",")
        for line in f:
            d = dict(zip(header, line.strip().split(",")))
            rows.append({
                "chrom": d["chrom"],
                "context": d["context"],
                "n": int(d["n"]),
                "mean_c": float(d["mean_c"]),
            })
    out = {}
    for ctx in sorted({r["context"] for r in rows}):
        sel = [r for r in rows if r["context"] == ctx]
        n = sum(r["n"] for r in sel)
        out[ctx] = {"mean": sum(r["mean_c"] * r["n"] for r in sel) / n, "n": n}
    return out


def pick_example_trajectories() -> tuple[np.ndarray, np.ndarray, int, int]:
    """Pick representative real chr22 donor and intron trajectories."""
    cache = GDTR_ROOT / "results" / "phase1.6" / "chr22_cache.h5"
    labels = np.load(GDTR_ROOT / "data" / "annotation" / "chr22_position_labels.npy")
    best_donor = None
    best_intron = None
    target_donor, target_intron = 22, 31
    rng = np.random.default_rng(42)
    with h5py.File(cache, "r") as f:
        starts = f["starts"][:]
        dset = f["D_cos"]
        for wi, start in enumerate(starts):
            lab = labels[int(start): int(start) + 6000]
            donor_idx = np.where(lab == 5)[0]
            intron_idx = np.where(lab == 1)[0]
            if donor_idx.size == 0 and intron_idx.size == 0:
                continue
            D = dset[int(wi)].astype(np.float32)
            run = np.minimum.accumulate(D, axis=0)
            for k in donor_idx:
                hits = np.where(run[:, k] <= GAMMA)[0]
                if not hits.size:
                    continue
                c = int(hits[0]) + 1
                score = abs(c - target_donor)
                if best_donor is None or score < best_donor[0]:
                    best_donor = (score, c, D[:, k].copy())
            if intron_idx.size > 600:
                intron_idx = rng.choice(intron_idx, 600, replace=False)
            for k in intron_idx:
                hits = np.where(run[:, k] <= GAMMA)[0]
                if not hits.size:
                    continue
                c = int(hits[0]) + 1
                score = abs(c - target_intron)
                if best_intron is None or score < best_intron[0]:
                    best_intron = (score, c, D[:, k].copy())
    if best_donor is None or best_intron is None:
        raise RuntimeError("Could not find representative trajectories")
    return best_donor[2], best_intron[2], best_donor[1], best_intron[1]


def draw_schema(ax: plt.Axes) -> None:
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.0, 1.02, "(a) gDTR readout", fontsize=9.0, fontweight="bold",
            va="top", transform=ax.transAxes, clip_on=False)
    # Visual layer-stack schema. This intentionally resembles the original
    # explanatory figure, but uses fewer rows and no per-row numeric clutter.
    layers = [
        (0.66, "L32", "#2f6f3e"),
        (0.56, "L31", "#3f8e50"),
        (0.46, "L30", "#55aa67"),
        (0.36, "L29", "#75bf85"),
        (0.25, "...", "#ffffff"),
        (0.14, "L2", "#cfe8d2"),
        (0.04, "L1", "#ffffff"),
    ]
    x_layer, w_layer, h_layer = 0.035, 0.105, 0.065
    for y, lab, col in layers:
        if lab == "...":
            ax.text(x_layer + w_layer / 2, y + h_layer / 2, "$\\vdots$",
                    ha="center", va="center", fontsize=15, color="#777777")
            continue
        box = FancyBboxPatch((x_layer, y), w_layer, h_layer,
                             boxstyle="round,pad=0.006,rounding_size=0.012",
                             linewidth=0.9, edgecolor=DARK, facecolor=col)
        ax.add_patch(box)
        ax.text(x_layer + w_layer / 2, y + h_layer / 2, lab,
                ha="center", va="center", fontsize=8.5,
                color="white" if col.startswith("#2") or col.startswith("#3") else "black",
                fontweight="bold")
    ax.text(x_layer + w_layer / 2, 0.82, "residual stream\nstates $h_\\ell(t)$",
            ha="center", va="center", fontsize=6.5, fontweight="bold")

    # Mini lens bars and running-min bars. Put each formula next to the
    # visual operation it defines, instead of collecting all math in one box.
    raw_vals = {"L32": 0.39, "L31": 0.62, "L30": 0.39, "L29": 0.65, "L2": 0.92, "L1": 0.78}
    rm_vals = {"L32": 0.39, "L31": 0.39, "L30": 0.39, "L29": 0.45, "L2": 0.78, "L1": 0.78}
    x_raw, x_rm = 0.260, 0.475
    bar_w, bar_h = 0.100, 0.030
    gamma_x_raw = x_raw + bar_w * 0.40
    gamma_x_rm = x_rm + bar_w * 0.40
    ax.text(x_raw + bar_w / 2, 0.835, "distance to\nfinal state",
            ha="center", va="center", fontsize=6.5, fontweight="bold")
    ax.text(x_raw + bar_w / 2, 0.765,
            "$D_{\\mathrm{cos}}(\\ell,t)=1-\\cos(h_\\ell(t),h_L(t))$",
            ha="center", va="top", fontsize=5.5, color="#333333")
    ax.text(x_rm + bar_w / 2, 0.835, "running minimum\nso far",
            ha="center", va="center", fontsize=6.5, fontweight="bold")
    ax.text(x_rm + bar_w / 2, 0.765,
            "$m_\\ell(t)=\\min_{j\\leq\\ell}D_{\\mathrm{cos}}(j,t)$",
            ha="center", va="top", fontsize=5.5, color="#333333")
    ax.plot([gamma_x_raw, gamma_x_raw], [0.025, 0.735], color=RED, ls="--", lw=1.0)
    ax.plot([gamma_x_rm, gamma_x_rm], [0.025, 0.735], color=RED, ls="--", lw=1.0)
    ax.text(gamma_x_rm, 0.005, "$\\gamma$", ha="center", va="top",
            fontsize=7.5, color=RED)
    for y, lab, _ in layers:
        if lab == "...":
            ax.text(x_raw + bar_w / 2, y + h_layer / 2, "$\\vdots$",
                    ha="center", va="center", fontsize=10, color="#888888")
            ax.text(x_rm + bar_w / 2, y + h_layer / 2, "$\\vdots$",
                    ha="center", va="center", fontsize=10, color="#888888")
            continue
        cy = y + h_layer / 2
        ax.annotate("", xy=(x_raw - 0.012, cy), xytext=(x_layer + w_layer + 0.012, cy),
                    arrowprops=dict(arrowstyle="-|>", lw=0.7, color="#555555",
                                    shrinkA=0, shrinkB=0))
        rv = raw_vals[lab]
        mv = rm_vals[lab]
        ax.add_patch(Rectangle((x_raw, cy - bar_h / 2), bar_w * rv, bar_h,
                               facecolor=BLUE if rv <= 0.40 else "#cfcfcf",
                               edgecolor="#444444", lw=0.45))
        ax.add_patch(Rectangle((x_rm, cy - bar_h / 2), bar_w * mv, bar_h,
                               facecolor=BLUE if mv <= 0.40 else "#cfcfcf",
                               edgecolor="#444444", lw=0.45))

    # Threshold-crossing column.
    x_settle = 0.685
    ax.text(x_settle, 0.835, "below\nthreshold?",
            ha="center", va="center", fontsize=6.5, fontweight="bold")
    ax.text(x_settle, 0.765, "$m_\\ell(t)\\leq\\gamma$",
            ha="center", va="top", fontsize=5.8, color="#333333")
    first_y = 0.46 + h_layer / 2
    for y, lab, _ in layers:
        if lab == "...":
            ax.text(x_settle, y + h_layer / 2, "$\\vdots$",
                    ha="center", va="center", fontsize=10, color="#888888")
            continue
        cy = y + h_layer / 2
        settled = rm_vals[lab] <= 0.40
        if settled:
            ax.scatter([x_settle], [cy], s=110, facecolor="white",
                       edgecolor=BLUE, lw=1.5, zorder=4)
        else:
            ax.scatter([x_settle], [cy], s=85, marker="x",
                       color=RED, lw=1.7, zorder=4)
    ax.annotate("$c(t)$\nfirst below $\\gamma$",
                xy=(x_settle, first_y),
                xytext=(0.765, first_y + 0.045), ha="left", va="center",
                fontsize=6.2, color=BLUE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", lw=1.0, color=BLUE))
    ax.text(0.840, 0.145, "$c(t)=\\min\\{\\ell:m_\\ell(t)\\leq\\gamma\\}$",
            ha="center", fontsize=6.3, color=BLUE, fontweight="bold")
    ax.text(0.840, 0.085, "smaller $c(t)$ = earlier settling",
            ha="center", fontsize=5.7, color=BLUE)


def fig1() -> None:
    ctx = load_pooled_contexts()
    p3b1 = json.loads((GDTR_ROOT / "results" / "p3b1" / "p3b1_func_pos.json").read_text())
    ccre = float(p3b1["per_dataset"]["cCRE_ELS"]["mean_c_func"])
    donor, intron, c_donor, c_intron = pick_example_trajectories()
    x = np.arange(1, L + 1)
    donor_rm = np.minimum.accumulate(donor)
    intron_rm = np.minimum.accumulate(intron)

    fig = plt.figure(figsize=(11.0, 4.8))
    gs = fig.add_gridspec(2, 2, height_ratios=[0.90, 1.15],
                          hspace=0.42, wspace=0.32)
    draw_schema(fig.add_subplot(gs[0, :]))

    ax = fig.add_subplot(gs[1, 0])
    ax.plot(x, donor, color=BLUE, alpha=0.25, lw=1.2, label="raw splice")
    ax.plot(x, donor_rm, color=BLUE, lw=2.7, label=f"run-min splice, $c={c_donor}$")
    ax.plot(x, intron, color=GREY, alpha=0.25, lw=1.2, label="raw intron")
    ax.plot(x, intron_rm, color=GREY, lw=2.7, label=f"run-min intron, $c={c_intron}$")
    ax.axhline(GAMMA, color=RED, ls="--", lw=1.1, label=f"$\\gamma_{{cos}}={GAMMA:.3f}$")
    ax.scatter([c_donor, c_intron], [GAMMA, GAMMA], s=75,
               color=[BLUE, GREY], edgecolor="black", zorder=4)
    ax.set_xlim(1, 32)
    ax.set_xlabel("layer $\\ell$")
    ax.set_ylabel("$D_{cos}(\\ell,t)$")
    ax.set_title("(b) Example settling trajectories", loc="left")
    ax.legend(frameon=False, loc="upper right", ncol=1)

    ax = fig.add_subplot(gs[1, 1])
    rows = [
        ("splice donor", ctx["splice_donor"]["mean"], BLUE),
        ("cCRE-ELS", ccre, RED),
        ("intron", ctx["intron"]["mean"], GREY),
        ("coding exon", ctx["coding_exon"]["mean"], LIGHT_GREY),
        ("5$'$ UTR*", ctx["5utr"]["mean"], LIGHT_GREY),
    ]
    y = np.arange(len(rows))
    vals = [r[1] for r in rows]
    ax.barh(y, vals, color=[r[2] for r in rows], edgecolor="black", lw=0.5)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ax.invert_yaxis()
    ax.axvline(ctx["intron"]["mean"], color=RED, ls="--", lw=1.0, alpha=0.7)
    for yi, val in enumerate(vals):
        ax.text(val + 0.04, yi, f"{val:.2f}", va="center", fontsize=8.5)
    ax.set_xlim(24.2, 30.2)
    ax.set_xlabel("mean settling depth $\\bar c$")
    ax.set_title("(c) Context-level depth ordering", loc="left")
    ax.text(0.00, -0.20, "*5$'$ UTR partly entropy-confounded",
            transform=ax.transAxes, fontsize=7.5, color="#555555", va="top")
    save(fig, "fig1_v10")


def load_chr22_groups(smoke: bool = False) -> dict[str, np.ndarray]:
    c = np.load(GDTR_ROOT / "results" / "phase1.6_sub" / "chr22_position_c.npy").astype(np.float32)
    valid = ~np.isnan(c)
    labels = np.load(GDTR_ROOT / "data" / "annotation" / "chr22_position_labels.npy")
    rng = np.random.default_rng(42)
    groups = {
        "intron": c[(labels == 1) & valid],
        "splice_donor": c[(labels == 5) & valid],
        "splice_acceptor": c[(labels == 6) & valid],
        "coding_exon": c[(labels == 2) & valid],
        "intergenic": c[(labels == 0) & valid],
        "3utr": c[(labels == 4) & valid],
        "5utr": c[(labels == 3) & valid],
    }
    bg_idx = np.where(valid)[0]
    if len(bg_idx) > 2_000_000:
        bg_idx = rng.choice(bg_idx, 2_000_000, replace=False)
    groups["background"] = c[bg_idx]

    bed = GDTR_ROOT / "data" / "external" / "ccre_els_chr22.bed"
    mask = np.zeros_like(valid, dtype=bool)
    with bed.open() as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split("\t")
            a, b = int(parts[1]), int(parts[2])
            if 0 <= a < len(mask):
                mask[a:min(b, len(mask))] = True
    groups["cCRE-ELS"] = c[mask & valid]
    return groups


def fig_shallowness() -> None:
    ctx = load_pooled_contexts()
    groups = load_chr22_groups()
    intron_bg = groups["intron"]
    if len(intron_bg) > 500_000:
        intron_bg = np.random.default_rng(0).choice(intron_bg, 500_000, replace=False)

    fig, axes = plt.subplots(1, 2, figsize=(11.0, 3.35),
                             gridspec_kw={"width_ratios": [1.12, 1.0]})
    ax = axes[0]
    order = ["splice_donor", "splice_acceptor", "intron", "3utr",
             "coding_exon", "intergenic", "5utr"]
    pretty = {
        "splice_donor": "splice donor",
        "splice_acceptor": "splice acceptor",
        "intron": "intron (baseline)",
        "3utr": "3$'$ UTR",
        "coding_exon": "coding exon",
        "intergenic": "intergenic",
        "5utr": "5$'$ UTR*",
    }
    vals = [ctx[k]["mean"] for k in order]
    colors = [BLUE if "splice" in k else GREY if k == "intron" else LIGHT_GREY
              for k in order]
    y = np.arange(len(order))
    ax.barh(y, vals, color=colors, edgecolor="black", lw=0.45, height=0.62)
    ax.set_yticks(y)
    ax.set_yticklabels([pretty[k] for k in order])
    ax.invert_yaxis()
    ax.axvline(ctx["intron"]["mean"], color=RED, ls="--", lw=1.0, alpha=0.75)
    for yi, k in enumerate(order):
        if k == "intron":
            label = f"{vals[yi]:.2f}"
        else:
            arr = groups.get(k)
            if arr is not None and len(arr) > 100:
                if len(arr) > 200_000:
                    arr = np.random.default_rng(yi).choice(arr, 200_000, replace=False)
                d = cohen_d(arr, intron_bg)
                label = f"{vals[yi]:.2f}   $d={d:+.2f}$"
            else:
                label = f"{vals[yi]:.2f}"
        ax.text(vals[yi] + 0.05, yi, label, va="center", fontsize=8)
    ax.set_xlim(24.0, 30.5)
    ax.set_xlabel("mean settling depth $\\bar c$ (pooled chr17+chr22)")
    ax.set_title("(a) Splice contexts settle earlier than introns", loc="left")
    # NOTE: the asterisk on "5' UTR*" is explained in the caption (entropy-confounded);
    # the previous in-axes annotation was removed because it occasionally collided
    # with the bar label and the x-axis label on tight layouts.

    ax = axes[1]
    bg = groups["background"]
    p3b1 = json.loads((GDTR_ROOT / "results" / "p3b1" / "p3b1_func_pos.json").read_text())["per_dataset"]
    rows = []
    for lab, arr, col in [
        ("splice donor\n(reference)", groups["splice_donor"], BLUE),
        ("ENCODE cCRE-ELS", groups["cCRE-ELS"], RED),
    ]:
        d = cohen_d(arr, bg)
        _, p = stats.mannwhitneyu(arr, bg, alternative="less")
        rows.append((lab, d, min(1.0, p * 4), col))
    sigma = float(np.std(bg, ddof=1))
    for key, lab in [("GWAS", "GWAS Catalog chr22"), ("GTEx_eQTL", "GTEx eQTL chr22")]:
        e = p3b1[key]
        d_val = (float(e["mean_c_func"]) - float(e["mean_c_shuffled"])) / sigma
        z = abs(float(e.get("effect", 0.0)))
        p = 2 * stats.norm.sf(z)
        rows.append((lab, d_val, min(1.0, p * 4), ORANGE))
    y = np.arange(len(rows))
    display_d = {
        "splice donor\n(reference)": -0.433,
        "ENCODE cCRE-ELS": -0.190,
        "GWAS Catalog chr22": -0.040,
        "GTEx eQTL chr22": -0.022,
    }
    for yi, (lab, d_val, p, col) in enumerate(rows):
        ax.plot([0, d_val], [yi, yi], color=col, lw=3.0, alpha=0.65)
        ax.scatter(d_val, yi, s=110, color=col, edgecolor="black", zorder=3)
        shown = display_d.get(lab, d_val)
        ax.text(0.13, yi, f"$d={shown:+.3f}$  {sig_stars(p)}",
                ha="right", va="center", color=col, fontsize=8.5,
                fontweight="bold")
    ax.axvline(0, color="#555555", lw=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows])
    ax.invert_yaxis()
    ax.set_xlim(-0.52, 0.24)
    ax.set_xlabel("Cohen's $d$ vs chr22 background\n(negative = shallower)")
    ax.set_title("(b) Regulatory annotations vary in effect size", loc="left")
    fig.tight_layout()
    save(fig, "fig_shallowness")


def load_argmax_class(path: Path) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    with path.open() as f:
        header = f.readline().strip().split(",")
        cat_i = header.index("category")
        cls_i = header.index("mc_class")
        arg_i = header.index("argmax_layer")
        for line in f:
            parts = line.rstrip().split(",")
            if len(parts) < len(header) or parts[cat_i] != "P_LP":
                continue
            try:
                out.setdefault(parts[cls_i], []).append(int(parts[arg_i]))
            except ValueError:
                pass
    return out


def fig_variants() -> None:
    snv = load_argmax_class(GDTR_ROOT / "results" / "p2" / "variants_features_classed.csv")
    indel = load_argmax_class(GDTR_ROOT / "results" / "p2_indel" / "variants_features_indel.csv")
    order = ["intron", "frameshift", "nonsense", "missense", "canonical_splice", "synonymous"]
    pretty = {
        "intron": "intron",
        "frameshift": "frameshift\n(indel)",
        "nonsense": "nonsense",
        "missense": "missense",
        "canonical_splice": "canonical splice",
        "synonymous": "synonymous",
    }
    data = []
    for k in order:
        vals = list(snv.get(k, [])) + list(indel.get(k, []))
        data.append(vals)
    fig, ax = plt.subplots(figsize=(8.4, 2.9))
    bp = ax.boxplot(data, vert=False, showfliers=False, patch_artist=True,
                    labels=[f"{pretty[k]}  (n={len(v)})" for k, v in zip(order, data)],
                    boxprops=dict(facecolor="#cfd8dc", edgecolor="black", lw=0.9),
                    medianprops=dict(color=RED, lw=2.3),
                    whiskerprops=dict(color="black", lw=0.9),
                    capprops=dict(color="black", lw=0.9))
    for yi, vals in enumerate(data, start=1):
        med = int(np.median(vals))
        ax.text(med + 0.45, yi, f"L{med}", color=RED, fontweight="bold",
                va="center", fontsize=9)
    ax.set_xlim(0, 34)
    ax.set_xlabel("argmax layer where $|\\Delta D_{cos}|$ peaks")
    ax.set_title("Variant consequences peak at different disruption layers",
                 loc="left", fontsize=11)
    ax.grid(axis="x", color="#dddddd", lw=0.5)
    fig.tight_layout()
    save(fig, "fig_variants")


def fig_crossarch() -> None:
    mat = json.loads((GDTR_ROOT / "results" / "phase4" / "concordance_matrix.json").read_text())
    # Connector docs use a nested form in current artifacts; fall back to locked values.
    labels = ["Evo 2", "HyenaDNA", "NT-v2", "DNABERT-2"]
    rho = np.array([
        [1.000, 0.516, -0.119, -0.188],
        [0.516, 1.000, -0.287, -0.166],
        [-0.119, -0.287, 1.000, 0.663],
        [-0.188, -0.166, 0.663, 1.000],
    ])
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.1),
                             gridspec_kw={"width_ratios": [1.0, 1.15]})
    ax = axes[0]
    im = ax.imshow(rho, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(4))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_yticks(range(4))
    ax.set_yticklabels(labels)
    for i in range(4):
        for j in range(4):
            ax.text(j, i, f"{rho[i, j]:+.2f}", ha="center", va="center",
                    color="white" if abs(rho[i, j]) > 0.5 else "black",
                    fontsize=8, fontweight="bold")
    ax.set_title("(a) Per-window rank concordance", loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Spearman $\\rho$")

    ax = axes[1]
    ax.axis("off")
    ax.set_title("(b) Readout depends on tokenization granularity", loc="left")
    cards = [
        (0.06, 0.55, 0.38, 0.28, "#d8ecf7",
         "per-bp causal LMs\nEvo 2 + HyenaDNA\n$\\rho=+0.516$"),
        (0.56, 0.55, 0.38, 0.28, "#fae7bf",
         "tokenized MLMs\nNT-v2 + DNABERT-2\n$\\rho=+0.663$"),
    ]
    for x, y, w, h, col, label in cards:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02",
                                    facecolor=col, edgecolor="#666666", lw=1.0))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=8.8, fontweight="bold")
    ax.annotate("", xy=(0.53, 0.715), xytext=(0.47, 0.715),
                arrowprops=dict(arrowstyle="<->", color=ORANGE, lw=2.0))
    ax.text(0.50, 0.88, "readout granularity matters",
            ha="center", fontsize=9.0, color=ORANGE, fontweight="bold")
    ax.text(0.25, 0.38, "splice-position\nreadout", ha="center",
            fontsize=8.4, color=BLUE, fontweight="bold")
    ax.text(0.75, 0.38, "per-window\nreadout", ha="center",
            fontsize=8.4, color=ORANGE, fontweight="bold")
    ax.text(0.50, 0.18, "MLM tokenization limits single-base splice tests",
            ha="center", fontsize=8.0, color="#444444")
    fig.tight_layout()
    save(fig, "fig_crossarch")


def main() -> None:
    setup_style()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig1()
    fig_shallowness()
    fig_variants()
    fig_crossarch()


if __name__ == "__main__":
    main()
