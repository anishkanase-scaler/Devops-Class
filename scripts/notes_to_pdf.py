#!/usr/bin/env python3
"""
notes_to_pdf.py — turn a Class-NN/notes.md into a styled Class-NN/notes.pdf.

    .venv/bin/python scripts/notes_to_pdf.py Class-NN/notes.md Class-NN/notes.pdf

See CLAUDE.md ("Task: turning notes.md into a PDF") for the contract this
implements: per-class theme, dark gradient cover, rainbow section headers,
emoji-keyed callout cards, terminal code blocks, zebra tables.
"""

import os
import re
import sys
import html as _html

# WeasyPrint needs homebrew's pango/gdk-pixbuf; set this BEFORE the import.
os.environ.setdefault("DYLD_FALLBACK_LIBRARY_PATH", "/opt/homebrew/lib")

import markdown  # noqa: E402
from weasyprint import HTML  # noqa: E402


# ──────────────────────────────────────────────────────────────────────────
#  Per-class themes.  Add an entry whenever a new class appears, otherwise
#  it falls back to grey Graphite.
# ──────────────────────────────────────────────────────────────────────────
THEMES = {
    1:  ("Sunrise",        "#ff7849", "#ffb347", "#2b1503"),
    2:  ("Deep Ocean",     "#2563eb", "#38bdf8", "#04101f"),
    3:  ("Terminal Green", "#22c55e", "#86efac", "#04170c"),
    4:  ("Grape Soda",     "#a855f7", "#e879f9", "#1a0625"),
    5:  ("Slate",          "#64748b", "#94a3b8", "#0b1220"),
    6:  ("Docker Whale",   "#0ea5e9", "#67e8f9", "#031722"),
    7:  ("Neon Nights",    "#d946ef", "#f0abfc", "#1b0524"),
    8:  ("High Voltage",   "#eab308", "#fde047", "#211703"),
    9:  ("Compose Teal",   "#14b8a6", "#5eead4", "#04201d"),
    10: ("Kube Indigo",    "#6366f1", "#a5b4fc", "#0b0a2b"),
    11: ("Lagoon",         "#06b6d4", "#7dd3fc", "#032027"),
    12: ("Ember",          "#f97316", "#fdba74", "#231003"),
    13: ("Signal Blue",    "#3b82f6", "#93c5fd", "#040f26"),
    14: ("Moss",           "#65a30d", "#bef264", "#101c03"),
    15: ("Magma",          "#e11d48", "#fb7185", "#250309"),
    16: ("Iris",           "#8b5cf6", "#c4b5fd", "#140828"),
    17: ("Pipeline Mint",  "#10b981", "#6ee7b7", "#03201a"),
    18: ("Shield Crimson", "#dc2626", "#fca5a5", "#240404"),
    19: ("Terraform Plum", "#7c3aed", "#a78bfa", "#12062a"),
    20: ("Cloud Amber",    "#f59e0b", "#fcd34d", "#221603"),
    21: ("Launch Cyan",    "#0891b2", "#67e8f9", "#031c24"),
}
FALLBACK_THEME = ("Graphite", "#52525b", "#a1a1aa", "#0c0c0f")

# Rotating accents for `##` section headers.
SECTION_ACCENTS = [
    "#ef4444", "#f97316", "#eab308", "#22c55e", "#14b8a6",
    "#0ea5e9", "#6366f1", "#a855f7", "#ec4899",
]

# keyword -> emoji, used when a heading has no explicit emoji of its own.
SECTION_EMOJI = [
    ("60-second",      "⚡"), ("cheat",        "🧾"), ("homework",     "📝"),
    ("transcript",     "🗒️"), ("housekeep",    "🗓️"), ("logistics",    "🗓️"),
    ("warm-up",        "🔁"), ("recap",        "🔁"), ("drill",        "🔁"),
    ("volume",         "📦"), ("storage",      "💾"), ("persistent",   "💾"),
    ("claim",          "🎟️"), ("storageclass", "⚡"), ("access mode",  "🔐"),
    ("reclaim",        "♻️"), ("hpa",          "📈"), ("autoscal",     "📈"),
    ("scale",          "📈"), ("probe",        "🩺"), ("health",       "🩺"),
    ("lab",            "🏋️"), ("hands-on",     "🏋️"), ("network",      "🌐"),
    ("service",        "🔌"), ("ingress",      "🚪"), ("configmap",    "🗂️"),
    ("secret",         "🔐"), ("docker",       "🐳"), ("container",    "📦"),
    ("image",          "🖼️"), ("deployment",   "🚀"), ("pod",          "🫛"),
    ("kubernetes",     "☸️"), ("helm",         "⛵"), ("git",          "🌿"),
    ("linux",          "🐧"), ("shell",        "🐚"), ("script",       "📜"),
    ("review",         "🔎"), ("mini-project", "🏗️"), ("project",      "🏗️"),
    ("cleanup",        "🧹"), ("delete",       "🧹"), ("why",          "🧠"),
    ("question",       "❓"), ("interview",    "🎯"), ("bonus",        "🎁"),
]

# Callout emoji -> (css class, label).  The renderer keys off these exactly.
CALLOUTS = {
    "🧠":  ("c-brain",  "Picture this"),
    "💡":  ("c-bulb",   "Good to know"),
    "⚠️":  ("c-warn",   "Watch out"),
    "✅":  ("c-lock",   "Lock this in"),
    "🎯":  ("c-target", "Interview alert"),
    "🎤":  ("c-quote",  "Said in class"),
    "🔍":  ("c-clar",   "Clarified"),
    "😄":  ("c-fun",    "Class moment"),
    "🔥":  ("c-hard",   "Hard mode"),
    "📌":  ("c-note",   "Note"),
    "🧪":  ("c-try",    "Try it yourself"),
    "🎬":  ("c-film",   "Watch it happen"),
    "🏋️":  ("c-lab",    "Do this yourself"),
    "🧩":  ("c-mech",   "Why it works"),
    "📝":  ("c-hw",     "Homework"),
}
# Match longest-first so the variation-selector forms win.
CALLOUT_KEYS = sorted(CALLOUTS, key=len, reverse=True)

MD_EXTS = ["fenced_code", "codehilite", "tables", "attr_list", "sane_lists", "md_in_html"]
MD_CFG = {"codehilite": {"noclasses": False, "pygments_style": "dracula", "guess_lang": False}}

PLACEHOLDER = "xxbqplaceholderxx{}xx"
PLACEHOLDER_RE = re.compile(r"xxbqplaceholderxx(\d+)xx")


def make_md():
    return markdown.Markdown(extensions=MD_EXTS, extension_configs=MD_CFG)


# ──────────────────────────────────────────────────────────────────────────
#  Blockquote extraction.
#
#  python-markdown's fenced-code handler is a PREPROCESSOR that only sees ```
#  at the start of a line, so a fence behind a "> " prefix never becomes a
#  code block.  So: lift every top-level blockquote out, leave a padded
#  placeholder paragraph, render its inner markdown with a fresh Markdown
#  instance, and splice the result back in afterwards.
# ──────────────────────────────────────────────────────────────────────────
def extract_blockquotes(text):
    lines = text.split("\n")
    out, blocks = [], []
    i = 0
    while i < len(lines):
        if lines[i].startswith(">"):
            j = i
            buf = []
            while j < len(lines) and lines[j].startswith(">"):
                stripped = lines[j][1:]
                if stripped.startswith(" "):
                    stripped = stripped[1:]
                buf.append(stripped)
                j += 1
            blocks.append("\n".join(buf))
            # blank-line padding so a neighbouring list or paragraph can't
            # swallow the placeholder as a lazy continuation line.
            out.extend(["", PLACEHOLDER.format(len(blocks) - 1), ""])
            i = j
        else:
            out.append(lines[i])
            i += 1
    return "\n".join(out), blocks


def render_callout(inner_md):
    """Render one blockquote's inner markdown into a <blockquote> card."""
    css_class, label = "c-plain", None
    body = inner_md
    for key in CALLOUT_KEYS:
        if body.lstrip().startswith(key):
            css_class, label = CALLOUTS[key]
            body = body.lstrip()[len(key):].lstrip()
            break

    # Nested blockquotes inside a callout get the same treatment.
    body, nested = extract_blockquotes(body)
    html_body = make_md().convert(body)
    if nested:
        html_body = restore_blockquotes(html_body, nested)

    head = ""
    if label:
        head = (
            f'<div class="callout-head"><span class="callout-chip">{label}</span></div>'
        )
    return f'<blockquote class="callout {css_class}">{head}{html_body}</blockquote>'


def restore_blockquotes(html_text, blocks):
    rendered = [render_callout(b) for b in blocks]

    def swap(m):
        return rendered[int(m.group(1))]

    # Pass 1: the placeholder as its own paragraph.
    for idx, card in enumerate(rendered):
        html_text = html_text.replace(f"<p>{PLACEHOLDER.format(idx)}</p>", card)
    # Pass 2 (loose fallback): anywhere it survived, e.g. absorbed into a <li>.
    html_text = PLACEHOLDER_RE.sub(swap, html_text)

    assert "xxbqplaceholder" not in html_text, "a callout placeholder was lost"
    return html_text


# ──────────────────────────────────────────────────────────────────────────
#  Headings
# ──────────────────────────────────────────────────────────────────────────
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF←-⇿⌀-➿⬀-⯿⏩-⏺©®]"
    "[️‍\U0001F3FB-\U0001F3FF]*"
)


def pick_emoji(title):
    """An explicit emoji in the heading wins; else the keyword map; else a dot."""
    bare = re.sub(r"^\s*\d+[.)]\s*", "", title)  # strip a leading "12. "
    m = EMOJI_RE.match(bare.strip())
    if m:
        return m.group(0), EMOJI_RE.sub("", bare, count=1).strip()
    low = bare.lower()
    for kw, emo in SECTION_EMOJI:
        if kw in low:
            return emo, bare.strip()
    return "•", bare.strip()


INLINE_CODE = re.compile(r"`([^`]+)`")
INLINE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
INLINE_EM = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def inline_md(s):
    """Minimal inline markdown for heading text, which is not run through
    the full parser (it is rebuilt from plain text in decorate_headings)."""
    s = _html.escape(s)
    s = INLINE_CODE.sub(r"<code>\1</code>", s)
    s = INLINE_BOLD.sub(r"<strong>\1</strong>", s)
    s = INLINE_EM.sub(r"<em>\1</em>", s)
    return s


def collect_sections(text):
    """Every `## N. Title` -> (number, emoji, clean title, accent)."""
    out = []
    for line in text.split("\n"):
        if line.startswith("## "):
            raw = line[3:].strip()
            m = re.match(r"^(\d+)[.)]\s*(.*)$", raw)
            num, rest = (m.group(1), m.group(2)) if m else ("", raw)
            emo, clean = pick_emoji(rest)
            out.append((num, emo, clean, SECTION_ACCENTS[len(out) % len(SECTION_ACCENTS)]))
    return out


def decorate_headings(html_text, sections):
    """Give each <h2> a numeral badge, its emoji and its rotating accent."""
    idx = {"i": 0}

    def sub(m):
        inner = m.group(1)
        if idx["i"] >= len(sections):
            return m.group(0)
        num, emo, clean, accent = sections[idx["i"]]
        idx["i"] += 1
        badge = f'<span class="h2-badge">{_html.escape(num)}</span>' if num else ""
        return (
            f'<h2 style="--accent:{accent}">{badge}'
            f'<span class="h2-emoji">{emo}</span>'
            f'<span class="h2-text">{inline_md(clean)}</span></h2>'
        )

    return re.sub(r"<h2[^>]*>(.*?)</h2>", sub, html_text, flags=re.S)


def strip_empty_theads(html_text):
    """`| | |` header rows render as a blank coloured bar — drop them."""
    def sub(m):
        thead = m.group(0)
        if re.sub(r"<[^>]+>|&nbsp;|\s", "", thead) == "":
            return "__NOHEAD__"
        return thead

    html_text = re.sub(r"<thead>.*?</thead>", sub, html_text, flags=re.S)
    html_text = re.sub(
        r"<table>(\s*)__NOHEAD__", r'<table class="nohead">\1', html_text
    )
    return html_text.replace("__NOHEAD__", "")


def tick_lists(html_text):
    html_text = html_text.replace("<li>[x] ", '<li class="tick done">')
    html_text = html_text.replace("<li>[ ] ", '<li class="tick">')
    return html_text


# ──────────────────────────────────────────────────────────────────────────
#  Front matter / cover
# ──────────────────────────────────────────────────────────────────────────
def split_front_matter(text):
    """Everything before the first `---` line is the metadata header block."""
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if line.strip() == "---" and i > 0:
            return "\n".join(lines[:i]), "\n".join(lines[i + 1:])
    return "", text


def build_cover(front, sections, theme):
    name, c1, c2, dark = theme
    title, meta_rows = "", []
    for line in front.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            title = line[2:].strip()
        elif line.startswith("**") and ":**" in line:
            k, _, v = line.partition(":**")
            meta_rows.append((k.strip("* "), v.strip()))

    md = make_md()
    rows = "".join(
        f'<div class="meta-row"><div class="meta-k">{_html.escape(k)}</div>'
        f'<div class="meta-v">{md.reset().convert(v).removeprefix("<p>").removesuffix("</p>")}</div></div>'
        for k, v in meta_rows
    )
    chips = "".join(
        f'<div class="chip" style="--accent:{a}">'
        f'<span class="chip-num">{_html.escape(n)}</span>'
        f'<span class="chip-emoji">{e}</span>'
        f'<span class="chip-text">{inline_md(t)}</span></div>'
        for n, e, t, a in sections
    )
    return f"""
<section class="cover">
  <div class="cover-glow"></div>
  <div class="cover-kicker">{_html.escape(name)}</div>
  <h1 class="cover-title">{_html.escape(title)}</h1>
  <div class="meta-card">{rows}</div>
  <div class="chips-head">What's inside</div>
  <div class="chips">{chips}</div>
</section>
"""


# ──────────────────────────────────────────────────────────────────────────
#  CSS
# ──────────────────────────────────────────────────────────────────────────
def build_css(theme, footer):
    name, c1, c2, dark = theme
    return f"""
@page {{
  size: A4; margin: 17mm 15mm 16mm 15mm;
  @top-right  {{ content: "{footer}"; font-size: 7.5pt; color: #94a3b8;
                 font-family: Inter, Helvetica, sans-serif; }}
  @bottom-right {{ content: counter(page); font-size: 8pt; color: {c1}; font-weight: 700;
                   font-family: Inter, Helvetica, sans-serif; }}
  @bottom-left {{ content: "{name}"; font-size: 7pt; color: #cbd5e1; letter-spacing: .08em;
                  text-transform: uppercase; font-family: Inter, Helvetica, sans-serif; }}
}}
/* the running footer must not bleed onto the cover */
@page :first {{ margin: 0;
  @top-right {{ content: ""; }} @bottom-right {{ content: ""; }} @bottom-left {{ content: ""; }}
}}

* {{ box-sizing: border-box; }}
body {{ font-family: Inter, "Helvetica Neue", Helvetica, "Apple Color Emoji", sans-serif;
        font-size: 9.3pt; line-height: 1.62; color: #1e293b; margin: 0; }}

/* ── cover ─────────────────────────────────────────────────────────── */
.cover {{ page: first; page-break-after: always; position: relative; overflow: hidden;
          padding: 20mm 15mm; height: 297mm;
          background: linear-gradient(150deg, {dark} 0%, #000 55%, {dark} 100%); }}
.cover > * {{ position: relative; }}          /* the glow must not paint over the title */
.cover-glow {{ position: absolute; top: -70mm; right: -60mm; width: 190mm; height: 190mm;
               border-radius: 50%; opacity: .30;
               background: radial-gradient(circle, {c1} 0%, transparent 68%); }}
.cover-kicker {{ font-size: 8pt; letter-spacing: .34em; text-transform: uppercase;
                 color: {c2}; font-weight: 700; margin-bottom: 7mm; }}
.cover-title {{ font-size: 30pt; line-height: 1.12; font-weight: 800; color: #fff;
                margin: 0 0 9mm 0; letter-spacing: -.015em;
                border-left: 4px solid {c1}; padding-left: 6mm; }}
.meta-card {{ background: rgba(255,255,255,.055); border: 1px solid rgba(255,255,255,.13);
              border-radius: 4mm; padding: 6mm 7mm; margin-bottom: 9mm; }}
.meta-row {{ display: flex; gap: 5mm; padding: 1.5mm 0;
             border-bottom: 1px solid rgba(255,255,255,.07); }}
.meta-row:last-child {{ border-bottom: none; }}
.meta-k {{ flex: 0 0 30mm; font-size: 7.4pt; letter-spacing: .1em; text-transform: uppercase;
           color: {c2}; font-weight: 700; padding-top: .7mm; }}
.meta-v {{ flex: 1; font-size: 8.6pt; color: #e2e8f0; line-height: 1.5; }}
/* dark text was invisible on the dark cover */
.cover em    {{ color: {c2}; font-style: italic; }}
.cover strong{{ color: #fff; }}
.cover a     {{ color: {c2}; text-decoration: none; }}
.cover code  {{ background: rgba(255,255,255,.1); color: {c2}; padding: 0 1mm;
                border-radius: 1mm; }}
/* guard: a callout accidentally left in the header block stays legible */
.cover .callout {{ color: #1e293b; background: #fff; }}
.cover .callout strong, .cover .callout em {{ color: #1e293b; }}

.chips-head {{ font-size: 7.6pt; letter-spacing: .28em; text-transform: uppercase;
               color: {c2}; font-weight: 700; margin-bottom: 4mm; }}
.chips {{ column-count: 2; column-gap: 6mm; }}
.chip {{ break-inside: avoid; display: flex; align-items: baseline; gap: 2.2mm;
         padding: 1.15mm 2.5mm; margin-bottom: 1.1mm; border-radius: 1.6mm;
         background: rgba(255,255,255,.045);
         border-left: 2.2px solid var(--accent); }}
.chip-num  {{ flex: 0 0 5mm; font-size: 7.4pt; font-weight: 800; color: var(--accent); }}
.chip-emoji{{ font-size: 7.6pt; }}
.chip-text {{ font-size: 7.6pt; color: #cbd5e1; line-height: 1.32; }}
.chip-text code {{ font-size: 7pt; background: rgba(255,255,255,.1); color: {c2};
                   border: none; padding: 0 .6mm; }}

/* ── body ──────────────────────────────────────────────────────────── */
.body {{ padding-top: 2mm; }}
h2 {{ font-size: 15pt; font-weight: 800; color: #0f172a; margin: 11mm 0 4mm 0;
      padding: 0 0 2.4mm 0; letter-spacing: -.01em;
      border-bottom: 2.5px solid var(--accent); break-after: avoid; }}
.h2-badge {{ display: inline-block; min-width: 7.5mm; margin-right: 2.4mm;
             padding: .4mm 1.6mm; border-radius: 1.6mm; text-align: center;
             background: var(--accent); color: #fff; font-size: 9.5pt; font-weight: 800; }}
.h2-emoji {{ margin-right: 1.8mm; }}
h2 code {{ font-size: 12pt; background: #f1f5f9; color: #0f172a; border-color: #cbd5e1;
           font-weight: 700; }}
h3 {{ font-size: 10.8pt; font-weight: 700; color: #1e293b; margin: 6mm 0 2mm 0;
      break-after: avoid; }}
h4 {{ font-size: 9.6pt; font-weight: 700; color: #334155; margin: 4.5mm 0 1.5mm 0;
      break-after: avoid; }}
p  {{ margin: 0 0 2.6mm 0; }}
hr {{ border: none; border-top: 1px solid #e2e8f0; margin: 7mm 0; }}
a  {{ color: {c1}; text-decoration: none; border-bottom: .6px solid #cbd5e1; }}
strong {{ color: #0f172a; font-weight: 700; }}
ul, ol {{ margin: 0 0 2.8mm 0; padding-left: 5.5mm; }}
li {{ margin-bottom: 1.1mm; }}
li.tick {{ list-style: none; position: relative; }}
li.tick::before {{ content: "☐"; position: absolute; left: -5mm; color: #94a3b8; }}
li.tick.done::before {{ content: "☑"; color: #22c55e; }}

code {{ font-family: "SF Mono", Menlo, monospace; font-size: 8.1pt;
        font-variant-ligatures: none; font-feature-settings: "liga" 0, "calt" 0;
        background: #f1f5f9; color: #be185d; padding: .3mm 1.1mm;
        border-radius: 1mm; border: .5px solid #e2e8f0; }}

/* ── terminal code blocks ──────────────────────────────────────────── */
.codehilite, pre {{ background: #282a36; border-radius: 2.4mm; padding: 6mm 4mm 3.4mm 4mm;
                    margin: 0 0 3.4mm 0; position: relative; break-inside: avoid;
                    border: 1px solid #1a1b22; }}
.codehilite::before, pre::before {{
  content: ""; position: absolute; top: 2.3mm; left: 3.4mm;
  width: 8.2mm; height: 1.9mm;
  background-image:
    radial-gradient(circle .95mm at .95mm .95mm, #ff5f56 99%, transparent 100%),
    radial-gradient(circle .95mm at 4.1mm .95mm, #ffbd2e 99%, transparent 100%),
    radial-gradient(circle .95mm at 7.25mm .95mm, #27c93f 99%, transparent 100%); }}
.codehilite pre {{ background: none; border: none; padding: 0; margin: 0; }}
img {{ max-width: 100%; height: auto; }}
.codehilite pre::before {{ display: none; }}
pre, .codehilite code {{ font-family: "SF Mono", Menlo, monospace; font-size: 7.6pt;
                         font-variant-ligatures: none;
                         font-feature-settings: "liga" 0, "calt" 0;
                         line-height: 1.5; color: #f8f8f2; background: none;
                         border: none; padding: 0; white-space: pre-wrap;
                         word-break: break-word; }}

/* ── tables ────────────────────────────────────────────────────────── */
table {{ width: 100%; border-collapse: collapse; margin: 0 0 3.4mm 0; font-size: 8.3pt;
         break-inside: avoid; }}
thead th {{ background: {c1}; color: #fff; text-align: left; font-weight: 700;
            padding: 1.9mm 2.4mm; font-size: 8pt; }}
thead th:first-child {{ border-top-left-radius: 1.6mm; }}
thead th:last-child  {{ border-top-right-radius: 1.6mm; }}
tbody td {{ padding: 1.7mm 2.4mm; border-bottom: .6px solid #e2e8f0; vertical-align: top; }}
tbody tr:nth-child(even) {{ background: #f8fafc; }}
table.nohead tbody tr:first-child {{ border-top: 2px solid {c1}; }}
table code {{ font-size: 7.5pt; }}

/* ── callout cards ─────────────────────────────────────────────────── */
blockquote.callout {{ margin: 0 0 3.6mm 0; padding: 3.4mm 4mm 2.2mm 4mm;
                      border-radius: 2.4mm; border-left: 3px solid var(--cc);
                      background: var(--cbg); orphans: 3; widows: 3; }}
/* short cards stay whole; only genuinely long ones (labs) may split */
blockquote.callout.c-quote, blockquote.callout.c-lock,
blockquote.callout.c-target, blockquote.callout.c-note,
blockquote.callout.c-fun {{ break-inside: avoid; }}
.callout-head {{ margin-bottom: 1.8mm; }}
.callout-chip {{ display: inline-block; padding: .55mm 2.2mm; border-radius: 4mm;
                 background: var(--cc); color: #fff; font-size: 6.7pt; font-weight: 800;
                 letter-spacing: .1em; text-transform: uppercase; }}
.callout p:last-child {{ margin-bottom: 1mm; }}
.callout table {{ margin-bottom: 2mm; }}
.callout thead th {{ background: var(--cc); }}
.callout blockquote.callout {{ margin-top: 2.4mm; }}

.c-brain  {{ --cc:#8b5cf6; --cbg:#f5f3ff; }}
.c-bulb   {{ --cc:#f59e0b; --cbg:#fffbeb; }}
.c-warn   {{ --cc:#ef4444; --cbg:#fef2f2; }}
.c-lock   {{ --cc:#22c55e; --cbg:#f0fdf4; }}
.c-target {{ --cc:#ec4899; --cbg:#fdf2f8; }}
.c-quote  {{ --cc:#64748b; --cbg:#f8fafc; }}
.c-clar   {{ --cc:#14b8a6; --cbg:#f0fdfa; }}
.c-fun    {{ --cc:#3b82f6; --cbg:#eff6ff; }}
.c-hard   {{ --cc:#f97316; --cbg:#fff7ed; }}
.c-note   {{ --cc:#3b82f6; --cbg:#eff6ff; }}
.c-try    {{ --cc:#0d9488; --cbg:#f0fdfa; }}
.c-film   {{ --cc:#6366f1; --cbg:#eef2ff; }}
.c-lab    {{ --cc:#0d9488; --cbg:#ecfeff; }}
.c-mech   {{ --cc:#a855f7; --cbg:#faf5ff; }}
.c-hw     {{ --cc:#475569; --cbg:#f1f5f9; }}
.c-plain  {{ --cc:#cbd5e1; --cbg:#f8fafc; }}
"""


def pygments_css():
    from pygments.formatters import HtmlFormatter
    return HtmlFormatter(style="dracula").get_style_defs(".codehilite")


# ──────────────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) != 3:
        sys.exit("usage: notes_to_pdf.py <notes.md> <notes.pdf>")
    src, dst = sys.argv[1], sys.argv[2]
    text = open(src, encoding="utf-8").read()

    m = re.search(r"Class-(\d+)", os.path.abspath(src))
    class_no = int(m.group(1)) if m else 0
    theme = THEMES.get(class_no, FALLBACK_THEME)

    front, body_md = split_front_matter(text)
    sections = collect_sections(body_md)

    stripped, blocks = extract_blockquotes(body_md)
    body_html = make_md().convert(stripped)
    body_html = restore_blockquotes(body_html, blocks)
    body_html = decorate_headings(body_html, sections)
    body_html = strip_empty_theads(body_html)
    body_html = tick_lists(body_html)

    footer = f"DevOps & Cloud [SWE] · Class {class_no}"
    doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
<style>{pygments_css()}</style><style>{build_css(theme, footer)}</style></head>
<body>{build_cover(front, sections, theme)}<div class="body">{body_html}</div></body></html>"""

    HTML(string=doc, base_url=os.path.dirname(os.path.abspath(src)) or ".").write_pdf(dst)
    print(f"✓ {dst}  ({theme[0]} theme, {len(sections)} sections, {len(blocks)} callouts)")


if __name__ == "__main__":
    main()
