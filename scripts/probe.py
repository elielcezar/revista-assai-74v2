#!/usr/bin/env python
"""Mede a posicao real (page-absolute) de elementos-chave e compara com o Figma.

    python scripts/probe.py
"""
import pathlib, sys
import re
from playwright.sync_api import sync_playwright

# selector -> (left, top) esperado em coordenadas absolutas da pagina (Figma)
# o carrossel de banners (405px + 28 de margem) empurra o que vem depois:
# +433 dentro da secao dos pactos, +357 nas secoes seguintes
# folga de 80px entre o texto dos pactos e o carrossel (pedido fora do Figma):
# +80 do .bl-carousel para baixo
# sem a seta da citacao (.quote-rule) e com metade do vao ate CONFIANCA (pedido
# fora do Figma): autor -36; -87 do .bl-trust para baixo
# mede o layout do CSS: o js/scroll-fx.js (animacoes) fica bloqueado
EXPECT = [
    ("header.head",            0, 0),
    (".head-logo",            54, 78),
    (".head-nav",              0, 141),

    (".bl-hero",               0, 182),
    (".h1-kicker",            18, 233),
    (".h1-main",              18,  None),
    (".hero-lead",            20, 363),
    (".hero-figure > img",   -10, 457),
    (".hero-meta",           255, 456),
    (".hero-band",             0, 903),
    (".hero-band p",          29, 939),

    (".bl-bands",              0, 1052),
    (".band--red p",          26, 1084),
    (".band--darkred",         0, 1211),
    (".band--darkred p",      26, 1259),
    (".bands-figure",       -155, 1469),

    (".bl-gen",                0, 1918),
    (".gen-title",            22, 1975),
    (".gen-icon--pencil img",117, 2073),
    (".gen-group:nth-of-type(1) .gen-pill",  -11, 2117),
    (".gen-group:nth-of-type(1) .gen-card",   20, 2175),
    (".gen-group:nth-of-type(1) .gen-list",   38, 2215),
    (".gen-icon--mouse > span", 146, 2396),
    (".gen-group:nth-of-type(2) .gen-pill",  -11, 2470),
    (".gen-group:nth-of-type(2) .gen-card",   20, 2528),
    (".gen-group:nth-of-type(2) .gen-list",   38, 2575),

    (".bl-story",              0, 2763),
    (".story-photo",         -17, 2737),
    (".story-text h2",        20, 3147),

    (".bl-quote",              0, 3886),
    (".quote-laptop",         40, 4022),
    (".quote-bread",         127, 4056),
    (".quote-marquee",        12, 4254),
    (".quote-author",         78, 4343),

    (".bl-trust",              0, 4405),
    (".trust-text h2",        20, 4412),
    (".trust-rays",          157, 5027),
    (".trust-ball",          -17, 5064),
    (".trust-cta",            84, 5170),

    (".bl-pacts",              0, 5275),
    (".pacts",               -15, 5275),
    (".pacts-text h2",        20, 6152),

    (".bl-carousel",           0, 6582),
    (".carousel",             20, 6582),
    (".carousel-nav--prev",   15, 6790),
    (".carousel-nav--next",  358, 6790),
    (".video-play",           32, 7114),
    (".video-sound",         303, 7138),
    (".video-ring",         -153, 7243),

    (".bl-closing",            0, 7452),
    (".closing-card",          0, 7442),  # sem sangria: cabe nos 402 da coluna
    (".closing-card h2",      20, 7536),  # grupo centrado em 406px
    (".closing-outro p",      24, 8041),

    ("footer.foot",            0, 8262),
    (".foot-bar",              0, 8307),
]


def main():
    url = pathlib.Path("74/principal.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick|scroll-fx\.js"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(600)

        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 8028 + banners 357)\n")
        print(f"{'selector':<42}{'left':>16}{'top':>18}   {'w x h'}")
        print("-" * 100)
        bad = 0
        for sel, ex_l, ex_t in EXPECT:
            box = pg.evaluate(
                """(s) => { const e = document.querySelector(s); if (!e) return null;
                    const r = e.getBoundingClientRect();
                    return {x: r.x + scrollX, y: r.y + scrollY, w: r.width, h: r.height}; }""",
                sel)
            if box is None:
                print(f"{sel:<42}  *** NAO ENCONTRADO ***"); bad += 1; continue
            gl = round(box["x"], 1); gt = round(box["y"], 1)
            dl = "" if ex_l is None else f"{gl - ex_l:+.0f}"
            dt = "" if ex_t is None else f"{gt - ex_t:+.0f}"
            off = (ex_l is not None and abs(gl - ex_l) > 2) or (ex_t is not None and abs(gt - ex_t) > 2)
            if off: bad += 1
            flag = "  <<<" if off else ""
            sl = f"{gl:g}" + (f" (esp {ex_l}, {dl})" if ex_l is not None else "")
            st = f"{gt:g}" + (f" (esp {ex_t}, {dt})" if ex_t is not None else "")
            print(f"{sel:<42}{sl:>16}{st:>18}   {box['w']:.0f}x{box['h']:.0f}{flag}")
        print("-" * 100)
        print(f"fora de posicao: {bad}/{len(EXPECT)}")
        b.close()


if __name__ == "__main__":
    main()
