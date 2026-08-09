#!/usr/bin/env python3
"""Generate the README banner and per-theme title cards.

Reads every theme under themes/ and writes assets to images/, so the
artwork always reflects the actual theme colors. Each title card shows
the theme name, its palette with hex values, and a small vignette drawn
entirely from that palette. Assets are authored as SVG and rasterized
to PNG at 2x, since the VS Code Marketplace does not render SVG images
in extension READMEs.

Requires rsvg-convert (brew install librsvg).

Usage: python3 scripts/build-assets.py
"""

import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = ROOT / "themes"
IMAGES_DIR = ROOT / "images"

CARD_WIDTH = 1600
CARD_HEIGHT = 420
VIGNETTE_WIDTH = 760
VIGNETTE_HEIGHT = 300

BANNER_WIDTH = 1200
BANNER_HEIGHT = 230

SERIF = "Georgia, 'Times New Roman', serif"
MONO = "'SF Mono', Menlo, Consolas, monospace"

TAGLINES = {
    "neon": "80s cyberpunk and synthwave",
    "deep": "Neo-noir, late nights",
    "warm": "Golden-hour cinematography",
    "kodachrome": "Vintage film stock",
    "drivein": "1950s Americana",
    "psychedelic": "1960s counterculture",
    "marquee": "Classic Hollywood marquee lights",
    "silentera": "Silver nitrate, title cards",
}


def load_jsonc(path: Path) -> dict:
    """Parse a VS Code theme file (JSON with comments and trailing commas)."""
    text = path.read_text()
    out = []
    i = 0
    in_string = False
    while i < len(text):
        char = text[i]
        if in_string:
            out.append(char)
            if char == "\\":
                out.append(text[i + 1])
                i += 2
                continue
            if char == '"':
                in_string = False
            i += 1
        elif char == '"':
            in_string = True
            out.append(char)
            i += 1
        elif text[i : i + 2] == "//":
            while i < len(text) and text[i] != "\n":
                i += 1
        elif text[i : i + 2] == "/*":
            end = text.find("*/", i + 2)
            i = len(text) if end == -1 else end + 2
        else:
            out.append(char)
            i += 1
    stripped = re.sub(r",(\s*[}\]])", r"\1", "".join(out))
    return json.loads(stripped)


def token_colors(theme: dict) -> dict:
    """Map token scopes to their foreground colors."""
    result = {}
    for entry in theme.get("tokenColors", []):
        foreground = entry.get("settings", {}).get("foreground")
        if not foreground:
            continue
        scopes = entry.get("scope", [])
        if isinstance(scopes, str):
            scopes = [s.strip() for s in scopes.split(",")]
        for scope in scopes:
            result.setdefault(scope, foreground)
    return result


def palette_of(theme: dict) -> dict:
    colors = theme.get("colors", {})
    tokens = token_colors(theme)
    palette = {
        "bg": colors.get("editor.background"),
        "keyword": tokens.get("keyword"),
        "function": tokens.get("entity.name.function"),
        "string": tokens.get("string"),
        "variable": tokens.get("variable"),
        "fg": colors.get("editor.foreground"),
        "comment": tokens.get("comment"),
    }
    missing = [key for key, value in palette.items() if not value]
    if missing:
        raise SystemExit(f"{theme.get('name')}: missing colors for {missing}")
    return palette


# --- Vignettes -------------------------------------------------------------
# Each vignette draws in a 760x300 viewport using only its theme's palette.


def vignette_neon(p: dict) -> str:
    street = 200
    tubes = [
        (60, 55, 16, 145, p["keyword"]), (108, 95, 9, 105, p["function"]),
        (170, 40, 24, 160, p["function"]), (232, 105, 9, 95, p["keyword"]),
        (300, 75, 16, 125, p["variable"]), (360, 50, 11, 150, p["keyword"]),
        (412, 115, 20, 85, p["string"]), (500, 40, 14, 160, p["function"]),
        (552, 85, 9, 115, p["keyword"]), (620, 65, 18, 135, p["variable"]),
        (688, 105, 11, 95, p["function"]),
    ]
    crossbars = [(148, 82, 68, 7, p["keyword"]), (478, 74, 58, 7, p["keyword"]),
                 (338, 130, 56, 7, p["function"])]
    shapes = "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{w / 2}" fill="{color}"/>'
        for x, y, w, h, color in tubes
    ) + "".join(
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{color}"/>'
        for x, y, w, h, color in crossbars
    )
    return (
        '<filter id="neon-glow" x="-50%" y="-50%" width="200%" height="200%">'
        '<feGaussianBlur stdDeviation="6"/></filter>'
        f'<g filter="url(#neon-glow)" opacity="0.7">{shapes}</g>'
        f"<g>{shapes}</g>"
        f'<line x1="0" y1="{street}" x2="{VIGNETTE_WIDTH}" y2="{street}" '
        f'stroke="{p["fg"]}" stroke-opacity="0.25"/>'
        f'<g transform="translate(0,{2 * street}) scale(1,-1)" opacity="0.22" '
        f'filter="url(#neon-glow)">{shapes}</g>'
    )


def vignette_deep(p: dict) -> str:
    parts = [f'<circle cx="590" cy="90" r="52" fill="{p["keyword"]}" fill-opacity="0.9"/>']
    buildings = [(0, 150, 90), (80, 110, 70), (140, 190, 100), (230, 130, 80), (300, 210, 110),
                 (400, 120, 90), (480, 170, 70), (540, 140, 90), (620, 200, 80), (690, 150, 70)]
    for x, height, width in buildings:
        top = VIGNETTE_HEIGHT - height
        parts.append(f'<rect x="{x}" y="{top}" width="{width}" height="{height}" fill="{p["keyword"]}" fill-opacity="0.14"/>')
        for wx in range(x + 12, x + width - 10, 22):
            for wy in range(top + 14, VIGNETTE_HEIGHT - 16, 30):
                if (wx * 7 + wy * 13) % 5 < 2:
                    parts.append(f'<rect x="{wx}" y="{wy}" width="7" height="10" fill="{p["function"]}" fill-opacity="0.85"/>')
    return "".join(parts)


def vignette_warm(p: dict) -> str:
    return "".join([
        f'<circle cx="530" cy="120" r="64" fill="{p["keyword"]}"/>',
        f'<path d="M0,210 Q190,150 380,205 T760,195 V300 H0 Z" fill="{p["function"]}" fill-opacity="0.55"/>',
        f'<path d="M0,245 Q220,195 430,245 T760,240 V300 H0 Z" fill="{p["keyword"]}" fill-opacity="0.5"/>',
        f'<path d="M0,278 Q260,240 500,280 T760,272 V300 H0 Z" fill="{p["variable"]}" fill-opacity="0.55"/>',
    ])


def vignette_kodachrome(p: dict) -> str:
    frames = [p["keyword"], p["function"], p["string"]]
    parts = [f'<g transform="rotate(-3 380 150)">',
             f'<rect x="20" y="70" width="720" height="160" rx="8" fill="{p["fg"]}" fill-opacity="0.12"/>']
    for row_y in (82, 204):
        for hx in range(44, 720, 48):
            parts.append(f'<rect x="{hx}" y="{row_y}" width="18" height="14" rx="3" fill="{p["bg"]}"/>')
    for i, color in enumerate(frames):
        parts.append(f'<rect x="{52 + i * 230}" y="106" width="200" height="88" rx="4" fill="{color}" fill-opacity="0.9"/>')
    parts.append("</g>")
    return "".join(parts)


def vignette_drivein(p: dict) -> str:
    parts = []
    for cx, cy in [(80, 60), (200, 30), (330, 75), (500, 40), (640, 65), (720, 25), (420, 20)]:
        parts.append(f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="{p["fg"]}" fill-opacity="0.6"/>')
    parts.extend([
        f'<rect x="250" y="205" width="10" height="60" fill="{p["fg"]}" fill-opacity="0.25"/>',
        f'<rect x="500" y="205" width="10" height="60" fill="{p["fg"]}" fill-opacity="0.25"/>',
        f'<path d="M210,100 L550,88 L550,208 L210,214 Z" fill="{p["fg"]}" fill-opacity="0.92"/>',
        f'<path d="M210,100 L550,88 L550,208 L210,214 Z" fill="none" stroke="{p["keyword"]}" stroke-width="4"/>',
    ])
    cars = [(60, p["keyword"]), (180, p["function"]), (330, p["variable"]), (480, p["keyword"]), (620, p["function"])]
    for x, color in cars:
        parts.extend([
            f'<rect x="{x}" y="272" width="90" height="18" rx="9" fill="{color}" fill-opacity="0.85"/>',
            f'<rect x="{x + 22}" y="258" width="46" height="18" rx="9" fill="{color}" fill-opacity="0.85"/>',
        ])
    return "".join(parts)


def vignette_psychedelic(p: dict) -> str:
    colors = [p["keyword"], p["function"], p["string"], p["variable"]]
    parts = []
    cx, cy = 380, 150
    for i, radius in enumerate(range(230, 8, -22)):
        color = colors[i % len(colors)]
        drift = i * 6
        parts.append(f'<circle cx="{cx + drift}" cy="{cy + drift // 2}" r="{radius}" fill="{color}" fill-opacity="0.9"/>')
    return "".join(parts)


def vignette_marquee(p: dict) -> str:
    parts = [
        f'<rect x="150" y="55" width="460" height="190" rx="18" fill="{p["fg"]}" fill-opacity="0.08"/>',
        f'<rect x="150" y="55" width="460" height="190" rx="18" fill="none" stroke="{p["keyword"]}" stroke-width="3"/>',
        f'<rect x="205" y="115" width="350" height="16" rx="8" fill="{p["function"]}"/>',
        f'<rect x="245" y="152" width="270" height="12" rx="6" fill="{p["fg"]}" fill-opacity="0.7"/>',
        f'<rect x="285" y="185" width="190" height="12" rx="6" fill="{p["fg"]}" fill-opacity="0.45"/>',
    ]
    bulbs = []
    for i in range(14):
        bulbs.append((178 + i * 31.5, 78))
        bulbs.append((178 + i * 31.5, 222))
    for i in range(4):
        bulbs.append((172, 106 + i * 30))
        bulbs.append((588, 106 + i * 30))
    for i, (bx, by) in enumerate(bulbs):
        color = p["keyword"] if i % 2 == 0 else p["fg"]
        parts.append(f'<circle cx="{bx:.0f}" cy="{by}" r="5" fill="{color}"/>')
    return "".join(parts)


def vignette_silentera(p: dict) -> str:
    """Academy countdown leader: sweep wedge, crosshair, numeral."""
    cx, cy, r = 380, 150, 128
    return "".join([
        f'<rect width="{VIGNETTE_WIDTH}" height="{VIGNETTE_HEIGHT}" fill="{p["fg"]}" fill-opacity="0.05"/>',
        # frame-edge sprocket holes
        "".join(f'<rect x="{x}" y="{y}" width="16" height="12" rx="3" fill="{p["fg"]}" fill-opacity="0.12"/>'
                for x in (14, 730) for y in range(18, VIGNETTE_HEIGHT - 18, 34)),
        # sweep wedge from twelve o'clock
        f'<path d="M{cx},{cy} L{cx},{cy - r} A{r},{r} 0 0 1 {cx + r * 0.866:.0f},{cy - r * 0.5:.0f} Z" '
        f'fill="{p["fg"]}" fill-opacity="0.1"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{p["keyword"]}" stroke-width="3" stroke-opacity="0.85"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r - 30}" fill="none" stroke="{p["keyword"]}" stroke-width="2" stroke-opacity="0.4"/>',
        f'<line x1="{cx - 190}" y1="{cy}" x2="{cx + 190}" y2="{cy}" stroke="{p["comment"]}" stroke-opacity="0.5"/>',
        f'<line x1="{cx}" y1="{cy - 140}" x2="{cx}" y2="{cy + 140}" stroke="{p["comment"]}" stroke-opacity="0.5"/>',
        f'<text x="{cx}" y="{cy + 58}" text-anchor="middle" font-family="{SERIF}" '
        f'font-size="160" fill="{p["keyword"]}">3</text>',
    ])


VIGNETTES = {
    "neon": vignette_neon,
    "deep": vignette_deep,
    "warm": vignette_warm,
    "kodachrome": vignette_kodachrome,
    "drivein": vignette_drivein,
    "psychedelic": vignette_psychedelic,
    "marquee": vignette_marquee,
    "silentera": vignette_silentera,
}


# --- Cards and banner ------------------------------------------------------


def card_svg(slug: str, display_name: str, palette: dict) -> str:
    swatches = []
    chip, gap = 62, 18
    labels = ["bg", "keyword", "function", "string", "variable", "fg"]
    for i, key in enumerate(labels):
        x = 90 + i * (chip + gap)
        color = palette[key]
        swatches.append(
            f'<rect x="{x}" y="248" width="{chip}" height="{chip}" rx="14" fill="{color}" '
            f'stroke="{palette["fg"]}" stroke-opacity="0.18"/>'
            f'<text x="{x + chip / 2}" y="338" text-anchor="middle" font-family="{MONO}" '
            f'font-size="13" fill="{palette["comment"]}">{color.upper()}</text>'
        )
    vignette = VIGNETTES[slug](palette)
    vx = CARD_WIDTH - VIGNETTE_WIDTH - 60
    vy = (CARD_HEIGHT - VIGNETTE_HEIGHT) / 2
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_WIDTH}" height="{CARD_HEIGHT}" '
        f'viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}">'
        f'<defs><clipPath id="card"><rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="14"/></clipPath>'
        f'<clipPath id="vignette"><rect width="{VIGNETTE_WIDTH}" height="{VIGNETTE_HEIGHT}" rx="12"/></clipPath></defs>'
        f'<g clip-path="url(#card)">'
        f'<rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" fill="{palette["bg"]}"/>'
        f'<text x="90" y="150" font-family="{SERIF}" font-size="58" fill="{palette["fg"]}">{display_name}</text>'
        f'<text x="92" y="196" font-family="{SERIF}" font-size="19" font-style="italic" '
        f'fill="{palette["comment"]}">{TAGLINES[slug]}</text>'
        f"{''.join(swatches)}"
        f'<g transform="translate({vx},{vy})" clip-path="url(#vignette)">{vignette}</g>'
        f"</g>"
        f'<rect x="0.5" y="0.5" width="{CARD_WIDTH - 1}" height="{CARD_HEIGHT - 1}" rx="14" '
        f'fill="none" stroke="{palette["fg"]}" stroke-opacity="0.2"/>'
        "</svg>\n"
    )


def banner_svg(accents: list) -> str:
    bar_width = 88
    bar_gap = 14
    strip_width = len(accents) * bar_width + (len(accents) - 1) * bar_gap
    strip_x = (BANNER_WIDTH - strip_width) / 2
    bars = "".join(
        f'<rect x="{strip_x + i * (bar_width + bar_gap)}" y="176" '
        f'width="{bar_width}" height="6" rx="3" fill="{color}"/>'
        for i, color in enumerate(accents)
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{BANNER_WIDTH}" '
        f'height="{BANNER_HEIGHT}" viewBox="0 0 {BANNER_WIDTH} {BANNER_HEIGHT}">'
        f'<rect width="{BANNER_WIDTH}" height="{BANNER_HEIGHT}" rx="10" fill="#131313"/>'
        f'<text x="{BANNER_WIDTH / 2}" y="112" text-anchor="middle" '
        f'font-family="{SERIF}" font-size="54" letter-spacing="18" '
        f'fill="#E8E0CE">TECHNICOLOR</text>'
        f'<text x="{BANNER_WIDTH / 2}" y="148" text-anchor="middle" '
        f'font-family="{SERIF}" font-size="13" letter-spacing="6" '
        f'fill="#8A8578">EIGHT DARK THEMES FOR VISUAL STUDIO CODE</text>'
        f"{bars}</svg>\n"
    )


def rasterize(svg: Path, width: int) -> None:
    png = svg.with_suffix(".png")
    subprocess.run(
        ["rsvg-convert", "-w", str(width), str(svg), "-o", str(png)],
        check=True,
    )
    print(f"wrote {png.relative_to(ROOT)}")


def main() -> None:
    if not shutil.which("rsvg-convert"):
        raise SystemExit("rsvg-convert is required: brew install librsvg")
    IMAGES_DIR.mkdir(exist_ok=True)

    manifest = json.loads((ROOT / "package.json").read_text())
    accents = []
    for contribution in manifest["contributes"]["themes"]:
        path = ROOT / contribution["path"]
        theme = load_jsonc(path)
        palette = palette_of(theme)
        accents.append(palette["keyword"])
        slug = path.stem.replace("technicolor-", "").replace("-color-theme", "")
        display_name = contribution["label"].replace("Technicolor ", "")
        out = IMAGES_DIR / f"card-{slug}.svg"
        out.write_text(card_svg(slug, display_name, palette))
        rasterize(out, CARD_WIDTH * 2)

    banner = IMAGES_DIR / "banner.svg"
    banner.write_text(banner_svg(accents))
    rasterize(banner, BANNER_WIDTH * 2)


if __name__ == "__main__":
    main()
