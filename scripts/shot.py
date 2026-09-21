#!/usr/bin/env python
"""Screenshot full-page de um HTML local (ou URL) numa largura exata.

    python scripts/shot.py 74/principal.html reference/render.png 402
"""
import sys, os, pathlib
import re
from playwright.sync_api import sync_playwright

FREEZE = """
*, *::before, *::after {
  animation-play-state: paused !important;
  animation-delay: 0s !important;
  transition: none !important;
}
"""


def main():
    src = sys.argv[1]
    out = sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 402

    url = src if "://" in src else pathlib.Path(src).resolve().as_uri()
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 900},
                                device_scale_factor=1)
        # QA nao dispara pageview no Analytics (tag GTM das paginas)
        page.route(re.compile(r"googletagmanager|google-analytics|doubleclick"), lambda r: r.abort())
        page.goto(url, wait_until="networkidle")
        # captura so o frame do Figma: esconde o invólucro (css/shell.css)
        page.add_style_tag(content=".dt-sidebar { display: none !important; }")
        # animacoes finitas (ex.: queda dos icones da EXPEDIENTE) vao para o estado final
        page.evaluate("""() => document.getAnimations().forEach(a => {
            try { if (isFinite(a.effect.getComputedTiming().endTime)) a.finish(); } catch (e) {} })""")
        page.add_style_tag(content=FREEZE)
        page.wait_for_timeout(600)
        try:
            page.evaluate("document.fonts.ready")
        except Exception:
            pass
        page.wait_for_timeout(200)
        page.screenshot(path=out, full_page=True)
        h = page.evaluate("document.documentElement.scrollHeight")
        browser.close()

    print(f"{out}  width={width}  scrollHeight={h}")


if __name__ == "__main__":
    main()
