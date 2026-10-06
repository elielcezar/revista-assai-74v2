#!/usr/bin/env python
"""Casca do desktop: gera o markup em todas as páginas a partir de um modelo só.

A casca (lateral esquerda com logo, edição, menu e "Edições anteriores";
lateral direita com redes sociais e QR) é igual em todas as páginas das
edições #74 e #73. Muda só:
  - o prefixo dos caminhos (raiz: "", 74/ e 73/: "../");
  - o texto da edição (73/: #73; o resto: #74);
  - o item ativo do menu;
  - EDITORIAL, PARCEIROS e EXPEDIENTE, que nas páginas da 73/ abrem as
    versões da própria 73/.

O script substitui, em cada página, o bloco entre <!-- CASCA ... --> e
<!-- /CASCA --> (ou, na primeira vez, a antiga <aside class="dt-sidebar">
com os comentários INVÓLUCRO em volta, se houver), e garante no <head> o
css/shell-desktop.css e antes do </body> o js/shell-desktop.js.

    python scripts/shell_sync.py                 # todas as páginas
    python scripts/shell_sync.py index.html      # só as indicadas
    python scripts/shell_sync.py --check         # só lista o que mudaria

Trava: se o menu gerado para uma página não tiver os mesmos itens, na mesma
ordem e com os mesmos links do menu que ela tem hoje, a página não é gravada
e a diferença é listada (--forcar grava assim mesmo, para quando a mudança
de menu for intencional).

Estilo em css/shell-desktop.css; QR em js/shell-desktop.js.
"""
import sys, re, glob, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent

EDICOES = {
    "73": ("Edição #73", "Jul-Ago/2026"),
    None: ("Edição #74", "Setembro/2026"),
}
EDICOES_ANTERIORES = "https://www.assai.com.br/revistas"

# (rótulo, página na raiz, cor do traço, abre na própria edição)
MENU = [
    ("CAPA",              "index.html",                "#000000", False),
    ("PRINCIPAL",         "categoria-principal.html",  "#004696", False),
    ("GESTÃO",            "categoria-gestao.html",     "#f0051e", False),
    ("MKT DIGITAL",       "categoria-mkt-digital.html", "#ff7300", False),
    ("PRODUTO",           "categoria-produto.html",    "#ffaa00", False),
    ("CONSUMIDOR",        "categoria-consumidor.html", "#ffdc00", False),
    ("DELIVERY",          "categoria-delivery.html",   "#532f82", False),
    ("NOVO NEGÓCIO",      "categoria-novo-negocio.html", "#b40082", False),
    ("ACADEMIA ASSAÍ",    "categoria-academia.html",   "#ff5564", False),
    ("NOTÍCIAS DO ASSAÍ", "categoria-noticias.html",   "#0082c8", False),
    ("EDITORIAL",         "editorial.html",            "#666666", True),
    ("PARCEIROS",         "parceiros.html",            "#666666", True),
    ("EXPEDIENTE",        "expediente.html",           "#666666", True),
]

# (nome, endereço, ícone, largura, altura)
REDES = [
    ("Facebook",  "https://www.facebook.com/assaiatacadistaoficial",  "facebook",  17, 32),
    ("Instagram", "https://www.instagram.com/assaiatacadistaoficial", "instagram", 33, 33),
    ("X",         "https://twitter.com/assaioficial",                 "x",         32, 39),
    ("TikTok",    "https://www.tiktok.com/@assaiatacadistaoficial",   "tiktok",    31, 40),
    ("YouTube",   "https://www.youtube.com/assaioficial",             "youtube",   36, 30),
    ("LinkedIn",  "https://www.linkedin.com/company/3624827",         "linkedin",  31, 31),
]

# itens que só existem no menu de uma página (entram antes do item indicado)
EXTRAS = {
    "73/download.html": [(("DOWNLOAD", "download.html", "#004696", True), "EDITORIAL")],
}

# páginas cujo item ativo não dá para ler do markup atual
ATIVO_FIXO = {"73/expediente.html": "EXPEDIENTE"}

ABRE = "<!-- ============ CASCA DESKTOP: gerada por scripts/shell_sync.py — não edite aqui ============ -->"
FECHA = "<!-- ============ /CASCA DESKTOP ============ -->"


def menu_da_pagina(rel):
    menu = list(MENU)
    for item, antes_de in EXTRAS.get(rel, []):
        menu.insert([r for r, *_ in menu].index(antes_de), item)
    return menu


def links_do_menu(bloco):
    """[(href, rótulo)] do <nav> de um bloco de casca/sidebar, sem comentários."""
    nav = re.search(r'<nav\b.*?</nav>', re.sub(r'<!--.*?-->', '', bloco, flags=re.S), re.S)
    return re.findall(r'<a\b[^>]*?\bhref="([^"]*)"[^>]*>\s*([^<]+?)\s*</a>', nav.group(0)) if nav else []


def casca(pasta, ativo, menu=MENU):
    p = "../" if pasta else ""
    num, data = EDICOES.get(pasta, EDICOES[None])
    itens = []
    for rot, alvo, cor, local in menu:
        href = alvo if (local and pasta == "73") else p + alvo
        ativa = ' class="is-active" aria-current="page"' if rot == ativo else ""
        # os links do menu sempre abrem em nova aba
        itens.append(f'      <a href="{href}" target="_blank" rel="noopener" style="--mc:{cor}"{ativa}>{rot}</a>')
    redes = [
        f'      <li><a href="{url}" target="_blank" rel="noopener" aria-label="Assaí no {nome}">'
        f'<img src="{p}assets/shell/rede-{ic}.svg" alt="" width="{w}" height="{h}"></a></li>'
        for nome, url, ic, w, h in REDES
    ]
    return "\n".join([
        ABRE,
        '<div class="casca">',
        '  <aside class="casca-esq" aria-label="Navegação da revista">',
        '    <a class="casca-logo" href="https://www.assai.com.br" target="_blank" rel="noopener">'
        f'<img src="{p}assets/shell/dt-logo-assai.png" alt="Assaí Atacadista" width="124" height="124"></a>',
        f'    <p class="casca-edicao">{num}<br>{data}</p>',
        '    <div class="casca-menu">',
        '      <nav class="casca-nav" aria-label="Seções da revista">',
        *["  " + i for i in itens],
        '      </nav>',
        f'      <a class="casca-pilula" href="{EDICOES_ANTERIORES}" target="_blank" rel="noopener">Edições anteriores</a>',
        '    </div>',
        '  </aside>',
        '  <aside class="casca-dir" aria-label="Assaí nas redes sociais">',
        '    <p class="casca-siga">Siga o Assaí</p>',
        '    <ul class="casca-redes">',
        *redes,
        '    </ul>',
        '    <div class="casca-qr">',
        '      <p class="casca-pilula">Ler no celular</p>',
        '      <div class="casca-qr-img" role="img" aria-label="QR code com o endereço desta página"></div>',
        '    </div>',
        '  </aside>',
        '</div>',
        FECHA,
    ])


def rotulo_ativo(bloco):
    m = re.search(r'<a\b[^>]*\bis-active\b[^>]*>\s*([^<]+?)\s*</a>', bloco)
    return m.group(1) if m else None


def versao(texto):
    # a maior versao 74-NN da pagina (os links nao sobem todos juntos)
    nums = [int(n) for n in re.findall(r"[?]v=74-(\d+)", texto)]
    return f"74-{max(nums)}" if nums else None


def sincroniza(rel, ver, so_checa, forcar=False):
    arq = RAIZ / rel
    with open(arq, encoding="utf-8", newline="") as f:
        s = f.read()
    nl = "\r\n" if "\r\n" in s else "\n"   # mantém a quebra de linha do arquivo
    pasta = rel.split("/")[0] if "/" in rel else None

    novo_re = re.compile(re.escape(ABRE) + r".*?" + re.escape(FECHA), re.S)
    velho_re = re.compile(
        r'(?:<!--[^>]*INVÓLUCRO[^>]*-->\s*)?<aside class="dt-sidebar".*?</aside>(?:\s*<!--[^>]*/INVÓLUCRO[^>]*-->)?', re.S)
    m = novo_re.search(s) or velho_re.search(s)
    if not m:
        return None

    menu = menu_da_pagina(rel)
    ativo = ATIVO_FIXO.get(rel, rotulo_ativo(m.group(0)))
    if ativo not in [r for r, *_ in menu]:
        ativo = None
    bloco = casca(pasta, ativo, menu)

    # trava: o menu gerado tem de ter os mesmos itens, na mesma ordem e com os
    # mesmos links do menu que a página tem hoje
    antes, depois = links_do_menu(m.group(0)), links_do_menu(bloco)
    if antes != depois and not forcar:
        print(f"MENU DIVERGE, não gravei: {rel}")
        for a, d in zip(antes + [None] * len(depois), depois + [None] * len(antes)):
            if a != d:
                print(f"    hoje: {a}  ->  gerado: {d}")
        return "divergente"

    t = s[:m.start()] + bloco.replace("\n", nl) + s[m.end():]

    p = "../" if pasta else ""
    css = f'<link rel="stylesheet" href="{p}css/shell-desktop.css?v={ver}">'
    js = f'<script src="{p}js/shell-desktop.js?v={ver}"></script>'
    if "shell-desktop.css" in t:
        t = re.sub(r'<link[^>]*shell-desktop\.css[^>]*>', css, t)
    else:
        t = t.replace("</head>", f"<!-- casca do desktop: por último -->{nl}{css}{nl}</head>", 1)
    if "shell-desktop.js" in t:
        t = re.sub(r'<script[^>]*shell-desktop\.js[^>]*></script>', js, t)
    else:
        i = t.rfind("</body>")
        t = t[:i] + js + nl + t[i:]

    if t == s:
        return False
    if not so_checa:
        with open(arq, "w", encoding="utf-8", newline="") as f:
            f.write(t)
    return ativo or "(nenhum)"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    so_checa = "--check" in sys.argv
    ver = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--versao=")), None)
    ver = ver or versao((RAIZ / "index.html").read_text(encoding="utf-8"))
    paginas = args or sorted(
        str(pathlib.Path(f).as_posix())
        for f in glob.glob(str(RAIZ / "*.html")) + glob.glob(str(RAIZ / "74/*.html")) + glob.glob(str(RAIZ / "73/*.html")))
    paginas = [pathlib.Path(p).resolve().relative_to(RAIZ).as_posix() for p in paginas]

    for rel in paginas:
        r = sincroniza(rel, ver, so_checa, "--forcar" in sys.argv)
        if r is None or r == "divergente":
            continue
        print(f"{'mudaria' if so_checa and r else 'ok' if r is False else 'gerada'}: {rel}"
              + (f"  (ativo: {r})" if r else ""))
    print(f"versão de cache: {ver}")


if __name__ == "__main__":
    main()
