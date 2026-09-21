/* Revista Assaí #74 — pagina PRINCIPAL */
(function () {
  "use strict";

  // posicao horizontal do ponteiro nas coordenadas da coluna: no mobile o
  // js/shell.js aplica zoom no .page, e o arrasto tem que acompanhar o dedo
  function px(e) {
    var page = document.querySelector(".page");
    return e.clientX / ((page && parseFloat(page.style.zoom)) || 1);
  }

  /* ---------- carrossel ---------- */
  var root = document.querySelector("[data-carousel]");
  if (root) {
    var track = root.querySelector("[data-track]");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-slide]"));
    var prev = root.querySelector("[data-prev]");
    var next = root.querySelector("[data-next]");
    var VIEW = 382;
    var MAX = 2085 - VIEW;
    var index = 0;

    // desloca a trilha pelo centro de cada imagem, mantendo o slide 1 em 0
    // (estado inicial do Figma: trilha sem deslocamento)
    var first = slides[0].offsetLeft + slides[0].offsetWidth / 2;
    var offsets = slides.map(function (el) {
      var center = el.offsetLeft + el.offsetWidth / 2;
      return Math.max(0, Math.min(MAX, Math.round(center - first)));
    });

    function go(i) {
      index = (i + slides.length) % slides.length;
      track.style.transform = "translateX(" + -offsets[index] + "px)";
    }

    if (prev) prev.addEventListener("click", function () { go(index - 1); });
    if (next) next.addEventListener("click", function () { go(index + 1); });

    go(0);

    /* ---------- arrastar (mouse e dedo) ---------- */
    // a trilha anda com transform, entao a transicao sai durante o arrasto
    // e o slide mais proximo e "encaixado" ao soltar
    var view = root.querySelector(".carousel-viewport");
    var dx0 = 0, base = 0, pid = null, moved = false;

    function nearest(off) {
      var best = 0;
      for (var i = 1; i < offsets.length; i++) {
        if (Math.abs(offsets[i] - off) < Math.abs(offsets[best] - off)) best = i;
      }
      return best;
    }

    view.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      pid = e.pointerId;
      dx0 = px(e);
      base = offsets[index];
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
      var off = Math.max(0, Math.min(MAX, base - dx));
      track.style.transform = "translateX(" + -off + "px)";
    });

    function drop(e) {
      if (e.pointerId !== pid) return;
      try { view.releasePointerCapture(pid); } catch (err) {}
      pid = null;
      view.classList.remove("is-dragging");
      track.style.transition = "";
      if (moved) go(nearest(Math.max(0, Math.min(MAX, base - (px(e) - dx0)))));
    }
    view.addEventListener("pointerup", drop);
    view.addEventListener("pointercancel", drop);

    // arrastar em cima de uma imagem nao vira "arrastar imagem" no desktop
    view.addEventListener("dragstart", function (e) { e.preventDefault(); });
  }

  /* ---------- citacao: arrastar com o mouse ---------- */
  // no toque o proprio overflow-x ja rola; aqui so o mouse, que nao tem esse gesto
  var quote = document.querySelector(".quote-marquee");
  if (quote) {
    var qx = 0, q0 = 0, qid = null;

    quote.addEventListener("pointerdown", function (e) {
      if (e.pointerType !== "mouse" || e.button !== 0) return;
      qid = e.pointerId;
      qx = px(e);
      q0 = quote.scrollLeft;
      quote.classList.add("is-dragging");
      try { quote.setPointerCapture(qid); } catch (err) {}
      e.preventDefault(); // nao inicia selecao de texto
    });

    quote.addEventListener("pointermove", function (e) {
      if (e.pointerId !== qid) return;
      quote.scrollLeft = q0 - (px(e) - qx);
    });

    function endDrag(e) {
      if (e.pointerId !== qid) return;
      try { quote.releasePointerCapture(qid); } catch (err) {}
      qid = null;
      quote.classList.remove("is-dragging");
    }
    quote.addEventListener("pointerup", endDrag);
    quote.addEventListener("pointercancel", endDrag);
  }

  /* ---------- carrossel de banners: arrastar + bolinhas ---------- */
  var bcar = document.querySelector("[data-bcar]");
  if (bcar) {
    var bview = bcar.querySelector(".bcar-view");
    var btrack = bcar.querySelector("[data-btrack]");
    var bslides = Array.prototype.slice.call(bcar.querySelectorAll("[data-bslide]"));
    var bdots = Array.prototype.slice.call(bcar.querySelectorAll("[data-bdot]"));
    var bi = 0;

    function bwidth() { return bview.clientWidth; }

    function bgo(i) {
      bi = Math.max(0, Math.min(i, bslides.length - 1));
      btrack.style.transform = "translateX(" + -(bi * bwidth()) + "px)";
      bdots.forEach(function (d, k) {
        d.classList.toggle("is-active", k === bi);
        if (k === bi) d.setAttribute("aria-current", "true");
        else d.removeAttribute("aria-current");
      });
    }

    bdots.forEach(function (d, k) {
      d.addEventListener("click", function () { bgo(k); });
    });

    var bx = 0, bbase = 0, bpid = null, bmoved = false;

    bview.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      bpid = e.pointerId;
      bx = px(e);
      bbase = bi * bwidth();
      bmoved = false;
      btrack.style.transition = "none";
      bview.classList.add("is-dragging");
      try { bview.setPointerCapture(bpid); } catch (err) {}
      if (e.pointerType === "mouse") e.preventDefault();
    });

    bview.addEventListener("pointermove", function (e) {
      if (e.pointerId !== bpid) return;
      var dx = px(e) - bx;
      if (Math.abs(dx) > 4) bmoved = true;
      var max = (bslides.length - 1) * bwidth();
      btrack.style.transform = "translateX(" + -Math.max(0, Math.min(max, bbase - dx)) + "px)";
    });

    function bdrop(e) {
      if (e.pointerId !== bpid) return;
      try { bview.releasePointerCapture(bpid); } catch (err) {}
      bpid = null;
      bview.classList.remove("is-dragging");
      btrack.style.transition = "";
      // encaixa no banner mais proximo
      if (bmoved) bgo(Math.round((bbase - (px(e) - bx)) / bwidth()));
    }
    bview.addEventListener("pointerup", bdrop);
    bview.addEventListener("pointercancel", bdrop);
    bview.addEventListener("dragstart", function (e) { e.preventDefault(); });

    bgo(0);
  }

  /* ---------- botao de som ---------- */
  var sound = document.querySelector(".video-sound");
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
