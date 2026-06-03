/* ═══════════════════════════════════════════════════════════════
   TikTok Shop Sentiment Dashboard — App Logic
   Chart.js driven | Dynamic tab switching
   ═══════════════════════════════════════════════════════════════ */

let DATA = null;

// Color palette
const COLORS = {
  somethinc: '#22d3ee',
  somethincAlpha: 'rgba(34, 211, 238, 0.2)',
  skintific: '#8b5cf6',
  skintificAlpha: 'rgba(139, 92, 246, 0.2)',
  positive: '#22c55e',
  neutral: '#eab308',
  negative: '#ef4444',
  cyan: '#22d3ee',
  blue: '#3b82f6',
  purple: '#8b5cf6',
  pink: '#ec4899',
  green: '#22c55e',
  orange: '#f97316',
  red: '#ef4444',
  yellow: '#eab308',
  text: '#9090a8',
  grid: 'rgba(42, 42, 58, 0.5)',
};

const CHART_DEFAULTS = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { labels: { color: COLORS.text, font: { size: 11, family: "'Inter', sans-serif" }, usePointStyle: true, padding: 12 } },
  },
  scales: {
    x: { ticks: { color: COLORS.text, font: { size: 10 } }, grid: { color: COLORS.grid } },
    y: { ticks: { color: COLORS.text, font: { size: 10 } }, grid: { color: COLORS.grid } },
  },
};

// ── Tab Navigation ──
function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(btn.dataset.tab);
      if (target) {
        target.classList.add('active');
        // Resize charts after tab becomes visible
        setTimeout(() => {
          window.dispatchEvent(new Event('resize'));
        }, 100);
      }
    });
  });
}

// ── Data Loader ──
async function loadData() {
  try {
    const resp = await fetch('data/analysis_output.json');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    DATA = await resp.json();
    console.log('Data loaded:', Object.keys(DATA).length, 'keys');
    renderAll();
  } catch (e) {
    document.getElementById('dash-content').innerHTML = `
      <div style="text-align:center;padding:80px 20px;">
        <div style="font-size:48px;margin-bottom:16px;">⚠️</div>
        <h2>Gagal memuat data</h2>
        <p style="color:var(--text-secondary);margin-top:8px;">${e.message}</p>
        <p style="color:var(--text-muted);font-size:13px;margin-top:4px;">Pastikan analysis_output.json ada di dashboard/data/</p>
      </div>`;
  }
}

// ── Render Everything ──
function renderAll() {
  renderOverview();
  renderProductAnalysis();
  renderCompetitive();
  renderOperations();
  renderPriceAffiliate();
  renderAnomalyTrends();
  renderDataTable();
}

// ════════════════════════════════════════════════════
// TAB 1: OVERVIEW
// ════════════════════════════════════════════════════
function renderOverview() {
  const meta = DATA._meta;
  const cb = DATA['02_competitive_benchmark'];
  if (!meta || !cb) return;

  const som = cb.somethinc || {};
  const skn = cb.skintific || {};

  // KPIs
  document.getElementById('kpi-total-reviews').textContent = meta.total_reviews;
  document.getElementById('kpi-som-rating').textContent = som.avg_rating || '-';
  document.getElementById('kpi-skn-rating').textContent = skn.avg_rating || '-';
  document.getElementById('kpi-anomalies').textContent = DATA['09_anomaly_detection']?.overall?.total_suspicious || 0;

  // Rating gap delta
  const ratingGap = (skn.avg_rating || 0) - (som.avg_rating || 0);
  const deltaEl = document.getElementById('kpi-som-delta');
  if (deltaEl) {
    deltaEl.textContent = ratingGap > 0 ? `▲ +${ratingGap.toFixed(2)} gap` : `▼ ${ratingGap.toFixed(2)} gap`;
    deltaEl.className = `kpi-delta ${ratingGap > 0 ? 'negative' : 'positive'}`;
  }

  // 1a. Sentiment Distribution (Doughnut)
  const sentDist = meta.sentiment_distribution || {};
  new Chart(document.getElementById('chart-sentiment-dist'), {
    type: 'doughnut',
    data: {
      labels: ['Positif', 'Netral', 'Negatif'],
      datasets: [{
        data: [sentDist.positive || 0, sentDist.neutral || 0, sentDist.negative || 0],
        backgroundColor: [COLORS.positive, COLORS.neutral, COLORS.negative],
        borderWidth: 0,
      }]
    },
    options: {
      ...CHART_DEFAULTS,
      cutout: '65%',
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: { ...CHART_DEFAULTS.plugins.legend, position: 'bottom' },
      },
    },
  });

  // 1b. Brand Comparison (Grouped Bar)
  new Chart(document.getElementById('chart-brand-compare'), {
    type: 'bar',
    data: {
      labels: ['Avg Rating', 'Positive %', 'Negative %'],
      datasets: [
        {
          label: 'Somethinc',
          data: [som.avg_rating, som.positive_pct, som.negative_pct],
          backgroundColor: COLORS.somethincAlpha,
          borderColor: COLORS.somethinc,
          borderWidth: 2,
        },
        {
          label: 'Skintific',
          data: [skn.avg_rating, skn.positive_pct, skn.negative_pct],
          backgroundColor: COLORS.skintificAlpha,
          borderColor: COLORS.skintific,
          borderWidth: 2,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' },
      },
      scales: {
        ...CHART_DEFAULTS.scales,
        y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true },
      },
    },
  });

  // 1c. Rating Distribution (Stacked Bar)
  const somRatings = som.rating_distribution || {};
  const sknRatings = skn.rating_distribution || {};
  const allRatings = ['1', '2', '3', '4', '5'];
  new Chart(document.getElementById('chart-rating-dist'), {
    type: 'bar',
    data: {
      labels: allRatings.map(r => `${r} ★`),
      datasets: [
        {
          label: 'Somethinc',
          data: allRatings.map(r => somRatings[r] || 0),
          backgroundColor: COLORS.somethinc,
        },
        {
          label: 'Skintific',
          data: allRatings.map(r => sknRatings[r] || 0),
          backgroundColor: COLORS.skintific,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      scales: {
        ...CHART_DEFAULTS.scales,
        x: { ...CHART_DEFAULTS.scales.x, stacked: false },
        y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true, stacked: false },
      },
    },
  });

  // Overview Insights
  const insights = document.getElementById('overview-insights');
  if (insights) {
    const positivePct = (sentDist.positive || 0) / meta.total_reviews * 100;
    const negativePct = (sentDist.negative || 0) / meta.total_reviews * 100;
    const anomalyPct = DATA['09_anomaly_detection']?.overall?.suspicious_pct || 0;
    insights.innerHTML = `
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(34,197,94,0.15);">📊</div>
        <h4>Sentimen Keseluruhan</h4></div>
        <p>${positivePct.toFixed(1)}% review positif, ${negativePct.toFixed(1)}% negatif.
        Rasio positif/negatif <strong>${(positivePct / Math.max(negativePct, 1)).toFixed(1)}:1</strong>.</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(34,211,238,0.15);">🏆</div>
        <h4>Kompetisi Brand</h4></div>
        <p>Skintific unggul rating ${(skn.avg_rating || 0).toFixed(2)} vs ${(som.avg_rating || 0).toFixed(2)} (gap ${Math.abs(ratingGap).toFixed(2)}).
        ${ratingGap > 0 ? '⚠️ Tapi rating lebih tinggi belum tentu kualitas — cek analisis afiliator.' : '✅ Somethinc unggul rating.'}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(239,68,68,0.15);">⚠️</div>
        <h4>Anomali Terdeteksi</h4></div>
        <p>${DATA['09_anomaly_detection']?.overall?.total_suspicious || 0} review mencurigakan (${anomalyPct}% dari total) — rating tinggi tapi teks negatif.</p>
      </div>`;
  }
}

// ════════════════════════════════════════════════════
// TAB 2: PRODUCT ANALYSIS
// ════════════════════════════════════════════════════
function renderProductAnalysis() {
  const pi = DATA['01_product_improvement'];
  const fe = DATA['03_feature_evaluation'];
  if (!pi || !fe) return;

  // Get Somethinc product data
  const somProducts = Object.entries(pi).filter(([k]) => !k.startsWith('skn'));
  const sknProducts = Object.entries(pi).filter(([k]) => k.startsWith('skn'));

  // 2a. Product Negative % (Somethinc)
  const somProdNames = somProducts.map(([_, v]) => _.replace('som-', '').slice(0, 20) + '...' .repeat(0));
  // Use actual names
  const somProdLabels = somProducts.map(([k, v]) => {
    // key is product name from the data
    return k;
  });
  const somNegPct = somProducts.map(([_, v]) => v.negative_pct || 0);

  new Chart(document.getElementById('chart-som-product-issues'), {
    type: 'bar',
    data: {
      labels: somProdLabels,
      datasets: [{
        label: 'Negatif %',
        data: somNegPct,
        backgroundColor: somNegPct.map(v => v > 30 ? COLORS.red : v > 20 ? COLORS.orange : COLORS.yellow),
        borderRadius: 4,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: 'y',
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: { display: false },
      },
      scales: {
        ...CHART_DEFAULTS.scales,
        x: { ...CHART_DEFAULTS.scales.x, beginAtZero: true, max: 60 },
      },
    },
  });

  // 2b. Skintific product issues
  const sknProdLabels = sknProducts.map(([k, _]) => k);
  const sknNegPct = sknProducts.map(([_, v]) => v.negative_pct || 0);

  new Chart(document.getElementById('chart-skn-product-issues'), {
    type: 'bar',
    data: {
      labels: sknProdLabels,
      datasets: [{
        label: 'Negatif %',
        data: sknNegPct,
        backgroundColor: sknNegPct.map(v => v > 30 ? COLORS.red : v > 20 ? COLORS.orange : COLORS.yellow),
        borderRadius: 4,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: 'y',
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: { ...CHART_DEFAULTS.scales, x: { ...CHART_DEFAULTS.scales.x, beginAtZero: true, max: 60 } },
    },
  });

  // 2c. Feature Evaluation Heatmap (Somethinc)
  buildAspectHeatmap(fe.somethinc || {}, 'chart-feature-heatmap-som', COLORS.somethinc);
  buildAspectHeatmap(fe.skintific || {}, 'chart-feature-heatmap-skn', COLORS.skintific);

  // Product insights
  const productInsights = document.getElementById('product-insights');
  if (productInsights && somProducts.length > 0) {
    // Find worst product
    const worst = somProducts.reduce((a, b) => (a[1].negative_pct || 0) > (b[1].negative_pct || 0) ? a : b);
    const worstAspects = worst[1].aspect_complaints || {};
    const topAspect = Object.entries(worstAspects).sort((a, b) => (b[1].count || 0) - (a[1].count || 0))[0];

    productInsights.innerHTML = `
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(239,68,68,0.15);">🔴</div>
        <h4>Prioritas Perbaikan</h4></div>
        <p><strong>${worst[0]}</strong> punya tingkat komplain tertinggi (${worst[1].negative_pct}%).
        ${topAspect ? `Masalah utama: <strong>${topAspect[0]}</strong> (${topAspect[1].count} keluhan).` : ''}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(34,211,238,0.15);">📐</div>
        <h4>Fitur Paling Dikeluhkan</h4></div>
        <p>${renderWorstAspect(fe.somethinc)}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(139,92,246,0.15);">🔬</div>
        <h4>Komparasi Skintific</h4></div>
        <p>${renderWorstAspect(fe.skintific)}</p>
      </div>`;
  }
}

function renderWorstAspect(features) {
  const entries = Object.entries(features || {}).sort((a, b) => (b[1].complaint_ratio || 0) - (a[1].complaint_ratio || 0));
  if (entries.length === 0) return 'Data tidak tersedia.';
  const top3 = entries.slice(0, 3);
  return top3.map(([k, v]) => `${k}: ${v.complaint_ratio}% komplain`).join(' → ');
}

function buildAspectHeatmap(data, canvasId, color) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const entries = Object.entries(data || {});
  if (entries.length === 0) return;

  const labels = entries.map(([k]) => k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()));
  const complaintRates = entries.map(([_, v]) => v.complaint_ratio || 0);
  const mentionCounts = entries.map(([_, v]) => v.total_mentions || 0);

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: 'Complaint Ratio (%)',
          data: complaintRates,
          backgroundColor: complaintRates.map(v => v > 50 ? COLORS.red : v > 30 ? COLORS.orange : v > 15 ? COLORS.yellow : COLORS.green),
          borderRadius: 4,
          yAxisID: 'y',
        },
        {
          label: 'Total Mentions',
          data: mentionCounts,
          type: 'line',
          borderColor: color,
          backgroundColor: color,
          pointBackgroundColor: color,
          pointRadius: 4,
          tension: 0.3,
          yAxisID: 'y1',
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
      scales: {
        x: { ...CHART_DEFAULTS.scales.x },
        y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true, max: 100, title: { display: true, text: 'Complaint %', color: COLORS.text } },
        y1: {
          beginAtZero: true,
          position: 'right',
          grid: { display: false },
          ticks: { color: COLORS.text },
          title: { display: true, text: 'Mentions', color: COLORS.text },
        },
      },
    },
  });
}

// ════════════════════════════════════════════════════
// TAB 3: COMPETITIVE
// ════════════════════════════════════════════════════
function renderCompetitive() {
  const cb = DATA['02_competitive_benchmark'];
  if (!cb) return;

  const gap = cb.sentiment_gap || {};
  const aspectWins = gap.aspect_wins || {};

  // 3a. Aspect Sentiment Comparison (Radar)
  const aspLabels = Object.keys(aspectWins);
  const somAspects = aspLabels.map(a => aspectWins[a].somethinc_avg || 0);
  const sknAspects = aspLabels.map(a => aspectWins[a].skintific_avg || 0);

  new Chart(document.getElementById('chart-aspect-radar'), {
    type: 'radar',
    data: {
      labels: aspLabels.map(a => a.charAt(0).toUpperCase() + a.slice(1)),
      datasets: [
        { label: 'Somethinc', data: somAspects, borderColor: COLORS.somethinc, backgroundColor: COLORS.somethincAlpha, pointBackgroundColor: COLORS.somethinc, borderWidth: 2 },
        { label: 'Skintific', data: sknAspects, borderColor: COLORS.skintific, backgroundColor: COLORS.skintificAlpha, pointBackgroundColor: COLORS.skintific, borderWidth: 2 },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'bottom' } },
      scales: {
        r: {
          beginAtZero: true,
          grid: { color: COLORS.grid },
          angleLines: { color: COLORS.grid },
          pointLabels: { color: COLORS.text, font: { size: 10 } },
          ticks: { color: COLORS.text, backdropColor: 'transparent' },
        },
      },
    },
  });

  // 3b. Most Praised Words Comparison
  const somPraised = Object.entries(cb.somethinc?.most_praised_words || {}).slice(0, 10);
  const sknPraised = Object.entries(cb.skintific?.most_praised_words || {}).slice(0, 10);

  // Praised words - Somethinc
  new Chart(document.getElementById('chart-som-praised'), {
    type: 'bar',
    data: {
      labels: somPraised.map(([k]) => k),
      datasets: [{
        label: 'Somethinc',
        data: somPraised.map(([_, v]) => v),
        backgroundColor: COLORS.somethinc,
        borderRadius: 4,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: 'y',
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: { ...CHART_DEFAULTS.scales, x: { ...CHART_DEFAULTS.scales.x, beginAtZero: true } },
    },
  });

  // Skintific praised
  new Chart(document.getElementById('chart-skn-praised'), {
    type: 'bar',
    data: {
      labels: sknPraised.map(([k]) => k),
      datasets: [{
        label: 'Skintific',
        data: sknPraised.map(([_, v]) => v),
        backgroundColor: COLORS.skintific,
        borderRadius: 4,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: 'y',
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: { ...CHART_DEFAULTS.scales, x: { ...CHART_DEFAULTS.scales.x, beginAtZero: true } },
    },
  });

  // 3c. Sentiment Gap Bar
  const gapLabels = Object.keys(aspectWins);
  const gapValues = gapLabels.map(a => aspectWins[a].gap || 0);

  new Chart(document.getElementById('chart-sentiment-gap'), {
    type: 'bar',
    data: {
      labels: gapLabels.map(a => a.charAt(0).toUpperCase() + a.slice(1)),
      datasets: [{
        label: 'Somethinc - Skintific',
        data: gapValues,
        backgroundColor: gapValues.map(v => v > 0 ? COLORS.somethinc : COLORS.skintific),
        borderRadius: 4,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true } },
    },
  });

  // Competitive insights
  const compInsights = document.getElementById('competitive-insights');
  if (compInsights) {
    const winnerAspects = gapLabels.filter(a => (aspectWins[a]?.winner || '') === 'somethinc');
    const loserAspects = gapLabels.filter(a => (aspectWins[a]?.winner || '') === 'skintific');

    compInsights.innerHTML = `
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(34,211,238,0.15);">🥇</div>
        <h4>Unggulan Somethinc</h4></div>
        <p>${winnerAspects.length > 0 ? winnerAspects.map(a => `✅ <strong>${a}</strong>: +${Math.abs(aspectWins[a]?.gap || 0).toFixed(2)}`).join('<br>') : 'Tidak ada aspek yang unggul.'}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(139,92,246,0.15);">⚠️</div>
        <h4>Skintific Unggul</h4></div>
        <p>${loserAspects.length > 0 ? loserAspects.map(a => `🔴 <strong>${a}</strong>: selisih ${Math.abs(aspectWins[a]?.gap || 0).toFixed(2)}`).join('<br>') : 'Tidak ada.'}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(234,179,8,0.15);">💡</div>
        <h4>Action Item</h4></div>
        <p>${gap.sentiment_gap > 0 ? 'Somethinc perlu' : 'Somethinc perlu'} tingkatkan <strong>${loserAspects[0] || 'harga'}</strong> untuk mengejar ketertinggalan.</p>
      </div>`;
  }
}

// ════════════════════════════════════════════════════
// TAB 4: OPERATIONS
// ════════════════════════════════════════════════════
function renderOperations() {
  const ops = DATA['04_operational_issues'];
  if (!ops) return;

  ['somethinc', 'skintific'].forEach(brand => {
    const data = ops[brand] || {};
    const breakdown = data.operational_breakdown || {};

    const chartId = brand === 'somethinc' ? 'chart-ops-som' : 'chart-ops-skn';
    const ctx = document.getElementById(chartId);
    if (!ctx) return;

    const labels = Object.keys(breakdown).map(k =>
      k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
    );
    const counts = Object.values(breakdown).map(v => v.total_mentions || 0);
    const ratings = Object.values(breakdown).map(v => v.avg_rating || 0);

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Mentions',
            data: counts,
            backgroundColor: brand === 'somethinc' ? COLORS.somethincAlpha : COLORS.skintificAlpha,
            borderColor: brand === 'somethinc' ? COLORS.somethinc : COLORS.skintific,
            borderWidth: 2,
            borderRadius: 4,
            yAxisID: 'y',
          },
          {
            label: 'Avg Rating',
            data: ratings,
            type: 'line',
            borderColor: COLORS.red,
            backgroundColor: COLORS.red,
            pointBackgroundColor: COLORS.red,
            pointRadius: 5,
            tension: 0.3,
            yAxisID: 'y1',
          },
        ],
      },
      options: {
        ...CHART_DEFAULTS,
        plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
        scales: {
          x: { ...CHART_DEFAULTS.scales.x },
          y: { beginAtZero: true, position: 'left', ticks: { color: COLORS.text }, grid: { color: COLORS.grid } },
          y1: { beginAtZero: true, max: 5, position: 'right', grid: { display: false }, ticks: { color: COLORS.text } },
        },
      },
    });

    // Ops KPIs
    const kpiPrefix = brand === 'somethinc' ? 'som' : 'skn';
    document.getElementById(`kpi-${kpiPrefix}-ops-pct`).textContent = (data.pct_of_all_reviews || 0).toFixed(1) + '%';
    document.getElementById(`kpi-${kpiPrefix}-ops-rating`).textContent = (data.avg_rating_with_ops_issue || 0).toFixed(2);
    document.getElementById(`kpi-${kpiPrefix}-noops-rating`).textContent = (data.avg_rating_without_ops_issue || 0).toFixed(2);
    document.getElementById(`kpi-${kpiPrefix}-false-neg`).textContent = data.false_negatives_from_ops || 0;
  });

  // Operations insights
  const opsInsights = document.getElementById('ops-insights');
  if (opsInsights) {
    opsInsights.innerHTML = `
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(239,68,68,0.15);">📦</div>
        <h4>Dampak Operasional</h4></div>
        <p>Rating turun drastis saat ada issue operasional. Somethinc: ${(ops.somethinc?.avg_rating_with_ops_issue || 0).toFixed(2)} vs tanpa issue ${(ops.somethinc?.avg_rating_without_ops_issue || 0).toFixed(2)}. Gap: ${(ops.somethinc?.rating_gap_due_to_ops || 0).toFixed(2)}.</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(34,197,94,0.15);">📉</div>
        <h4>False Negatives</h4></div>
        <p>${(ops.somethinc?.false_negatives_from_ops || 0)} review Somethinc rating rendah hanya karena operasional, bukan produk. Ini bisa diperbaiki tanpa mengubah formula.</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(139,92,246,0.15);">⚡</div>
        <h4>Quick Win</h4></div>
        <p>Prioritas: perbaiki packing dan kecepatan pengiriman — ini yang paling sering dikeluhkan dan langsung berdampak ke rating.</p>
      </div>`;
  }
}

// ════════════════════════════════════════════════════
// TAB 5: PRICE & AFFILIATE
// ════════════════════════════════════════════════════
function renderPriceAffiliate() {
  const ps = DATA['05_price_sensitivity'];
  const aff = DATA['07_affiliate_influence'];
  if (!ps || !aff) return;

  // 5a. Price Sensitivity
  const priceLabels = ['Avg Rating', 'Avg Sentiment'];
  new Chart(document.getElementById('chart-price-sensitivity'), {
    type: 'bar',
    data: {
      labels: priceLabels,
      datasets: [
        {
          label: 'Somethinc - Ada mention harga',
          data: [(ps.somethinc?.avg_rating_price_mentioners || 0), (ps.somethinc?.avg_sentiment_price_mentioners || 0) / 4],
          backgroundColor: COLORS.somethincAlpha,
          borderColor: COLORS.somethinc,
          borderWidth: 2,
        },
        {
          label: 'Somethinc - Tanpa mention harga',
          data: [(ps.somethinc?.avg_rating_no_price_mention || 0), (ps.somethinc?.avg_sentiment_no_price_mention || 0) / 4],
          backgroundColor: 'rgba(34, 211, 238, 0.05)',
          borderColor: COLORS.somethinc,
          borderWidth: 1,
          borderDash: [4, 4],
        },
        {
          label: 'Skintific - Ada mention harga',
          data: [(ps.skintific?.avg_rating_price_mentioners || 0), (ps.skintific?.avg_sentiment_price_mentioners || 0) / 4],
          backgroundColor: COLORS.skintificAlpha,
          borderColor: COLORS.skintific,
          borderWidth: 2,
        },
        {
          label: 'Skintific - Tanpa mention harga',
          data: [(ps.skintific?.avg_rating_no_price_mention || 0), (ps.skintific?.avg_sentiment_no_price_mention || 0) / 4],
          backgroundColor: 'rgba(139, 92, 246, 0.05)',
          borderColor: COLORS.skintific,
          borderWidth: 1,
          borderDash: [4, 4],
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true } },
    },
  });

  // 5b. Discount Effect
  new Chart(document.getElementById('chart-discount-effect'), {
    type: 'bar',
    data: {
      labels: ['Somethinc', 'Skintific'],
      datasets: [
        {
          label: 'Avg Rating (dengan diskon)',
          data: [(ps.somethinc?.avg_rating_discount_mentioners || 0), (ps.skintific?.avg_rating_discount_mentioners || 0)],
          backgroundColor: COLORS.green,
          borderRadius: 4,
        },
        {
          label: 'Avg Rating (tanpa diskon)',
          data: [(ps.somethinc?.avg_rating_no_price_mention || 0), (ps.skintific?.avg_rating_no_price_mention || 0)],
          backgroundColor: COLORS.orange,
          borderRadius: 4,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true, max: 5 } },
    },
  });

  // 5c. Affiliate Influence
  new Chart(document.getElementById('chart-affiliate-comparison'), {
    type: 'bar',
    data: {
      labels: ['Somethinc', 'Skintific'],
      datasets: [
        {
          label: 'Affiliate Avg Rating',
          data: [(aff.somethinc?.affiliate_avg_rating || 0), (aff.skintific?.affiliate_avg_rating || 0)],
          backgroundColor: COLORS.pink,
          borderRadius: 4,
        },
        {
          label: 'Organic Avg Rating',
          data: [(aff.somethinc?.organic_avg_rating || 0), (aff.skintific?.organic_avg_rating || 0)],
          backgroundColor: COLORS.blue,
          borderRadius: 4,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true, max: 5 } },
    },
  });

  // 5d. Rating inflation per brand
  const inflationData = {
    labels: ['Somethinc', 'Skintific'],
    datasets: [{
      label: 'Rating Inflation (Affiliate - Organic)',
      data: [
        (aff.somethinc?.rating_inflation || 0),
        (aff.skintific?.rating_inflation || 0),
      ],
      backgroundColor: [
        COLORS.somethinc,
        COLORS.skintific,
      ],
      borderRadius: 4,
    }],
  };

  new Chart(document.getElementById('chart-rating-inflation'), {
    type: 'bar',
    data: inflationData,
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true } },
    },
  });

  // Price insights
  const priceInsights = document.getElementById('price-insights');
  if (priceInsights) {
    const somInfl = (aff.somethinc?.rating_inflation || 0);
    const sknInfl = (aff.skintific?.rating_inflation || 0);
    priceInsights.innerHTML = `
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(34,211,238,0.15);">💰</div>
        <h4>Sensitivitas Harga</h4></div>
        <p>Skintific: rating ${ps.skintific?.avg_rating_discount_mentioners || 0} saat diskon, ${ps.skintific?.avg_rating_no_price_mention || 0} tanpa diskon. ${(ps.skintific?.avg_rating_discount_mentioners || 0) > (ps.skintific?.avg_rating_no_price_mention || 0) ? 'Diskon signifikan dorong rating!' : 'Diskon tidak terlalu pengaruh.'}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(236,72,153,0.15);">📢</div>
        <h4>Inflasi Afiliator</h4></div>
        <p>Somethinc: rating afiliator ${aff.somethinc?.affiliate_avg_rating || 0} vs organik ${aff.somethinc?.organic_avg_rating || 0} (inflasi +${somInfl.toFixed(2)}).<br>
        Skintific: ${aff.skintific?.affiliate_avg_rating || 0} vs ${aff.skintific?.organic_avg_rating || 0} (inflasi +${sknInfl.toFixed(2)}).</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(139,92,246,0.15);">🧹</div>
        <h4>Koreksi Rating</h4></div>
        <p>${sknInfl > somInfl ? 'Skintific lebih bergantung pada afiliator (+' + sknInfl.toFixed(2) + '). Rating riil mungkin lebih rendah dari yang terlihat.' : 'Somethinc lebih alami — rating afiliator dan organik lebih dekat.'}</p>
      </div>`;
  }
}

// ════════════════════════════════════════════════════
// TAB 6: ANOMALY & TRENDS
// ════════════════════════════════════════════════════
function renderAnomalyTrends() {
  const ad = DATA['09_anomaly_detection'];
  const tt = DATA['10_temporal_trends'];
  if (!ad || !tt) return;

  // 6a. Suspicious by Brand
  new Chart(document.getElementById('chart-anomaly-brand'), {
    type: 'pie',
    data: {
      labels: ['Somethinc', 'Skintific'],
      datasets: [{
        data: [ad.somethinc?.total_suspicious || 0, ad.skintific?.total_suspicious || 0],
        backgroundColor: [COLORS.somethinc, COLORS.skintific],
        borderWidth: 0,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: {
        ...CHART_DEFAULTS.plugins,
        legend: { ...CHART_DEFAULTS.plugins.legend, position: 'bottom' },
      },
    },
  });

  // 6b. Suspicious % by Brand
  new Chart(document.getElementById('chart-anomaly-pct'), {
    type: 'bar',
    data: {
      labels: ['Somethinc', 'Skintific'],
      datasets: [{
        label: 'Suspicious %',
        data: [ad.somethinc?.suspicious_pct || 0, ad.skintific?.suspicious_pct || 0],
        backgroundColor: [COLORS.somethinc, COLORS.skintific],
        borderRadius: 4,
      }],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true } },
    },
  });

  // 6c. Weekly Pattern
  const weekly = tt.weekly_pattern || {};
  const weekdays = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'];
  const negByDay = weekdays.map(d => weekly[d]?.negative || 0);
  const posByDay = weekdays.map(d => weekly[d]?.positive || 0);

  new Chart(document.getElementById('chart-weekly-pattern'), {
    type: 'line',
    data: {
      labels: weekdays,
      datasets: [
        {
          label: 'Positif',
          data: posByDay,
          borderColor: COLORS.green,
          backgroundColor: 'rgba(34,197,94,0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
        },
        {
          label: 'Negatif',
          data: negByDay,
          borderColor: COLORS.red,
          backgroundColor: 'rgba(239,68,68,0.1)',
          fill: true,
          tension: 0.4,
          pointRadius: 4,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true } },
    },
  });

  // 6d. Brand Timeline (weekly)
  const timeline = tt.brand_timeline || {};
  const timeBuckets = ['0-7 hari', '8-30 hari', '31-60 hari', '61-90 hari', '90+ hari'];

  new Chart(document.getElementById('chart-timeline'), {
    type: 'line',
    data: {
      labels: timeBuckets,
      datasets: [
        {
          label: 'Somethinc Sentiment',
          data: timeBuckets.map(b => timeline.somethinc?.[b]?.avg_sentiment || 0),
          borderColor: COLORS.somethinc,
          backgroundColor: COLORS.somethincAlpha,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
        },
        {
          label: 'Skintific Sentiment',
          data: timeBuckets.map(b => timeline.skintific?.[b]?.avg_sentiment || 0),
          borderColor: COLORS.skintific,
          backgroundColor: COLORS.skintificAlpha,
          fill: true,
          tension: 0.4,
          pointRadius: 4,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
      scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true } },
    },
  });

  // 6e. Peak Complaint Days
  if (tt.peak_complaint_days) {
    const peakLabels = Object.keys(tt.peak_complaint_days);
    const peakValues = Object.values(tt.peak_complaint_days);
    new Chart(document.getElementById('chart-peak-complaints'), {
      type: 'bar',
      data: {
        labels: peakLabels,
        datasets: [{
          label: 'Deviation from avg (%)',
          data: peakValues,
          backgroundColor: peakValues.map(v => v > 0 ? COLORS.red : COLORS.green),
          borderRadius: 4,
        }],
      },
      options: {
        ...CHART_DEFAULTS,
        plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false } },
        scales: { ...CHART_DEFAULTS.scales, y: { ...CHART_DEFAULTS.scales.y, beginAtZero: true } },
      },
    });
  }

  // Anomaly insights
  const anomalyInsights = document.getElementById('anomaly-insights');
  if (anomalyInsights) {
    const worstDay = Object.entries(tt.peak_complaint_days || {}).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))[0] || ['-', 0];
    anomalyInsights.innerHTML = `
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(234,179,8,0.15);">🔍</div>
        <h4>Anomali Rating</h4></div>
        <p>${ad.overall?.suspicious_alert || ''}<br>
        ${ad.overall?.total_suspicious || 0} review suspicious (${ad.overall?.suspicious_pct || 0}% dari total). 
        ${(ad.overall?.suspicious_pct || 0) > 5 ? '⚠️ Perlu investigasi lebih lanjut.' : '✅ Masih dalam batas wajar.'}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(239,68,68,0.15);">📅</div>
        <h4>Peak Complaint Day</h4></div>
        <p>Hari dengan komplain tertinggi: <strong>${worstDay[0]}</strong> (${Math.abs(worstDay[1]).toFixed(1)}% dari rata-rata). 
        ${worstDay[0] !== '-' ? 'Cek apakah ada flash sale atau batch baru minggu sebelumnya.' : ''}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(34,211,238,0.15);">📈</div>
        <h4>Sentimen Timeline</h4></div>
        <p>${Object.entries(timeline.somethinc || {}).length > 0 ? 'Somethinc sentimen ' + (Object.values(timeline.somethinc)[0]?.avg_sentiment > Object.values(timeline.somethinc).slice(-1)[0]?.avg_sentiment ? 'menurun' : 'stabil') + ' dari waktu ke waktu.' : 'Data timeline tidak tersedia.'}</p>
      </div>`;
  }
}

// ════════════════════════════════════════════════════
// TAB 7: DATA TABLE
// ════════════════════════════════════════════════════
function renderDataTable() {
  const rp = DATA['08_repeat_purchase'];
  const fr = DATA['06_feature_requests'];

  // Loyalty KPIs
  document.getElementById('kpi-som-repeat').textContent = (rp.somethinc?.repeat_pct || 0).toFixed(1) + '%';
  document.getElementById('kpi-skn-repeat').textContent = (rp.skintific?.repeat_pct || 0).toFixed(1) + '%';
  document.getElementById('kpi-som-requests').textContent = fr.somethinc?.total_feature_requests || 0;
  document.getElementById('kpi-skn-requests').textContent = fr.skintific?.total_feature_requests || 0;

  // Most repeated products
  const somRepeatProds = rp.somethinc?.most_repeated_products || {};
  const sknRepeatProds = rp.skintific?.most_repeated_products || {};
  const allRepeatProdLabels = [...new Set([...Object.keys(somRepeatProds), ...Object.keys(sknRepeatProds)])].slice(0, 8);

  new Chart(document.getElementById('chart-repeat-product'), {
    type: 'bar',
    data: {
      labels: allRepeatProdLabels,
      datasets: [
        {
          label: 'Somethinc',
          data: allRepeatProdLabels.map(p => somRepeatProds[p] || 0),
          backgroundColor: COLORS.somethinc,
          borderRadius: 4,
        },
        {
          label: 'Skintific',
          data: allRepeatProdLabels.map(p => sknRepeatProds[p] || 0),
          backgroundColor: COLORS.skintific,
          borderRadius: 4,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: 'y',
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
      scales: { ...CHART_DEFAULTS.scales, x: { ...CHART_DEFAULTS.scales.x, beginAtZero: true } },
    },
  });

  // Feature requests
  const somReqs = fr.somethinc?.most_requested_products || {};
  const sknReqs = fr.skintific?.most_requested_products || {};
  const allReqLabels = [...new Set([...Object.keys(somReqs), ...Object.keys(sknReqs)])].slice(0, 8);

  new Chart(document.getElementById('chart-feature-requests'), {
    type: 'bar',
    data: {
      labels: allReqLabels,
      datasets: [
        {
          label: 'Somethinc',
          data: allReqLabels.map(p => somReqs[p] || 0),
          backgroundColor: COLORS.somethinc,
          borderRadius: 4,
        },
        {
          label: 'Skintific',
          data: allReqLabels.map(p => sknReqs[p] || 0),
          backgroundColor: COLORS.skintific,
          borderRadius: 4,
        },
      ],
    },
    options: {
      ...CHART_DEFAULTS,
      indexAxis: 'y',
      plugins: { ...CHART_DEFAULTS.plugins, legend: { ...CHART_DEFAULTS.plugins.legend, position: 'top' } },
      scales: { ...CHART_DEFAULTS.scales, x: { ...CHART_DEFAULTS.scales.x, beginAtZero: true } },
    },
  });

  // Customer insights
  const custInsights = document.getElementById('customer-insights');
  if (custInsights) {
    custInsights.innerHTML = `
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(34,211,238,0.15);">❤️</div>
        <h4>Loyalitas Brand</h4></div>
        <p>Somethinc: ${rp.somethinc?.repeat_pct || 0}% review menyebut repeat order.<br>
        Skintific: ${rp.skintific?.repeat_pct || 0}%.<br>
        ${(rp.somethinc?.repeat_pct || 0) > (rp.skintific?.repeat_pct || 0) ? '✅ Somethinc punya loyalitas lebih tinggi.' : '⚠️ Skintific unggul repeat rate.'}</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(139,92,246,0.15);">💡</div>
        <h4>R&D Signal</h4></div>
        <p>Banyak permintaan varian untuk ${Object.keys(fr.somethinc?.most_requested_products || {})[0] || 'produk Somethinc'}. 
        ${fr.somethinc?.total_feature_requests || 0} request untuk Somethinc, ${fr.skintific?.total_feature_requests || 0} untuk Skintific.</p>
      </div>
      <div class="insight-card">
        <div class="insight-card-header"><div class="insight-icon" style="background:rgba(234,179,8,0.15);">⭐</div>
        <h4>Rating Loyal vs Baru</h4></div>
        <p>Somethinc: repeat customer rating ${rp.somethinc?.repeat_avg_rating || 0} vs pembeli baru ${rp.somethinc?.non_repeat_avg_rating || 0} (premium loyalitas +${(rp.somethinc?.loyalty_rating_premium || 0)}).<br>
        Skintific: ${rp.skintific?.repeat_avg_rating || 0} vs ${rp.skintific?.non_repeat_avg_rating || 0} (premium +${rp.skintific?.loyalty_rating_premium || 0}).</p>
      </div>`;
  }
}

// ════════════════════════════════════════════════════
// INIT
// ════════════════════════════════════════════════════
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  loadData();
});
