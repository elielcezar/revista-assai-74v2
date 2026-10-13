#!/usr/bin/env python
"""Mede a posicao real dos elementos da ACADEMIA ASSAÍ #75 contra as coordenadas do Figma.

    python scripts/probe_75_academia.py

Figma: 6948:8406 (402 x 7591, HEAD de 182 incluso): top esperado = y do Figma.
"""
import pathlib
from playwright.sync_api import sync_playwright

D = 0
EXPECT = [
    (".hero-foto",            0, 182),
    (".hero-crescer",       22, 633),
    (".hero-exige",         24, 704),
    (".hero-edicao",        24, 786),
    (".hero-autor",         24, 826),
    (".hero-icones",       200, 760),
    (".hero-olho",          22, 903),
    (".hero-texto",         24, 1083),
    (".caixa--faixa-1",     -1, 1254),
    (".t-mes",              25, 1311),
    (".btn--g1",            28, 1580),
    (".h-lar",              26, 1707),
    (".t-ritmo",            25, 1788),
    (".btn--g2",            25, 1936),
    (".reforma-foto",        0, 2018),
    (".capa-reforma",       63, 2274),
    (".caixa--reforma",    -10, 2363),
    (".t-reforma",          31, 2461),
    (".h-roxo",             33, 2963),
    (".t-investir",         31, 3050),
    (".faixa-escolha",     -12, 3420),
    (".caixa--cursos",     -10, 3455),
    (".tile--cursos",       46, 3492),
    (".h-cursos",           34, 3505),
    (".item--c1",           81, 3566),
    (".btn--c1",            28, 3635),
    (".item--c2",           84, 3698),
    (".btn--c2",            28, 3752),
    (".t-cursos",           46, 3832),
    (".caixa--video",       -9, 3741),
    (".tile--video",        42, 4001),
    (".h-video",           -34, 4017),
    (".item--v1",           80, 4079),
    (".btn--v1",            24, 4201),
    (".item--v2",           87, 4274),
    (".btn--v2",            26, 4395),
    (".caixa--baixar",     -13, 4479),
    (".tile--baixar",       42, 4550),
    (".h-baixar",          -31, 4568),
    (".item--b1",           86, 4616),
    (".btn--b1",            24, 4818),
    (".item--b2",           87, 4895),
    (".btn--b2",            23, 5083),
    (".h-base",            -50, 5249),
    (".t-base",             25, 5293),
    (".btn--s1",            23, 5396),
    (".btn--s2",            24, 5454),
    (".t-dicas",            26, 5549),
    (".caixa--assessoria",  -7, 5723),
    (".tile--assess",       42, 5765),
    (".h-assess",          111, 5765),
    (".t-sorteio",          24, 5848),
    (".h-aumento",          24, 5959),
    (".t-aumento",          24, 6031),
    (".h-comece",           26, 6316),
    (".t-comece",           27, 6391),
    (".caixa--chamada",     55, 6556),
    (".btn--site",          26, 6692),
    (".ad-rotulo",          24, 6789),
    (".ad-box",              0, 6812),
    (".ad-texto",           70, 7009),
    (".ad-play",           162, 7163),
    ("footer.foot",          0, 7475),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.goto(pathlib.Path("75/academia.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [s for s, _, _ in EXPECT])
    ruins = 0
    for (s, x, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:22} AUSENTE"); ruins += 1; continue
        dy = r[1] - y; dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:22} x {r[0]:7.1f} ({dx:+4.0f})  y {r[1]:7.1f} esp {y:6} ({dy:+5.0f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 7591)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
