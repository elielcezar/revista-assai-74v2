#!/usr/bin/env python
"""Mede a posicao real dos elementos da NOVO NEGOCIO #75 contra as coordenadas do Figma.

    python scripts/probe_75_negocio.py

Figma: 6931:7505 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 7277, HEAD de 182 incluso).
Os 4 blocos do Figma comecam em 182, 632, 2478 e 4993 (B1..B4 abaixo).
O banner rotativo (.adbox: 40 de folga + 419 da imagem = AD) nao existe no Figma: entra depois
da foto do Largura e empurra tudo o que vem abaixo em AD. O probe bloqueia o negocio.js
para o banner nao ser sorteado. O titulo (.hero-gancho) fica 8px acima da caixa do Figma
(43,86 em vez de 51,86): o glifo da Raspoutine cai ~8px abaixo da caixa.
"""
import pathlib
from playwright.sync_api import sync_playwright

AD = 459.14
B1, B2, B3, B4 = 182, 632, 2478, 4993
# (seletor, y esperado)
EXPECT = [
    (".hero-gancho", B1 + 43.86),
    (".hero-destaque", B1 + 140.86),
    (".hero-olho", B1 + 206.8),
    (".hero-assina", B1 + 336),
    (".t-bar", B2 + 954),
    (".retrato--frym", B2 + 1454),
    (".bl-bar .legenda", B2 + 1725),
    (".adbox", B3 + 926.5 + 40),
    (".t-largura", B3 + 988.26 + AD),
    (".retrato--wilson", B3 + 1461.32 + AD),
    (".legenda--wilson", B3 + 1739.39 + AD),
    (".h-narrativa", B3 + 1841.09 + AD),
    (".ensina", B4 + 333 + AD),
    (".t-tres", B4 + 714.03 + AD),
    (".licao-num", B4 + 828 + AD),
    (".caixa-fecho", B4 + 1831 + AD),
    ("footer.foot", 7161 + AD),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return r.top + scrollY; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.route("**/negocio.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/negocio.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [e[0] for e in EXPECT])
    ruins = 0
    for (s, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:28} AUSENTE"); ruins += 1; continue
        dy = r - y
        flag = "  <<<" if abs(dy) > 3 else ""
        ruins += bool(flag)
        print(f"{s:28} y {r:8.1f} esp {y:8.1f} ({dy:+5.1f}){flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 7277 + banner {AD})")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
