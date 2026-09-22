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
    var attrDesloc = sec.getAttribute("data-fx-deslocamento");
    var fixo = (attrDesloc && attrDesloc !== "base") ? pct(attrDesloc, 40) : null;
    var duracao = pct(sec.getAttribute("data-fx-duracao"), 0.6);

    // quanto o item precisa descer (px de CSS) para ficar na borda de baixo da tela
    function ateBase(topoTela) {
      return fixo !== null ? fixo : Math.max(0, (window.innerHeight - topoTela) / zoom());
    }

    var visivel = itens.map(function () { return false; });
    // acima do que vem depois (ex.: banner logo abaixo), senão o item passaria por trás
    gsap.set(itens, { visibility: "hidden", position: "relative", zIndex: 2 });

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
     pop-in  (efeito de ENTRADA: roda ao carregar, não depende do scroll)
     Os itens surgem um de cada vez, na ordem do HTML, crescendo do centro com
     um pequeno quique no fim ("pop"). Espera as imagens dos itens carregarem
     (limite de 3s), para não surgirem vazios.

       <div data-fx="pop-in">                      ← pode ser a camada de decoração
         <span data-fx-item data-fx-balanco="30">…</span>  ← depois fica balançando
         <span data-fx-item data-fx-flutuacao="20">…</span>   ← depois fica flutuando
       </div>

     Opções no contêiner:
       data-fx-duracao="0.5"     segundos de cada item
       data-fx-intervalo="0.2"   segundos entre um item e o seguinte
       data-fx-atraso="0"        segundos antes do primeiro
     Opção no item:
       data-fx-balanco="30"      depois de surgir, gira ±N graus em volta do
                                 centro, ida e volta, sem parar
       data-fx-balanco-duracao="1.6"  segundos de cada ida (ou volta)
       data-fx-flutuacao="20"    depois de surgir, sobe N px e volta, sem parar;
                                 cada item com ritmo e fase um pouco diferentes
                                 (para não flutuarem sincronizados)

     Precisa do trecho anti-piscada no <head> (ver a skill scroll-fx).
     ========================================================= */
  function popIn(sec) {
    var itens = gsap.utils.toArray(sec.querySelectorAll("[data-fx-item]"));
    if (!itens.length) return;
    var duracao = pct(sec.getAttribute("data-fx-duracao"), 0.5);
    var intervalo = pct(sec.getAttribute("data-fx-intervalo"), 0.2);
    var atraso = pct(sec.getAttribute("data-fx-atraso"), 0);

    gsap.set(itens, { scale: 0, transformOrigin: "50% 50%" });

    // depois de surgir: balanço (gira) e/ou flutuação (sobe e desce), sem parar
    function continuar(el) {
      var graus = pct(el.getAttribute("data-fx-balanco"), 0);
      var altura = pct(el.getAttribute("data-fx-flutuacao"), 0);
      if (!graus && !altura) { gsap.set(el, { clearProps: "transform,transformOrigin" }); return; }
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

    function comecar() {
      gsap.to(itens, {
        scale: 1, duration: duracao, delay: atraso, ease: "back.out(1.7)",
        stagger: { each: intervalo, onComplete: function () { continuar(this.targets()[0]); } }
      });
    }

    var imgs = itens.map(function (el) { return el.tagName === "IMG" ? el : el.querySelector("img"); })
      .filter(function (im) { return im && !im.complete; });
    var foi = false;
    function vai() { if (!foi) { foi = true; comecar(); } }
    if (!imgs.length) return vai();
    var faltam = imgs.length;
    imgs.forEach(function (im) {
      function pronto() { if (--faltam <= 0) vai(); }
      im.addEventListener("load", pronto);
      im.addEventListener("error", pronto);
    });
    setTimeout(vai, 3000); // imagem lenta demais: entra assim mesmo
  }

  /* ---------- inicialização ---------- */
  var efeitos = { "card-accordeon": cardAccordeon, "pin-horizontal": pinHorizontal, "slide-in-up": slideInUp };
  var entradas = { "slide-in-left": slideInLeft, "scale-up": scaleUp, "pop-in": popIn };

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
