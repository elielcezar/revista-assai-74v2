#!/usr/bin/env python
"""Mede a posicao real dos elementos da PRINCIPAL #75 contra as coordenadas do Figma.

    python scripts/probe_75_principal.py

Figma: 6949:8697 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 7102, com o HEAD).
Topo esperado = y do Figma no frame (blocos em 182, 1926, 3068, 4228, 5144, 5516).
"""
import pathlib
from playwright.sync_api import sync_playwright

H = 0  # o frame novo ja inclui o HEAD (0..182)
STORY = 757.4  # story em video (9:16) inserido antes do .t-dados: 42,7 + 715 que o Figma nao tem
EXPECT = [
    (".hero-edicao",                22,  546),
    (".hero-autor",                 22,  585),
    (".hero-titulo",                22,  637),
    (".hero-olho",                  23,  755),
    (".caixa--intro",            -79.5,  902.29),
    (".caixa--intro p",             28,  951.7),
    (".retrato--menuci",            80, 1343.7),
    (".q-menuci p",                 20, 1633.33),
    (".q-menuci .legenda",          20, 1819.33),
    (".donmax",                   0.36, 1926),
    (".microfone",              117.36, 2151.67),
    (".caixa--palco",              -73, 2282.35),
    (".h-palco",                 20.36, 2343.8),
    (".t-palco",                 20.36, 2430.8),
    (".retrato--zanatta",        80.36, 2670.64),
    (".legenda--palco",             20, 2925.5),
    (".bl-efeito .h-sec",           19, 3079.14),
    (".bl-efeito .t-sec",           19, 3139.14),
    (".banda",                      -1, 3315.12),
    (".stat--1",                    -1, 3566.03),
    (".stat--2",                    -1, 3666.94),
    (".stat--3",                    -1, 3785.09),
    (".stat--4",                    -1, 3904.46),
    (".t-dados",                  18.6, 4085 + STORY),
    (".bl-cliente .h-sec",          19, 4237 + STORY),
    (".bl-cliente .t-sec",          19, 4324 + STORY),
    (".h-exp",                      19, 4674.76 + STORY),
    (".exp",                        19, 4781 + STORY),
    (".bl-gastar .h-sec",           19, 5173 + STORY),
    (".bl-gastar .t-sec",           19, 5260 + STORY),
    (".bar",                    -24.66, 5516 + STORY),
    (".pandeiro",                89.36, 5714.2 + STORY),
    (".caixa--custo",            -82.5, 5800.44 + STORY),
    (".h-custo",                    19, 5924 + STORY),
    (".t-cache",                    19, 5971 + STORY),
    (".custos",                     20, 6045 + STORY),
    (".t-fecho",                    19, 6515 + STORY),
    ("footer.foot",                  0, 6986 + STORY),
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
