// COFINANCE CI - Calculateur de crédit temps réel
document.addEventListener('DOMContentLoaded', () => {
  const amountInput = document.getElementById('calc-amount');
  const durationSelect = document.getElementById('calc-duration');
  const preview = document.getElementById('calc-preview');
  if (!amountInput || !durationSelect || !preview) return;

  const RATE = 5;
  const amountDisplay = document.getElementById('amount-display');

  function format(n) {
    return Number(n).toLocaleString('fr-FR', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' F';
  }

  function update() {
    const amount = parseFloat(amountInput.value) || 0;
    const duration = parseInt(durationSelect.value) || 3;

    const totalInterest = amount * RATE / 100 * duration / 12;
    const totalToPay = amount + totalInterest;
    const monthly = totalToPay / duration;
    const income = parseFloat(document.getElementById('calc-income')?.value) || 0;
    const ratio = income > 0 ? (monthly / income * 100) : 0;

    if (amountDisplay) amountDisplay.textContent = format(amount);

    const updateEl = function(id, val) {
      const el = document.getElementById(id);
      if (el) el.textContent = val;
    };

    updateEl('preview-amount', format(amount));
    updateEl('preview-duration', duration + ' mois');
    updateEl('preview-interest', format(totalInterest));
    updateEl('preview-total', format(totalToPay));
    updateEl('preview-monthly', format(monthly) + ' /mois');

    if (income > 0) {
      let ratioRow = document.getElementById('ratio-row');
      if (!ratioRow) {
        ratioRow = document.createElement('div');
        ratioRow.className = 'row';
        ratioRow.id = 'ratio-row';
        ratioRow.innerHTML = '<span class="label">Ratio revenu / mensualité</span><span class="value" id="ratio-value"></span>';
        preview.appendChild(ratioRow);
      }
      const rv = document.getElementById('ratio-value');
      if (rv) {
        rv.textContent = ratio.toFixed(1) + '%';
        rv.style.color = ratio > 50 ? '#ff6b6b' : ratio > 30 ? 'var(--gold-light)' : '#6bcf7f';
      }
    }
  }

  amountInput.addEventListener('input', update);
  durationSelect.addEventListener('change', update);
  const incomeInput = document.getElementById('calc-income');
  if (incomeInput) incomeInput.addEventListener('input', update);
  update();
});
