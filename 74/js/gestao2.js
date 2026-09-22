/* Revista Assaí #74 — pagina GESTÃO 02 */
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

  /* ---------- voltar ao topo ---------- */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
