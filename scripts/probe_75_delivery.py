#!/usr/bin/env python
"""Mede a posicao real dos elementos da DELIVERY #75 contra as coordenadas do Figma.

    python scripts/probe_75_delivery.py

Figma: 6919:1041 (402 x 10905, HEAD de 182 incluso). Blocos empilhados:
head 0 | hero 182 | fraude 1242 | plataformas 3125 | barata 5008 |
agir 6846 | direitos 8690 | IA 9874 | rodape 10789. Top esperado = y do bloco + y interno.
"""
import pathlib
from playwright.sync_api import sync_playwright

B1, B2, B3, B4, B5, B6, B7 = 182, 1242, 3125, 5008, 6846, 8690, 9874
EXPECT = [
    (".hero-golpes",         21, B1 + 48.57),
    (".hero-com",           25, B1 + 129.79),
    (".hero-olho",          24, B1 + 198.11),
    (".coxinha--1",         71, B1 + 285.46),
    (".coxinha--2",        179, B1 + 309.7),
    (".hero-edicao",       None, B1 + 516),
    (".t-hero",             20, B1 + 612.03),
    (".mosca",             165, B1 + 966.91),
    (".foto-golpe",          0, B2 + 32.91),
    (".h-fraude",           None, B2 + 403.65),
    (".etapas",             20, B2 + 494.83),
    (".h-contestacao",      20, B2 + 1375.17),
    (".mancha",             91, B2 + 1710.37),
    (".caixa--ifood",        0, B3 + 52.99),
    (".h-plat",             20, B3 + 102.42),
    (".t-ifood",            20, B3 + 151.42),
    (".caixa--ifood .retrato", 61, B3 + 781.39),
    (".q-ifood",            21, B3 + 1123.12),
    (".caixa--99",           0, B3 + 1502.84),
    (".t-99",               20, B3 + 1659.2),
    (".h-caso",             20, B4 + 69),
    (".foto-chat",          20, B4 + 287.89),
    (".t-caso-2",           20, B4 + 607.77),
    (".foto-pizza",         19, B4 + 724.34),
    (".t-caso-3",           20, B4 + 1069.98),
    (".caixa--beatriz .retrato", 61, B4 + 1259.79),
    (".caixa--beatriz",      0, B4 + 1390.14),
    (".t-beatriz",          20, B4 + 1656.9),
    (".h-agir",             20, B5 + 59),
    (".t-ideia",            20, B5 + 801.5),
    (".arco--1",           -24, B5 + 1048.07),
    (".arco--2",           -24, B5 + 1277.57),
    (".arco--3",           -24, B5 + 1452.72),
    (".caixa--recomenda",   -3, B5 + 1615),
    (".h-direitos",         None, B6 + 45),
    (".barra",               0, B6 + 103.56),
    (".t-direitos",         19, B6 + 196.62),
    (".barra--2",            0, B6 + 717.7),
    (".t-direitos--2",      19, B6 + 810.76),
    (".prato--a",          187, B7 + 16.25),
    (".prato--b",           11, B7 + 52.6),
    (".h-ia",               20, B7 + 242),
    (".t-ia-1",             19, B7 + 302.78),
    (".btn-ia",             20, B7 + 491.02),
    (".t-ia-2",             19, B7 + 581.25),
    ("footer.foot",          0, 10789),
]

JS = """(sels) => sels.map(s => { const e = document.querySelector(s); if (!e) return null;
  const r = e.getBoundingClientRect(); return [r.left, r.top + scrollY, r.width, r.height]; })"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 402, "height": 900})
    pg.route("**/*google*/**", lambda r: r.abort())
    pg.goto(pathlib.Path("75/delivery.html").resolve().as_uri(), wait_until="load")
    pg.evaluate("document.fonts.ready")
    pg.wait_for_timeout(600)
    pg.evaluate("document.querySelector('.casca') && (document.querySelector('.casca').style.display='none')")
    res = pg.evaluate(JS, [s for s, _, _ in EXPECT])
    ruins = 0
    for (s, x, y), r in zip(EXPECT, res):
        if r is None:
            print(f"{s:26} AUSENTE"); ruins += 1; continue
        dy = r[1] - y; dx = 0 if x is None else r[0] - x
        flag = "  <<<" if abs(dy) > 3 or abs(dx) > 3 else ""
        ruins += bool(flag)
        print(f"{s:26} x {r[0]:7.1f} ({dx:+4.0f})  y {r[1]:8.1f} esp {y:8.1f} ({dy:+5.0f})  {r[2]:.0f}x{r[3]:.0f}{flag}")
    print(f"altura da pagina: {pg.evaluate('document.documentElement.scrollHeight')} (Figma 10905)")
    print(f"fora de posicao: {ruins}/{len(EXPECT)}")
    b.close()
