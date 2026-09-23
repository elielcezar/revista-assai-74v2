---
name: scroll-fx
description: >-
  Aplica os efeitos prontos da Revista Assaí (js/scroll-fx.js, GSAP +
  ScrollTrigger) marcando o HTML com data-fx, sem escrever JS por página:
  efeitos de scroll e efeitos de entrada ao carregar a página. Use quando o
  usuário pedir para aplicar um efeito do catálogo (ex.: "aplica o
  card-accordeon nos cards X da página Y", "slide-in-left na imagem do hero",
  "pin-horizontal na citação/no carrossel", "slide-in-up nos itens da lista"), pedir
  cards/listas que abrem e fecham acompanhando o scroll empurrando o conteúdo
  abaixo, uma frase/faixa larga que corre para o lado enquanto a tela fica
  congelada (scroll horizontal com a página travada — texto ou galeria/carrossel
  de imagens), itens de lista que entram
  subindo em cascata conforme chegam à tela, um elemento que entra deslizando
  ao carregar a página, formas de fundo que crescem em cascata na abertura
  ("scale-up nas cúpulas do hero"), ou peças/itens de lista que surgem um de cada
  vez com "pop", subindo com fade, ou entrando pela esquerda com fade
  ("fade-right"/"fade-in-right") — na abertura ou quando o bloco chega à tela — e
  depois ficam balançando/flutuando ("pop-in na bisnaga e nas gotas", "pop-in
  nos sachês", "fade-up com 0,5s entre os sachês pequenos", "os 3 itens entram
  com fadein-right"), ou um título cujas
  letras se juntam vindas de todo lado ao carregar ("magnetic-pull no h1"), ou
  um elemento que percorre uma curva do layout crescendo e girando conforme o
  scroll ("orbit-in no celular").
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
   <!-- só se a página usar magnetic-pull (quebra o texto em letras): -->
   <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/SplitText.min.js"></script>
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
   <style>.fx-espera [data-fx="slide-in-left"],.fx-espera [data-fx="scale-up"] [data-fx-item]{visibility:hidden}</style>
   ```
   No `<style>`, liste **cada efeito de entrada usado na página** (seletores
   separados por vírgula). Efeito aplicado no próprio elemento
   (`slide-in-left`) usa `[data-fx="…"]`; efeito de contêiner com itens
   (`scale-up`, `pop-in`) esconde os itens: `[data-fx="…"] [data-fx-item]` —
   esconder o contêiner inteiro sumiria também o que não anima (ex.: o
   `hero-wash`, ou o resto da `.art-bg` da GESTÃO).

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

**Como funciona (não refaça com o pin do ScrollTrigger):** o componente põe a
coluna dentro de dois invólucros — um `sticky` que gruda a coluna inteira e um
espaçador com a altura do percurso do trilho. O ponto da trava é lido do layout
real a cada frame, e o trilho anda pelo `scrollLeft`. **Vários por página:**
cada congelamento embrulha o anterior (stickies aninhados), mede a sua trava ao
vivo e se desfaz na ordem inversa. O pin do
ScrollTrigger foi testado e **falhou**: com o zoom do mobile a coluna encolhia
(360 → 322px) e, com um `card-accordeon` acima, travava no lugar errado e
saltava 73px.

Checklist:
- O trilho (`data-fx-item`) tem `overflow-x` (`auto`/`hidden`) e conteúdo mais
  largo que ele — o percurso é `scrollWidth - clientWidth`. Se couber, nada trava.
  Serve texto ou galeria: no carrossel da PRINCIPAL o trilho é a
  `.carousel-viewport` (382px, `overflow: hidden`) com a trilha de 2085px dentro.
- **Tire os controles próprios do trilho** — setas, arrasto, e qualquer
  `transform`/`transition` que mova o conteúdo: brigariam com o `scrollLeft`
  animado. No carrossel saíram os botões `.carousel-nav`, o bloco do carrossel
  em `js/principal.js` e o `cursor: grab`/`transition` do CSS (o probe também
  perdeu as entradas das setas). Arrasto que só mexe no `scrollLeft` pode ficar
  (a citação mantém o dela).
- Não depende do tipo de decoração: a coluna inteira congela junto, então
  funciona também nas páginas de decoração global.
- Sem `position: sticky`/`fixed` que dependa do `.page` como pai direto de
  `body` (ele passa a ficar dentro de `.fx-congela`); a sidebar do desktop não
  é afetada.
- Se o trilho já tiver arrasto próprio (a citação da PRINCIPAL tem, em
  `js/principal.js`), ele continua funcionando: o efeito só escreve o
  `scrollLeft` enquanto o leitor rola.

Em uso: `74/principal.html` — citação (`.bl-quote` / `.quote-marquee`, 2296px de
percurso) e carrossel da matéria (`.bl-carousel` / `.carousel-viewport`, 1703px),
os dois na mesma página; `74/gestao.html` — carrossel "quando a cortesia faz
sentido" (`.s-carrossel` / `.carousel-viewport`, 1358px), numa página de
decoração global (setas, arrasto e `transition` removidos, probe sem as setas).

### `card-stack` — scroll

Os cards **se empilham** conforme o leitor rola. Cada card para no alto da tela
e o seguinte sobe até encostar nele, deixando uma **faixa** do anterior à mostra
— é ela que diz que existe card embaixo. O último não trava: ao subir, ele
**empurra** a pilha inteira, que sai da tela mantendo as faixas à vista.
A página **não congela** e a altura do documento não muda.

```html
<div class="cards" data-fx="card-stack" data-fx-faixa="10" data-fx-topo="20">
  <section data-fx-item>…</section>
  <section data-fx-item>…</section>
  <section data-fx-item>…</section>
</div>
```

| atributo (no contêiner) | padrão | efeito |
|---|---|---|
| `data-fx-faixa` | `10` | px de cada card que continuam aparecendo acima do seguinte |
| `data-fx-topo` | `0` | px do alto da tela em que o primeiro card para |

**Não use `position: sticky` para isto.** Abaixo de 402px o `js/shell.js` reduz
o `.page` com `transform`, e sticky dentro de um elemento transformado gruda no
referencial dele, não na janela — os cards travam fora da tela. O componente
mede ao vivo e converte pela escala, como o `pin-horizontal`.

Checklist:
- **Fundo, texto e enfeites de cada card precisam estar no mesmo elemento.** Se
  o fundo colorido for uma decoração absoluta da `.art-bg` e só o texto estiver
  no fluxo, cada um anda por conta. Refatore antes (o fundo vira `::before` da
  seção, com as coordenadas do Figma passadas para dentro dela) e confirme com
  print antes/depois. Foi o caso da CONSUMIDOR.
- Se o fundo for mais alto que a seção (o rabo que preenche atrás dos cantos
  arredondados do card seguinte), **recorte no contêiner** — `overflow-y: clip`
  no `.cards` —, senão o rabo desce junto com o card e invade o bloco de baixo.
- A altura do documento **não muda** (os cards só recebem `translateY`), então
  serve nas páginas de decoração global, em que as decorações são absolutas e
  não acompanhariam um fluxo que crescesse.
- No probe da página, bloqueie o `js/scroll-fx.js`.

Em uso: `74/consumidor.html`, os 3 cards coloridos (`.cards`, faixa 10, topo 20).

### `pin-sequencia` — scroll

**A tela congela** e, dentro dela, passa uma sequência: a foto ocupa a tela
inteira e os balões de texto **atravessam de baixo para cima**, um de cada vez.
No instante em que um balão sai pelo topo, o seguinte entra por baixo e a foto
**troca em fade cruzado** — cada texto anda com a sua imagem. Quando o último
balão sai, a página volta a rolar.

```html
<section class="bl" data-fx="pin-sequencia">
  <figure data-fx-foto>…</figure>
  <blockquote data-fx-balao>…</blockquote>
  <figure data-fx-foto>…</figure>
  <blockquote data-fx-balao>…</blockquote>
  <p>texto que fica fora da sequência</p>
</section>
```

| atributo (no contêiner) | padrão | efeito |
|---|---|---|
| `data-fx-troca` | `0.3` | fração do percurso de cada balão gasta no fade cruzado (maior = troca mais lenta, acompanhando a subida e a saída do balão) |

**O JS monta o palco**: tira as fotos e os balões do fluxo, põe um palco de
100vh no lugar e escala cada foto para cobri-lo sem deformar. Sem JS a página
fica exatamente como o CSS manda — fotos e balões um abaixo do outro.

Checklist:
- **Enfeites presos à foto** (um rabisco, um selo) precisam estar **dentro da
  `<figure>`** dela, com as coordenadas relativas à foto: no palco a foto é
  escalada, e só assim eles acompanham. Na NOVO NEGÓCIO isso exigiu dar
  especificidade às regras deles (`.foto-41 .callout-pudim`), senão a regra
  genérica `.foto-41 img` esticava o enfeite ao tamanho da foto.
- **Nenhum balão pode aparecer antes de a tela travar**: eles ficam invisíveis
  até a vez de cada um, e recebem `top: 0` para que "y = altura da tela" os
  ponha na borda de baixo do palco — senão o primeiro assoma na base enquanto o
  palco ainda desce.
- O efeito **aumenta a altura do documento** (o espaçador do congelamento) e
  troca a altura do bloco pela do palco. Como a coluna inteira congela junto,
  serve também nas páginas de decoração global.
- No probe da página, bloqueie o `js/scroll-fx.js`.

Em uso: `74/negocio.html`, a história do primeiro pudim (`.bl-historia`).

### `orbit-in` — scroll contínuo

O elemento **percorre um arco** — a curvatura de uma elipse do próprio layout —
enquanto **cresce e gira**, tudo amarrado ao scroll (1:1, vai e volta). Começa
pequeno, "em pé" e num ponto da curva; termina exatamente na posição, tamanho e
inclinação do CSS.

```html
<span class="d-img28" data-fx="orbit-in" data-fx-curva=".d-sub1"
      data-fx-de-angulo="30" data-fx-escala="0.05" data-fx-rotacao="52.64"
      data-fx-inicio="100%" data-fx-fim="50%">…</span>
```

| atributo | padrão | efeito |
|---|---|---|
| `data-fx-curva` | — | seletor do elemento cuja **caixa define a elipse** do trajeto (centro da caixa, raios = metade). Use o arco/círculo do layout que o movimento deve acompanhar |
| `data-fx-de-angulo` | `30` | ângulo de partida na elipse (0 = direita, 90 = topo, 180 = esquerda) |
| `data-fx-escala` | `0.05` | tamanho no começo (1 = tamanho final) |
| `data-fx-rotacao` | `0` | graus a mais no começo; para deixar "em pé" um elemento inclinado no CSS, use o valor oposto ao dele (CSS −52.64 → `52.64`) |
| `data-fx-inicio` | `100%` | ponto da tela (do centro final do elemento) em que o movimento começa |
| `data-fx-fim` | `50%` | ponto da tela em que termina |

**O fim não é chutado:** o componente mede onde o centro do elemento cai em
relação à elipse (ângulo e distância) e termina ali — se o layout mudar, o
trajeto acompanha. Medições ao vivo a cada frame, como no `pin-horizontal`.

Como achar os valores: meça a caixa do elemento e a da curva (`offsetLeft/Top`,
largura/altura). O ângulo de partida é o ponto da elipse onde o arco encontra a
borda da tela — `cos θ = (x − centroX) / raioX`. Na GESTÃO 02: celular com centro
em (250, 2956), arco branco com centro (183, 3109) e raios 245×116 → partida a
30° = (395, 3050), na borda direita.

Checklist:
- Anime o invólucro, não a imagem: a rotação do CSS (se houver) fica no elemento
  de dentro e as duas se somam.
- O elemento pode estar na camada de decoração (`.art-bg`): o efeito só usa
  `transform`, então não mexe no layout — vale em página de decoração global.

Em uso: `74/gestao2.html`, celular do bloco "quando essa estratégia funciona"
(`.d-img28`, sobre o arco `.d-sub1`).

### `slide-in-up` — scroll disparado

Cada item fica **escondido** até o topo dele passar da sua linha (a `margem` px
do fundo da tela); aí **aparece sem fade** (100% de opacidade) **na borda de
baixo da tela** e **percorre todo o caminho, visível, até o lugar**. Cada item
seguinte espera um pouco mais (cascata). Rolando de volta para cima, **desce até
a borda de baixo e se esconde** ao cruzar a mesma linha. Não acompanha o scroll
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
| `data-fx-passo` | — | em vez da linha de cada item: **px de scroll entre uma entrada e a seguinte**, contados pelo 1º item (1º entra na margem, 2º `passo` px de scroll depois, …). Use em pilhas em que os itens ficam colados/sobrepostos — a linha de cada item faria vários entrarem quase juntos |
| `data-fx-deslocamento` | `base` | de onde sobe: `base` = da borda de baixo da tela (caminho inteiro visível); ou px fixos (ex.: `40`) |
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
- Enquanto sobem, os itens passam por cima do que vem logo abaixo: o componente
  põe `position: relative` e `z-index` inline neles, **crescendo com a ordem**
  (2, 3, 4…) — sem isso, um banner/imagem seguinte, pintado depois no HTML, os
  esconderia no meio do caminho, e numa pilha sobreposta o item que sobe da base
  passaria por trás do anterior. Confira que nada abaixo tem `z-index` maior.
- **Ordem estrita:** um item só entra se o anterior já entrou, e sai junto/depois
  do seguinte. Nunca aparece o 3º antes do 2º.
- Os itens nascem escondidos **assim que o script roda**, antes de esperar as
  fontes — senão, quem abre a página com o bloco na tela vê a pilha inteira por
  um instante.
- Sem JS ou com "reduzir movimento", os itens ficam visíveis no lugar.

Em uso: `74/principal.html`, lista dos 5 acordos (`.pacts`), margem 200;
`74/gestao.html`, os 3 cards coloridos de "a conta" (`.s-contas`), pilha
sobreposta, `data-fx-margem="200" data-fx-passo="200"` (testados 300/150 por
linha, 400/400 e 200/100 por passo — 200/200 foi o aprovado para dar tempo de
ver a pilha se montando).

### `typewriter` — entrada

Os textos são **digitados letra a letra**, um de cada vez: o primeiro aparece,
fica um instante na tela, é **apagado de trás para frente**, e o seguinte é
digitado no lugar. O último fica. Com um item só, é só a digitação.

```html
<section data-fx="typewriter">
  <h1 data-fx-item>Não engane<br><span class="am">SEU CLIENTE</span><br>com IA</h1>
  <p  data-fx-item>mas aprenda<br>com ela</p>
</section>
```

| atributo (no contêiner) | padrão | efeito |
|---|---|---|
| `data-fx-velocidade` | `0.06` | segundos por letra ao escrever |
| `data-fx-apagar` | `0.03` | segundos por letra ao apagar |
| `data-fx-pausa` | `1.2` | segundos que o texto fica inteiro na tela |
| `data-fx-atraso` | `0.3` | segundos antes de começar |
| `data-fx-repetir` | — | recomeça sem parar; o valor são os segundos entre uma volta e a seguinte. No loop o último texto também é apagado, para o ciclo fechar |

O markup de cada item é preservado (`<br>`, `<span>` de cor): o efeito esvazia e
repõe só os **nós de texto**, na ordem. Como as quebras continuam no lugar, a
caixa não muda de altura enquanto digita.

Checklist:
- **O item digitado precisa de altura fixa** (`height`, as linhas que ele tem
  cheio). Enquanto o texto está vazio ou pela metade a caixa encolhe — na MKT,
  de 165px para 110px, porque as 3 linhas viram 2 —, e tudo abaixo sobe junto.
  Foi o que descolava o selo `#74` e o resto do texto das decorações.
- Os textos que se revezam ocupam **o mesmo lugar na tela**. Em página de
  decoração global, o segundo (e os seguintes) precisam ficar **fora do fluxo**
  (`position: absolute`, com as coordenadas do primeiro): se ocupassem espaço, o
  texto abaixo andaria e as decorações, que são absolutas, ficariam para trás.
  Na MKT isso deslocava 28px tudo a partir do hero.
- No CSS, deixe visível só o primeiro: **sem JS é ele que fica**, e é o estado
  legível. Os demais começam com `visibility: hidden`.
- Precisa do trecho anti-piscada no `<head>`, com o seletor dos itens — senão os
  textos aparecem todos, sobrepostos, antes de o efeito começar.

Em uso: `74/mkt.html`, o hero (`.s-hero`): "Não engane seu cliente com IA" dá
lugar a "mas aprenda com ela", em loop (`data-fx-repetir="0.5"`).

### `reveal-wipe` — entrada

O elemento é **descoberto de um lado ao outro**, como uma cortina que abre: nada
se move nem muda de opacidade — o que muda é o recorte (`clip-path`). Roda ao
carregar (se já estiver à vista) e **refaz toda vez que volta à tela**.

```html
<p data-fx="reveal-wipe">…</p>
```

| atributo (no elemento) | padrão | efeito |
|---|---|---|
| `data-fx-duracao` | `1.2` | segundos |
| `data-fx-de` | `esquerda` | de onde a cortina abre: `esquerda`, `direita`, `cima` ou `baixo` |
| `data-fx-margem` | `100` | px acima do fundo da tela que disparam |

Checklist:
- **Marque o texto, não a caixa.** No `<blockquote>`/`<section>` o recorte come
  o bloco inteiro (fundo, padding, o que mais houver dentro); no `<p>` ele
  descobre só o texto. Foi o ajuste que a citação da DELIVERY pediu.
- Num parágrafo de várias linhas a cortina abre em **todas ao mesmo tempo**
  (uma faixa vertical atravessando o bloco). Revelar linha a linha seria outro
  efeito.
- Não mexe no fluxo (só recorta), então serve em página de decoração global.
- Se o elemento estiver acima da dobra, precisa do trecho anti-piscada no
  `<head>`, com `[data-fx="reveal-wipe"]`.

Em uso: `74/delivery.html`, a citação da `.s-oriento` (o `<p>` de dentro).

### `popcorn-pop` — entrada

As letras **pipocam**: cada uma surge do nada (escala 0), subindo alguns px e
girando um pouco, em **ordem aleatória** e com um quique no fim
(`back.out(2)`). Roda ao carregar e **refaz toda vez que o texto volta à tela** —
ao sair, rearma.

```html
<h1 data-fx="popcorn-pop">Descontos<br><span class="am">fantasmas</span></h1>
```

| atributo (no elemento) | padrão | efeito |
|---|---|---|
| `data-fx-intervalo` | `0.04` | segundos entre uma letra e a seguinte |
| `data-fx-duracao` | `0.4` | segundos de cada letra |
| `data-fx-deslocamento` | `30` | px de onde a letra sobe |
| `data-fx-rotacao` | `20` | graus máximos (sorteados) de onde ela vem |
| `data-fx-atraso` | `0` | segundos antes da primeira (só ao carregar) |
| `data-fx-margem` | `100` | px acima do fundo da tela que disparam |

- Carregue o **`SplitText.min.js`** (gratuito desde a 3.13) antes do
  `scroll-fx.js`. Sem ele o texto fica parado — nada quebra.
- **Espera as fontes**: as letras são medidas na quebra. Até lá fica escondido
  (precisa do trecho anti-piscada no `<head>`, com `[data-fx="popcorn-pop"]`).
- Quebra por letra **com `smartWrap`**, senão a linha pode quebrar no meio da
  palavra. Entre uma vez e outra o HTML **volta ao original** (`split.revert()`).
- A caixa do texto não muda de altura, então serve em página de decoração
  global.
- Serve para título curto. Em texto longo são centenas de letras animando.

Em uso: `74/delivery.html`, título da abertura (`.hero-title`).

### `magnetic-pull` — entrada

Ao carregar, o texto é quebrado em **letras** (SplitText) e cada uma vem de uma
posição e rotação aleatórias, surgindo, até o lugar — como se um ímã as
juntasse. No fim, o texto **volta a ser o HTML original** (`split.revert()`):
nada muda de layout nem de acessibilidade depois da animação.

```html
<h1 data-fx="magnetic-pull">Clube de descontos, <span>VALE A PENA?</span></h1>
```

| atributo (no elemento) | padrão | efeito |
|---|---|---|
| `data-fx-distancia` | `200` | px máximos de onde cada letra vem (x e y) |
| `data-fx-rotacao` | `90` | graus máximos de rotação inicial |
| `data-fx-intervalo` | `0.02` | segundos entre uma letra e a seguinte |
| `data-fx-duracao` | `1` | segundos de cada letra |
| `data-fx-atraso` | `0` | segundos antes da primeira |

Checklist:
- Carregue o **`SplitText.min.js`** (gratuito desde a 3.13) antes do
  `scroll-fx.js`. Sem ele, o texto fica parado — nada quebra.
- **Espera as fontes**: as letras são medidas na quebra, e com a fonte
  substituta sairiam do tamanho errado. Até lá o texto fica escondido (precisa
  do trecho anti-piscada no `<head>`, com `[data-fx="magnetic-pull"]`).
- Quebra por letra **com `smartWrap`**, senão a linha pode quebrar no meio da
  palavra.
- Serve para título curto. Em texto longo são centenas de letras animando.

Em uso: `74/gestao2.html`, título da abertura (`.s-hero h1`).

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

### `scale-up` — entrada

Os itens **crescem a partir da base** (de 0 ao tamanho final, ancorados no
centro de baixo), **um depois do outro** na ordem do HTML, logo na abertura da
página. Pensado para formas de fundo — na PRINCIPAL, as cúpulas atrás da foto
do hero (vermelha, branca, laranja e a textura), que continuam atrás da foto
porque o `.backdrop` vem antes dela no HTML. Não espera a foto: as cúpulas sobem
e a foto (`slide-in-left`) desliza por cima quando carrega.

```html
<div class="backdrop" data-fx="scale-up"
     data-fx-fundo="#ffe3cc" data-fx-fundo-abaixo=".hero-wash">
  <span class="hero-wash"></span>                 ← não anima (sem data-fx-item)
  <span class="hero-e140" data-fx-item><img …></span>
  <span class="hero-e141" data-fx-item><img …></span>
</div>
```

| atributo (no contêiner) | padrão | efeito |
|---|---|---|
| `data-fx-duracao` | `0.9` | segundos de cada item |
| `data-fx-intervalo` | `0.15` | segundos entre um item e o seguinte |
| `data-fx-atraso` | `0` | segundos antes do primeiro |
| `data-fx-origem` | `50% 100%` | ponto de onde cresce (`transform-origin`) |
| `data-fx-fundo` | — | cor de fundo do contêiner **só durante a entrada** (não fica branco atrás dos itens); sai quando o último termina |
| `data-fx-fundo-abaixo` | — | seletor: o fundo só começa onde esse elemento termina |

**Fundo durante a entrada (lição aprendida):** se houver uma camada
**translúcida** por cima (o `hero-wash` é laranja a 20%), um fundo no contêiner
inteiro soma com ela e o topo escurece — os dois blocos ficam de cores
diferentes, com qualquer cor. Use `data-fx-fundo-abaixo` apontando para essa
camada e, como cor, **a que ela dá sobre branco** (laranja 20% sobre branco =
`#ffe3cc`): assim embaixo fica igual a em cima, e nada muda de cor quando o
fundo sai no fim. O fundo sai no fim porque imagens com transparência (a foto
do hero é PNG) mostrariam a cor onde o design mostra branco.

Checklist:
- Anime o invólucro (`<span>`), não a imagem: a imagem pode ter `transform` no
  CSS (as cúpulas têm `rotate(180deg)`), e o efeito sobrescreveria.
- Precisa do trecho anti-piscada no `<head>`, com o seletor dos itens.

Em uso: `74/principal.html`, cúpulas do hero (`.bl-hero .backdrop`).

### `pop-in` — entrada

Os itens **surgem um de cada vez**, na ordem do HTML, crescendo do centro com um
pequeno quique no fim (`back.out`) — ou, com `data-fx-entrada`, surgindo e
subindo alguns px com fade (`fade-up`) ou **vindo da esquerda** com fade
(`fade-right`). Espera as imagens dos itens carregarem
(limite de 3s) para não surgirem vazios. **Quando:** itens sem grupo surgem ao
abrir a página; `data-fx-quando="scroll"` no contêiner faz a lista inteira
esperar **chegar à tela**; e itens com `data-fx-grupo` formam sequências
próprias, cada uma disparando na chegada do seu grupo — use um dos dois para
peças abaixo da dobra, senão a entrada acontece sem ninguém ver. O que espera a
tela **recomeça a cada entrada**: o grupo que sai inteiro da tela volta ao
estado inicial e anima de novo quando o leitor volta — e no Ctrl+R, que devolve
o leitor onde ele estava. Só a sequência de abertura (`carregar`) roda uma vez
por carregamento. Depois de surgir,
cada item pode **continuar se mexendo**: balançar (girar em volta do centro, ida
e volta) e/ou flutuar (subir e descer), sem parar. O contêiner pode ser a camada
de decoração inteira (`.art-bg`): só os `data-fx-item` animam, e um mesmo
contêiner pode ter a abertura e vários grupos.

```html
<div class="art-bg" data-fx="pop-in">
  <!-- abertura: surgem ao carregar -->
  <span class="d-hero-saco"  data-fx-item data-fx-balanco="7">…</span>
  <span class="d-hero-gota1" data-fx-item data-fx-flutuacao="10">…</span>
  <!-- grupo: surge quando chega à tela; intervalo e margem no 1º item do grupo -->
  <span class="d-sache1" data-fx-item data-fx-grupo="saches" data-fx-intervalo="0.5">…</span>
  <span class="d-sache2" data-fx-item data-fx-grupo="saches">…</span>
</div>
```

Lista inteira que entra quando chega à tela, um item a cada 0,5s, vindo da
esquerda com fade (os atributos do contêiner valem para todos os itens):

```html
<ul class="tools" data-fx="pop-in" data-fx-quando="scroll"
    data-fx-entrada="fade-right" data-fx-intervalo="0.5">
  <li data-fx-item>…</li>
  <li data-fx-item>…</li>
</ul>
```

Os atributos marcados **item** podem ir no contêiner, valendo para todos os
itens; o do item vence o do contêiner.

| atributo | onde | padrão | efeito |
|---|---|---|---|
| `data-fx-quando` | contêiner | `carregar` | `carregar` (na abertura) ou `scroll` (a lista inteira espera chegar à tela) |
| `data-fx-duracao` | contêiner | `0.5` | segundos do "pop" de cada item |
| `data-fx-intervalo` | contêiner ou item | `0.2` | segundos entre um item e o seguinte |
| `data-fx-entrada` | contêiner ou item | `pop` | como o item entra: `pop` (cresce do centro com quique), `fade` (só aparece, sem sair do lugar), `fade-left` (vem da direita), `fade-up` (surge subindo, com fade; mínimo 0,6s) ou `fade-right` (surge vindo da esquerda, com fade; mínimo 0,6s) |
| `data-fx-deslocamento` | contêiner ou item | `30` | (`fade-up`/`fade-right`) px que o item percorre ao entrar |
| `data-fx-origem` | item | `50% 50%` | ponto de onde o item cresce (`transform-origin`); use quando o desenho é maior que a caixa do item (ex.: o centro do balão) |
| `data-fx-grupo` | item | — | nome do grupo: sequência própria, que recomeça a cada vez que o grupo entra na tela |
| `data-fx-margem` | contêiner ou item | `100` | px acima do fundo da tela em que a sequência dispara (maior = mais tarde, com o bloco mais dentro da tela) |
| `data-fx-linha` | contêiner ou item | — | em vez da margem: a linha de disparo nessa fração da altura da tela, contada **do topo** (`"80%"` = quando o item chega aos 80% da tela). Não depende do tamanho do aparelho |
| `data-fx-atraso` | contêiner | `0` | segundos antes do primeiro (só ao carregar) |
| `data-fx-balanco` | item | — | depois de surgir, gira ±N graus em volta do centro, sem parar |
| `data-fx-balanco-duracao` | item | `1.6` | segundos de cada ida (ou volta) do balanço |
| `data-fx-flutuacao` | item | — | depois de surgir, sobe N px e volta, sem parar; cada item com ritmo (1,4–2s) e fase próprios, para não flutuarem juntos |

Valores aprovados na GESTÃO: balanço **7°** na bisnaga, flutuação **10px** nas
gotas (30° e 20px ficaram exagerados — prefira movimentos contínuos pequenos);
intervalo de **0,5s** entre os sachês (2s e 1s ficaram lentos demais), também
usado nos 3 sachês pequenos com `fade-up`.

**Itens independentes:** sem grupo (ou com `data-fx-quando="scroll"`), os itens
entram *em sequência*, disparados pelo primeiro. Para cada um entrar **na sua
própria linha**, dê a cada um o **seu** `data-fx-grupo` — aí cada grupo mede a
posição dele. E como o `data-fx-margem` também vale por item, dá para segurar um
deles: na DELIVERY a citação é alta e cruzava a linha cedo demais, então ela ficou
com margem 320 enquanto o parágrafo seguinte usa os 150 do contêiner.

**`fade-up`/`fade-right` aqui × `slide-in-up`:** use os fades do `pop-in` quando
os itens entram **juntos, em sequência de tempo** (um a cada X s, assim que o
bloco chega à tela — ex.: 3 peças lado a lado, ou uma lista curta). Use o
`slide-in-up` quando cada item deve entrar **pela própria posição** conforme o
leitor rola (itens empilhados, cada um com a sua linha), e sem fade.

Checklist:
- As peças precisam ser **elementos separados** (uma imagem por peça). Se o
  Figma entregar uma arte composta, extraia peça por peça primeiro (README,
  armadilha 3) — foi o que permitiu animar a bisnaga e as gotas da GESTÃO.
- Anime o invólucro (`<span>`): o efeito usa `scale`, `rotation` e `y`, e
  sobrescreveria um `transform` do CSS na imagem.
- **Texto + desenho que formam uma peça** (balão com frase, selo com número…)
  precisam estar **no mesmo elemento** — se o desenho estiver na camada de
  decoração e o texto no fluxo, cada um cresce de um centro e o texto escorrega
  para fora do desenho. Refatore assim, sem mexer no layout:
  1. um invólucro (`.balao`, `position: relative`) com **as margens e a largura
     que o texto tinha** — ocupa no fluxo o mesmo lugar, nada abaixo se move;
  2. o desenho dentro dele, `position: absolute`, com o **deslocamento medido**
     em relação à caixa do texto (topo/esquerda do desenho − do texto);
  3. o texto depois do desenho, `position: relative` (fica por cima), sem margens;
  4. remova o desenho da camada de decoração;
  5. confira com print antes/depois (0 pixel diferente) e o probe da página;
  6. `data-fx-origem` no invólucro = centro do desenho em relação à caixa.
  Feito no balão "É só um sachê de R$ 0,15." da GESTÃO (`.balao`, antes
  `.d-union` na `.art-bg` + `.q-sache` solto).
- **O item precisa ser uma caixa no fluxo**, não uma camada sobre a lista. Se
  as peças vieram do Figma em coordenadas absolutas relativas à lista inteira,
  refatore antes de animar: cada item vira uma linha (`display: flex`), com as
  peças posicionadas **dentro dele**, e as medidas que variam de um item para
  outro em variáveis CSS. Senão o `x`/`y` do efeito move uma camada que cobre a
  lista toda, e o que é "um item" para o efeito não é o que se vê na tela. Foi o
  caso da `ul.tools` da MKT (print antes/depois: 0 pixel diferente).
- **Anti-piscada** no `<head>` (com o seletor dos itens) só é preciso quando os
  itens estão **acima da dobra** — é a entrada ao carregar que pisca. Lista que
  espera o scroll (`data-fx-quando="scroll"`) ou grupo abaixo da dobra dispensa:
  o componente já pôs o estado inicial muito antes de o leitor chegar lá.
- Probes: bloqueie o `js/scroll-fx.js` no probe da página — senão ele mede os
  itens ainda em escala 0 (esperando chegar à tela) e acusa 0×0.

Em uso: `74/gestao.html` — bisnaga e 5 gotas na abertura; sachês 1 e 2 do bloco
"O problema nunca é um sachê!" em grupo (`data-fx-grupo="saches"`), todos na
mesma `.art-bg`; os 3 sachês pequenos lado a lado em grupo com `fade-up`
(`data-fx-grupo="saches-mini"`, 0,5s); balão com a frase em outro contêiner
(`.s-sache`), grupo `balao`, crescendo do centro do desenho
(`data-fx-origem="105.5px 43px"`).
`74/mkt.html` — as 3 ferramentas de IA (`ul.tools`) com `data-fx-quando="scroll"`
e `fade-right`, 0,5s entre elas.
`74/negocio.html` — os 7 itens da `ul.checklist` em `pop` (1s entre eles), os 5
da `ol.passos` em `fade-left` e as 4 pills da `.foto-faturamento` em `pop`
(0,5s), todos disparando aos 80% da tela (`data-fx-linha`).
`74/delivery.html` — o ícone do fantasma (`pop`, na camada de decoração) e, na
`.s-pausar`, a citação e o parágrafo seguinte em `fade` de 1s, cada um no seu
grupo para entrar na própria linha.

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
posição do CSS (o `probe` da página confere). No `scale-up` com fundo, confira
no meio da entrada que os blocos de cima e de baixo têm a mesma cor (amostre
um pixel de cada).

**`pin-horizontal`:** role por posições da faixa congelada (início, 25%, 50%,
fim, depois) e meça: topo do `.page`, fundo do bloco de cima e topo do de baixo
**parados** (±1px) enquanto o `scrollLeft` do trilho vai de 0 ao máximo; com
vários na página, cada trilho rola sozinho (os outros parados) e o centro dele
fica fixo no ponto da trava;
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
