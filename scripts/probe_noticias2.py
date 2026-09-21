#!/usr/bin/env python
"""Mede a posicao real dos elementos da NOTICIAS 02 contra as coordenadas do Figma.

    python scripts/probe_noticias2.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

EXPECT = [
    ("header.head",              0,    0),
    (".head-logo",              54,   78),

    (".bl-hero",                  0,  182),
    (".hero-title",              19,  604),
    (".hero-sub",                19,  645),
    (".hero-lead",               19,  786),
    (".badge74",                 19,  928),

    (".bl-arroz",                 0, 1026),
    (".t-arroz",                 30, 1067),
    (".foto-arroz",              77, 1281),
    (".cifrao--1",               68, 1272),
    (".cifrao--2",              201, 1231),
    (".cifrao--3",              368, 1341),

    (".t-seguranca",             21, 1457),

    (".foto-feijao",             -2, 1983),

    (".h-comparacao",            20, 2436),
    (".t-comparacao",            20, 2513),
    (".gallery",                 -2, 2855),

    (".bl-exemplo",               0, 2943),
    (".t-exemplo",               17, 3036),

    (".h-rendimento",            20, 3288),
    (".t-rendimento",            20, 3365),

    (".h-regularidade",          20, 4094),
    (".t-regularidade",          20, 4171),

    (".h-marcas",                20, 4645),
    (".t-marcas",                20, 4722),

    (".banner-chef",              0, 5261),
    (".h-cta",                   20, 5532),
    (".btn-cta",                 20, 5626),

    ("footer.foot",               0, 5682),
]


def main():
    url = pathlib.Path("74/noticias2.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 5798)\n")
        print(f"{'selector':<24}{'left':>18}{'top':>20}   w x h")
        print("-" * 96)
        bad = 0
        for sel, ex_l, ex_t in EXPECT:
            box = pg.evaluate(
                """(s) => { const e = document.querySelector(s); if (!e) return null;
                    const r = e.getBoundingClientRect();
                    return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}; }""", sel)
            if box is None:
                print(f"{sel:<24}  *** NAO ENCONTRADO ***"); bad += 1; continue
            gl = round(box["x"], 1); gt = round(box["y"], 1)
            off = abs(gl - ex_l) > 2 or abs(gt - ex_t) > 2
            if off: bad += 1
            print(f"{sel:<24}{f'{gl:g} (esp {ex_l}, {gl-ex_l:+.0f})':>18}"
                  f"{f'{gt:g} (esp {ex_t}, {gt-ex_t:+.0f})':>20}   {box['w']:.0f}x{box['h']:.0f}{'  <<<' if off else ''}")
        print("-" * 96)
        print(f"fora de posicao: {bad}/{len(EXPECT)}")
        b.close()


if __name__ == "__main__":
    main()
