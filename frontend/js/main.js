(function () {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const fileNameEl = document.getElementById("file-name");
  const continueBtn = document.getElementById("continue-btn");
  const backToUploadBtn = document.getElementById("back-to-upload-btn");
  const backToCriteriaBtn = document.getElementById("back-to-criteria-btn");
  const generateBtn = document.getElementById("generate-btn");
  const newReviewBtn = document.getElementById("new-review-btn");
  const errorBanner = document.getElementById("error-banner");
  const downloadMdBtn = document.getElementById("download-md");
  const downloadJsonBtn = document.getElementById("download-json");
  const selectAllBtn = document.getElementById("select-all");
  const selectNoneBtn = document.getElementById("select-none");
  const stepper = document.getElementById("stepper");

  let criteria = [];
  let selectedFile = null;
  let reviewData = null;
  let currentStep = 1;
  let highestReachedStep = 1;

  function showError(message) {
    errorBanner.textContent = message;
    errorBanner.hidden = false;
  }

  function clearError() {
    errorBanner.hidden = true;
    errorBanner.textContent = "";
  }

  function goToStep(n) {
    currentStep = n;
    highestReachedStep = Math.max(highestReachedStep, n);

    document.querySelectorAll(".step").forEach((el) => {
      el.classList.toggle("step--active", Number(el.dataset.step) === n);
    });

    stepper.querySelectorAll(".vstepper__item").forEach((el) => {
      const stepNum = Number(el.dataset.step);
      el.classList.toggle("vstepper__item--active", stepNum === n);
      el.classList.toggle("vstepper__item--done", stepNum < highestReachedStep);
      el.querySelector(".vstepper__button").disabled = stepNum >= highestReachedStep && stepNum !== n;
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  stepper.querySelectorAll(".vstepper__item").forEach((el) => {
    const stepNum = Number(el.dataset.step);
    el.querySelector(".vstepper__button").addEventListener("click", () => {
      if (stepNum < highestReachedStep || stepNum === currentStep) {
        clearError();
        goToStep(stepNum);
      }
    });
  });

  function refreshGenerateEnabled() {
    generateBtn.disabled = getSelectedRubrics().length === 0;
  }

  function selectFile(file) {
    selectedFile = file;
    fileNameEl.textContent = file.name;
    fileNameEl.title = file.name;
    fileNameEl.hidden = false;
    clearError();
    continueBtn.disabled = false;
  }

  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.classList.add("dropzone--active");
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.classList.remove("dropzone--active");
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.classList.remove("dropzone--active");
    const file = e.dataTransfer.files[0];
    if (file) selectFile(file);
  });

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) selectFile(fileInput.files[0]);
  });

  continueBtn.addEventListener("click", () => {
    if (!selectedFile) return;
    goToStep(2);
  });

  backToUploadBtn.addEventListener("click", () => goToStep(1));
  backToCriteriaBtn.addEventListener("click", () => {
    clearError();
    backToCriteriaBtn.hidden = true;
    goToStep(2);
  });

  selectAllBtn.addEventListener("click", () => {
    setAllRubrics(true);
    refreshGenerateEnabled();
  });

  selectNoneBtn.addEventListener("click", () => {
    setAllRubrics(false);
    refreshGenerateEnabled();
  });

  document.getElementById("rubric-list").addEventListener("change", refreshGenerateEnabled);

  function renderResults() {
    renderPaperHeader(reviewData);
    renderSummary(reviewData);
    renderTabs(criteria, reviewData, true, true);
  }

  generateBtn.addEventListener("click", async () => {
    if (!selectedFile) return;
    const selectedKeys = getSelectedRubrics();
    if (selectedKeys.length === 0) return;

    clearError();
    backToCriteriaBtn.hidden = true;
    renderProgressList(selectedKeys);
    goToStep(3);

    try {
      await submitPaperStream(selectedFile, selectedKeys, (event) => {
        switch (event.stage) {
          case "queued":
            event.rubrics.forEach((key) => setProgressItemStatus(key, "running", "Reviewing…"));
            break;
          case "agent_done":
            setProgressItemStatus(event.key, "done", `Score ${event.result.score}/10`);
            break;
          case "agent_error":
            setProgressItemStatus(event.key, "error", "Failed");
            break;
          case "synthesizing":
            break;
          case "complete":
            reviewData = event.result;
            renderResults();
            goToStep(4);
            break;
          case "error":
            showError(event.message || "Something went wrong while generating the review.");
            backToCriteriaBtn.hidden = false;
            break;
        }
      });
    } catch (err) {
      showError(err.message || "Something went wrong while generating the review.");
      backToCriteriaBtn.hidden = false;
    }
  });

  newReviewBtn.addEventListener("click", () => {
    selectedFile = null;
    reviewData = null;
    fileInput.value = "";
    fileNameEl.hidden = true;
    continueBtn.disabled = true;
    setAllRubrics(true);
    refreshGenerateEnabled();
    clearError();
    highestReachedStep = 1;
    goToStep(1);
  });

  downloadMdBtn.addEventListener("click", () => {
    if (!reviewData) return;
    const md = buildMarkdownExport(
      criteria,
      reviewData.title || "Unknown Title",
      reviewData.reviews,
      reviewData.overall_score,
      reviewData.recommendation,
      reviewData.meta_summary
    );
    downloadTextFile("review.md", "text/markdown", md);
  });

  downloadJsonBtn.addEventListener("click", () => {
    if (!reviewData) return;
    const json = buildJsonExport(
      reviewData.title,
      reviewData.abstract,
      reviewData.overall_score,
      reviewData.recommendation,
      reviewData.reviews,
      reviewData.meta_summary
    );
    downloadTextFile("review.json", "application/json", json);
  });

  async function init() {
    goToStep(1);
    try {
      criteria = await fetchCriteria();
      renderRubricPicker(criteria);
      refreshGenerateEnabled();
    } catch (err) {
      showError("Could not reach the backend API. Is it running?");
    }
  }

  init();
})();
