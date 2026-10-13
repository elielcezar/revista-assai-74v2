#!/usr/bin/env python
"""Mede a posicao real dos elementos da PRODUTO #75 contra as coordenadas do Figma.

    python scripts/probe_75_produto.py

Figma: 6867:1969 (402 x 7328, HEAD de 182 incluso): top esperado = y do Figma.
"""
import pathlib
from playwright.sync_api import sync_playwright

EXPECT = [
    (".hero-foto",            0,  185),
    (".hero-assina",        24,  709),
    (".hero-titulo",        21,  788),  # a tinta bate com o Figma; o navegador assenta o Raspoutine 4px mais baixo na caixa
    (".hero-olho",          26,  970),
    (".t-hero",             26, 1108),
    (".video",               0, 1524),
    (".video-sound",       316, 1503),
    (".q-polemica",         24, 2000),
    (".anvisa-titulo",      63, 2275),  # oval e titulo 5px abaixo do nó: e onde a tinta aparece no Figma
    (".t-anvisa",           26, 2429),
    (".caixa--resolucao",   24, 2574),
    (".t-trabalhar",        26, 2930),
    (".t-cartilha",         27, 3086),
    (".foto-lavando",        0, 3187),
    (".btn-cartilha",       81, 3451),
    (".padrao",              0, 3497),
    (".maos",               -2, 3520),
    (".caixa--bordo",      -91, 3734),
    (".h-bordo",            46, 3839),
    (".t-bordo",            29, 3930),
    (".burger",             -1, 4481),
    (".caixa--azul",       -91, 4782),
    (".h-pretas",           47, 4882),
    (".t-pretas",           24, 4961),
    (".luvas-circulo",      86, 5189),
    (".caixa--vermelha",   -91, 5248),
    (".card--1",            44, 5443),
    (".card--2",            47, 5616),
    (".card--3",            47, 5834),
    (".card--4",            47, 6035),
    (".card--5",            47, 6236),
    (".duvida",             24, 6492),
    (".h-duvida",           91, 6594),
    (".t-duvida",           24, 6675),
    ("footer.foot",          0, 7214),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.goto(pathlib.Path("75/produto.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [s for s, _, _ in EXPECT])
    ruins = 0
    for (s, x, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:20} AUSENTE"); ruins += 1; continue
        dy = r[1] - y; dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:20} x {r[0]:7.1f} ({dx:+4.0f})  y {r[1]:7.1f} esp {y:5} ({dy:+5.0f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 7328)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
