/* Revista Assaí #74 — pagina GESTÃO 02 */
(function () {
  "use strict";

  /* ---------- carrossel (7 cards de 275px, gap 22) ---------- */
  var root = document.querySelector("[data-carousel]");
  if (root) {
    var track = root.querySelector("[data-track]");
    var slides = Array.prototype.slice.call(root.querySelectorAll("[data-slide]"));
    var prev = root.querySelector("[data-prev]");
    var next = root.querySelector("[data-next]");
    var VIEW = 382;
    var index = 0;

    function maxOffset() {
      return Math.max(0, track.scrollWidth - VIEW);
    }

    function go(i) {
      index = (i + slides.length) % slides.length;
      var off = Math.min(slides[index].offsetLeft, maxOffset());
      track.style.transform = "translateX(" + -off + "px)";
    }

    if (prev) prev.addEventListener("click", function () { go(index - 1); });
    if (next) next.addEventListener("click", function () { go(index + 1); });

    go(0);
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
