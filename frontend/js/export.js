function buildMarkdownExport(criteria, title, reviews, avg, rec, metaSummary) {
  const lines = [
    `# Review for: ${title}`,
    "",
    `**Overall score (avg)**: ${avg.toFixed(1)}/10`,
    `**Recommendation**: ${rec}`,
    "",
  ];

  if (metaSummary) {
    lines.push(`**Supervisor synthesis**: ${metaSummary}`, "");
  }

  lines.push("---", "");

  for (const c of criteria) {
    if (!reviews[c.key]) continue;
    const rv = reviews[c.key];
    lines.push(`## ${c.key}`);
    if (c.synonyms && c.synonyms.length) {
      lines.push(`*Synonyms*: ${c.synonyms.join(", ")}`);
    }
    if (c.desc) {
      lines.push(`*Description*: ${c.desc}`);
    }
    lines.push("");
    if (rv.score !== undefined && rv.score !== null) {
      lines.push(`**Score**: ${rv.score}/10`);
    }
    if (rv.text) {
      lines.push(rv.text);
    }
    if (rv.bullets && rv.bullets.length) {
      lines.push("");
      lines.push("**Comments**");
      for (const b of rv.bullets) {
        lines.push(`- ${b}`);
      }
    }
    lines.push("");
  }

  return lines.join("\n");
}

function buildJsonExport(title, abstract, avg, rec, reviews, metaSummary) {
  return JSON.stringify(
    {
      title,
      abstract,
      average_score: avg,
      recommendation: rec,
      meta_summary: metaSummary,
      rubrics: reviews,
    },
    null,
    1
  );
}

function downloadTextFile(filename, mimeType, content) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
