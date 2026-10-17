#!/usr/bin/env python
"""Mede a posicao real dos elementos da DELIVERY #75 contra as coordenadas do Figma.

    python scripts/probe_75_delivery.py

Figma: 6931:4097 (arquivo aquTnQHLWwiogtzEAG9qyp, 402 x 10905, HEAD de 182 incluso).
Os 7 blocos "DELIVERY" do Figma comecam em 182, 1242, 3125, 5008, 6846, 8690 e 9874.
O banner rotativo (.adbox, 419px + 50 de folga) nao existe no Figma: entra depois das
etapas e empurra o que vem abaixo em AD. O probe bloqueia o delivery.js para o banner
nao ser sorteado.
"""
import pathlib
from playwright.sync_api import sync_playwright

AD = 469   # banner rotativo: 419 + 50
# (seletor, x, y no Figma, depois do banner?)
EXPECT = [
    (".mosca",             165,  1148.91, 0),   # 182 + 966.91
    (".foto-golpe",          0,  1274.91, 0),   # 1242 + 32.91
    (".h-fraude",            0,  1645.65, 0),   # 1242 + 403.65
    (".etapas",             20,  1736.83, 0),   # 1242 + 494.83
    (".h-contestacao",      20,  2617.17, 1),   # 1242 + 1375.17
    (".t-ifood",            20,  3276.42, 1),   # 3125 + 151.42
    (".t-99",               20,  4784.2,  1),   # 3125 + 1659.2
    (".h-caso",             20,  5077,    1),   # 5008 + 69
    (".h-agir",             20,  6905,    1),   # 6846 + 59
    (".h-direitos",          0,  8735,    1),   # 8690 + 45 (centralizado na coluna)
    (".h-ia",               20, 10116,    1),   # 9874 + 242
    (".btn-ia",             20, 10365.02, 1),   # 9874 + 491.02
    ("footer.foot",          0, 10789,    1),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.route("**/scroll-fx.js*", lambda r: r.abort())
    pg.route("**/delivery.js*", lambda r: r.abort())
    pg.goto(pathlib.Path("75/delivery.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(800)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [e[0] for e in EXPECT])
    ruins = 0
    for (s, x, y, dep), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:22} AUSENTE"); ruins += 1; continue
        alvo = y + (AD if dep else 0)
        dy = r[1] - alvo; dx = r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:22} x {r[0]:7.1f} ({dx:+5.1f})  y {r[1]:7.1f} esp {alvo:8.1f} ({dy:+5.1f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 10905 + banner {AD})")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
