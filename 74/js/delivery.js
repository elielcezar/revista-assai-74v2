/* Revista Assaí #74 — pagina DELIVERY */
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
  if (nav) nav.scrollLeft = 240;

  /* ---------- carrossel de banners: arrastar + bolinhas (igual a PRINCIPAL e GESTÃO) ---------- */
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

  /* ---------- banner rotativo: sorteia um anuncio por carregamento ---------- */
  var adbox = document.querySelector("[data-ad-random]");
  if (adbox) {
    var adimg = adbox.querySelector("img");
    var lista = [];
    try { lista = JSON.parse(adbox.getAttribute("data-ad-random")) || []; } catch (e) { lista = []; }
    if (adimg && lista.length > 1) {
      var escolhido = lista[Math.floor(Math.random() * lista.length)];
      if (escolhido && escolhido.src !== adimg.getAttribute("src")) {
        adimg.src = escolhido.src;
        adimg.alt = escolhido.alt || "";
      }
    }
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
