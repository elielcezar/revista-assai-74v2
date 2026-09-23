#!/usr/bin/env python
"""Mede a posicao real dos elementos da CONSUMIDOR contra as coordenadas do Figma.

    python scripts/probe_consumidor.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

# selector -> (left, top) absolutos na pagina, do metadata da API REST do Figma
# do banner rotativo em diante, os tops levam +475 (419 da imagem + 56 de margem):
# texto e decoracoes da .art-bg foram deslocados juntos
EXPECT = [
    ("header.head",              0, 0),
    (".head-logo",              54, 78),
    (".art",                     0, 182),

    ("h1",                      18, 224),
    (".hero-lead",              17, 441),
    (".hero-foto img",           7, 578),
    (".hero-meta",              125, 974),

    (".t-pesquisa",             22, 1124),

    (".h-experimento",          22, 2023),
    (".lista-experimento",      15, 2112),
    (".t-demonstrou",           22, 2361),

    (".t-maastricht",           22, 2622),
    (".h-conclusao",            20, 3332),
    (".t-conclusao",            20, 3411),

    (".h-sinais",               22, 4423),
    (".t-sinais",               22, 4573),

    (".h-nome",                 29, 4993),
    (".t-nome",                 22, 5051),

    (".h-foto",                 29, 5643),
    (".t-foto",                 22, 5700),

    (".h-embalagem",            29, 6243),
    (".t-embalagem",            22, 6301),

    (".h-teste",                26, 7025),
    (".teste-texto",            20, 7084),

    ("footer.foot",              0, 7631),
    (".foot-bar",                0, 7676),
]


def main():
    url = pathlib.Path("74/consumidor.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick|scroll-fx.js"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 7272 + banner 475)\n")
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
