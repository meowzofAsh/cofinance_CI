(function() {
  // NPS Survey Modal logic
  const surveyModal = document.getElementById('nps-modal');
  const scoreInputs = document.querySelectorAll('.nps-score-btn');
  const scoreHidden = document.getElementById('nps-score-value');
  const submitBtn = document.getElementById('nps-submit-btn');
  const feedbackText = document.getElementById('nps-comment');
  const npsForm = document.getElementById('nps-form');

  if (!surveyModal) return;

  // Score selection
  scoreInputs.forEach(function(btn) {
    btn.addEventListener('click', function() {
      scoreInputs.forEach(function(b) { b.classList.remove('selected'); });
      this.classList.add('selected');
      if (scoreHidden) scoreHidden.value = this.dataset.score;
      if (submitBtn) submitBtn.disabled = false;
      updateNPSPreview(this.dataset.score);
    });
  });

  function updateNPSPreview(score) {
    const preview = document.getElementById('nps-category-preview');
    if (!preview) return;
    var category, cls;
    score = parseInt(score);
    if (score >= 9) {
      category = 'Promoteur ⭐ — Vous êtes un véritable ambassadeur !';
      cls = 'badge-success';
    } else if (score >= 7) {
      category = 'Passif — Satisfait mais peut mieux faire';
      cls = 'badge-warning';
    } else {
      category = 'Détracteur 😟 — Aidez-nous à nous améliorer';
      cls = 'badge-danger';
    }
    preview.innerHTML = '<span class="badge ' + cls + '">' + category + '</span>';
  }

  // Auto-show modal on page load if data attributes present
  var trigger = document.querySelector('[data-nps-trigger]');
  if (trigger && !localStorage.getItem('nps_done_' + trigger.dataset.npsTrigger)) {
    setTimeout(function() {
      surveyModal.classList.add('open');
    }, 1500);
  }

  // Mark as done on submit
  if (npsForm) {
    npsForm.addEventListener('submit', function() {
      var trigger = document.querySelector('[data-nps-trigger]');
      if (trigger) {
        try {
          localStorage.setItem('nps_done_' + trigger.dataset.npsTrigger, '1');
        } catch(e) {}
      }
    });
  }

  // Feedback textarea toggle
  const toggleFeedback = document.getElementById('nps-toggle-feedback');
  const feedbackGroup = document.getElementById('nps-feedback-group');
  if (toggleFeedback && feedbackGroup) {
    toggleFeedback.addEventListener('click', function(e) {
      e.preventDefault();
      feedbackGroup.style.display = feedbackGroup.style.display === 'none' ? 'block' : 'none';
    });
  }
})();
