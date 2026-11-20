"""
Kavinan Design Studio — pencil-sketch generator
-----------------------------------------------
Turns selected project renders into hand-drawn pencil sketches (WebP) used by the
"sketch → render" scroll reveal and comparison sliders on the website.

    python tools/make_sketches.py        (needs: pip install pillow numpy)

Add a render to SKETCHES below to create a sketch for it; the output is saved next to the
optimised image as <name>-sketch-<width>.webp and registered in assets/img/manifest.json.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
SKETCHES = ["strata-yercaud/str2_5", "prabu-residence-kumbakonam/pr_2", "prabu-residence-kumbakonam/pr_4"]
WIDTHS = [640, 1280, 1920]


def pencil(im):
    """Colour-dodge pencil sketch: grey / (1 - blurred inverted grey), then darkened lines."""
    grey = np.asarray(ImageOps.grayscale(im), dtype=np.float32)
    inv_blur = np.asarray(ImageOps.invert(ImageOps.grayscale(im)).filter(ImageFilter.GaussianBlur(radius=im.width / 220)), dtype=np.float32)
    dodge = np.clip(grey * 255.0 / np.maximum(255.0 - inv_blur, 1.0), 0, 255)
    dodge = 255 - (255 - dodge) * 1.6                      # deepen the pencil lines
    dodge = np.clip(dodge, 0, 255).astype(np.uint8)
    sk = Image.fromarray(dodge).filter(ImageFilter.SMOOTH)
    # warm paper tint so it sits on the site's warm white
    paper = Image.new("RGB", sk.size, (247, 245, 240))
    ink = Image.new("RGB", sk.size, (18, 36, 30))
    return Image.composite(paper, ink, sk)


def main():
    manifest = json.loads((IMG / "manifest.json").read_text(encoding="utf-8"))
    for key in SKETCHES:
        m = manifest[key]
        src = IMG / f"{key}-{m['widths'][-1]}.webp"
        sk = pencil(Image.open(src).convert("RGB"))
        done = []
        for w in WIDTHS:
            if w > sk.width:
                continue
            h = round(sk.height * w / sk.width)
            sk.resize((w, h), Image.LANCZOS).save(IMG / f"{key}-sketch-{w}.webp", "WEBP", quality=72, method=6)
            done.append(w)
        manifest[f"{key}-sketch"] = {"w": sk.width, "h": sk.height, "widths": done}
        print("  sketch:", key)
    (IMG / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
