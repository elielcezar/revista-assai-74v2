#!/usr/bin/env python
"""Mede a posicao real dos elementos da ACADEMIA contra as coordenadas do Figma.

    python scripts/probe_academia.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

EXPECT = [
    ("header.head",              0,    0),
    (".head-logo",              54,   78),

    (".bl-hero",                  0,  182),
    (".hero-title-a",            19,  227.5),
    (".hero-title-b",            19,  280.5),
    (".hero-lead",               21,  434),
    (".badge74",             137.5,  590),
    (".hero-foto",               -4,  660),

    (".bl-minuto",                0, 1093),
    (".t-minuto",                22, 1160),
    (".quote-minuto",            49, 1622),

    (".h-caminho",               24, 1977),
    (".t-caminho",               24, 2054),
    (".gallery",                  7, 2378),

    (".t-para-chegar",           20, 2812),
    (".h-20-negocios",           20, 3135),
    (".mapa-badges",             15, 3245),

    (".btn-pill",                 20, 3642),
    (".h-votacao",                24, 3777),
    (".t-votacao",                24, 3827),

    (".h-voce",                   24, 4556),
    (".t-voce",                   24, 4606),

    (".h-premio",                 24, 5654),
    (".t-premio",                 24, 5731),
    (".logo-premio",             129, 6402),

    ("footer.foot",                0, 6474),
]


def main():
    url = pathlib.Path("74/academia.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 6590)\n")
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
