#!/usr/bin/env python
"""Mede a posicao real dos elementos da EXPEDIENTE contra o render da #73.

    python scripts/probe_expediente.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

EXPECT = [
    ("header.head",               0,    0),
    (".head-logo",               54,   78),

    (".ex-logo-assai",          159,  218),
    (".ex-conselho h2",          24,  282),
    (".ex-redes",                 0,  500),
    (".ex-redes h2",             29,  516),
    # icones em space-between: o Figma tem vaos irregulares (60-63px), so as pontas batem
    (".ex-soc li:first-child",   24,  560),
    (".ex-soc li:last-child",   332,  560),
    (".ex-logo-mm",             141,  705),
    (".ex-megamidia h2",         20,  798),
    (".ex-revista h2",           26, 1076),
    (".ex-contato",              19, 1345),
    (".ex-contato-cap",         142, 1308),
    (".ex-contato-ico",         174, 1316),
    (".ex-contato h2",           47, 1370),
    ("footer.foot",               0, 1567),
]


def main():
    url = pathlib.Path("expediente.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }"
                                 " .ex-soc li { animation: none !important; opacity: 1 !important; transform: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (#73 1683)\n")
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
