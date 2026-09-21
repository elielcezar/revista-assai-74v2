#!/usr/bin/env python
"""Mede a posicao real dos elementos da NEGOCIO contra as coordenadas do Figma.

    python scripts/probe_negocio.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

EXPECT = [
    ("header.head",              0,    0),
    (".head-logo",              54,   78),
    (".bl-hero",                 0,  182),

    (".hero-title .azul",       18,  569),
    (".hero-title .pink",       24,  665),
    (".hero-lead",              26,  772),
    (".hero-badge",         142.5,  933),

    (".bl-historia",             0, 1034),
    (".foto-39",                -7, 1034),
    (".q-azul--1",              11, 1382),
    (".foto-40",                 0, 1475),
    (".q-azul--2",              16, 1650),
    (".rabisco-8717",            82, 1585),
    (".foto-41",               -32, 1718),
    (".callout-pudim",         201, 1925.78),
    (".q-azul--3",              19, 2066),
    (".depois-arco",        -244.4, 2530),

    (".bl-depois",                0, 2402),
    (".t-pink--0",               27, 2230),
    (".t-pink--1",               27, 2439),
    (".checklist",               47, 2567),
    (".foto-guilherme",          61, 2866),
    (".t-validar",               22, 3191),

    (".bl-erro",                  0, 3378),
    (".h-erro",                  22, 3430),
    (".t-erro",                  22, 3477),
    (".h-cinco",                 66, 3835),
    (".passos",                   0, 3934),

    (".bl-conhecimento",           0, 4297),
    (".h-conhecimento",           18, 4342),
    (".t-conhecimento",           18, 4455),
    (".q-sebrae",                 28, 4785),
    (".rabisco-sebrae",        66.42, 4773.43),
    (".fonte-sebrae",             63, 5046),

    (".bl-numeros",                0, 5128),
    (".h-numeros",                20, 5181),
    (".foto-2024",                82, 5266),
    (".ano--2024",                18.8, 5379),
    (".stats--2024",               0, 5447),
    (".foto-2026-recorte",        82, 5659),
    (".foto-2026-fundo",          82, 5767),
    (".ano--2026",                18.8, 5885),
    (".stats--2026",               0, 5956),

    (".bl-varias",                  0, 6159),
    (".h-varias",                  21, 6202),
    (".t-varias",                  21, 6315),
    (".foto-picole",               28, 6651),
    (".h-fonte",                  -23, 7075),
    (".foto-faturamento",         -16, 7143),
    (".pill--1",                  139, 7155),
    (".pill--2",                   56, 7226),
    (".pill--3",                  231, 7317),
    (".pill--4",                   99, 7417),

    (".bl-continuar",               0, 7511),
    (".h-continuar",                20, 7566),
    (".t-continuar",                20, 7625),

    ("footer.foot",                 0, 7932),
]


def main():
    url = pathlib.Path("74/negocio.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 8048)\n")
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
