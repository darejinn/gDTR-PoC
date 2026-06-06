from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "figures" / "fig1_v10_source_with_panel_b.png"
OUT = ROOT / "figures" / "fig1_trajectory.png"


def main() -> None:
    im = Image.open(SOURCE).convert("RGB")
    # Keep only the old panel (b). The right-hand context ordering panel is
    # intentionally dropped because Fig. 2(a) now carries that result.
    crop = im.crop((0, 420, 1065, im.height))
    canvas = Image.new("RGB", (1120, crop.height + 30), "white")
    canvas.paste(crop, (30, 0))
    canvas.save(OUT)


if __name__ == "__main__":
    main()
