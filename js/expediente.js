/* Revista Assaí #74 — pagina EXPEDIENTE */
(function () {
  "use strict";

  /* ---------- redes sociais: icones caem como moedas ao entrar na tela (como na #73) ---------- */
  var soc = document.querySelector("[data-coin-fall]");
  if (soc && "IntersectionObserver" in window) {
    soc.classList.add("is-armed");
    var io = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      soc.classList.add("is-in");
      io.disconnect();
    }, { threshold: 0.3 });
    io.observe(soc);
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
