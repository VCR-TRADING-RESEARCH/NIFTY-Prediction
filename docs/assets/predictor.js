(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const form = $("predict-form");
  const dateInput = $("as-of-date");
  const predictButton = $("predict-button");
  const inputError = $("input-error");
  const resultSection = $("result-section");

  let payload = null;
  let availablePredictions = [];

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
    const dt = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    return new Intl.DateTimeFormat("en-IN", {
      day: "2-digit", month: "short", year: "numeric"
    }).format(dt);
  }

  function parseInputDate(value) {
    const match = /^\\s*(\\d{1,2})[\\/.-](\\d{1,2})[\\/.-](\\d{4})\\s*$/.exec(value || "");
    if (!match) return null;
    const day = Number(match[1]), month = Number(match[2]), year = Number(match[3]);
    const date = new Date(Date.UTC(year, month - 1, day));
    if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
    return year + "-" + String(month).padStart(2, "0") + "-" + String(day).padStart(2, "0");
  }

  function displayDateInput(isoDate) {
    const parts = isoDate.split("-");
    return parts.length === 3 ? parts[2] + "/" + parts[1] + "/" + parts[0] : isoDate;
  }

  function formatPercent(value) {
    if (typeof value !== "number" || !Number.isFinite(value)) return "—";
    return (value * 100).toFixed(1) + "%";
  }

  function setPageStatus(text, statusClass) {
    const element = $("page-status");
    element.className = "status-pill " + statusClass;
    element.innerHTML = '<span class="status-dot"></span>' + text;
  }

  function choosePrediction(date) {
    if (payload && payload.latest_forecast && payload.latest_forecast.as_of_date === date) {
      return payload.latest_forecast;
    }
    return availablePredictions.find((record) => record.as_of_date === date) || null;
  }

  function renderPrediction(record) {
    const isLatest = record.prediction_kind === "LATEST_FORWARD_FORECAST";
    const direction = record.direction;
    const isUp = direction === "UP";
    $("forecast-kind").textContent = isLatest
      ? "Forward forecast for the next scheduled expiry"
      : "Historical out-of-sample forecast";
    $("result-date").textContent = "Anchor: " + formatDate(record.as_of_date) + " · " + (record.as_of_time_ist || "10:00 IST");
    $("direction-symbol").textContent = isUp ? "↗" : "↘";
    $("direction-symbol").classList.toggle("down", !isUp);
    $("direction-value").textContent = direction;
    $("direction-value").classList.toggle("down", !isUp);
    $("direction-description").textContent = isUp
      ? "The model classifies the NIFTY spot expiry close as higher than the 10:00 anchor."
      : "The model classifies the NIFTY spot expiry close as lower than the 10:00 anchor.";
    $("target-expiry").textContent = formatDate(record.target_expiry_date);
    $("p-up").textContent = formatPercent(record.p_up);
    $("train-count").textContent = Number.isFinite(record.training_rows) ? String(record.training_rows) : "—";
    $("train-through").textContent = formatDate(record.trained_through_expiry_date);

    const expiryNote = $("expiry-note");
    const notes = [];
    if (isLatest && record.target_calendar_status) {
      notes.push("Expiry calendar: " + record.target_calendar_status.replaceAll("_", " ").toLowerCase() + ".");
      notes.push("Confirm the actual contract expiry date with NSE before using this forecast.");
    }
    const targetDate = record.target_expiry_date ? new Date(record.target_expiry_date + "T00:00:00") : null;
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (targetDate && targetDate < today) {
      notes.push("This target expiry is in the past; this is a historical forecast, not a current signal.");
    }
    expiryNote.textContent = notes.join(" ");
    expiryNote.hidden = notes.length === 0;
    resultSection.hidden = false;
  }

  function handlePrediction(date) {
    clearInputError();
    const normalizedDate = parseInputDate(date);\n    if (!normalizedDate) {\n      showInputError("Enter a valid date as DD/MM/YYYY, for example 21/10/2026.");\n      resultSection.hidden = true;\n      return;\n    }\n    const record = choosePrediction(normalizedDate);
    if (!record) {
      const sorted = availablePredictions.map((item) => item.as_of_date).sort();
      const nearestBefore = sorted.filter((value) => value < date).pop();
      const nearestAfter = sorted.find((value) => value > date);
      let hint = "No saved forecast exists for this date. The model is defined for the first session after the previous expiry, using the first eligible 10:00–10:03 IST minute bar.";
      if (nearestBefore || nearestAfter) {
        hint += " Available nearby anchor dates: " +
          (nearestBefore ? formatDate(nearestBefore) : "") +
          (nearestBefore && nearestAfter ? " or " : "") +
          (nearestAfter ? formatDate(nearestAfter) : "") + ".";
      }
      showInputError(hint);
      resultSection.hidden = true;
      return;
    }
    renderPrediction(record);
  }

  async function initialize() {
    try {
      const response = await fetch("./data/extra_trees_forecasts.json", { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Forecast data file is not available yet (HTTP " + response.status + ").");
      }
      payload = await response.json();
      if (!Array.isArray(payload.historical_predictions)) payload.historical_predictions = [];
      availablePredictions = payload.historical_predictions;
      const dates = availablePredictions.map((record) => record.as_of_date);
      if (payload.latest_forecast && payload.latest_forecast.as_of_date) {
        dates.push(payload.latest_forecast.as_of_date);
      }
      const uniqueDates = Array.from(new Set(dates)).sort();
      if (!uniqueDates.length) {
        throw new Error(payload.latest_forecast_error || "No eligible forecasts have been generated yet.");
      }

      dateInput.min = uniqueDates[0];
      dateInput.max = uniqueDates[uniqueDates.length - 1];
      dateInput.value = payload.latest_forecast && payload.latest_forecast.as_of_date
        ? payload.latest_forecast.as_of_date
        : uniqueDates[uniqueDates.length - 1];
      predictButton.disabled = false;
      setPageStatus(payload.latest_forecast ? "Forecast record ready" : "Historical records ready", "status-ready");

      const gate = payload.data_quality || {};
      $("gate-status").textContent = gate.status || "BLOCKED";
      $("gate-description").textContent =
        (gate.detail || "Source and anchor validation is incomplete.") +
        (Number.isFinite(gate.close_mismatches_over_1_point)
          ? " Independent comparison: " + gate.close_mismatches_over_1_point + " of " +
            gate.sessions_compared + " daily closes differed from official closes by more than one point."
          : "") +
        " The forecast remains exploratory and is not cleared for trading.";

      if (payload.generated_at_utc) {
        const dt = new Date(payload.generated_at_utc);
        $("generated-at").textContent = "Prediction data generated " +
          new Intl.DateTimeFormat("en-IN", { dateStyle: "medium", timeStyle: "short", timeZone: "Asia/Kolkata" }).format(dt) +
          " IST. The site does not run a Python model in the browser; predictions are produced by the repository workflow.";
      } else {
        $("generated-at").textContent = "Forecast data loaded. Predictions are generated by the repository's Python workflow.";
      }

      if (payload.latest_forecast_error) {
        $("gate-description").textContent += " Latest forward forecast unavailable: " + payload.latest_forecast_error;
      }
    } catch (error) {
      setPageStatus("Forecast data unavailable", "status-blocked");
      showInputError(error && error.message ? error.message : "Unable to load prediction data.");
      $("generated-at").textContent = "Forecast data could not be loaded. Check the repository workflow and data-quality logs.";
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    handlePrediction(dateInput.value);
  });

  initialize();
})();
