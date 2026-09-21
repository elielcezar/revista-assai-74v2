#!/usr/bin/env python
"""Mede a posicao real dos elementos da DELIVERY contra as coordenadas do Figma.

    python scripts/probe_delivery.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

# do banner rotativo em diante, os tops levam +475 (419 da imagem + 56 de margem):
# texto e decoracoes da .art-bg foram deslocados juntos
EXPECT = [
    ("header.head",              0,    0),
    (".head-logo",              54,   78),
    (".art",                     0,  182),

    (".hero-title",             21,  253),
    (".hero-lead",              24,  413),
    (".hero-badge",             22,  685),
    (".t-hero",                 19,  825),

    (".h-porque",                25, 1198),
    (".t-porque",                25, 1255),
    (".q-porque",                25, 1501),
    (".q-porque-2",              25, 1663),

    (".h-caso",                  20, 2446),
    (".t-caso",                  20, 2495),
    (".q-juca",                  20, 2837),
    (".t-mercado",               20, 3193),

    (".q-oriento",               -7, 3323),
    (".adbox",                    0, 3738),

    (".t-conferem",              20, 4247),
    (".t-bloqueio",              20, 4736),
    (".t-repassar",              20, 5424),
    (".t-acompanhando",          27, 5546),

    (".q-pausar",                 0, 5789),
    (".h-fiscalizacao",         109, 6287),
    (".t-discussao",             23, 6410),
    (".t-senacon",               20, 6595),

    (".h-confira",               25, 7060),
    (".t-confira",               30, 7106),
    (".dicas",                    0, 7334),
    (".t-final",                 20, 7880),

    ("footer.foot",              0, 8049),
]


def main():
    url = pathlib.Path("74/delivery.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 7690 + banner 475)\n")
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
