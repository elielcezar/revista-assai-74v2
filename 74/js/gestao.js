/* Revista Assaí #74 — pagina GESTÃO 01 */
(function () {
  "use strict";

  // posicao horizontal do ponteiro nas coordenadas da coluna: no mobile o
  // js/shell.js reduz o .page (transform: scale), e o arrasto tem que acompanhar
  // o dedo — a escala vem do proprio shell
  function px(e) {
    var esc = (window.ShellFit && window.ShellFit.escala()) || 1;
    return e.clientX / esc;
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
