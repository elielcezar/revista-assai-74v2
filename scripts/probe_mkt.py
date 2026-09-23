#!/usr/bin/env python
"""Mede a posicao real dos elementos da MKT DIGITAL contra as coordenadas do Figma.

    python scripts/probe_mkt.py
"""
import pathlib
import re
from playwright.sync_api import sync_playwright

# a partir do banner rotativo, os tops levam +438 (384 da imagem + margens, ja descontado o colapso de 2px):
# o texto e as decoracoes da .art-bg foram deslocados juntos
#
# o .hero-lead teve a margem de cima reduzida de 42 para 20px (ajuste de design)
# e os mesmos 22px voltaram na margem de baixo: so ele subiu, e o texto daqui
# para baixo ficou onde estava, alinhado com as decoracoes da .art-bg.
#
# hero: o .hero-title2 ("mas aprenda com ela") fica FORA DO FLUXO (absolute), por
# cima do .hero-title — os dois se revezam no efeito typewriter. Se ele voltasse
# ao fluxo, o texto daqui para baixo subiria 28px e as decoracoes da .art-bg,
# que sao absolutas, ficariam onde estao. As esperas do .hero-lead ate o
# .t-caso2 tinham sido anotadas com ele no fluxo (28px acima) e voltaram para o
# layout real.
EXPECT = [
    ("header.head",              0, 0),
    (".head-logo",              54, 78),

    (".s-hero",                  0, 182),
    (".d-foto1439",              -1, 540),
    (".d-hero-cutout",           10, 524),
    (".d-e116",               -173, 670),
    (".hero-title",              19, 811),
    (".hero-title2",             19, 838),
    (".hero-lead",               20, 996),

    (".badge74",                220, 1207),
    (".badge74-ed",             220, 1207),
    (".t-caso1",                 20, 1308),
    (".gallery",                 43, 1729),
    (".d-e120",               -197, 1139),
    (".d-e121",               -186, 1155),
    (".t-caso2",                 19, 2223),

    (".h-ia",                    21, 2743),
    (".d-robot",                -15, 2467),
    (".t-ia1",                   20, 2823),
    (".t-ia2",                   20, 2895),
    (".h-comecar",               16, 3099),
    (".t-comecar",               19, 3152),

    (".t-food-def",              20, 3717),
    (".food-badge-txt",         112, 3635),
    (".d-e122b",                48, 3555),
    (".d-basil",               110, 3544),
    (".d-tomato",              191, 3555),
    (".t-food",                  20, 3832),
    (".t-quote",                 20, 4221),

    (".passo-badge-txt",        103, 5043),
    (".d-e124",                 48, 4981),
    # a rotacao do celular passou para um <span> interno (o orbit-in anima a caixa):
    # a caixa medida agora e a do elemento sem giro; o visual nao mudou
    (".d-phone",             136.5, 4870),
    (".t-melhor-foto",           20, 5151),
    (".steps",                   33, 5217),
    (".t-agora",                 20, 5732),

    (".t-voce-deve",             20, 6210),
    (".tools",                    0, 6337),
    (".d-e125",               -275, 6298.5),
    (".d-chat-photo",             0, 5861),
    (".tool--claude .tool-logo", 87, 6622),

    (".t-copie",                 20, 6826),
    (".t-prompt",                20, 7009),
    (".t-segundos",              20, 7497),
    (".t-continua",              19, 7635),

    (".dica-badge-txt",         136, 8158),
    (".d-e126",                 48, 8097),
    (".d-choc",                130, 8028),
    (".t-dica",                  20, 8285),
    (".t-final",                 20, 8608),

    ("footer.foot",               0, 8757),
]


def main():
    url = pathlib.Path("74/mkt.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 402, "height": 900}, device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        pg.route(re.compile(r"googletagmanager|google-analytics|doubleclick|scroll-fx\.js"), lambda r: r.abort())
        pg.goto(url, wait_until="networkidle")
        # mede so o frame do Figma: esconde o invólucro (css/shell.css)
        pg.add_style_tag(content=".dt-sidebar { display: none !important; }")
        pg.wait_for_timeout(700)
        print(f"scrollHeight = {pg.evaluate('document.documentElement.scrollHeight')}  (figma 8435 + banner 438)\n")
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
