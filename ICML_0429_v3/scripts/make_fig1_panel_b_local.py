"""Reproduce Fig 1 panel (b) — example settling trajectories.

Faithful to the settling-trajectory definition (Eq. 1, Eq. 2 of the
manuscript):

  D_cos(ell, t) = 1 - cos(h_ell(t), h_norm(t))
  c(t)          = min { ell : runmin(D_cos)(ell, t) <= gamma_cos }

The illustrative trajectories below are SYNTHETIC but follow the
definition exactly: both raw curves are anchored near 1.0 at L=1
(orthogonal embedding) and oscillate non-monotonically; the run-min
curves are computed as the actual running minimum of the corresponding
raw curve. Splice donor's run-min reaches gamma=0.397 first at L=22;
intronic run-min only at L=31.

The TikZ panel (b) inside `figures/fig1_combined.tex` uses the same raw
coordinates with manually-pre-computed run-min steps. Keeping these two
sources in sync is important — if you edit one, edit the other.

Run:
    python scripts/make_fig1_panel_b_local.py
Output:
    figures/fig1_panel_b.{png,pdf}
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

V3_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = V3_DIR / "figures"

GAMMA = 0.397
BLUE = "#1f77b4"
BLUE_LIGHT = "#5a9bd4"  # mid-blue for thicker raw line readability
GREY = "#7f7f7f"
GREY_LIGHT = "#9b9b9b"  # mid-grey for thicker raw line readability
RED = "#d62728"


# ----------------------------------------------------------------------
# RAW trajectories — synthetic but follow the settling-trajectory
# definition. Both anchored near 1.0 at L=1 (residual stream is
# orthogonal to h_norm at the embedding); occasional bumps above 1.0
# are valid (cos can be negative → D_cos > 1). MUST stay in sync with
# the TikZ panel-(b) inside figures/fig1_combined.tex.
# ----------------------------------------------------------------------

# Splice donor: noisy descent that first crosses gamma at L=22.
RAW_SPLICE = [
    (1, 1.00), (2, 0.98), (3, 1.02), (4, 0.95), (5, 0.93), (6, 0.96),
    (7, 0.88), (8, 0.85), (9, 0.92), (10, 0.78), (11, 0.85),
    (12, 0.62), (13, 0.55), (14, 0.62), (15, 0.48), (16, 0.55),
    (17, 0.45), (18, 0.50), (19, 0.43), (20, 0.45), (21, 0.42),
    (22, 0.397),  # first sub-gamma — defines splice c=22
    (23, 0.50), (24, 0.43), (25, 0.45), (26, 0.50), (27, 0.42),
    (28, 0.40), (29, 0.45), (30, 0.42), (31, 0.40), (32, 0.41),
]

# Intronic position: gradual descent, never sub-gamma until L=31.
RAW_INTRON = [
    (1, 1.00), (2, 1.05), (3, 0.97), (4, 1.02), (5, 0.95), (6, 0.93),
    (7, 0.95), (8, 0.88), (9, 0.92), (10, 0.85), (11, 0.83),
    (12, 0.85), (13, 0.78), (14, 0.80), (15, 0.74), (16, 0.78),
    (17, 0.72), (18, 0.75), (19, 0.68), (20, 0.72), (21, 0.65),
    (22, 0.68), (23, 0.62), (24, 0.65), (25, 0.58), (26, 0.62),
    (27, 0.55), (28, 0.58), (29, 0.50), (30, 0.45),
    (31, 0.397),  # first sub-gamma — defines intron c=31
    (32, 0.42),
]


def _xy(coords):
    arr = np.asarray(coords, dtype=float)
    return arr[:, 0], arr[:, 1]


def running_min(coords):
    """Return (x, runmin(y)). Defines the run-min trace exactly per
    Eq. 2 of the manuscript: at each layer, value = min over all values
    seen so far."""
    x, y = _xy(coords)
    rm = np.minimum.accumulate(y)
    return x, rm


def setup_style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "legend.fontsize": 8.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


def main() -> None:
    setup_style()
    fig, ax = plt.subplots(figsize=(7.4, 3.6))

    # gamma threshold (drawn first so traces sit on top of it)
    ax.axhline(GAMMA, color=RED, ls="--", lw=1.0, zorder=1,
               label=f"$\\gamma_{{\\cos}}={GAMMA:.3f}$")

    # raw splice (mid-weight so the line is readable)
    x, y = _xy(RAW_SPLICE)
    ax.plot(x, y, color=BLUE_LIGHT, lw=1.4, alpha=0.95,
            label="raw splice", zorder=2)

    # run-min splice — actual running minimum of raw splice
    x_rm, y_rm = running_min(RAW_SPLICE)
    ax.plot(x_rm, y_rm, color=BLUE, lw=2.4,
            label="run-min splice, $c=22$",
            drawstyle="steps-post", zorder=4)

    # raw intron (mid-weight so the line is readable)
    x, y = _xy(RAW_INTRON)
    ax.plot(x, y, color=GREY_LIGHT, lw=1.4, alpha=0.95,
            label="raw intron", zorder=3)

    # run-min intron — actual running minimum of raw intron
    x_rm, y_rm = running_min(RAW_INTRON)
    ax.plot(x_rm, y_rm, color=GREY, lw=2.4,
            label="run-min intron, $c=31$",
            drawstyle="steps-post", zorder=5)

    # settling-circle markers at the first sub-gamma layer (the
    # crossing point used to define c(t))
    ax.scatter([22], [GAMMA], s=110, color=BLUE, edgecolor="black",
               lw=0.8, zorder=6)
    ax.scatter([31], [GAMMA], s=110, color=GREY, edgecolor="black",
               lw=0.8, zorder=6)

    ax.set_xlim(0.5, 32.5)
    ax.set_ylim(0.30, 1.30)
    ax.set_xticks([5, 10, 15, 20, 25, 30])
    ax.set_yticks([0.4, 0.6, 0.8, 1.0, 1.2])
    ax.set_xlabel("layer $\\ell$")
    ax.set_ylabel("$D_{\\cos}(\\ell, t)$")
    ax.set_title("(b) Example settling trajectories", loc="left",
                 fontsize=12)

    handles, labels = ax.get_legend_handles_labels()
    order = ["raw splice", "run-min splice, $c=22$",
             "raw intron", "run-min intron, $c=31$",
             f"$\\gamma_{{\\cos}}={GAMMA:.3f}$"]
    by_label = dict(zip(labels, handles))
    # Legend OUTSIDE plot, on the right margin — the plot stays
    # unobstructed and the user can read every trace cleanly.
    ax.legend([by_label[k] for k in order if k in by_label],
              [k for k in order if k in by_label],
              loc="upper left", bbox_to_anchor=(1.02, 1.0),
              frameon=False, borderpad=0.0)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "fig1_panel_b.png", dpi=300)
    fig.savefig(OUT_DIR / "fig1_panel_b.pdf")
    plt.close(fig)
    print(f"wrote {OUT_DIR / 'fig1_panel_b.png'}")
    print(f"wrote {OUT_DIR / 'fig1_panel_b.pdf'}")

    # Sanity check that printed run-min crossings match the markers.
    x_rm, y_rm = running_min(RAW_SPLICE)
    splice_c = int(x_rm[np.argmax(y_rm <= GAMMA)])
    x_rm, y_rm = running_min(RAW_INTRON)
    intron_c = int(x_rm[np.argmax(y_rm <= GAMMA)])
    print(f"splice c = {splice_c} (expected 22)")
    print(f"intron c = {intron_c} (expected 31)")


if __name__ == "__main__":
    main()
