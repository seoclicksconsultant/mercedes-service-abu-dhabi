#!/usr/bin/env python3
"""Assemble the static pages.

Each file in _src/pages/ starts with a JSON block inside an HTML comment:
  <!--meta {"out": "about-us/index.html", "title": "...", "desc": "...", "cur": "about"} -->
The shared head, header and footer from _src/partials/ are wrapped around it.
Run:  python3 build.py
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "_src"
partials = {p.stem: p.read_text(encoding="utf-8") for p in (SRC / "partials").glob("*.html")}

for page in sorted((SRC / "pages").glob("*.html")):
    text = page.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--meta\s+(\{.*?\})\s*-->\s*", text, re.S)
    if not m:
        raise SystemExit(f"{page.name}: missing <!--meta {{...}} --> block")
    meta = json.loads(m.group(1))
    body = text[m.end():]
    out = Path(meta["out"])
    depth = len(out.parts) - 1
    root = "../" * depth or "./"

    html = partials["head"] + partials["header"] + body + partials["footer"] + "</body>\n</html>\n"
    reps = {
        "TITLE": meta["title"],
        "DESC": meta["desc"],
        "PRELOAD": meta.get("preload", ""),
        "SCHEMA": meta.get("schema", ""),
    }
    for k, v in reps.items():
        html = html.replace("{{" + k + "}}", v)
    for key in ("home", "about", "contact"):
        html = html.replace("{{CUR_" + key + "}}", 'aria-current="page"' if meta.get("cur") == key else "")
    html = html.replace("{{ROOT}}", root)
    html = re.sub(r'href="\./#', 'href="#', html) if depth == 0 else html

    dest = ROOT / out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    print("built", out)
