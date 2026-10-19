#!/usr/bin/env python
"""Mede a posicao real dos elementos da CONSUMIDOR #75 contra as coordenadas do Figma.

    python scripts/probe_75_consumidor.py

Figma: 6941:8303 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 9006, HEAD de 182 incluso).
O titulo (.hero-titulo) fica 4px acima da caixa do Figma (33,77 em vez de 37,77): o glifo
da Raspoutine cai ~4px abaixo da caixa e, assim, bate com o Figma.
A cupula rosa (.cupula--formula) cresce em telas altas (min-height: max(328, 100vh - 570)); o probe usa
viewport de 800px de altura, em que vale os 328px do Figma.
O banner rotativo (.adbox) fecha a pagina e nao existe no Figma; o probe bloqueia o
consumidor.js para ele nao ser sorteado.
"""
import pathlib
from playwright.sync_api import sync_playwright

D = 182   # o BLOCO do Figma comeca depois do HEAD
# (seletor, x, y no BLOCO do Figma)
EXPECT = [
    (".hero-titulo",                 26,     33.77),
    (".hero-olho",                   25,    182),
    (".hero-assina",                133.5,  309.68),
    (".hero-foto",                 -78.79,  341.47),
    (".t-intro",                     20,    772.51),
    (".foto-buffet",                -12,   1272.75),
    (".cupula--ocasiao",            -82.5,  1566.75),
    (".h-ocasiao",                   20,   1641.63),
    (".t-ocasiao",                   20,   1728.63),
    (".h-comemos",                   26,   2200.21),
    (".t-motivacoes",                23,   2243.97),
    (".circulos--rosa",              24,   2355.02),
    (".circulos--rosa .circulo:nth-child(3)", 24, 2544.52),
    (".h-pesa",                      27,   2783.92),
    (".circulos--roxo",              24,   2868.04),
    (".circulo--centro",            117,   3046.09),
    (".fonte",                       27,   3256.89),
    (".cupula--chef",               -81,   3369.61),
    (".t-chef",                      22.43, 3470.61),
    (".chef",                        81,   3904.04),
    (".q-chef",                      20,   4213),
    (".cupula--redes",              -82.5,  4497),
    (".h-redes",                     20,   4571.88),
    (".t-redes",                     20,   4658.88),
    (".insta",                       17,   5036.27),
    (".h-feed",                     113,   5149.27),
    (".stat--topo",                 132.2,  5216.44),
    (".barra-roxa",                 -12,   5379.36),
    (".stats--a .stat:nth-child(1)", 53.95, 5460.84),
    (".stats--a .stat:nth-child(2)", 53.95, 5562.09),
    (".barra-roxa--2",              -12,   5679.03),
    (".stats--b .stat:nth-child(1)", 53.95, 5768.4),
    (".stats--b .stat:nth-child(2)", 53.95, 5869.65),
    (".stats--b .stat:nth-child(3)", 53.95, 5970.9),
    (".fonte--feed",                 96,   6086.32),
    (".foto-pizza",                  -3,   6148.9),
    (".faixa--atracao",             -53,   6485.9),
    (".t-retencao",                  20,   6681.95),
    (".cupula--nem",                -82.5,  7117),
    (".cupula--nem .h-cupula",       26,   7216),
    (".cupula--nem .t-cupula",       26,   7303),
    (".cupula--descubra",           -91,   7755),
    (".cupula--descubra .h-cupula",  20,   7847.34),
    (".cupula--descubra .t-cupula",  20,   7961.34),
    (".cupula--formula",            -83,   8379.99),
    (".formula",                     30,   8469.04),
    (".adbox",                        0,   8708),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 800})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.route("**/consumidor.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/consumidor.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [e[0] for e in EXPECT])
    ruins = 0
    for (s, x, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:38} AUSENTE"); ruins += 1; continue
        alvo = y + D
        dy = r[1] - alvo; dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:38} x {r[0]:7.1f} ({dx:+5.1f})  y {r[1]:7.1f} esp {alvo:7.1f} ({dy:+5.1f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 9006 + banner)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
