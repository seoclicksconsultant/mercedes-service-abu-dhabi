#!/usr/bin/env python3
"""Assemble the static pages.

Each file in _src/pages/ starts with a JSON block inside an HTML comment:
  <!--meta {"out": "about-us/index.html", "title": "...", "desc": "...", "cur": "about"} -->
Service pages are generated from _src/services/*.md by _src/services_build.py.
The shared head, header and footer from _src/partials/ are wrapped around every page.
Run:  python3 build.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "_src"
sys.path.insert(0, str(SRC))
import services_build  # noqa: E402
import luxe_gen  # noqa: E402

luxe_gen.build()

partials = {p.stem: p.read_text(encoding="utf-8") for p in (SRC / "partials").glob("*.html")}

def assemble(meta, body):
    out = Path(meta["out"])
    depth = len(out.parts) - 1
    root = "../" * depth or "./"
    html = partials["head"] + partials["header"] + body + partials["footer"] + "</body>\n</html>\n"
    reps = {
        "TITLE": meta["title"],
        "DESC": meta["desc"],
        "PRELOAD": meta.get("preload", ""),
        "SCHEMA": meta.get("schema", ""),
        "EXTRA_HEAD": "\n".join(f'<link rel="stylesheet" href="{{{{ROOT}}}}{h}">' for h in meta.get("styles", [])),
        "EXTRA_BODY": "\n".join(f'<script src="{{{{ROOT}}}}{j}" defer></script>' for j in meta.get("scripts", [])),
    }
    for k, v in reps.items():
        html = html.replace("{{" + k + "}}", v)
    for key in ("home", "about", "contact", "services"):
        html = html.replace("{{CUR_" + key + "}}", 'aria-current="page"' if meta.get("cur") == key else "")
    html = html.replace("{{ROOT}}", root)
    html = re.sub(r'href="\./#', 'href="#', html) if depth == 0 else html
    dest = ROOT / out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    print("built", out)

for page in sorted((SRC / "pages").glob("*.html")):
    text = page.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--meta\s+(\{.*?\})\s*-->\s*", text, re.S)
    if not m:
        raise SystemExit(f"{page.name}: missing <!--meta {{...}} --> block")
    assemble(json.loads(m.group(1)), text[m.end():])

for meta, body in services_build.render_all():
    assemble(meta, body)
