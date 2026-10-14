#!/usr/bin/env python
"""Mede a posicao real dos elementos da PRINCIPAL #75 contra as coordenadas do Figma.

    python scripts/probe_75_principal.py

Figma: 6842:1693 (402 x 9296, sem o HEAD). Topo esperado = y do Figma + 182 do HEAD.
"""
import pathlib
from playwright.sync_api import sync_playwright

H = 182
EXPECT = [
    (".hero-edicao",        25,  364),
    (".hero-autor",         25,  403),
    (".hero-titulo",        22,  455),
    (".hero-olho",          23,  573),
    (".caixa--intro",       -1,  715),
    (".caixa--intro p",     29,  760),
    (".caixa--intro p:nth-of-type(2)", 29, 922),
    (".menuci",             80, 1199),
    (".q-menuci p",         27, 1463),
    (".zanatta",            71, 1877),
    (".caixa--palco",        0, 1962),
    (".h-palco",            24, 2250),
    (".caixa--palco p",     24, 2335),
    (".t-levantamento",     33, 2721),
    (".h-efeito",            0, 2906),
    (".t-consumidores",      0, 2940),
    (".stat--1",             0, 2989),
    (".stat--2",             0, 3090),
    (".stat--3",             0, 3208),
    (".stat--4",             0, 3327),
    (".banda",               0, 3407),
    (".t-dados",            25, 3748),
    (".caixa--cliente",      0, 3919),
    (".h-cliente",          39, 3983),
    (".t-cliente",          26, 4071),
    (".exp",                26, 4755),
    (".h-gastar",           24, 5215),
    (".t-gastar",           28, 5299),
    (".pilula--1",          27, 5455),
    (".pilula--4",          27, 5641),
    (".t-alerta",           25, 5729),
    (".caixa--habito",       0, 5838),
    (".h-habito",           28, 5886),
    (".t-habito",           28, 5978),
    (".h-custo",             0, 6274),
    (".t-cache",             0, 6311),
    (".custos",             22, 6366),
    (".q-couvert",          28, 6948),
    (".faixa--vermelha",     0, 7171),
    (".conta",              28, 7243),
    (".t-compare",          26, 7416),
    (".salao",             -11, 7500),
    (".caixa--cheia",      -11, 7778),
    (".h-cheia",            20, 7849),
    (".faixa--grad",        -6, 8151),
    (".ruido",              26, 8205),
    (".h-final-a",          30, 8487),
    (".t-final",            30, 8600),
    (".caixa--final",        0, 8849),
    (".t-final-fim",        30, 9108),
    ("footer.foot",          0, 9296),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/principal.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [s for s, _, _ in EXPECT])
    ruins = 0
    for (s, x, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:34} AUSENTE"); ruins += 1; continue
        dy = r[1] - (y + H); dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:34} x {r[0]:7.1f} ({dx:+5.0f})  y {r[1]:7.1f} esp {y+H:5} ({dy:+5.0f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
