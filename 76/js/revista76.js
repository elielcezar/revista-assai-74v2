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

  /* carrosseis de rolagem lateral do Webflow: ideias do DELIVERY ([data-carrossel]) e
     beneficios do Assai Pay na NOTICIAS ([data-faixa], que ja tem setas e pontos).
     No celular sao rolagem nativa (dedo), que o mouse nao arrasta. Com mouse: arrastar
     anda um item por vez e para nas pontas, como os carrosseis da #74/#75. O dedo
     continua com a rolagem nativa; indicadores, setas e pontos acompanham a rolagem. */
  var faixas = [];
  var q1 = document.querySelectorAll(".page [data-carrossel]");
  for (var k = 0; k < q1.length; k++) faixas.push([q1[k], q1[k].children]);
  var q2 = document.querySelectorAll(".page [data-faixa]");
  for (k = 0; k < q2.length; k++) {
    var jan = q2[k].querySelector(".rv-nt-janela");
    if (jan) faixas.push([jan, q2[k].querySelectorAll(".rv-nt-painel")]);
  }
  for (k = 0; k < faixas.length; k++) (function (lista, itens) {
    var x0 = null, s0 = 0, moveu = false, id = 0;
    function posicoes() {
      var p = [];
      for (var i = 0; i < itens.length; i++) p.push(itens[i].offsetLeft - itens[0].offsetLeft);
      return p;
    }
    lista.classList.add("rv-arrastavel");
    lista.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      x0 = e.clientX; s0 = lista.scrollLeft; moveu = false; id = e.pointerId;
      lista.style.scrollSnapType = "none";
      lista.classList.add("is-arrastando");
      try { lista.setPointerCapture(id); } catch (err) {}
    });
    lista.addEventListener("pointermove", function (e) {
      if (x0 === null) return;
      var dx = e.clientX - x0;
      if (Math.abs(dx) > 3) moveu = true;
      lista.scrollLeft = s0 - dx;
    });
    function solta(e) {
      if (x0 === null) return;
      var dx = e.clientX - x0, p = posicoes(), i = 0, melhor = Infinity;
      x0 = null;
      for (var j = 0; j < p.length; j++) {           // item em que o arraste começou
        if (Math.abs(p[j] - s0) < melhor) { melhor = Math.abs(p[j] - s0); i = j; }
      }
      if (Math.abs(dx) > 40) i += dx < 0 ? 1 : -1;
      i = Math.max(0, Math.min(p.length - 1, i));
      lista.classList.remove("is-arrastando");
      try { lista.releasePointerCapture(id); } catch (err) {}
      lista.scrollTo({ left: p[i], behavior: "smooth" });
      setTimeout(function () { lista.style.scrollSnapType = ""; }, 450);
    }
    lista.addEventListener("pointerup", solta);
    lista.addEventListener("pointercancel", solta);
    lista.addEventListener("dragstart", function (e) { e.preventDefault(); });
    lista.addEventListener("click", function (e) {
      if (moveu) { e.preventDefault(); e.stopPropagation(); moveu = false; }
    }, true);
  })(faixas[k][0], faixas[k][1]);

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
