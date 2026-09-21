/* Revista Assaí #74 — invólucro comum (sidebar desktop) */
(function () {
  "use strict";

  /* ---------- sidebar: em janelas baixas, rola a lista ate o item ativo ---------- */
  // ancora dois itens acima do ativo, como na #73, para dar contexto
  function centerActive() {
    var nav = document.querySelector(".dt-nav");
    if (!nav || nav.offsetParent === null) return;
    var items = nav.querySelectorAll("a");
    var active = nav.querySelector("a.is-active");
    if (!active) return;
    var i = Array.prototype.indexOf.call(items, active);
    var anchor = items[Math.max(0, i - 2)];
    var max = nav.scrollHeight - nav.clientHeight;
    if (max <= 0) return;
    var target = anchor.offsetTop - nav.offsetTop + anchor.offsetHeight / 2 - nav.clientHeight / 2;
    nav.scrollTop = Math.max(0, Math.min(target, max));
  }

  centerActive();
  window.addEventListener("load", centerActive);
  window.addEventListener("resize", centerActive);
})();
