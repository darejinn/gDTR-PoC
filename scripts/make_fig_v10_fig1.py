"""Make Fig 1 (v10 conceptual) — replaces user-supplied schematic.

2-panel layout, total height ≤ 3 inches:
  (a) Two real D_cos(ℓ) trajectories overlaid (splice donor vs intron),
      γ_cos as red horizontal, settling-layer markers.
  (b) Compact hierarchy bar of mean settling depth c̄ across contexts:
      splice donor / cCRE-ELS / coding exon / intron baseline / 5'UTR.
      Intron baseline as red dashed reference.

Design intent: a reader unfamiliar with the framework can read Fig 1 in
~10 seconds and grasp (i) "settling depth = first layer at which the
running-min cosine distance crosses γ" and (ii) "biologically salient
positions settle earlier; 5'UTR is anomalous".

Inputs (server):
  results/phase1.6/chr22_cache.h5            — D_cos[12978, 32, 6000]
  data/annotation/chr22_position_labels.npy  — context labels per bp
  results/p1a/calib_val_table.csv            — pooled mean c per context
  results/p3b1/p3b1_func_pos.json            — cCRE-ELS mean c
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

import numpy as np
import h5py
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

GDTR_ROOT = Path(os.environ.get("GDTR_ROOT", "/root/gDTR")).expanduser()
GAMMA_COS = 0.39663
N_LAYERS = 32
OUT_DIR = GDTR_ROOT / "results" / "figures_v3"

LOG = logging.getLogger("make_fig_v10_fig1")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def stylize():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })


def find_example_trajectories():
    """Scan all chr22 windows, accumulate per-position c values for donor
    (label==5) and intron (label==1). Pick a donor whose c is close to
    the chr22 donor mean (≈25) and an intron whose c is close to the
    chr22 intron mean (≈28). Return D_cos[L] for the two picked positions
    so that the trajectories shown in Fig 1(a) are representative, not
    extremal."""
    cache_path = GDTR_ROOT / "results" / "phase1.6" / "chr22_cache.h5"
    labels = np.load(GDTR_ROOT / "data" / "annotation" /
                     "chr22_position_labels.npy")

    target_donor_c = 25
    target_intron_c = 28

    best_donor = None     # (abs_diff, window_idx, in_window_pos, c, traj)
    best_intron = None
    with h5py.File(cache_path, "r") as f:
        starts = f["starts"][:]
        for wi in range(len(starts)):
            s = int(starts[wi])
            T = 6000
            slab = labels[s:s + T]
            donor_idx = np.where(slab == 5)[0]
            intron_idx = np.where(slab == 1)[0]
            if donor_idx.size == 0 and intron_idx.size == 0:
                continue
            D = f["D_cos"][int(wi)].astype(np.float32)
            run_min = np.minimum.accumulate(D, axis=0)

            for k in donor_idx:
                hits = np.where(run_min[:, k] <= GAMMA_COS)[0]
                c = int(hits[0]) + 1 if hits.size else N_LAYERS + 1
                diff = abs(c - target_donor_c)
                if best_donor is None or diff < best_donor[0]:
                    best_donor = (diff, wi, int(k), c, D[:, k].copy())

            # intron is huge — sample at most 500 random per window for
            # speed; restrict to settled positions to avoid c=33 noise
            if intron_idx.size > 500:
                ix = np.random.default_rng(wi).choice(intron_idx, 500,
                                                       replace=False)
            else:
                ix = intron_idx
            for k in ix:
                hits = np.where(run_min[:, k] <= GAMMA_COS)[0]
                if not hits.size:
                    continue  # never-settled intron, skip
                c = int(hits[0]) + 1
                diff = abs(c - target_intron_c)
                if best_intron is None or diff < best_intron[0]:
                    best_intron = (diff, wi, int(k), c, D[:, k].copy())

    donor_traj = best_donor[4]
    intron_traj = best_intron[4]
    donor_pos = int(starts[best_donor[1]]) + best_donor[2]
    intron_pos = int(starts[best_intron[1]]) + best_intron[2]
    LOG.info("donor: window %d  pos %d  c=%d (target %d)",
              best_donor[1], donor_pos, best_donor[3], target_donor_c)
    LOG.info("intron: window %d  pos %d  c=%d (target %d)",
              best_intron[1], intron_pos, best_intron[3], target_intron_c)
    return donor_traj, intron_traj, donor_pos, intron_pos


def settling_layer(d_traj):
    rm = np.minimum.accumulate(d_traj)
    hits = np.where(rm <= GAMMA_COS)[0]
    return int(hits[0]) + 1 if hits.size else N_LAYERS + 1


def draw_schema(ax):
    """Layered, intuitive schema (inspired by user's reference figure):

      vertical stack of layer boxes (32 .. 1, with ellipsis)
      → per-layer cosine UR lens (mini bar = D_cos sample)
      → per-layer running-min (mini bar = run-min sample)
      → numeric D_cos column
      → Settled / Not-Settled markers (○ = settled, × = unsettled)
    """
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9.6)
    ax.axis("off")

    # Eight rows shown as a sample of the 32-layer stack:
    #   32, 31, 30, 29, ..., 2, 1
    # For each row store: y-center, label, run-min D_cos value, settled flag
    rows = [
        (7.2, "32$^{\\mathrm{nd}}$ Layer", 0.39, True),
        (6.2, "31$^{\\mathrm{st}}$ Layer", 0.40, True),
        (5.2, "30$^{\\mathrm{th}}$ Layer", 0.39, True),
        (4.2, "29$^{\\mathrm{th}}$ Layer", 0.42, False),
        (3.2, "$\\ldots$",                None, None),
        (2.2, "$\\ldots$",                None, None),
        (1.2, "2$^{\\mathrm{nd}}$ Layer",  0.78, False),
        (0.2, "1$^{\\mathrm{st}}$ Layer",  0.92, False),
    ]

    # --- Layer column (left, vertical green stack) ---
    box_x = 0.4; box_w = 2.1
    greens = ["#2e6b3c", "#3d8a4d", "#4ea561", "#67b878",
               "#a3d6ad", "#a3d6ad", "#cce6cf", "#ffffff"]
    for (yc, lbl, _, _), col in zip(rows, greens):
        if lbl == "$\\ldots$":
            ax.text(box_x + box_w / 2, yc + 0.4, "$\\vdots$",
                     ha="center", va="center", fontsize=18, color="#666666")
            continue
        rect = FancyBboxPatch(
            (box_x, yc), box_w, 0.75,
            boxstyle="round,pad=0.02,rounding_size=0.15",
            linewidth=0.9, edgecolor="black", facecolor=col, alpha=0.95)
        ax.add_patch(rect)
        ax.text(box_x + box_w / 2, yc + 0.38, lbl,
                ha="center", va="center", fontsize=8.5,
                color="white" if col in ("#2e6b3c", "#3d8a4d") else "black",
                fontweight="bold")

    # --- Mini-histogram cluster: cosine UR lens (raw D_cos sample) ---
    def mini_hist(cx, yc, color="#bbbbbb", peak_layer="middle"):
        """Draw a tiny 5-bar histogram centered at (cx, yc)."""
        bar_w = 0.10
        gap = 0.02
        if peak_layer == "right":
            heights = [0.10, 0.18, 0.30, 0.45, 0.30]
        elif peak_layer == "left":
            heights = [0.40, 0.30, 0.18, 0.10, 0.06]
        elif peak_layer == "middle":
            heights = [0.10, 0.25, 0.42, 0.25, 0.10]
        for i, h in enumerate(heights):
            x = cx - 2 * (bar_w + gap) + i * (bar_w + gap)
            ax.add_patch(Rectangle((x, yc + 0.10), bar_w, h * 0.45,
                                     facecolor=color, edgecolor="#444444",
                                     linewidth=0.4))

    lens_x = 4.0
    runmin_x = 5.6
    val_x = 7.2
    for yc, lbl, dcos_val, settled in rows:
        if lbl == "$\\ldots$":
            ax.text(lens_x, yc + 0.4, "$\\vdots$",
                     ha="center", va="center", fontsize=14, color="#888888")
            ax.text(runmin_x, yc + 0.4, "$\\vdots$",
                     ha="center", va="center", fontsize=14, color="#888888")
            ax.text(val_x, yc + 0.4, "$\\vdots$",
                     ha="center", va="center", fontsize=14, color="#888888")
            continue
        # Determine peak side based on layer depth (deeper = sharper toward right)
        if dcos_val < 0.45:
            peak = "right"
        elif dcos_val < 0.70:
            peak = "middle"
        else:
            peak = "left"
        # Cosine UR lens histogram (raw)
        mini_hist(lens_x, yc, color="#dddddd", peak_layer=peak)
        # Running-min histogram (sharper, biased left)
        mini_hist(runmin_x, yc, color="#9ec5e6",
                   peak_layer="right" if dcos_val < 0.70 else peak)
        # Numeric value
        ax.text(val_x, yc + 0.38, f"{dcos_val:.2f}",
                 ha="center", va="center", fontsize=9.0)
        # Arrow: layer → lens
        ax.add_patch(FancyArrowPatch(
            (box_x + box_w + 0.05, yc + 0.38), (lens_x - 0.65, yc + 0.38),
            arrowstyle="-|>", mutation_scale=8, linewidth=0.7,
            color="#555555"))
        # Arrow: lens → run-min
        ax.add_patch(FancyArrowPatch(
            (lens_x + 0.55, yc + 0.38), (runmin_x - 0.65, yc + 0.38),
            arrowstyle="-|>", mutation_scale=8, linewidth=0.7,
            color="#555555"))
        # Arrow: run-min → value
        ax.add_patch(FancyArrowPatch(
            (runmin_x + 0.55, yc + 0.38), (val_x - 0.30, yc + 0.38),
            arrowstyle="-", mutation_scale=8, linewidth=0.7,
            color="#555555"))

    # Section labels above the columns
    ax.text(lens_x, 8.05, "Cosine UR\nLens",
             ha="center", va="bottom", fontsize=8.5, fontweight="bold",
             color="#333333")
    ax.text(runmin_x, 8.05, "Running\nMin $D_{\\cos}$",
             ha="center", va="bottom", fontsize=8.5, fontweight="bold",
             color="#333333")
    ax.text(val_x, 8.05, "$D_{\\cos}$ value",
             ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # Dashed boundary boxes around lens+run-min and value columns
    for x_left, x_right in [(lens_x - 0.95, runmin_x + 0.95)]:
        rect = Rectangle((x_left, -0.1), x_right - x_left, 7.95,
                          fill=False, linestyle="--", linewidth=0.7,
                          edgecolor="#3a5f3a", alpha=0.6)
        ax.add_patch(rect)
    rect_v = Rectangle((val_x - 0.6, -0.1), 1.2, 7.95,
                        fill=False, linestyle="--", linewidth=0.7,
                        edgecolor="#3a5f3a", alpha=0.6)
    ax.add_patch(rect_v)

    # --- Settled / Not-Settled column on the right ---
    bracket_x = val_x + 0.95
    settle_x = bracket_x + 0.7
    ax.plot([bracket_x, bracket_x + 0.4, bracket_x + 0.4, bracket_x],
             [0.45, 0.45, 7.65, 7.65], color="black", linewidth=1.0)
    ax.plot([bracket_x + 0.4, bracket_x + 0.6], [4.0, 4.0],
             color="black", linewidth=1.0)
    for yc, lbl, dcos_val, settled in rows:
        if lbl == "$\\ldots$":
            ax.text(settle_x + 0.6, yc + 0.4, "$\\vdots$",
                     ha="center", va="center", fontsize=14, color="#888888")
            continue
        if settled:
            ax.scatter(settle_x + 0.6, yc + 0.38, s=140, marker="o",
                        facecolor="white", edgecolor="#1f3b6b", linewidth=1.6,
                        zorder=3)
        else:
            ax.scatter(settle_x + 0.6, yc + 0.38, s=140, marker="x",
                        color="#c0392b", linewidths=1.8, zorder=3)
    ax.text(settle_x + 0.6, 8.05, "Settled\nlayer?",
             ha="center", va="bottom", fontsize=8.5, fontweight="bold",
             color="#333333")
    # Annotation: arrow to first settled (top-most non-settled boundary)
    settled_y_first = rows[2][0] + 0.38   # last settled (30th layer)
    ax.annotate("first\nsettled\n($c(t)$)",
                xy=(settle_x + 0.6, settled_y_first),
                xytext=(settle_x + 1.6, settled_y_first - 0.5),
                fontsize=8.0, fontweight="bold", color="#1f3b6b",
                arrowprops=dict(arrowstyle="->", color="#1f3b6b",
                                  linewidth=0.9))
    # Title strip (top); details deferred to caption
    ax.text(0.0, 9.45, "(a) gDTR pipeline",
             fontsize=10.5, fontweight="bold", ha="left", va="top")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stylize()

    donor_traj, intron_traj, dpos, ipos = find_example_trajectories()
    L = N_LAYERS
    x = np.arange(1, L + 1)

    # Hierarchy values from existing analyses
    p1a_csv = GDTR_ROOT / "results" / "p1a" / "calib_val_table.csv"
    rows = []
    with p1a_csv.open() as f:
        header = f.readline().rstrip().split(",")
        for ln in f:
            d = dict(zip(header, ln.rstrip().split(",")))
            rows.append({"chrom": d["chrom"], "context": d["context"],
                         "n": int(d["n"]), "mean_c": float(d["mean_c"])})

    def pooled(ctx):
        sel = [r for r in rows if r["context"] == ctx]
        if not sel:
            return float("nan"), 0
        n = sum(r["n"] for r in sel)
        m = sum(r["mean_c"] * r["n"] for r in sel) / n
        return m, n

    intron_mean, _ = pooled("intron")
    splice_d_mean, _ = pooled("splice_donor")
    exon_mean, _ = pooled("coding_exon")
    utr5_mean, _ = pooled("5utr")

    # cCRE-ELS from p3b1
    p3b1 = json.loads(
        (GDTR_ROOT / "results" / "p3b1" / "p3b1_func_pos.json").read_text())
    cCRE_mean = float(p3b1["per_dataset"]["cCRE_ELS"]["mean_c_func"])

    hierarchy = [
        ("splice donor", splice_d_mean, "#1f77b4"),
        ("cCRE-ELS", cCRE_mean, "#d62728"),
        ("coding exon", exon_mean, "#bbbbbb"),
        ("intron (baseline)", intron_mean, "#7f7f7f"),
        ("5$'$ UTR", utr5_mean, "#bbbbbb"),
    ]

    # ---- Figure ----  3-element layout: tall schema (a) on top spanning
    # full width, then data panels (b) and (c) on a shorter row below.
    fig = plt.figure(figsize=(11.0, 5.4))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.4, 1.0],
                          hspace=0.30, wspace=0.30)

    ax_schema = fig.add_subplot(gs[0, :])
    draw_schema(ax_schema)

    ax_traj = fig.add_subplot(gs[1, 0])
    ax_hier = fig.add_subplot(gs[1, 1])
    axes = [ax_traj, ax_hier]

    # Panel B: two trajectories (was panel a)
    ax = axes[0]
    rm_d = np.minimum.accumulate(donor_traj)
    rm_i = np.minimum.accumulate(intron_traj)
    c_d = settling_layer(donor_traj)
    c_i = settling_layer(intron_traj)
    ax.plot(x, donor_traj, "-", color="#1f77b4", alpha=0.4, linewidth=1.0,
            label="raw $D_{\\cos}$ (splice)")
    ax.plot(x, rm_d, "-", color="#1f77b4", linewidth=2.4,
            label=f"run-min (splice, $c={c_d}$)")
    ax.plot(x, intron_traj, "-", color="#7f7f7f", alpha=0.4, linewidth=1.0,
            label="raw $D_{\\cos}$ (intron)")
    ax.plot(x, rm_i, "-", color="#7f7f7f", linewidth=2.4,
            label=f"run-min (intron, $c={c_i}$)")
    ax.axhline(GAMMA_COS, color="#d62728", linestyle="--", linewidth=1.0,
               label=f"$\\gamma_{{\\cos}}={GAMMA_COS:.2f}$")
    ax.scatter([c_d], [GAMMA_COS], s=80, color="#1f77b4", zorder=4,
               edgecolor="black", linewidth=0.6)
    ax.scatter([c_i], [GAMMA_COS], s=80, color="#7f7f7f", zorder=4,
               edgecolor="black", linewidth=0.6)
    ax.set_xlim(1, L)
    ax.set_xlabel("layer $\\ell$")
    ax.set_ylabel("$D_{\\cos}(\\ell, t)$")
    ax.set_title("(b) Per-token settling depth on two real chr22 positions",
                 loc="left", fontsize=9.5)
    ax.legend(loc="upper right", frameon=False, fontsize=7.5)

    # Panel B: hierarchy
    ax = axes[1]
    labels = [h[0] for h in hierarchy]
    means = [h[1] for h in hierarchy]
    colors = [h[2] for h in hierarchy]
    y = np.arange(len(hierarchy))
    bars = ax.barh(y, means, color=colors, height=0.65,
                   edgecolor="black", linewidth=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.axvline(intron_mean, color="#d62728", linestyle="--", linewidth=0.9,
               alpha=0.7)
    ax.set_xlim(24, 30.5)
    ax.set_xlabel("mean settling depth $\\bar c$  (pooled chr17+chr22)")
    ax.set_title("(c) Biological hierarchy of settling depth", loc="left",
                  fontsize=9.5)
    for b, m in zip(bars, means):
        ax.text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2,
                f"{m:.2f}", va="center", fontsize=8)

    fig.tight_layout()
    out_pdf = OUT_DIR / "fig1_v10.pdf"
    out_png = OUT_DIR / "fig1_v10.png"
    fig.savefig(out_pdf)
    fig.savefig(out_png, dpi=200)
    plt.close(fig)
    LOG.info("wrote %s + .png", out_pdf)
    meta = {"donor_pos": int(dpos), "intron_pos": int(ipos),
             "donor_c": int(c_d), "intron_c": int(c_i),
             "hierarchy": [(l, float(m)) for l, m, _ in hierarchy]}
    (OUT_DIR / "fig1_v10_meta.json").write_text(
        json.dumps(meta, indent=2, default=str))


if __name__ == "__main__":
    main()
