/* =========================================================
   Revista Assaí — efeitos de scroll e de entrada (GSAP + ScrollTrigger)
   Compartilhado entre edições. Uso declarativo, sem JS por página:

     <section data-fx="card-accordeon">          ← scroll: contêiner
       <div data-fx-item>…</div>                 ← itens que abrem
     </section>
     <section data-fx="pin-horizontal">          ← scroll: congela a tela
       <div data-fx-item>…texto largo…</div>     ← trilho que rola para o lado
     </section>
     <ol data-fx="slide-in-up"><li data-fx-item> ← scroll (disparado): itens entram subindo
     <img data-fx="slide-in-left" …>             ← entrada: roda ao carregar
     <div data-fx="scale-up"><span data-fx-item> ← entrada: crescem da base, em cascata
     <div data-fx="pop-in"><span data-fx-item>   ← entrada: surgem com "pop", um de cada vez
     <span data-fx="orbit-in">                   ← scroll: percorre uma curva crescendo e girando
     <h1 data-fx="magnetic-pull">                ← entrada: letras se juntam vindas de todo lado
                                                   (precisa do SplitText.min.js)

   Efeitos de entrada precisam do trecho anti-piscada no <head> (ver a skill).

   Requer, antes deste arquivo:
     gsap.min.js e ScrollTrigger.min.js (3.15.0, jsDelivr)
   Sem JS, ou com "reduzir movimento" no sistema, a página fica como no CSS.
   Catálogo e checklist: .claude/skills/scroll-fx/SKILL.md
   ========================================================= */
(function () {
  "use strict";

  if (!window.gsap || !window.ScrollTrigger) return;
  gsap.registerPlugin(ScrollTrigger);

  // abaixo de 402px o js/shell.js reduz o .page (transform: scale): medidas de
  // layout (px de CSS) viram px de tela multiplicadas por essa escala
  function zoom() {
    if (window.ShellFit && window.ShellFit.escala) return window.ShellFit.escala() || 1;
    var page = document.querySelector(".page");
    if (!page) return 1;
    var m = /scale\(([\d.]+)\)/.exec(page.style.transform || "");
    return m ? parseFloat(m[1]) : (parseFloat(page.style.zoom) || 1);
  }

  // "80%" -> 80
  function pct(valor, padrao) {
    var n = parseFloat(valor);
    return isNaN(n) ? padrao : n;
  }

  /* ---------- efeitos que deslocam o que vem abaixo ----------
     Cada um registra quantos px de CSS está deslocando agora: o card-accordeon,
     o que ainda está fechado; o pin-horizontal, o percurso em que a tela fica
     congelada. Um gatilho mais abaixo soma isso para medir onde ele estará
     quando o leitor chegar lá. */
  var encolhedores = [];

  function offsetAcima(el) {
    var total = 0;
    encolhedores.forEach(function (e) {
      var antes = e.contenedor.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING;
      if (antes && !e.contenedor.contains(el)) total += e.encolhido();
    });
    return total;
  }

  /* =========================================================
     card-accordeon
     Os itens começam fechados (altura e padding verticais em 0) e crescem de
     verdade conforme o scroll, empurrando o que vem abaixo. Cada item começa a
     abrir quando o topo dele chega ao ponto de início da tela, e nunca antes do
     anterior terminar. Rolando para cima, fecham na ordem inversa.

     Opções no contêiner:
       data-fx-inicio="80%"  ponto da tela (a partir do topo) que dispara cada item
       data-fx-ritmo="1.5"   px de scroll para cada px de item aberto
     ========================================================= */
  function cardAccordeon(sec) {
    var itens = gsap.utils.toArray(sec.querySelectorAll("[data-fx-item]"));
    if (!itens.length) return;

    var inicio = pct(sec.getAttribute("data-fx-inicio"), 80);
    var ritmo = pct(sec.getAttribute("data-fx-ritmo"), 1.5);
    var z = zoom();

    // min-height do CSS no contêiner (ex.: 845px na .bl-gen): encolhe junto com
    // os itens, senão os itens fecham e o espaço continua lá
    var minAltura = parseFloat(getComputedStyle(sec).minHeight) || 0;

    // medidas com tudo aberto, como no CSS (px de CSS)
    var topo0 = itens[0].getBoundingClientRect().top;
    var abertos = itens.map(function (el) {
      var cs = getComputedStyle(el);
      return {
        h: el.offsetHeight,
        pt: parseFloat(cs.paddingTop) || 0,
        pb: parseFloat(cs.paddingBottom) || 0,
        dist: (el.getBoundingClientRect().top - topo0) / z // topo a topo, tudo aberto
      };
    });
    var alturaAberta = abertos.reduce(function (s, a) { return s + a.h; }, 0);

    // posição de cada item na timeline, em px de scroll (de CSS)
    var fim = 0;
    abertos.forEach(function (a) {
      a.inicio = Math.max(a.dist, fim);
      a.dur = a.h * ritmo;
      fim = a.inicio + a.dur;
    });

    gsap.set(itens, { overflow: "hidden", minHeight: 0 });

    var registro = {
      contenedor: sec,
      encolhido: function () {
        var agora = itens.reduce(function (s, el) { return s + el.offsetHeight; }, 0);
        return Math.max(0, alturaAberta - agora);
      }
    };
    // o min-height do contêiner desconta exatamente o que está fechado: fechados,
    // os itens puxam o que vem abaixo; abertos, volta ao valor do CSS
    function ajustaContenedor() {
      if (minAltura) sec.style.minHeight = Math.max(0, minAltura - registro.encolhido()) + "px";
    }

    var tl = gsap.timeline({
      defaults: { ease: "none" },
      scrollTrigger: {
        trigger: itens[0],
        // calculado à mão: soma o que ainda está fechado acima deste contêiner
        start: function () {
          var topo = itens[0].getBoundingClientRect().top + window.scrollY;
          return topo + offsetAcima(sec) * zoom() - window.innerHeight * inicio / 100;
        },
        end: function () { return "+=" + fim * zoom(); },
        scrub: true,
        invalidateOnRefresh: true,
        onRefresh: ajustaContenedor
      },
      onUpdate: ajustaContenedor
    });
    itens.forEach(function (el, i) {
      var a = abertos[i];
      tl.fromTo(el,
        { height: 0, paddingTop: 0, paddingBottom: 0 },
        { height: a.h, paddingTop: a.pt, paddingBottom: a.pb, duration: a.dur },
        a.inicio);
    });

    ajustaContenedor(); // estado inicial, já com os itens fechados

    encolhedores.push(registro);
    return function () {
      encolhedores.splice(encolhedores.indexOf(registro), 1);
      sec.style.minHeight = "";
    };
  }

  /* =========================================================
     pin-horizontal  (scroll)
     Quando o centro do trilho chega ao ponto da tela, a TELA INTEIRA congela:
     tudo o que está visível (o fim do bloco de cima, o começo do de baixo) fica
     parado, e o scroll vertical passa a rolar só o trilho para o lado, 1:1.
     Quando o trilho chega ao fim, a página volta a rolar de onde parou.

       <section data-fx="pin-horizontal">          ← bloco do trilho
         <div data-fx-item>…texto largo…</div>     ← trilho com overflow-x
       </section>

     Opção no contêiner:
       data-fx-inicio="50%"  ponto da tela onde o centro do trilho trava

     Convive com controles próprios que mexam no scrollLeft (setas, arrasto, o
     gesto do dedo): o que for mexido por fora é absorvido e somado à posição do
     scroll, então o leitor pode adiantar/voltar o trilho e seguir rolando dali.
     O que não pode é um controle que mova o conteúdo por transform.

     Como congela: a coluna vai para dentro de dois invólucros — o de fora ganha
     um espaçador com altura igual ao percurso do texto; o de dentro é position: sticky com
     top negativo, então a coluna inteira "gruda" no ponto da trava enquanto o
     scroll atravessa essa altura extra. Vários por página: cada um embrulha o
     anterior (stickies aninhados), e cada um mede a sua trava ao vivo. Sticky é do navegador: não treme e
     respeita o zoom do mobile (o pin do ScrollTrigger, com position: fixed,
     aplicava o zoom duas vezes). O ponto da trava é medido do layout real a
     cada frame, então continua certo com um card-accordeon acima abrindo e
     fechando. Anima o scrollLeft do trilho: convive com o toque/arrasto nativos.
     ========================================================= */
  function pinHorizontal(sec) {
    var trilho = sec.querySelector("[data-fx-item]");
    var page = document.querySelector(".page");
    if (!trilho || !page) return;
    var inicio = pct(sec.getAttribute("data-fx-inicio"), 50);

    // embrulha o que estiver mais por fora: a coluna, ou o congelamento anterior
    var alvo = page;
    while (alvo.parentElement && alvo.parentElement !== document.body) alvo = alvo.parentElement;

    var fora = document.createElement("div");   // coluna + espaçador
    var dentro = document.createElement("div"); // gruda (sticky)
    var espaco = document.createElement("div"); // altura extra = percurso do texto
    fora.className = "fx-congela-fora";
    dentro.className = "fx-congela";
    alvo.parentNode.insertBefore(fora, alvo);
    fora.appendChild(dentro);
    fora.appendChild(espaco);
    dentro.appendChild(alvo);
    dentro.style.position = "sticky";
    // espaçador, não padding: o sticky só anda dentro da área de conteúdo do pai

    var dist = 0, percurso = 0, trava = 0;
    // ajuste manual: o que setas, arrasto ou o dedo mexerem no trilho é absorvido
    // e somado à posição do scroll, em vez de ser sobrescrito no frame seguinte
    var manual = 0, ultimo = null;
    function medir() {
      var z = zoom();
      dist = Math.max(0, trilho.scrollWidth - trilho.clientWidth); // px de CSS
      percurso = dist * z;                                         // px de tela, 1:1
      espaco.style.height = percurso + "px";
      atualizar();
    }
    function atualizar() {
      // ponto da trava (scroll em px de tela), do layout de agora: o trilho medido
      // em relação ao próprio invólucro grudante não é afetado por este sticky
      // (e já inclui o que os congelamentos de dentro deslocaram)
      var rp = dentro.getBoundingClientRect(), rt = trilho.getBoundingClientRect();
      var centro = rt.top + rt.height / 2 - rp.top;        // do topo do invólucro
      var alvo = window.innerHeight * inicio / 100;          // onde o centro para
      var topoFora = fora.getBoundingClientRect().top + window.scrollY;
      trava = topoFora + centro - alvo;
      var top = Math.round(alvo - centro) + "px";            // sticky: medido do topo da tela
      if (dentro.style.top !== top) dentro.style.top = top;
      if (!dist) return;
      if (ultimo !== null) manual += trilho.scrollLeft - ultimo;   // mexeram por fora
      var alvo = gsap.utils.clamp(0, 1, (window.scrollY - trava) / percurso) * dist;
      manual = gsap.utils.clamp(-alvo, dist - alvo, manual);
      ultimo = Math.round(alvo + manual);
      trilho.scrollLeft = ultimo;
    }

    var pedido = 0;
    function noScroll() {
      if (!pedido) pedido = requestAnimationFrame(function () { pedido = 0; atualizar(); });
    }
    window.addEventListener("scroll", noScroll, { passive: true });
    window.addEventListener("resize", medir);
    window.addEventListener("load", medir);
    medir();

    // o que vem abaixo do trilho só chega depois do congelamento: conta o que
    // ainda falta congelar (depois dele, o sticky já empurrou a coluna)
    var registro = {
      contenedor: trilho, // conta para tudo o que vem depois do trilho, mesmo no mesmo bloco
      encolhido: function () {
        var andou = (dentro.getBoundingClientRect().top - fora.getBoundingClientRect().top) / zoom();
        return Math.max(0, dist - andou);
      }
    };
    encolhedores.push(registro);
    ScrollTrigger.refresh(); // a página ficou mais alta: gatilhos remedem

    return function () {
      encolhedores.splice(encolhedores.indexOf(registro), 1);
      window.removeEventListener("scroll", noScroll);
      window.removeEventListener("resize", medir);
      window.removeEventListener("load", medir);
      if (pedido) cancelAnimationFrame(pedido);
      fora.parentNode.insertBefore(alvo, fora);
      fora.remove();
      trilho.scrollLeft = 0;
      manual = 0; ultimo = null;
    };
  }

  /* =========================================================
     card-stack  (scroll)
     Os cards se EMPILHAM: cada um para no alto da tela e o seguinte sobe por
     cima até cobri-lo, deixando uma faixa do anterior à mostra (é ela que diz
     que existe card embaixo). O último não trava — leva a página junto.

       <div class="cards" data-fx="card-stack" data-fx-faixa="10">
         <section data-fx-item>…</section>
         <section data-fx-item>…</section>
       </div>

     Opções no contêiner:
       data-fx-faixa="10"   px do card anterior que continuam aparecendo
       data-fx-topo="0"     px do alto da tela em que o primeiro card para

     É o mesmo que position: sticky faria, mas em JS — e por um motivo: abaixo
     de 402px o js/shell.js reduz o .page com transform, e sticky dentro de um
     elemento transformado passa a grudar no referencial dele, não na janela
     (os cards travavam fora da tela). Aqui a posição é medida ao vivo e
     convertida pela escala, como no pin-horizontal.

     A altura do documento não muda: os cards só recebem translateY, e o espaço
     deles no fluxo continua igual. Isso importa nas páginas de decoração
     global, em que as decorações são absolutas e não acompanhariam o fluxo.
     ========================================================= */
  function cardStack(sec) {
    var itens = gsap.utils.toArray(sec.querySelectorAll("[data-fx-item]"));
    if (itens.length < 2) return;
    var faixa = pct(sec.getAttribute("data-fx-faixa"), 10);
    var topo = pct(sec.getAttribute("data-fx-topo"), 0);

    // De baixo para cima: a posição de cada card depende da do card seguinte.
    // A página não congela e a altura do documento não muda — os cards só
    // recebem translateY, e o espaço deles no fluxo continua igual. Isso
    // importa nas páginas de decoração global, em que as decorações são
    // absolutas e não acompanhariam o fluxo.
    function medir() {
      var z = zoom(), pos = [], ultimo = itens.length - 1;
      for (var i = ultimo; i >= 0; i--) {
        var el = itens[i];
        var deslocado = gsap.getProperty(el, "y") || 0;
        var natural = el.getBoundingClientRect().top / z - deslocado;  // sem o efeito
        var p;
        if (i === ultimo) {
          p = natural;                               // o último nunca trava: leva a página
        } else {
          p = Math.max(natural, topo + faixa * i);   // trava no alto da tela
          // e nunca fica a menos de uma faixa do card de baixo: quando este
          // sobe, EMPURRA a pilha em vez de cobri-la (é o que mantém as
          // listrinhas de todos os cards à vista)
          p = Math.min(p, pos[i + 1] - faixa);
        }
        pos[i] = p;
        gsap.set(el, { y: p - natural });
      }
    }

    var st = ScrollTrigger.create({
      trigger: sec, start: "top bottom", end: "bottom top",
      onUpdate: medir, onRefresh: medir
    });
    medir();
    return function () {
      st.kill();
      itens.forEach(function (el) { gsap.set(el, { clearProps: "transform" }); });
    };
  }

  /* =========================================================
     orbit-in  (scroll contínuo, 1:1)
     O elemento percorre um arco — a curvatura de uma elipse do próprio layout —
     enquanto cresce e gira, tudo amarrado ao scroll: começa pequeno, "em pé" e
     num ponto da curva; termina na posição, tamanho e inclinação do CSS.
     Rolando para cima, desfaz.

       <span class="d-img28" data-fx="orbit-in" data-fx-curva=".d-sub1"
             data-fx-de-angulo="30" data-fx-escala="0.05" data-fx-rotacao="52.64">

     Opções:
       data-fx-curva=".x"        elemento cuja caixa define a elipse do trajeto
                                 (centro da caixa, raios = metade dela)
       data-fx-curva-metade="topo"  quando esse elemento é só a METADE DE CIMA da
                                 elipse (arco/cúpula): centro = base da caixa,
                                 raio vertical = altura inteira
       data-fx-de-angulo="30"    ângulo de partida na elipse, em graus
                                 (0 = direita, 90 = topo, 180 = esquerda)
       data-fx-escala="0.05"     tamanho no começo (1 = tamanho final)
       data-fx-rotacao="0"       graus a mais no começo (ex.: 52.64 deixa em pé
                                 um elemento que no CSS está inclinado -52.64)
       data-fx-inicio="100%"     ponto da tela (do centro final) em que começa
       data-fx-fim="50%"         ponto da tela em que termina

     O raio do fim sai do próprio elemento: o componente mede onde o centro dele
     cai em relação à elipse, então o trajeto termina exatamente na posição do
     CSS. Medições ao vivo a cada frame (não depende de recálculo).
     ========================================================= */
  function orbitIn(el) {
    var curva = document.querySelector(el.getAttribute("data-fx-curva") || "");
    if (!curva) return;
    var ang0 = pct(el.getAttribute("data-fx-de-angulo"), 30) * Math.PI / 180;
    var esc0 = pct(el.getAttribute("data-fx-escala"), 0.05);
    var rot0 = pct(el.getAttribute("data-fx-rotacao"), 0);
    var inicio = pct(el.getAttribute("data-fx-inicio"), 100) / 100;
    var fim = pct(el.getAttribute("data-fx-fim"), 50) / 100;

    gsap.set(el, { transformOrigin: "50% 50%" });

    // tudo em px de CSS, sem transform: offsetLeft/Top não sofrem com a animação
    function caixa(e, metadeTopo) {
      var cx = e.offsetLeft + e.offsetWidth / 2;
      if (metadeTopo) {
        return { cx: cx, cy: e.offsetTop + e.offsetHeight, rx: e.offsetWidth / 2, ry: e.offsetHeight };
      }
      return { cx: cx, cy: e.offsetTop + e.offsetHeight / 2,
               rx: e.offsetWidth / 2, ry: e.offsetHeight / 2 };
    }

    function atualizar() {
      var z = zoom();
      var c = caixa(curva, el.getAttribute("data-fx-curva-metade") === "topo"), m = caixa(el);
      // onde o centro final cai na elipse: ângulo e quanto além do raio
      var dx = (m.cx - c.cx) / c.rx, dy = (c.cy - m.cy) / c.ry;
      var angF = Math.atan2(dy, dx), kF = Math.hypot(dx, dy);
      // progresso pelo ponto da tela em que está o centro final (sem transform)
      var topoArt = el.offsetParent ? el.offsetParent.getBoundingClientRect().top : 0;
      var yTela = topoArt + m.cy * z;
      var de = window.innerHeight * inicio, ate = window.innerHeight * fim;
      var p = gsap.utils.clamp(0, 1, (de - yTela) / (de - ate));
      var ang = ang0 + (angF - ang0) * p, k = 1 + (kF - 1) * p;
      gsap.set(el, {
        x: c.cx + k * c.rx * Math.cos(ang) - m.cx,
        y: c.cy - k * c.ry * Math.sin(ang) - m.cy,
        scale: esc0 + (1 - esc0) * p,
        rotation: rot0 * (1 - p)
      });
    }

    var pedido = 0;
    function noScroll() {
      if (!pedido) pedido = requestAnimationFrame(function () { pedido = 0; atualizar(); });
    }
    window.addEventListener("scroll", noScroll, { passive: true });
    window.addEventListener("resize", noScroll);
    window.addEventListener("load", noScroll);
    atualizar();

    return function () {
      window.removeEventListener("scroll", noScroll);
      window.removeEventListener("resize", noScroll);
      window.removeEventListener("load", noScroll);
      if (pedido) cancelAnimationFrame(pedido);
      gsap.set(el, { clearProps: "transform,transformOrigin" });
    };
  }

  /* =========================================================
     slide-in-up  (scroll, disparado — não acompanha o scroll 1:1)
     Cada item fica escondido até o topo dele passar da sua linha (a `margem`
     px do fundo da tela); aí aparece, sem fade, NA BORDA DE BAIXO DA TELA e
     percorre todo o caminho, visível, até o lugar. Rolando de volta para cima,
     desce até a borda de baixo e se esconde ao cruzar a mesma linha.

       <ol data-fx="slide-in-up">
         <li data-fx-item>…</li>                   ← cada item decide sozinho
       </ol>

     Opções no contêiner:
       data-fx-margem="60"           px de tela acima do fundo em que o 1º item entra
       data-fx-escalonamento="0.1"   cada item seguinte espera +10% dessa margem
                                     (60, 66, 72, 78, 84…) — cascata
       data-fx-passo="400"           em vez da linha de cada item: px de scroll entre
                                     uma entrada e a seguinte, contados pelo 1º item
                                     (1º entra na margem, 2º 400px de scroll depois…)
       data-fx-deslocamento="base"   de onde o item sobe: "base" = da borda de
                                     baixo da tela; ou um número de px (ex. 40)
       data-fx-duracao="0.6"         segundos

     Por que não um gatilho do ScrollTrigger: o ponto de disparo pré-calculado
     dependia do estado do card-accordeon/pin-horizontal acima no momento do
     recálculo (carregamento de imagens, resize) e chegou a disparar ~380px
     atrasado. Aqui cada item lê a própria posição real a cada frame.
     ========================================================= */
  function slideInUp(sec) {
    var itens = gsap.utils.toArray(sec.querySelectorAll("[data-fx-item]"));
    if (!itens.length) return;
    var margem = pct(sec.getAttribute("data-fx-margem"), 60);
    var escala = pct(sec.getAttribute("data-fx-escalonamento"), 0.1);
    var passo = pct(sec.getAttribute("data-fx-passo"), 0);
    var attrDesloc = sec.getAttribute("data-fx-deslocamento");
    var fixo = (attrDesloc && attrDesloc !== "base") ? pct(attrDesloc, 40) : null;
    var duracao = pct(sec.getAttribute("data-fx-duracao"), 0.6);

    // quanto o item precisa descer (px de CSS) para ficar na borda de baixo da tela
    function ateBase(topoTela) {
      return fixo !== null ? fixo : Math.max(0, (window.innerHeight - topoTela) / zoom());
    }

    var visivel = itens.map(function () { return false; });
    // acima do que vem depois (ex.: banner logo abaixo), senão o item passaria por
    // trás; e cada item uma camada acima do anterior, para o que sobe da base nunca
    // passar por trás de um item de antes (pilhas com sobreposição, ex.: as contas)
    itens.forEach(function (el, i) {
      gsap.set(el, { visibility: "hidden", position: "relative", zIndex: 2 + i });
    });

    function checar() {
      var z = zoom();
      // na ordem: um item só entra se o anterior já entrou, e só sai depois do
      // seguinte (garante a pilha se montando/desmontando em sequência)
      // topo do item sem o deslocamento da própria animação, em px de tela
      function topoDe(el) { return el.getBoundingClientRect().top - gsap.getProperty(el, "y") * z; }
      var topoPrimeiro = topoDe(itens[0]);
      itens.forEach(function (el, i) {
        var topo = topoDe(el);
        var dentro = passo
          ? topoPrimeiro <= window.innerHeight - margem - passo * i      // por scroll, a partir do 1º
          : topo <= window.innerHeight - margem * (1 + escala * i);      // linha de cada item
        dentro = dentro && (i === 0 || visivel[i - 1]);
        if (dentro === visivel[i]) return;
        visivel[i] = dentro;
        if (dentro) {
          // se ainda estava descendo (saída interrompida), continua de onde está
          var deOnde = gsap.isTweening(el) ? gsap.getProperty(el, "y") : ateBase(topo);
          gsap.set(el, { visibility: "visible", y: deOnde });
          gsap.to(el, { y: 0, duration: duracao, ease: "power2.out", overwrite: true });
        } else {
          gsap.to(el, { y: ateBase(topo), duration: duracao, ease: "power2.in", overwrite: true,
            onComplete: function () { gsap.set(el, { visibility: "hidden" }); } });
        }
      });
    }

    var pedido = 0;
    function noScroll() {
      if (!pedido) pedido = requestAnimationFrame(function () { pedido = 0; checar(); });
    }
    window.addEventListener("scroll", noScroll, { passive: true });
    window.addEventListener("resize", noScroll);
    window.addEventListener("load", noScroll);
    checar();

    return function () {
      window.removeEventListener("scroll", noScroll);
      window.removeEventListener("resize", noScroll);
      window.removeEventListener("load", noScroll);
      if (pedido) cancelAnimationFrame(pedido);
      gsap.killTweensOf(itens);
      gsap.set(itens, { clearProps: "visibility,transform,position,zIndex" });
    };
  }

  /* =========================================================
     slide-in-left  (efeito de ENTRADA: roda ao carregar, não depende do scroll)
     O elemento desliza para a ESQUERDA: entra vindo de fora do bloco pela
     direita até a posição final, sempre opaco (o recorte do bloco esconde a
     parte que ainda está fora). Começa quando a imagem termina de carregar.

     Opções no próprio elemento:
       data-fx-duracao="1.5" segundos
       data-fx-atraso="0"    segundos antes de começar

     Precisa do trecho anti-piscada no <head> (ver a skill scroll-fx).
     ========================================================= */
  function slideInLeft(el) {
    var duracao = pct(el.getAttribute("data-fx-duracao"), 1.5);
    var atraso = pct(el.getAttribute("data-fx-atraso"), 0);

    // começa inteiro para fora, à direita do ancestral que recorta (overflow), px de CSS
    var corte = el.parentElement;
    while (corte && corte !== document.body && getComputedStyle(corte).overflowX === "visible") {
      corte = corte.parentElement;
    }
    var borda = (corte && corte !== document.body) ? corte.getBoundingClientRect().right : window.innerWidth;
    var fora = (borda - el.getBoundingClientRect().left) / zoom();

    gsap.set(el, { x: fora });
    var tween = gsap.to(el, {
      x: 0, duration: duracao, delay: atraso, ease: "power2.out", paused: true,
      clearProps: "transform" // no fim, devolve o elemento ao CSS
    });

    var foi = false;
    function vai() { if (!foi) { foi = true; tween.play(); } }
    if (el.tagName === "IMG" && !el.complete) {
      el.addEventListener("load", vai);
      el.addEventListener("error", vai);
      setTimeout(vai, 4000); // imagem lenta demais: entra assim mesmo
    } else {
      vai();
    }
  }

  /* =========================================================
     scale-up  (efeito de ENTRADA: roda ao carregar, não depende do scroll)
     Os itens crescem a partir da base (centro de baixo), de 0 ao tamanho
     final, um depois do outro na ordem do HTML. Pensado para formas de fundo
     (ex.: as cúpulas atrás da foto do hero).

       <div data-fx="scale-up">
         <span data-fx-item>…</span>               ← anima o invólucro, não a
       </div>                                        imagem (que pode ter rotate)

     Opções no contêiner:
       data-fx-duracao="0.9"    segundos de cada item
       data-fx-intervalo="0.15" segundos entre um item e o seguinte
       data-fx-atraso="0"       segundos antes do primeiro
       data-fx-origem="50% 100%" ponto de onde cresce (transform-origin)
       data-fx-fundo="#ffe3cc"  cor de fundo do contêiner só enquanto os itens
                                entram (não fica branco atrás deles); sai no fim
       data-fx-fundo-abaixo=".x" o fundo só começa onde termina esse elemento —
                                use quando houver uma camada translúcida por
                                cima (senão as cores somam e o topo escurece).
                                A cor deve ser a que essa camada dá sobre branco.

     Precisa do trecho anti-piscada no <head> (ver a skill scroll-fx).
     ========================================================= */
  function scaleUp(sec) {
    var itens = gsap.utils.toArray(sec.querySelectorAll("[data-fx-item]"));
    if (!itens.length) return;
    var fundo = sec.getAttribute("data-fx-fundo");
    if (fundo) {
      var acima = sec.getAttribute("data-fx-fundo-abaixo");
      var ref = acima && sec.querySelector(acima);
      if (ref) {
        // px de CSS do topo do contêiner até o fim da camada de cima
        var corte = (ref.getBoundingClientRect().bottom - sec.getBoundingClientRect().top) / zoom();
        sec.style.backgroundImage = "linear-gradient(to bottom, transparent " + corte + "px, " + fundo + " " + corte + "px)";
      } else {
        sec.style.backgroundColor = fundo;
      }
    }
    gsap.set(itens, { scale: 0, transformOrigin: sec.getAttribute("data-fx-origem") || "50% 100%" });
    gsap.to(itens, {
      scale: 1,
      duration: pct(sec.getAttribute("data-fx-duracao"), 0.9),
      stagger: pct(sec.getAttribute("data-fx-intervalo"), 0.15),
      delay: pct(sec.getAttribute("data-fx-atraso"), 0),
      ease: "power3.out",
      clearProps: "transform,transformOrigin", // no fim, devolve os itens ao CSS
      onComplete: function () {
        if (fundo) sec.style.backgroundColor = sec.style.backgroundImage = "";
      }
    });
  }

  /* =========================================================
     pop-in  (entrada, ao carregar ou ao chegar à tela)
     Os itens surgem um de cada vez, na ordem do HTML: crescendo do centro com um
     quique ("pop"), subindo com fade ("fade-up") ou vindo da esquerda com fade
     ("fade-right"). Espera as imagens dos itens carregarem (limite de 3s).

     QUANDO cada item surge:
       - contêiner com data-fx-quando="scroll": a sequência do contêiner começa
         quando ele chega à tela;
       - item com data-fx-grupo="x": forma uma sequência própria, que começa
         quando esse grupo chega à tela (vários grupos no mesmo contêiner);
       - o resto: ao carregar a página.
     O que espera a tela RECOMEÇA a cada entrada: o grupo que sai inteiro da tela
     volta ao estado inicial e anima de novo quando o leitor voltar (e no Ctrl+R,
     que devolve o leitor onde ele estava). Só a sequência de abertura
     ("carregar") roda uma vez por carregamento.

       <ul data-fx="pop-in" data-fx-quando="scroll"
           data-fx-entrada="fade-right" data-fx-intervalo="0.5">
         <li data-fx-item>…</li>
       </ul>

     Opções no contêiner:
       data-fx-quando="carregar"  "carregar" (padrão) ou "scroll"
       data-fx-entrada="pop"      padrão dos itens: "pop", "fade-up" ou "fade-right"
       data-fx-duracao="0.5"      segundos de cada item
       data-fx-intervalo="0.2"    segundos entre um item e o seguinte
       data-fx-atraso="0"         segundos antes do primeiro (só ao carregar)
       data-fx-margem="100"       px acima do fundo da tela que disparam a sequência
       data-fx-deslocamento="30"  px percorridos no fade-up/fade-right
     Opções no item (sobrepõem as do contêiner):
       data-fx-entrada, data-fx-deslocamento, data-fx-origem="50% 50%",
       data-fx-grupo="x", data-fx-intervalo, data-fx-margem,
       data-fx-balanco="7"        depois de surgir, gira ±N graus, sem parar
       data-fx-balanco-duracao="1.6"
       data-fx-flutuacao="10"     depois de surgir, sobe N px e volta, sem parar

     Precisa do trecho anti-piscada no <head> (ver a skill scroll-fx).
     ========================================================= */
  function popIn(sec) {
    var itens = gsap.utils.toArray(sec.querySelectorAll("[data-fx-item]"));
    if (!itens.length) return;
    var duracao = pct(sec.getAttribute("data-fx-duracao"), 0.5);
    var atraso = pct(sec.getAttribute("data-fx-atraso"), 0);

    function attr(el, nome, padrao) {
      var v = el.getAttribute(nome);
      return v !== null ? v : sec.getAttribute(nome) !== null ? sec.getAttribute(nome) : padrao;
    }
    function tipo(el) {
      var t = attr(el, "data-fx-entrada", "pop");
      return (t === "fade-up" || t === "fade-right") ? t : "pop";
    }
    function desloc(el) { return pct(attr(el, "data-fx-deslocamento", "30"), 30); }

    // Estado inicial de um item. Também rearma o grupo que saiu da tela, então
    // desfaz o que a entrada (e o balanço/flutuação que vêm depois) deixou.
    function estadoInicial(el) {
      gsap.killTweensOf(el);
      var t = tipo(el), d = desloc(el), base = { x: 0, y: 0, rotation: 0 };
      if (t === "fade-up") base.y = d;
      else if (t === "fade-right") base.x = -d;
      if (t === "pop") {
        base.scale = 0;
        base.transformOrigin = el.getAttribute("data-fx-origem") || "50% 50%";
      } else {
        base.scale = 1; base.autoAlpha = 0;
      }
      gsap.set(el, base);
    }
    itens.forEach(estadoInicial);

    // depois de surgir: balanço (gira) e/ou flutuação (sobe e desce), sem parar
    function continuar(el) {
      var graus = pct(el.getAttribute("data-fx-balanco"), 0);
      var altura = pct(el.getAttribute("data-fx-flutuacao"), 0);
      if (!graus && !altura) { gsap.set(el, { clearProps: "transform,transformOrigin,opacity,visibility" }); return; }
      if (graus) {
        var ida = pct(el.getAttribute("data-fx-balanco-duracao"), 1.6);
        // do repouso até um lado, depois de um lado ao outro
        gsap.timeline()
          .to(el, { rotation: -graus, duration: ida / 2, ease: "sine.out" })
          .to(el, { rotation: graus, duration: ida, ease: "sine.inOut", repeat: -1, yoyo: true });
      }
      if (altura) {
        gsap.to(el, { y: -altura, duration: gsap.utils.random(1.4, 2), ease: "sine.inOut",
          repeat: -1, yoyo: true, delay: gsap.utils.random(0, 0.6) });
      }
    }

    // a sequência de um grupo, depois de as imagens dele carregarem (limite 3s)
    function surgir(grupo, intervalo, espera) {
      var foi = false;
      function vai() {
        if (foi) return; foi = true;
        grupo.forEach(function (el, i) {
          var quando = espera + i * intervalo, acabou = function () { continuar(el); };
          if (tipo(el) === "pop") {
            gsap.to(el, { scale: 1, duration: duracao, delay: quando, ease: "back.out(1.7)", onComplete: acabou });
          } else {
            gsap.to(el, { autoAlpha: 1, x: 0, y: 0, duration: Math.max(duracao, 0.6), delay: quando,
              ease: "power2.out", onComplete: acabou });
          }
        });
      }
      var imgs = grupo.map(function (el) { return el.tagName === "IMG" ? el : el.querySelector("img"); })
        .filter(function (im) { return im && !im.complete; });
      if (!imgs.length) return vai();
      var faltam = imgs.length;
      imgs.forEach(function (im) {
        function pronto() { if (--faltam <= 0) vai(); }
        im.addEventListener("load", pronto);
        im.addEventListener("error", pronto);
      });
      setTimeout(vai, 3000); // imagem lenta demais: entra assim mesmo
    }

    // monta os lotes: ao carregar, ou por chegada à tela (contêiner ou grupos)
    var porScroll = sec.getAttribute("data-fx-quando") === "scroll";
    var grupos = {}, aoCarregar = [];
    itens.forEach(function (el) {
      var g = el.getAttribute("data-fx-grupo") || (porScroll ? "__sec" : null);
      if (g) (grupos[g] = grupos[g] || []).push(el); else aoCarregar.push(el);
    });
    if (aoCarregar.length) surgir(aoCarregar, pct(sec.getAttribute("data-fx-intervalo"), 0.2), atraso);

    var pendentes = Object.keys(grupos).map(function (g) {
      var primeiro = grupos[g][0];
      return { itens: grupos[g],
               intervalo: pct(attr(primeiro, "data-fx-intervalo", "0.2"), 0.2),
               margem: pct(attr(primeiro, "data-fx-margem", "100"), 100),
               dentro: false };   // a sequência está rodando/terminada na tela?
    });
    if (!pendentes.length) return;

    // A sequência RECOMEÇA a cada entrada na tela: quando o grupo sai inteiro,
    // volta ao estado inicial e espera a próxima. É o que faz a entrada
    // aparecer de novo no Ctrl+R (que devolve o leitor onde ele estava) e a
    // cada vez que o leitor sobe e desce a página.
    function checar() {
      pendentes.forEach(function (g) {
        var primeiro = g.itens[0].getBoundingClientRect();
        var ultimo = g.itens[g.itens.length - 1].getBoundingClientRect();
        var chegou = primeiro.top <= window.innerHeight - g.margem && ultimo.bottom > 0;
        var saiu = ultimo.bottom <= 0 || primeiro.top > window.innerHeight;
        if (!g.dentro && chegou) { g.dentro = true; surgir(g.itens, g.intervalo, 0); }
        else if (g.dentro && saiu) { g.dentro = false; g.itens.forEach(estadoInicial); }
      });
    }
    var pedido = 0;
    function noScroll() {
      if (!pedido) pedido = requestAnimationFrame(function () { pedido = 0; checar(); });
    }
    window.addEventListener("scroll", noScroll, { passive: true });
    window.addEventListener("resize", noScroll);
    checar();
  }

  /* =========================================================
     magnetic-pull  (efeito de ENTRADA: roda ao carregar, não depende do scroll)
     O texto é quebrado em letras (SplitText) e cada letra vem de uma posição e
     rotação aleatórias, surgindo, até o lugar — como se fossem puxadas por um
     ímã. No fim o texto volta a ser o HTML original (split.revert()).

       <h1 data-fx="magnetic-pull">…</h1>

     Opções no elemento:
       data-fx-distancia="200"  px máximos de onde cada letra vem (x e y)
       data-fx-rotacao="90"     graus máximos de rotação inicial
       data-fx-intervalo="0.02" segundos entre uma letra e a seguinte
       data-fx-duracao="1"      segundos de cada letra
       data-fx-atraso="0"       segundos antes da primeira

     Precisa: SplitText.min.js (gsap 3.15, jsDelivr) antes deste arquivo e o
     trecho anti-piscada no <head>. Sem o SplitText, o texto fica parado.
     ========================================================= */
  function magneticPull(el) {
    if (!window.SplitText) return;
    gsap.registerPlugin(SplitText);
    var dist = pct(el.getAttribute("data-fx-distancia"), 200);
    var rot = pct(el.getAttribute("data-fx-rotacao"), 90);
    // escondido até as fontes: as letras são medidas na quebra, e com a fonte
    // substituta sairiam do tamanho errado
    gsap.set(el, { visibility: "hidden" });
    function vai() {
      // chars sem words quebraria linhas no meio da palavra: smartWrap segura a palavra
      var split = SplitText.create(el, { type: "chars", smartWrap: true });
      gsap.set(el, { visibility: "visible" });
      gsap.from(split.chars, {
        x: function () { return gsap.utils.random(-dist, dist); },
        y: function () { return gsap.utils.random(-dist, dist); },
        rotation: function () { return gsap.utils.random(-rot, rot); },
        opacity: 0,
        stagger: pct(el.getAttribute("data-fx-intervalo"), 0.02),
        duration: pct(el.getAttribute("data-fx-duracao"), 1),
        delay: pct(el.getAttribute("data-fx-atraso"), 0),
        ease: "power3.out",
        onComplete: function () { split.revert(); } // volta ao HTML original
      });
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(vai); else vai();
  }

  /* =========================================================
     typewriter  (entrada: roda ao carregar)
     Os textos são DIGITADOS letra a letra, um de cada vez: o primeiro aparece,
     fica um instante, é apagado de trás para frente, e o seguinte é digitado no
     lugar. O último fica.

       <section data-fx="typewriter">
         <h1 data-fx-item>Não engane<br><span class="am">SEU CLIENTE</span></h1>
         <p  data-fx-item>mas aprenda<br>com ela</p>
       </section>

     Opções no contêiner:
       data-fx-velocidade="0.06"  segundos por letra ao escrever
       data-fx-apagar="0.03"      segundos por letra ao apagar
       data-fx-pausa="1.2"        segundos que o texto fica inteiro na tela
       data-fx-atraso="0.3"       segundos antes de começar

     O markup de cada item é preservado (<br>, <span> de cor): o efeito esvazia
     e repõe só os NÓS DE TEXTO, na ordem. Como as quebras continuam no lugar, a
     caixa do texto não muda de altura enquanto digita — o que importa nas
     páginas de decoração global, em que as decorações são absolutas.

     Precisa do trecho anti-piscada no <head> (ver a skill scroll-fx).
     ========================================================= */
  function typewriter(sec) {
    var itens = gsap.utils.toArray(sec.querySelectorAll("[data-fx-item]"));
    if (!itens.length) return;
    var vel = pct(sec.getAttribute("data-fx-velocidade"), 0.06);
    var velApagar = pct(sec.getAttribute("data-fx-apagar"), 0.03);
    var pausa = pct(sec.getAttribute("data-fx-pausa"), 1.2);
    var atraso = pct(sec.getAttribute("data-fx-atraso"), 0.3);
    // data-fx-repetir="1.5": recomeça sem parar, esperando N s entre uma volta
    // e outra (no loop o último texto também é apagado, para o ciclo fechar)
    var repetir = sec.getAttribute("data-fx-repetir");

    // guarda os nós de texto de cada item, na ordem em que aparecem
    var dados = itens.map(function (el) {
      var nos = [];
      (function anda(n) {
        for (var f = n.firstChild; f; f = f.nextSibling) {
          if (f.nodeType === 3) { if (f.nodeValue.length) nos.push({ no: f, txt: f.nodeValue }); }
          else if (f.nodeType === 1) anda(f);
        }
      })(el);
      var total = 0;
      nos.forEach(function (x) { total += x.txt.length; });
      return { el: el, nos: nos, total: total };
    });

    function escrever(d, n) {
      var resta = Math.round(n);
      d.nos.forEach(function (x) {
        var k = resta <= 0 ? 0 : Math.min(x.txt.length, resta);
        if (x.no.nodeValue.length !== k) x.no.nodeValue = x.txt.slice(0, k);
        resta -= k;
      });
    }

    dados.forEach(function (d) { escrever(d, 0); gsap.set(d.el, { visibility: "hidden" }); });

    var tl = gsap.timeline({ delay: atraso, repeat: repetir !== null ? -1 : 0,
                             repeatDelay: pct(repetir, 1) });
    dados.forEach(function (d, i) {
      var conta = { n: 0 };
      tl.set(d.el, { visibility: "visible" })
        .to(conta, { n: d.total, duration: d.total * vel, ease: "none",
                     onUpdate: function () { escrever(d, conta.n); } });
      if (i < dados.length - 1 || repetir !== null) {   // o último fica, salvo no loop
        tl.to({}, { duration: pausa })
          .to(conta, { n: 0, duration: d.total * velApagar, ease: "none",
                       onUpdate: function () { escrever(d, conta.n); } })
          .set(d.el, { visibility: "hidden" });
      }
    });

    return function () {
      tl.kill();
      dados.forEach(function (d) {
        escrever(d, d.total);
        gsap.set(d.el, { clearProps: "visibility" });
      });
    };
  }

  /* ---------- inicialização ---------- */
  var efeitos = { "card-accordeon": cardAccordeon, "pin-horizontal": pinHorizontal, "slide-in-up": slideInUp, "orbit-in": orbitIn, "card-stack": cardStack };
  var entradas = { "slide-in-left": slideInLeft, "scale-up": scaleUp, "pop-in": popIn, "magnetic-pull": magneticPull, "typewriter": typewriter };

  // entradas: já, sem esperar fontes (não medem texto). O trecho do <head>
  // escondeu os elementos antes da primeira pintura; daqui em diante o GSAP manda.
  var semMovimento = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  gsap.utils.toArray("[data-fx]").forEach(function (el) {
    var f = entradas[el.getAttribute("data-fx")];
    if (f && !semMovimento) f(el);
  });
  document.documentElement.classList.remove("fx-espera");

  var alvos = gsap.utils.toArray("[data-fx]").filter(function (el) {
    return efeitos[el.getAttribute("data-fx")];
  });
  if (!alvos.length) return;

  // A ancoragem de rolagem do navegador compensa conteúdo que cresce acima do
  // ponto de leitura mexendo no scroll. Com scrub isso realimenta (o item cresce,
  // o scroll anda, o item cresce mais) e os itens abririam sozinhos.
  document.documentElement.style.overflowAnchor = "none";
  document.body.style.overflowAnchor = "none";

  // Itens do slide-in-up já nascem escondidos, antes de esperar as fontes: senão,
  // quem abre a página com o bloco na tela vê a pilha inteira por um instante.
  var semMov = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!semMov) {
    alvos.forEach(function (el) {
      if (el.getAttribute("data-fx") === "slide-in-up") {
        gsap.set(el.querySelectorAll("[data-fx-item]"), { visibility: "hidden" });
      }
    });
  }

  // Só começa depois das fontes: os efeitos medem alturas de texto, e com a fonte
  // substituta as medidas saem erradas. Até lá a página fica como no CSS.
  function iniciar() {
    var mm = gsap.matchMedia();
    mm.add("(prefers-reduced-motion: no-preference)", function () {
      // na ordem da página (de cima para baixo), como o ScrollTrigger espera
      var limpezas = alvos.map(function (el) {
        return efeitos[el.getAttribute("data-fx")](el);
      });
      return function () {
        // ao contrário: congelamentos aninhados se desfazem de fora para dentro
        limpezas.slice().reverse().forEach(function (f) { if (f) f(); });
      };
    });
  }
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(iniciar);
  } else {
    iniciar();
  }

  // imagens mudam alturas ao carregar: recalcula os gatilhos
  window.addEventListener("load", function () { ScrollTrigger.refresh(); });

  // para efeitos futuros medirem posições abaixo de um card-accordeon/pin-horizontal
  window.ScrollFx = { offsetAcima: offsetAcima, zoom: zoom };
})();
