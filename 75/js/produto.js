/* Revista Assaí #75 — pagina PRODUTO */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 79;

  /* ---------- video: autoplay mudo, o botao liga e desliga o som ---------- */
  var sound = document.querySelector(".video-sound");
  var video = document.querySelector(".video video");
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
