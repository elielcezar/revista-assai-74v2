#!/usr/bin/env python
"""Mede a posicao real dos elementos da CAPA contra as coordenadas do Figma.

    python scripts/probe_capa.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

# os tops abaixo do banner (LINHA 2 em diante) levam +235px: altura do
# banner da capa (226) mais a margem de 9
EXPECT = [
    ("header.head",              0, 0),
    (".head-logo",              54, 78),

    (".hero",                     0, 179),
    (".hero .card-tag",          24, 531),
    (".hero-title",              23, 556),

    (".grid--2:nth-of-type(1) .card:nth-child(1)",        -6, 648),
    (".grid--2:nth-of-type(1) .card:nth-child(1) .card-tag",   23, 664.16),
    (".grid--2:nth-of-type(1) .card:nth-child(1) .card-title", 23, 691.14),
    (".grid--2:nth-of-type(1) .card:nth-child(2)",       207, 648),
    (".grid--2:nth-of-type(1) .card:nth-child(2) .card-tag",  217.4, 778),
    (".grid--2:nth-of-type(1) .card:nth-child(2) .card-title", 217, 805),

    (".grid--2:nth-of-type(2) .card:nth-child(1)",        -1, 1124),
    (".grid--2:nth-of-type(2) .card:nth-child(1) .card-tag",   23, 1270),
    (".grid--2:nth-of-type(2) .card:nth-child(1) .card-title", 23, 1297),
    (".grid--2:nth-of-type(2) .card:nth-child(2)",       206, 1124),
    (".grid--2:nth-of-type(2) .card:nth-child(2) .card-tag",  217, 1254),
    (".grid--2:nth-of-type(2) .card:nth-child(2) .card-title", 217, 1281),

    (".card--mkt",        -3, 1365),
    (".card--mkt .card-title", 233, 1437.92),
    (".card--mkt .card-tag",  232.86, 1494.95),

    (".card--consumidor",         -12, 1607),
    (".card--consumidor .card-tag", 270, 1647),
    (".card--consumidor .card-title", 270, 1674),

    (".card--inset",               -13, 1841),
    (".card--inset .card-tag",      24, 1999),
    (".card--inset .card-title",    26, 2026),

    (".grid--2:nth-of-type(3) .card:nth-child(1)",        -2, 2083),
    (".grid--2:nth-of-type(3) .card:nth-child(1) .card-tag",   24, 2224.05),
    (".grid--2:nth-of-type(3) .card:nth-child(1) .card-title", 24, 2252.05),
    (".grid--2:nth-of-type(3) .card:nth-child(2)",       206, 2083),
    (".grid--2:nth-of-type(3) .card:nth-child(2) .card-tag",  219, 2208),
    (".grid--2:nth-of-type(3) .card:nth-child(2) .card-title", 219, 2235),
]


def main():
    url = pathlib.Path("index.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 2162 + banner 235)\n")
        print(f"{'selector':<58}{'left':>18}{'top':>20}   w x h")
        print("-" * 120)
        bad = 0
        for sel, ex_l, ex_t in EXPECT:
            box = pg.evaluate(
                """(s) => { const e = document.querySelector(s); if (!e) return null;
                    const r = e.getBoundingClientRect();
                    return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}; }""", sel)
            if box is None:
                print(f"{sel:<58}  *** NAO ENCONTRADO ***"); bad += 1; continue
            gl = round(box["x"], 1); gt = round(box["y"], 1)
            off = abs(gl - ex_l) > 2 or abs(gt - ex_t) > 2
            if off: bad += 1
            print(f"{sel:<58}{f'{gl:g} (esp {ex_l}, {gl-ex_l:+.0f})':>18}"
                  f"{f'{gt:g} (esp {ex_t}, {gt-ex_t:+.0f})':>20}   {box['w']:.0f}x{box['h']:.0f}{'  <<<' if off else ''}")
        print("-" * 120)
        print(f"fora de posicao: {bad}/{len(EXPECT)}")
        b.close()


if __name__ == "__main__":
    main()
