/**
 * Carrossel de anúncios genérico.
 *
 * Uso: adicione data-ad-carousel no elemento raiz do carrossel.
 * Ele procura automaticamente:
 *   - [data-ad-track]   → faixa de slides
 *   - [data-ad-slide]   → cada slide (ou filhos diretos do track)
 *   - [data-ad-dot]     → botões de navegação
 *
 * Pode haver múltiplos carrosseis na mesma página.
 */
(function () {
  var carousels = document.querySelectorAll('[data-ad-carousel]');
  if (!carousels.length) return;

  for (var c = 0; c < carousels.length; c++) {
    initCarousel(carousels[c]);
  }

  function initCarousel(carousel) {
    var track = carousel.querySelector('[data-ad-track]');
    if (!track) return;

    var dots = carousel.querySelectorAll('[data-ad-dot]');
    var slides = track.querySelectorAll('[data-ad-slide]');
    if (!slides.length) slides = track.children;
    var slideCount = slides.length;
    if (!slideCount) return;

    var current = 0;
    var paused = false;
    var autoTimer = null;
    var active = false;
    var capId = null;
    var startX = 0;
    var scroll0 = 0;

    function slideWidth() {
      return track.clientWidth || 402;
    }

    function setDot(index) {
      current = index;
      for (var i = 0; i < dots.length; i++) {
        var on = i === index;
        dots[i].classList.toggle('is-active', on);
        if (on) dots[i].setAttribute('aria-current', 'true');
        else dots[i].removeAttribute('aria-current');
      }
    }

    function goTo(index, smooth) {
      var i = (index + slideCount) % slideCount;
      track.scrollTo({ left: i * slideWidth(), behavior: smooth ? 'smooth' : 'auto' });
      setDot(i);
    }

    function syncFromScroll() {
      var w = slideWidth();
      if (!w) return;
      var i = Math.round(track.scrollLeft / w);
      if (i < 0) i = 0;
      if (i > slideCount - 1) i = slideCount - 1;
      setDot(i);
    }

    function startAuto() {
      stopAuto();
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      autoTimer = window.setInterval(function () {
        if (paused || active) return;
        goTo(current + 1, true);
      }, 4500);
    }

    function stopAuto() {
      if (autoTimer) {
        window.clearInterval(autoTimer);
        autoTimer = null;
      }
    }

    track.addEventListener('scroll', function () {
      syncFromScroll();
    }, { passive: true });

    track.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse') return;
      if (e.button !== 0) return;
      active = true;
      paused = true;
      capId = e.pointerId;
      startX = e.clientX;
      scroll0 = track.scrollLeft;
      track.classList.add('is-dragging');
      try { track.setPointerCapture(e.pointerId); } catch (err) {}
    });

    track.addEventListener('pointermove', function (e) {
      if (!active || e.pointerId !== capId) return;
      track.scrollLeft = scroll0 - (e.clientX - startX);
    });

    function endPointer(e) {
      if (!active || (e && e.pointerId !== capId)) return;
      active = false;
      capId = null;
      track.classList.remove('is-dragging');
      try { if (e) track.releasePointerCapture(e.pointerId); } catch (err) {}
      window.setTimeout(function () { paused = false; }, 4000);
    }

    track.addEventListener('pointerup', endPointer);
    track.addEventListener('pointercancel', endPointer);

    for (var d = 0; d < dots.length; d++) {
      dots[d].addEventListener('click', function () {
        var i = parseInt(this.getAttribute('data-ad-dot'), 10);
        paused = true;
        goTo(i, true);
        window.setTimeout(function () { paused = false; }, 4000);
      });
    }

    if (window.IntersectionObserver) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) startAuto();
          else stopAuto();
        });
      }, { threshold: 0.4 });
      io.observe(carousel);
    } else {
      startAuto();
    }

    setDot(0);
  }
})();
