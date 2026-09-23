#!/usr/bin/env python
"""Mede a posicao real dos elementos da PRODUTO contra as coordenadas do Figma.

    python scripts/probe_produto.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

# selector -> (left, top) absolutos na pagina, do metadata da API REST do Figma
# banner rotativo antes do titulo do bloco 'trabalho' (419 da imagem + margens):
#  +520 no que vem depois dele dentro do bloco
#  +470 nos blocos seguintes (o bloco do trabalho absorve 50px no min-height)
# margin-bottom de 60px no .bl-trabalho (pedido fora do Figma): +60 do .bl-alcance para baixo
EXPECT = [
    ("header.head",              0, 0),
    (".head-logo",              54, 78),
    (".bl-hero",                 0, 182),

    (".hero-fatias",          -114, 224),
    (".hero-badge",             23, 566),
    (".hero-title .laranja",    20, 643),
    (".hero-title .vermelho",   21, 700),
    (".hero-lead",              23, 786),
    (".t-hero",                 23, 888),

    (".bl-perguntas",            0, 1262),
    (".h-curiosidade",          20, 1283),
    (".t-curiosidade",          20, 1342),
    (".foto-ingredientes",    90.5, 1806),
    (".h-pergunte",           21.5, 1995),
    (".perguntas",              20, 2073),

    (".bl-caso",                 0, 2436),
    (".caso-foto",              32, 2465),
    (".h-caso",                 22, 2834),
    (".t-caso",                 22, 2893),

    (".bl-trabalho",             0, 3409),
    (".trabalho-foto",         -65, 3409),
    (".trabalho-detalhe",    122.7, 3836),
    (".h-trabalho",             22, 4537),
    (".t-trabalho",             22, 4623),

    (".bl-alcance",              0, 5163),
    (".alcance-foto",        -4.5, 5163),
    (".alcance-faixa",           0, 5462),
    (".estatisticas",           20, 5586),

    (".bl-fecho",                0, 6176),
    (".h-continuidade",         20, 6176),
    (".t-continuidade",         20, 6262),
    (".foto-final",         -129.5, 6618),
    (".h-reputacao",            21, 6929),
    (".t-reputacao",            21, 7015),

    ("footer.foot",              0, 7275),
]


def main():
    url = pathlib.Path("74/produto.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick|scroll-fx.js"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 6861 + banner 470 + margem 60)\n")
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
