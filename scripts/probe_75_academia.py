#!/usr/bin/env python
"""Mede a posicao real dos elementos da ACADEMIA #75 contra as coordenadas do Figma.

    python scripts/probe_75_academia.py

Figma: 6961:2480 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 7307, HEAD de 182 incluso;
y abaixo no BLOCO do Figma, que comeca em 182).
O carrossel Heinz (40 + 451 + 54 - 102 = 443px) nao existe no Figma: entra depois dos botoes
"Para comecar pela base" e empurra o que vem abaixo em SH. O probe bloqueia o scroll-fx e o
ad-carousel.
"""
import pathlib
from playwright.sync_api import sync_playwright

D = 182     # o BLOCO do Figma comeca depois do HEAD
SH = 443    # carrossel Heinz
# (seletor, y no BLOCO do Figma, depois do carrossel?, "top" ou "bottom")
EXPECT = [
    (".hero-crescer", 443, 0, "top"),
    (".hero-linha", 547.5, 0, "top"),
    (".hero-olho", 673.5, 0, "top"),
    (".caixa--faixa-1", 842.5, 0, "top"),
    (".t-faixa", 873.08, 0, "top"),
    (".caixa--faixa-1", 1326.5, 0, "bottom"),
    (".btn--g1", 1301, 0, "top"),
    (".h-lar", 1388.13, 0, "top"),
    (".t-ritmo", 1469.13, 0, "top"),
    (".btn--g2", 1627.57, 0, "top"),
    (".reforma-foto", 1713.78, 0, "top"),
    (".caixa--reforma", 2005.2, 0, "top"),
    (".capa-reforma", 2016.72, 0, "top"),
    (".t-reforma", 2192.91, 0, "top"),
    (".caixa--reforma", 2610.2, 0, "bottom"),
    (".h-roxo", 2651, 0, "top"),
    (".t-investir", 2738, 0, "top"),
    (".faixa-escolha", 3094.89, 0, "top"),
    (".caixa--cursos", 3095, 0, "top"),
    (".caixa--cursos .cab", 3183.89, 0, "top"),
    (".item--c1", 3269, 0, "top"),
    (".btn--c1", 3364, 0, "top"),
    (".item--c2", 3450.45, 0, "top"),
    (".btn--c2", 3529.87, 0, "top"),
    (".caixa--cursos", 3606, 0, "bottom"),
    (".caixa--video", 3556.29, 0, "top"),
    (".t-cursos", 3648, 0, "top"),
    (".caixa--video .cab", 3774.5, 0, "top"),
    (".item--v1", 3852.5, 0, "top"),
    (".btn--v1", 3974.5, 0, "top"),
    (".item--v2", 4060.95, 0, "top"),
    (".btn--v2", 4181.95, 0, "top"),
    (".caixa--video", 4283.13, 0, "bottom"),
    (".caixa--baixar", 3958, 0, "top"),
    (".caixa--baixar .cab", 4320, 0, "top"),
    (".item--b1", 4391, 0, "top"),
    (".btn--b1", 4583, 0, "top"),
    (".item--b2", 4666, 0, "top"),
    (".caixa--baixar", 4874.5, 0, "bottom"),
    (".btn--b2", 4915.6, 0, "top"),
    (".h-base", 5030, 0, "top"),
    (".t-base", 5081.95, 0, "top"),
    (".btn--s1", 5206, 0, "top"),
    (".btn--s2", 5264, 0, "top"),
    (".caixa--assessoria", 5408, 1, "top"),
    (".caixa--assessoria .cab", 5461, 1, "top"),
    (".t-sorteio", 5554, 1, "top"),
    (".caixa--assessoria", 5682, 1, "bottom"),
    (".h-comece", 5763, 1, "top"),
    (".t-comece", 5843, 1, "top"),
    (".caixa--chamada", 6016, 1, "top"),
    (".btn--site", 6164.33, 1, "top"),
    (".ad-rotulo", 6284, 1, "top"),
    ("footer.foot", 7009, 1, "top"),
]

JS = """(items) => items.map(([s, m]) => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, m === "bottom" ? r.top + scrollY + r.height : r.top + scrollY]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.route("**/ad-carousel.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/academia.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [[e[0], e[3]] for e in EXPECT])
    ruins = 0
    for (s, y, dep, m), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:30} AUSENTE"); ruins += 1; continue
        alvo = y + D + (SH if dep else 0)
        dy = r[1] - alvo
        flag = "  <<<" if abs(dy) > 3 else ""
        ruins += bool(flag)
        print(f"{s:30} {m:6} y {r[1]:8.1f} esp {alvo:8.1f} ({dy:+5.1f}){flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 7307 + carrossel {SH})")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
