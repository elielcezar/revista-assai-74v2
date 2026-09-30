/* Revista Assaí #74 — invólucro comum: coluna de 402px no mobile.
   A casca do desktop é comum às edições: js/shell-desktop.js */
(function () {
  "use strict";

  /* ---------- mobile: a coluna de 402px cabe na largura da tela ---------- */
  // Usa transform: scale, e NAO zoom. O zoom refaz o layout na escala reduzida,
  // e cada linha de texto arredonda para o pixel do aparelho: as secoes encolhem
  // alguns decimos cada, isso acumula pagina abaixo (ate 46px na MKT em 390px) e
  // o texto sai do lugar das decoracoes, que sao absolutas e nao encolhem. Com
  // transform o layout e calculado nos 402px do Figma e so depois reduzido, entao
  // tudo escala junto. Em troca, a caixa no fluxo continua com a altura de 402px:
  // a altura reduzida e dada ao body, senao a pagina rolaria muito alem do
  // rodape. Acima de 402px nada disso se aplica.
  var FRAME_W = 402;
  var page = document.querySelector(".page");
  var escala = 1;

  // o body fica com a altura que a pagina realmente ocupa depois de reduzida
  // (margem negativa no .page nao encolhe o scrollHeight do documento)
  function medirAltura() {
    if (!page || escala === 1) return;
    document.body.style.height = Math.round(page.offsetHeight * escala) + "px";
  }

  function fitPage() {
    if (!page) return;
    var vw = document.documentElement.clientWidth || window.innerWidth;
    escala = vw < FRAME_W ? vw / FRAME_W : 1;
    if (escala === 1) {
      page.style.width = page.style.transform = page.style.transformOrigin = "";
      document.body.style.height = "";
    } else {
      page.style.width = FRAME_W + "px";
      page.style.transformOrigin = "top left";
      page.style.transform = "scale(" + escala + ")";
      medirAltura();
    }
    document.documentElement.style.setProperty("--shell-escala", escala);
  }

  // quem precisa converter px de tela em px de CSS (scroll-fx, arrasto dos
  // carrosseis) le a escala daqui, em vez de ler o style do .page
  window.ShellFit = { escala: function () { return escala; } };

  fitPage();
  window.addEventListener("resize", fitPage);
  window.addEventListener("orientationchange", fitPage);
  // o conteudo muda de altura (imagens, acordeao, congelamentos): remede a sobra
  if (window.ResizeObserver && page) new ResizeObserver(medirAltura).observe(page);
  window.addEventListener("load", medirAltura);
})();
