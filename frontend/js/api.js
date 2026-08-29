async function fetchCriteria() {
  const res = await fetch(`${window.API_BASE_URL}/api/criteria`);
  if (!res.ok) {
    throw new Error(`Failed to load rubric list (status ${res.status})`);
  }
  return res.json();
}

// Native EventSource only supports GET, but we need to POST a file, so we
// read the streamed response body directly and parse "data: {...}\n\n"
// frames out of it by hand.
async function submitPaperStream(file, rubricKeys, onEvent) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("rubrics", rubricKeys.join(","));

  const res = await fetch(`${window.API_BASE_URL}/api/review`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Review request failed (status ${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);
      const line = frame.split("\n").find((l) => l.startsWith("data:"));
      if (!line) continue;
      const payload = line.slice(5).trim();
      if (!payload) continue;
      try {
        onEvent(JSON.parse(payload));
      } catch (e) {
        console.error("Failed to parse review event", e, payload);
      }
    }
  }
}
