"""
Kavinan Design Studio - image optimiser
---------------------------------------
Converts the studio's source images into fast, responsive WebP sets for the
website and writes assets/img/manifest.json (used by build.py for srcset,
width/height and alt text).

Run from the website folder (needs Pillow:  pip install pillow):
    python tools/optimize_images.py

To add a new project's images: drop them in a folder, add an entry to
SOURCES below (or to content/projects.json "images" and re-run), then build.
"""
import json
import os
import sys
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent          # website/
STUDIO = ROOT.parent                                   # D:/KDS
SRC = STUDIO / "_Portfolio" / "assets"
OUT = ROOT / "assets" / "img"
WIDTHS = [640, 1280, 1920]
QUALITY = 76

# project slug -> list of images. Each entry is either a file stem in _Portfolio/assets (e.g. "st_6")
# or a ("name", "path relative to D:/KDS") pair for images kept in a project folder.
STRATA_R2 = "Project - Strata - Yercaud/R2"
PRABU = "Mr. Prabu Residence - Kumbakonam/Interior"
SOURCES = {
    "s-gan-villa": ["sg_c3", "sg_c4", "sg_c6", "sg_c9", "sg_c1", "sg_c2", "sg_c5", "sg_c7", "sg_c8",
                    "sg_c10", "sg_c12", "sg_r1", "sg_r2", "sg_r3", "sg_r4",
                    "sg_b1", "sg_b2", "sg_b3", "sg_b4", "sg_p1", "sg_p2", "sg_p3", "sg_p4"],
    "strata-yercaud": [("str2_5", f"{STRATA_R2}/5.jpg"), ("str2_1", f"{STRATA_R2}/1.jpg"), ("str2_2", f"{STRATA_R2}/2.jpg"),
                       ("str2_3", f"{STRATA_R2}/3.jpg"), ("str2_4", f"{STRATA_R2}/4.jpg"), ("str2_6", f"{STRATA_R2}/6.jpg"),
                       ("str2_7", f"{STRATA_R2}/7.jpg"),
                       "st_6", "st_2", "st_3", "st_4", "st_5", "st_7", "st_8",
                       "st_p0", "st_p1", "st_p2", "st_p3", "st_d1", "st_d2"],
    "prabu-residence-kumbakonam": [("pr_2", f"{PRABU}/Enscape_2026-11-06-17-15-19.png"), ("pr_1", f"{PRABU}/Enscape_2026-11-06-16-57-38.png"),
                                   ("pr_3", f"{PRABU}/Enscape_2026-11-06-17-23-10.png"), ("pr_4", f"{PRABU}/Enscape_2026-11-06-17-29-53.png"),
                                   ("pr_5", f"{PRABU}/Enscape_2026-11-06-17-36-09.png"), ("pr_6", f"{PRABU}/Enscape_2026-11-06-17-43-46.png"),
                                   ("pr_7", f"{PRABU}/Enscape_2026-11-06-17-50-28.png"), ("pr_8", f"{PRABU}/Enscape_2026-11-06-17-55-47.png"),
                                   ("pr_9", f"{PRABU}/Enscape_2026-11-06-18-04-31.png")],
    "aravindhan-residence": ["ar_1", "ar_2", "ar_3"],
    "residences-tamil-nadu": ["rk_1", "dn_1", "dn_2", "kn_1", "kn_2", "lk_1", "lk_2", "lk_3"],
    "lakeside-farmhouse": ["fh_1", "fh_2", "fh_3", "fh_4"],
    "mixed-use-development": ["mu_1", "mu_2", "mu_3", "mu_4", "mu_5"],
    "tata-corporate-office": ["tt_1", "tt_2"],
    "thozhi-womens-hostel": ["th_1", "th_2", "th_3"],
    "alpha-multispeciality-hospital": ["ah_1", "ah_2", "ah_3", "ah_4", "ah_5", "ah_6"],
    "architectural-institute": ["ai_1", "ai_2", "ai_3", "ai_4", "ai_5", "ai_6"],
    "performing-arts-centre": ["vp_1", "vp_2", "vp_3", "vp_4", "vp_5"],
    "isro-campus-visualisation": ["isro_1", "isro_2", "isro_3", "isro_4", "isro_5", "isro_6"],
    "elidi-stadia": ["eli_1", "eli_2", "eli_3", "eli_4", "eli_5", "eli_6"],
    "maritime-heritage-complex": ["nh_1", "nh_2", "nh_3", "nh_4", "nh_5"],
    "pavilion-csa": ["pv_1", "pv_2", "pv_3"],
    "pond-park-sivakasi": ["pp_1", "pp_2", "pp_3", "pp_4", "pp_5"],
    "jithu-residence-interiors": ["jr_1", "jr_2", "jr_3", "jr_4", "jr_5", "jr_6"],
    "church-interior-chromepet": ["ch_1", "ch_2"],
    "archdais-interior-competition": ["ad_1", "ad_2", "ad_3", "ad_4", "ad_5", "ad_6", "ad_7", "ad_8"],
    "cubro-operating-theatre": ["cb_d1", "cb_d2", "cb_d3", "cb_d4", "cb_d5"],
    "pitau-travertine-facade": ["pt_d1", "pt_d2", "pt_d3", "pt_d4"],
    "team": ["tm_srk", "tm_ridhima", "tm_bharath", "tm_mohana", "tm_nivetha", "tm_venkata",
             "tm_shiva", "tm_kannan", "tm_kavitha"],
}


def save_set(im, folder, name, widths, manifest):
    folder.mkdir(parents=True, exist_ok=True)
    w0, h0 = im.size
    done = []
    for w in widths:
        if w > w0 and done:
            continue
        w = min(w, w0)
        h = round(h0 * w / w0)
        dst = folder / f"{name}-{w}.webp"
        if not dst.exists():
            im.resize((w, h), Image.LANCZOS).save(dst, "WEBP", quality=QUALITY, method=6)
        done.append(w)
    key = f"{folder.name}/{name}"
    manifest[key] = {"w": w0, "h": h0, "widths": done}


def og_image(im, dst):
    """1200x630 social-share crop (JPEG, for WhatsApp / Facebook / LinkedIn previews)."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    ImageOps.fit(im, (1200, 630), Image.LANCZOS, centering=(0.5, 0.45)).save(dst, "JPEG", quality=82, optimize=True)


def brand_assets():
    brand = OUT / "brand"
    brand.mkdir(parents=True, exist_ok=True)
    for src, name in [("logo.png", "logo"), ("logo_w.png", "logo-white")]:
        im = Image.open(SRC / src).convert("RGBA")
        im = im.crop(im.getbbox())
        im.thumbnail((640, 640), Image.LANCZOS)
        im.save(brand / f"{name}.png", optimize=True)
        im.save(brand / f"{name}.webp", "WEBP", quality=90)
    # Symbol only (top cluster of the stacked mark) for favicons / app icons
    mark = Image.open(SRC / "mark.png").convert("RGBA")
    alpha = mark.split()[-1]
    rows = [any(alpha.getpixel((x, y)) > 20 for x in range(0, mark.width, 4)) for y in range(mark.height)]
    top = rows.index(True)
    y, gap = top, 0
    while y < mark.height:            # walk down until the first clear horizontal gap after the symbol
        if not rows[y]:
            gap += 1
            if gap > 25 and y - top > mark.height * 0.25:
                break
        else:
            gap = 0
        y += 1
    symbol = mark.crop((0, top, mark.width, y - gap))
    symbol = symbol.crop(symbol.getbbox())
    symbol.save(brand / "symbol.png", optimize=True)
    for size, bg in [(512, None), (192, None), (180, (245, 242, 236, 255)), (32, None), (16, None)]:
        canvas = Image.new("RGBA", (size, size), bg or (0, 0, 0, 0))
        s = symbol.copy()
        pad = int(size * (0.14 if bg else 0.06))
        s.thumbnail((size - 2 * pad, size - 2 * pad), Image.LANCZOS)
        canvas.paste(s, ((size - s.width) // 2, (size - s.height) // 2), s)
        name = {512: "icon-512.png", 192: "icon-192.png", 180: "apple-touch-icon.png",
                32: "favicon-32.png", 16: "favicon-16.png"}[size]
        canvas.save(brand / name, optimize=True)
    fav = Image.open(brand / "icon-512.png")
    fav.save(ROOT / "assets" / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    # QR to the studio location (from portfolio)
    Image.open(SRC / "qr.png").save(brand / "location-qr.png", optimize=True)


def main():
    if not SRC.exists():
        sys.exit(f"Source folder not found: {SRC}")
    manifest = {}
    for slug, stems in SOURCES.items():
        folder = OUT / slug
        for i, entry in enumerate(stems):
            stem, src = (entry, SRC / f"{entry}.jpg") if isinstance(entry, str) else (entry[0], STUDIO / entry[1])
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            widths = [480, 900] if slug == "team" else WIDTHS
            save_set(im, folder, stem, widths, manifest)
            if i == 0 and slug != "team":
                og_image(im, OUT / "og" / f"{slug}.jpg")
        print(f"  {slug}: {len(stems)} images")
    # Default social image (Strata hero)
    og_image(Image.open(STUDIO / STRATA_R2 / "5.jpg").convert("RGB"), OUT / "og" / "default.jpg")
    brand_assets()
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    total = sum(f.stat().st_size for f in OUT.rglob("*") if f.is_file())
    print(f"Done. {len(manifest)} images, {total / 1e6:.1f} MB in {OUT}")


if __name__ == "__main__":
    main()
