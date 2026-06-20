let lastRequestId = null;

const queryEl = document.getElementById("query");
const domainEl = document.getElementById("domain");
const minScoreEl = document.getElementById("minScore");
const answerText = document.getElementById("answerText");
const citationsList = document.getElementById("citationsList");
const feedbackBox = document.getElementById("feedbackBox");

async function ask() {
  const query = queryEl.value.trim();
  if (!query) {
    answerText.textContent = "Please enter a query.";
    return;
  }

  answerText.textContent = "Running retrieval and generation...";
  citationsList.innerHTML = "<p class='muted'>Retrieving evidence...</p>";

  const res = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      domain: domainEl.value || null,
      min_score: Number(minScoreEl.value || 0),
    }),
  });

  const data = await res.json();
  if (!res.ok) {
    answerText.textContent = data.error || "Unexpected error.";
    return;
  }

  lastRequestId = data.request_id;
  answerText.textContent = data.answer;
  feedbackBox.hidden = false;
  renderCitations(data.citations || []);
}

function renderCitations(citations) {
  if (!citations.length) {
    citationsList.innerHTML = "<p class='muted'>No citations passed the confidence threshold.</p>";
    return;
  }

  citationsList.innerHTML = citations
    .map(
      (c) => `
      <article class="citation-item">
        <h3>${c.title}</h3>
        <p class="meta">${c.source} • domain: ${c.domain} • score: ${c.score}</p>
        <p>${c.snippet}</p>
      </article>
    `,
    )
    .join("");
}

async function reindex() {
  answerText.textContent = "Rebuilding vector index...";
  const res = await fetch("/api/ingest", { method: "POST" });
  const data = await res.json();

  if (!res.ok) {
    answerText.textContent = data.error || "Index rebuild failed.";
    return;
  }

  answerText.textContent = `Index rebuilt: ${data.stats.documents} docs, ${data.stats.chunks} chunks.`;
}

async function submitFeedback(rating) {
  if (!lastRequestId) return;

  await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id: lastRequestId, rating }),
  });

  answerText.textContent += "\n\nFeedback saved. Thanks.";
}

document.getElementById("askBtn").addEventListener("click", ask);
document.getElementById("reindexBtn").addEventListener("click", reindex);
document.querySelectorAll(".rate").forEach((btn) => {
  btn.addEventListener("click", () => submitFeedback(Number(btn.dataset.rating)));
});
