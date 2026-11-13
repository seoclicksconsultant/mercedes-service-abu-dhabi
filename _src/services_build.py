"""Turn the service-page markdown in _src/services/*.md into designed HTML bodies.

build.py calls render_all(); each page returns (meta, body) and is wrapped
with the shared head/header/footer like every other page.
"""
import html, json, math, re
from pathlib import Path

from services_config import PAGES, ORDER

SRC = Path(__file__).parent
WA = "971586095249"
TEL = "+971586095249"
TEL_TXT = "+971 58 609 5249"

# ---------------------------------------------------------------- markdown
def unesc(s):
    return re.sub(r"\\([\[\]\+\|\$\-\.\*#_!()])", r"\1", s)

def inline(s):
    s = re.sub(r"(?<!\*)\*\\\[[^*]*?\\\]\*(?!\*)", "", s)          # *\[editor note\]* -> removed
    s = unesc(s).strip()
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
               lambda m: f'<a class="inline" href="{m.group(2)}" target="_blank" rel="noopener">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return s.replace("**", "")

def plain(s):
    return re.sub(r"<[^>]+>", "", inline(s))

def clean_head(s):
    s = unesc(s).replace("**", "").strip()
    return s.rstrip(":").strip()

def parse(text):
    """Return list of blocks: (kind, data)."""
    lines = text.splitlines()
    blocks, i = [], 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1; continue
        if s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                r = lines[i].strip().strip("|")
                cells = [c.strip() for c in re.split(r"(?<!\\)\|", r)]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells if c):
                    rows.append(cells)
                i += 1
            blocks.append(("table", rows)); continue
        m = re.match(r"^(?:([*\-]|\d+\.)\s+)?(#{1,6})\s+(.*)$", s)
        if m:
            blocks.append(("h", (len(m.group(2)), clean_head(m.group(3)), bool(m.group(1)))))
        elif re.match(r"^\*\*Meta (Title|Description):\*\*", s):
            k = "title" if "Title" in s else "desc"
            blocks.append(("meta", (k, unesc(re.sub(r"^\*\*Meta \w+:\*\*", "", s)).replace("**", "").strip())))
        elif "609 5249" in s or re.match(r"^\*\*\\\[", s):
            blocks.append(("cta", re.findall(r"\\\[([^\\\]]+)\\\]", s)))
        elif re.match(r"^[*\-]\s+", s):
            blocks.append(("li", re.sub(r"^[*\-]\s+", "", s)))
        else:
            blocks.append(("p", s))
        i += 1
    return blocks

def to_doc(blocks):
    doc = {"meta": {}, "h1": "", "intro": [], "ctas": [], "sections": []}
    cur = None
    for kind, d in blocks:
        if kind == "meta":
            doc["meta"][d[0]] = d[1]
        elif kind == "h" and d[0] == 1:
            doc["h1"] = d[1]
        elif kind == "h" and (d[0] == 2 or (d[1].startswith("Book Your") and d[0] <= 3)):
            cur = {"title": d[1], "blocks": []}
            doc["sections"].append(cur)
        elif kind == "cta":
            if not doc["ctas"]:
                doc["ctas"] = d
        elif cur is None:
            if kind == "p":
                doc["intro"].append(d)
        else:
            cur["blocks"].append((kind, d))
    return doc

# ---------------------------------------------------------------- icons
def svg(path, sw="1.8"):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>')

I = {
    "disc": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2"/><path d="M17 4.5a9 9 0 0 1 2.6 3" stroke-width="3"/>',
    "scan": '<rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4M7 10l2-2 3 3 5-5"/>',
    "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5"/>',
    "bolt": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "chip": '<rect x="6" y="6" width="12" height="12" rx="2"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/><path d="M10 10h4v4h-4z"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
    "pipe": '<path d="M3 7h6a3 3 0 0 1 3 3v4a3 3 0 0 0 3 3h6"/><path d="M3 4v6M21 14v6"/><path d="M15 9s2 2 2 3.2a2 2 0 0 1-4 0C13 11 15 9 15 9z"/>',
    "thermo": '<path d="M14 14.8V4a2 2 0 1 0-4 0v10.8a4 4 0 1 0 4 0z"/><path d="M12 9v8"/>',
    "snow": '<path d="M12 2v20M4.9 7l14.2 10M19.1 7L4.9 17M9 3.5l3 2 3-2M9 20.5l3-2 3 2"/>',
    "brush": '<path d="M18.4 2.6a2 2 0 0 1 2.9 2.9L12 14.8 9.2 12z"/><path d="M9 12.5c-2.5 0-4 1.6-4 4 0 1.8-1 2.8-3 3.5 3 1.4 8 1.4 9.6-1.6.9-1.8.6-3.6-.6-4.9"/>',
    "car": '<path d="M3 15l2-5c.4-1 1.3-1.6 2.3-1.6h9.4c1 0 1.9.6 2.3 1.6l2 5v3h-2M5 18H3v-3h18"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "flag": '<path d="M4 22V4M4 4h13l-2 4 2 4H4"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18v3h3l6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.8-.8-.8-2.8z"/>',
    "fan": '<circle cx="12" cy="12" r="2"/><path d="M12 10c0-4 1-7 4-7 2 0 3 2 2 4-1 2-4 3-6 3zM14 12c4 0 7 1 7 4 0 2-2 3-4 2-2-1-3-4-3-6zM12 14c0 4-1 7-4 7-2 0-3-2-2-4 1-2 4-3 6-3zM10 12c-4 0-7-1-7-4 0-2 2-3 4-2 2 1 3 4 3 6z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "shield": '<path d="M12 3l8 3v6c0 4.4-3.4 8.3-8 9-4.6-.7-8-4.6-8-9V6z"/><path d="M8.5 12l2.5 2.5 4.5-5"/>',
    "ruler": '<path d="M3 17L17 3l4 4L7 21z"/><path d="M7 13l2 2M10 10l2 2M13 7l2 2"/>',
    "tag": '<path d="M3 12V4a1 1 0 0 1 1-1h8l9 9-9 9z"/><circle cx="7.5" cy="7.5" r="1.5"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    "people": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6 6 0 0 1 3.5 6"/>',
    "doc": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5M10 13h6M10 17h6"/>',
    "battery": '<rect x="2" y="7" width="18" height="10" rx="2"/><path d="M22 11v2M7 10v4M5 12h4M13 12h4"/>',
    "light": '<path d="M9 18h6M10 21h4M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3z"/>',
    "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "pin": '<path d="M12 22s7-6.2 7-12a7 7 0 1 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "star": '<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1.1 6.2L12 17.3 6.4 20.2l1.1-6.2L3 9.6l6.2-.9z"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
    "tick": '<path d="M5 12l5 5L20 7"/>',
}
WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.1-1.7-.8-2-.9-.3-.1-.5-.1-.7.1-.2.3-.8.9-.9 1.1-.2.2-.3.2-.6.1-.3-.1-1.2-.5-2.3-1.4-.9-.8-1.4-1.7-1.6-2-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5 2.5 1 3 .8 3.6.8.6-.1 1.7-.7 2-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8a9.8 9.8 0 0 1-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1 1 12 21.8zm0-21.6A11.8 11.8 0 0 0 1.8 18l-1.7 6 6.2-1.6A11.8 11.8 0 1 0 12 .2z"/></svg>'

KEYWORDS = [
    (("carbon-ceramic", "amg", "performance", "turbo"), "flag"),
    (("parking brake",), "chip"),
    (("pad", "disc", "brake"), "disc"),
    (("diagnos", "scan", "quick test", "live data", "test"), "scan"),
    (("battery",), "battery"),
    (("electr", "48v", "wiring", "starter", "alternator", "eq ", "hybrid", "ev "), "bolt"),
    (("software", "coding", "module", "conductor", "sam", "mechatronic", "control", "srs", "airbag"), "chip"),
    (("leak", "hose", "line"), "pipe"),
    (("oil", "fluid", "coolant", "regas"), "drop"),
    (("gear", "transmission", "clutch", "valve", "torque", "dct", "transfer"), "gear"),
    (("overheat", "cooling", "heat", "thermo"), "thermo"),
    (("ac ", "condenser", "evaporator", "compressor", "climate", "airmatic", "suspension"), "snow"),
    (("paint", "colour", "coat", "rim", "polish", "designo", "matte", "scratch", "chip", "respray", "finish"), "brush"),
    (("dent", "panel", "bumper", "body", "door", "collision", "accident", "chassis", "frame", "aluminium", "plastic", "trim"), "car"),
    (("glass", "windshield", "adas", "camera", "light", "headlight"), "eye"),
    (("filter", "air ", "blower", "airflow", "fan"), "fan"),
    (("timing", "camshaft"), "clock"),
    (("mount",), "ruler"),
    (("misfire", "ignition", "injection", "fuel"), "bolt"),
    (("window", "seat", "lock", "comfort"), "people"),
    (("rebuild", "overhaul", "replace", "repair", "head gasket"), "wrench"),
    (("assyst", "record", "reset", "selection", "approval"), "doc"),
]
def icon_for(title):
    t = " " + title.lower() + " "
    for keys, name in KEYWORDS:
        if any(k in t for k in keys):
            return I[name]
    return I["wrench"]

WHY_ICONS = ["people", "ruler", "drop", "scan", "shield", "tag", "check", "doc"]

# ---------------------------------------------------------------- emblems (big rotating line art)
def emblem(kind):
    c = 100
    out = []
    if kind == "disc":
        out.append(f'<circle cx="{c}" cy="{c}" r="92"/><circle cx="{c}" cy="{c}" r="84" opacity=".4"/><circle cx="{c}" cy="{c}" r="34"/><circle cx="{c}" cy="{c}" r="12"/>')
        for k in range(5):
            a = math.radians(k * 72 - 90)
            out.append(f'<circle cx="{c+22*math.cos(a):.1f}" cy="{c+22*math.sin(a):.1f}" r="4"/>')
        for ring, n in ((50, 18), (62, 22), (74, 26)):
            for k in range(n):
                a = math.radians(k * 360 / n + ring)
                out.append(f'<circle cx="{c+ring*math.cos(a):.1f}" cy="{c+ring*math.sin(a):.1f}" r="2.2" class="f"/>')
        out.append('<path d="M150 22a92 92 0 0 1 36 52" stroke-width="14" class="t"/>')
    elif kind == "gears":
        def gear(cx, cy, r, n, rot=0):
            pts = []
            for k in range(n * 4):
                a = math.radians(rot + k * 90 / n)
                rr = r + (8 if k % 4 in (1, 2) else 0)
                pts.append(f"{cx+rr*math.cos(a):.1f},{cy+rr*math.sin(a):.1f}")
            return f'<polygon points="{" ".join(pts)}"/><circle cx="{cx}" cy="{cy}" r="{r*.35:.1f}"/><circle cx="{cx}" cy="{cy}" r="{r*.7:.1f}" opacity=".4"/>'
        out.append(gear(84, 92, 56, 16))
        out.append(gear(150, 150, 34, 10, 9))
        out.append(gear(152, 48, 24, 8, 5))
    elif kind == "turbo":
        out.append(f'<circle cx="{c}" cy="{c}" r="92"/><circle cx="{c}" cy="{c}" r="78" opacity=".4"/><circle cx="{c}" cy="{c}" r="14"/>')
        for k in range(11):
            a = k * 360 / 11
            out.append(f'<path d="M100 86 C 118 70, 128 46, 116 24" transform="rotate({a:.1f} 100 100)"/>')
    elif kind == "palette":
        cols = ["#0b0d11", "#7c838e", "#f4f4f2", "#1d3f6e", "#9b1b30", "#b9bec5", "#24443a", "#c9a227"]
        for k, col in enumerate(cols):
            a0, a1 = math.radians(k * 45 - 90 + 2), math.radians((k + 1) * 45 - 90 - 2)
            r0, r1 = 58, 92
            p = (f"M{c+r1*math.cos(a0):.1f} {c+r1*math.sin(a0):.1f} A{r1} {r1} 0 0 1 {c+r1*math.cos(a1):.1f} {c+r1*math.sin(a1):.1f} "
                 f"L{c+r0*math.cos(a1):.1f} {c+r0*math.sin(a1):.1f} A{r0} {r0} 0 0 0 {c+r0*math.cos(a0):.1f} {c+r0*math.sin(a0):.1f}Z")
            out.append(f'<path d="{p}" fill="{col}" stroke="rgb(11 13 17 / .15)" stroke-width="1"/>')
        out.append(f'<circle cx="{c}" cy="{c}" r="44" opacity=".5"/><circle cx="{c}" cy="{c}" r="4" class="f"/>')
    elif kind == "gauge":
        out.append(f'<circle cx="{c}" cy="{c}" r="92"/><circle cx="{c}" cy="{c}" r="60" opacity=".4"/>')
        for k in range(72):
            a = math.radians(k * 5)
            r0 = 80 if k % 6 else 70
            out.append(f'<path d="M{c+r0*math.cos(a):.1f} {c+r0*math.sin(a):.1f}L{c+88*math.cos(a):.1f} {c+88*math.sin(a):.1f}"/>')
        out.append('<path d="M100 30v140M30 100h140" opacity=".5"/><path d="M100 64l10 18h-20z" class="f"/>')
    elif kind == "radar":
        for r in (92, 70, 48, 26):
            out.append(f'<circle cx="{c}" cy="{c}" r="{r}" opacity="{.35 if r < 92 else 1}"/>')
        out.append('<path d="M100 8v184M8 100h184" opacity=".35"/>')
        out.append('<g class="sweep"><path d="M100 100L100 8A92 92 0 0 1 165 35z" class="f" opacity=".18"/><path d="M100 100L165 35"/></g>')
        out.append('<circle cx="140" cy="60" r="4" class="f"/><circle cx="62" cy="128" r="3" class="f"/><circle cx="120" cy="150" r="3" class="f"/>')
    elif kind == "droplet":
        for r in (92, 72, 52):
            out.append(f'<circle cx="{c}" cy="{c}" r="{r}" class="ripple" opacity=".5"/>')
        out.append('<path d="M100 52s30 32 30 54a30 30 0 0 1-60 0c0-22 30-54 30-54z" stroke-width="3"/><path d="M86 112a14 14 0 0 0 14 14"/>')
    elif kind == "circuit":
        out.append(f'<circle cx="{c}" cy="{c}" r="92"/><circle cx="{c}" cy="{c}" r="40"/>')
        for k in range(12):
            a = math.radians(k * 30)
            x1, y1 = c + 40 * math.cos(a), c + 40 * math.sin(a)
            x2, y2 = c + 70 * math.cos(a), c + 70 * math.sin(a)
            x3, y3 = c + 70 * math.cos(a + .25), c + 70 * math.sin(a + .25)
            out.append(f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}L{x3:.1f} {y3:.1f}"/><circle cx="{x3:.1f}" cy="{y3:.1f}" r="3.5" class="f"/>')
        out.append('<path d="M106 74L86 104h16l-6 24 20-32h-16z" class="f"/>')
    elif kind == "flake":
        out.append(f'<circle cx="{c}" cy="{c}" r="92" opacity=".5"/>')
        for k in range(6):
            a = k * 60
            out.append(f'<g transform="rotate({a} 100 100)"><path d="M100 100V22M100 44l-14-14M100 44l14-14M100 66l-12-10M100 66l12-10"/></g>')
        out.append(f'<circle cx="{c}" cy="{c}" r="10" class="f"/>')
    return ('<svg class="emblem" viewBox="0 0 200 200" fill="none" stroke="currentColor" stroke-width="1.4" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + "".join(out) + "</svg>")

# ---------------------------------------------------------------- helpers
def wa_link(text):
    from urllib.parse import quote
    return f"https://wa.me/{WA}?text={quote(text)}"

def esc(s):
    return html.escape(s, quote=True)

def short_title(t):
    t = re.sub(r"^(Mercedes|Our Mercedes|Your Mercedes)\s+", "", t)
    t = t.replace(" Your Mercedes", "").replace(" Mercedes", "").replace(" in Abu Dhabi", "")
    return re.sub(r"\s+(for|to|of)$", "", t)

def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:48]

def urgency(txt):
    t = txt.lower()
    if "stop" in t or "burning" in t:
        return "stop", "Stop &amp; call"
    if "now" in t or "right away" in t:
        return "now", "Book now"
    if "days" in t or "soon" in t or "check" in t:
        return "soon", "Book soon"
    if "convenient" in t:
        return "later", "When convenient"
    return "info", "Recommended"

def split_head_rest(blocks):
    """paragraphs before the first non-paragraph block, and the rest."""
    head, rest, seen = [], [], False
    for b in blocks:
        if not seen and b[0] == "p":
            head.append(b[1])
        else:
            seen = True; rest.append(b)
    return head, rest

def paras(ps, cls=""):
    c = f' class="{cls}"' if cls else ""
    return "".join(f"<p{c}>{inline(p)}</p>" for p in ps)

def head(eyebrow, title, ps, center=False, dark=False, hid=None):
    cls = "head head--center" if center else "head"
    return (f'<div class="{cls} reveal"><span class="eyebrow">{eyebrow}</span>'
            f'<h2>{esc(title)}</h2>{paras(ps)}</div>')

# ---------------------------------------------------------------- viz
def viz_html(v):
    t = v["type"]
    if t == "bars":
        rows = []
        mx = v.get("max") or max(x["value"] for x in v["items"])
        for x in v["items"]:
            lo = x.get("lo")
            w = x["value"] / mx * 100
            left = (lo / mx * 100) if lo is not None else 0
            rows.append(
                f'<li class="vbar__row"><span class="vbar__label">{x["label"]}</span>'
                f'<span class="vbar__track"><span class="vbar__fill" style="--l:{left:.1f}%;--w:{w - left:.1f}%"></span></span>'
                f'<b class="vbar__val">{x["show"]}</b></li>')
        marks = "".join(f'<span class="vbar__mark" style="--x:{m["at"]/mx*100:.1f}%"><i>{m["label"]}</i></span>' for m in v.get("marks", []))
        return (f'<figure class="viz vbar vbar--{v.get("tone","heat")} reveal"><figcaption><b>{v["title"]}</b>'
                f'{"<span>"+v["note"]+"</span>" if v.get("note") else ""}</figcaption>'
                f'<ul class="vbar__list">{"".join(rows)}</ul><div class="vbar__marks">{marks}</div></figure>')
    if t == "donut":
        r = 52; C = 2 * math.pi * r
        return (f'<figure class="viz donut reveal" style="--C:{C:.1f};--p:{v["value"]}">'
                f'<div class="donut__ring"><svg viewBox="0 0 140 140" aria-hidden="true"><circle cx="70" cy="70" r="{r}" class="donut__bg"/>'
                f'<circle cx="70" cy="70" r="{r}" class="donut__fg"/></svg>'
                f'<div class="donut__num"><b>{v["show"]}</b><span>{v["label"]}</span></div></div>'
                f'<figcaption>{v["title"]}</figcaption></figure>')
    if t == "stats":
        items = "".join(
            f'<div class="istat"><b>{x["pre"] if x.get("pre") else ""}<span {"data-count=" + chr(34) + str(x["count"]) + chr(34) if x.get("count") is not None else ""}>{x["num"]}</span>{x.get("suf","")}</b><span>{x["label"]}</span></div>'
            for x in v["items"])
        return f'<div class="viz istats reveal">{"<p class=istats__t>"+v["title"]+"</p>" if v.get("title") else ""}{items}</div>'
    if t == "gauge":
        return ('<figure class="viz uv reveal" style="--v:%s"><svg viewBox="0 0 220 130" aria-hidden="true">'
                '<defs><linearGradient id="uvg" x1="0" x2="1"><stop offset="0" stop-color="#3fb950"/><stop offset=".3" stop-color="#f5c518"/>'
                '<stop offset=".55" stop-color="#f08c00"/><stop offset=".78" stop-color="#e5484d"/><stop offset="1" stop-color="#8e44ad"/></linearGradient></defs>'
                '<path d="M20 115a90 90 0 0 1 180 0" stroke="url(#uvg)" stroke-width="18" fill="none" stroke-linecap="round"/>'
                '<g class="uv__needle"><path d="M110 115L110 40" stroke="#0b0d11" stroke-width="4" stroke-linecap="round"/><circle cx="110" cy="115" r="9" fill="#0b0d11"/></g></svg>'
                '<div class="uv__num"><b>%s</b><span>%s</span></div><figcaption>%s</figcaption></figure>') % (v["value"] / v["max"], v["show"], v["label"], v["title"])
    if t == "layers":
        ls = "".join(f'<div class="layer" style="--i:{k};--c:{x["c"]}"><span class="layer__tag"><b>{x["name"]}</b>{x.get("note","")}</span></div>'
                     for k, x in enumerate(v["items"]))
        return f'<figure class="viz layers reveal" style="--n:{len(v["items"])}"><div class="layers__stack">{ls}</div><figcaption>{v["title"]}</figcaption></figure>'
    if t == "cone":
        return ('<figure class="viz cone reveal"><svg viewBox="0 0 520 220" aria-hidden="true">'
                '<rect x="0" y="0" width="520" height="220" rx="18" class="cone__road"/>'
                '<path d="M0 74H520M0 146H520" class="cone__lane"/>'
                '<path d="M66 110L510 110" class="cone__ok"/><path d="M66 110L510 52" class="cone__bad"/>'
                '<path d="M66 110L510 92L510 128Z" class="cone__beam"/>'
                '<g transform="translate(18 96)"><rect width="52" height="28" rx="9" class="cone__car"/><circle cx="46" cy="14" r="4" fill="#4fb0ff"/></g>'
                '<text x="500" y="102" text-anchor="end" class="cone__t ok">Correct aim: stays in its lane</text>'
                '<text x="500" y="34" text-anchor="end" class="cone__t bad">A few degrees off: the next lane</text></svg>'
                f'<figcaption>{v["title"]}</figcaption></figure>')
    if t == "code":
        parts = "".join(f'<span class="code__ch" style="--i:{k}"><b>{ch}</b><i>{lab}</i></span>' for k, (ch, lab) in enumerate(v["parts"]))
        return f'<figure class="viz code reveal"><div class="code__row">{parts}</div><figcaption>{v["title"]}</figcaption></figure>'
    if t == "image":
        return f'<figure class="viz vimg reveal"><img src="../assets/img/{v["src"]}-sm.webp" srcset="../assets/img/{v["src"]}-sm.webp 800w, ../assets/img/{v["src"]}.webp 1600w" sizes="(max-width: 900px) 100vw, 45vw" alt="{esc(v["alt"])}" loading="lazy" width="800" height="533"></figure>'
    return ""

# ---------------------------------------------------------------- table renderers
def tbl_default(rows):
    h, body = rows[0], rows[1:]
    th = "".join(f"<th scope=col>{inline(c)}</th>" for c in h)
    trs = "".join("<tr>" + "".join(f'<td data-label="{esc(plain(h[k]) if k < len(h) else "")}">{inline(c)}</td>' for k, c in enumerate(r)) + "</tr>" for r in body)
    return f'<div class="table-wrap stable reveal"><table class="table"><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

_CARDS = [0]

def tbl_cards(rows):
    _CARDS[0] += 1
    ring = _CARDS[0] % 2 == 1
    h, body = rows[0], rows[1:]
    cards = []
    for k, r in enumerate(body):
        dl = "".join(f"<div><dt>{inline(h[j])}</dt><dd>{inline(c)}</dd></div>" for j, c in enumerate(r[1:], 1) if c)
        cards.append(f'<article class="spec" style="--i:{k}"><span class="spec__k">{plain(h[0])}</span><h3>{inline(r[0])}</h3><dl>{dl}</dl></article>')
    return (f'<div class="ring reveal" data-ring><div class="ring__stage"><div class="specs ring__track">{"".join(cards)}</div></div>'
            f'<div class="ring__ui"><button type="button" class="ring__b" data-ring-go="-1" aria-label="Previous">{svg(I["arrow"], "2")}</button>'
            f'<span class="ring__count"><b>01</b> / {len(cards):02d}</span><button type="button" class="ring__b" data-ring-go="1" aria-label="Next">{svg(I["arrow"], "2")}</button></div></div>') if ring else f'<div class="specs specs--rows reveal">{"".join(cards)}</div>'

def tbl_decision(rows, uid):
    h, body = rows[0], rows[1:]
    tabs, panels = [], []
    for k, r in enumerate(body):
        sel = "true" if k == 0 else "false"
        tabs.append(f'<button class="dec__tab" role="tab" id="{uid}-t{k}" aria-controls="{uid}-p{k}" aria-selected="{sel}"><span>{k+1:02d}</span>{inline(r[0])}</button>')
        why = f'<p class="dec__why"><span>{plain(h[2])}</span>{inline(r[2])}</p>' if len(r) > 2 else ""
        panels.append(f'<div class="dec__panel" role="tabpanel" id="{uid}-p{k}" aria-labelledby="{uid}-t{k}"{"" if k == 0 else " hidden"}>'
                      f'<span class="dec__k">{plain(h[1])}</span><p class="dec__opt">{inline(r[1])}</p>{why}</div>')
    return (f'<div class="dec reveal" data-tabs><div class="dec__tabs" role="tablist" aria-label="{esc(plain(h[0]))}">{"".join(tabs)}</div>'
            f'<div class="dec__stage">{"".join(panels)}</div></div>')

def tbl_matrix(rows):
    h, body = rows[0], rows[1:]
    def cell(c):
        t = plain(c).strip()
        if t == "Yes":
            return f'<span class="mx mx--y" aria-label="Yes">{svg(I["tick"], "2.6")}</span>'
        if t == "No":
            return f'<span class="mx mx--n" aria-label="No">{svg(I["x"], "2.4")}</span>'
        return f'<span class="mx mx--t">{inline(c)}</span>'
    th = "".join(f"<th scope=col>{inline(c)}</th>" for c in h)
    trs = "".join("<tr>" + f"<th scope=row>{inline(r[0])}</th>" + "".join(f'<td data-label="{esc(plain(h[j]))}">{cell(c)}</td>' for j, c in enumerate(r[1:], 1)) + "</tr>" for r in body)
    return f'<div class="matrix reveal"><table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'

PAINT_HEX = {"149": "#f3f3ef", "799": "#f7f5ee", "197": "#16181d", "040": "#050505", "775": "#b8bcc1", "992": "#80868f", "890": "#1f3458"}
def tbl_swatches(rows):
    h, body = rows[0], rows[1:]
    out = []
    for r in body:
        code = plain(r[0]).strip()
        col = PAINT_HEX.get(code, "#999")
        finish = plain(r[2]).lower()
        kind = "pearl" if "pearl" in finish else "metal" if "metallic" in finish else "solid"
        out.append(f'<article class="swatch swatch--{kind} tilt" style="--c:{col}"><div class="swatch__chip"><span>{code}</span></div>'
                   f'<h3>{inline(r[1])}</h3><span class="swatch__fin">{inline(r[2])}</span><p>{inline(r[3])}</p></article>')
    return f'<div class="swatches reveal">{"".join(out)}</div>'

def tbl_lights(rows):
    h, body = rows[0], rows[1:]
    out = []
    for k, r in enumerate(body):
        red = "red" in plain(r[1]).lower()
        flash = "flashing" in plain(r[0]).lower()
        out.append(f'<article class="wl {"wl--red" if red else "wl--amber"}{" wl--flash" if flash else ""}" style="--i:{k}">'
                   f'<span class="wl__lamp">{svg(I["alert"] if red else I["light"], "2")}</span>'
                   f'<div><h3>{inline(r[0])}</h3><p>{inline(r[2])}</p><span class="wl__do">{inline(r[3])}</span></div></article>')
    return f'<div class="wls reveal">{"".join(out)}</div>'

def tbl_letters(rows):
    h, body = rows[0], rows[1:]
    out = "".join(f'<article class="letter tilt"><b>{plain(r[0])}</b><h3>{inline(r[1])}</h3><p>{inline(r[2])}</p></article>' for r in body)
    return f'<div class="letters reveal">{out}</div>'

def tbl_compare2(rows):
    h, body = rows[0], rows[1:]
    cols = []
    for j in (1, 2):
        lis = "".join(f"<li><span>{inline(r[0])}</span><b>{inline(r[j])}</b></li>" for r in body)
        cols.append(f'<article class="cmp2__card{" cmp2__card--dark" if j == 2 else ""} tilt"><h3>{inline(h[j])}</h3><ul>{lis}</ul></article>')
    return f'<div class="cmp2 reveal">{"".join(cols)}</div>'

def tbl_escalate(rows):
    h, body = rows[0], rows[1:]
    out = "".join(f'<li class="esc__row" style="--i:{k}"><span class="esc__a">{inline(r[0])}</span><span class="esc__arrow">{svg(I["arrow"], "2")}</span><span class="esc__b">{inline(r[1])}</span></li>' for k, r in enumerate(body))
    return (f'<div class="esc reveal"><div class="esc__head"><span>{inline(h[0])}</span><span>{inline(h[1])}</span></div><ol>{out}</ol></div>')

def tbl_capacity(rows):
    h, body = rows[0], rows[1:]
    vals = []
    for r in body:
        m = re.search(r"([\d.]+)\s*L", plain(r[2]))
        vals.append(float(m.group(1)) if m else 0)
    mx = max(vals) or 1
    out = "".join(f'<li><div class="cap__meta"><b>{inline(r[0])}</b><span>{inline(r[1])}</span></div>'
                  f'<div class="cap__bar"><span style="--w:{v/mx*100:.1f}%"></span></div><strong>{inline(r[2])}</strong></li>' for r, v in zip(body, vals))
    return f'<div class="cap reveal"><ul>{out}</ul></div>'

def render_table(rows, uid):
    h = [plain(c).lower() for c in rows[0]]
    flat = " ".join(plain(c) for r in rows[1:] for c in r)
    if h[0] == "situation" or any(x in h for x in ("best option", "our approach")):
        return tbl_decision(rows, uid) if len(h) >= 2 else tbl_default(rows)
    if "paint code" in h[0]:
        return tbl_swatches(rows)
    if "warning light" in h[0]:
        return tbl_lights(rows)
    if "code letter" in h[0]:
        return tbl_letters(rows)
    if "oil capacity" in h:
        return tbl_capacity(rows)
    if len(h) == 3 and h[0] == "" and "agency" in h[1]:
        return tbl_compare2(rows)
    if len(h) == 2 and "if ignored" in h[1]:
        return tbl_escalate(rows)
    if flat.count("Yes") + flat.count("No") >= len(rows):
        return tbl_matrix(rows)
    if len(rows) - 1 <= 8 and len(h) >= 3:
        return tbl_cards(rows)
    return tbl_default(rows)

# ---------------------------------------------------------------- sections
def sec_symptoms(sec, cfg, sid):
    hp, rest = split_head_rest(sec["blocks"])
    rows = next(d for k, d in rest if k == "table")
    h, body = rows[0], rows[1:]
    has_urg = any(w in plain(h[2]).lower() for w in ("urgen", "what to do"))
    cards, counts = [], {}
    for k, r in enumerate(body):
        lvl, lab = urgency(plain(r[2])) if has_urg else ("info", plain(h[2]))
        counts[lvl] = counts.get(lvl, 0) + 1
        cards.append(
            f'<li class="sym sym--{lvl}" data-lvl="{lvl}" style="--i:{k}"><span class="sym__dot" aria-hidden="true"></span>'
            f'<h3>{inline(r[0])}</h3><p><span class="sym__k">{plain(h[1])}</span>{inline(r[1])}</p>'
            f'<span class="sym__badge">{inline(r[2]) if has_urg else inline(r[2])}</span></li>')
    filt = ""
    if has_urg:
        names = [("stop", "Stop &amp; call"), ("now", "Book now"), ("soon", "Book soon"), ("later", "When convenient")]
        btns = "".join(f'<button class="symf__b symf__b--{k}" data-f="{k}" aria-pressed="false"><i></i>{n}<span>{counts[k]}</span></button>' for k, n in names if counts.get(k))
        total = len(body)
        meter = "".join(f'<span class="symm symm--{k}" style="flex:{counts[k]}"></span>' for k, _ in names if counts.get(k))
        filt = (f'<div class="symf reveal"><div class="symf__btns"><button class="symf__b is-on" data-f="all" aria-pressed="true">All signs<span>{total}</span></button>{btns}</div>'
                f'<div class="symf__meter" aria-hidden="true">{meter}</div></div>')
    return (f'<section class="section ssym" id="{sid}"><div class="container">'
            f'<div class="ssym__top">{head("Know the warning signs", sec["title"], hp)}{filt}</div>'
            f'<ul class="syms" role="list">{"".join(cards)}</ul></div></section>')

def sec_timely(sec, cfg, sid):
    hp, rest = split_head_rest(sec["blocks"])
    extra_ps = [d for k, d in rest if k == "p"]
    tables = [d for k, d in rest if k == "table"]
    viz = "".join(viz_html(v) for v in cfg.get("timely", []))
    tbl = "".join(render_table(t, sid + "-t") for t in tables)
    return (f'<section class="section section--paper stimely" id="{sid}"><div class="container stimely__grid">'
            f'<div class="stimely__copy">{head("Why act early", sec["title"], hp)}<div class="stimely__more reveal">{paras(extra_ps)}</div></div>'
            f'<div class="stimely__side">{tbl}{viz}</div></div></section>')

def sec_services(sec, cfg, sid):
    hp, rest = split_head_rest(sec["blocks"])
    groups, cur = [], None
    for k, d in rest:
        if k == "h" and d[0] == 3:
            cur = {"title": d[1], "ps": [], "items": []}; groups.append(cur)
        elif k == "h" and d[0] >= 4 and cur is not None:
            cur["items"].append({"title": d[1], "ps": []})
        elif k == "p" and cur is not None:
            (cur["items"][-1]["ps"] if cur["items"] else cur["ps"]).append(d)
    photos = [cfg["photo"], cfg["photo2"]]
    slides, n = [], 0
    total = sum(len(g["items"]) for g in groups)
    for g_i, g in enumerate(groups):
        ph = photos[g_i % 2]
        slides.append(
            f'<article class="cf cf--intro"><img src="../assets/img/{ph[0]}-sm.webp" alt="{esc(ph[1])}" loading="lazy" width="800" height="533">'
            f'<div class="cf__body"><span class="cf__idx">Group {g_i+1:02d} / {len(groups):02d}</span><h3>{esc(g["title"])}</h3>{paras(g["ps"])}'
            f'<span class="cf__hint">{len(g["items"])} services {svg(I["arrow"], "2")}</span></div></article>')
        for it in g["items"]:
            n += 1
            wa = wa_link(f"Hello Exotic Auto Services, I'd like a quote for {it['title']} on my Mercedes.")
            slides.append(
                f'<article class="cf"><span class="cf__big" aria-hidden="true">{n:02d}</span>'
                f'<div class="cf__orb" aria-hidden="true"><i></i>{svg(icon_for(it["title"]), "1.6")}</div>'
                f'<span class="cf__n">{n:02d} / {total:02d}</span><h4>{esc(it["title"])}</h4>{paras(it["ps"])}'
                f'<a class="cf__ask" href="{wa}" target="_blank" rel="noopener">{WA_SVG}Ask about this</a></article>')
    return (f'<section class="section sserv2" id="{sid}"><div class="container sserv2__head">{head("What we fix", sec["title"], hp)}'
            f'<div class="cfui" aria-hidden="true"><button class="cfui__b" data-cf="-1" type="button" tabindex="-1">{svg(I["arrow"], "2")}</button>'
            f'<button class="cfui__b" data-cf="1" type="button" tabindex="-1">{svg(I["arrow"], "2")}</button></div></div>'
            f'<div class="cflow" data-cflow><div class="cflow__track">{"".join(slides)}</div></div>'
            f'<div class="container"><div class="cfbar"><span class="cfbar__fill"></span></div></div></section>')

def sec_heat(sec, cfg, sid):
    hp, rest = split_head_rest(sec["blocks"])
    ps = hp + [d for k, d in rest if k == "p"]
    viz = "".join(viz_html(v) for v in cfg.get("heat", []))
    return (f'<section class="section dark sheat" id="{sid}"><div class="sheat__glow" aria-hidden="true"></div><div class="container sheat__grid">'
            f'<div class="sheat__copy"><div class="reveal"><span class="eyebrow">{cfg.get("heat_eyebrow","Built for UAE conditions")}</span><h2>{esc(sec["title"])}</h2></div>'
            f'<div class="reveal">{paras(ps)}</div></div><div class="sheat__viz">{viz}</div></div></section>')

def sec_tips(sec, cfg, sid):
    hp, rest = split_head_rest(sec["blocks"])
    items = []
    for k, d in rest:
        if k == "li":
            m = re.match(r"\*\*(.+?):?\*\*:?\s*(.*)", d)
            t, body = (m.group(1).rstrip(":"), m.group(2)) if m else ("", d)
            items.append((t, body))
    cards = "".join(f'<li class="tip2 reveal" style="--i:{k}"><span class="tip2__n">{k+1:02d}</span><h3>{inline(t)}</h3><p>{inline(b)}</p></li>' for k, (t, b) in enumerate(items))
    return (f'<section class="section stips" id="{sid}"><div class="container">'
            f'{head("Owner tips", sec["title"], hp or ([cfg["tips_lead"]] if cfg.get("tips_lead") else []))}<ol class="tips2" role="list">{cards}</ol></div></section>')

def sec_process(sec, cfg, sid):
    hp, rest = split_head_rest(sec["blocks"])
    steps, cur = [], None
    for k, d in rest:
        if k == "h":
            cur = {"t": d[1], "ps": []}; steps.append(cur)
        elif k == "p" and cur:
            cur["ps"].append(d)
    lis = "".join(f'<li class="pstep" style="--i:{k}"><span class="pstep__dot">{k+1:02d}</span><div class="pstep__card reveal"><h3>{esc(s["t"])}</h3>{paras(s["ps"])}</div></li>' for k, s in enumerate(steps))
    return (f'<section class="section section--paper sproc" id="{sid}"><div class="container">'
            f'{head("How it works", sec["title"], hp or ["Five clear steps, the same on every job, so you always know what is happening and why."], center=True)}'
            f'<ol class="ptl" role="list"><span class="ptl__line" aria-hidden="true"><span class="ptl__fill"></span></span>{lis}</ol></div></section>')

def sec_why(sec, cfg, sid):
    hp, rest = split_head_rest(sec["blocks"])
    items, cur = [], None
    for k, d in rest:
        if k == "h":
            cur = {"t": d[1], "ps": []}; items.append(cur)
        elif k == "p" and cur:
            cur["ps"].append(d)
    cards = "".join(f'<article class="wcard tilt reveal"><span class="wcard__icon">{svg(I[WHY_ICONS[k % len(WHY_ICONS)]])}</span><h3>{esc(it["t"])}</h3>{paras(it["ps"])}</article>' for k, it in enumerate(items))
    return (f'<section class="section dark swhy" id="{sid}"><div class="container">'
            f'{head("Why Exotic Auto Services", sec["title"], hp or ["MOIAT-certified, Mercedes-focused and rated 4.5 from 765 Google reviews. Here is what that means for your car."])}'
            f'<div class="wcards">{cards}</div></div></section>')

def sec_faq(sec, cfg, sid, faq_out):
    items, cur = [], None
    for k, d in sec["blocks"]:
        if k == "h":
            cur = {"q": d[1], "ps": []}; items.append(cur)
        elif k == "p" and cur:
            cur["ps"].append(d)
    faq_out.extend(items)
    dets = "".join(f'<details{" open" if k == 0 else ""}><summary><h3>{esc(it["q"])}</h3></summary><div class="faq__a">{paras(it["ps"])}</div></details>' for k, it in enumerate(items))
    title = sec["title"].replace("Aasked", "Asked")
    return (f'<section class="section sfaq" id="{sid}"><div class="container sfaq__grid">'
            f'<div class="sfaq__side"><div class="sfaq__sticky reveal"><span class="eyebrow">FAQs</span><h2>{esc(title)}</h2>'
            f'<p>Still unsure? Send us a message with your model and what you have noticed. A Mercedes technician will reply.</p>'
            f'<div class="sfaq__card"><span class="sfaq__av">{svg(I["people"])}</span><div><b>Talk to a technician</b><span>Mon–Sat 9am–10pm · Sun 9am–7pm</span></div></div>'
            f'<div class="btn-row"><a class="btn btn--wa btn--sm" href="{wa_link(cfg["wa_text"])}" target="_blank" rel="noopener">{WA_SVG}WhatsApp</a>'
            f'<a class="btn btn--ghost btn--sm" href="tel:{TEL}">{svg(I["phone"])}Call</a></div></div></div>'
            f'<div class="faq">{dets}</div></div></section>')

def sec_generic(sec, cfg, sid, idx):
    hp, rest = split_head_rest(sec["blocks"])
    vizs = []
    for key, vs in cfg.get("viz", {}).items():
        if key.lower() in sec["title"].lower():
            vizs = vs
    tables = [d for k, d in rest if k == "table"]
    after = [d for k, d in rest if k == "p"]
    paper = idx % 2 == 0
    cls = "section section--paper sgen" if paper else "section sgen"
    if not tables:
        side = "".join(viz_html(v) for v in vizs) or viz_html({"type": "image", "src": cfg["photo"][0], "alt": cfg["photo"][1]})
        return (f'<section class="{cls}" id="{sid}"><div class="container split sgen__split">'
                f'<div>{head(cfg.get("eyebrows", {}).get(sec["title"], "Good to know"), sec["title"], hp)}<div class="reveal">{paras(after)}</div></div>'
                f'<div class="sgen__side">{side}</div></div></section>')
    body = "".join(render_table(t, f"{sid}-{k}") for k, t in enumerate(tables))
    vz = "".join(viz_html(v) for v in vizs)
    note = f'<div class="sgen__note reveal">{paras(after)}</div>' if after else ""
    if vz:
        return (f'<section class="{cls}" id="{sid}"><div class="container"><div class="sgen__hz">'
                f'{head(cfg.get("eyebrows", {}).get(sec["title"], "Reference"), sec["title"], hp)}<div class="sgen__vz">{vz}</div></div>{body}{note}</div></section>')
    return (f'<section class="{cls}" id="{sid}"><div class="container">'
            f'{head(cfg.get("eyebrows", {}).get(sec["title"], "Reference"), sec["title"], hp)}{body}{note}</div></section>')

def sec_book(sec, cfg, sid, ctas):
    ps = [d for k, d in sec["blocks"] if k == "p"]
    label = ctas[0] if ctas else "Book Now"
    title = sec["title"]
    return (f'<section class="section sbook" id="book"><div class="container"><div class="sbook__card">'
            f'<div class="sbook__glow" aria-hidden="true"></div>'
            f'<div class="sbook__copy"><span class="eyebrow">Book today</span><h2>{esc(title)}</h2>{paras(ps)}'
            f'<ul class="sbook__facts">'
            f'<li>{svg(I["pin"])}<span><b>Exotic Auto Services LLC</b>M-21, Mussafah Industrial Area, Abu Dhabi</span></li>'
            f'<li>{svg(I["clock"])}<span><b>Open 7 days</b>Mon–Sat 9am–10pm · Sun 9am–7pm</span></li>'
            f'<li>{svg(I["phone"])}<span><b>Call or WhatsApp</b><a href="tel:{TEL}">{TEL_TXT}</a></span></li></ul>'
            f'<img class="sbook__car" src="../assets/img/{cfg["cta_car"]}.webp" alt="" loading="lazy" width="1200" height="600"></div>'
            f'<form class="sbook__form" data-wa novalidate>'
            f'<h3>{esc(label)}</h3><p class="sbook__sub">Send your details and we will confirm a time on WhatsApp.</p>'
            f'<input type="hidden" name="service" value="{esc(cfg["service_name"])}">'
            f'<div class="field"><label for="b-name">Your name</label><input id="b-name" name="name" required autocomplete="name"></div>'
            f'<div class="form__row"><div class="field"><label for="b-mob">Mobile</label><input id="b-mob" name="mobile" type="tel" required autocomplete="tel" placeholder="05x xxx xxxx"></div>'
            f'<div class="field"><label for="b-model">Model &amp; year</label><input id="b-model" name="model" placeholder="e.g. C 300, 2021"></div></div>'
            f'<div class="field"><label for="b-msg">What have you noticed?</label><textarea id="b-msg" name="message" rows="3"></textarea></div>'
            f'<input type="text" name="website" tabindex="-1" autocomplete="off" class="sr-only" aria-hidden="true">'
            f'<button class="btn btn--accent magnetic" type="submit">{WA_SVG}{esc(label)} on WhatsApp</button>'
            f'<p class="form__ok" hidden>WhatsApp opened with your details. Press send and we will reply shortly.</p>'
            f'<div class="sbook__alt"><a href="tel:{TEL}">{svg(I["phone"])}Call Now {TEL_TXT}</a></div></form>'
            f'</div></div></section>')

def related(cur_slug):
    cards = []
    for s in ORDER:
        if s == cur_slug:
            continue
        p = PAGES[s]
        cards.append(f'<a class="rel tilt" href="../{s}/"><img src="../assets/img/{p["photo"][0]}-sm.webp" alt="" loading="lazy" width="800" height="533">'
                     f'<span class="rel__body"><span class="rel__icon">{svg(I[p["icon"]])}</span><b>{p["short"]}</b><span>{p["blurb"]}</span></span>'
                     f'<span class="rel__go">{svg(I["arrow"], "2")}</span></a>')
    return (f'<section class="section section--paper srel"><div class="container">'
            f'<div class="srel__head reveal"><div><span class="eyebrow">More Mercedes services</span><h2>Everything your Mercedes needs, under one roof</h2></div>'
            f'<a class="btn btn--ghost" href="../#services">All services</a></div><div class="rels">{"".join(cards)}</div></div></section>')

# ---------------------------------------------------------------- shared trust block (hero)
G_LOGO = ('<svg class="glogo" viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/>'
          '<path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>'
          '<path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/>'
          '<path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>')

def trust_html(root="../"):
    items = [("shield", "MOIAT", "Certified"), ("clock", "10+ Years", "Experience"),
             ("people", "1,000+", "Happy customers"), ("check", "Genuine", "or OE parts")]
    lis = "".join(f'<li>{svg(I[i], "1.8")}<b>{a}</b><span>{b}</span></li>' for i, a, b in items)
    return (f'<ul class="trust" role="list">{lis}</ul>'
            '<div class="rate"><span class="rate__avs" aria-hidden="true"><i>J</i><i>S</i><i>A</i><i class="k">1K+</i></span>'
            '<span class="rate__txt">Trusted by <b>1,000+</b> owners</span>'
            f'<span class="rate__g"><b>4.5</b><span class="rate__stars" aria-hidden="true">★★★★★</span><small>(765 reviews)</small>{G_LOGO}</span></div>')

# ---------------------------------------------------------------- hero
def split_words(text, cls=""):
    return " ".join(f'<span class="w{(" " + cls) if cls else ""}"><span>{esc(w)}</span></span>' for w in text.split())

def hero(doc, cfg, ticker_items):
    h1 = doc["h1"]
    m = re.search(r"\s(That|for|Matched|with)\s", h1)
    h1_html = (split_words(h1[:m.start()]) + " " + split_words(h1[m.start() + 1:], "g")) if m else split_words(h1)
    ctas = doc["ctas"]
    label = ctas[0] if ctas else "Book Now"
    photos_btn = any("Photo" in c for c in ctas)
    second = (f'<a class="btn btn--wa magnetic" href="{wa_link(cfg["photo_text"])}" target="_blank" rel="noopener">{WA_SVG}WhatsApp Photos</a>' if photos_btn else
              f'<a class="btn btn--wa magnetic" href="{wa_link(cfg["wa_text"])}" target="_blank" rel="noopener">{WA_SVG}WhatsApp Us</a>')
    chips = "".join(f'<div class="schip schip--{k}" data-depth="{(k + 1) * 14}"><span class="schip__icon">{svg(I[c[0]])}</span><span><b>{c[1]}</b>{c[2]}</span></div>' for k, c in enumerate(cfg["chips"]))
    stats = "".join(
        f'<div class="hstat"><b>{s.get("pre","")}<span{(" data-count=" + chr(34) + str(s["count"]) + chr(34)) if s.get("count") is not None else ""}>{s["num"]}</span>{s.get("suf","")}</b><span>{s["label"]}</span></div>'
        for s in cfg["stats"])
    car = cfg["car"]
    hp = cfg["hero"]
    tick = "".join(f"<span>{esc(t)}</span>" for t in ticker_items) * 2
    return f'''
<section class="shero2" style="--tone:{cfg["tone"]}">
  <div class="shero2__bg" aria-hidden="true"><img src="../assets/img/{hp[0]}.webp" srcset="../assets/img/{hp[0]}-sm.webp 900w, ../assets/img/{hp[0]}.webp 2000w" sizes="100vw" alt="" fetchpriority="high"></div>
  <canvas class="shero2__fx" aria-hidden="true"></canvas>
  <span class="shero2__word" aria-hidden="true">{cfg["word"]}</span>
  <div class="container shero2__grid">
    <div class="shero2__copy">
      <ol class="crumbs"><li><a href="../">Home</a></li><li><a href="../#services">Services</a></li><li aria-current="page">{cfg["short"]}</li></ol>
      <span class="shero2__badge"><i></i>Mercedes specialists · Mussafah M-21</span>
      <h1>{h1_html}</h1>
      <div class="shero2__lead">{paras(doc["intro"], "lead")}</div>
      <div class="btn-row shero2__ctas">
        <a class="btn btn--accent magnetic" href="#book">{esc(label)} {svg(I["arrow"], "2")}</a>
        {second}
      </div>
      {trust_html()}
    </div>
    <div class="shero2__stage" data-stage>
      <div class="turn" aria-hidden="true"><i></i><i></i><i></i><b></b></div>
      <div class="shero2__emblem" data-depth="-20" aria-hidden="true">{emblem(cfg["emblem"])}</div>
      <div class="shero2__car" data-depth="10">
        <img src="../assets/img/{car[0]}.webp" alt="{esc(car[1])}" width="2200" height="1200">
        <span class="sheen" aria-hidden="true" style="-webkit-mask-image:url(../assets/img/{car[0]}.webp);mask-image:url(../assets/img/{car[0]}.webp)"></span>
      </div>
      {chips}
    </div>
  </div>
  <div class="sticker" aria-hidden="true"><div class="sticker__row">{tick}</div></div>
  <div class="container"><div class="hstats">{stats}</div></div>
</section>'''


# ---------------------------------------------------------------- page
def render(slug):
    cfg = PAGES[slug]
    text = (SRC / "services" / f"{slug}.md").read_text(encoding="utf-8")
    for a, b in cfg.get("fixes", {}).items():
        text = text.replace(a, b)
    doc = to_doc(parse(text))
    _CARDS[0] = 0
    ticker = []
    for sec in doc["sections"]:
        if "services we offer" in sec["title"].lower():
            ticker = [d[1] for k, d in sec["blocks"] if k == "h" and d[0] >= 4]
    parts, toc, faq, gen_i = [], [], [], 0
    for sec in doc["sections"]:
        t = sec["title"]
        tl = t.lower()
        sid = slugify(short_title(t))
        if tl.startswith("book your"):
            parts.append(sec_book(sec, cfg, sid, doc["ctas"])); continue
        if "signs" in tl and any(k == "table" for k, _ in sec["blocks"]):
            parts.append(sec_symptoms(sec, cfg, sid)); toc.append((sid, "Warning signs"))
        elif tl.startswith("why timely"):
            parts.append(sec_timely(sec, cfg, sid)); toc.append((sid, "Why act early"))
        elif "services we offer" in tl:
            parts.append(sec_services(sec, cfg, sid)); toc.append((sid, "Services"))
        elif ("heat" in tl or "sun affects" in tl) and tl.startswith("how abu dhabi"):
            parts.append(sec_heat(sec, cfg, sid)); toc.append((sid, "Abu Dhabi heat" if "heat" in tl else "Abu Dhabi sun"))
        elif tl.startswith("tips"):
            parts.append(sec_tips(sec, cfg, sid)); toc.append((sid, "Tips"))
        elif "process" in tl:
            parts.append(sec_process(sec, cfg, sid)); toc.append((sid, "Process"))
        elif tl.startswith("why choose"):
            parts.append(sec_why(sec, cfg, sid)); toc.append((sid, "Why us"))
        elif "frequently" in tl:
            parts.append(sec_faq(sec, cfg, sid, faq)); toc.append((sid, "FAQs"))
        else:
            parts.append(sec_generic(sec, cfg, sid, gen_i)); gen_i += 1
            toc.append((sid, cfg.get("toc", {}).get(t, short_title(t))))
    subnav = ('<nav class="subnav" aria-label="On this page"><div class="container subnav__in"><span class="subnav__t">On this page</span><div class="subnav__links">'
              + "".join(f'<a href="#{i}">{esc(n)}</a>' for i, n in toc) + '</div><a class="btn btn--accent btn--sm subnav__cta" href="#book">Book</a></div>'
              '<span class="subnav__bar" aria-hidden="true"></span></nav>')
    # body order: hero, subnav, sections (book last before related)
    book = [p for p in parts if 'id="book"' in p]
    rest = [p for p in parts if 'id="book"' not in p]
    # alternate white / paper backgrounds, counting back from the paper "related" band
    paper = False
    for k in range(len(rest) - 1, -1, -1):
        if rest[k].startswith('<section class="section dark'):
            continue
        rest[k] = re.sub(r'^<section class="section(?: section--paper)? ', '<section class="section section--paper ' if paper else '<section class="section ', rest[k], count=1)
        paper = not paper
    body = "<main id=\"main\" class=\"svcpage\" style=\"--tone:%s\">" % cfg["tone"] + hero(doc, cfg, ticker) + subnav + "".join(rest) + related(slug) + "".join(book) + "</main>\n"

    schema = [{
        "@context": "https://schema.org", "@type": "Service",
        "name": doc["meta"]["title"].split("|")[0].strip(),
        "serviceType": cfg["service_name"],
        "description": doc["meta"]["desc"],
        "provider": {"@id": "https://exoticautoservices.ae/#business"},
        "areaServed": {"@type": "City", "name": "Abu Dhabi"},
    }]
    if faq:
        schema.append({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": " ".join(plain(p) for p in f["ps"])}} for f in faq]})
    schema_html = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>\n' for s in schema)
    meta = {
        "out": f"{slug}/index.html",
        "title": doc["meta"]["title"],
        "desc": doc["meta"]["desc"],
        "cur": "services",
        "preload": f'<link rel="preload" as="image" href="../assets/img/{cfg["car"][0]}.webp">',
        "styles": ["assets/css/service.css?v=6"],
        "scripts": ["assets/js/service.js?v=6"],
        "schema": schema_html,
    }
    return meta, body

def render_all():
    return [render(s) for s in ORDER]
