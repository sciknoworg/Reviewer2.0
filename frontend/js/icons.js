// Small hand-authored line-icon set, one per rubric, keyed by rubric name.
// Unknown/future rubric keys fall back to ICONS.default so the picker and
// tabs never break if the backend's rubric registry grows.
const ICON_STROKE = 'stroke="currentColor" fill="none" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"';

const ICONS = {
  "Originality": `<circle cx="12" cy="10" r="5" ${ICON_STROKE}/><path d="M9.5 18h5M10 20.5h4" ${ICON_STROKE}/><path d="M12 3v1.4M5 6l1 1M19 6l-1 1" ${ICON_STROKE}/>`,
  "Soundness": `<path d="M12 3l7 3v5c0 4.4-3 7.6-7 9-4-1.4-7-4.6-7-9V6l7-3z" ${ICON_STROKE}/><path d="M9 12l2 2 4-4" ${ICON_STROKE}/>`,
  "Impact": `<path d="M4 16l5-5 3.5 3.5L20 7" ${ICON_STROKE}/><path d="M14.5 7H20v5.5" ${ICON_STROKE}/>`,
  "Presentation": `<rect x="6" y="3" width="12" height="18" rx="1.5" ${ICON_STROKE}/><path d="M9 8h6M9 12h6M9 16h3.5" ${ICON_STROKE}/>`,
  "Positioning w.r.t Related Work": `<circle cx="8" cy="12" r="3.2" ${ICON_STROKE}/><circle cx="16" cy="12" r="3.2" ${ICON_STROKE}/><path d="M10.6 12h2.8" ${ICON_STROKE}/>`,
  "Reference & Citation Quality": `<path d="M12 5c-1.6-1.2-3.6-1.6-6-1.2v13c2.4-.4 4.4 0 6 1.2 1.6-1.2 3.6-1.6 6-1.2v-13c-2.4-.4-4.4 0-6 1.2z" ${ICON_STROKE}/><path d="M12 5v13" ${ICON_STROKE}/>`,
  "Reproducibility & Artifacts": `<path d="M12 3l7 4v10l-7 4-7-4V7l7-4z" ${ICON_STROKE}/><path d="M5 7l7 4 7-4M12 11v9" ${ICON_STROKE}/>`,
  "Ethical Considerations & Broader Impact": `<path d="M12 3v18M8 21h8" ${ICON_STROKE}/><path d="M12 6l-5 1.5L4 12a3 3 0 006 0L7 7.5" ${ICON_STROKE}/><path d="M12 6l5 1.5L20 12a3 3 0 01-6 0l3-4.5" ${ICON_STROKE}/>`,
  "default": `<circle cx="12" cy="12" r="8" ${ICON_STROKE}/><path d="M12 8v4l2.5 2.5" ${ICON_STROKE}/>`,
};

function rubricIconSvg(key) {
  const inner = ICONS[key] || ICONS.default;
  return `<svg class="rubric-icon" viewBox="0 0 24 24" aria-hidden="true">${inner}</svg>`;
}
