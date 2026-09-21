/* Revista Assaí #74 — pagina NOVO NEGÓCIO */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 323;

  /* ---------- voltar ao topo ---------- */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
