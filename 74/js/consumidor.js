/* Revista Assaí #74 — pagina CONSUMIDOR */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 157;

  /* ---------- banners rotativos: cada um sorteia um anuncio por carregamento ---------- */
  Array.prototype.forEach.call(document.querySelectorAll("[data-ad-random]"), function (adbox) {
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
  });

  /* ---------- voltar ao topo ---------- */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
