#!/usr/bin/env python
"""Mede a posicao real dos elementos da GESTÃƒO #75 contra as coordenadas do Figma.

    python scripts/probe_75_academia.py

Figma: 6954:9346 (402 x 8900, HEAD de 182 incluso): top esperado = y do Figma.
"""
import pathlib
from playwright.sync_api import sync_playwright

D = 0
EXPECT = [
    (".hero-foto",            0, 182),
    (".caixa--hero",       -123, 638),
    (".hero-titulo",         24, 738),
    (".hero-agora",          24, 832),
    (".hero-edicao",         23, 963),
    (".hero-autor",          23, 1003),
    (".hero-olho",           25, 1052),
    (".t-intro",             25, 1219),
    (".caixa--roxo",         -4, 1571),
    (".placa",               68, 1468),
    (".t-passo",             25, 1668),
    (".h-taxa",              18, 2089),
    (".t-conta",             25, 2129),
    (".caixa--conta",        13, 2171),
    (".conta-col--a .conta-icone", 36, 2190),
    (".conta-sinal--div",    110, 2201),
    (".conta-col--b .conta-icone", 164, 2190),
    (".conta-sinal--mul",    260, 2201),
    (".conta-cem",           298, 2197),
    (".conta-col--a .conta-rotulo", 4, 2256),
    (".conta-col--b .conta-rotulo", 177, 2267),
    (".t-mes",               26, 2364),
    (".caixa--resultado",    18, 2451),
    (".faixa-media",          0, 2581),
    (".lista-dados",         26, 2695),
    (".foto-mesa",            0, 3133),
    (".bl-mesa .h-roxo",     24, 3460),
    (".t-empório",           25, 3514),
    (".foto-gui",            40, 3958),
    (".leg-gui",             24, 4294),
    (".caixa--receita",      24, 4377),
    (".t-receita",           51, 4422),
    (".h-antes",             26, 5056),
    (".t-antes",             26, 5119),
    (".cupula-passos",       41, 5673),
    (".caixa--passos",       21, 5748),
    (".passo--1 .passo-n",  166, 5886),
    (".passo--1 h3",         23, 5942),
    (".passo--2 .passo-n",  166, 6028),
    (".passo--3 .passo-n",  166, 6166),
    (".passo--4 .passo-n",  166, 6321),
    (".passo--5 .passo-n",  171, 6476),
    (".h-decidiu",           24, 6697),
    (".t-cdc",               24, 6798),
    (".fundo-checklist",      0, 7236),
    (".caixa--checklist",    22, 7280),
    (".t-certifique",        49, 7355),
    (".h-funciona",          26, 8006),
    (".lista-vermelha",      26, 8061),
    (".t-fecho",             26, 8489),
    ("footer.foot",           0, 8786),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.goto(pathlib.Path("75/gestao.html").resolve().as_uri(), wait_until="load")
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
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 8900)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
