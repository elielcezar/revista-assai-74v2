#!/usr/bin/env python
"""Exporta o protótipo para o Drupal 7.

    python drupal7/scripts/exportar.py

Lê as páginas listadas em drupal7/tema/revista2026/revista.json ("paginas") e
gera, em drupal7/build/:

  tema/revista2026/   o tema pronto para sites/all/themes/: os arquivos de
                      drupal7/tema/revista2026 + os CSS, JS, fontes e ícones
                      comuns, copiados do protótipo (casca, shell, scroll-fx)
  ftp/ed74/, ed73/    o que sobe por FTP para a pasta das edições: CSS, JS,
                      imagens, vídeos e fontes de cada página (só o que é usado)
  conteudos/          o corpo de cada conteúdo (<edicao>/<nome>.html), pronto
                      para colar, e CADASTRO.md com título, endereço, CSS e JS
                      de cada um; conteudos.json para o preview.php

O corpo leva só o miolo da página: no layout da #74, o que fica entre o
cabeçalho e o rodapé (o tema monta .page, cabeçalho, menu e rodapé); no shell
da #73, o <main> inteiro, com o menu trocado pelo marcador
<!-- revista2026:menu -->. Caminhos relativos viram endereços do FTP e links
entre páginas viram os aliases do revista.json.
"""
import html
import json
import pathlib
import posixpath
import re
import shutil
import sys
from urllib.parse import unquote

RAIZ = pathlib.Path(__file__).resolve().parents[2]
D7 = RAIZ / "drupal7"
TEMA_SRC = D7 / "tema" / "revista2026"
BUILD = D7 / "build"
CFG = json.loads((TEMA_SRC / "revista.json").read_text(encoding="utf-8"))

SITE = CFG["urls"]["site"].rstrip("/") + "/"
FTP = CFG["urls"]["ftp"].rstrip("/")

# arquivos do protótipo que viram parte do tema (destino no tema: origem)
TEMA_COMUNS = {
    "css/base.css": "css/base.css",
    "css/shell.css": "css/shell.css",
    "css/shell-desktop.css": "css/shell-desktop.css",
    "css/revista-73-shell.css": "73/css/revista-73-shell.css",
    "js/shell.js": "js/shell.js",
    "js/shell-desktop.js": "js/shell-desktop.js",
    "js/scroll-fx.js": "js/scroll-fx.js",
    "js/vendor/qrcode-generator.min.js": "js/vendor/qrcode-generator.min.js",
    "js/revista-73-menu.js": "73/js/revista-73-menu.js",
    "assets/imgLogoHead.svg": "assets/imgLogoHead.svg",
    "assets/imgGroup.svg": "assets/imgGroup.svg",
    "assets/imgGroup2.svg": "assets/imgGroup2.svg",
    "assets/imgGroup8650.svg": "assets/imgGroup8650.svg",
    "assets/imgGroup8651.svg": "assets/imgGroup8651.svg",
    "assets/imgVector1.svg": "assets/imgVector1.svg",
    "assets/imgVector2.svg": "assets/imgVector2.svg",
    "assets/shell/dt-logo-assai.png": "assets/shell/dt-logo-assai.png",
    **{f"assets/shell/rede-{r['icone']}.svg": f"assets/shell/rede-{r['icone']}.svg" for r in CFG["redes"]},
}
CSS_DO_TEMA = {v for k, v in TEMA_COMUNS.items() if k.startswith("css/")}
JS_DO_TEMA = {v for k, v in TEMA_COMUNS.items() if k.startswith("js/")}
LOGO_PADRAO = "assets/imgLogoHead.svg"

avisos = []
copias = {}          # destino em build/ftp -> origem no protótipo


def aviso(pagina, msg):
    avisos.append(f"{pagina}: {msg}")


# ---------------------------------------------------------------- caminhos

def partir(ref):
    m = re.match(r"^([^?#]*)(.*)$", ref, re.S)
    return m.group(1), m.group(2)


def externo(caminho):
    return (not caminho or caminho.startswith(("/", "#"))
            or re.match(r"^[a-z][a-z0-9+.-]*:", caminho, re.I) is not None)


def origens():
    """(origem, edicao) com as pastas específicas antes da raiz ("")."""
    pares = [(o, ed) for ed, d in CFG["edicoes"].items() for o in d["origens"]]
    return sorted(pares, key=lambda p: p[0] == "")


def destino(alvo):
    """arquivo do protótipo -> (edicao, caminho dentro da pasta da edição)."""
    for origem, ed in origens():
        if origem == "":
            return ed, alvo
        if alvo.startswith(origem + "/"):
            return ed, alvo[len(origem) + 1:]
    raise AssertionError(alvo)


def url_ftp(alvo):
    """endereço no FTP (mantém a codificação %20 do original no link; o arquivo
    copiado leva o nome decodificado, que é o que o servidor procura)."""
    ed, rel = destino(alvo)
    pasta = CFG["edicoes"][ed]["pasta"]
    copias[unquote(f"{pasta}/{rel}")] = unquote(alvo)
    return f"{FTP}/{pasta}/{rel}"


def seguir_stub(alvo):
    """endereços antigos (meta refresh) levam à página nova."""
    for _ in range(5):
        arq = RAIZ / alvo
        if alvo in CFG["paginas"] or not arq.exists():
            return alvo
        m = re.search(r'http-equiv="refresh"\s+content="\d+;\s*url=([^"]+)"', arq.read_text(encoding="utf-8"))
        if not m:
            return alvo
        alvo = posixpath.normpath(posixpath.join(posixpath.dirname(alvo), m.group(1)))
    return alvo


def resolver(ref, pasta_pagina, pagina, exigir=True):
    """caminho relativo do protótipo -> endereço no Drupal/FTP (None = manter)."""
    caminho, resto = partir(ref)
    if externo(caminho):
        return None
    alvo = posixpath.normpath(posixpath.join(pasta_pagina, caminho))
    if alvo.startswith(".."):
        aviso(pagina, f"caminho fora do protótipo: {ref}")
        return None
    if alvo.endswith(".html"):
        alvo = seguir_stub(alvo)
        if alvo not in CFG["paginas"]:
            aviso(pagina, f"link para página sem alias no revista.json: {ref}")
            return None
        return SITE + CFG["paginas"][alvo] + resto
    if not (RAIZ / unquote(alvo)).is_file():
        if exigir:
            aviso(pagina, f"arquivo não existe: {ref}")
        return None
    return url_ftp(alvo) + resto


# ---------------------------------------------------------------- HTML

ATRIB = re.compile(r'(\s(src|href|poster|srcset|data-[\w-]+|style)\s*=\s*)("([^"]*)"|\'([^\']*)\')', re.I)
TOKEN = re.compile(r'(?<![\w/.:%-])((?:\.\.?/)*[\w@%+-][\w@%+.-]*(?:/[\w@%+.-]+)+\.[A-Za-z0-9]{2,5}(?:\?[^"\'\s,)&]*)?)')
URL_CSS = re.compile(r'url\(\s*(["\']?)([^"\')]+)\1\s*\)')


def reescrever_html(s, pasta_pagina, pagina):
    def troca_valor(nome, valor):
        nome = nome.lower()
        if nome in ("src", "href", "poster"):
            novo = resolver(html.unescape(valor), pasta_pagina, pagina)
            return valor if novo is None else novo
        if nome == "srcset":
            partes = []
            for item in valor.split(","):
                bits = item.strip().split(None, 1)
                novo = resolver(bits[0], pasta_pagina, pagina) if bits else None
                partes.append(" ".join([novo or bits[0]] + bits[1:]) if bits else item)
            return ", ".join(partes)
        # data-* (ex.: lista JSON dos banners) e style: só o que for arquivo existente
        valor = URL_CSS.sub(lambda m: "url(" + m.group(1) + (resolver(m.group(2), pasta_pagina, pagina) or m.group(2)) + m.group(1) + ")", valor) \
            if nome == "style" else valor
        return TOKEN.sub(lambda m: resolver(m.group(1), pasta_pagina, pagina, exigir=False) or m.group(1), valor)

    def troca(m):
        aspas = '"' if m.group(4) is not None else "'"
        valor = m.group(4) if m.group(4) is not None else m.group(5)
        return m.group(1) + aspas + troca_valor(m.group(2), valor) + aspas

    s = ATRIB.sub(troca, s)
    # <style> dentro do corpo
    s = re.sub(r"(<style\b[^>]*>)(.*?)(</style>)",
               lambda m: m.group(1) + URL_CSS.sub(
                   lambda u: "url(" + u.group(1) + (resolver(u.group(2), pasta_pagina, pagina) or u.group(2)) + u.group(1) + ")",
                   m.group(2)) + m.group(3), s, flags=re.S | re.I)
    for sc in re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", s, re.S | re.I):
        if re.search(r"[\"'](\.\./)*(assets|css|js|fonts|7\d)/|\.html[\"'#?]", sc):
            aviso(pagina, "script embutido com caminho relativo (não reescrito): " + sc.strip()[:80])
    return s


def copiar_css(alvo, pagina):
    """copia um CSS da edição, ajustando url() e copiando o que ele usa."""
    ed, rel = destino(alvo)
    pasta_css = posixpath.dirname(f"{CFG['edicoes'][ed]['pasta']}/{rel}")
    texto = (RAIZ / alvo).read_text(encoding="utf-8")

    def troca(m):
        caminho, resto = partir(m.group(2))
        if externo(caminho):
            return m.group(0)
        origem = posixpath.normpath(posixpath.join(posixpath.dirname(alvo), caminho))
        if not (RAIZ / origem).is_file():
            aviso(pagina, f"{alvo}: url() para arquivo que não existe: {m.group(2)}")
            return m.group(0)
        url_ftp(origem)
        ed2, rel2 = destino(origem)
        novo = posixpath.relpath(f"{CFG['edicoes'][ed2]['pasta']}/{rel2}", pasta_css)
        return f"url({m.group(1)}{novo}{resto}{m.group(1)})"

    novo = URL_CSS.sub(troca, texto)
    dest = BUILD / "ftp" / f"{CFG['edicoes'][ed]['pasta']}/{rel}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(novo, encoding="utf-8", newline="")
    copias.pop(f"{CFG['edicoes'][ed]['pasta']}/{rel}", None)


def rotulo(trecho):
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", trecho)).strip())


def exportar_pagina(pagina):
    txt = (RAIZ / pagina).read_text(encoding="utf-8")
    pasta = posixpath.dirname(pagina)
    i_head = txt.index("</head>")
    head, resto = txt[:i_head], txt[i_head:]
    corpo = resto[resto.index(">", resto.index("<body")) + 1:resto.rindex("</body>")]

    meta = {"pagina": pagina}
    for ed, d in CFG["edicoes"].items():
        if any(o and pagina.startswith(o + "/") for o in d["origens"]):
            meta["edicao"] = ed
    meta.setdefault("edicao", CFG["edicao_atual"])

    titulo = rotulo(re.search(r"<title>(.*?)</title>", head, re.S).group(1))
    titulo = re.sub(r"\s*—\s*" + re.escape(CFG["titulo_sufixo"]) + r"\s*#\d+\s*$", "", titulo)
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', head)
    if m:
        meta["descricao"] = html.unescape(m.group(1))

    # CSS: os do tema saem; os da página vão para o campo de CSS
    css = []
    for tag in re.findall(r"<link\b[^>]*>", head, re.I):
        if not re.search(r'rel="stylesheet"', tag):
            continue
        href = re.search(r'href="([^"]+)"', tag).group(1)
        caminho, q = partir(href)
        if externo(caminho):
            if "fonts.googleapis.com" in href:
                meta["fontes"] = html.unescape(href)
            else:
                aviso(pagina, f"CSS externo ignorado: {href}")
            continue
        alvo = posixpath.normpath(posixpath.join(pasta, caminho))
        if alvo in CSS_DO_TEMA:
            continue
        copiar_css(alvo, pagina)
        css.append(url_ftp(alvo) + q)

    # JS: idem; GSAP vem do tema quando a página usa o scroll-fx
    js = []
    for tag in re.findall(r"<script\b[^>]*\bsrc=\"[^\"]+\"[^>]*>\s*</script>", txt, re.I):
        src = re.search(r'src="([^"]+)"', tag).group(1)
        caminho, q = partir(src)
        if "cdn.jsdelivr.net/npm/gsap" in src:
            if "SplitText" in src:
                meta["splittext"] = True
            continue
        if externo(caminho):
            aviso(pagina, f"JS externo ignorado: {src}")
            continue
        alvo = posixpath.normpath(posixpath.join(pasta, caminho))
        if alvo == "js/scroll-fx.js":
            meta["fx"] = True
        if alvo in JS_DO_TEMA:
            continue
        js.append(url_ftp(alvo) + q + (" defer" if re.search(r"\sdefer\b", tag) else ""))
    corpo = re.sub(r"[ \t]*(<!--(?:(?!-->).)*-->\s*)?<script\b[^>]*\bsrc=\"[^\"]+\"[^>]*>\s*</script>[ \t]*\r?\n?", "", corpo, flags=re.S | re.I)

    # anti-piscada; outros <style>/<script> do <head> vão para o começo do corpo
    m = re.search(r"<style>(\.fx-espera[^{]*)\{visibility:hidden\}</style>", head)
    if m:
        meta["espera"] = m.group(1)
    sem_gtm = re.sub(r"<!-- Google Tag Manager -->.*?<!-- End Google Tag Manager -->", "", head, flags=re.S)
    levar = []
    for bloco in re.findall(r"[ \t]*<(?:style|script)\b[^>]*>.*?</(?:style|script)>", sem_gtm, re.S | re.I):
        if "fx-espera" in bloco or re.search(r"<script\b[^>]*\bsrc=", bloco):
            continue
        levar.append(bloco.strip())
        if bloco.strip().startswith("<script"):
            aviso(pagina, "script embutido do <head> foi para o corpo")

    # casca do desktop: o tema gera
    corpo = re.sub(r"<!-- =+ CASCA DESKTOP.*?/CASCA DESKTOP =+ -->", "", corpo, flags=re.S)

    if re.search(r'<div class="page[ "]', corpo):
        meta["layout"] = "74"
        m = re.search(r'<div class="page( [^"]*)?">', corpo)
        if m.group(1):
            meta["classe"] = m.group(1).strip()
        a = corpo.index('<header class="head"')
        b = corpo.index("</header>", a) + len("</header>")
        cab = corpo[a:b]
        ativo = re.search(r'class="is-active"><a[^>]*>(.*?)</a>', cab)
        if ativo:
            meta["ativo"] = rotulo(ativo.group(1))
        logo = re.search(r'class="head-logo" src="([^"]+)"', cab).group(1)
        if posixpath.normpath(posixpath.join(pasta, partir(logo)[0])) != LOGO_PADRAO:
            meta["logo"] = resolver(logo, pasta, pagina)
        f = corpo.find("<!-- ============ COMPONENTE RODAPE", b)
        if f < 0:
            f = corpo.index('<footer class="foot"', b)
        miolo = corpo[b:f].strip("\r\n")
        fim = corpo.index("</footer>", f) + len("</footer>")
        sobra = corpo[:m.start()] + corpo[corpo.index("</div>", fim) + 6:]
    elif "<main" in corpo:
        meta["layout"] = "73"
        a = corpo.index("<main")
        b = corpo.rindex("</main>") + len("</main>")
        miolo = corpo[a:b]
        ativo = re.search(r'<a class="[^"]*\bis-active\b[^"]*"[^>]*data-menu-item[^>]*>(.*?)</a>', miolo)
        if ativo:
            meta["ativo"] = rotulo(ativo.group(1))
        miolo, n = re.subn(r'(<div class="head-menu-inner">)(.*?)(\s*</div>)',
                           lambda m: m.group(1) + "\n<!-- revista2026:menu -->" + m.group(3), miolo, count=1, flags=re.S)
        if not n:
            aviso(pagina, "menu (.head-menu-inner) não encontrado")
        sobra = corpo[:a] + corpo[b:]
    else:
        aviso(pagina, "não achei .page nem <main>; página pulada")
        return None

    # o que sobra fora do miolo (scripts embutidos depois do <main>) vai junto, no fim
    sobra = re.sub(r"<!--.*?-->", "", sobra, flags=re.S).strip()
    if re.sub(r"<script\b[^>]*>.*?</script>", "", sobra, flags=re.S | re.I).strip():
        aviso(pagina, f"conteúdo fora do miolo (mantido no fim do corpo): {sobra[:120]!r}")
    depois = [sobra] if sobra else []

    miolo = reescrever_html("\n".join(levar + [miolo] + depois), pasta, pagina)
    if meta.get("espera") and not meta.get("fx"):
        aviso(pagina, "anti-piscada sem scroll-fx")

    cab_json = json.dumps(meta, ensure_ascii=False, indent=1).replace("--", "-\\u002d")
    texto = f"<!-- revista2026 {cab_json} -->\n{miolo}\n"
    nome = f"{meta['edicao']}/{posixpath.splitext(posixpath.basename(pagina))[0]}.html"
    dest = BUILD / "conteudos" / nome
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(texto, encoding="utf-8", newline="\n")

    return {"pagina": pagina, "edicao": meta["edicao"], "layout": meta["layout"],
            "alias": CFG["paginas"][pagina], "titulo": titulo, "corpo": f"conteudos/{nome}",
            "css": css, "js": js}


# ---------------------------------------------------------------- tema

def montar_tema():
    dest = BUILD / "tema" / "revista2026"
    shutil.copytree(TEMA_SRC, dest)
    for alvo, origem in TEMA_COMUNS.items():
        d = dest / alvo
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / origem, d)
        if alvo.endswith(".css"):
            # fontes que o CSS comum usa (o tema repete a estrutura css/ fonts/ da raiz)
            for m in URL_CSS.finditer((RAIZ / origem).read_text(encoding="utf-8")):
                caminho = partir(m.group(2))[0]
                if externo(caminho):
                    continue
                f = posixpath.normpath(posixpath.join(posixpath.dirname(origem), caminho))
                g = posixpath.normpath(posixpath.join(posixpath.dirname(alvo), caminho))
                assert not g.startswith(".."), (origem, caminho)
                (dest / g).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(RAIZ / f, dest / g)


# ---------------------------------------------------------------- saída

def cadastro(itens):
    l = ["# Cadastro dos conteúdos", "",
         "Gerado por `drupal7/scripts/exportar.py`. Para cada conteúdo do tipo Revista 2026:",
         "", "- **Título** e **Endereço (alias)** como abaixo;",
         "- **Corpo**: o arquivo indicado, inteiro (inclusive o comentário `revista2026` da primeira linha),",
         "  num formato de texto **sem editor visual e sem filtros**;",
         "- **CSS** e **JS**: um endereço por item, na ordem.", ""]
    for ed in sorted({i["edicao"] for i in itens}, reverse=True):
        l += [f"## Edição #{ed}", ""]
        for i in (x for x in itens if x["edicao"] == ed):
            l += [f"### {i['titulo']}", "",
                  f"- Endereço: `{i['alias']}`",
                  f"- Corpo: `build/{i['corpo']}` (layout {i['layout']}; origem `{i['pagina']}`)"]
            l += [f"- CSS: `{u}`" for u in i["css"]] or ["- CSS: —"]
            l += [f"- JS: `{u}`" for u in i["js"]] or ["- JS: —"]
            l.append("")
    return "\n".join(l)


def main():
    if BUILD.exists():
        shutil.rmtree(BUILD)
    (BUILD / "conteudos").mkdir(parents=True)

    itens = [i for i in (exportar_pagina(p) for p in CFG["paginas"]) if i]

    for dest, origem in sorted(copias.items()):
        d = BUILD / "ftp" / dest
        if d.exists():
            continue
        d.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(RAIZ / origem, d)
    montar_tema()

    (BUILD / "conteudos" / "conteudos.json").write_text(
        json.dumps(itens, ensure_ascii=False, indent=1), encoding="utf-8")
    (BUILD / "conteudos" / "CADASTRO.md").write_text(cadastro(itens), encoding="utf-8")

    arquivos = [p for p in (BUILD / "ftp").rglob("*") if p.is_file()]
    mb = sum(p.stat().st_size for p in arquivos) / 1e6
    print(f"{len(itens)} conteúdos, {len(arquivos)} arquivos para o FTP ({mb:.1f} MB)")
    for a in avisos:
        print("AVISO", a)
    return 1 if any("não existe" in a or "pulada" in a for a in avisos) else 0


if __name__ == "__main__":
    sys.exit(main())
