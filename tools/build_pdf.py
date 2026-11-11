#!/usr/bin/env python3
"""Builds one PDF from story.md, the shot list data and assets.md.

Usage: python3 tools/build_pdf.py OUT.pdf [FONTS_DIR]

Needs the `markdown` Python package and Node with Playwright (Chromium).
FONTS_DIR may hold Inter and Noto Naskh Arabic .woff2 files (fontsource
names); without it the system fonts are used.
"""
import html
import os
import re
import subprocess
import sys
import tempfile

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from build_shotlist import SCENES  # noqa: E402

DRAFT = "Draft 1 · 11 November 2026"


def tc(s):
    return f"{s // 60}:{s % 60:02d}"


def md_file(name, drop_h1=True):
    text = open(os.path.join(ROOT, name), encoding="utf-8").read()
    if drop_h1:
        text = re.sub(r"\A# .*\n", "", text)
    # a list straight after a paragraph line needs a blank line before it
    text = re.sub(r"(?m)^(?!\s*[-*] )(\S.*)\n(?=- )", r"\1\n\n", text)
    return markdown.markdown(text, extensions=["tables", "sane_lists"])


def esc(s):
    return html.escape(s, quote=False)


def sound_html(s):
    s = esc(s)
    return re.sub(
        r"([A-Z]{3,}(?: \([^)]*\))?): (\"[^\"]*\")",
        r'<span class="who">\1</span> <span class="line">\2</span>',
        s,
    )


def shot_list_html():
    out = []
    n = 0
    t = 0
    total = sum(d for _, _, shots in SCENES for d, *_ in shots)
    count = sum(len(shots) for _, _, shots in SCENES)
    hero = sum(1 for _, _, shots in SCENES for s in shots if s[1] == "H")
    cut = [s for _, _, shots in SCENES for s in shots if s[1] == "C"]
    out.append('<section class="shots">')
    out.append("<h1>Shot list</h1>")
    out.append(
        f'<p class="lede">{count} shots · running time {tc(total)} · limit 7:00, '
        f"so {420 - total} seconds of margin.</p>"
    )
    out.append(
        '<div class="legend">'
        f'<span><i class="sw hero"></i><em><b>★ Hero shot</b> ({hero}). Generate these first and spend the retries here.</em></span>'
        f'<span><i class="sw cut"></i><em><b>○ Cuttable</b> ({len(cut)} shots, {sum(s[0] for s in cut)}s). Drop these first if time runs short.</em></span>'
        '<span><i class="sw present"></i><em><b>Present</b>: 4:3 frame, locked camera, closed curtains, cool. Yellow is the only strong colour.</em></span>'
        '<span><i class="sw memory"></i><em><b>Memory</b>: full-width frame, handheld, golden hour, warm.</em></span>'
        "</div>"
    )
    for title, intent, shots in SCENES:
        start = t
        rows = []
        for dur, pri, look, size, pic, cam, snd in shots:
            n += 1
            cls = {"P": "present", "F": "memory", "-": "graphic"}[look]
            if pri == "H":
                cls += " hero"
            if pri == "C":
                cls += " cut"
            mark = {"H": "★", "C": "○", "": ""}[pri]
            rows.append(
                f'<tr class="{cls}">'
                f'<td class="num">{n:02d}<span class="mark">{mark}</span></td>'
                f'<td class="time">{tc(t)}</td>'
                f'<td class="dur">{dur}s</td>'
                f'<td class="size">{esc(size)}</td>'
                f'<td class="pic">{esc(pic)}</td>'
                f'<td class="cam">{esc(cam)}</td>'
                f'<td class="snd">{sound_html(snd)}</td>'
                "</tr>"
            )
            t += dur
        out.append('<div class="scene">')
        out.append(
            f'<h2><span>{esc(title)}</span><span class="span">{tc(start)} – {tc(t)} · {t - start}s · '
            f'{len(shots)} shot{"s" if len(shots) != 1 else ""}</span></h2>'
        )
        if intent:
            out.append(f'<p class="intent">{esc(intent)}</p>')
        out.append(
            "<table><thead><tr><th>#</th><th>In</th><th>Dur</th><th>Shot</th>"
            "<th>Picture</th><th>Camera</th><th>Sound &amp; dialogue</th></tr></thead><tbody>"
            + "".join(rows)
            + "</tbody></table></div>"
        )
    out.append("</section>")
    return "\n".join(out), count, total


def font_css(fonts_dir):
    if not fonts_dir:
        return ""
    faces = []
    for w in (400, 500, 600, 700):
        for style in ("normal", "italic"):
            p = os.path.join(fonts_dir, f"inter-latin-{w}-{style}.woff2")
            if os.path.exists(p):
                faces.append(
                    f"@font-face{{font-family:'Inter';font-weight:{w};font-style:{style};src:url('file://{p}') format('woff2');}}"
                )
    for w in (400, 700):
        p = os.path.join(fonts_dir, f"noto-naskh-arabic-arabic-{w}-normal.woff2")
        if os.path.exists(p):
            faces.append(
                f"@font-face{{font-family:'Noto Naskh Arabic';font-weight:{w};src:url('file://{p}') format('woff2');unicode-range:U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF;}}"
            )
    return "\n".join(faces)


CSS = """
:root{
  --ink:#1c1b19; --muted:#6b675f; --rule:#d9d5cc; --paper:#ffffff;
  --yellow:#e2a400; --yellow-soft:#fdf4d7; --burgundy:#7a2233;
  --memory:#fbf1e2; --present:#ffffff; --graphic:#f1f0ec;
}
@page{ size:A4 portrait; margin:16mm 16mm 16mm 16mm; }
@page wide{ size:A4 landscape; margin:12mm 11mm 13mm 11mm; }
*{ box-sizing:border-box; }
html{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body{ margin:0; background:var(--paper); color:var(--ink);
  font-family:'Inter','Noto Naskh Arabic','Liberation Sans','DejaVu Sans',sans-serif;
  font-size:10pt; line-height:1.5; }
h1,h2,h3{ line-height:1.2; margin:0; }
p{ margin:0 0 7pt; }

/* cover */
.cover{ height:262mm; display:flex; flex-direction:column; justify-content:space-between;
  break-after:page; }
.cover .kicker{ font-size:9pt; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); }
.cover .title{ font-size:84pt; font-weight:700; letter-spacing:-.02em; line-height:1; margin:0; }
.cover .ar{ font-family:'Noto Naskh Arabic','DejaVu Sans',sans-serif; font-size:54pt; font-weight:700;
  color:var(--yellow); line-height:1; }
.cover .titles{ display:flex; align-items:center; gap:10mm; }
.cover .logline{ font-size:14pt; line-height:1.45; max-width:150mm; margin-top:12mm; }
.cover .stats{ display:flex; gap:10mm; border-top:1.5pt solid var(--ink); padding-top:5mm; }
.cover .stats div{ font-size:9pt; color:var(--muted); }
.cover .stats b{ display:block; font-size:17pt; color:var(--ink); font-weight:600; }
.cover .bar{ width:26mm; height:3mm; background:var(--yellow); margin-bottom:9mm; }

/* prose sections */
.doc{ break-after:page; }
.doc h1{ font-size:24pt; font-weight:700; margin-bottom:8mm; padding-bottom:3mm;
  border-bottom:1.5pt solid var(--ink); }
.doc h2{ font-size:13pt; font-weight:700; margin:9mm 0 3mm; break-after:avoid; }
.doc h2::before{ content:''; display:inline-block; width:3mm; height:3mm; background:var(--yellow);
  margin-right:2.5mm; }
.doc h3{ font-size:10.5pt; margin:5mm 0 2mm; break-after:avoid; }
.doc ul,.doc ol{ margin:0 0 7pt; padding-left:5mm; }
.doc li{ margin-bottom:3pt; }
.doc blockquote{ margin:0 0 7pt; padding:1mm 0 1mm 4mm; border-left:2pt solid var(--yellow); }
.doc table{ width:100%; border-collapse:collapse; margin:3mm 0 5mm; font-size:9pt; line-height:1.4; }
.doc th{ text-align:left; font-size:7.5pt; letter-spacing:.08em; text-transform:uppercase;
  color:var(--muted); font-weight:600; border-bottom:1pt solid var(--ink); padding:1.5mm 2mm; }
.doc td{ border-bottom:.5pt solid var(--rule); padding:1.8mm 2mm; vertical-align:top; }
.doc tr{ break-inside:avoid; }
.doc code{ font-family:'Liberation Mono','DejaVu Sans Mono',monospace; font-size:8.5pt; }

/* shot list */
.shots{ page:wide; break-after:page; font-size:8.2pt; line-height:1.38; }
.shots h1{ font-size:24pt; font-weight:700; margin-bottom:2mm; }
.shots .lede{ font-size:10pt; color:var(--muted); margin-bottom:4mm; }
.legend{ display:grid; grid-template-columns:1fr 1fr; gap:1.5mm 8mm; font-size:8.2pt;
  border-top:1.5pt solid var(--ink); border-bottom:.5pt solid var(--rule); padding:3mm 0; margin-bottom:5mm; }
.legend span{ display:flex; align-items:baseline; gap:2mm; }
.legend em{ font-style:normal; }
.legend b{ white-space:nowrap; }
.sw{ flex:none; display:inline-block; width:3.2mm; height:3.2mm; border:.5pt solid var(--rule);
  transform:translateY(.5mm); }
.sw.hero{ background:var(--yellow); border-color:var(--yellow); }
.sw.cut{ background:#fff; border:.8pt dashed var(--muted); }
.sw.present{ background:var(--present); }
.sw.memory{ background:var(--memory); border-color:#ecd9b8; }
.scene{ margin-bottom:6mm; }
.scene h2{ display:flex; justify-content:space-between; align-items:baseline; font-size:11.5pt;
  font-weight:700; border-bottom:1.2pt solid var(--ink); padding-bottom:1.2mm; break-after:avoid; }
.scene h2 .span{ font-size:8pt; font-weight:500; color:var(--muted); }
.scene .intent{ font-style:italic; color:var(--muted); margin:1.5mm 0 1.5mm; break-after:avoid; }
.shots table{ width:100%; border-collapse:collapse; table-layout:fixed; }
.shots thead{ display:table-header-group; }
.shots th{ text-align:left; font-size:6.8pt; letter-spacing:.08em; text-transform:uppercase;
  color:var(--muted); font-weight:600; padding:1.2mm 1.6mm; border-bottom:.5pt solid var(--rule); }
.shots td{ padding:1.6mm 1.6mm; vertical-align:top; border-bottom:.5pt solid var(--rule);
  overflow-wrap:break-word; }
.shots tr{ break-inside:avoid; }
.shots th:nth-child(1){ width:13mm; } .shots th:nth-child(2){ width:10mm; }
.shots th:nth-child(3){ width:9mm; }  .shots th:nth-child(4){ width:31mm; }
.shots th:nth-child(5){ width:98mm; } .shots th:nth-child(6){ width:44mm; }
tr.memory td{ background:var(--memory); }
tr.graphic td{ background:var(--graphic); }
td.num{ font-weight:700; font-variant-numeric:tabular-nums; border-left:2.2pt solid transparent; white-space:nowrap; }
tr.hero td.num{ border-left-color:var(--yellow); }
tr.cut td.num{ border-left:1.2pt dashed var(--muted); }
td.num .mark{ margin-left:1mm; color:var(--yellow); font-family:'DejaVu Sans',sans-serif; }
tr.cut td.num .mark{ color:var(--muted); }
td.time,td.dur{ font-variant-numeric:tabular-nums; color:var(--muted); white-space:nowrap; }
td.size{ font-weight:600; }
td.cam{ color:#4a4741; }
.who{ font-weight:700; font-size:7.2pt; letter-spacing:.05em; color:var(--burgundy); }
.line{ font-weight:600; }
.doc:last-child,.shots:last-child{ break-after:auto; }
"""


def build(out_pdf, fonts_dir):
    shots, count, total = shot_list_html()
    story = md_file("story.md")
    assets = md_file("assets.md")
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>LOOK — Story and Shot List</title>
<style>{font_css(fonts_dir)}{CSS}</style></head><body>
<section class="cover">
  <div>
    <div class="bar"></div>
    <div class="kicker">Short film · 1 Billion Followers Summit AI Film Award 2027</div>
  </div>
  <div>
    <div class="titles">
      <h1 class="title">LOOK</h1>
      <div class="ar" dir="rtl" lang="ar">بُصّ</div>
    </div>
    <p class="logline">Four months after the crash that killed his wife and daughter, a man keeps them alive at home as two mannequins, until the memory he has been refusing returns one fragment at a time, and he finally looks at the last thing his daughter wanted to show him.</p>
  </div>
  <div>
    <div class="stats">
      <div><b>{tc(total)}</b>running time</div>
      <div><b>{count}</b>shots</div>
      <div><b>4 + 2</b>people + mannequins</div>
      <div><b>Story · Shot list · Assets</b>{DRAFT}</div>
    </div>
  </div>
</section>
<section class="doc"><h1>Story</h1>{story}</section>
{shots}
<section class="doc"><h1>Characters, locations &amp; props</h1>{assets}</section>
</body></html>"""
    tmp = tempfile.mkdtemp(prefix="lookpdf_")
    html_path = os.path.join(tmp, "look.html")
    open(html_path, "w", encoding="utf-8").write(doc)
    js = """
const { chromium } = require('playwright');
(async () => {
  const [htmlPath, outPath] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + htmlPath);
  await page.evaluate(() => document.fonts.ready);
  const footer = '<div style="width:100%;font-family:Liberation Sans,sans-serif;font-size:7px;color:#8a867d;padding:0 11mm;display:flex;justify-content:space-between;"><span>LOOK · %DRAFT%</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>';
  await page.pdf({ path: outPath, preferCSSPageSize: true, printBackground: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: footer });
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
""".replace("%DRAFT%", DRAFT)
    js_path = os.path.join(tmp, "print.js")
    open(js_path, "w").write(js)
    subprocess.run(["node", js_path, html_path, os.path.abspath(out_pdf)], check=True, cwd=tmp)
    print(f"wrote {out_pdf} ({count} shots, {tc(total)})")


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
