from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures" / "fig1_v10.png"
PDF = ROOT / "figures" / "fig1_v10.pdf"
SOURCE = ROOT / "figures" / "fig1_v10_source_with_panel_b.png"

BLUE = "#1f77b4"
GREEN = "#2f6f3e"
GREEN2 = "#3f8e50"
GREEN3 = "#55aa67"
GREEN4 = "#75bf85"
PALE = "#cfe8d2"
DARK = "#222222"
GREY = "#d7d7d7"
RED = "#d62728"

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(BOLD if bold else FONT, size=size)


def centered(draw: ImageDraw.ImageDraw, xy: tuple[float, float], text: str,
             fnt: ImageFont.FreeTypeFont, fill: str = "black",
             spacing: int = 4) -> None:
    x, y = xy
    box = draw.multiline_textbbox((0, 0), text, font=fnt, spacing=spacing, align="center")
    w, h = box[2] - box[0], box[3] - box[1]
    draw.multiline_text((x - w / 2, y - h / 2), text, font=fnt, fill=fill,
                        spacing=spacing, align="center")


def rounded_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                fill: str, outline: str = DARK, width: int = 4, radius: int = 10) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int],
          fill: str = "#555555", width: int = 4) -> None:
    draw.line([start, end], fill=fill, width=width)
    x, y = end
    draw.polygon([(x, y), (x - 18, y - 9), (x - 18, y + 9)], fill=fill)


def main() -> None:
    if not SOURCE.exists():
        Image.open(FIG).convert("RGB").save(SOURCE)

    source = Image.open(SOURCE).convert("RGB")
    w = source.size[0]
    top_h = 500
    out_h = 1180
    base = Image.new("RGB", (w, out_h), "white")
    draw = ImageDraw.Draw(base)

    title = font(38, True)
    head = font(27, True)
    small = font(19)
    small_bold = font(19, True)
    layer_font = font(34, True)
    tiny = font(18)

    draw.text((110, 18), "(a) gDTR readout", font=title, fill="black")

    # Column anchors.
    x_layer = 285
    layer_w, layer_h = 260, 34
    xs = {
        "raw": 715,
        "rm": 1125,
        "thr": 1515,
        "ct": 1855,
    }

    centered(draw, (x_layer, 104), "residual stream\nstates hℓ(t)", head)
    centered(draw, (xs["raw"], 92), "distance to final state", head)
    centered(draw, (xs["raw"], 137),
             "Dcos(ℓ,t) = 1 - cos( hℓ(t), hL(t) )", small, "#333333")
    centered(draw, (xs["raw"], 167),
             "compare this layer with the final layer", tiny, "#555555")

    centered(draw, (xs["rm"], 92), "running minimum so far", head)
    centered(draw, (xs["rm"], 140), "mℓ(t) = min over j≤ℓ of Dcos(j,t)",
             small, "#333333")

    centered(draw, (xs["thr"], 92), "below threshold?", head)
    centered(draw, (xs["thr"], 140), "mℓ(t) ≤ γ", small, "#333333")

    centered(draw, (xs["ct"], 104), "settling depth", head)
    centered(draw, (xs["ct"], 150), "c(t) = first ℓ with mℓ(t) ≤ γ",
             small_bold, BLUE)
    centered(draw, (xs["ct"], 182), "smaller c(t) = earlier settling", tiny, BLUE)

    layers = [
        ("L32", GREEN, 0.39, 0.39, True),
        ("L31", GREEN2, 0.62, 0.39, True),
        ("L30", GREEN3, 0.39, 0.39, True),
        ("L29", GREEN4, 0.65, 0.45, False),
        ("...", None, None, None, None),
        ("L2", PALE, 0.92, 0.78, False),
        ("L1", "white", 0.78, 0.78, False),
    ]
    ys = [205, 255, 305, 355, 390, 425, 462]
    bar_w, bar_h = 225, 20
    gamma_frac = 0.40

    for (label, fill, raw, rm, settled), y in zip(layers, ys):
        if label == "...":
            draw.line([(x_layer, y - 14), (x_layer, y + 14)], fill="#888888", width=5)
            centered(draw, (xs["raw"], y), "...", small_bold, "#777777")
            centered(draw, (xs["rm"], y), "...", small_bold, "#777777")
            centered(draw, (xs["thr"], y), "...", small_bold, "#777777")
            continue

        box = (x_layer - layer_w // 2, y - layer_h // 2,
               x_layer + layer_w // 2, y + layer_h // 2)
        rounded_box(draw, box, fill)
        txt_color = "white" if fill in {GREEN, GREEN2} else "black"
        centered(draw, (x_layer, y), label, layer_font, txt_color)

        arrow(draw, (x_layer + layer_w // 2 + 18, y), (xs["raw"] - 100, y))

        for x, val in [(xs["raw"], raw), (xs["rm"], rm)]:
            left = x - bar_w // 2
            top = y - bar_h // 2
            draw.rectangle((left, top, left + int(bar_w * val), top + bar_h),
                           fill=BLUE if val <= gamma_frac else GREY,
                           outline="#555555", width=2)

        if settled:
            draw.ellipse((xs["thr"] - 22, y - 22, xs["thr"] + 22, y + 22),
                         fill="white", outline=BLUE, width=5)
        else:
            draw.line([(xs["thr"] - 18, y - 18), (xs["thr"] + 18, y + 18)],
                      fill=RED, width=6)
            draw.line([(xs["thr"] - 18, y + 18), (xs["thr"] + 18, y - 18)],
                      fill=RED, width=6)

    # Threshold guide lines for the two bar columns.
    for x in [xs["raw"], xs["rm"]]:
        gx = x - bar_w // 2 + int(bar_w * gamma_frac)
        draw.line([(gx, 190), (gx, 477)], fill=RED, width=3)
        centered(draw, (gx, 488), "gamma", tiny, RED)

    # Mark the first crossing as the settling depth.
    first_y = ys[2]
    arrow(draw, (xs["thr"] + 42, first_y), (xs["ct"] - 155, 170), BLUE, 4)
    centered(draw, (xs["ct"] - 125, 250), "c(t)", font(27, True), BLUE)

    # Reuse the already rendered trajectory panel and center it under the schema.
    # Panel (c) is intentionally omitted because it duplicates Fig. 2(a).
    trace = source.crop((0, 420, 1045, source.size[1]))
    trace = trace.resize((1280, 670), Image.Resampling.LANCZOS)
    base.paste(trace, ((w - trace.size[0]) // 2, top_h))
    base.save(FIG)
    base.save(PDF, "PDF", resolution=300.0)


if __name__ == "__main__":
    main()
