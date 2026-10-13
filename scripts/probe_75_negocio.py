#!/usr/bin/env python
"""Mede a posicao real dos elementos da NOVO NEGOCIO #75 contra as coordenadas do Figma.

    python scripts/probe_75_negocio.py

Figma: 4424:19580 (402 x 8971, HEAD de 182 incluso): top esperado = y do Figma.
A partir da .caixa--narrativa, +37: respiro de 40px sob o texto que o Figma corta (a cupula o cobre).
"""
import pathlib
from playwright.sync_api import sync_playwright

EXPECT = [
    (".hero-foto",            0,  182),
    (".hero-gancho",      None,  633),
    (".hero-destaque",    None,  722),
    (".hero-olho",          20,  795),
    (".hero-edicao",      None,  930),
    (".hero-autor",       None,  969),
    (".foto--cemiterio",    -7, 1034),
    (".balao--1",           11, 1382),
    (".foto--fachada",       0, 1475),
    (".balao--2",           16, 1689),
    (".t-comprova",         24, 1854),
    (".t-bar",              21, 1942),
    (".t-clientela",        21, 2241),
    (".t-halloween",        24, 2414),
    (".faixa-boo",           0, 2605),
    (".caixa--velorio",      0, 2820),
    (".h-velorio",          21, 2855),
    (".t-velorio",          23, 2904),
    (".vulcao",             53, 3087),
    (".t-vulcao",           22, 3394),
    (".mapa",                0, 3598),
    (".balao--3",           18, 3938),
    (".foto--largura",       0, 4004),
    (".h-largura",          17, 4562),
    (".t-recife",           17, 4621),
    (".q-espremida",        20, 4741),
    (".t-endereco",         26, 5098),
    (".caixa--narrativa",    0, 5358),
    (".h-narrativa",      None, 5500),
    (".t-narrativa",        30, 5611),
    (".t-cozinha",          39, 6339),
    (".foto--prato",         0, 6650),
    (".caixa--ensina",       0, 7039),
    (".t-tres",              0, 7484),
    (".licao:nth-child(1)", 18, 7583),
    (".licao:nth-child(2)", 18, 7943),
    (".licao:nth-child(3)", 18, 8273),
    (".caixa--fecho",       -2, 8580),
    ("footer.foot",          0, 8892),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/negocio.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [s for s, _, _ in EXPECT])
    ruins = 0
    for (s, x, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:24} AUSENTE"); ruins += 1; continue
        dy = r[1] - y
        dx = 0 if x is None else r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:24} x {r[0]:7.1f} ({dx:+4.0f})  y {r[1]:7.1f} esp {y:5} ({dy:+5.0f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 8971 + 37)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
