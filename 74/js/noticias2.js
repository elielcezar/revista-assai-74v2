/* Revista Assaí #74 — pagina NOTICIAS 02 */
(function () {
  "use strict";

  /* ---------- menu: no Figma a faixa aparece rolada ate o item ativo ---------- */
  var nav = document.querySelector(".head-nav");
  if (nav) nav.scrollLeft = 592;

  /* ---------- banners rotativos: sorteia um anuncio (imagem ou video) por carregamento ----------
     cada item: {src, alt, w, h} e, se for video, "video": true. O HTML ja traz o
     primeiro como <img>; se o sorteado for video, a <img> vira um <video> mudo em loop */
  Array.prototype.forEach.call(document.querySelectorAll("[data-ad-random]"), function (box) {
    var lista = [];
    try { lista = JSON.parse(box.getAttribute("data-ad-random")) || []; } catch (e) { lista = []; }
    var atual = box.querySelector("img, video");
    if (!atual || lista.length < 2) return;
    var item = lista[Math.floor(Math.random() * lista.length)];
    if (!item || item.src === atual.getAttribute("src")) return;
    var novo = document.createElement(item.video ? "video" : "img");
    if (item.video) {
      novo.muted = novo.loop = novo.autoplay = novo.playsInline = true;
      novo.setAttribute("muted", ""); novo.setAttribute("playsinline", "");
      novo.setAttribute("aria-label", item.alt || "");
    } else {
      novo.alt = item.alt || "";
    }
    if (item.w) novo.width = item.w;
    if (item.h) novo.height = item.h;
    novo.src = item.src;
    box.replaceChild(novo, atual);
  });

  /* ---------- voltar ao topo ---------- */
  var toTop = document.querySelector(".foot-top");
  if (toTop) {
    toTop.addEventListener("click", function (e) {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
})();
