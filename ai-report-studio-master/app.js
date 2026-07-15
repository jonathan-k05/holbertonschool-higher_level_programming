// AI Report Studio front-end controller.
// Talks to the FastAPI backend running on http://localhost:8000.
(function () {
  "use strict";

  const API_BASE = "http://localhost:8000";

  class AIReportStudio {
    constructor() {
      this.datasetId = null;
      this.reportId = null;

      this.fileInput = document.getElementById("fileInput");
      this.uploadBtn = document.getElementById("uploadBtn");
      this.uploadStatus = document.getElementById("uploadStatus");

      this.templateSection = document.getElementById("templateSection");
      this.templateSelect = document.getElementById("templateSelect");
      this.generateBtn = document.getElementById("generateBtn");
      this.templateStatus = document.getElementById("templateStatus");

      this.reportSection = document.getElementById("reportSection");
      this.reportStatus = document.getElementById("reportStatus");
      this.reportContent = document.getElementById("reportContent");

      this._bindEvents();
    }

    _bindEvents() {
      this.uploadBtn.addEventListener("click", () => this.uploadDataset());
      this.generateBtn.addEventListener("click", () => this.generateReport());
    }

    // Helper: render a message into a status div.
    // kind is "error", "success", or undefined (neutral).
    _setStatus(el, message, kind) {
      if (!el) return;
      el.textContent = message || "";
      el.className = "status" + (kind ? " " + kind : "");
    }

    _show(el) {
      if (el) el.classList.remove("hidden");
    }

    _hide(el) {
      if (el) el.classList.add("hidden");
    }

    _setBusy(button, busy, label) {
      if (!button) return;
      button.disabled = busy;
      if (label !== undefined) button.textContent = label;
    }

    async uploadDataset() {
      const file = this.fileInput.files && this.fileInput.files[0];
      if (!file) {
        this._setStatus(this.uploadStatus, "Please choose a CSV or JSON file first.", "error");
        return;
      }

      this._setStatus(this.uploadStatus, "Uploading…");
      this._setBusy(this.uploadBtn, true, "Uploading…");

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE}/datasets`, {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          const detail = await this._extractError(response);
          throw new Error(detail || "Upload failed. Please try again.");
        }

        const data = await response.json();
        this.datasetId = data.id;
        this._setStatus(
          this.uploadStatus,
          `Uploaded "${data.filename}" (${data.row_count} rows). Now choose a template below.`,
          "success"
        );

        this._show(this.templateSection);
        await this.loadTemplates();
      } catch (err) {
        this._setStatus(this.uploadStatus, this._friendlyError(err, "uploading your file"), "error");
      } finally {
        this._setBusy(this.uploadBtn, false, "Upload");
      }
    }

    async loadTemplates() {
      this._setStatus(this.templateStatus, "");
      try {
        const response = await fetch(`${API_BASE}/templates`);
        if (!response.ok) {
          const detail = await this._extractError(response);
          throw new Error(detail || "Could not load templates.");
        }

        const data = await response.json();
        const templates = Array.isArray(data.templates) ? data.templates : [];

        this.templateSelect.innerHTML = "";
        if (templates.length === 0) {
          const option = document.createElement("option");
          option.value = "";
          option.textContent = "No templates available";
          this.templateSelect.appendChild(option);
          this.templateSelect.disabled = true;
          this.generateBtn.disabled = true;
          return;
        }

        this.templateSelect.disabled = false;
        this.generateBtn.disabled = false;
        templates.forEach((tpl) => {
          const option = document.createElement("option");
          option.value = tpl.name;
          option.textContent = tpl.name;
          this.templateSelect.appendChild(option);
        });
      } catch (err) {
        this._setStatus(
          this.templateStatus,
          this._friendlyError(err, "loading templates"),
          "error"
        );
      }
    }

    async generateReport() {
      const templateName = this.templateSelect.value;
      if (!this.datasetId) {
        this._setStatus(this.templateStatus, "Please upload a dataset first.", "error");
        return;
      }
      if (!templateName) {
        this._setStatus(this.templateStatus, "Please choose a template.", "error");
        return;
      }

      this._setStatus(this.templateStatus, "Generating report…");
      this._setBusy(this.generateBtn, true, "Generating…");

      try {
        const response = await fetch(`${API_BASE}/reports`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            dataset_id: this.datasetId,
            template_name: templateName,
          }),
        });

        if (!response.ok) {
          const detail = await this._extractError(response);
          throw new Error(detail || "Report generation failed.");
        }

        const report = await response.json();
        this.reportId = report.id;
        this.reportContent.textContent = report.content || "";
        this._setStatus(this.reportStatus, "Report ready. Use the buttons below to export.", "success");
        this._show(this.reportSection);
      } catch (err) {
        this._setStatus(
          this.templateStatus,
          this._friendlyError(err, "generating the report"),
          "error"
        );
      } finally {
        this._setBusy(this.generateBtn, false, "Generate");
      }
    }

    async exportReport(format) {
      if (!this.reportId) {
        this._setStatus(this.reportStatus, "No report available to export yet.", "error");
        return;
      }
      this._setStatus(this.reportStatus, `Preparing ${format.toUpperCase()} download…`);

      try {
        const response = await fetch(
          `${API_BASE}/reports/${this.reportId}/export?format=${encodeURIComponent(format)}`
        );
        if (!response.ok) {
          const detail = await this._extractError(response);
          throw new Error(detail || "Export failed.");
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = `report_${this.reportId}.${format === "md" ? "md" : "html"}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this._setStatus(this.reportStatus, `Downloaded ${format.toUpperCase()} report.`, "success");
      } catch (err) {
        this._setStatus(
          this.reportStatus,
          this._friendlyError(err, `exporting the ${format.toUpperCase()} report`),
          "error"
        );
      }
    }

    // Best-effort extraction of an error message from a Response body.
    async _extractError(response) {
      try {
        const body = await response.json();
        if (body && typeof body.detail === "string") return body.detail;
      } catch (_ignore) {
        // ignore — fall through to generic handling
      }
      return null;
    }

    // Turn any thrown error into a friendly, non-technical message.
    _friendlyError(err, action) {
      const raw = (err && err.message) || "";
      if (raw) return `Sorry, there was a problem ${action}: ${raw}`;
      return `Sorry, there was a problem ${action}. Please check your connection and try again.`;
    }
  }

  function init() {
    const studio = new AIReportStudio();
    window.aiReportStudio = studio;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
