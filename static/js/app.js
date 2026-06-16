// COFINANCE CI — App utils v2
document.addEventListener('DOMContentLoaded', () => {

  // Sidebar toggle
  const sidebar = document.querySelector('.sidebar');
  const toggle = document.querySelector('.sidebar-toggle');
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
  }

  // Mobile sidebar
  const burger = document.querySelector('[data-burger]');
  if (burger && sidebar) {
    burger.addEventListener('click', () => sidebar.classList.toggle('open'));
  }

  // Modales
  document.querySelectorAll('[data-modal-open]').forEach(btn => {
    btn.addEventListener('click', () => {
      const m = document.getElementById(btn.dataset.modalOpen);
      if (m) m.classList.add('open');
    });
  });
  document.querySelectorAll('[data-modal-close]').forEach(btn => {
    btn.addEventListener('click', () => btn.closest('.modal-backdrop').classList.remove('open'));
  });
  document.querySelectorAll('.modal-backdrop').forEach(b => {
    b.addEventListener('click', (e) => { if (e.target === b) b.classList.remove('open'); });
  });

  // Auto-dismiss alerts
  document.querySelectorAll('.alert[data-auto]').forEach(a => {
    setTimeout(() => {
      a.style.opacity = '0';
      setTimeout(() => a.remove(), 300);
    }, 5000);
  });

  // Smooth scroll pour les ancres internes
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      if (id === '#') return;
      const el = document.querySelector(id);
      if (el) { e.preventDefault(); el.scrollIntoView({ behavior: 'smooth' }); }
    });
  });

  // Compteur animé pour les valeurs stats
  document.querySelectorAll('.stat-card .value').forEach(el => {
    const text = el.textContent.trim();
    const num = parseFloat(text.replace(/[^0-9.-]/g, ''));
    if (isNaN(num)) return;
    const suffix = text.replace(/[0-9.,\s-]/g, '');
    const duration = 800;
    const start = performance.now();
    const step = (ts) => {
      const p = Math.min((ts - start) / duration, 1);
      const ease = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(num * ease).toLocaleString('fr-FR') + suffix;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  });

  // NPS Modal auto-trigger
  const npsTrigger = document.querySelector('[data-nps-trigger]');
  const npsModal = document.getElementById('nps-modal');
  if (npsTrigger && npsModal) {
    const key = 'nps_done_' + npsTrigger.dataset.npsTrigger;
    if (!localStorage.getItem(key)) {
      setTimeout(() => {
        npsModal.classList.add('open');
        // Set context type/id
        const ctxInput = document.getElementById('nps-context-type');
        const ctxIdInput = document.getElementById('nps-context-id');
        if (ctxInput) ctxInput.value = npsTrigger.dataset.npsContext || '';
        if (ctxIdInput) ctxIdInput.value = npsTrigger.dataset.npsContextId || '';
      }, 2000);
    }
  }

  // NPS form submit
  const npsForm = document.getElementById('nps-form');
  if (npsForm) {
    npsForm.addEventListener('submit', function() {
      const trigger = document.querySelector('[data-nps-trigger]');
      if (trigger) {
        try { localStorage.setItem('nps_done_' + trigger.dataset.npsTrigger, '1'); } catch(e) {}
      }
    });
  }

  // NPS score selection
  const npsScoreBtns = document.querySelectorAll('.nps-score-btn');
  const npsScoreHidden = document.getElementById('nps-score-value');
  const npsSubmitBtn = document.getElementById('nps-submit-btn');
  npsScoreBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      npsScoreBtns.forEach(b => b.classList.remove('selected'));
      this.classList.add('selected');
      if (npsScoreHidden) npsScoreHidden.value = this.dataset.score;
      if (npsSubmitBtn) npsSubmitBtn.disabled = false;

      // Update preview
      const preview = document.getElementById('nps-category-preview');
      if (preview) {
        const score = parseInt(this.dataset.score);
        let category, cls;
        if (score >= 9) { category = 'Promoteur ⭐ — Vous êtes un ambassadeur !'; cls = 'badge-success'; }
        else if (score >= 7) { category = 'Passif — Satisfait mais peut mieux faire'; cls = 'badge-warning'; }
        else { category = 'Détracteur — Aidez-nous à nous améliorer'; cls = 'badge-danger'; }
        preview.innerHTML = '<span class="badge ' + cls + '">' + category + '</span>';
      }
    });
  });

  // NPS toggle feedback
  const toggleFeedback = document.getElementById('nps-toggle-feedback');
  const feedbackGroup = document.getElementById('nps-feedback-group');
  if (toggleFeedback && feedbackGroup) {
    toggleFeedback.addEventListener('click', function(e) {
      e.preventDefault();
      feedbackGroup.style.display = feedbackGroup.style.display === 'none' ? 'block' : 'none';
    });
  }
});
