/* Revista Assaí #74 — pagina MKT DIGITAL */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 19;

  /* ---------- galeria: rola com as setas e arrastando ---------- */
  // e uma imagem unica: o dedo usa o scroll nativo do container,
  // aqui tratamos so as setas e o arrasto com mouse
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
      gx = e.clientX;
      g0 = gal.scrollLeft;
      gal.classList.add("is-dragging");
      try { gal.setPointerCapture(gid); } catch (err) {}
      e.preventDefault();
    });

    gal.addEventListener("pointermove", function (e) {
      if (e.pointerId !== gid) return;
      gal.scrollLeft = g0 - (e.clientX - gx);
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

  /* ---------- banner rotativo: sorteia um anuncio por carregamento ---------- */
  var adbox = document.querySelector("[data-ad-random]");
  if (adbox) {
    var adimg = adbox.querySelector("img");
    var lista = [];
    try { lista = JSON.parse(adbox.getAttribute("data-ad-random")) || []; } catch (e) { lista = []; }
    if (adimg && lista.length > 1) {
      var escolhido = lista[Math.floor(Math.random() * lista.length)];
      if (escolhido && escolhido.src !== adimg.getAttribute("src")) {
        adimg.src = escolhido.src;
        adimg.alt = escolhido.alt || "";
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
