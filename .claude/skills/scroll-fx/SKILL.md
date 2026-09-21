---
name: scroll-fx
description: >-
  Aplica os efeitos de scroll prontos da Revista Assaí (js/scroll-fx.js, GSAP +
  ScrollTrigger) marcando o HTML com data-fx, sem escrever JS por página. Use
  quando o usuário pedir para aplicar um efeito do catálogo (ex.: "aplica o
  card-accordeon nos cards X da página Y"), ou pedir cards/listas que abrem e
  fecham acompanhando o scroll, empurrando o conteúdo abaixo. Para um efeito
  novo que não está no catálogo, use a skill gsap-animar-html e depois
  acrescente o efeito aqui.
---
# Efeitos de scroll da revista (scroll-fx)

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

## Catálogo

### `card-accordeon`

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

## Antes de aplicar (checklist)

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
5. **Efeitos abaixo de um `card-accordeon`** que usem ScrollTrigger devem somar
   `ScrollFx.offsetAcima(el) * ScrollFx.zoom()` à posição medida — senão
   disparam cedo (medidos com os itens de cima ainda fechados).

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
  `prefers-reduced-motion: reduce`, os itens ficam abertos como no CSS.
- `ScrollTrigger.refresh()` depois das imagens (`load`).

## Verificação (sempre, em 402px e 360px)

Role por posições do gatilho e meça a altura de cada item e o topo do bloco
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

1. Implemente como função `nomeDoEfeito(contêiner)` em `js/scroll-fx.js` e
   registre em `efeitos` (`"nome-do-efeito": nomeDoEfeito`).
2. Se mudar a altura da página, registre em `encolhedores` (veja o
   `card-accordeon`).
3. Documente aqui: HTML de exemplo, atributos, checklist específico e onde está
   em uso.
