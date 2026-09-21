# Revista Assaí Bons Negócios

Site estático em HTML + CSS + JavaScript puro, sem build. Os arquivos do
repositório são o produto final. Duas edições convivem: a **#74** (atual) e a
**#73** (anterior), cada uma na sua pasta, com as listagens de categoria
compartilhadas na raiz.

## Estrutura

```
/                     index.html (capa da #74) · categoria-*.html (10) · expediente.html
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
5. O item CAPA, em qualquer página das duas edições, volta para o `index.html`
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

Ainda não existem: COLUNA, DOWNLOAD, EDITORIAL e PARCEIROS. No menu ficam
como `#`.

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

- **Mobile**: menu horizontal no HEAD.
- **Desktop (≥ 1024px)**: sidebar fixa de 313px (logo + navegação) com fundo
  `assets/shell/dt-bg-pattern.png`. A faixa cinza do HEAD some e o HEAD fica
  com 141px. A coluna de 402px fica em x:733 a partir de 1920px; abaixo disso
  sidebar e coluna se centralizam como um bloco, com a coluna 400px à direita
  da sidebar.

As páginas de categoria usam um shell próprio, herdado da #73:
`css/categoria-shell.css` e `js/categoria-menu.js`.

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

## Cache

CSS, JS e as imagens de banner levam `?v=74-NN` — hoje **74-21**. Ao mexer em
CSS ou JS, suba o número em todos os HTMLs de uma vez:

```bash
sed -i 's/?v=74-21/?v=74-22/g' *.html 74/*.html
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

3. **Recortes de imagem inválidos no codegen.** Na GESTÃO, os seis recortes de
   `Rectangle 1457` vieram com percentuais que mostram só um canto vazio. A
   arte foi extraída composta em `74/assets/gestao/heroArte.png`.

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

11. **Texto rasterizado dentro de arte do Figma.** O `heroArte.png` da GESTÃO
    trazia o título e o olho já desenhados, e apareciam borrados atrás do texto
    real da página.

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
