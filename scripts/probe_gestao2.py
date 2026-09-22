#!/usr/bin/env python
"""Mede a posicao real dos elementos da GESTAO 02 contra as coordenadas do Figma.

    python scripts/probe_gestao2.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

# selector -> (left, top) absolutos na pagina, do metadata do Figma
EXPECT = [
    ("header.head",              0,    0),
    (".head-logo",              54,   78),
    (".art",                     0,  182),

    (".h1-kicker",              39,  243),
    (".h1-main",                39,  280),
    (".hero-foto img",        -125,  379),
    (".hero-lead",              20,  753),
    (".hero-meta",             128,  866),
    (".t-intro",                20, 1004),

    (".pratos-a",              -41, 1753),
    (".pratos-b",              207, 1753),

    (".h-fidelizacao",          22, 2063),
    (".t-fidelizacao",          22, 2135),
    (".q-marcos",               19, 2761),

    (".h-funciona",             67, 3314),
    (".t-funciona",             24, 3419),

    (".h-metas",                22, 3875),
    (".t-metas",                24, 3926),

    (".h-numero",               78, 4659),
    (".t-numero",               24, 4719),

    (".h-fora",                 34, 4970),
    (".fora-cards",              0, 5071),
    (".fc--ultimo",              0, 5617),

    (".perguntas-foto img",    -24, 5775),
    (".h-perguntas",            48, 6116),
    (".carousel",               20, 6252),
    (".carousel-nav--prev",     35, 6364),
    (".carousel-nav--next",    375, 6364),

    (".h-alerta",               29, 6659),
    (".t-alerta",               29, 6709),
    (".faixa--verde",           42, 7019),
    (".faixa--vermelha",        41, 7180),
    (".t-fecho",                23, 7359),

    ("footer.foot",              0, 7515),
    (".foot-bar",                0, 7560),
]


def main():
    url = pathlib.Path("74/gestao2.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick|scroll-fx\.js"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 7631)\n")
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
