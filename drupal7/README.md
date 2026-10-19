# Revista 2026 no Drupal 7

Conversão do protótipo (raiz do repositório) num tema de Drupal 7. O protótipo
continua sendo a fonte: as páginas são editadas e validadas nele, e
`scripts/exportar.py` gera o tema, os arquivos do FTP e o corpo de cada
conteúdo.

## Como funciona no site

1. Cada página da revista é um conteúdo do tipo **Revista 2026**.
2. O **ThemeKey** troca para o tema `revista2026` quando o conteúdo aberto é
   desse tipo.
3. O **corpo** do conteúdo traz só o miolo da página. O tema monta o resto:
   - GTM, viewport, fontes;
   - a casca do desktop (logo, edição, menu, redes, QR);
   - nas páginas da #74, a coluna `.page` com cabeçalho, menu mobile e rodapé;
   - os CSS e JS comuns (base, shell, `scroll-fx.js` + GSAP).
4. Os **campos de CSS e JS** do conteúdo apontam os arquivos da página, que
   ficam na pasta da edição no FTP (`ed74/`, `ed73/`).
5. O **menu** é fixo no tema: `tema/revista2026/revista.json`.

### O corpo

A primeira linha é um comentário de controle, que o tema lê e retira:

```html
<!-- revista2026 {
 "pagina": "74/gestao.html",
 "edicao": "74",
 "layout": "74",
 "ativo": "GESTÃO",
 "fx": true,
 "espera": ".fx-espera [data-fx=\"pop-in\"] [data-fx-item]"
} -->
<article class="art">
  …
</article>
```

| chave | o quê |
| --- | --- |
| `edicao` | texto da casca ("Edição #74 · Setembro/2026") e links do menu |
| `layout` | `74`: o tema põe `.page`, cabeçalho e rodapé em volta do corpo. `73`: o corpo traz o `<main>` inteiro, com cabeçalho e rodapé próprios (categorias, parceiros, editorial e toda a #73 — cada página tem o seu) |
| `classe` | classe extra do `.page` (`capa`, `academia`…) |
| `ativo` | item do menu em destaque |
| `logo` | logo do cabeçalho, quando a página usa outro (CONSUMIDOR, DELIVERY, PRODUTO) |
| `descricao` | meta description |
| `fontes` | o Google Fonts da página (as da #73 pedem pesos e famílias diferentes) |
| `fx`, `splittext` | carregam GSAP + ScrollTrigger (+ SplitText) e o `scroll-fx.js` |
| `espera` | seletores do trecho anti-piscada dos efeitos de entrada |
| `pagina` | arquivo de origem; usado para o item extra DOWNLOAD da `73/download.html` |

No layout 73, o marcador `<!-- revista2026:menu -->` dentro do `.head-menu-inner`
vira os links do menu.

**O tema imprime o corpo como foi gravado, sem os filtros do formato de
texto.** O "Full HTML" do Drupal troca quebras de linha por `<p>`/`<br>` e
corrige tags, o que desmonta o layout. Pela mesma razão, o campo **não pode ter
editor visual** (CKEditor/WYSIWYG): ao salvar, ele reescreve o HTML (tira
atributos `data-fx`, comentários, SVG…). Use um formato de texto sem editor.

### Campos de CSS e JS

O tema lê os campos indicados em *Aparência › Configurações › Revista Assaí
2026* (padrão `field_css` e `field_js`). Em cada item vale:

- um endereço (`/sites/default/files/revista2026/ed74/css/gestao.css?v=74-112`);
- vários, um por linha;
- tags `<link>`/`<script>` coladas (o tema lê o `href`/`src`);
- caminho relativo (`css/gestao.css`), lido a partir da pasta da edição;
- `defer` depois do endereço (ou na tag `<script>`), para carregar com
  `defer`, como vários scripts da #73 (`animista-scroll.js`, `ad-carousel.js`…).
  A ordem de execução em relação ao `revista-73-menu.js` depende disso.

A ordem dos itens é a ordem de carga. O `CADASTRO.md` gerado traz a lista de
cada conteúdo.

## Pasta

```
drupal7/
  tema/revista2026/       fonte do tema (sem os CSS/JS comuns, que vêm do protótipo)
    revista2026.info
    template.php          ligação com o Drupal (lê o conteúdo, limpa o CSS do núcleo)
    revista2026.inc       montagem da página, sem dependência do Drupal
    theme-settings.php    tipo de conteúdo, campos de CSS/JS, GTM
    revista.json          edições, menu, redes, GTM, endereços das páginas e do FTP
    templates/            html.tpl.php, page.tpl.php
  scripts/
    exportar.py           protótipo -> build/
    preview.php           renderiza cada conteúdo com o tema, fora do Drupal
    comparar.py           protótipo x tema: prints, links, 404, erros de JS
  build/                  gerado, fora do git
    tema/revista2026/     o tema completo: sobe para sites/all/themes/
    ftp/ed74/, ftp/ed73/  sobem para a pasta de urls.ftp do revista.json
    conteudos/            corpo de cada conteúdo + CADASTRO.md
```

## Gerar e conferir

```bash
python drupal7/scripts/exportar.py
php drupal7/scripts/preview.php           # PHP 7.3 ou 8.1 do Laragon
python drupal7/scripts/comparar.py        # ou só algumas: comparar.py 74/gestao.html
```

O `exportar.py` só copia para o FTP os arquivos que as páginas usam (HTML e
`url()` dos CSS), com os nomes decodificados (`%20` vira espaço, como o
servidor procura). Ele avisa sobre link para página sem endereço no
`revista.json`, arquivo que não existe e conteúdo fora do miolo.

O `comparar.py` serve o protótipo e um "site" que imita o Drupal (tema em
`/sites/all/themes/revista2026`, FTP em `urls.ftp`, cada conteúdo no seu
alias) e compara página por página. Os efeitos do `scroll-fx` ficam
bloqueados, os vídeos parados e o sorteio dos banners fixo, como nos probes.
O ícone de som da GESTÃO é um GIF animado e pode aparecer como diferença de
alguns pixels.

## Instalação

1. **Endereços.** Em `revista.json`:
   - `paginas`: o alias de cada conteúdo (os que estão lá são provisórios);
   - `urls.ftp`: o endereço público da pasta das edições;
   - `urls.site`: o prefixo dos links, se o Drupal não estiver na raiz.

   Depois rode o `exportar.py` de novo: os links e os endereços de arquivo
   ficam gravados nos corpos.
2. **FTP.** Suba `build/ftp/ed74` e `build/ftp/ed73` para a pasta de
   `urls.ftp`.
3. **Tema.** Suba `build/tema/revista2026` para `sites/all/themes/`. Em
   *Aparência*, habilite o tema **sem** torná-lo padrão. Em *Configurações*,
   confira o tipo de conteúdo, os nomes dos campos de CSS/JS e o GTM:
   desmarque o GTM se o site já o insere por módulo.
4. **Formato de texto.** Crie, ou use, um formato sem filtros e sem editor
   visual, e deixe-o como padrão do corpo do tipo Revista 2026.
5. **ThemeKey.** Crie uma regra: tipo de conteúdo = Revista 2026 → tema
   `revista2026`. Em *Aparência*, deixe marcado "Usar o tema de
   administração ao editar ou criar conteúdo": o tema da revista só monta a
   visualização (`node/N`) e mostraria o formulário de edição sem estilo.
6. **Conteúdos.** Cadastre cada um conforme `build/conteudos/CADASTRO.md`:
   título, alias, corpo (o arquivo inteiro, com o comentário da primeira
   linha), CSS e JS.

Para quem está logado, as abas (Ver/Editar) e as mensagens do Drupal aparecem
numa caixa fixa no canto inferior direito, fora do layout.

## Detalhes do tema

- **Ordem e endereço dos arquivos.** Os CSS e JS do tema saem direto no
  `html.tpl.php`, na ordem do protótipo e sem a agregação do Drupal: o
  `shell-desktop.js` acha o gerador de QR pelo próprio endereço. O cache usa
  `?v=` com a `versao` do `revista.json`.
- **CSS do núcleo removido** (`hook_css_alter`) nas páginas da revista. Para
  quem está logado, fica o da barra de administração. O jQuery e o
  `drupal.js` continuam no `$scripts`.
- **Nada em volta do conteúdo.** O `page.tpl.php` não tem regiões nem
  invólucros: o shell da #73 procura `body > main`, e o `scroll-fx` mede a
  coluna `.page` a partir do topo.
- **Rodapé da capa:** no protótipo, o "NOSSAS LOJAS" da capa apontava para
  `#`. O tema usa o mesmo link das outras páginas (`nossas_lojas`).
- **Meta description:** o tema insere a do comentário de controle. Se o site
  usar o módulo Metatag, a tag pode sair duplicada.

## Edição nova

1. Monte a edição no protótipo, como hoje.
2. Em `revista.json`, cadastre a edição em `edicoes` (rótulo, data, pasta,
   pastas de origem no protótipo) e as páginas em `paginas`. Atualize
   `edicao_atual` e `versao`.
3. Rode `exportar.py` → `preview.php` → `comparar.py`, suba o tema e a pasta
   nova do FTP e cadastre os conteúdos.
