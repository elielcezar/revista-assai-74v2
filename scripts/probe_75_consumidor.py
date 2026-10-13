#!/usr/bin/env python
"""Mede a posicao real dos elementos da CONSUMIDOR #75 contra as coordenadas do Figma.

    python scripts/probe_75_consumidor.py

Figma: 6903:2345 (402 x 11829, HEAD de 182 incluso): top esperado = y do Figma.
O quadro do Figma termina no meio da "formula de sucesso" e nao tem rodape:
a partir da .cupula--formula a pagina cresce (texto inteiro + rodape comum).
"""
import pathlib
from playwright.sync_api import sync_playwright

EXPECT = [
    (".hero-titulo",            26,  228),
    (".hero-olho",              25,  372),
    (".hero-assina",           131,  500),
    (".hero-foto",               0,  532),
    (".bl-intro p",             26,  963),
    (".foto-buffet",           -12, 1463),
    (".cupula--ocasiao",       -82, 1757),
    (".h-ocasiao",              20, 1832),
    (".t-ocasiao",              20, 1919),
    (".h-comemos",              26, 2390),
    (".t-motivacoes",           23, 2434),
    (".circulos--rosa .circulo", 24, 2545),
    (".h-pesa",                 27, 2974),
    (".circulos--roxo .circulo", 24, 3058),
    (".fonte",                  27, 3447),
    (".cupula--chef",          -81, 3560),
    (".cupula--chef p",         22, 3661),
    (".chef",                   56, 4070),
    (".q-chef",                 20, 4403),
    (".cupula--jornada",       -82, 4687),
    (".h-feed",                 24, 5964),
    (".stat-num",                0, 6027),
    (".barra-roxa",            -12, 6089),
    (".foto-pizza",             -3, 6593),
    (".faixa--atracao",        -53, 6930),
    (".t-retencao",             30, 7109),
    (".cupula-num--3",         180, 7596),
    (".cupula--nem",           -82, 7624),
    (".cupula-num--4",         168, 8353),
    (".cupula--descubra",      -91, 8366),
    (".h-pistas",               26, 9454),
    (".pistas",                 26, 9572),
    (".cupula-num--5",         174, 10456),
    (".cupula--testar",        -81, 10469),
    (".faixa--oferta",         -35, 11139),
    (".checklist",              25, 11289),  # no Figma a caixa de texto comeca em 11250, com a 1a linha em 11289
    (".cupula--formula",       -72, 11664),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.goto(pathlib.Path("75/consumidor.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [s for s, _, _ in EXPECT])
    ruins = 0
    for (s, x, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:26} AUSENTE"); ruins += 1; continue
        dy = r[1] - y; dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:26} x {r[0]:7.1f} ({dx:+4.0f})  y {r[1]:8.1f} esp {y:6} ({dy:+5.0f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 11829, sem rodape)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
