#!/usr/bin/env python
"""Mede a posicao real dos elementos da MKT DIGITAL #75 contra as coordenadas do Figma.

    python scripts/probe_75_mkt.py

Figma: 6934:6616 (402 x 8311, HEAD de 182 incluso): top esperado = y do Figma.
No Figma os dois titulos brancos do topo se sobrepoem (811 e 866, 48px): aqui
eles seguem em fluxo, em 4 linhas, e tudo abaixo desce +55px (D).
"""
import pathlib
from playwright.sync_api import sync_playwright

D = 55
EXPECT = [
    (".video--hero",           0, 182),
    (".caixa--hero",          0, 693),
    (".hero-titulo",         27, 811),
    (".hero-olho",           28, 1009 + D),
    (".hero-assina",         24, 1163 + D),
    (".bl-cookies .h-rosa",  27, 1316 + D),
    (".t-cookies",           27, 1374 + D),
    (".duas",              75.5, 1768 + D),
    (".caixa--resultado",   -94, 1955 + D),
    (".h-resultado",        26, 2047 + D),
    (".t-resultado",        35, 2140 + D),
    (".cookie",            -12, 2409 + D),
    (".h-longe",            32, 2666 + D),
    (".t-boticario",        36, 2715 + D),
    (".video--clip",        -11, 2982 + D),
    (".h-viral",            26, 3463 + D),
    (".t-pergunta",         26, 3521 + D),
    (".q-giulia",           33, 3658 + D),
    (".t-edna",             31, 4042 + D),
    (".foto-cookies",       -8, 4473 + D),
    (".capa-basico",        61, 5011 + D),
    (".t-pequeno",          28, 5171 + D),
    (".pilulas",            20, 5264 + D),
    (".t-mais",             28, 5637 + D),
    (".pilulas--2",         20, 5701 + D),
    (".t-giulia",           34, 6197 + D),
    (".video--circulo",     19, 6414 + D),
    (".caixa--trend",      -50, 6826 + D),
    (".h-trend",             7, 6890 + D),
    (".passos",             46, 6950 + D),
    (".pronto",             49, 7785 + D),
    (".t-cuidados",         35, 8077 + D),
    ("footer.foot",          0, 8196 + D),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.goto(pathlib.Path("75/mkt.html").resolve().as_uri(), wait_until="load")
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
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 8311 + {D} + 1)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
