#!/usr/bin/env python
"""Mede a posicao real dos elementos da PRODUTO #75 contra as coordenadas do Figma.

    python scripts/probe_75_produto.py

Figma: 6960:1125 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 5965, HEAD de 182 incluso).
O story do Maturatta (715px + 40 de folga) nao existe no Figma: entra depois dos cards
de materiais e empurra tudo o que vem abaixo em STORY.
O titulo (.hero-titulo) fica 4px acima da caixa do Figma (441 em vez de 445) porque o
glifo da Raspoutine cai ~4px abaixo da caixa; o glifo bate com o Figma.
"""
import pathlib
from playwright.sync_api import sync_playwright

D = 182        # o BLOCO do Figma comeca depois do HEAD
STORY = 755    # story do Maturatta: 715 + 40
# (seletor, x, y no BLOCO do Figma, depois do story?)
EXPECT = [
    (".hero-titulo",              21,    441,     0),
    (".hero-olho",                21,    594.5,   0),
    (".hero-assina",              21,    715,     0),
    (".t-hero",                   19.25, 821.09,  0),
    (".h-anvisa",                 20,    1301,    0),
    (".t-anvisa",                 20,    1361,    0),
    (".caixa--norma",            -9.98,  1543.4,  0),
    (".t-norma",                  17.15, 1584.9,  0),
    (".maos",                     82.7,  1818.76, 0),
    (".t-cartilha",               19,    2113,    0),
    (".foto-lavando",            -1,     2193,    0),
    (".btn-cartilha",             19,    2463.48, 0),
    (".caixa--laranja",          -82.5,  2474,    0),
    (".t-laranja",                18.09, 2536.83, 0),
    (".burger",                  -29.31, 2969.33, 0),
    (".caixa--azul",             -82.5,  3331,    0),
    (".h-pretas",                 19.5,  3400.37, 0),
    (".t-pretas",                 19.5,  3460.37, 0),
    (".luvas-circulo",            81,    3735.09, 0),
    (".h-materiais",              20,    4013.09, 0),
    (".t-materiais",              20,    4073.09, 0),
    (".cards",                   -4,     4204,    0),
    (".card:nth-child(2)",       -4,     4429,    0),
    (".card:nth-child(3)",       -4,     4634,    0),
    (".card:nth-child(4)",       -4,     4839,    0),
    (".story",                    0,     5047,    0),
    (".h-questiona",              20,     5072,   1),
    (".t-questiona",              20,     5159,   1),
    ("footer.foot",               0,     5667,    1),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/produto.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [e[0] for e in EXPECT])
    ruins = 0
    for (s, x, y, dep), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:24} AUSENTE"); ruins += 1; continue
        alvo = y + D + (STORY if dep else 0)
        dy = r[1] - alvo; dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:24} x {r[0]:7.1f} ({dx:+5.1f})  y {r[1]:7.1f} esp {alvo:7.1f} ({dy:+5.1f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 5965 + story {STORY})")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
