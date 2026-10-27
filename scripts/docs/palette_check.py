#!/usr/bin/env python3
"""Check a categorical chart palette with numbers instead of eyes. Standard library only.

Checks, in slot order (slot 1 is the first series, slot 2 the second, and so on):
  lightness band   OKLCH lightness within the band for the surface (light 0.43 to 0.77, dark 0.48 to 0.67)
  chroma floor     OKLCH chroma at least 0.10, so no slot reads as grey
  CVD separation   OKLab distance (x100) between neighbouring slots under simulated protanopia and deuteranopia
                   (Machado, Oliveira and Fernandes 2009, severity 1.0): 8 or more passes, 6 to 8 warns and needs
                   direct labels or a legend, below 6 fails
  normal vision    OKLab distance (x100) between neighbouring slots for full colour vision: 15 or more, else fails
  contrast         WCAG contrast of each slot against the surface: 3:1 or more, else a warning that asks for visible
                   labels or a table view

Exit code 1 on any FAIL. Use --pairs all for charts where every pair sits side by side (scatter, maps).

  python3 scripts/docs/palette_check.py "#2a78d6,#eb6834,#1baf7a,#eda100,#e87ba4,#008300,#6250d6,#e34948"
  python3 scripts/docs/palette_check.py --theme atlassian
  python3 scripts/docs/palette_check.py "#0052cc,#ff991f" --surface "#1a1a19" --mode dark
"""
from __future__ import annotations

import argparse
import math
import os
import sys

BAND = {"light": (0.43, 0.77), "dark": (0.48, 0.67)}
CHROMA_FLOOR = 0.10
CVD_PASS, CVD_WARN = 8.0, 6.0
NORMAL_FLOOR = 15.0
CONTRAST_MIN = 3.0
DEFAULT_SURFACE = {"light": "#fcfcfb", "dark": "#1a1a19"}
# Machado, Oliveira and Fernandes (2009), severity 1.0, applied to linear RGB.
MACHADO = {
    "protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
}


def hex_to_linear(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"bad colour {h!r}")
    rgb = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]


def cbrt(x):
    return math.copysign(abs(x) ** (1.0 / 3.0), x)


def linear_to_oklab(rgb):
    r, g, b = rgb
    l = cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def simulate(rgb, kind):
    matrix = MACHADO[kind]
    return [min(1.0, max(0.0, sum(matrix[i][j] * rgb[j] for j in range(3)))) for i in range(3)]


def delta_e(lab1, lab2):
    return 100.0 * math.sqrt(sum((a - b) ** 2 for a, b in zip(lab1, lab2)))


def luminance(rgb):
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def contrast(rgb1, rgb2):
    l1, l2 = sorted((luminance(rgb1), luminance(rgb2)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def check(colours, mode="light", surface=None, pairs="adjacent"):
    surface = surface or DEFAULT_SURFACE[mode]
    linear = [hex_to_linear(c) for c in colours]
    labs = [linear_to_oklab(c) for c in linear]
    results, failed = [], False
    lo, hi = BAND[mode]
    out_of_band = [(c, round(lab[0], 2)) for c, lab in zip(colours, labs) if not lo <= lab[0] <= hi]
    results.append(("lightness band", "FAIL" if out_of_band else "PASS",
                    f"all {len(colours)} inside L {lo}-{hi}" if not out_of_band else f"outside L {lo}-{hi}: {out_of_band}"))
    low_chroma = [(c, round(math.hypot(lab[1], lab[2]), 2)) for c, lab in zip(colours, labs) if math.hypot(lab[1], lab[2]) < CHROMA_FLOOR]
    results.append(("chroma floor", "FAIL" if low_chroma else "PASS",
                    f"all >= {CHROMA_FLOOR}" if not low_chroma else f"below {CHROMA_FLOOR}: {low_chroma}"))
    if pairs == "all":
        pairlist = [(i, j) for i in range(len(colours)) for j in range(i + 1, len(colours))]
    else:
        pairlist = [(i, i + 1) for i in range(len(colours) - 1)]
    worst_cvd, worst_normal = None, None
    for i, j in pairlist:
        cvd = min(delta_e(linear_to_oklab(simulate(linear[i], k)), linear_to_oklab(simulate(linear[j], k))) for k in MACHADO)
        normal = delta_e(labs[i], labs[j])
        if worst_cvd is None or cvd < worst_cvd[0]:
            worst_cvd = (cvd, colours[i], colours[j])
        if worst_normal is None or normal < worst_normal[0]:
            worst_normal = (normal, colours[i], colours[j])
    if worst_cvd:
        status = "PASS" if worst_cvd[0] >= CVD_PASS else "WARN" if worst_cvd[0] >= CVD_WARN else "FAIL"
        results.append(("CVD separation", status, f"worst {worst_cvd[1]} vs {worst_cvd[2]}: dE {worst_cvd[0]:.1f} "
                                                  f"(pass >= {CVD_PASS:g}, warn >= {CVD_WARN:g} with labels)"))
        results.append(("normal vision", "PASS" if worst_normal[0] >= NORMAL_FLOOR else "FAIL",
                        f"worst {worst_normal[1]} vs {worst_normal[2]}: dE {worst_normal[0]:.1f} (floor {NORMAL_FLOOR:g})"))
    surf = hex_to_linear(surface)
    low_contrast = [(c, round(contrast(rgb, surf), 2)) for c, rgb in zip(colours, linear) if contrast(rgb, surf) < CONTRAST_MIN]
    results.append(("contrast vs surface", "WARN" if low_contrast else "PASS",
                    f"all >= {CONTRAST_MIN:g}:1 on {surface}" if not low_contrast
                    else f"below {CONTRAST_MIN:g}:1 on {surface}, label the marks or add a table: {low_contrast}"))
    failed = any(status == "FAIL" for _, status, _ in results)
    return results, failed


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("palette", nargs="?", help="comma-separated hex colours in slot order")
    ap.add_argument("--theme", help="check a theme from scripts/docs/themes instead")
    ap.add_argument("--mode", choices=["light", "dark"], default="light")
    ap.add_argument("--surface", help="chart surface colour (default per mode)")
    ap.add_argument("--pairs", choices=["adjacent", "all"], default="adjacent")
    args = ap.parse_args()
    if args.theme:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from doc_themes import load_theme
        theme = load_theme(args.theme)
        colours, surface = theme["series"], args.surface or theme["chrome"]["surface"]
    elif args.palette:
        colours, surface = [c.strip() for c in args.palette.split(",") if c.strip()], args.surface
    else:
        ap.error("give a palette or --theme")
    results, failed = check(colours, args.mode, surface, args.pairs)
    print(f"palette ({args.mode}, {args.pairs} pairs): {len(colours)} slots: {', '.join(colours)}")
    for name, status, detail in results:
        print(f"  [{status}] {name:20s} {detail}")
    print("  -> FAIL" if failed else "  -> PASS (WARN items need labels, a legend or a table view)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
