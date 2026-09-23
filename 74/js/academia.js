/* Revista Assaí #74 — pagina ACADEMIA */
(function () {
  "use strict";

  // posicao horizontal do ponteiro nas coordenadas da coluna: no mobile o
  // js/shell.js reduz o .page (transform: scale), e o arrasto tem que acompanhar
  // o dedo — a escala vem do proprio shell
  function px(e) {
    var esc = (window.ShellFit && window.ShellFit.escala()) || 1;
    return e.clientX / esc;
  }

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 430;

  /* ---------- galeria de premios: setas item por item + arrastar ---------- */
  var root = document.querySelector("[data-carousel]");
  if (root) {
    var view = root.querySelector(".gallery-view");
    var track = root.querySelector("[data-track]");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-slide]"));
    var prev = root.querySelector("[data-prev]");
    var next = root.querySelector("[data-next]");
    var index = 0;

    function maxOffset() {
      return Math.max(0, track.scrollWidth - view.clientWidth);
    }

    function offsetOf(i) {
      return Math.min(slides[i].offsetLeft, maxOffset());
    }

    // anda de card em card e para nas pontas (sem dar a volta)
    function go(i) {
      index = Math.max(0, Math.min(i, slides.length - 1));
      track.style.transform = "translateX(" + -offsetOf(index) + "px)";
    }

    // setas invertidas de proposito: a seta "puxa" os cards para o seu lado,
    // entao a da esquerda avança e a da direita volta
    if (prev) prev.addEventListener("click", function () { go(index + 1); });
    if (next) next.addEventListener("click", function () { go(index - 1); });

    go(0);

    var dx0 = 0, base = 0, pid = null, moved = false;

    function nearest(off) {
      var best = 0;
      for (var i = 1; i < slides.length; i++) {
        if (Math.abs(offsetOf(i) - off) < Math.abs(offsetOf(best) - off)) best = i;
      }
      return best;
    }

    view.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      pid = e.pointerId;
      dx0 = px(e);
      base = offsetOf(index);
      moved = false;
      track.style.transition = "none";
      view.classList.add("is-dragging");
      try { view.setPointerCapture(pid); } catch (err) {}
      if (e.pointerType === "mouse") e.preventDefault();
    });

    view.addEventListener("pointermove", function (e) {
      if (e.pointerId !== pid) return;
      var dx = px(e) - dx0;
      if (Math.abs(dx) > 4) moved = true;
      track.style.transform = "translateX(" + -Math.max(0, Math.min(maxOffset(), base - dx)) + "px)";
    });

    function drop(e) {
      if (e.pointerId !== pid) return;
      try { view.releasePointerCapture(pid); } catch (err) {}
      pid = null;
      view.classList.remove("is-dragging");
      track.style.transition = "";
      if (moved) go(nearest(Math.max(0, Math.min(maxOffset(), base - (px(e) - dx0)))));
    }
    view.addEventListener("pointerup", drop);
    view.addEventListener("pointercancel", drop);
    view.addEventListener("dragstart", function (e) { e.preventDefault(); });
  }

  /* ---------- banner de video: autoplay mudo (politica dos navegadores) ---------- */
  var advid = document.querySelector(".adbox video");
  if (advid) {
    advid.muted = true;
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
