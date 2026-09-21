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

  // abaixo de 402px o js/shell.js aplica zoom no .page: medidas de layout
  // (px de CSS) viram px de scroll multiplicadas por esse zoom
  function zoom() {
    var page = document.querySelector(".page");
    return (page && parseFloat(page.style.zoom)) || 1;
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

     Como congela: o .page vai para dentro de dois invólucros — o de fora ganha
     um espaçador com altura igual ao percurso do texto; o de dentro é position: sticky com
     top negativo, então a coluna inteira "gruda" no ponto da trava enquanto o
     scroll atravessa essa altura extra. Sticky é do navegador: não treme e
     respeita o zoom do mobile (o pin do ScrollTrigger, com position: fixed,
     aplicava o zoom duas vezes). O ponto da trava é medido do layout real a
     cada frame, então continua certo com um card-accordeon acima abrindo e
     fechando. Anima o scrollLeft do trilho: convive com o toque/arrasto nativos.
     ========================================================= */
  function pinHorizontal(sec) {
    var trilho = sec.querySelector("[data-fx-item]");
    var page = document.querySelector(".page");
    // um por página: congela a coluna inteira
    if (!trilho || !page || page.parentElement.classList.contains("fx-congela")) return;
    var inicio = pct(sec.getAttribute("data-fx-inicio"), 50);

    var fora = document.createElement("div");   // coluna + espaçador
    var dentro = document.createElement("div"); // gruda (sticky)
    var espaco = document.createElement("div"); // altura extra = percurso do texto
    fora.className = "fx-congela-fora";
    dentro.className = "fx-congela";
    page.parentNode.insertBefore(fora, page);
    fora.appendChild(dentro);
    fora.appendChild(espaco);
    dentro.appendChild(page);
    dentro.style.position = "sticky";
    // espaçador, não padding: o sticky só anda dentro da área de conteúdo do pai

    var dist = 0, percurso = 0, trava = 0;
    function medir() {
      var z = zoom();
      dist = Math.max(0, trilho.scrollWidth - trilho.clientWidth); // px de CSS
      percurso = dist * z;                                         // px de tela, 1:1
      espaco.style.height = percurso + "px";
      atualizar();
    }
    function atualizar() {
      // ponto da trava (scroll em px de tela), do layout de agora: o trilho medido
      // em relação à própria coluna não é afetado pelo sticky
      var rp = page.getBoundingClientRect(), rt = trilho.getBoundingClientRect();
      var centro = rt.top + rt.height / 2 - rp.top;        // do topo da coluna
      var alvo = window.innerHeight * inicio / 100;          // onde o centro para
      var topoFora = fora.getBoundingClientRect().top + window.scrollY;
      trava = topoFora + centro - alvo;
      var top = Math.round(alvo - centro) + "px";            // sticky: medido do topo da tela
      if (dentro.style.top !== top) dentro.style.top = top;
      if (dist) trilho.scrollLeft = gsap.utils.clamp(0, 1, (window.scrollY - trava) / percurso) * dist;
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
      contenedor: sec,
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
      fora.parentNode.insertBefore(page, fora);
      fora.remove();
      trilho.scrollLeft = 0;
    };
  }

  /* =========================================================
     slide-in-up  (scroll, disparado — não acompanha o scroll 1:1)
     Cada item fica escondido até o topo dele passar da sua linha (a `margem`
     px do fundo da tela); aí aparece, sem fade, e sobe até o lugar. Rolando de
     volta para cima, desce e se esconde ao cruzar a mesma linha.

       <ol data-fx="slide-in-up">
         <li data-fx-item>…</li>                   ← cada item decide sozinho
       </ol>

     Opções no contêiner:
       data-fx-margem="60"           px de tela acima do fundo em que o 1º item entra
       data-fx-escalonamento="0.1"   cada item seguinte espera +10% dessa margem
                                     (60, 66, 72, 78, 84…) — cascata
       data-fx-deslocamento="40"     px que o item sobe ao entrar (e desce ao sair)
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
    var desloc = pct(sec.getAttribute("data-fx-deslocamento"), 40);
    var duracao = pct(sec.getAttribute("data-fx-duracao"), 0.6);

    var visivel = itens.map(function () { return false; });
    gsap.set(itens, { visibility: "hidden", y: desloc });

    function checar() {
      var z = zoom();
      itens.forEach(function (el, i) {
        var linha = window.innerHeight - margem * (1 + escala * i);
        // topo do item sem o deslocamento da própria animação, em px de tela
        var topo = el.getBoundingClientRect().top - gsap.getProperty(el, "y") * z;
        var dentro = topo <= linha;
        if (dentro === visivel[i]) return;
        visivel[i] = dentro;
        if (dentro) {
          gsap.set(el, { visibility: "visible" });
          gsap.to(el, { y: 0, duration: duracao, ease: "power2.out", overwrite: true });
        } else {
          gsap.to(el, { y: desloc, duration: duracao, ease: "power2.in", overwrite: true,
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
      gsap.set(itens, { clearProps: "visibility,transform" });
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

  /* ---------- inicialização ---------- */
  var efeitos = { "card-accordeon": cardAccordeon, "pin-horizontal": pinHorizontal, "slide-in-up": slideInUp };
  var entradas = { "slide-in-left": slideInLeft };

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
        limpezas.forEach(function (f) { if (f) f(); });
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
