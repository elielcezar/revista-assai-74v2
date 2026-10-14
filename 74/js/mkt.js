/* Revista Assaí #74 — pagina MKT DIGITAL */
(function () {
  "use strict";

  // posicao horizontal do ponteiro nas coordenadas da coluna: no mobile o
  // js/shell.js reduz o .page (transform: scale), e o arrasto tem que acompanhar
  // o dedo — a escala vem do proprio shell
  function px(e) {
    var esc = (window.ShellFit && window.ShellFit.escala()) || 1;
    return e.clientX / esc;
  }

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 19;

  /* ---------- galeria: setas e arrasto, alem do pin-horizontal ---------- */
  // e uma imagem unica: o dedo usa o scroll nativo do container, aqui tratamos
  // so as setas e o arrasto com mouse. O pin-horizontal (js/scroll-fx.js) tambem
  // mexe no scrollLeft com o scroll da pagina, e absorve o que for feito aqui.
  var gal = document.querySelector("[data-gallery]");
  if (gal) {
    var gprev = document.querySelector("[data-gprev]");
    var gnext = document.querySelector("[data-gnext]");
    var STEP = 240;

    // setas invertidas de proposito: a seta "puxa" a imagem para o seu lado,
    // entao a da esquerda avança na imagem e a da direita volta
    if (gprev) gprev.addEventListener("click", function () { gal.scrollBy({ left: STEP, behavior: "smooth" }); });
    if (gnext) gnext.addEventListener("click", function () { gal.scrollBy({ left: -STEP, behavior: "smooth" }); });

    var gx = 0, g0 = 0, gid = null;

    gal.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      gid = e.pointerId;
      gx = px(e);
      g0 = gal.scrollLeft;
      gal.classList.add("is-dragging");
      try { gal.setPointerCapture(gid); } catch (err) {}
      e.preventDefault();
    });

    gal.addEventListener("pointermove", function (e) {
      if (e.pointerId !== gid) return;
      gal.scrollLeft = g0 - (px(e) - gx);
    });

    function gdrop(e) {
      if (e.pointerId !== gid) return;
      try { gal.releasePointerCapture(gid); } catch (err) {}
      gid = null;
      gal.classList.remove("is-dragging");
    }
    gal.addEventListener("pointerup", gdrop);
    gal.addEventListener("pointercancel", gdrop);
    gal.addEventListener("dragstart", function (e) { e.preventDefault(); });
  }

  /* ---------- banner rotativo: sorteia um anuncio (imagem ou video) por carregamento ----------
     cada item: {src, alt, w, h} e, se for video, "video": true. O HTML ja traz a
     primeira imagem; se o sorteado for video, a img vira um video mudo em loop.
     O video e mais alto que as artes (402x715 contra 402x384): a diferenca vai
     para --ad-extra, que desce as decoracoes absolutas abaixo do banner */
  var adbox = document.querySelector("[data-ad-random]");
  if (adbox) {
    var atual = adbox.querySelector("img, video");
    var lista = [];
    try { lista = JSON.parse(adbox.getAttribute("data-ad-random")) || []; } catch (e) { lista = []; }
    if (atual && lista.length > 1) {
      var escolhido = lista[Math.floor(Math.random() * lista.length)];
      if (escolhido && escolhido.src !== atual.getAttribute("src")) {
        var novo = document.createElement(escolhido.video ? "video" : "img");
        if (escolhido.video) {
          novo.muted = novo.loop = novo.autoplay = novo.playsInline = true;
          novo.setAttribute("muted", "");
          novo.setAttribute("playsinline", "");
          novo.setAttribute("aria-label", escolhido.alt || "");
          novo.preload = "metadata";
        } else {
          novo.alt = escolhido.alt || "";
        }
        if (escolhido.w) novo.width = escolhido.w;
        if (escolhido.h) novo.height = escolhido.h;
        novo.src = escolhido.src;
        adbox.replaceChild(novo, atual);
        if (escolhido.video && escolhido.w && escolhido.h) {
          var art = document.querySelector(".art");
          if (art) art.style.setProperty("--ad-extra", "calc(402px * " + escolhido.h + " / " + escolhido.w + " - 402px * 2016 / 2112)");
          var play = novo.play();
          if (play && play.catch) play.catch(function () {});
        }
      }
    }
  }

  /* ---------- voltar ao topo ---------- */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
