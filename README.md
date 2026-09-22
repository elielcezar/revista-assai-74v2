# Revista Assaí Bons Negócios

Site estático em HTML + CSS + JavaScript puro, sem build. Os arquivos do
repositório são o produto final. Duas edições convivem: a **#74** (atual) e a
**#73** (anterior), cada uma na sua pasta, com as listagens de categoria
compartilhadas na raiz.

## Estrutura

```
/                     index.html (capa da #74) · categoria-*.html (10) · expediente.html
                      editorial.html · parceiros.html · parceiro-1.html … parceiro-5.html
                      css/ (base, shell, capa, expediente, categoria-*) · js/ · fonts/
                      assets/ (capa, categorias, expediente, shell + ícones do head/rodapé)
/74/                  as 10 matérias da edição #74 + css/ + js/ + assets/
/73/                  edição #73 completa (repositório git próprio)
/73/_bkp_categorias/  as categorias antigas da #73, fora do ar
/scripts/             shot.py, compare.py e um probe_*.py por página
/reference/           renders de comparação (fora do git)
```

### Navegação

1. O visitante entra pelo `index.html`, a capa da #74.
2. O menu (horizontal no mobile, sidebar no desktop) leva para
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

`css/shell.css` entra por último no `<head>` e `js/shell.js` antes do JS da
página. O markup fica entre os comentários `INVÓLUCRO` … `/INVÓLUCRO`, logo
depois do `<body>`, e é igual em todas as páginas; só muda o `is-active`.

- **Mobile**: menu horizontal no HEAD. Em telas com menos de 402px (quase todo
  celular real), o `js/shell.js` aplica `zoom = largura / 402` no `.page` e o
  `css/shell.css` corta a sobra com `overflow-x: clip` — sem isso a coluna de
  402px estourava a tela e dava rolagem lateral (a simulação do Chrome não
  mostra). Os carrosséis dividem o movimento do dedo pelo zoom (`px(e)`) para o
  arrasto acompanhar o dedo.
- **Desktop (≥ 1024px)**: sidebar fixa de 313px (logo + navegação) com fundo
  `assets/shell/dt-bg-pattern.png`. A faixa cinza do HEAD some e o HEAD fica
  com 141px. A coluna de 402px fica em x:733 a partir de 1920px; abaixo disso
  sidebar e coluna se centralizam como um bloco, com a coluna 400px à direita
  da sidebar.

As páginas de categoria usam um shell próprio, herdado da #73:
`css/categoria-shell.css` e `js/categoria-menu.js`. EDITORIAL e PARCEIROS
na raiz usam o shell original da #73 (`73/css/revista-73-shell.css` e
`73/js/revista-73-menu.js`).

## Carrosséis e banners

Todos os carrosséis arrastam com **mouse e dedo** (pointer events; no toque a
rolagem vertical da página segue funcionando via `touch-action: pan-y`), andam
item por item e param nas pontas.

| onde | o quê |
| --- | --- |
| `74/principal.html` | carrossel da matéria · citação com arrasto horizontal · carrossel de 5 banners com bolinhas |
| `74/gestao.html` | carrossel de 6 cards |
| `74/academia.html` | galeria de 5 cards de prêmios |
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
| `pin-horizontal` (scroll) | quando o centro do trilho chega ao meio da tela, a tela inteira congela e o scroll corre só o trilho (texto ou galeria) para o lado (1:1); no fim, a página volta a rolar. Vários por página | `74/principal.html` (citação `.bl-quote` e carrossel `.bl-carousel`) |
| `slide-in-up` (scroll disparado) | ao passar da sua linha perto do fundo da tela, cada item aparece sem fade na borda de baixo e sobe o caminho inteiro até o lugar, em cascata; desce e se esconde ao voltar | `74/principal.html` (lista `.pacts`, margem 200) |
| `scale-up` (entrada) | na abertura, os itens crescem a partir da base, em cascata; fundo opcional só durante a entrada | `74/principal.html` (cúpulas do hero) |
| `pop-in` (entrada) | os itens surgem com "pop", um de cada vez — na abertura, ou em grupos que disparam quando chegam à tela; depois podem balançar (girar) e/ou flutuar sem parar | `74/gestao.html` (abertura: bisnaga com balanço 7°, gotas flutuando 10px; grupo: sachês com 0,5s entre eles) |
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

O `probe.py` da PRINCIPAL bloqueia o `js/scroll-fx.js` e mede o layout do CSS,
sem as animações (cards abertos, nada congelado).

## Cache

CSS, JS e as imagens de banner levam `?v=74-NN` — hoje **74-55**. Ao mexer em
CSS ou JS, suba o número em todos os HTMLs de uma vez:

```bash
sed -i 's/?v=74-55/?v=74-56/g' *.html 74/*.html
```

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
coordenadas do Figma. Eles escondem a sidebar antes de medir e bloqueiam o
GTM. Quando uma inserção desloca a página de propósito (banner, bloco novo), o
deslocamento é somado às posições esperadas, com o motivo anotado no topo do
arquivo.

**Estado atual:**

| página | resultado |
| --- | --- |
| capa, gestao, gestao2, produto, consumidor, delivery, negocio, academia, noticias2, expediente | 0 fora de posição |
| principal | 1/56 — `.carousel-nav--prev` foi movida de `-5px` para `15px` direto no CSS |
| mkt | 7/50 — `.hero-title2` está com `display: none` em `74/css/mkt.css`, o que sobe 28px o que vem depois |

Os dois pendentes vêm de mudanças feitas à mão, não de regressão. Se as
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

## Assets

`assets/_manifest.txt` e `74/assets/<pagina>/_manifest.txt` ligam cada arquivo
à constante do código gerado pelo Figma, o que facilita ressincronizar quando o
design mudar.

Os banners ficam em `74/assets/banners/`. As capas das categorias ficam em
`assets/categorias/` — `<materia>74.png` para a #74 e o nome da seção para a
#73, todas em 400×474.

As fontes (FS Lola, Raspoutine) são licenciadas: cuidado ao tornar o
repositório público.
