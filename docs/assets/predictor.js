(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const form = $("predict-form");
  const dateInput = $("as-of-date");
  const predictButton = $("predict-button");
  const inputError = $("input-error");
  const resultSection = $("result-section");
  let apiBaseUrl = "";
  const originalButtonLabel = predictButton.innerHTML;

  function showInputError(message) {
    inputError.textContent = message;
    inputError.hidden = false;
  }
  function clearInputError() {
    inputError.textContent = "";
    inputError.hidden = true;
  }
  function formatDate(value) {
    if (!value) return "—";
    const parts = value.split("-");
    if (parts.length !== 3) return value;
    const dt = new Date(Date.UTC(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2])));
    return new Intl.DateTimeFormat("en-IN", {day:"2-digit", month:"short", year:"numeric", timeZone:"UTC"}).format(dt);
  }
  function parseInputDate(value) {
    const text = String(value || "").trim();
    let match;
    if ((match = /^(\d{4})-(\d{1,2})-(\d{1,2})$/.exec(text))) {
      const year = Number(match[1]), month = Number(match[2]), day = Number(match[3]);
      const dt = new Date(Date.UTC(year, month - 1, day));
      if (dt.getUTCFullYear() !== year || dt.getUTCMonth() !== month - 1 || dt.getUTCDate() !== day) return null;
      return year + "-" + String(month).padStart(2, "0") + "-" + String(day).padStart(2, "0");
    }
    if ((match = /^(\d{1,2})[\/.-](\d{1,2})[\/.-](\d{4})$/.exec(text))) {
      const day = Number(match[1]), month = Number(match[2]), year = Number(match[3]);
      const dt = new Date(Date.UTC(year, month - 1, day));
      if (dt.getUTCFullYear() !== year || dt.getUTCMonth() !== month - 1 || dt.getUTCDate() !== day) return null;
      return year + "-" + String(month).padStart(2, "0") + "-" + String(day).padStart(2, "0");
    }
    return null;
  }
  function formatPercent(value) {
    return typeof value === "number" && Number.isFinite(value) ? (value * 100).toFixed(1) + "%" : "—";
  }
  function setPageStatus(text, statusClass) {
    const element = $("page-status");
    element.className = "status-pill " + statusClass;
    element.textContent = text;
  }
  async function responseJson(response) {
    let body = {};
    try { body = await response.json(); } catch (_) {}
    if (!response.ok) {
      const detail = body.detail || body.error || ("HTTP " + response.status);
      throw new Error(typeof detail === "string" ? detail : "The live API request failed.");
    }
    return body;
  }
  function renderPrediction(record) {
    const isUp = record.direction === "UP";
    $("forecast-kind").textContent = "Fresh point-in-time inference from Dhan data";
    $("result-date").textContent = "Anchor: " + formatDate(record.as_of_date) + " · " + (record.as_of_time_ist || "10:00 IST");
    $("direction-symbol").textContent = isUp ? "↗" : "↘";
    $("direction-symbol").classList.toggle("down", !isUp);
    $("direction-value").textContent = record.direction;
    $("direction-value").classList.toggle("down", !isUp);
    $("direction-description").textContent = isUp
      ? "ExtraTrees classifies the NIFTY 50 spot close at the target expiry as higher than the selected 10:00 anchor."
      : "ExtraTrees classifies the NIFTY 50 spot close at the target expiry as lower than the selected 10:00 anchor.";
    $("target-expiry").textContent = formatDate(record.target_expiry_date);
    $("p-up").textContent = formatPercent(record.p_up);
    $("train-count").textContent = Number.isFinite(record.training_rows) ? String(record.training_rows) : "—";
    $("train-through").textContent = formatDate(record.trained_through_expiry_date);
    $("anchor-price").textContent = Number.isFinite(record.anchor_price)
      ? record.anchor_price.toLocaleString("en-IN", {maximumFractionDigits:2}) : "—";
    $("bars-used").textContent = Number.isFinite(record.bars_used) ? record.bars_used.toLocaleString("en-IN") : "—";
    const gate = record.data_quality || {};
    $("gate-status").textContent = gate.status || "BLOCKED";
    $("gate-description").textContent = (gate.detail || "Independent source validation is incomplete.") +
      " The output is exploratory, not cleared for trading.";
    $("generated-at").textContent = "Computed " + new Intl.DateTimeFormat("en-IN", {
      dateStyle:"medium", timeStyle:"short", timeZone:"Asia/Kolkata"
    }).format(new Date(record.generated_at_utc || Date.now())) +
      " IST. Dhan token refreshed for this request; ExtraTrees refitted. Older minute-data chunks may be reused from the backend cache.";
    const targetDate = record.target_expiry_date ? new Date(record.target_expiry_date + "T00:00:00Z") : null;
    const today = new Date();
    today.setUTCHours(0, 0, 0, 0);
    const notes = [];
    if (targetDate && targetDate < today) notes.push("This is a historical point-in-time forecast, not a current signal.");
    if (record.note) notes.push(record.note);
    $("expiry-note").textContent = notes.join(" ");
    $("expiry-note").hidden = notes.length === 0;
    resultSection.hidden = false;
  }
  async function runPrediction(asOfDate) {
    const response = await fetch(apiBaseUrl + "/predict", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({as_of_date:asOfDate})
    });
    const queued = await responseJson(response);
    if (!queued.job_id) throw new Error("The live service did not return a prediction job ID.");
    setPageStatus("Refreshing Dhan data and fitting ExtraTrees", "status-loading");
    for (let attempt = 0; attempt < 360; attempt += 1) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      const poll = await fetch(apiBaseUrl + "/jobs/" + encodeURIComponent(queued.job_id), {cache:"no-store"});
      const job = await responseJson(poll);
      if (job.status === "succeeded" && job.result) {
        renderPrediction(job.result);
        setPageStatus("Live prediction complete", "status-ready");
        return;
      }
      if (job.status === "failed") throw new Error(job.error || "Dhan inference failed. Check the date and retry.");
      setPageStatus(job.status === "queued" ? "Live prediction queued" : "Fetching history and training model", "status-loading");
    }
    throw new Error("The live request is taking too long. Check the API deployment status before retrying.");
  }
  async function initialize() {
    predictButton.disabled = true;
    try {
      const configResponse = await fetch("./assets/live-api-config.json?ts=" + Date.now(), {cache:"no-store"});
      const config = await responseJson(configResponse);
      apiBaseUrl = String(config.api_base_url || "").replace(/\/+$/, "");
      if (!apiBaseUrl) {
        setPageStatus("Live API not deployed", "status-blocked");
        showInputError("The secure Dhan inference service has not published its endpoint yet. Check the 'Deploy Live Dhan ExtraTrees API' workflow.");
        $("generated-at").textContent = "Waiting for secure backend deployment; Dhan credentials are not stored in this page.";
        return;
      }
      const health = await responseJson(await fetch(apiBaseUrl + "/health", {cache:"no-store"}));
      if (health.status !== "ready") {
        setPageStatus("Dhan API needs setup", "status-blocked");
        showInputError("The service is reachable but Dhan credentials are not configured. Check backend deployment secrets.");
        $("generated-at").textContent = "Live API endpoint: " + apiBaseUrl;
        return;
      }
      setPageStatus("Live Dhan API ready", "status-ready");
      $("generated-at").textContent = "Ready: Predict refreshes Dhan authentication, obtains the selected cutoff's minute data, and refits ExtraTrees on the server.";
      predictButton.disabled = false;
    } catch (error) {
      setPageStatus("Live API unavailable", "status-blocked");
      showInputError(error && error.message ? error.message : "Could not connect to the secure live API.");
      $("generated-at").textContent = "The page cannot reach its secure Dhan inference service.";
    }
  }
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearInputError();
    resultSection.hidden = true;
    const asOfDate = parseInputDate(dateInput.value);
    if (!asOfDate) {
      showInputError("Enter a valid date as YYYY-MM-DD or DD/MM/YYYY, for example 2024-05-10.");
      dateInput.focus();
      return;
    }
    if (!apiBaseUrl) {
      showInputError("The secure live Dhan API is not configured yet. Check the deployment workflow.");
      return;
    }
    predictButton.disabled = true;
    predictButton.textContent = "Running…";
    setPageStatus("Starting live prediction", "status-loading");
    try {
      await runPrediction(asOfDate);
    } catch (error) {
      setPageStatus("Prediction failed", "status-blocked");
      showInputError(error && error.message ? error.message : "Live prediction failed. Please retry.");
    } finally {
      predictButton.disabled = false;
      predictButton.innerHTML = originalButtonLabel;
    }
  });
  initialize();
})();