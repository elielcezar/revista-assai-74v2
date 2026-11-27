/* Revista Assaí #76 — invólucro das páginas vindas do Webflow (comportamento igual ao da #75) */
(function () {
  "use strict";

  /* HEAD e RODAPÉ sao desenhos de 402px: em telas menores, reduzidos na proporcao.
     zoom (e nao transform) para que a caixa ocupe no fluxo a altura reduzida. */
  var FRAME_W = 402;
  var fixos = document.querySelectorAll(".page > .head, .page > .foot");
  function ajusta() {
    var w = document.documentElement.clientWidth || window.innerWidth;
    var z = w < FRAME_W ? String(w / FRAME_W) : "";
    for (var i = 0; i < fixos.length; i++) fixos[i].style.zoom = z;
  }
  ajusta();
  window.addEventListener("resize", ajusta);
  window.addEventListener("orientationchange", ajusta);

  /* menu do celular: a faixa abre rolada até o item ativo (posição de cada página no data-rolagem) */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = parseInt(nav.getAttribute("data-rolagem"), 10) || 0;

  /* voltar ao topo */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* carrosseis de rolagem lateral do Webflow: ideias do DELIVERY ([data-carrossel]) e
     beneficios do Assai Pay na NOTICIAS ([data-faixa], que ja tem setas e pontos).
     No celular sao rolagem nativa (dedo), que o mouse nao arrasta. Com mouse: arrastar
     anda um item por vez e para nas pontas, como os carrosseis da #74/#75. O dedo
     continua com a rolagem nativa; indicadores, setas e pontos acompanham a rolagem. */
  var faixas = [];
  var q1 = document.querySelectorAll(".page [data-carrossel]");
  for (var k = 0; k < q1.length; k++) faixas.push([q1[k], q1[k].children]);
  var q2 = document.querySelectorAll(".page [data-faixa]");
  for (k = 0; k < q2.length; k++) {
    var jan = q2[k].querySelector(".rv-nt-janela");
    if (jan) faixas.push([jan, q2[k].querySelectorAll(".rv-nt-painel")]);
  }
  for (k = 0; k < faixas.length; k++) (function (lista, itens) {
    var x0 = null, s0 = 0, moveu = false, id = 0;
    function posicoes() {
      var p = [];
      for (var i = 0; i < itens.length; i++) p.push(itens[i].offsetLeft - itens[0].offsetLeft);
      return p;
    }
    lista.classList.add("rv-arrastavel");
    lista.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      x0 = e.clientX; s0 = lista.scrollLeft; moveu = false; id = e.pointerId;
      lista.style.scrollSnapType = "none";
      lista.classList.add("is-arrastando");
      try { lista.setPointerCapture(id); } catch (err) {}
    });
    lista.addEventListener("pointermove", function (e) {
      if (x0 === null) return;
      var dx = e.clientX - x0;
      if (Math.abs(dx) > 3) moveu = true;
      lista.scrollLeft = s0 - dx;
    });
    function solta(e) {
      if (x0 === null) return;
      var dx = e.clientX - x0, p = posicoes(), i = 0, melhor = Infinity;
      x0 = null;
      for (var j = 0; j < p.length; j++) {           // item em que o arraste começou
        if (Math.abs(p[j] - s0) < melhor) { melhor = Math.abs(p[j] - s0); i = j; }
      }
      if (Math.abs(dx) > 40) i += dx < 0 ? 1 : -1;
      i = Math.max(0, Math.min(p.length - 1, i));
      lista.classList.remove("is-arrastando");
      try { lista.releasePointerCapture(id); } catch (err) {}
      lista.scrollTo({ left: p[i], behavior: "smooth" });
      setTimeout(function () { lista.style.scrollSnapType = ""; }, 450);
    }
    lista.addEventListener("pointerup", solta);
    lista.addEventListener("pointercancel", solta);
    lista.addEventListener("dragstart", function (e) { e.preventDefault(); });
    lista.addEventListener("click", function (e) {
      if (moveu) { e.preventDefault(); e.stopPropagation(); moveu = false; }
    }, true);
  })(faixas[k][0], faixas[k][1]);

  /* carrossel de publicidade (73/js/ad-carousel.js): com mouse, arrastar mais de 40px anda um slide
     (so o snap do navegador exigiria passar da metade da largura); com o dedo segue a rolagem nativa */
  Array.prototype.forEach.call(document.querySelectorAll(".page .rv76-car-trilho"), function (t) {
    var x0 = null, i0 = 0;
    t.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      x0 = e.clientX; i0 = Math.round(t.scrollLeft / (t.clientWidth || 1));
    });
    t.addEventListener("pointerup", function (e) {
      if (x0 === null) return;
      var dx = e.clientX - x0; x0 = null;
      if (Math.abs(dx) < 40) return;
      var i = Math.max(0, Math.min(t.children.length - 1, i0 + (dx < 0 ? 1 : -1)));
      t.scrollTo({ left: i * t.clientWidth, behavior: "smooth" });
    });
    t.addEventListener("pointercancel", function () { x0 = null; });
  });

  /* publicidade (ANUNCIOS no webflow76.py): conjuntos de banners mostram um sorteado por visita;
     story em video e mudo, em loop, e so toca enquanto aparece (com "reduzir movimento": parado, com controles) */
  var pubs = document.querySelectorAll(".page [data-rv76-random]");
  for (var pi = 0; pi < pubs.length; pi++) {
    try {
      var sorteio = JSON.parse(pubs[pi].getAttribute("data-rv76-random"));
      var it = sorteio[Math.floor(Math.random() * sorteio.length)], im = pubs[pi].querySelector("img");
      if (im && it) { im.src = it[0]; im.alt = it[1]; im.width = it[2]; im.height = it[3]; }
    } catch (err) {}
  }
  var reduzPub = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  Array.prototype.forEach.call(document.querySelectorAll(".page .rv76-pub video"), function (v) {
    v.muted = true;
    if (reduzPub || !("IntersectionObserver" in window)) { v.controls = true; return; }
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); } else { v.pause(); }
      });
    }, { threshold: 0.4 }).observe(v);
  });

  /* capa: o hero (video criado pelo script do Webflow a partir do data-src) comeca mudo; o botao de som
     (o da #75) liga e desliga o audio sem abrir a materia. O video pausa fora da tela, para o som nao seguir
     quem rolou para os cards. O botao fica ao lado do link (nao dentro dele), num invólucro do hero. */
  var heroSom = document.querySelector(".rv-cp-hero[data-som]");
  if (heroSom) {
    var hv = heroSom.querySelector("video");
    if (hv) {
      var wrap = document.createElement("div");
      wrap.className = "rv76-hero";
      heroSom.parentNode.insertBefore(wrap, heroSom);
      wrap.appendChild(heroSom);
      var bt = document.createElement("button");
      bt.type = "button"; bt.className = "rv76-som";
      bt.setAttribute("aria-label", "Ativar o som do vídeo"); bt.setAttribute("aria-pressed", "false");
      bt.innerHTML = '<img class="rv76-som-bg" src="../75/assets/mkt/ellipse6.svg?v=75-2" alt=""><img class="rv76-som-ico" src="../75/assets/mkt/sound.png?v=75-2" alt="">';
      wrap.appendChild(bt);
      hv.muted = true;
      bt.addEventListener("click", function (e) {
        e.preventDefault(); e.stopPropagation();
        var on = bt.getAttribute("aria-pressed") !== "true";
        hv.muted = !on;
        if (on && hv.paused) { var pp = hv.play(); if (pp && pp.catch) pp.catch(function () {}); }
        bt.setAttribute("aria-pressed", String(on));
        bt.setAttribute("aria-label", on ? "Desativar o som do vídeo" : "Ativar o som do vídeo");
      });
      if ("IntersectionObserver" in window && !reduzPub) {
        new IntersectionObserver(function (es) {
          es.forEach(function (e) {
            if (e.isIntersecting) { var pr = hv.play(); if (pr && pr.catch) pr.catch(function () {}); } else { hv.pause(); }
          });
        }, { threshold: 0.25 }).observe(heroSom);
      }
    }
  }

  /* capa: cards com data-video (CARDS_VIDEO no webflow76.py) trocam a imagem por video mudo em loop, que
     so toca enquanto o card aparece; com "reduzir movimento" fica so a imagem */
  Array.prototype.forEach.call(document.querySelectorAll(".rv-cp-card[data-video]"), function (c) {
    if (reduzPub) return;
    var cv = document.createElement("video");
    cv.className = "rv-cp-video";
    cv.src = c.getAttribute("data-video");
    cv.muted = true; cv.loop = true; cv.playsInline = true; cv.preload = "metadata";
    cv.setAttribute("muted", ""); cv.setAttribute("playsinline", ""); cv.setAttribute("aria-hidden", "true");
    c.insertBefore(cv, c.querySelector(".rv-cp-pelicula"));
    if (!("IntersectionObserver" in window)) { var p0 = cv.play(); if (p0 && p0.catch) p0.catch(function () {}); return; }
    new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { var pr = cv.play(); if (pr && pr.catch) pr.catch(function () {}); } else { cv.pause(); }
      });
    }, { threshold: 0.25 }).observe(c);
  });

  /* compartilhar: como no rodape do Webflow (compartilhamento do aparelho; sem ele,
     copia o link e o botao fica meio apagado por 1,2s) */
  var share = document.querySelector(".foot-share");
  if (share) {
    share.addEventListener("click", function (e) {
      e.preventDefault();
      var d = { title: document.title, url: location.href };
      if (navigator.share) {
        navigator.share(d).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(d.url).then(function () {
          share.setAttribute("aria-label", "Link copiado");
          share.style.opacity = ".5";
          setTimeout(function () { share.style.opacity = ""; share.setAttribute("aria-label", "Compartilhar"); }, 1200);
        });
      }
    });
  }
})();
