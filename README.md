# Revista Assaí Bons Negócios

Site estático em HTML + CSS + JavaScript puro, sem build. Os arquivos do
repositório são o produto final. Duas edições convivem: a **#74** (atual) e a
**#73** (anterior), cada uma na sua pasta, com as listagens de categoria
compartilhadas na raiz.

## Estrutura

```
/                     index.html (capa da #74) · categoria-*.html (10) · expediente.html
                      editorial.html · parceiros.html · parceiro-1.html … parceiro-5.html
                      css/ (base, shell, shell-desktop, capa, expediente, categoria-*)
                      js/ (+ vendor/) · fonts/
                      assets/ (capa, categorias, expediente, shell + ícones do head/rodapé)
/74/                  as 10 matérias da edição #74 + css/ + js/ + assets/
/73/                  edição #73 completa
/73/_bkp_categorias/  as categorias antigas da #73, fora do ar
/scripts/             shot.py, compare.py e um probe_*.py por página
/reference/           renders de comparação (fora do git)
```

### Navegação

1. O visitante entra pelo `index.html`, a capa da #74.
2. O menu (horizontal no mobile, na casca lateral no desktop) leva para
   `categoria-*.html`, na raiz.
3. Cada categoria abre com a matéria da **#74** e lista abaixo a matéria
   equivalente da **#73**.
4. As matérias da #74 abrem em `74/`, as da #73 em `73/`.
5. EDITORIAL e PARCEIROS abrem na raiz (`editorial.html`, `parceiros.html` e
   as matérias `parceiro-1.html` … `parceiro-5.html`), copiados da #73. CSS,
   JS e assets continuam em `73/`.
6. O item CAPA, em qualquer página das duas edições, volta para o `index.html`
   da raiz.

Endereços antigos (`mkt.html`, `gestao.html`… na raiz) são stubs de redirect
que mandam para a categoria correspondente, com `meta refresh` e
`location.replace` — funcionam com e sem JavaScript.

## Páginas da #74

| seção | arquivo | frame do Figma |
| --- | --- | --- |
| CAPA | [`index.html`](index.html) | `4468:1434` |
| PRINCIPAL | [`74/principal.html`](74/principal.html) | `4424:20329` |
| GESTÃO 01 | [`74/gestao.html`](74/gestao.html) | `4424:20033` |
| GESTÃO 02 | [`74/gestao2.html`](74/gestao2.html) | `4424:19879` |
| MKT DIGITAL | [`74/mkt.html`](74/mkt.html) | `4424:19757` |
| PRODUTO | [`74/produto.html`](74/produto.html) | `4543:3135` |
| CONSUMIDOR | [`74/consumidor.html`](74/consumidor.html) | `4424:19327` |
| DELIVERY | [`74/delivery.html`](74/delivery.html) | `4424:19499` |
| NOVO NEGÓCIO | [`74/negocio.html`](74/negocio.html) | `4424:19580` |
| ACADEMIA ASSAÍ | [`74/academia.html`](74/academia.html) | `4424:19140` |
| NOTÍCIAS DO ASSAÍ | [`74/noticias2.html`](74/noticias2.html) | `4424:19218` |
| EXPEDIENTE | [`expediente.html`](expediente.html) | `1624:984` (da #73) |
| EDITORIAL | [`editorial.html`](editorial.html) | `1624:798` (da #73) |
| PARCEIROS | [`parceiros.html`](parceiros.html) | `1624:891` (da #73) |
| PARCEIRO 1–5 | [`parceiro-1.html`](parceiro-1.html) … [`parceiro-5.html`](parceiro-5.html) | `1659:541` (da #73) |

Ainda não existem: COLUNA e DOWNLOAD. No menu ficam como `#`.

## Arquitetura

Todo o conteúdo editorial fica em **fluxo normal**. `position: absolute` é
usado só na camada de decoração e no que de fato sangra, gira ou se sobrepõe.
Blocos de texto não têm altura fixa; só as `<section>` carregam `min-height`
para preservar o ritmo vertical do Figma.

**Atenção: há dois tipos de página, e a diferença importa muito na hora de
inserir conteúdo.**

- **Decoração por bloco** (PRINCIPAL, PRODUTO, ACADEMIA, CAPA): cada
  `<section class="bl">` tem sua própria `.backdrop`. Inserir conteúdo entre
  blocos empurra tudo junto, sem efeito colateral.
- **Decoração global** (GESTÃO, MKT, CONSUMIDOR): uma `.art-bg` única, com as
  decorações em coordenadas absolutas dentro da `.art`. Inserir conteúdo no
  fluxo empurra **só o texto** — as decorações ficam para trás e a página
  quebra. É preciso somar o mesmo deslocamento ao `top` de cada decoração
  abaixo do ponto de inserção, às `matrix()` (o 6º valor é o deslocamento
  vertical) e ao `min-height` da `.art`.

Para descobrir o deslocamento: insira o conteúdo, meça no navegador quanto o
primeiro elemento de texto seguinte desceu e aplique exatamente esse valor.
Cuidado com colapso de margem — na MKT o texto desceu 438 enquanto a conta
ingênua dava 440.

## Invólucro (shell)

Duas camadas:

- **Casca do desktop** — uma só, para as duas edições (todas as páginas da
  raiz, da `74/` e da `73/`). Ver "Casca do desktop" abaixo.
- **Shell de cada edição** — mobile e cabeçalho da coluna, que dependem do HTML
  de cada edição:
  - #74 (capa, expediente e as matérias da `74/`): `css/shell.css` depois do
    CSS da página e `js/shell.js` antes do JS da página;
  - #73 (a `73/`, as `categoria-*.html`, EDITORIAL, PARCEIROS e
    `74/parceiro-*.html`): `73/css/revista-73-shell.css` e
    `73/js/revista-73-menu.js`.

Shell da #74:

- **Mobile**: menu horizontal no HEAD. Em telas com menos de 402px (quase todo
  celular real), o `js/shell.js` reduz o `.page` com
  `transform: scale(largura / 402)` e o `css/shell.css` corta a sobra com
  `overflow-x: clip` — sem isso a coluna de 402px estourava a tela e dava
  rolagem lateral (a simulação do Chrome não mostra). Quem precisa converter px
  de tela em px de CSS (o `scroll-fx` e o arrasto dos carrosséis, `px(e)`) lê a
  escala de `window.ShellFit.escala()`.
  **Foi `zoom` até a 74-69, e não pode voltar a ser:** o `zoom` refaz o layout
  já na escala reduzida, e cada linha de texto arredonda para o pixel do
  aparelho. As seções encolhem alguns décimos cada, isso **acumula** página
  abaixo (na MKT em 390px, −46px no fim) e o texto sai do lugar das decorações,
  que são absolutas e não encolhem — o sintoma era o título "VAMOS AO PASSO A
  PASSO?" subindo para cima do celular. Com `transform` o layout é calculado nos
  402px do Figma e só depois reduzido, então tudo escala junto (desvio medido:
  0,0px). Em troca, a caixa no fluxo mantém a altura de 402px, e o `shell.js`
  dá ao `body` a altura reduzida (remedida por `ResizeObserver`, porque
  acordeões e congelamentos mudam a altura). Nas páginas que congelam a tela, o
  invólucro do congelamento também precisa da altura reduzida — ver armadilha 8.
- **Desktop (≥ 1024px)**: a faixa cinza do HEAD some (a casca assume a
  navegação) e o HEAD fica com 141px.

### Casca do desktop

Figma: frame "Desktop - 1" (`2331:3157`). Lateral esquerda (logo, edição, menu
num painel, botão "Edições anteriores") e lateral direita (redes sociais e QR
"Ler no celular"), com a coluna de 402px entre elas, sobre fundo branco.

| arquivo | o quê |
| --- | --- |
| [`css/shell-desktop.css`](css/shell-desktop.css) | tudo da casca, **e a posição da coluna** no desktop. Entra por último no `<head>` |
| [`js/shell-desktop.js`](js/shell-desktop.js) | monta o QR com o endereço da página aberta; baixa `js/vendor/qrcode-generator.min.js` (MIT) só quando a lateral direita aparece |
| [`scripts/shell_sync.py`](scripts/shell_sync.py) | **gera o markup** da casca em todas as páginas a partir de um modelo só |
| `assets/shell/` | logo e ícones das redes (`rede-*.svg`) |

**Não edite a casca no HTML.** O markup fica entre os comentários
`CASCA DESKTOP` … `/CASCA DESKTOP`, logo depois do `<body>`. Para mudar menu,
textos, redes ou links, mude o modelo em `scripts/shell_sync.py` e rode:

```bash
python scripts/shell_sync.py            # todas as páginas
python scripts/shell_sync.py --check    # só lista o que mudaria
```

O script calcula por página o prefixo dos caminhos (raiz ou `../`), o texto da
edição (`73/`: "Edição #73 · Jul-Ago/2026"; o resto: "#74 · Setembro/2026") e
o item ativo. Nas páginas da `73/`, EDITORIAL, PARCEIROS e EXPEDIENTE abrem as
versões da própria `73/`; a `73/download.html` tem um item DOWNLOAD a mais
(`EXTRAS` no script). **Trava:** se o menu gerado para uma página não tiver os
mesmos itens, na mesma ordem e com os mesmos links do que ela tem hoje, a
página não é gravada e a diferença é listada (`--forcar` grava assim mesmo,
quando a mudança de menu for intencional).

Comportamento:

- **Largura**: ≥ 1920px, exatamente o Figma (lateral esquerda em x:225, coluna
  em x:733, lateral direita em x:1433), centralizado em telas maiores. De 1200 a
  1919px, os quatro espaços (margem, vão, vão, margem) encolhem na mesma
  proporção. De 1024 a 1199px, some a lateral direita. Abaixo de 1024px não há
  casca.
- **Altura**: as duas laterais são fixas (não rolam com a página).
  - Esquerda: ocupa a altura da tela. Os espaços verticais são múltiplos de
    `--casca-u`, que vale 1px em telas com 987px de altura útil ou mais e
    encolhe abaixo disso para a lateral caber inteira. **O logo (124px) e os
    textos não encolhem.** Piso de 0,35px: abaixo de ~604px o menu rola por
    dentro. A conta (398px fixos + 589 × u) está no CSS e depende do número de
    itens do menu — mudou o menu, refaça.
  - Direita: a 50px da base, medidas do Figma. Some em janelas com menos de
    540px de altura.
- **Desvios do Figma** (de propósito): o menu usa 12,58px em todos os itens (o
  código do Figma diz 14,39px nas seções, mas o desenho mostra 12,58px) e o
  passo médio de 46px entre eles (o Figma é irregular); sem COLUNA e DOWNLOAD,
  o painel é mais curto e o botão sobe junto; ícones e QR centralizados na
  lateral direita (no Figma, ~6px à esquerda).
- **Links de menu abrem em nova aba** (`target="_blank" rel="noopener"`), em
  todos os menus: o da casca (gerado pelo script), o `head-nav` mobile da #74
  e o `head-menu` da #73/categorias. Página nova precisa vir assim; os `#`
  (COLUNA) ficam sem. O mesmo vale para os links das matérias (`74/…`,
  `73/…`) nos cards da capa e nas `categoria-*.html`.
- **"Edições anteriores"** abre https://www.assai.com.br/revistas em nova aba
  (`EDICOES_ANTERIORES` no script).

Os scripts de QA (`shot.py`, `probe_*.py`) escondem a `.casca` antes de medir.

## Carrosséis e banners

Todos os carrosséis arrastam com **mouse e dedo** (pointer events; no toque a
rolagem vertical da página segue funcionando via `touch-action: pan-y`), andam
item por item e param nas pontas.

| onde | o quê |
| --- | --- |
| `74/principal.html` | carrossel da matéria · citação com arrasto horizontal · carrossel de 5 banners com bolinhas |
| `74/gestao.html` | carrossel de 6 cards |
| `74/academia.html` | galeria de 5 cards de prêmios (também corre com o scroll, pelo `pin-horizontal`) |
| `74/mkt.html` | galeria de rolagem contínua (uma imagem só) |
| `index.html` | banner fixo depois da primeira linha de cards |
| `74/mkt.html`, `74/produto.html`, `74/consumidor.html` | banner rotativo |

**Setas invertidas de propósito:** a da esquerda avança e a da direita volta,
simulando que ela "puxa" o conteúdo para o seu lado.

**Banner rotativo:** o HTML já traz a primeira imagem (aparece mesmo sem
JavaScript) e um `data-ad-random` com a lista; o JS da página sorteia um item e
troca `src` e `alt`. Só uma imagem é baixada por visita.

**Ao inserir banner em página de decoração global**, leia a seção Arquitetura.
Na PRODUTO houve outro detalhe: o banner caía sobre o morango
(`.trabalho-detalhe`, absoluto), e foi preciso dar folga no topo.

## Efeitos de scroll e de entrada (GSAP)

Efeitos amarrados ao scroll e efeitos de entrada (ao carregar) ficam num
componente compartilhado entre edições,
[`js/scroll-fx.js`](js/scroll-fx.js) (GSAP 3.15.0 + ScrollTrigger via jsDelivr).
A página só marca o HTML com `data-fx` — nada de JS por página. Sem JS, ou com
"reduzir movimento" no sistema, tudo fica como no CSS.

| efeito | o que faz | em uso |
| --- | --- | --- |
| `card-accordeon` (scroll) | itens começam fechados e crescem com o scroll, empurrando o que vem abaixo; fecham ao subir | `74/principal.html` (cards bege de `.bl-gen`) |
| `pin-horizontal` (scroll) | quando o centro do trilho chega ao meio da tela, a tela inteira congela e o scroll corre só o trilho (texto ou galeria) para o lado (1:1); no fim, a página volta a rolar. Vários por página | `74/principal.html` (citação `.bl-quote` e carrossel `.bl-carousel`); `74/gestao.html` (carrossel `.s-carrossel`); `74/academia.html` (galeria de prêmios `.gallery`, mantendo setas e arrasto: o carrossel anda pelo `scrollLeft`) |
| `card-stack` (scroll) | os cards se empilham com o scroll: cada um para no alto da tela deixando uma faixa do anterior à mostra, e o último empurra a pilha para fora | `74/consumidor.html` (os 3 cards coloridos: nome, foto e embalagem) |
| `pin-sequencia` (scroll) | a tela congela e passa uma sequência: a foto ocupa a tela inteira e os balões de texto atravessam de baixo para cima, um de cada vez; quando um sai pelo topo, o seguinte entra por baixo e a foto troca em fade cruzado | `74/negocio.html` (as 3 fotos e os 3 balões da história do primeiro pudim) |
| `orbit-in` (scroll contínuo) | o elemento percorre a curva de uma elipse do layout enquanto cresce e gira, preso ao scroll; termina na posição do CSS | `74/gestao2.html` (celular sobre o arco branco) |
| `slide-in-up` (scroll disparado) | ao passar da sua linha perto do fundo da tela, cada item aparece sem fade na borda de baixo e sobe o caminho inteiro até o lugar, em cascata e em ordem estrita; desce e se esconde ao voltar. Com `data-fx-passo`, as entradas ficam a N px de scroll uma da outra | `74/principal.html` (lista `.pacts`, margem 200); `74/gestao.html` (cards de "a conta", margem 200, passo 200) |
| `typewriter` (entrada) | os textos são digitados letra a letra, um de cada vez: o primeiro aparece, é apagado de trás para frente e o seguinte é digitado no lugar; com `data-fx-repetir`, em loop | `74/mkt.html` (o hero: "Não engane seu cliente com IA" dá lugar a "mas aprenda com ela") |
| `reveal-wipe` (entrada) | o texto é descoberto de um lado ao outro, como uma cortina que abre (`clip-path`); nada se move nem muda de opacidade. Refaz toda vez que volta à tela | `74/delivery.html` (citação "O que oriento é que…") |
| `popcorn-pop` (entrada) | as letras pipocam: cada uma surge do nada, subindo e girando um pouco, em ordem aleatória e com quique; refaz toda vez que o texto volta à tela (precisa do SplitText) | `74/delivery.html` (título "Descontos fantasmas"); `74/academia.html` (título "Preparados para votação pública" e a citação `.quote-minuto`) |
| `magnetic-pull` (entrada) | ao carregar, as letras do texto vêm de posições e rotações aleatórias e se juntam no lugar; no fim, o HTML volta ao original (precisa do SplitText) | `74/gestao2.html` (título da abertura) |
| `scale-up` (entrada) | na abertura, os itens crescem a partir da base, em cascata; fundo opcional só durante a entrada | `74/principal.html` (cúpulas do hero) |
| `pop-in` (entrada) | os itens surgem um de cada vez — com "pop", com `fade` (só aparecendo), com `fade-up` (subindo com fade) ou com `fade-right` (vindo da esquerda) ou `fade-left` (vindo da direita) — na abertura, ou a cada vez que o bloco/grupo entra na tela (recomeça ao voltar); depois podem balançar (girar) e/ou flutuar sem parar | `74/gestao.html` (abertura: bisnaga com balanço 7°, gotas flutuando 10px; grupos: sachês com 0,5s entre eles, os 3 sachês pequenos em `fade-up` com 0,5s, e o balão da frase); `74/mkt.html` (as 3 ferramentas de IA e os 6 itens do passo a passo em `fade-right`, 0,5s, ao chegar à tela); `74/academia.html` (foto do hero em `fade-up`, 40px, 0,9s, ao carregar; os 5 números do mapa com "pop", 0,7s entre eles, ao chegar à tela); `74/noticias2.html` (os 8 ícones e a sacola da `.gallery`, "pop", 0,7s, a cada vez que o conjunto chega a 100px da base) |
| `drop-in` (entrada) | os itens caem da borda de cima do bloco até o lugar, com fade, um de cada vez (0,7s), quando o bloco chega à tela; depois podem flutuar. Recomeça ao voltar à tela | `74/noticias2.html` (os 3 cifrões do bloco do arroz, flutuando 10px, 30% mais rápido) |
| `pop-shake` (entrada) | a peça surge com "pop" e depois chacoalha em rajadas: 3 balançadas rápidas, 2s parada, e repete sem parar; eixo configurável | `74/produto.html` (o morango da abertura, 1s de atraso, balançando pelo cabinho) |
| `slide-in-left` (entrada) | ao carregar, o elemento desliza para a esquerda, vindo de fora do bloco pela direita (1,5s) | `74/principal.html` (foto do hero) |

Efeito de entrada exige um trecho anti-piscada no `<head>` da página (está na
skill).

Catálogo completo, atributos, checklist (atenção às páginas de **decoração
global**) e verificação: [`.claude/skills/scroll-fx/SKILL.md`](.claude/skills/scroll-fx/SKILL.md).

### Procedimento (validado no `card-accordeon`)

**Aplicar um efeito do catálogo** — um pedido de uma linha basta:
*"aplica o `card-accordeon` nos cards X da página Y"*. A skill `scroll-fx` é
carregada sozinha pelo Claude Code (fica em `.claude/skills/`) e cuida do resto:

1. Confere o tipo de decoração da página (por bloco: ok; global: decidir antes).
2. Liga o GSAP + `../js/scroll-fx.js` no fim do `<body>` e marca o HTML com
   `data-fx` / `data-fx-item`. Ajustes finos vão em atributos
   (`data-fx-inicio`, `data-fx-ritmo`), sem tocar no JS.
3. Verifica em 402px e 360px, descendo e subindo, e com a fonte atrasada.

**Criar um efeito novo** (fora do catálogo):

1. Descrever o comportamento: elemento, movimento, quando começa/termina, o que
   acontece ao rolar para cima.
2. Implementar com a skill `gsap-animar-html` (inventário → auditoria → código
   em camada separada → verificação), validar na página e aprovar visualmente.
3. Promover a componente: função em `js/scroll-fx.js`, registrada em `efeitos`,
   e documentada na skill `scroll-fx` (HTML de exemplo, atributos, checklist).
   Daí em diante ele entra no catálogo e vale para todas as edições.

Regras que o procedimento garante: nenhum HTML/CSS existente é alterado além dos
atributos `data-fx`; o estado inicial vai no JS (sem JS a página fica como no
CSS); nada mede layout antes de `document.fonts.ready`; ajuste feito no
componente vale para todas as páginas que o usam.

Os probes da PRINCIPAL (`probe.py`) e da GESTÃO (`probe_gestao.py`) bloqueiam o
`js/scroll-fx.js` e medem o layout do CSS, sem as animações (cards abertos,
nada congelado, nada em escala 0). Página nova com efeitos: faça o mesmo no
probe dela.

**Flutuação e balanço sem "degraus":** o `pop-in` (e o `drop-in`) põe
`will-change: transform` em quem flutua ou balança. Sem isso o Chrome arredonda o
item para o pixel inteiro a cada quadro, e um movimento lento e curto parece
andar um passo de cada vez.

**Texto + desenho animados juntos** (balão com frase, selo…): os dois precisam
estar no mesmo elemento. Na GESTÃO, o balão "É só um sachê de R$ 0,15." era o
desenho na `.art-bg` e a frase solta no fluxo; virou um `.balao` com o desenho
atrás da frase, no mesmo lugar (print antes/depois idêntico). O passo a passo
está na skill, no `pop-in`.

## Cache

CSS, JS e as imagens de banner levam `?v=74-NN` — hoje **74-112**. Ao mexer em
CSS ou JS, suba o número em todos os HTMLs de uma vez, **incluindo os da
`73/`** (eles também carregam a casca, `css/shell-desktop.css`):

```bash
sed -i -E 's/\?v=74-[0-9]+/?v=74-113/g' *.html 74/*.html 73/*.html
```

Use a expressão (`74-[0-9]+`), não o número exato: trocar só `74-79` deixava
para trás os links que já estavam em outra versão (a capa ficou com `base.css`,
`shell.css`, `shell.js` e `capa.js` presos em 74-79 enquanto o resto ia a
74-107).

Os arquivos da #73 levam `?v=73-NN` — hoje **73-33** para
`73/css/revista-73-shell.css`, `73/js/revista-73-menu.js` e `73/css/home.css`.
Mexeu num deles? Suba as referências a ele em `*.html 74/*.html 73/*.html`.

A versão fica dentro do HTML, então os HTMLs precisam subir para o cache
limpar. Se a página continuar quebrada depois do deploy, o HTML pode estar em
cache no servidor ou na CDN. Para checar, no console da página em produção:

```js
fetch('css/capa.css?bust='+Date.now()).then(r=>r.text()).then(t=>console.log(t.includes('.banner')))
```

`false` = o arquivo novo não subiu. `true` = subiu, e o problema é cache do
HTML.

## Analytics

Dois contêineres do Google Tag Manager (`GTM-MS6VK9B` e `GTM-W6GXJGP7`) no
`<head>` de toda página, logo depois do `<meta charset>` — mesmo snippet da
#73. Página nova precisa levar o bloco junto.

Os scripts de QA bloqueiam os domínios do Google, para não sujar o Analytics a
cada execução.

## Verificação

```bash
python scripts/shot.py 74/principal.html reference/render.png 402
python scripts/compare.py reference/original_native.png reference/render.png reference/cmp 800
python scripts/probe.py            # e um probe_<pagina>.py por página
```

Os `probe_*.py` medem a posição real de cada elemento-chave contra as
coordenadas do Figma. Eles escondem a casca do desktop antes de medir e
bloqueiam o GTM. Quando uma inserção desloca a página de propósito (banner, bloco novo), o
deslocamento é somado às posições esperadas, com o motivo anotado no topo do
arquivo.

**Estado atual** (medido na troca da casca, 74-108; os mesmos números antes e
depois dela):

| página | resultado |
| --- | --- |
| gestao, gestao2, produto, consumidor, delivery, academia, mkt, expediente | 0 fora de posição |
| principal | 1/53 |
| negocio | 5/58 |
| noticias2 | 9/30 |
| capa | 21/32 — desde os cards com vídeo (commit `c21428c`) |

Os pendentes vêm de mudanças posteriores aos probes, não da casca. Se as
posições novas forem as desejadas, basta atualizar o valor esperado no probe.

## Armadilhas encontradas

1. **Formatos diferentes da extensão da URL.** `imgImg41901` é JPG e
   `imgSound1` é um GIF animado, ambos servidos como `.png` pelo Figma.

2. **`RaspoutineMedium_TB.otf` quebrada no Chrome.** Glifos acentuados usam a
   forma obsoleta `seac`; o Chrome lê largura 229 em vez de 562 e o "ó" cola no
   "c". Use `fonts/RaspoutineMedium-fix.otf`.

3. **Recortes de imagem com a rotação do preenchimento errada no codegen.** Na
   GESTÃO, o saco e as gotas da abertura são recortes de `Rectangle 1457` com
   rotação/espelho *dentro* do preenchimento, que o código exportado não traz:
   aplicar os percentuais ao pé da letra mostra só um canto. Não use arte
   composta (a antiga `heroArte.png` juntava tudo e impedia animar as peças).
   Solução: baixe o original do preenchimento (vem com fundo transparente) e
   ajuste cada peça contra o `get_screenshot` do nó — casamento de pontos
   (SIFT, OpenCV) para peças com textura, silhueta + cor para as pequenas —, e
   gere PNG 2x por peça. Assim saíram `hero-saco.png` e `hero-gota1..5.png`
   (as gotas 3–5 conferiram com o recorte literal; saco e gotas 1–2, não).

4. **Coordenadas de nós girados.** O `get_metadata` devolve a geometria sem a
   rotação; para nós girados vale o `top`/`left` do código gerado.

5. **Ordem de pintura** no bloco "história" da PRINCIPAL: a foto fica abaixo
   das curvas e do preenchimento vermelho.

6. **Espaço entre parágrafos = 20px**, não 22: no Figma a separação é um
   parágrafo vazio, ou seja, uma linha do corpo de 18px.

7. **Coordenadas do rodapé** são relativas ao componente RODAPE, não à barra
   preta (que começa em `top: 45px` dentro dele).

8. **Vão em branco depois do rodapé, só no mobile (< 402px), nas páginas que
   congelam a tela** (`pin-horizontal`, `pin-sequencia`: PRINCIPAL, GESTÃO,
   GESTÃO 2, MKT, NOVO NEGÓCIO, ACADEMIA). O `.page` reduzido por `transform`
   continua ocupando no layout a altura original; sem congelamento o navegador
   ignora a sobra, porque mede o fim da página pela caixa transformada. Mas o
   congelamento embrulha a coluna em `.fx-congela-fora` / `.fx-congela`, e esses
   invólucros mediam a altura **sem** a redução: a diferença, altura × (1 −
   escala), virava branco depois do rodapé — ~260px em 390px e até ~1000px em
   360px (cresce quanto mais estreita a tela; a simulação do Chrome mostra).
   Correção no `js/scroll-fx.js` (`alturaReduzida`): o invólucro que embrulha o
   próprio `.page` recebe a altura já reduzida, remedida a cada quadro de
   scroll. Para conferir: role até o fim em 390 e 360px — o rodapé tem que
   encostar na base da tela. Efeito novo que embrulhe a coluna precisa do mesmo.

8. **Colapso de margem.** Na GESTÃO, a margem do primeiro filho de uma
   `<section>` escapava e empurrava a seção inteira. Resolvido com
   `display: flow-root` em `.s`.

9. **`:nth-of-type` na capa.** `css/capa.css` posiciona as linhas de cards
   contando os `div` irmãos. Conteúdo novo ali precisa ser `<figure>` ou outro
   elemento — um `<div>` desloca as regras de todas as linhas seguintes.

10. **Especificidade vence o gap.** `.art-bg > span { display: block }` é mais
    específico que `.d-stripes { display: flex }`, e o `gap` era ignorado — as
    listras da tabela de CMV saíam do passo das linhas. Resolvido com
    `.art-bg > .d-stripes`.

11. **Texto rasterizado dentro de arte do Figma.** A antiga `heroArte.png` da
    GESTÃO trazia o título e o olho já desenhados, e apareciam borrados atrás do
    texto real da página. Motivo a mais para exportar peça por peça.

12. **z-index em componente compartilhado.** Na capa, o `z-index` estava na
    barra preta do rodapé e escondia os ícones, irmãos dela. Ele pertence ao
    `.foot` inteiro.

13. **`zoom` desalinha a decoração no mobile.** O `zoom` refaz o layout já na
    escala reduzida, e cada linha de texto arredonda para o pixel do aparelho.
    Cada seção encolhe alguns décimos, o erro **acumula** página abaixo (na MKT
    em 390px: −1,8px na segunda seção, −45,9px na última) e o texto sai do lugar
    das decorações, que são absolutas na `.art` e não encolhem — o título "VAMOS
    AO PASSO A PASSO?" subia para cima do celular, a frase seguinte colava na
    elipse, e o mesmo em outros blocos de toda página de decoração global. O
    layout em 402px estava certo, e no desktop nada aparecia: só reproduz abaixo
    de 402px. Por isso o `.page` é reduzido com `transform: scale`, que calcula o
    layout nos 402px do Figma e só depois reduz (desvio medido: 0,0px). Ver
    Invólucro. **Não volte a usar `zoom` aqui.** O shell da #73 (usado também
    pelas categorias) já reduz com `transform`, no `73/js/revista-73-menu.js`.

14. **Altura do monitor não é altura da tela.** Num monitor de 1080px, o
    navegador deixa ~940px úteis (barras e abas); num notebook, ~730px. A
    primeira casca tinha 1080px de altura e rolava junto com a página: em
    qualquer tela real, a lateral direita começava cortada e o logo sumia ao
    rolar. Teste a casca com a altura útil (1920×945, 1536×730, 1366×657),
    não com a do monitor.

15. **Regra genérica de link vence a cor do botão.** `.casca a { color:
    inherit }` pesa mais que `.casca-pilula { color: #fff }`, e o texto de
    "Edições anteriores" (um link) saía escuro. Os resets da casca usam
    `:where(.casca) …`, que tem peso zero.

## Assets

`assets/_manifest.txt` e `74/assets/<pagina>/_manifest.txt` ligam cada arquivo
à constante do código gerado pelo Figma, o que facilita ressincronizar quando o
design mudar.

Os banners ficam em `74/assets/banners/`. As capas das categorias ficam em
`assets/categorias/` — `<materia>74.png` para a #74 e o nome da seção para a
#73, todas em 400×474.

As fontes (FS Lola, Raspoutine) são licenciadas: cuidado ao tornar o
repositório público.
