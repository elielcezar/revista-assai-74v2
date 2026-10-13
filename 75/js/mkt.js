/* Revista Assaí #75 — pagina MKT DIGITAL */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 7;

  /* ---------- videos: autoplay mudo; cada botao liga e desliga o som do seu video ---------- */
  Array.prototype.forEach.call(document.querySelectorAll(".video"), function (fig) {
    var video = fig.querySelector("video");
    var sound = fig.querySelector(".video-sound");
    if (!video || !sound) return;
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
