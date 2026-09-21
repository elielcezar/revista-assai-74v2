---
name: scroll-fx
description: >-
  Aplica os efeitos prontos da Revista Assaí (js/scroll-fx.js, GSAP +
  ScrollTrigger) marcando o HTML com data-fx, sem escrever JS por página:
  efeitos de scroll e efeitos de entrada ao carregar a página. Use quando o
  usuário pedir para aplicar um efeito do catálogo (ex.: "aplica o
  card-accordeon nos cards X da página Y", "slide-in-left na imagem do hero",
  "pin-horizontal na citação", "slide-in-up nos itens da lista"), pedir
  cards/listas que abrem e fecham acompanhando o scroll empurrando o conteúdo
  abaixo, uma frase/faixa larga que corre para o lado enquanto a tela fica
  congelada (scroll horizontal com a página travada), itens de lista que entram
  subindo em cascata conforme chegam à tela, ou um elemento que entra deslizando
  ao carregar a página.
  Para um efeito novo que não está no catálogo, use a skill gsap-animar-html e
  depois acrescente o efeito aqui.
---
# Efeitos de scroll e de entrada da revista (scroll-fx)

O código mora em **`js/scroll-fx.js`** (raiz, compartilhado entre edições). Esta
skill não repete o código: diz quando usar cada efeito, o que conferir antes e
como verificar. **Não copie a lógica para a página** — ajuste no componente, e o
ajuste vale para todas.

## Como ligar numa página

1. No fim do `<body>`, depois dos scripts da página:
   ```html
   <!-- animações de scroll (camada separada; sem elas a página fica como no CSS) -->
   <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
   <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/ScrollTrigger.min.js"></script>
   <script src="../js/scroll-fx.js?v=74-NN"></script>
   ```
   (caminho relativo à pasta da edição; `?v=` = versão de cache atual do README)
2. Marque o HTML com `data-fx` (veja o catálogo). Só atributos — nada de CSS novo.
3. **Só se a página usar efeito de entrada:** o trecho anti-piscada no `<head>`,
   logo depois do `<meta name="viewport">`. Ele esconde os elementos antes da
   primeira pintura (senão aparecem na posição final por um instante e depois
   saltam para fora); o componente assume em seguida e, se ele não rodar,
   reaparecem sozinhos em 3s. Sem JS a classe nunca é posta: nada some.
   ```html
   <!-- scroll-fx: esconde os efeitos de entrada antes da primeira pintura; o
        js/scroll-fx.js assume depois. Se ele não rodar, reaparecem em 3s. -->
   <script>document.documentElement.classList.add("fx-espera");setTimeout(function(){document.documentElement.classList.remove("fx-espera")},3000);</script>
   <style>.fx-espera [data-fx="slide-in-left"]{visibility:hidden}</style>
   ```
   No `<style>`, liste **cada efeito de entrada usado na página** (seletores
   separados por vírgula).

## Catálogo

Três tipos: **scroll contínuo** (acompanha a rolagem 1:1, vai e volta),
**scroll disparado** (dispara uma animação ao cruzar um ponto da tela, e desfaz
ao voltar) e **entrada** (roda uma vez ao carregar a página).

### `card-accordeon` — scroll

Itens começam **100% fechados** (altura e padding verticais em 0) e **crescem de
verdade** conforme o scroll, empurrando o que vem abaixo. Cada item começa quando
o topo dele chega ao ponto de início da tela, e nunca antes do anterior terminar
— rolando pouco, só o primeiro abre um pouco. Rolando para cima, fecham ao
contrário. `scrub: true` (acompanha o scroll 1:1).

```html
<section class="bl bl-gen" data-fx="card-accordeon">
  …<div class="gen-card" data-fx-item>…</div>
  …<div class="gen-card" data-fx-item>…</div>
</section>
```

| atributo (no contêiner) | padrão | efeito |
|---|---|---|
| `data-fx-inicio` | `80%` | ponto da tela, a partir do topo, que dispara cada item (maior = começa antes) |
| `data-fx-ritmo` | `1.5` | px de scroll por px de item aberto (maior = abre mais devagar) |

Em uso: `74/principal.html`, cards bege de `.bl-gen`.

### `pin-horizontal` — scroll

Quando o centro do trilho chega ao ponto da tela, **a tela inteira congela**:
tudo o que está visível (o fim do bloco de cima, o começo do de baixo) fica
parado e preenchido, e o scroll vertical passa a rolar **só o trilho** para o
lado, 1:1 (1px de scroll = 1px de texto). Quando o trilho chega ao fim, a página
volta a rolar de onde parou. Rolando para cima, desfaz.

```html
<section class="bl bl-quote" data-fx="pin-horizontal">
  …<div class="quote-marquee" data-fx-item>
     <p>"Uma frase bem mais larga que a tela…"</p>
   </div>
</section>
```

| atributo (no contêiner) | padrão | efeito |
|---|---|---|
| `data-fx-inicio` | `50%` | ponto da tela, a partir do topo, onde o centro do trilho trava |

**Como funciona (não refaça com o pin do ScrollTrigger):** o componente põe o
`.page` dentro de dois invólucros — um `sticky` que gruda a coluna inteira e um
espaçador com a altura do percurso do texto. O ponto da trava é lido do layout
real a cada frame, e o texto anda pelo `scrollLeft` do trilho. O pin do
ScrollTrigger foi testado e **falhou**: com o zoom do mobile a coluna encolhia
(360 → 322px) e, com um `card-accordeon` acima, travava no lugar errado e
saltava 73px.

Checklist:
- **Um por página** (congela a coluna inteira; o segundo é ignorado).
- O trilho (`data-fx-item`) tem `overflow-x` (`auto`/`hidden`) e conteúdo mais
  largo que ele — o percurso é `scrollWidth - clientWidth`. Se couber, nada trava.
- Não depende do tipo de decoração: a coluna inteira congela junto, então
  funciona também nas páginas de decoração global.
- Sem `position: sticky`/`fixed` que dependa do `.page` como pai direto de
  `body` (ele passa a ficar dentro de `.fx-congela`); a sidebar do desktop não
  é afetada.
- Se o trilho já tiver arrasto próprio (a citação da PRINCIPAL tem, em
  `js/principal.js`), ele continua funcionando: o efeito só escreve o
  `scrollLeft` enquanto o leitor rola.

Em uso: `74/principal.html`, citação (`.bl-quote` / `.quote-marquee`).

### `slide-in-up` — scroll disparado

Cada item fica **escondido** até o topo dele passar da sua linha (a `margem` px
do fundo da tela); aí **aparece sem fade** (100% de opacidade) e **sobe** até o
lugar. Cada item seguinte espera um pouco mais (cascata). Rolando de volta para
cima, **desce e se esconde** ao cruzar a mesma linha. Não acompanha o scroll
1:1: é uma animação de tempo fixo disparada pela posição.

```html
<ol class="pacts" data-fx="slide-in-up" data-fx-margem="200">
  <li data-fx-item>…</li>
  <li data-fx-item>…</li>
</ol>
```

| atributo (no contêiner) | padrão | efeito |
|---|---|---|
| `data-fx-margem` | `60` | px de tela acima do fundo em que o **1º** item entra (maior = entra mais tarde) |
| `data-fx-escalonamento` | `0.1` | cada item seguinte espera +10% dessa margem (margem 200 → 200, 220, 240…) |
| `data-fx-deslocamento` | `40` | px que o item sobe ao entrar (e desce ao sair) |
| `data-fx-duracao` | `0.6` | segundos |

**Como funciona (não refaça com gatilho do ScrollTrigger):** cada item lê a
**própria posição real a cada frame** e compara com a sua linha. A primeira
versão usava um gatilho pré-calculado do ScrollTrigger, corrigido pelo
deslocamento do `card-accordeon`/`pin-horizontal` acima — no navegador real,
depois de um recálculo (imagens carregando, resize), disparou ~380px atrasado.
Lendo a posição ao vivo, nada acima interfere.

Checklist:
- Os itens não podem ter `transform` nem `transition` de `transform`/`visibility`
  no CSS (o efeito anima `y` e troca `visibility`).
- Sem JS ou com "reduzir movimento", os itens ficam visíveis no lugar.

Em uso: `74/principal.html`, lista dos 5 acordos (`.pacts`), margem 200.

### `slide-in-left` — entrada

O elemento **desliza para a esquerda**: entra vindo de fora do bloco, pela
direita, até a posição final. Sempre opaco — o `overflow` do bloco esconde a
parte que ainda está fora, então parece entrar pela borda da tela (no mobile e
no desktop). Começa quando a imagem termina de carregar (limite de 4s),
desacelera no fim (`power2.out`) e devolve o elemento ao CSS ao terminar.
Precisa do trecho anti-piscada no `<head>`.

```html
<img src="…" data-fx="slide-in-left" alt="…">
```

| atributo (no próprio elemento) | padrão | efeito |
|---|---|---|
| `data-fx-duracao` | `1.5` | segundos |
| `data-fx-atraso` | `0` | segundos antes de começar |

Checklist: um ancestral precisa recortar (`overflow: hidden`/`clip`) — é ele que
esconde o elemento enquanto está fora; sem recorte, o elemento atravessaria a
tela. Não use num elemento que já tem `transform` no CSS (o efeito anima `x`).

Em uso: `74/principal.html`, foto do hero (`.hero-figure > img`).

## Antes de aplicar um efeito de scroll (checklist)

1. **Tipo de decoração da página** (README, seção Arquitetura). O
   `card-accordeon` muda a altura do documento.
   - **Decoração por bloco** (PRINCIPAL, PRODUTO, ACADEMIA, CAPA): ok, tudo abaixo
     desce junto.
   - **Decoração global** (GESTÃO, MKT, CONSUMIDOR): as decorações em
     coordenadas absolutas da `.art-bg` **não acompanham** — com os itens
     fechados elas ficam fora do lugar. Não aplique sem antes decidir com o
     usuário como tratar essas decorações.
2. **Contêiner = o bloco que deve encolher.** Se ele tiver `min-height`, o
   componente desconta dele, a cada frame, exatamente o que está fechado; aberto,
   volta ao valor do CSS e o layout é idêntico. Não mexa no CSS por causa disso.
3. **Itens = o que abre.** Precisam ter altura própria (ex.: `min-height` ou
   conteúdo). O componente põe `overflow: hidden` neles: confira que nada
   deveria transbordar para os lados (medir o texto contra a borda do item).
4. **Nada de `transition` em `height`/`padding`** nos itens (brigaria com o
   scrub).
5. **Efeitos abaixo de um `card-accordeon` ou `pin-horizontal`**: prefira ler a
   posição real a cada frame (como o `slide-in-up` e o `pin-horizontal`). Se
   precisar de um gatilho pré-calculado do ScrollTrigger, some
   `ScrollFx.offsetAcima(el) * ScrollFx.zoom()` à posição medida — mas saiba que
   isso depende do estado da página no momento do recálculo e já falhou no
   navegador real.

## O que o componente já resolve (não refaça)

- **Ancoragem de rolagem** do navegador desligada (`overflow-anchor: none`):
  com ela, conteúdo crescendo acima do ponto de leitura mexe no scroll e o scrub
  realimenta — os itens abririam sozinhos.
- **Zoom do mobile** (`js/shell.js`, abaixo de 402px): distâncias de scroll
  multiplicadas pelo zoom atual; recalcula no resize.
- **Fontes**: só inicia depois de `document.fonts.ready` — as medidas de
  altura dependem da fonte real (com a substituta, o espaço final do
  `min-height` sumia). Até lá a página fica como no CSS. Não meça nada de
  layout antes disso num efeito novo.
- **Vários acordeões na mesma página**: cada um mede sua posição como se os de
  cima já estivessem abertos.
- **Acessibilidade e falha**: sem JS, sem GSAP ou com
  `prefers-reduced-motion: reduce`, os efeitos não rodam e a página fica como no
  CSS (itens abertos, elementos de entrada já no lugar).
- `ScrollTrigger.refresh()` depois das imagens (`load`).

## Verificação (sempre, em 402px e 360px)

**Entrada:** com a imagem atrasada de propósito (~1,5s), o elemento não pode
aparecer no lugar antes de o efeito começar; ao final, sem `style` inline e na
posição do CSS (o `probe` da página confere).

**`pin-horizontal`:** role por posições da faixa congelada (início, 25%, 50%,
fim, depois) e meça: topo do `.page`, fundo do bloco de cima e topo do de baixo
**parados** (±1px) enquanto o `scrollLeft` do trilho vai de 0 ao máximo;
largura da coluna igual à da tela em 360px (zoom); sem overflow horizontal; no
desktop (1440px), coluna e sidebar na mesma posição que sem o efeito.

**`slide-in-up`:** role em passos pequenos pelo caminho real (passando por
acordeões e congelamentos acima) e anote, para cada item, a distância do topo ao
fundo da tela no momento em que aparece: deve bater com a linha dele (margem ×
(1 + escalonamento × índice)), dentro do tamanho do passo. Voltando para cima,
todos se escondem. **Teste também com recarga no meio da página** — foi aí que a
versão com gatilho pré-calculado falhou.

**`card-accordeon`:** role por posições do gatilho e meça a altura de cada item e o topo do bloco
seguinte (divida por `zoom` para comparar em px de CSS):

- no início: todos os itens com altura 0; o bloco seguinte sobe a soma das alturas;
- no meio do 1º: só o 1º parcialmente aberto;
- no fim: todos abertos e o bloco seguinte **exatamente** na posição sem JS;
- subindo: fecham na ordem inversa; parado: nada muda sozinho;
- sem erros de console;
- **com a fonte atrasada** (bloqueie `fonts/` por ~1s no teste, ou cache frio):
  um teste com a fonte já em cache passou enquanto o espaço final sumia no
  navegador de verdade.

O `probe` da página mede no topo, com os itens fechados: tudo abaixo do
acordeão aparece deslocado pela soma das alturas — esperado, não é regressão.

## Acrescentar um efeito novo ao catálogo

1. Implemente como função `nomeDoEfeito(elemento)` em `js/scroll-fx.js` e
   registre em `efeitos` (scroll: roda depois das fontes) ou em `entradas`
   (entrada: roda na hora, sem esperar fontes). Efeito de entrada entra também
   no seletor do trecho anti-piscada.
2. Se deslocar o que vem abaixo (mudar altura, congelar a tela), registre em
   `encolhedores` quantos px de CSS está deslocando (veja o `card-accordeon` e o
   `pin-horizontal`).
3. Congelar/travar: use a técnica do `pin-horizontal` (sticky + espaçador), não
   o `pin` do ScrollTrigger — este quebra com o zoom do mobile.
4. Disparar ao cruzar um ponto da tela: leia a posição real a cada frame (veja o
   `slide-in-up`), não um gatilho pré-calculado — este erra abaixo de efeitos
   que mudam a página.
5. Documente aqui: HTML de exemplo, atributos, checklist específico e onde está
   em uso.
