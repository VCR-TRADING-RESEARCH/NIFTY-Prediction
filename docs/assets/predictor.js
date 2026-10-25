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
  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  async function runPrediction(asOfDate) {
    if (!apiBaseUrl) throw new Error("Secure prediction service is not configured yet. Please retry after deployment.");
    const response = await fetch(apiBaseUrl + "/predict", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({as_of_date: asOfDate})
    });
    const job = await responseJson(response);
    if (!job.job_id) throw new Error("The prediction service did not return a job ID.");
    setPageStatus("Python model running", "status-loading");
    for (let attempt = 0; attempt < 360; attempt += 1) {
      await delay(3000);
      const statusResponse = await fetch(apiBaseUrl + "/jobs/" + encodeURIComponent(job.job_id), {cache:"no-store"});
      const status = await responseJson(statusResponse);
      if (status.status === "succeeded" && status.result) {
        renderPrediction(status.result);
        setPageStatus("Live prediction complete", "status-ready");
        return;
      }
      if (status.status === "failed") throw new Error(status.error || "The prediction failed its data/model checks.");
    }
    throw new Error("Prediction is taking too long. Please retry; no old forecast was substituted.");
  }
  async function initialize() {
    setPageStatus("Checking secure prediction service", "status-loading");
    $("generated-at").textContent = "Checking whether the secure Python inference service is available.";
    try {
      const configResponse = await fetch("./assets/live-api-config.json?ts=" + Date.now(), {cache:"no-store"});
      if (!configResponse.ok) throw new Error("Could not load the live-service configuration.");
      const config = await configResponse.json();
      apiBaseUrl = typeof config.api_base_url === "string" ? config.api_base_url.replace(/\\/$/, "") : "";
      if (!apiBaseUrl || !/^https:\\/\\//i.test(apiBaseUrl)) {
        predictButton.disabled = true;
        setPageStatus("Secure service not deployed", "status-blocked");
        showInputError("One-click prediction is not active yet because the secure Python service has not been deployed. This page will not ask you to submit a GitHub issue or expose credentials.");
        $("generated-at").textContent = "Deployment is pending. Dhan credentials must remain server-side.";
      } else {
        const healthResponse = await fetch(apiBaseUrl + "/health", {cache:"no-store"});
        const health = await responseJson(healthResponse);
        if (health.status !== "ready") throw new Error("The secure service is online but Dhan credentials are not fully configured.");
        predictButton.disabled = false;
        setPageStatus("Live prediction ready", "status-ready");
        $("generated-at").textContent = "Predict calls the secure Python service directly. Dhan credentials stay server-side; the model is refit for each request.";
      }
    } catch (error) {
      predictButton.disabled = true;
      setPageStatus("Secure service unavailable", "status-blocked");
      showInputError(error && error.message ? error.message : "The secure prediction service could not be reached.");
      $("generated-at").textContent = "Live prediction is unavailable until the secure Python service is deployed and healthy.";
    }
    const requestedDate = parseInputDate(new URLSearchParams(window.location.search).get("as_of_date"));
    if (requestedDate) dateInput.value = requestedDate;
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
    predictButton.disabled = true;
    predictButton.textContent = "Running…";
    setPageStatus("Starting Python inference", "status-loading");
    try {
      await runPrediction(asOfDate);
    } catch (error) {
      setPageStatus("Prediction not confirmed", "status-blocked");
      showInputError(error && error.message ? error.message : "Could not retrieve the new prediction.");
    } finally {
      predictButton.disabled = false;
      predictButton.innerHTML = originalButtonLabel;
      predictButton.disabled = !apiBaseUrl;
    }
  });
  initialize();
})();
