"""Shared colour themes for the documentation scripts.

One JSON per theme in scripts/docs/themes/: chart series colours (in slot order), chart chrome (surface, ink, grid),
the threshold colour, Mermaid theme variables for rendered diagrams, and Mermaid classDef strings for node roles.
Pick a theme with --theme on scripts/docs/chart.py and scripts/docs/confluence_publish.py, or set DOC_THEME.
Check a palette with scripts/docs/palette_check.py before adding a theme.
"""
from __future__ import annotations

import json
import os

THEME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes")
DEFAULT_CHROME = {"surface": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781",
                  "grid": "#e1e0d9", "axis": "#c3c2b7"}
REQUIRED = ("name", "series", "threshold", "mermaid", "classes")


def list_themes():
    return sorted(f[:-5] for f in os.listdir(THEME_DIR) if f.endswith(".json"))


def load_theme(name_or_path="default"):
    path = name_or_path if name_or_path.endswith(".json") else os.path.join(THEME_DIR, f"{name_or_path}.json")
    if not os.path.isfile(path):
        raise FileNotFoundError(f"theme {name_or_path!r} not found; available: {', '.join(list_themes())}")
    with open(path, encoding="utf-8") as f:
        theme = json.load(f)
    missing = [k for k in REQUIRED if k not in theme]
    if missing:
        raise ValueError(f"{path}: missing keys {missing}")
    theme["chrome"] = {**DEFAULT_CHROME, **theme.get("chrome", {})}
    theme["path"] = path
    return theme


def mermaid_config(theme):
    """The Mermaid config object for mermaid-cli (-c) or an %%{init: ...}%% directive."""
    return {"theme": theme["mermaid"].get("theme", "base"), "themeVariables": theme["mermaid"].get("themeVariables", {})}


if __name__ == "__main__":
    for name in list_themes():
        t = load_theme(name)
        print(f"{name:12s} {len(t['series'])} series  {t.get('description', '')}")
