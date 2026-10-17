#!/usr/bin/env python
"""Mede a posicao real dos elementos da GESTAO #75 contra as coordenadas do Figma.

    python scripts/probe_75_gestao.py

Figma: 6956:9875 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 8199, HEAD de 182 incluso).
O story do Omo (715px) entra depois da caixa vermelha e nao existe no Figma:
tudo o que vem abaixo dele desce 715px (STORY).
"""
import pathlib
from playwright.sync_api import sync_playwright

D = 182      # o BLOCO do Figma comeca depois do HEAD
STORY = 715  # story do Omo (video 402 x 715)
# (seletor, x, y no BLOCO do Figma, depois do story?)
EXPECT = [
    (".hero-foto",               -6.37,   -8.31, 0),
    (".caixa--hero",            -82.5,   370.89, 0),
    (".hero-titulo",             21.25,  420.01, 0),
    (".hero-agora",              None,   514.01, 0),
    (".hero-olho",               21.25,  598.08, 0),
    (".hero-assina",            132.5,   784.59, 0),
    (".t-intro",                 21.25,  888.28, 0),
    (".placa",                   85.11, 1161.05, 0),
    (".caixa--roxo",             -4,    1251.27, 0),
    (".t-passo",                 25,    1348.27, 0),
    (".story",                   0,     1717.27, 0),
    (".bl-taxa .h-roxo",         20,    1786.13, 1),
    (".t-taxa",                  20,    1873.13, 1),
    (".bl-media .h-roxo",        20,    2105.57, 1),
    (".lista-dados",             20,    2192.57, 1),
    (".foto-mesa",               -6.5,  2639.87, 1),
    (".bl-mesa .h-roxo",         21,    2970,    1),
    (".t-empório",               21,    3030,    1),
    (".caixa--receita",          -4,    3528.11, 1),
    (".caixa--receita .h-amarelo", 21,  3569,    1),
    (".t-receita",               21,    3656,    1),
    (".foto-gui",                81,    4150.17, 1),
    (".leg-gui",                 24,    4415,    1),
    (".bl-cobrar .h-vermelho",   20,    4527,    1),
    (".t-antes",                 20,    4587,    1),
    (".prato",                   47.35, 5121.7,  1),
    (".h-caminhos",              21.5,  5463.7,  1),
    (".passo--1",                21.5,  5551,    1),
    (".passo--2",                21.5,  5701,    1),
    (".passo--3",                21.5,  5852,    1),
    (".passo--4",                21.5,  6020,    1),
    (".passo--5",                21.5,  6188,    1),
    (".caixa--decidiu",         -89.17, 6446.56, 1),
    (".caixa--decidiu .h-amarelo", 24,  6625,    1),
    (".t-cdc",                   24,    6721,    1),
    (".t-checklist",             24,    7165.78, 1),
    (".t-fecho",                 21.17, 7689.56, 1),
    ("footer.foot",               0,    7901,    1),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/gestao.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [e[0] for e in EXPECT])
    ruins = 0
    for (s, x, y, dep), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:28} AUSENTE"); ruins += 1; continue
        alvo = y + D + (STORY if dep else 0)
        dy = r[1] - alvo; dx = 0 if x is None else r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:28} x {r[0]:7.1f} ({dx:+5.1f})  y {r[1]:7.1f} esp {alvo:7.1f} ({dy:+5.1f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 8199 + story {STORY})")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
