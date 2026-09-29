---
name: figma-pixel-perfect-html
description: >-
  Implementa um design do Figma em HTML + CSS + JavaScript puro com fidelidade
  pixel perfect, usando arquitetura flow-first (conteúdo no fluxo, decoração
  presa ao bloco dela) e um loop de screenshot → comparação programática →
  correção, fechado por uma auditoria de estrutura obrigatória. Use quando o
  usuário pedir para implementar, converter, "codar" ou montar uma página a
  partir de um design do Figma (ou de uma URL figma.com) em HTML/CSS/JS, ou
  para montar uma nova edição/matéria da revista a partir do Figma.
---
# Implementar design do Figma em HTML/CSS/JS (pixel perfect)

## Por que esta skill existe

O Figma entrega **coordenadas absolutas** de cada nó em relação ao frame. O
caminho mais curto — copiar cada `top`/`left` para um `position: absolute` — dá
um print idêntico e uma página **impossível de manter**. Isso já aconteceu, e
o custo apareceu depois:

- inserir um banner exigiu somar o mesmo deslocamento a dezenas de `top` de
  decorações (e um `top: calc(2429px - 141px)` escapou e quebrou a página);
- fotos "sentadas" sobre uma aba ficaram soltas no meio do bloco quando a lista
  de cima passou a abrir e fechar;
- a sombra de uma peça e o "%" sobre uma foto eram elementos separados, em
  outro lugar do HTML, e apareceram sozinhos quando a peça foi animada;
- um parágrafo que visualmente abria o bloco B estava no HTML do fim do bloco A;
- ícones posicionados com `:nth-child` impediram reordenar o HTML;
- uma arte composta (várias peças numa imagem só) e uma PNG de 1920px com
  quase tudo transparente impediram animar/recortar as peças.

Cada regra abaixo evita um desses casos. **Fidelidade visual não basta: a
página precisa passar na auditoria de estrutura (seção 6).**

## 1. Stack

HTML + CSS + JavaScript **puro** (sem framework), a menos que o usuário peça
outra coisa. Reset mínimo sempre:
`*{box-sizing:border-box} img{display:block;max-width:100%} figure{margin:0}`.

## 2. Fluxo de trabalho (loop até ficar fiel)

Não pare no passo 5, e não pare antes do passo 8.

1. **Analisar o Figma.** Design context, metadata e um **screenshot em
   resolução nativa** (peça `maxDimension` alto — o padrão vem pequeno, ex.
   ~130px de largura). Anote larguras, alturas, cores, fontes e line-heights.
2. **Mapear os blocos antes de escrever qualquer código** (seção 3). Escreva o
   mapa: blocos, o que é conteúdo, o que é decoração, o que é peça presa a outra.
3. **Baixar assets**, verificar o formato real e **recortar a área útil**
   (seção 5). Salve em `assets/`.
4. **Escrever HTML/CSS** seguindo as regras (seção 4).
5. **Renderizar** no mesmo tamanho do original (`scripts/shot.py`).
6. **Comparar de forma programática** (`scripts/compare.py`), não no olho.
7. **Corrigir e repetir 5–6** até ficar fiel.
8. **Rodar a auditoria de estrutura** (seção 6). Se reprovar, corrija a
   estrutura **e volte ao passo 5** — a auditoria não autoriza piorar o visual,
   e o visual não autoriza pular a auditoria.

## 3. Mapear antes de codar

As coordenadas do Figma servem para **medir distâncias**, não para virar `top`
na página. Para cada região visual do design, responda por escrito:

**a) Qual é o bloco?** Um bloco é uma faixa horizontal da página com começo e
fim visuais (mudança de fundo, título de seção, foto de largura cheia). Cada
bloco vira uma `<section>` com `position: relative`. **A ordem das seções no
HTML é a ordem de leitura, de cima para baixo.**

**b) Cada nó do Figma é o quê?** Classifique um por um:

| tipo | exemplos | vai para |
|---|---|---|
| **conteúdo** | títulos, parágrafos, listas, citações, foto que ilustra o texto, botões, banners | **fluxo normal**, dentro da seção onde aparece |
| **decoração do bloco** | formas de fundo, arcos, manchas, texturas, faixas coloridas atrás do texto | camada `.backdrop` **da própria seção**, em `position: absolute` |
| **peça presa a outra** | sombra de um objeto, "%" ou selo sobre uma foto, texto dentro de um balão, número sobre um mapa, legenda sobre imagem | **dentro do mesmo invólucro** do objeto, posicionada em relação a ele |

**c) Onde cada nó mora no HTML?** Na seção cuja área visual ele ocupa. Um
elemento que aparece no topo do bloco B **não pode** estar no HTML do bloco A,
mesmo que no Figma ele esteja agrupado lá. Da mesma forma, uma `<img>` mora
dentro do `div`/`figure` do contexto dela — nunca solta noutra parte do HTML e
arrastada até lá com `absolute`.

**d) Em que ordem?** Dentro de um bloco, a ordem do HTML segue a leitura:
de cima para baixo e, na mesma linha, da esquerda para a direita. Efeitos em
sequência (entradas "um de cada vez") seguem a ordem do HTML — se ela não for
a visual, a animação sai fora de ordem.

**Teste do DevTools:** passe o mouse sobre cada item no Elements. O realce
tem que cair exatamente sobre o que se vê na tela, e o item tem que estar no
HTML entre os vizinhos visuais dele. Caixa que cobre a página inteira, item
realçado num lugar e desenhado noutro, ou `<img>` fora do seu contexto:
estrutura errada.

## 4. Regras de HTML e CSS

### Proibido (reprova na auditoria)

1. **`position: absolute` em conteúdo.** Título, parágrafo, lista, citação,
   foto de conteúdo, botão e banner ficam no fluxo. Posicione com `margin`,
   `padding`, `gap`, Flexbox e Grid.
2. **Absoluto posicionado em relação à página.** Todo elemento absoluto tem
   como referência a **sua seção** (ou um invólucro menor dentro dela) — nunca
   `.page`, `article` ou `body`. Consequência prática: **nenhum `top` passa da
   altura da seção** que o contém. `top: 4986px` é sempre erro.
3. **Uma camada de decoração única para a página inteira** (`.art-bg` com
   todas as decorações em coordenadas da página). Cada seção tem o seu
   `.backdrop`.
4. **Peça presa separada do seu objeto.** Sombra, selo, "%", número, texto de
   balão: no mesmo invólucro do objeto, com `top`/`left` relativos a ele.
5. **`top`/`left` com `calc()` de coordenadas de página** (`calc(2429px -
   141px)`). Se precisou disso, o elemento está no contêiner errado.
6. **`margin-top` acima de ~200px** entre blocos de conteúdo. Quase sempre
   significa que uma imagem ou um bloco deveria estar no fluxo naquele ponto.
7. **Altura fixa ou mínima em blocos de texto** (`p`, `ul`, `ol`,
   `blockquote`, o `div` que agrupa textos). A altura vem do texto. `min-height`
   é aceitável **só na `<section>`**, e só para preservar um fundo/decoração.
8. **Posição por `:nth-child`** para itens que podem mudar de ordem. Use uma
   classe por item (`.icon--1`) ou `:nth-of-type`, ou melhor: Flexbox/Grid.
9. **`transform` no invólucro de uma peça** (rotação, espelho). Coloque o
   `transform` num elemento interno; o invólucro fica livre para animação.
10. **Arte composta**: várias peças independentes numa imagem só. Cada peça é
    uma imagem (ver seção 5).
11. **Tags vazias sem função.** Um `<span>` vazio só existe se for decoração
    (forma de fundo) — e aí fica no `.backdrop` da seção, com `aria-hidden`.

### Obrigatório

- `<section class="bl bl-nome">` por bloco, com `position: relative`.
- Hierarquia correta de `h1`/`h2`/`h3`; `<p>`, `<ul>/<li>`, `<figure>`.
- Elementos visualmente conectados (título + texto, aba + lista + fotos da aba)
  num mesmo contêiner lógico.
- Decoração: `<div class="backdrop" aria-hidden="true">` como **primeiro filho**
  da seção; conteúdo depois, com `position: relative` se precisar ficar por cima.
- Cada peça que pode ser animada é um elemento próprio: `<span class="peca">`
  envolvendo a `<img>`.
- A página pode ficar alguns px mais longa que o Figma por causa do texto
  fluido. Isso é aceito; posicionar texto com absoluto para "acertar" não é.

### Receita: peça presa a um objeto

```html
<figure class="cesta">                       <!-- position: relative -->
  <img src="assets/cesta.png" alt="…">
  <span class="cesta-sombra" aria-hidden="true"></span>   <!-- absolute, relativo à cesta -->
</figure>
```

Medida: `top/left da peça no Figma − top/left do objeto no Figma`.

### Receita: foto do Figma com `imageTransform` (rotação/corte no preenchimento)

O código exportado costuma trazer o recorte errado. Baixe o preenchimento
original e ajuste contra o screenshot do nó. Nunca "conserte" com absoluto na
página: o ajuste vai no `img` dentro do invólucro da peça.

## 5. Assets

- **Verifique o formato real** (a URL diz `.png` e o arquivo é JPG ou GIF).
- **Recorte a área útil.** PNG com grande margem transparente (ex.: 1920px de
  largura com a figura em 821px) deve ser recortado na hora; posicione o
  recorte, não a margem vazia.
- **Uma imagem por peça.** Se o Figma entregar uma arte composta, extraia peça
  por peça (máscara por silhueta/cor, ou casamento de pontos contra o
  screenshot do nó) e gere PNG 2x de cada uma.
- Imagens de conteúdo com `width`/`height` no HTML (evita salto de layout).

## 6. Auditoria de estrutura (obrigatória antes de entregar)

Rode este teste na página (Playwright, largura do design). Ele imprime os
problemas; **a meta é zero em todas as linhas**. O cabeçalho e o rodapé comuns
(componentes iguais em todas as páginas) ficam fora da conta. Se algum item for uma exceção
legítima (ex.: uma ilustração que realmente sangra por cima de dois blocos),
explique no relatório final **por que**, item por item.

```python
# python auditoria.py pagina.html 402
import sys, pathlib
from playwright.sync_api import sync_playwright
html, largura = sys.argv[1], int(sys.argv[2])
JS = r"""() => {
  const CONTEUDO = 'h1,h2,h3,h4,p,ul,ol,li,blockquote,button,a.btn,figure:not([aria-hidden])';
  const out = {absConteudo:[], absNaPagina:[], topAlto:[], margemGrande:[], alturaTexto:[], nthChild:[]};
  const nome = e => e.tagName.toLowerCase() + (e.className && typeof e.className==='string' ? '.'+e.className.trim().split(/\s+/).join('.') : '');
  // referência "de página": o próprio corpo/coluna, ou qualquer caixa que não
  // esteja dentro de uma seção ou que contenha seções (ex.: uma .art-bg que
  // cobre a página inteira com todas as decorações)
  const dePagina = ref => !ref || ref.matches('body,.page,article,main')
    || !!ref.querySelector('section') || !ref.closest('section');
  // cabeçalho e rodapé comuns (iguais em todas as páginas) ficam fora: o
  // header/footer que não está dentro de uma seção nem de um artigo
  const comum = e => {
    if (e.closest('.dt-sidebar')) return true;
    const hf = e.closest('header, footer');
    return !!hf && !hf.parentElement.closest('section, article, blockquote, figure');
  };
  document.querySelectorAll('body *').forEach(e => {
    if (comum(e)) return;
    const cs = getComputedStyle(e);
    if (cs.position === 'absolute') {
      const ref = e.offsetParent;
      // conteúdo em absolute só passa como peça presa a um objeto (a referência
      // é um invólucro pequeno, não a seção)
      if (e.matches(CONTEUDO) && !e.closest('[aria-hidden="true"]') && (dePagina(ref) || ref.matches('section')))
        out.absConteudo.push(nome(e));
      if (dePagina(ref)) out.absNaPagina.push(nome(e));
      else if (e.offsetTop > ref.offsetHeight + 50) out.topAlto.push(nome(e)+' top '+e.offsetTop+' > altura do contêiner '+ref.offsetHeight);
    }
    if (parseFloat(cs.marginTop) > 200) out.margemGrande.push(nome(e)+' margin-top '+cs.marginTop);
    if (e.matches('p,ul,ol,blockquote') && (e.style.height || cs.minHeight !== '0px' && cs.minHeight !== 'auto'))
      out.alturaTexto.push(nome(e)+' min-height '+cs.minHeight);
  });
  for (const sh of document.styleSheets) { try { for (const r of sh.cssRules)
    if (r.selectorText && /:nth-child\(/.test(r.selectorText) && /(top|left)\s*:/.test(r.cssText))
      out.nthChild.push(r.selectorText); } catch (_) {} }
  return out;
}"""
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": largura, "height": 900})
    pg.goto(pathlib.Path(html).resolve().as_uri(), wait_until="load"); pg.wait_for_timeout(800)
    for k, v in pg.evaluate(JS).items():
        print(f"{k:13} {len(v):3}  " + ("OK" if not v else "; ".join(v[:8]) + (" …" if len(v) > 8 else "")))
    b.close()
```

O que cada linha significa:

| linha | reprova quando | corrija assim |
|---|---|---|
| `absConteudo` | texto, lista, foto de conteúdo ou botão em `absolute` posicionado em relação à seção ou à página | volte para o fluxo (seção 4, regra 1); se for peça presa (botão de som sobre o vídeo, legenda sobre a foto), coloque no invólucro do objeto |
| `absNaPagina` | absoluto cuja referência é a página, ou uma caixa fora de qualquer seção / que contém seções (camada de decoração global) | mova para o `.backdrop` da seção ou para o invólucro do objeto |
| `topAlto` | `top` maior que a altura do contêiner | o elemento está no contêiner errado |
| `margemGrande` | `margin-top` > 200px | falta um elemento no fluxo ali |
| `alturaTexto` | bloco de texto com altura/mínima | remova; a altura vem do texto |
| `nthChild` | posição por `:nth-child` | classe por item, `:nth-of-type` ou Flexbox |

Além do script, confira à mão e registre no relatório:

- [ ] A ordem das seções e dos elementos no HTML é a ordem visual.
- [ ] Teste do DevTools (seção 3) sem nenhum item fora do lugar.
- [ ] Cada peça presa (sombra, selo, "%", número, texto de balão) está no
      invólucro do seu objeto.
- [ ] Nenhuma imagem tem margem transparente grande; nenhuma arte é composta.
- [ ] **Teste de inserção:** acrescente temporariamente um `<div
      style="height:300px">` no começo de uma seção do meio. Tudo abaixo deve
      descer junto, sem nada ficar para trás. Remova depois.

## 7. Scripts utilitários

Requisitos: `pip install playwright pillow numpy` e `playwright install chromium`.

- **`scripts/shot.py`** — screenshot full-page de um HTML local (ou URL) numa
  largura exata:
  ```bash
  python scripts/shot.py index.html reference/render.png 402
  ```
- **`scripts/compare.py`** — fatias lado a lado (original × render) e extensão
  horizontal não-branca por linha (detecta deslocamentos):
  ```bash
  python scripts/compare.py reference/original_native.png reference/render.png reference/cmp 800
  ```
  **Leia as fatias** geradas em `reference/cmp/` e as medições impressas.

## 8. Relatório final (obrigatório)

Ao entregar, informe:

1. O mapa de blocos (seção 3).
2. A saída da auditoria (seção 6), com zero em todas as linhas ou a
   justificativa de cada exceção.
3. O resultado do teste de inserção e do teste do DevTools.
4. As diferenças visuais restantes em relação ao Figma, em px.
