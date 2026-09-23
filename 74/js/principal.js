/* Revista Assaí #74 — pagina PRINCIPAL */
(function () {
  "use strict";

  // posicao horizontal do ponteiro nas coordenadas da coluna: no mobile o
  // js/shell.js reduz o .page (transform: scale), e o arrasto tem que acompanhar
  // o dedo — a escala vem do proprio shell
  function px(e) {
    var esc = (window.ShellFit && window.ShellFit.escala()) || 1;
    return e.clientX / esc;
  }

  /* o carrossel da matéria (.carousel) não tem mais setas nem arrasto: ele
     corre para o lado com o scroll, pelo pin-horizontal do js/scroll-fx.js */

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

  /* ---------- video: autoplay mudo, o botao liga e desliga o som ---------- */
  var sound = document.querySelector(".video-sound");
  var video = document.querySelector(".video-play video");
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
