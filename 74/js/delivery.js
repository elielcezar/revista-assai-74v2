/* Revista Assaí #74 — pagina DELIVERY */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 240;

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
