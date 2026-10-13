#!/usr/bin/env python
"""Mede a posicao real dos elementos da NOTICIAS #75 contra as coordenadas do Figma.

    python scripts/probe_75_noticias.py

Figma: 6889:2002 (402 x 5575, HEAD de 182 incluso): top esperado = y do Figma.
"""
import pathlib
from playwright.sync_api import sync_playwright

EXPECT = [
    (".hero-foto",            0,  182),
    (".hero-selo",          275,  197),
    (".hero-gancho",         25,  629),
    (".hero-destaque",       25,  700),
    (".hero-edicao",         25,  781),
    (".hero-olho",           26,  896),
    (".carrinho--1",        125, 1057),
    (".carrinho--2",         30, 1120),
    (".caixa--campanha",      0, 1283),
    (".t-campanha",          30, 1318),
    (".lista-premios",       19, 1665),
    (".cupula-amarela",      64, 1991),
    (".caixa--mecanica",     -3, 2099),
    (".h-multiplica",        24, 2512),
    (".t-extras",            25, 2590),
    (".carrossel-faixa",     58, 2679),
    (".extra--1 figure",    142, 2750),
    (".extra--1 p",         142, 2957),
    (".extra--2 figure",    561, 2743),
    (".extra--3 figure",    953, 2743),
    (".t-acumulo",           25, 3180),
    (".caixa--gratis",        0, 3351),
    (".h-gratis",            25, 3383),
    (".t-gratis",            26, 3436),
    (".t-ouro",              25, 3934),
    (".ilustra",             88, 4107),
    (".caixa--passos",       24, 4182),
    (".passos",              35, 4257),
    (".t-campanha-datas",    35, 4951),
    (".caixa--regulamento", -90, 5282),
    (".t-confira",           34, 5353),
    (".btn-regulamento",     74, 5386),
    ("footer.foot",           0, 5461),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.goto(pathlib.Path("75/noticias.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    # o carrossel horizontal vira scroll interno: as posicoes x dos cards 2 e 3 contam com scroll 0
    res = pg.evaluate(JS, [s for s, _, _ in EXPECT])
    ruins = 0
    for (s, x, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:22} AUSENTE"); ruins += 1; continue
        dy = r[1] - y; dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:22} x {r[0]:7.1f} ({dx:+4.0f})  y {r[1]:7.1f} esp {y:5} ({dy:+5.0f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 5575)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
