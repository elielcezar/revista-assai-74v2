/* Revista Assaí #74 — pagina NOVO NEGÓCIO */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 323;

  /* ---------- banner rotativo de video: sorteia um anuncio por carregamento ----------
     cada item: {src, alt}. O HTML traz o primeiro com preload="none" e sem
     autoplay; aqui troca o src se for outro e da o play mudo (politica dos navegadores) */
  var advid = document.querySelector(".adbox video");
  if (advid) {
    var adbox = advid.parentNode;
    var lista = [];
    try { lista = JSON.parse(adbox.getAttribute("data-ad-random")) || []; } catch (e) { lista = []; }
    var item = lista[Math.floor(Math.random() * lista.length)];
    if (item && item.src !== advid.getAttribute("src")) {
      advid.src = item.src;
      advid.setAttribute("aria-label", item.alt || "");
    }
    advid.muted = true;
    advid.preload = "auto";
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
