/* Revista Assaí — casca do desktop (css/shell-desktop.css), comum às edições.
   Monta o QR "Ler no celular" com o endereço da página aberta. O gerador
   (js/vendor/qrcode-generator.min.js) só é baixado quando a lateral direita
   aparece (>= 1200px). Sem JS, o bloco do QR fica escondido. */
(function () {
  "use strict";

  var bloco = document.querySelector(".casca-qr");
  var alvo = bloco && bloco.querySelector(".casca-qr-img");
  if (!alvo || !window.matchMedia) return;

  // o gerador fica ao lado deste arquivo, em qualquer profundidade de pasta
  var eu = document.currentScript;
  var pasta = eu ? eu.src.replace(/shell-desktop\.js(\?.*)?$/, "") : "js/";
  var largo = window.matchMedia("(min-width: 1200px)");
  var feito = false;

  function desenhar() {
    var qr = window.qrcode(0, "M");            // versão automática, correção M
    qr.addData(location.href.split("#")[0]);
    qr.make();
    // margem de 2 módulos: a zona clara que o leitor precisa em volta
    alvo.innerHTML = qr.createSvgTag({ cellSize: 4, margin: 8, scalable: true });
    bloco.classList.add("is-pronto");
  }

  function montar() {
    if (feito || !largo.matches) return;
    feito = true;
    if (window.qrcode) return desenhar();
    var s = document.createElement("script");
    s.src = pasta + "vendor/qrcode-generator.min.js";
    s.onload = desenhar;
    document.head.appendChild(s);
  }

  montar();
  if (largo.addEventListener) largo.addEventListener("change", montar);
  else largo.addListener(montar);
})();
