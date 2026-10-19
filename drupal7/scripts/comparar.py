#!/usr/bin/env python
"""Compara cada página do protótipo com a mesma página montada pelo tema.

    python drupal7/scripts/exportar.py
    php drupal7/scripts/preview.php
    python drupal7/scripts/comparar.py [alias ...]

Sobe dois servidores locais: o protótipo (a raiz do repositório) e um "site"
que imita o Drupal: o tema em /sites/all/themes/revista2026, o FTP no endereço
de urls.ftp do revista.json e cada conteúdo no seu alias (build/preview).

Para cada página: print de página inteira em 402px e da tela do desktop
(1920x945, com a casca), com os efeitos do scroll-fx bloqueados (como nos
probes), vídeos e GIFs pintados de cinza (o quadro varia entre prints; a
caixa continua sendo comparada) e sorteio fixo dos banners. Confere também
os links (o link do protótipo traduzido para o alias tem de bater), os
arquivos que não carregaram (404) e os erros de JavaScript.

Saída: build/comparacao/ (prints e diferenças) e o resumo no terminal.
"""
import functools
import http.server
import json
import pathlib
import posixpath
import re
import sys
import threading
from urllib.parse import unquote, urlsplit

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import exportar  # noqa: E402  (destino e seguir_stub: a mesma tradução da exportação)
BUILD = RAIZ / "drupal7" / "build"
CFG = json.loads((BUILD / "tema" / "revista2026" / "revista.json").read_text(encoding="utf-8"))
ITENS = json.loads((BUILD / "conteudos" / "conteudos.json").read_text(encoding="utf-8"))
SAIDA = BUILD / "comparacao"
FTP = CFG["urls"]["ftp"].rstrip("/") + "/"
TEMA = "/sites/all/themes/revista2026/"
P_PROTO, P_SITE = 8701, 8702


class Site(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        p = unquote(urlsplit(path).path)
        if p.startswith(TEMA):
            return str(BUILD / "tema" / "revista2026" / p[len(TEMA):])
        if p.startswith(FTP):
            return str(BUILD / "ftp" / p[len(FTP):])
        return str(BUILD / "preview" / p.strip("/") / "index.html")

    def log_message(self, *a):
        pass


class Proto(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Servidor(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        pass  # o navegador corta o download de vídeo no meio: não é erro


def servir(handler, porta):
    srv = Servidor(("127.0.0.1", porta), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def traduz(h):
    """link do protótipo (já como caminho do servidor) -> o que o tema deve ter."""
    if not h.startswith("/"):
        return h
    caminho, _, frag = h.partition("#")
    alvo = unquote(caminho.lstrip("/"))
    if alvo.endswith(".html"):
        alvo = exportar.seguir_stub(alvo)
        novo = "/" + CFG["paginas"].get(alvo, alvo)
    else:
        ed, rel = exportar.destino(caminho.lstrip("/"))
        novo = FTP + CFG["edicoes"][ed]["pasta"] + "/" + rel
    return novo + ("#" + frag if frag else "")


PREPARA = """async () => {
  await Promise.all(Array.from(document.images).map(i => i.decode().catch(() => {})));
  document.documentElement.classList.remove('fx-espera');
  // vídeos: espera o primeiro quadro e para no início (os dois lados iguais)
  await Promise.all(Array.from(document.querySelectorAll('video')).map(v => new Promise(ok => {
    const fim = () => { try { v.pause(); } catch (e) {} ok(); };
    setTimeout(fim, 6000);
    const zera = () => { try { v.pause(); v.currentTime = 0; } catch (e) {} v.addEventListener('seeked', fim, {once: true}); setTimeout(fim, 1500); };
    if (v.readyState >= 2) zera(); else v.addEventListener('loadeddata', zera, {once: true});
  })));
  document.getAnimations().forEach(a => { try { if (isFinite(a.effect.getComputedTiming().endTime)) a.finish(); } catch (e) {} });
  const s = document.createElement('style');
  s.textContent = '*,*::before,*::after{animation-play-state:paused!important;animation-delay:0s!important;transition:none!important;caret-color:transparent!important}'
    + '.casca-qr-img{visibility:hidden!important}'
    // o quadro do vídeo e do GIF varia de um print para outro: compara só a caixa
    + 'video,img[src*=".gif"]{filter:brightness(0) invert(.5)!important}';
  document.head.appendChild(s);
}"""

LINKS = """() => Array.from(document.querySelectorAll('a[href]')).map(a => {
  const h = a.getAttribute('href');
  if (/^(https?:)?\\/\\//.test(h) || h.startsWith('#') || h.startsWith('mailto:')) return h;
  const u = new URL(a.href); return u.pathname + u.hash;
})"""


def abrir(browser, url, largura, altura, problemas):
    ctx = browser.new_context(viewport={"width": largura, "height": altura}, device_scale_factor=1)
    ctx.add_init_script("Math.random = () => 0;")
    ctx.route(re.compile(r"googletagmanager|google-analytics|doubleclick|/scroll-fx\.js|cdn\.jsdelivr\.net/npm/gsap"),
              lambda r: r.abort())
    page = ctx.new_page()
    page.on("pageerror", lambda e: problemas.append(f"erro JS: {e}"))
    page.on("response", lambda r: r.status >= 400 and problemas.append(f"{r.status} {r.url}"))
    page.goto(url, wait_until="load", timeout=60000)
    try:
        page.evaluate("document.fonts.ready")
    except Exception:
        pass
    page.wait_for_timeout(1500)
    page.evaluate(PREPARA)
    page.wait_for_timeout(300)
    return ctx, page


def diferenca(a, b, dest):
    ia, ib = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    if ia.size != ib.size:
        w, h = max(ia.width, ib.width), max(ia.height, ib.height)
        na, nb = Image.new("RGB", (w, h), "white"), Image.new("RGB", (w, h), "white")
        na.paste(ia), nb.paste(ib)
        ia, ib = na, nb
    d = ImageChops.difference(ia, ib).convert("L").point(lambda v: 255 if v > 24 else 0)
    caixa = d.getbbox()
    n = sum(d.histogram()[255:])
    if n:
        Image.composite(Image.new("RGB", ia.size, "red"), ia.point(lambda v: v // 3 + 170), d).save(dest)
    return n, caixa


def main():
    filtro = set(sys.argv[1:])
    itens = [i for i in ITENS if not filtro or i["alias"] in filtro or i["pagina"] in filtro]
    SAIDA.mkdir(parents=True, exist_ok=True)
    servir(functools.partial(Proto, directory=str(RAIZ)), P_PROTO)
    servir(Site, P_SITE)

    falhas = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for item in itens:
            nome = item["alias"].replace("/", "_")
            url_p = f"http://127.0.0.1:{P_PROTO}/{item['pagina']}"
            url_s = f"http://127.0.0.1:{P_SITE}/{item['alias']}"
            linhas = []

            for largura, altura, inteira in ((402, 900, True), (1920, 945, False)):
                problemas_p, problemas_s = [], []
                shots = []
                for url, prob, lado in ((url_p, problemas_p, "proto"), (url_s, problemas_s, "d7")):
                    ctx, page = abrir(browser, url, largura, altura, prob)
                    arq = SAIDA / f"{nome}-{largura}-{lado}.png"
                    if inteira:
                        # a janela já na altura da página: o print de página inteira
                        # redimensiona a janela e dispara de novo os scripts que
                        # escutam resize (centralizar o menu da #73, parallax)
                        page.set_viewport_size({"width": largura, "height": page.evaluate("document.documentElement.scrollHeight")})
                        page.wait_for_timeout(1000)
                    page.screenshot(path=str(arq), full_page=inteira)
                    if largura == 402:
                        links = page.evaluate(LINKS)
                        shots.append((arq, links, page.evaluate("document.documentElement.scrollHeight")))
                    else:
                        shots.append((arq, None, None))
                    ctx.close()
                n, caixa = diferenca(shots[0][0], shots[1][0], SAIDA / f"{nome}-{largura}-diff.png")
                if n:
                    linhas.append(f"  {largura}px: {n} px diferentes em {caixa}")
                if largura == 402:
                    if shots[0][2] != shots[1][2]:
                        linhas.append(f"  altura: protótipo {shots[0][2]} x tema {shots[1][2]}")
                    esperado = [traduz(h) for h in shots[0][1]]
                    if esperado != shots[1][1]:
                        for a, b in zip(esperado + [None] * len(shots[1][1]), shots[1][1] + [None] * len(esperado)):
                            if a != b:
                                linhas.append(f"  link: protótipo {a} -> tema {b}")
                for x in sorted(set(problemas_s) - set(problemas_p)):
                    linhas.append(f"  {largura}px tema: {x}")

            status = "OK " if not linhas else "DIF"
            falhas += bool(linhas)
            print(f"{status} {item['pagina']}  ->  /{item['alias']}")
            for l in linhas[:12]:
                print(l)
            if len(linhas) > 12:
                print(f"  ... +{len(linhas) - 12}")
        browser.close()
    print(f"\n{len(itens) - falhas}/{len(itens)} iguais. Prints em {SAIDA.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
