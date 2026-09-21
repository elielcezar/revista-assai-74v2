/* Revista Assaí #74 — pagina GESTÃO 01 */
(function () {
  "use strict";

  // posicao horizontal do ponteiro nas coordenadas da coluna: no mobile o
  // js/shell.js aplica zoom no .page, e o arrasto tem que acompanhar o dedo
  function px(e) {
    var page = document.querySelector(".page");
    return e.clientX / ((page && parseFloat(page.style.zoom)) || 1);
  }

  /* ---------- carrossel (6 cards de 275px, gap 22) ---------- */
  var root = document.querySelector("[data-carousel]");
  if (root) {
    var track = root.querySelector("[data-track]");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-slide]"));
    var prev = root.querySelector("[data-prev]");
    var next = root.querySelector("[data-next]");
    var VIEW = 402;
    var index = 0;

    function maxOffset() {
      return Math.max(0, track.scrollWidth - VIEW);
    }

    // anda de card em card e para nas pontas (sem dar a volta)
    function offsetOf(i) {
      return Math.min(slides[i].offsetLeft, maxOffset());
    }

    function go(i) {
      index = Math.max(0, Math.min(i, slides.length - 1));
      track.style.transform = "translateX(" + -offsetOf(index) + "px)";
    }

    if (prev) prev.addEventListener("click", function () { go(index - 1); });
    if (next) next.addEventListener("click", function () { go(index + 1); });

    go(0);

    /* ---------- arrastar (mouse e dedo) ---------- */
    // a trilha anda com transform: a transicao sai durante o arrasto e,
    // ao soltar, encaixa no card mais proximo
    var view = root.querySelector(".carousel-viewport");
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
      var off = Math.max(0, Math.min(maxOffset(), base - dx));
      track.style.transform = "translateX(" + -off + "px)";
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

  /* ---------- botao de som ---------- */
  var sound = document.querySelector(".casal-sound");
  if (sound) {
    sound.addEventListener("click", function () {
      var on = sound.getAttribute("aria-pressed") === "true";
      sound.setAttribute("aria-pressed", String(!on));
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
