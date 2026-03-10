(() => {
    // State
    let uploadedFilename = null;
    let selectedView = "isometric";
    let selectedStyle = "technical";
    let selectedFormat = "png";

    // Elements
    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const fileStatus = document.getElementById("fileStatus");
    const generateBtn = document.getElementById("generateBtn");
    const btnText = document.getElementById("btnText");
    const btnLoader = document.getElementById("btnLoader");
    const outputCard = document.getElementById("outputCard");
    const previewImg = document.getElementById("previewImg");
    const downloadBtn = document.getElementById("downloadBtn");
    const errorBanner = document.getElementById("errorBanner");
    const regenerateBtn = document.getElementById("regenerateBtn");
    const titleInput = document.getElementById("titleInput");
    const calloutInput = document.getElementById("calloutInput");

    // Chip groups
    setupChips("viewGroup", (v) => { selectedView = v; });
    setupChips("styleGroup", (v) => { selectedStyle = v; });
    setupChips("formatGroup", (v) => { selectedFormat = v; });

    function setupChips(groupId, onChange) {
        const group = document.getElementById(groupId);
        group.querySelectorAll(".chip").forEach(chip => {
            chip.addEventListener("click", () => {
                group.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
                chip.classList.add("active");
                onChange(chip.dataset.value);
            });
        });
    }

    // Drag & drop
    dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragging"); });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragging"));
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragging");
        const file = e.dataTransfer.files[0];
        if (file) handleFile(file);
    });
    dropZone.addEventListener("click", (e) => {
        if (e.target.tagName !== "LABEL" && e.target.tagName !== "INPUT") {
            fileInput.click();
        }
    });
    fileInput.addEventListener("change", () => {
        if (fileInput.files[0]) handleFile(fileInput.files[0]);
    });

    async function handleFile(file) {
        const ext = file.name.split(".").pop().toLowerCase();
        if (!["step", "stp"].includes(ext)) {
            showError("❌ Invalid file type. Please upload a .step or .stp file.");
            return;
        }

        fileStatus.textContent = `⏳ Uploading "${file.name}"…`;
        hideError();

        const formData = new FormData();
        formData.append("file", file);

        try {
            const res = await fetch("/upload", { method: "POST", body: formData });
            const data = await res.json();
            if (!res.ok || data.error) throw new Error(data.error || "Upload failed");
            uploadedFilename = data.filename;
            fileStatus.textContent = `✅ "${data.original_name}" uploaded successfully`;
            generateBtn.disabled = false;
        } catch (err) {
            showError(`Upload failed: ${err.message}`);
            fileStatus.textContent = "";
        }
    }

    // Generate
    generateBtn.addEventListener("click", async () => {
        if (!uploadedFilename) return;

        setLoading(true);
        outputCard.classList.add("hidden");
        hideError();

        const payload = {
            filename: uploadedFilename,
            view: selectedView,
            format: selectedFormat,
            style: selectedStyle,
            title: titleInput.value.trim() || "Technical Illustration",
            callout: calloutInput.value.trim(),
        };

        try {
            const res = await fetch("/process", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            const data = await res.json();
            if (!res.ok || data.error) throw new Error(data.error || "Processing failed");

            // Show preview
            const ts = Date.now();
            previewImg.src = `${data.preview_url}?t=${ts}`;
            downloadBtn.href = data.download_url;
            downloadBtn.download = data.output_file;
            outputCard.classList.remove("hidden");
            outputCard.scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (err) {
            showError(`❌ Error: ${err.message}`);
        } finally {
            setLoading(false);
        }
    });

    // Regenerate
    regenerateBtn.addEventListener("click", () => {
        outputCard.classList.add("hidden");
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    function setLoading(loading) {
        generateBtn.disabled = loading;
        btnText.textContent = loading ? "Generating…" : "Generate Illustration";
        btnLoader.classList.toggle("hidden", !loading);
    }

    function showError(msg) {
        errorBanner.textContent = msg;
        errorBanner.classList.remove("hidden");
    }
    function hideError() {
        errorBanner.classList.add("hidden");
        errorBanner.textContent = "";
    }
})();
