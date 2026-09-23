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
# o .hero-lead teve a margem de cima reduzida de 42 para 20px (ajuste de design):
# o texto daqui para baixo subiu 22px e as esperas foram atualizadas. As
# decoracoes da .art-bg sao absolutas e continuam onde estavam.
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

    (".badge74",                220, 1185),
    (".badge74-ed",             220, 1185),
    (".t-caso1",                 20, 1286),
    (".gallery",                 43, 1707),
    (".d-e120",               -197, 1139),
    (".d-e121",               -186, 1155),
    (".t-caso2",                 19, 2201),

    (".h-ia",                    21, 2721),
    (".d-robot",                -15, 2467),
    (".t-ia1",                   20, 2801),
    (".t-ia2",                   20, 2873),
    (".h-comecar",               16, 3077),
    (".t-comecar",               19, 3130),

    (".t-food-def",              20, 3695),
    (".food-badge-txt",         112, 3613),
    (".d-e122b",                48, 3555),
    (".d-basil",               110, 3544),
    (".d-tomato",              191, 3555),
    (".t-food",                  20, 3810),
    (".t-quote",                 20, 4199),

    (".passo-badge-txt",        103, 5021),
    (".d-e124",                 48, 4981),
    # a rotacao do celular passou para um <span> interno (o orbit-in anima a caixa):
    # a caixa medida agora e a do elemento sem giro; o visual nao mudou
    (".d-phone",             136.5, 4870),
    (".t-melhor-foto",           20, 5129),
    (".steps",                   33, 5195),
    (".t-agora",                 20, 5710),

    (".t-voce-deve",             20, 6188),
    (".tools",                    0, 6315),
    (".d-e125",               -275, 6298.5),
    (".d-chat-photo",             0, 5861),
    (".tool--claude .tool-logo", 87, 6600),

    (".t-copie",                 20, 6804),
    (".t-prompt",                20, 6987),
    (".t-segundos",              20, 7475),
    (".t-continua",              19, 7613),

    (".dica-badge-txt",         136, 8136),
    (".d-e126",                 48, 8097),
    (".d-choc",                130, 8028),
    (".t-dica",                  20, 8263),
    (".t-final",                 20, 8586),

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
