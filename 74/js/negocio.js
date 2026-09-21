/* Revista Assaí #74 — pagina NOVO NEGÓCIO */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 323;

  /* ---------- banner de video: autoplay mudo (politica dos navegadores) ---------- */
  var advid = document.querySelector(".adbox video");
  if (advid) {
    advid.muted = true;
    var play = advid.play();
    if (play && play.catch) play.catch(function () {});
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
