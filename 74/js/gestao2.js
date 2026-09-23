/* Revista Assaí #74 — pagina GESTÃO 02 */
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

  /* ---------- voltar ao topo ---------- */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
