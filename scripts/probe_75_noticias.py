#!/usr/bin/env python
"""Mede a posicao real dos elementos da NOTICIAS #75 contra as coordenadas do Figma.

    python scripts/probe_75_noticias.py

Figma: 6961:3218 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 6012, HEAD de 182 incluso).
Os 5 blocos do Figma comecam em 182, 1407, 2873, 4530 e 5493 (B2..B5 abaixo).
O banner rotativo (.adbox, 419px) fecha a pagina e nao existe no Figma: o rodape desce 419px.
O titulo (.hero-gancho) fica 4px acima da caixa do Figma (524,87 em vez de 528,87): o glifo da
Raspoutine cai ~4px abaixo da caixa e, assim, bate com o Figma. O probe bloqueia o
noticias.js para o banner nao ser sorteado.
"""
import pathlib
from playwright.sync_api import sync_playwright

B2, B3, B4, B5 = 1407, 2873, 4530, 5493
AD = 419.14
# (seletor, y esperado)
EXPECT = [
    (".hero-gancho", 182 + 524.87),
    (".hero-destaque", 182 + 612.87),
    (".hero-olho", 182 + 695.13),
    (".hero-assina", 182 + 820),
    (".carrinhos", 182 + 918.28),
    (".t-topo", B2 + 38.72),
    (".mais15", B2 + 295.11),
    (".premios", B2 + 455),
    (".bl-campanha .cupula-amarela", B2 + 784),
    (".caixa--mecanica", B2 + 892),
    (".t-mecanica", B2 + 967),
    (".btn-site", B2 + 1134),
    (".t-mecanica--2", B2 + 1207),
    (".h-multiplica", B3 + 35),
    (".t-extras", B3 + 134),
    (".carrossel-wrap", B3 + 299),
    (".h-marcas", B3 + 799),
    (".logos", B3 + 958),
    (".h-gratis", B3 + 1284),
    (".t-gratis", B3 + 1366),
    (".bl-passos .cupula-amarela", B4 + 77.46),
    (".passo--1 .passo-num", B4 + 265.16),
    (".passo--2 .passo-num", B4 + 431.48),
    (".passo--3 .passo-num", B4 + 568),
    (".passo--4 h3", B4 + 821),
    (".btn-regulamento", B5 + 182.66),
    (".t-legal", B5 + 266.42),
    ("footer.foot", 5896 + AD),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return r.top + scrollY; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.route("**/noticias.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/noticias.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [e[0] for e in EXPECT])
    ruins = 0
    for (s, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:32} AUSENTE"); ruins += 1; continue
        dy = r - y
        flag = "  <<<" if abs(dy) > 3 else ""
        ruins += bool(flag)
        print(f"{s:32} y {r:8.1f} esp {y:8.1f} ({dy:+5.1f}){flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 6012 + banner {AD})")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
