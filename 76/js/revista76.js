/* Revista Assaí #76 — invólucro das páginas vindas do Webflow (comportamento igual ao da #75) */
(function () {
  "use strict";

  /* HEAD e RODAPÉ sao desenhos de 402px: em telas menores, reduzidos na proporcao.
     zoom (e nao transform) para que a caixa ocupe no fluxo a altura reduzida. */
  var FRAME_W = 402;
  var fixos = document.querySelectorAll(".page > .head, .page > .foot");
  function ajusta() {
    var w = document.documentElement.clientWidth || window.innerWidth;
    var z = w < FRAME_W ? String(w / FRAME_W) : "";
    for (var i = 0; i < fixos.length; i++) fixos[i].style.zoom = z;
  }
  ajusta();
  window.addEventListener("resize", ajusta);
  window.addEventListener("orientationchange", ajusta);

  /* menu do celular: a faixa abre rolada até o item ativo (posição de cada página no data-rolagem) */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = parseInt(nav.getAttribute("data-rolagem"), 10) || 0;

  /* voltar ao topo */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  /* compartilhar: como no rodape do Webflow (compartilhamento do aparelho; sem ele,
     copia o link e o botao fica meio apagado por 1,2s) */
  var share = document.querySelector(".foot-share");
  if (share) {
    share.addEventListener("click", function (e) {
      e.preventDefault();
      var d = { title: document.title, url: location.href };
      if (navigator.share) {
        navigator.share(d).catch(function () {});
      } else if (navigator.clipboard) {
        navigator.clipboard.writeText(d.url).then(function () {
          share.setAttribute("aria-label", "Link copiado");
          share.style.opacity = ".5";
          setTimeout(function () { share.style.opacity = ""; share.setAttribute("aria-label", "Compartilhar"); }, 1200);
        });
      }
    });
  }
})();
