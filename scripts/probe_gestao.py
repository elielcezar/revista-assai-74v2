#!/usr/bin/env python
"""Mede a posicao real dos elementos da pagina GESTAO contra as coordenadas do Figma.

    python scripts/probe_gestao.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

# selector -> (left, top) absolutos na pagina, direto do metadata do Figma
EXPECT = [
    ("header.head",              0,    0),
    (".head-logo",              54,   78),
    (".art",                     0,  182),

    (".h1-kicker",              20,  242),
    (".h1-main",                20,  335),
    (".hero-lead",              20,  459),
    (".hero-meta",              21,  565),
    (".p-intro-1",              20,  851),
    (".p-intro-2",              21,  979),

    (".foto-gemini img",       -45, 1110),

    (".p-doce-1",               20, 1437),
    (".p-doce-2",               20, 1585),

    (".h-sache",                20, 1862),
    (".p-bianca",               21, 2192),
    (".q-sache",                95, 2328),
    (".p-multiplique",          20, 2469),

    (".conta--1",                0, 2665),
    (".conta--2",                0, 2747),
    (".conta--3",                0, 2835),

    (".p-margem",               22, 3194),
    (".q-dono",                 22, 3343),
    (".p-quando",               22, 3534),

    (".carousel",                0, 3609),

    (".h-teste",                20, 3966),
    (".t-teste",                22, 4021),

    (".casal-play",             58, 4446),
    (".casal-sound",           335, 4566),
    (".h-contabil",             22, 4844),
    (".p-contabil",             23, 4908),
    (".p-conta-a",              23, 4996),
    (".p-conta-b",              23, 5074),

    (".h-decida",               45, 5360),
    (".passo--1",               75, 5479),
    (".p-passo-1",              30, 5605),
    (".p-passo-1b",             29, 5723),
    (".passo--2",               48, 5936),
    (".p-passo-2",              30, 6081),
    (".h-entenda",              30, 6285),

    (".faixa--1",               57, 6480),
    (".faixa--2",               57, 6745),
    (".p-item",                 22, 6885),
    (".h-calculo",              22, 7064),
    (".formula",                30, 7162),
    (".t-ler",                  22, 7250),
    (".p-porcentagem",          20, 7616),

    (".cmv",                    17, 8000),

    (".t-junto",                20, 8415),
    (".p-nenhuma",              20, 8808),

    (".q-fecho",                35, 9145),

    ("footer.foot",              0, 9391),
    (".foot-bar",                0, 9436),
]


def main():
    url = pathlib.Path("74/gestao.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick|scroll-fx\.js"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)

        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 9507)\n")
        print(f"{'selector':<26}{'left':>18}{'top':>20}   w x h")
        print("-" * 100)
        bad = 0
        for sel, ex_l, ex_t in EXPECT:
            box = pg.evaluate(
                """(s) => { const e = document.querySelector(s); if (!e) return null;
                    const r = e.getBoundingClientRect();
                    return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}; }""",
                sel)
            if box is None:
                print(f"{sel:<26}  *** NAO ENCONTRADO ***"); bad += 1; continue
            gl = round(box["x"], 1); gt = round(box["y"], 1)
            off = abs(gl - ex_l) > 2 or abs(gt - ex_t) > 2
            if off: bad += 1
            sl = f"{gl:g} (esp {ex_l}, {gl-ex_l:+.0f})"
            st = f"{gt:g} (esp {ex_t}, {gt-ex_t:+.0f})"
            print(f"{sel:<26}{sl:>18}{st:>20}   {box['w']:.0f}x{box['h']:.0f}{'  <<<' if off else ''}")
        print("-" * 100)
        print(f"fora de posicao: {bad}/{len(EXPECT)}")
        b.close()


if __name__ == "__main__":
    main()
