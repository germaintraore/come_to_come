/**
 * Come To Code – 2S Informatique Plus
 * JavaScript principal
 */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-dismiss alerts après 5 secondes ──
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      bsAlert.close();
    }, 5000);
  });

  // ── Animation d'entrée des éléments ──
  const fadeEls = document.querySelectorAll('.ctc-card, .step-card, .dash-card, .welcome-banner');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    fadeEls.forEach(el => {
      el.style.opacity = '0';
      el.style.transform = 'translateY(20px)';
      el.style.transition = 'opacity .45s ease, transform .45s ease';
      observer.observe(el);
    });
  }

  // ── Animation du code panel (typing effect) ──
  const codeLines = document.querySelectorAll('.code-panel-body .code-line');
  codeLines.forEach((line, i) => {
    line.style.opacity = '0';
    setTimeout(() => {
      line.style.opacity = '1';
      line.style.transition = 'opacity .2s';
    }, 80 * i + 400);
  });

  // ── Navbar scroll effect ──
  const navbar = document.querySelector('.ctc-navbar');
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 50) {
        navbar.style.background = 'rgba(10,14,26,.98)';
      } else {
        navbar.style.background = 'rgba(10,14,26,.95)';
      }
    });
  }

});
