/* =========================================================
   Revista Assaí — efeitos amarrados ao scroll (GSAP + ScrollTrigger)
   Compartilhado entre edições. Uso declarativo, sem JS por página:

     <section data-fx="card-accordeon">          ← contêiner
       <div data-fx-item>…</div>                 ← itens que abrem
       <div data-fx-item>…</div>
     </section>

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

  /* ---------- efeitos que mudam a altura da página ----------
     Cada um registra quanto está "encolhido" agora (px de CSS). Um gatilho mais
     abaixo soma isso para medir onde ele estará quando o leitor chegar lá, já
     com tudo acima aberto. */
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

  /* ---------- inicialização ---------- */
  var efeitos = { "card-accordeon": cardAccordeon };
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

  // para efeitos futuros medirem posições abaixo de um card-accordeon
  window.ScrollFx = { offsetAcima: offsetAcima, zoom: zoom };
})();
