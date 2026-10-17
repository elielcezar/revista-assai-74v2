#!/usr/bin/env python
"""Mede a posicao real dos elementos da MKT DIGITAL #75 contra as coordenadas do Figma.

    python scripts/probe_75_mkt.py

Figma: 6941:8350 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 6552, HEAD de 182 incluso).
O banner rotativo (.adbox) nao existe no Figma: entra depois do video em circulo e
empurra tudo o que vem abaixo em AD (altura da 1a imagem, davene, em 402px + 46 de folga).
O probe bloqueia o mkt.js para o banner nao ser sorteado.
"""
import pathlib
from playwright.sync_api import sync_playwright

D = 182        # o BLOCO do Figma comeca depois do HEAD
AD = 465.14    # banner rotativo: 419,14 + 46
# (seletor, x, y no BLOCO do Figma, depois do banner?)
EXPECT = [
    (".hero-titulo",              18.41,  507.61, 0),
    (".hero-olho",                19.91,  691.46, 0),
    (".hero-assina",              19.91,  839.72, 0),
    (".t-cookies",                19.91, 1004.44, 0),
    (".cookie",                  -10.52, 1520.93, 0),
    (".caixa--resultado",        -88.02, 1608.51, 0),
    (".h-resultado",              20,    1854.26, 0),
    (".t-resultado",              20,    1914.26, 0),
    (".duas",                     75.5,  2389.39, 0),
    (".leg-duas",                 20,    2676.59, 0),
    (".h-viral",                  20,    2771,    0),
    (".t-pergunta",               20,    2831,    0),
    (".pilulas-mais",             20,    3310,    0),
    (".pilulas-mais li:nth-child(2)", 20, 3452,   0),
    (".pilulas-mais li:nth-child(3)", 20, 3594,   0),
    (".video--circulo",           19,    3716.34, 0),
    (".adbox",                    0,     4126.34, 0),
    (".capa-basico",              65.5,  4126.49, 1),
    (".t-pequeno",                28,    4305,    1),
    (".pilulas--a",               20,    4398,    1),
    (".t-mais",                   28,    4803.16, 1),
    (".pilulas--b",               20,    4867.16, 1),
    (".t-giulia",                 21.5,  5347.98, 1),
    (".bl-trend",                  0,    5581,    1),
    (".h-trend",                  21.5,  5628.44, 1),
    (".trend-video",              21.5,  5716,    1),
    ("footer.foot",                0,    6254,    1),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.route("**/mkt.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/mkt.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [e[0] for e in EXPECT])
    ruins = 0
    for (s, x, y, dep), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:32} AUSENTE"); ruins += 1; continue
        alvo = y + D + (AD if dep else 0)
        dy = r[1] - alvo; dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:32} x {r[0]:7.1f} ({dx:+5.1f})  y {r[1]:7.1f} esp {alvo:7.1f} ({dy:+5.1f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 6552 + banner {AD})")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
