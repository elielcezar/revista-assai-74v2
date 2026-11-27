"""Converte a exportação do Webflow da edição #76 para o formato das edições anteriores.

    python scripts/webflow76.py

Lê a exportação intacta em 76/_webflow/ e grava as páginas em 76/. Quando o
design reexportar: substitua o conteúdo de 76/_webflow/ pelo zip novo e rode de
novo (76/videos/ e os js baixados do CDN em 76/js/ são mantidos).

- CSS do Webflow forçado para o layout de celular: as @media (max-width) são
  desembrulhadas no lugar (mantendo a ordem da cascata) e as (min-width) saem.
  Assim a coluna de 402px do desktop fica idêntica à página original vista a
  402px. Abaixo de 402px o conteúdo é fluido (como o Webflow foi feito).
- vw vira min(vw, px de uma janela de 402px); o sizes das imagens idem.
- Cabeçalho (rv-cab) e rodapé (rv-rod) do Webflow saem; entram o HEAD e o
  RODAPÉ da #75 (cores e logos da #75), a casca do desktop (shell_sync) e o GTM.
- Vídeos, poster e scripts do CDN do Webflow apontam para os arquivos locais.
"""
import re, sys, json, shutil, pathlib, importlib.util
from html import escape

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DEST = RAIZ / "76"
RAW = DEST / "_webflow"
V = "76-7"
COL = 402

spec = importlib.util.spec_from_file_location("shell_sync", RAIZ / "scripts/shell_sync.py")
shell_sync = importlib.util.module_from_spec(spec); spec.loader.exec_module(shell_sync)

# ---------------------------------------------------------------- páginas
# arquivo -> (rótulo ativo no menu, cor da faixa do HEAD, logo, estilo extra do logo)
LOGO = "../assets/imgLogoHead.svg"
PAGINAS = {
    "index.html": ("CAPA", "#000", LOGO, ""),
    "principal-poder-de-compra-2027.html": ("PRINCIPAL", "#004696", LOGO, ""),
    "gestao-o-que-faz-um-funcionario-ficar.html": ("GESTÃO", "#f0051e", LOGO, ""),
    "mkt-digital-influenciador-no-restaurante.html": ("MKT DIGITAL", "#ff7300", "images/head/logo-head-mkt.svg", ""),
    "produto-reinventar-salgado.html": ("PRODUTO", "#ffaa00", "images/head/logo-head-produto.png", "object-fit:contain"),
    "consumidor-alimentos-funcionais-exigem-rigor.html": ("CONSUMIDOR", "#ffdc00", "images/head/logo-head-consumidor.svg", "mix-blend-mode:multiply"),
    "delivery-quando-a-embalagem-vira-experiencia.html": ("DELIVERY", "#532f82", LOGO, ""),
    "novo-negocio-comodato-cuidados-antes-de-aceitar.html": ("NOVO NEGÓCIO", "#b40082", LOGO, ""),
    "academia-ideias-que-transformam.html": ("ACADEMIA ASSAÍ", "#ff5564", "images/head/logo-head-academia.svg", ""),
    "noticias-como-escolher-maquininha-de-cartao.html": ("NOTÍCIAS DO ASSAÍ", "#0082c8", LOGO, ""),
    "noticias-corridas-de-rua-bons-negocios.html": ("NOTÍCIAS DO ASSAÍ", "#0082c8", LOGO, ""),
}
LOGOS_75 = {  # cópia dos logos próprios da #75
    "logo-head-mkt.svg": "75/assets/mkt/logo-head.svg",
    "logo-head-produto.png": "75/assets/produto/logo-head.png",
    "logo-head-consumidor.svg": "75/assets/consumidor/logo-head.svg",
    "logo-head-academia.svg": "75/assets/academia/logo-head.svg",
}
# ajustes de layout pedidos na aprovação, por página (entram depois de todo o CSS da página)
AJUSTES = {
    # vídeo da cozinha: o Webflow (24/11) desceu o vídeo 20px no celular "para o arco não
    # cobrir as cabeças", e a borda de cima ficou reta sob a curva. A moldura oval desce os
    # mesmos 20px e o vídeo volta ao topo dela: mesmo lugar e quadro, borda seguindo o arco.
    "principal-poder-de-compra-2027.html":
        ".rv-pi-arco .rv-pi-foto { top: calc(19.87% + 20px); }\n"
        ".rv-pi-arco .rv-ilustra-video, .rv-pi-arco .rv-pi-img { top: 0 !important; }",
}

# publicidade (fora do Webflow), arquivos em 76/banners/. Por página, uma lista de
# (onde, âncora, html):
#   "depois" / "antes"            âncora = trecho da tag de abertura de uma <section> (a 1ª que o contém)
#   "depois-de-texto" / "antes-de-texto"   âncora = texto; vale a <section> mais interna que o contém
#   "antes-da-tag"                âncora = trecho de uma tag qualquer (a 1ª), p.ex. <figure class="rv-figura">
# Cada anúncio, ou conjunto de anúncios sorteados, leva a etiqueta "Publicidade" (exigência legal).
# Imagem: largura da coluna; vídeo: story 9:16 de 402px, mudo, em loop, só toca quando aparece.
def anuncio(marca, corpo, extra="", attr=""):
    return (f"<!-- ============ PUBLICIDADE — {marca} (fora do Webflow) ============ -->\n"
            f'      <figure class="rv76-pub{extra}"{attr}><p class="rv76-pub-rot">Publicidade</p>{corpo}</figure>')


def anuncio_img(marca, itens, dentro=False):
    """itens: [(arquivo, alt, largura, altura), ...]. Com mais de um, o JS sorteia um por visita
    (o HTML já traz o primeiro, que aparece sem JavaScript)."""
    a, alt, w, h = itens[0]
    img = f'<img src="banners/{a}?v={V}" alt="{escape(alt)}" width="{w}" height="{h}" loading="lazy">'
    attr = ""
    if len(itens) > 1:
        lista = [[f"banners/{x[0]}?v={V}", x[1], x[2], x[3]] for x in itens]
        attr = ' data-rv76-random="' + escape(json.dumps(lista, ensure_ascii=False), quote=True) + '"'
    return anuncio(marca, img, " rv76-pub--dentro" if dentro else "", attr)


def anuncio_video(marca, arquivo, alt):
    return anuncio(marca, f'<video src="banners/{arquivo}?v={V}" width="720" height="1280" muted loop '
                          f'playsinline preload="metadata" aria-label="{escape(alt)}"></video>')


ANUNCIOS = {
    "principal-poder-de-compra-2027.html": [
        ("depois", 'aria-label="Endividamento das famílias"',
         anuncio_img("BANNER ORAL-B", [("principal-oralb.jpg", "Publicidade Oral-B: Tá brilhante, tô confiante! "
                     "Creme dental Oral-B 3D White Carvão e escovas Oral-B 3D White", 372, 250)])),
    ],
    "gestao-o-que-faz-um-funcionario-ficar.html": [
        ("depois-de-texto", 'class="rv-coluna is-texto"',
         anuncio_video("STORY TAKIS (BIMBO)", "gestao-bimbo.mp4", "Publicidade Takis: Se joga na intensidade. "
                       "Encontre Takis no Assaí! Pacote de Takis Intense Nacho sobre fundo colorido.")),
    ],
    "produto-reinventar-salgado.html": [
        ("depois", 'class="rv-bloco"',
         anuncio_video("STORY MATURATTA (JBS)", "produto-jbs.mp4", "Publicidade Maturatta Friboi: Antes da grelha acender, os preparativos já começaram. Antecipe as compras. Cortes de carne na grelha e embalagens de produtos Maturatta.")),
    ],
    "academia-ideias-que-transformam.html": [
        ("depois", 'class="rv-lead-bloco"',
         anuncio_img("BANNERS ACADEMIA (SORTEIO)", [
             ("academia-itabom.png", "Publicidade Itabom: linhas completas para preparos rápidos e receitas "
              "especiais.", 375, 391),
             ("academia-kim.png", "Publicidade Kim Nobre: pães macios por dentro, irresistíveis por inteiro. "
              "Experimente as versões original e integral.", 375, 391),
             ("academia-santamaria.png", "Publicidade Esfrelux, da Santa Maria: a escolha inteligente para quem "
              "vive em ritmo acelerado. Experimente agora!", 375, 391)])),
    ],
    "novo-negocio-comodato-cuidados-antes-de-aceitar.html": [
        ("depois", 'class="rv-bloco is-editoria"',
         anuncio_img("BANNERS NOVO NEGÓCIO (SORTEIO)", [
             ("novonegocio-engetech.png", "Publicidade Engetech: tem um Dover-Roll ideal para cada necessidade, "
              "o melhor saco para lixo do Brasil. Você encontra no Assaí!", 391, 375),
             ("novonegocio-goldenplast.png", "Publicidade Goldenplast: talheres Linha Master. Qualidade e "
              "resistência para o seu dia a dia! Disponível na rede Assaí Atacadista.", 375, 391),
             ("novonegocio-haleaon.png", "Publicidade Sensodyne: o cuidado da sensibilidade começa hoje. "
              "Embalagens do creme dental Sensodyne.", 391, 375)])),
    ],
    "mkt-digital-influenciador-no-restaurante.html": [
        ("antes", 'aria-labelledby="mkt-cliente"',
         anuncio_video("STORY AURORA", "mkt-aurora.mp4", "Publicidade Aurora: Se tem Aurora, só melhora. Pessoas provam linguiças e empanados de frango da Aurora; embalagens dos produtos aparecem no fim.")),
    ],
    "consumidor-alimentos-funcionais-exigem-rigor.html": [
        ("depois", 'class="rv-bloco"',
         anuncio_video("STORY OMO (UNILEVER)", "consumior-unilever.mp4", "Publicidade OMO: lavagem perfeita, agora "
                       "é OMO Todo Ciclo. Caixa do sabão em pó OMO Todo Ciclo.")),
    ],
    "delivery-quando-a-embalagem-vira-experiencia.html": [
        ("antes-da-tag", '<figure class="rv-figura">',
         anuncio_img("BANNERS DELIVERY (SORTEIO)", [
             ("delivery-celeste.jpg", "Publicidade Celeste: mega pano de microfibra super absorvente, mega panão "
              "nas lojas Assaí!", 375, 391),
             ("delivery-flora.png", "Publicidade Carmim Reguengos, da Casa Flora: Olaria tem uma opção para cada "
              "gosto. Duas garrafas de vinho Olaria. Beba com moderação.", 391, 375),
             ("delivery-johnson.jpg", "Publicidade Glade, da SC Johnson: casa de novela? Chá Branco nela. "
              "Aromatizadores Glade Chá Branco.", 391, 375)], dentro=True)),
    ],
    "noticias-como-escolher-maquininha-de-cartao.html": [
        ("antes-de-texto", "Quanto custa uma maquininha de cartão?",
         anuncio_img("BANNER 3CORAÇÕES", [("noticias-3coracoes.png", "Publicidade 3corações: escolhas especiais "
                     "para a sua primavera. Cafés 3corações sobre pedestais com flores.", 391, 375)])),
    ],
}

# link dos botões "Acesse o curso" da ACADEMIA (informado pelo cliente em 27/11)
LINK_CURSO = "https://nova.academiaassai.com.br/cursos/"
LINK_CURSO_PAGINAS = {"academia-ideias-que-transformam.html"}

# não entram no formato das edições anteriores (busca do Webflow, páginas de erro, vazio)
APAGAR = ["busca.html", "401.html", "404.html", "gestao-versao-anterior.html"]
# o <main> das matérias termina num padding-bottom de 48px: o RODAPÉ sobe os 45px brancos de
# cima dele por cima desse padding (transparentes), e a barra preta fica a 48px do conteúdo,
# como no Webflow. (O padding era a "faixa azul-marinho" até a correção do fundo do .rv-main.)
SEM_FAIXA = {"index.html", "academia-ideias-que-transformam.html"}

# ---------------------------------------------------------------- fontes
# A exportação veio sem as fontes (src: url('../images/')). As enviadas pelo design ficam
# em 76/fonts/ (FS Lola Regular, Medium, Bold e ExtraBold). Não vieram itálicos: os da
# fonts/ da raiz têm as mesmas larguras de letra. A Raspoutine enviada tem os acentos
# quebrados no Chrome (README, armadilha 2): vale a cópia corrigida da raiz.
FONTES_RAIZ = ["FSLola-Italic.otf", "FSLola-MediumItalic.otf", "FSLola-BoldItalic.otf", "RaspoutineMedium-fix.otf"]
FONTES_ENVIADAS = ["FS-Lola.woff2", "FS-Lola.woff", "FS-Lola-Medium.woff2", "FS-Lola-Medium.woff",
                   "FS-Lola-Bold.woff2", "FS-Lola-Bold.woff", "FS-Lola-ExtraBold.woff2", "FS-Lola-ExtraBold.woff"]


def _web(nome):
    return f"url('../fonts/{nome}.woff2') format('woff2'), url('../fonts/{nome}.woff') format('woff')"


FONTES = {  # (família, peso, estilo) do @font-face exportado -> src
    ("FS Lola", "400", "normal"): _web("FS-Lola"),
    ("FS Lola", "500", "normal"): _web("FS-Lola-Medium"),
    ("FS Lola", "700", "normal"): _web("FS-Lola-Bold"),
    ("FS Lola", "800", "normal"): _web("FS-Lola-ExtraBold"),
    ("FS Lola", "400", "italic"): "url('../fonts/FSLola-Italic.otf') format('opentype')",
    ("FS Lola", "500", "italic"): "url('../fonts/FSLola-MediumItalic.otf') format('opentype')",
    ("FS Lola", "700", "italic"): "url('../fonts/FSLola-BoldItalic.otf') format('opentype')",
    ("Raspoutine", "500", "normal"): "url('../fonts/RaspoutineMedium-fix.otf') format('opentype')",
}


def liga_fontes(css):
    def troca(m):
        b = m.group(0)
        fam = re.search(r"font-family:\s*['\"]?([^;'\"]+)", b).group(1).strip()
        peso = (re.search(r"font-weight:\s*(\d+)", b) or [None, "400"])[1]       # padrões do CSS
        estilo = (re.search(r"font-style:\s*(\w+)", b) or [None, "normal"])[1]
        src = FONTES.get((fam, peso, estilo))
        return re.sub(r"src:\s*url\(['\"]?\.\./images/['\"]?\)[^;]*;", f"src: {src};", b) if src else b
    css = re.sub(r"@font-face\s*{[^}]*}", troca, css)
    assert "../images/')" not in css and '../images/")' not in css, "fonte sem arquivo no CSS exportado"
    return css


# ---------------------------------------------------------------- CDN -> local
# Os arquivos locais foram baixados do CDN do Webflow e otimizados (CRF 28, até 1280px,
# áudio só no outburgers) quando ficaram menores que o original. Arquivo novo no CDN:
# baixe para 76/videos/ ou 76/js/ e acrescente aqui.
CDN_HOST = "https://cdn.prod.website-files.com/6ae120959d4de28ff1b3d8e8"
MIDIA = {  # nome no CDN -> arquivo em 76/
    "6afcb0772c962fe7776dda34_principal76-abertura.mp4": "videos/principal76-abertura.mp4",
    "6afcb125b0edfb198dc0bb4a_principal76-cozinha.mp4": "videos/principal76-cozinha.mp4",
    "6afcb125c047387ccb40fff0_gestao76-abertura.mp4": "videos/gestao76-abertura.mp4",
    "6afcb125e2975eebc2dc34c8_delivery76-outburgers.mp4": "videos/delivery76-outburgers.mp4",
    "6b05a6ce3d5492fcf20187f8_noticias76-corrida-fortaleza.mp4": "videos/noticias76-corrida-fortaleza.mp4",
    "6b05a6ce1cb336d8cb4a9735_noticias76-corrida-fortaleza-poster.jpg": "videos/noticias76-corrida-fortaleza-poster.jpg",
}
# ACADEMIA: o script monta o endereço com CDN + nome; os dois passam a ser locais
ACADEMIA_CDN_BASE = "var CDN='https://cdn.prod.website-files.com/6ae120959d4de28ff1b3d8e8/';"
ACADEMIA_VIDEOS = ["m76-hero-ia", "m76-capa-curso", "m76-trecho-aula1", "m76-trecho-aula2", "m76-trecho-aula3"]
ACADEMIA_HASH = {"m76-hero-ia": "6ae2117f2ba31b0216a9acd3", "m76-capa-curso": "6ae175e4b01bcbfdb71be340",
                 "m76-trecho-aula1": "6ae175f2025b704c26c25ea1", "m76-trecho-aula2": "6ae175f27c5ba8140e3d8da6",
                 "m76-trecho-aula3": "6ae175f2885f726d0a4d697b"}
SCRIPTS_CDN = {  # trecho do endereço -> arquivo em 76/
    "rvlistasemmemoria-1.0.0.js": "js/rvlistasemmemoria-1.0.0.js",
    "corridas_video_botoes-1.0.0.js": "js/corridas_video_botoes-1.0.0.js",
}
JQUERY_CDN = "https://d3e54v103j8qbb.cloudfront.net/js/jquery-3.5.1.min.dc5e7f18c8.js?site=6ae120959d4de28ff1b3d8e8"


# ---------------------------------------------------------------- CSS
def bloco(css, ini):
    """fim (exclusivo) do bloco { } que abre em css[ini-1] == '{'"""
    d, j = 1, ini
    while d:
        c = css[j]
        if c == "{": d += 1
        elif c == "}": d -= 1
        elif c in "\"'":  # pula strings
            j = css.index(c, j + 1)
        j += 1
    return j


def forca_celular(css):
    """desembrulha @media (max-width) no lugar; descarta @media (min-width)."""
    out, i = [], 0
    pat = re.compile(r"@media([^{]*){")
    while True:
        m = pat.search(css, i)
        if not m:
            out.append(css[i:]); break
        out.append(css[i:m.start()])
        j = bloco(css, m.end())
        q = m.group(1)
        if "max-width" in q and "min-width" not in q:
            out.append(css[m.end():j - 1])
        elif "min-width" in q:
            pass
        else:
            out.append(css[m.start():j])
        i = j
    return "".join(out)


def vw_em_px(css):
    # no celular (tela < 402px) a coluna é a tela: vw continua valendo; na coluna de
    # 402px do desktop, trava no valor de uma janela de 402px. Não mexe em nomes ("--x-vw").
    return re.sub(r"(?<![\w-])(\d*\.?\d+)vw\b",
                  lambda m: f"min({m.group(1)}vw, {float(m.group(1)) * COL / 100:g}px)", css)


def sem_fundo_main(css):
    """Correção do cliente (26/11): o background-color da classe .rv-main (o <main id="materia">
    de todas as matérias) foi uma edição errada no Designer e saiu; a classe fica só com o
    padding-bottom. A nossa exportação trazia #1a1f3a (azul-marinho: texto preto sobre ele em
    várias seções); a do cliente, #d8f2f3. Numa exportação já corrigida isto não muda nada."""
    return re.sub(r"(?m)^([ \t]*\.rv-main\s*\{)([^}]*)\}",
                  lambda m: m.group(1) + re.sub(r"\n[ \t]*background-color:[^;]*;", "", m.group(2)) + "}",
                  css)


def converte_css(css):
    return sem_fundo_main(vw_em_px(forca_celular(css)))


def sizes_402(valor):
    """sizes de um <img> para a coluna: o desktop baixava fotos de 920px+ para mostrar em 402px.
    Avalia o original como numa janela de 402px; se der em vw, abaixo de 402px continua em vw."""
    for parte in (p.strip() for p in valor.split(",")):
        m = re.match(r"\((max|min)-width:\s*(\d+)px\)\s*(.+)$", parte)
        if m:
            tipo, n, larg = m.group(1), int(m.group(2)), m.group(3)
            if not ((tipo == "max" and COL <= n) or (tipo == "min" and COL >= n)):
                continue
            parte = larg
        v = re.fullmatch(r"(\d*\.?\d+)vw", parte)
        if v:
            return f"(max-width: {COL - 1}px) {parte}, {float(v.group(1)) * COL / 100:g}px"
        return parte
    return valor


def converte_sizes(html):
    return re.sub(r'(<img\b[^>]*\bsizes=")([^"]*)(")', lambda m: m.group(1) + sizes_402(m.group(2)) + m.group(3), html)


# ---------------------------------------------------------------- HTML fixos
def gtm(i):
    return ("<!-- Google Tag Manager -->\n<script>\n(function(w,d,s,l,i){\n  w[l]=w[l]||[];\n"
            "  w[l].push({'gtm.start': new Date().getTime(),event:'gtm.js'});\n"
            "  var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';\n"
            "  j.async=true;\n  j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;\n"
            "  f.parentNode.insertBefore(j,f);\n"
            f"}})(window,document,'script','dataLayer','{i}');\n</script>\n<!-- End Google Tag Manager -->")


# rolagem inicial do menu do celular: os mesmos valores dos js da #75 (o menu é igual
# até ACADEMIA). NOTÍCIAS: a #75 pede 596 (item em x=159), mas abre em 0 por erro; sem
# COLUNA, o mesmo x dá 535.
ROLAGEM = {"CAPA": 0, "PRINCIPAL": 0, "GESTÃO": 0, "MKT DIGITAL": 7, "PRODUTO": 79, "CONSUMIDOR": 159,
           "DELIVERY": 240, "NOVO NEGÓCIO": 323, "ACADEMIA ASSAÍ": 357, "NOTÍCIAS DO ASSAÍ": 535}


def head_html(ativo, logo):
    itens = []
    for rot, alvo, cor, _local in shell_sync.MENU:
        if rot == ativo:
            itens.append(f'        <li style="--mc:{cor}" class="is-active"><a href="../{alvo}" aria-current="page" target="_blank" rel="noopener">{rot}</a></li>')
        else:
            itens.append(f'        <li style="--mc:{cor}"><a href="../{alvo}" target="_blank" rel="noopener">{rot}</a></li>')
    return "\n".join([
        "  <!-- ============ COMPONENTE HEAD (#75) ============ -->",
        '  <header class="head">',
        '    <div class="head-brand">',
        f'      <img class="head-logo" src="{logo}" alt="Assaí Bons Negócios" width="283" height="30">',
        "    </div>",
        f'    <nav class="head-nav" aria-label="Seções da revista" data-rolagem="{ROLAGEM[ativo]}">',
        "      <ul>", *itens, "      </ul>",
        "    </nav>",
        "  </header>",
    ])


FOOT = """  <!-- ============ COMPONENTE RODAPE (#75) ============ -->
  <footer class="foot">
    <span class="foot-bar" aria-hidden="true"></span>
    <a class="foot-top" href="#" aria-label="Voltar ao topo"><img src="../assets/imgGroup8650.svg" alt=""></a>
    <button class="foot-share" type="button" aria-label="Compartilhar">
      <img class="foot-share-a" src="../assets/imgGroup.svg" alt="">
      <img class="foot-share-b" src="../assets/imgVector1.svg" alt="">
      <img class="foot-share-c" src="../assets/imgVector2.svg" alt="">
    </button>
    <span class="foot-brand"><img src="../assets/imgGroup2.svg" alt="Assaí Atacadista"></span>
    <a class="foot-stores" href="https://www.assai.com.br/nossas-lojas" target="_blank" rel="noopener noreferrer">NOSSAS LOJAS <img src="../assets/imgGroup8651.svg" alt=""></a>
  </footer>"""


def secoes(s):
    """(início, fim, tag de abertura) de cada <section>, inclusive as aninhadas, na ordem da página."""
    pilha, out = [], []
    for m in re.finditer(r"<(/?)section\b[^>]*>", s):
        if m.group(1):
            ini = pilha.pop()
            out.append((ini.start(), m.end(), ini.group(0)))
        else:
            pilha.append(m)
    assert not pilha, "<section> sem fechamento"
    return sorted(out)


def insere_anuncio(s, onde, ancora, anuncio_html):
    """Insere o anúncio na página conforme `onde` (ver ANUNCIOS)."""
    if onde == "antes-da-tag":
        i = s.index(ancora)
        return s[:i] + anuncio_html + "\n          " + s[i:]
    if onde in ("depois", "antes"):
        alvos = [x for x in secoes(s) if ancora in x[2]]
    else:
        pos = s.index(ancora)
        alvos = sorted((x for x in secoes(s) if x[0] < pos < x[1]), key=lambda x: x[1] - x[0])
    assert alvos, f"âncora do anúncio não encontrada: {ancora}"
    ini, fim, _ = alvos[0]
    if onde.startswith("depois"):
        return s[:fim] + "\n      " + anuncio_html + s[fim:]
    return s[:ini] + anuncio_html + "\n      " + s[ini:]


def converte_html(nome, s):
    ativo, cor, logo, estilo_logo = PAGINAS[nome]

    # --- <head> ---
    s = s.replace("<html ", '<html lang="pt-BR" ', 1) if " lang=" not in s[:300] else s
    s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n' + gtm("GTM-MS6VK9B") + "\n" + gtm("GTM-W6GXJGP7"), 1)
    # CSS próprios com versão; o forçado para celular mora nos mesmos arquivos
    for c in ("normalize.css", "webflow.css", "assai-76.webflow.css"):
        s = s.replace(f'href="css/{c}"', f'href="css/{c}?v={V}"')
    s = converte_sizes(s)
    # favicon: o do Webflow (um "ô" magenta) sai; como nas edições anteriores (73-75), que não
    # declaram nenhum, fica o ícone padrão do Assaí do servidor (/favicon.ico)
    s = re.sub(r'[ \t]*<link\b[^>]*\brel="(?:icon|shortcut icon|apple-touch-icon)"[^>]*>\r?\n?', "", s)
    # estilos embutidos: mesmo tratamento do CSS
    s = re.sub(r"(<style[^>]*>)(.*?)(</style>)", lambda m: m.group(1) + converte_css(m.group(2)) + m.group(3), s, flags=re.S)
    # cor/logo do HEAD (#75) e invólucro, depois de todo o CSS da página
    extra_logo = f"\n.head-logo {{ {estilo_logo}; }}" if estilo_logo else ""
    extra_logo += f"\n/* ajuste da aprovação (scripts/webflow76.py, AJUSTES) */\n{AJUSTES[nome]}" if nome in AJUSTES else ""
    s = s.replace("</head>",
                  f'  <link href="css/revista76.css?v={V}" rel="stylesheet" type="text/css">\n'
                  f"  <style>.head {{ --head-bg: {cor}; }}{extra_logo}</style>\n"
                  '  <link href="../css/shell.css?v=74-117" rel="stylesheet" type="text/css">\n'
                  "</head>", 1)

    # --- <body> ---
    ib = s.index("<body"); ib = s.index(">", ib) + 1
    fim = s.index('<script src="' + JQUERY_CDN, ib)   # o corpo visível termina antes dos scripts finais
    corpo = s[ib:fim]
    cab = re.search(r'<header\b[^>]*class="rv-cab\b[^"]*"[^>]*>.*?</header>', corpo, re.S)
    rod = re.search(r'<footer class="rv-rod">.*?</footer>', corpo, re.S)
    assert cab and rod, nome
    antes, meio, depois = corpo[:cab.start()], corpo[cab.end():rod.start()], corpo[rod.end():]
    casca = shell_sync.casca("76", ativo)
    classe = "page" if nome in SEM_FAIXA else "page tem-faixa"
    novo = ("\n" + casca + "\n\n" + f'<div class="{classe}">\n\n' + head_html(ativo, logo) + "\n\n"
            + antes.strip() + meio.rstrip() + "\n" + depois.strip() + "\n\n" + FOOT + "\n\n</div>\n")
    s = s[:ib] + novo + s[fim:]
    for onde, ancora, anuncio_html in ANUNCIOS.get(nome, []):
        s = insere_anuncio(s, onde, ancora, anuncio_html)

    # --- scripts ---
    # cabeçalho/rodapé do Webflow saíram: o script deles também
    s = re.sub(r"(<!--\s*Revista: cabe[^>]*-->\s*)?<script>\s*\(function\(\)\{\s*var reduz=[^<]*?EDICOES.*?</script>", "", s, count=1, flags=re.S)
    # ScrollTrigger do CDN do Webflow: carregado sem o GSAP e sem uso nas páginas
    s = re.sub(r'\s*<script src="https://cdn\.prod\.website-files\.com/gsap/[^"]*ScrollTrigger[^"]*"[^>]*></script>', "", s)
    s = s.replace(JQUERY_CDN, f"js/jquery-3.5.1.min.js?v={V}")
    s = re.sub(r'(\s*integrity="[^"]*"\s*crossorigin="anonymous")', "", s) if f"js/jquery-3.5.1.min.js" in s else s
    s = s.replace('src="js/webflow.js"', f'src="js/webflow.js?v={V}"')
    for trecho, dest in SCRIPTS_CDN.items():
        s = re.sub(r'src="https://cdn\.prod\.website-files\.com/[^"]*' + re.escape(trecho) + '"', f'src="{dest}?v={V}"', s)
    for cdn_nome, dest in MIDIA.items():
        s = s.replace(f"{CDN_HOST}/{cdn_nome}", dest)
    if ACADEMIA_CDN_BASE in s:
        s = s.replace(ACADEMIA_CDN_BASE, "var CDN='videos/';")
        for n in ACADEMIA_VIDEOS:
            s = s.replace(f"'{ACADEMIA_HASH[n]}_{n}.mp4'", f"'{n}.mp4'")
    # ACADEMIA: os dois botões "Acesse o curso" (a exportação traz href="#" e LINK_CURSO='#')
    if nome in LINK_CURSO_PAGINAS:
        s = s.replace("var LINK_CURSO='#';", f"var LINK_CURSO='{LINK_CURSO}';")
        s, n = re.subn(r'<a href="#"( class="rv-botao )', rf'<a href="{LINK_CURSO}" target="_blank" rel="noopener"\1', s)
        assert n == 2, f"botões 'Acesse o curso' esperados: 2, achados: {n}"
    # comportamentos que dependiam da largura da janela/do cabeçalho do Webflow
    s = s.replace("window.matchMedia('(max-width: 991px)')", "window.matchMedia('all')")   # CONSUMIDOR: carrossel de celular sempre ligado
    s = s.replace("document.querySelector('.rv-cab, .rv-header, header')", "document.querySelector('.rv-cab')")  # GESTÃO: não confundir com o HEAD da #75
    # invólucro: HEAD e RODAPÉ reduzidos abaixo de 402px, voltar ao topo (sem o js/shell.js da
    # #75: o transform: scale dele quebrava os position: sticky das matérias)
    i = s.rfind("</body>")
    s = s[:i] + f'  <script src="js/revista76.js?v={V}"></script>\n' + s[i:]
    return s


REVISTA76_CSS = """/* =========================================================
   Revista Assaí Bons Negócios #76 — invólucro das páginas vindas do Webflow
   Coluna de 402px, HEAD e RODAPÉ da #75 (mesmas medidas de css/base.css).
   A cor da faixa do HEAD vem de --head-bg, definida em cada página.

   Abaixo de 402px o conteúdo do Webflow é fluido (ocupa a tela) e só o HEAD e o
   RODAPÉ, desenhos fixos de 402px, são reduzidos (zoom, em js/revista76.js).
   Não usa o transform: scale do js/shell.js da #75: com ele os position: sticky
   das matérias (painéis que acompanham a rolagem) saíam da tela.
   ========================================================= */

.page {
  width: 100%;
  max-width: 402px;
  margin: 0 auto;
  background: #fff;
  /* clip, e nao hidden: hidden faria do .page o recipiente dos position: sticky
     das materias (paineis que acompanham a rolagem) e eles parariam de grudar */
  overflow-x: clip;
}

/* ---------- reset so dos componentes da #75 (o conteudo do Webflow tem o seu) ----------
   :where() tem peso zero: as regras dos componentes abaixo (ex.: o branco do
   "NOSSAS LOJAS") vencem o reset (README, armadilha 15) */
:where(.head, .foot), :where(.head, .foot) * { box-sizing: border-box; }
:where(.head, .foot) img { display: block; max-width: none; }
:where(.head) ul { margin: 0; padding: 0; list-style: none; }
:where(.head, .foot) a { color: inherit; text-decoration: none; }
:where(.foot) button { font: inherit; color: inherit; background: none; border: 0; padding: 0; cursor: pointer; }

/* =========================================================
   COMPONENTE HEAD  (402 x 182)
   ========================================================= */
.head { position: relative; width: 402px; height: 182px; overflow: hidden; background: #fff; }
.head-brand { height: 141px; background: var(--head-bg, #004696); position: relative; }
.head-logo { position: absolute; width: 283px; height: 30px; top: 78px; left: 50%; margin-left: -147px; }

.head-nav {
  height: 41px;
  background: #d9d9d9;
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: none;
}
.head-nav::-webkit-scrollbar { display: none; }
.head-nav ul { display: flex; align-items: flex-start; gap: 14px; padding: 5px 0 0 8px; height: 41px; width: max-content; }
.head-nav li { border-bottom: 5px solid var(--mc); display: flex; align-items: center; justify-content: center; }
.head-nav a {
  font-family: "Inter", "FS Lola", Arial, sans-serif;
  font-size: 11px; font-weight: 400; color: #000; white-space: nowrap;
  padding: 10px 0 4px; line-height: normal;
}
.head-nav .is-active a { font-weight: 700; }

/* =========================================================
   COMPONENTE RODAPE  (402 x 116)
   ========================================================= */
.foot { position: relative; width: 402px; height: 116px; background: #fff; overflow: hidden; font-family: "FS Lola", "Segoe UI", Arial, sans-serif; -webkit-font-smoothing: antialiased; }
.foot-bar { position: absolute; left: 0; top: 45px; width: 402px; height: 71px; background: #000; display: block; }

.foot-top { position: absolute; left: 18px; top: 72px; width: 19px; height: 18px; display: flex; align-items: center; justify-content: center; }
.foot-top img { width: 18px; height: 19px; transform: rotate(90deg); }

.foot-share { position: absolute; left: 50px; top: 72px; width: 17px; height: 20px; display: block; }
.foot-share-a { position: absolute; left: 0; top: 0; width: 17px; height: 20px; }
.foot-share-b { position: absolute; left: 5px; top: 4px; width: 6px; height: 4px; }
.foot-share-c { position: absolute; left: 5px; top: 12px; width: 6px; height: 4px; }

.foot-brand { position: absolute; left: 169px; top: 62px; width: 50px; height: 37px; overflow: hidden; display: block; }
.foot-brand img { width: 50px; height: 37px; }

.foot-stores {
  position: absolute; left: 292px; top: 76.9px;
  font-size: 10px; font-weight: 500; color: #fff; white-space: nowrap; line-height: normal;
}
.foot-stores img { position: absolute; left: 70.5px; top: -4.9px; width: 20px; height: 19px; }

/* materias cujo <main> termina no padding-bottom de 48px do Webflow: o RODAPE sobe os
   45px brancos de cima por cima do padding (transparentes), e a barra preta fica a 48px
   do conteudo, como no Webflow (sem somar os dois espacos) */
.page.tem-faixa > .foot { margin-top: -45px; background: transparent; }

/* publicidade (ANUNCIOS no scripts/webflow76.py): imagem na largura da coluna, ou story de video
   9:16; branco acima, como a Predilecta na #75, e a etiqueta "Publicidade" discreta no canto */
.rv76-pub { margin: 0; padding-top: 22px; background: #fff; }
.rv76-pub-rot { display: block; width: max-content; margin: 0; padding: 1px 6px;
  border: 1px solid #c8c8c8; border-radius: 3px; font: 500 10px/14px "FS Lola", Arial, sans-serif;
  letter-spacing: .08em; text-transform: uppercase; color: #6b6b6b; }
.rv76-pub img, .rv76-pub video { display: block; width: 100%; height: auto; }
.rv76-pub video { aspect-ratio: 9 / 16; object-fit: cover; background: #fff; }
/* dentro da coluna de texto (DELIVERY): sai dos 22px de margem e ocupa a largura da pagina */
.rv76-pub--dentro { margin: 24px calc(50% - min(50vw, 201px)); padding-top: 0; }

/* carrosseis de rolagem lateral do Webflow: com mouse, arrastar (js/revista76.js) */
@media (hover: hover) and (pointer: fine) {
  .page .rv-arrastavel { cursor: grab; user-select: none; }
  .page .rv-arrastavel.is-arrastando { cursor: grabbing; }
}
"""

REVISTA76_JS = """/* Revista Assaí #76 — invólucro das páginas vindas do Webflow (comportamento igual ao da #75) */
(function () {
  "use strict";

  /* HEAD e RODAPÉ sao desenhos de 402px: em telas menores, reduzidos na proporcao.
     zoom (e nao transform) para que a caixa ocupe no fluxo a altura reduzida. */
  var FRAME_W = 402;
  var fixos = document.querySelectorAll(".page > .head, .page > .foot");
  function ajusta() {
    var w = document.documentElement.clientWidth || window.innerWidth;
    var z = w < FRAME_W ? String(w / FRAME_W) : "";
    for (var i = 0; i < fixos.length; i++) fixos[i].style.zoom = z;
  }
  ajusta();
  window.addEventListener("resize", ajusta);
  window.addEventListener("orientationchange", ajusta);

  /* menu do celular: a faixa abre rolada até o item ativo (posição de cada página no data-rolagem) */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = parseInt(nav.getAttribute("data-rolagem"), 10) || 0;

  /* voltar ao topo */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* carrosseis de rolagem lateral do Webflow: ideias do DELIVERY ([data-carrossel]) e
     beneficios do Assai Pay na NOTICIAS ([data-faixa], que ja tem setas e pontos).
     No celular sao rolagem nativa (dedo), que o mouse nao arrasta. Com mouse: arrastar
     anda um item por vez e para nas pontas, como os carrosseis da #74/#75. O dedo
     continua com a rolagem nativa; indicadores, setas e pontos acompanham a rolagem. */
  var faixas = [];
  var q1 = document.querySelectorAll(".page [data-carrossel]");
  for (var k = 0; k < q1.length; k++) faixas.push([q1[k], q1[k].children]);
  var q2 = document.querySelectorAll(".page [data-faixa]");
  for (k = 0; k < q2.length; k++) {
    var jan = q2[k].querySelector(".rv-nt-janela");
    if (jan) faixas.push([jan, q2[k].querySelectorAll(".rv-nt-painel")]);
  }
  for (k = 0; k < faixas.length; k++) (function (lista, itens) {
    var x0 = null, s0 = 0, moveu = false, id = 0;
    function posicoes() {
      var p = [];
      for (var i = 0; i < itens.length; i++) p.push(itens[i].offsetLeft - itens[0].offsetLeft);
      return p;
    }
    lista.classList.add("rv-arrastavel");
    lista.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      x0 = e.clientX; s0 = lista.scrollLeft; moveu = false; id = e.pointerId;
      lista.style.scrollSnapType = "none";
      lista.classList.add("is-arrastando");
      try { lista.setPointerCapture(id); } catch (err) {}
    });
    lista.addEventListener("pointermove", function (e) {
      if (x0 === null) return;
      var dx = e.clientX - x0;
      if (Math.abs(dx) > 3) moveu = true;
      lista.scrollLeft = s0 - dx;
    });
    function solta(e) {
      if (x0 === null) return;
      var dx = e.clientX - x0, p = posicoes(), i = 0, melhor = Infinity;
      x0 = null;
      for (var j = 0; j < p.length; j++) {           // item em que o arraste começou
        if (Math.abs(p[j] - s0) < melhor) { melhor = Math.abs(p[j] - s0); i = j; }
      }
      if (Math.abs(dx) > 40) i += dx < 0 ? 1 : -1;
      i = Math.max(0, Math.min(p.length - 1, i));
      lista.classList.remove("is-arrastando");
      try { lista.releasePointerCapture(id); } catch (err) {}
      lista.scrollTo({ left: p[i], behavior: "smooth" });
      setTimeout(function () { lista.style.scrollSnapType = ""; }, 450);
    }
    lista.addEventListener("pointerup", solta);
    lista.addEventListener("pointercancel", solta);
    lista.addEventListener("dragstart", function (e) { e.preventDefault(); });
    lista.addEventListener("click", function (e) {
      if (moveu) { e.preventDefault(); e.stopPropagation(); moveu = false; }
    }, true);
  })(faixas[k][0], faixas[k][1]);

  /* publicidade (ANUNCIOS no webflow76.py): conjuntos de banners mostram um sorteado por visita;
     story em video e mudo, em loop, e so toca enquanto aparece (com "reduzir movimento": parado, com controles) */
  var pubs = document.querySelectorAll(".page [data-rv76-random]");
  for (var pi = 0; pi < pubs.length; pi++) {
    try {
      var sorteio = JSON.parse(pubs[pi].getAttribute("data-rv76-random"));
      var it = sorteio[Math.floor(Math.random() * sorteio.length)], im = pubs[pi].querySelector("img");
      if (im && it) { im.src = it[0]; im.alt = it[1]; im.width = it[2]; im.height = it[3]; }
    } catch (err) {}
  }
  var reduzPub = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  Array.prototype.forEach.call(document.querySelectorAll(".page .rv76-pub video"), function (v) {
    v.muted = true;
    if (reduzPub || !("IntersectionObserver" in window)) { v.controls = true; return; }
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); } else { v.pause(); }
      });
    }, { threshold: 0.4 }).observe(v);
  });

  /* compartilhar: como no rodape do Webflow (compartilhamento do aparelho; sem ele,
     copia o link e o botao fica meio apagado por 1,2s) */
  var share = document.querySelector(".foot-share");
  if (share) {
    share.addEventListener("click", function (e) {
      e.preventDefault();
      var d = { title: document.title, url: location.href };
      if (navigator.share) {
        navigator.share(d).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(d.url).then(function () {
          share.setAttribute("aria-label", "Link copiado");
          share.style.opacity = ".5";
          setTimeout(function () { share.style.opacity = ""; share.setAttribute("aria-label", "Compartilhar"); }, 1200);
        });
      }
    });
  }
})();
"""


def main():
    # arquivos que a exportação não traz: baixados do CDN do Webflow (ver MIDIA/SCRIPTS_CDN)
    faltam = [d for d in [*MIDIA.values(), *SCRIPTS_CDN.values(), "js/jquery-3.5.1.min.js",
                          *(f"videos/{n}.mp4" for n in ACADEMIA_VIDEOS)] if not (DEST / d).exists()]
    if faltam:
        sys.exit("faltam em 76/ (baixar do CDN do Webflow): " + ", ".join(faltam))
    faltam = [f for f in FONTES_ENVIADAS if not (DEST / "fonts" / f).exists()]
    if faltam:
        sys.exit("faltam fontes em 76/fonts/: " + ", ".join(faltam))
    novos = sorted(p.name for p in RAW.glob("*.html") if p.name not in PAGINAS and p.name not in APAGAR)
    if novos:
        sys.exit("página nova na exportação, acrescente em PAGINAS ou APAGAR: " + ", ".join(novos))

    # a exportação intacta por cima da 76/ (videos/ e os js baixados ficam)
    for p in RAW.iterdir():
        if p.name in APAGAR: continue
        if p.is_dir(): shutil.copytree(p, DEST / p.name, dirs_exist_ok=True)
        else: shutil.copy2(p, DEST / p.name)
    for nome in APAGAR:
        (DEST / nome).unlink(missing_ok=True)

    for nome in FONTES_RAIZ:
        shutil.copy2(RAIZ / "fonts" / nome, DEST / "fonts" / nome)
    for c in ("webflow.css", "assai-76.webflow.css"):
        f = DEST / "css" / c
        f.write_text(liga_fontes(converte_css(f.read_text(encoding="utf-8"))), encoding="utf-8")
    (DEST / "css/revista76.css").write_text(REVISTA76_CSS, encoding="utf-8")
    (DEST / "js/revista76.js").write_text(REVISTA76_JS, encoding="utf-8")

    (DEST / "images/head").mkdir(exist_ok=True)
    for nome, orig in LOGOS_75.items():
        shutil.copy2(RAIZ / orig, DEST / "images/head" / nome)

    ver = shell_sync.versao((RAIZ / "index.html").read_text(encoding="utf-8"))
    for nome in PAGINAS:
        f = DEST / nome
        s = f.read_text(encoding="utf-8")
        f.write_text(converte_html(nome, s), encoding="utf-8", newline="")
        shell_sync.sincroniza(f"76/{nome}", ver, False)   # css/js da casca do desktop
        print("convertida:", nome)


if __name__ == "__main__":
    main()
