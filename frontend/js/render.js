function scoreBand(score) {
  if (score >= 8) return "good";
  if (score >= 5) return "mid";
  return "low";
}

function renderScoreGauge(score, size) {
  size = size || 72;
  const strokeWidth = size * 0.11;
  const radius = size / 2 - strokeWidth;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.max(0, Math.min(10, score)) / 10;
  const offset = circumference * (1 - pct);
  const band = scoreBand(score);

  return `
    <svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" class="score-gauge score-gauge--${band}">
      <circle cx="${size / 2}" cy="${size / 2}" r="${radius}" class="score-gauge__track" stroke-width="${strokeWidth}" />
      <circle cx="${size / 2}" cy="${size / 2}" r="${radius}" class="score-gauge__value" stroke-width="${strokeWidth}"
        stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
        transform="rotate(-90 ${size / 2} ${size / 2})" />
      <text x="50%" y="50%" class="score-gauge__label" dominant-baseline="central" text-anchor="middle">${score}</text>
    </svg>`;
}

function renderRubricPicker(criteria) {
  const list = document.getElementById("rubric-list");
  list.innerHTML = "";
  criteria.forEach((c) => {
    const label = document.createElement("label");
    label.className = "rubric-option";
    label.innerHTML = `
      <input type="checkbox" value="${c.key}" checked />
      ${rubricIconSvg(c.key)}
      <span class="rubric-option__text">
        <span class="rubric-option__key">${c.key}</span>
        <span class="rubric-option__desc">${c.desc}</span>
      </span>
    `;
    list.appendChild(label);
  });
}

function getSelectedRubrics() {
  return Array.from(document.querySelectorAll('#rubric-list input[type="checkbox"]:checked')).map((el) => el.value);
}

function setAllRubrics(checked) {
  document.querySelectorAll('#rubric-list input[type="checkbox"]').forEach((el) => {
    el.checked = checked;
  });
}

const PROGRESS_ICONS = {
  pending: "&#9675;",
  running: "&#8635;",
  done: "&#10003;",
  error: "&#10007;",
};

function renderProgressList(selectedKeys) {
  const list = document.getElementById("progress-list");
  list.innerHTML = "";
  selectedKeys.forEach((key) => {
    const li = document.createElement("li");
    li.className = "progress-item progress-item--pending";
    li.dataset.key = key;
    li.innerHTML = `
      <span class="progress-item__icon">${PROGRESS_ICONS.pending}</span>
      ${rubricIconSvg(key)}
      <span class="progress-item__label">${key}</span>
      <span class="progress-item__status">Queued</span>
    `;
    list.appendChild(li);
  });
}

function setProgressItemStatus(key, status, statusText) {
  const item = document.querySelector(`.progress-item[data-key="${CSS.escape(key)}"]`);
  if (!item) return;
  item.className = `progress-item progress-item--${status}`;
  item.querySelector(".progress-item__icon").innerHTML = PROGRESS_ICONS[status] || PROGRESS_ICONS.pending;
  item.querySelector(".progress-item__status").textContent = statusText;
}

function renderPaperHeader(reviewData) {
  document.getElementById("paper-title").textContent = reviewData.title || "Unknown Title";
  document.getElementById("paper-abstract").textContent = reviewData.abstract || "";
}

function renderSummary(reviewData) {
  document.getElementById("overall-gauge").innerHTML = renderScoreGauge(reviewData.overall_score, 96);
  const pill = document.getElementById("overall-recommendation");
  pill.textContent = reviewData.recommendation;
  pill.className = `recommendation-pill recommendation-pill--${scoreBand(reviewData.overall_score)}`;
  document.getElementById("meta-summary").textContent = reviewData.meta_summary || "";
}

function renderTabs(criteria, reviewData, showScores, showBullets) {
  const tabList = document.getElementById("tab-list");
  const tabPanels = document.getElementById("tab-panels");
  tabList.innerHTML = "";
  tabPanels.innerHTML = "";

  const shown = criteria.filter((c) => reviewData.reviews[c.key]);

  shown.forEach((c, idx) => {
    const rv = reviewData.reviews[c.key] || {};

    const tabBtn = document.createElement("button");
    tabBtn.className = "tab" + (idx === 0 ? " tab--active" : "");
    tabBtn.type = "button";
    tabBtn.innerHTML = `${rubricIconSvg(c.key)}<span>${c.key}</span>`;
    tabBtn.setAttribute("role", "tab");
    tabList.appendChild(tabBtn);

    const panel = document.createElement("div");
    panel.className = "tab-panel" + (idx === 0 ? " tab-panel--active" : "");
    panel.id = `panel-${idx}`;

    let html = `<div class="tab-panel__head">`;
    if (showScores && rv.score !== undefined && rv.score !== null) {
      html += `<div class="tab-panel__gauge">${renderScoreGauge(rv.score, 56)}</div>`;
    }
    html += `<div>`;
    if (c.synonyms && c.synonyms.length) {
      html += `<p class="tab-panel__synonyms">Synonyms: ${c.synonyms.join(", ")}</p>`;
    }
    if (c.desc) {
      html += `<p class="tab-panel__desc">${c.desc}</p>`;
    }
    html += `</div></div>`;

    if (rv.text) {
      html += `<p class="tab-panel__text"></p>`;
    }
    panel.innerHTML = html;

    if (rv.text) {
      panel.querySelector(".tab-panel__text").textContent = rv.text;
    }

    if (showBullets && rv.bullets && rv.bullets.length) {
      const ul = document.createElement("ul");
      ul.className = "tab-panel__bullets";
      rv.bullets.forEach((b) => {
        const li = document.createElement("li");
        li.textContent = b;
        ul.appendChild(li);
      });
      panel.appendChild(ul);
    }

    tabPanels.appendChild(panel);

    tabBtn.addEventListener("click", () => {
      tabList.querySelectorAll(".tab").forEach((t) => t.classList.remove("tab--active"));
      tabPanels.querySelectorAll(".tab-panel").forEach((p) => p.classList.remove("tab-panel--active"));
      tabBtn.classList.add("tab--active");
      panel.classList.add("tab-panel--active");
    });
  });
}
