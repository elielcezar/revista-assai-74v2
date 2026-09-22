/* Revista Assaí #74 — pagina GESTÃO 01 */
(function () {
  "use strict";

  // posicao horizontal do ponteiro nas coordenadas da coluna: no mobile o
  // js/shell.js aplica zoom no .page, e o arrasto tem que acompanhar o dedo
  function px(e) {
    var page = document.querySelector(".page");
    return e.clientX / ((page && parseFloat(page.style.zoom)) || 1);
  }

  /* o carrossel (.carousel) não tem mais setas nem arrasto: ele corre para o
     lado com o scroll, pelo pin-horizontal do js/scroll-fx.js */

  /* ---------- video: autoplay mudo, o botao liga e desliga o som ---------- */
  var sound = document.querySelector(".casal-sound");
  var video = document.querySelector(".casal-play video");
  if (sound && video) {
    // garante o mudo mesmo onde o atributo chega tarde (alguns Safari)
    video.muted = true;
    sound.addEventListener("click", function () {
      var on = sound.getAttribute("aria-pressed") !== "true";
      video.muted = !on;
      // se o autoplay foi bloqueado (modo economia de bateria), o clique da o play
      if (on && video.paused) video.play().catch(function () {});
      sound.setAttribute("aria-pressed", String(on));
      sound.setAttribute("aria-label", on ? "Desativar o som do vídeo" : "Ativar o som do vídeo");
    });
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
