document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("mediahubModal");
    const closeModalBtn = document.getElementById("mhCloseModal");
    const searchInput = document.getElementById("mhSearchInput");
    const kindFilter = document.getElementById("mhKindFilter");
    const searchBtn = document.getElementById("mhSearchBtn");
    const uploadBtn = document.getElementById("mhUploadBtn");
    const fileInput = document.getElementById("mhFileInput");
    const dropzone = document.getElementById("mhDropzone");
    const grid = document.getElementById("mhGrid");
    const pagination = document.getElementById("mhPagination");
    const messages = document.getElementById("mhMessages");

    const preview = document.getElementById("mhPreview");
    const titleInput = document.getElementById("mhTitleInput");
    const nameInput = document.getElementById("mhNameInput");
    const kindInput = document.getElementById("mhKindInput");
    const mimeInput = document.getElementById("mhMimeInput");
    const extensionInput = document.getElementById("mhExtensionInput");
    const sizeInput = document.getElementById("mhSizeInput");
    const dimensionsInput = document.getElementById("mhDimensionsInput");
    const createdInput = document.getElementById("mhCreatedInput");
    const urlInput = document.getElementById("mhUrlInput");
    const copyBtn = document.getElementById("mhCopyBtn");
    const saveBtn = document.getElementById("mhSaveBtn");
    const deleteBtn = document.getElementById("mhDeleteBtn");
    const useBtn = document.getElementById("mhUseBtn");

    const showGalleryInput = document.getElementById("mhShowGalleryInput");
    const showNewsInput = document.getElementById("mhShowNewsInput");

    let currentPage = 1;
    let selectedItem = null;
    let targetFieldSelector = null;

    function getCSRFToken() {
        const tokenMeta = document.querySelector('meta[name="csrf-token"]');
        if (tokenMeta) {
            return tokenMeta.getAttribute("content");
        }

        const value = `; ${document.cookie}`;
        const parts = value.split(`; csrftoken=`);
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return "";
    }

    function formatBytes(bytes) {
        if (!bytes) return "0 B";
        const units = ["B", "KB", "MB", "GB"];
        let i = 0;
        let n = Number(bytes);
        while (n >= 1024 && i < units.length - 1) {
            n /= 1024;
            i++;
        }
        return `${n.toFixed(2)} ${units[i]}`;
    }

    function escapeHtml(text) {
        return String(text || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function showMessage(text, type = "success") {
        messages.innerHTML = `<div class="mh-message ${type}">${escapeHtml(text)}</div>`;
        setTimeout(() => {
            messages.innerHTML = "";
        }, 3500);
    }

    function openModal(targetSelector = null) {
        targetFieldSelector = targetSelector;
        modal.classList.add("is-open");
        modal.setAttribute("aria-hidden", "false");
        loadItems(1);
    }

    function closeModal() {
        modal.classList.remove("is-open");
        modal.setAttribute("aria-hidden", "true");
    }

    document.querySelectorAll(".open-mediahub").forEach(btn => {
        btn.addEventListener("click", function () {
            openModal(btn.dataset.target || null);
        });
    });

    closeModalBtn.addEventListener("click", closeModal);
    modal.querySelector(".mh-modal-backdrop").addEventListener("click", closeModal);

    searchBtn.addEventListener("click", function () {
        loadItems(1);
    });

    searchInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            loadItems(1);
        }
    });

    kindFilter.addEventListener("change", function () {
        loadItems(1);
    });

    uploadBtn.addEventListener("click", function () {
        fileInput.click();
    });

    fileInput.addEventListener("change", function () {
        if (fileInput.files.length) {
            uploadFiles(fileInput.files);
            fileInput.value = "";
        }
    });

    ["dragenter", "dragover"].forEach(eventName => {
        dropzone.addEventListener(eventName, function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.add("is-dragover");
        });
    });

    ["dragleave", "drop"].forEach(eventName => {
        dropzone.addEventListener(eventName, function (e) {
            e.preventDefault();
            e.stopPropagation();
            dropzone.classList.remove("is-dragover");
        });
    });

    dropzone.addEventListener("drop", function (e) {
        const files = e.dataTransfer.files;
        if (files.length) {
            uploadFiles(files);
        }
    });

    async function loadItems(page = 1) {
        currentPage = page;
        selectedItem = null;
        clearSidebar();

        const q = searchInput.value.trim();
        const kind = kindFilter.value.trim();

        const url = new URL(window.MEDIAHUB.urls.itemsJson, window.location.origin);
        url.searchParams.set("page", page);
        if (q) url.searchParams.set("q", q);
        if (kind) url.searchParams.set("kind", kind);

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (!response.ok || !data.ok) {
                showMessage(data.message || "Αποτυχία φόρτωσης.", "error");
                return;
            }

            renderGrid(data.items);
            renderPagination(data.pagination);
        } catch (error) {
            showMessage("Σφάλμα επικοινωνίας με τον server.", "error");
        }
    }

    function renderGrid(items) {
        if (!items.length) {
            grid.innerHTML = `<div class="mh-empty">Δεν βρέθηκαν αρχεία.</div>`;
            return;
        }

        grid.innerHTML = items.map(item => {
            const thumb = renderThumb(item);
            return `
                <div class="mh-card" data-id="${item.id}">
                    <div class="mh-thumb">${thumb}</div>
                    <div class="mh-card-name">${escapeHtml(item.title || item.name)}</div>
                    <div class="mh-card-meta">${escapeHtml(item.extension || "")} · ${escapeHtml(item.kind || "")}</div>
                </div>
            `;
        }).join("");

        grid.querySelectorAll(".mh-card").forEach((card, index) => {
            card.addEventListener("click", function () {
                const item = items[index];
                selectItem(item, card);
            });
        });
    }

    function renderThumb(item) {
        if (item.kind === "image") {
            return `<img src="${item.thumbnail_url || item.url}" alt="${escapeHtml(item.name)}">`;
        }

        if (item.is_pdf) {
            return `<div class="mh-file-icon">PDF</div>`;
        }

        if (item.is_docx) {
            return `<div class="mh-file-icon">DOCX</div>`;
        }

        return `<div class="mh-file-icon">FILE</div>`;
    }

    function selectItem(item, cardEl) {
        selectedItem = item;

        document.querySelectorAll(".mh-card").forEach(el => el.classList.remove("is-active"));
        if (cardEl) {
            cardEl.classList.add("is-active");
        }

        titleInput.value = item.title || "";
        nameInput.value = item.name || "";
        kindInput.value = item.kind || "";
        mimeInput.value = item.mime_type || "";
        extensionInput.value = item.extension || "";
        sizeInput.value = formatBytes(item.size || 0);
        dimensionsInput.value = item.dimensions || "";
        createdInput.value = item.created_at || "";
        urlInput.value = item.url || "";

        showGalleryInput.checked = !!item.show_gallery;
        showNewsInput.checked = !!item.show_news;

        renderPreview(item);
    }

    function renderPreview(item) {
        if (item.kind === "image") {
            preview.innerHTML = `<img src="${item.url}" alt="${escapeHtml(item.name)}">`;
            return;
        }

        if (item.is_pdf) {
            preview.innerHTML = `
                <iframe src="${item.url}"></iframe>
            `;
            return;
        }

        if (item.is_docx) {
            preview.innerHTML = `
                <div class="mh-preview-placeholder">
                    <strong>DOCX αρχείο</strong>
                    <p>${escapeHtml(item.name)}</p>
                    <p>Δεν υπάρχει native browser preview για όλα τα DOCX.</p>
                    <p><a href="${item.url}" target="_blank" rel="noopener noreferrer">Άνοιγμα / λήψη αρχείου</a></p>
                </div>
            `;
            return;
        }

        preview.innerHTML = `
            <div class="mh-preview-placeholder">
                <strong>${escapeHtml(item.name)}</strong>
                <p>Δεν υπάρχει διαθέσιμο preview για αυτόν τον τύπο.</p>
                <p><a href="${item.url}" target="_blank" rel="noopener noreferrer">Άνοιγμα / λήψη αρχείου</a></p>
            </div>
        `;
    }

    function clearSidebar() {
        preview.innerHTML = `<div class="mh-preview-placeholder">Επίλεξε ένα αρχείο για preview</div>`;
        titleInput.value = "";
        nameInput.value = "";
        kindInput.value = "";
        mimeInput.value = "";
        extensionInput.value = "";
        sizeInput.value = "";
        dimensionsInput.value = "";
        createdInput.value = "";
        urlInput.value = "";

        showGalleryInput.checked = false;
        showNewsInput.checked = false;
    }

    function renderPagination(p) {
        pagination.innerHTML = "";
        if (!p || p.num_pages <= 1) return;

        const fragment = document.createDocumentFragment();

        const prevBtn = document.createElement("button");
        prevBtn.className = "mh-page-btn";
        prevBtn.textContent = "‹";
        prevBtn.disabled = !p.has_previous;
        prevBtn.addEventListener("click", () => loadItems(p.current_page - 1));
        fragment.appendChild(prevBtn);

        const start = Math.max(1, p.current_page - 2);
        const end = Math.min(p.num_pages, p.current_page + 2);

        for (let i = start; i <= end; i++) {
            const btn = document.createElement("button");
            btn.className = "mh-page-btn" + (i === p.current_page ? " is-active" : "");
            btn.textContent = i;
            btn.addEventListener("click", () => loadItems(i));
            fragment.appendChild(btn);
        }

        const nextBtn = document.createElement("button");
        nextBtn.className = "mh-page-btn";
        nextBtn.textContent = "›";
        nextBtn.disabled = !p.has_next;
        nextBtn.addEventListener("click", () => loadItems(p.current_page + 1));
        fragment.appendChild(nextBtn);

        pagination.appendChild(fragment);
    }

    async function uploadFiles(files) {
        const formData = new FormData();
        for (const file of files) {
            formData.append("files", file);
        }

        try {
            const response = await fetch(window.MEDIAHUB.urls.upload, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });

            const data = await response.json();

            if (!response.ok || !data.ok) {
                showMessage(data.message || "Αποτυχία upload.", "error");
                return;
            }

            if (data.errors && data.errors.length) {
                showMessage(data.errors.join(" | "), "error");
            } else {
                showMessage("Το upload ολοκληρώθηκε.");
            }

            loadItems(1);
        } catch (error) {
            showMessage("Σφάλμα upload.", "error");
        }
    }

    copyBtn.addEventListener("click", async function () {
        if (!urlInput.value) return;

        try {
            await navigator.clipboard.writeText(urlInput.value);
            copyBtn.textContent = "Copied";
            setTimeout(() => {
                copyBtn.textContent = "Copy";
            }, 1200);
        } catch (error) {
            showMessage("Δεν έγινε αντιγραφή.", "error");
        }
    });

    saveBtn.addEventListener("click", async function () {
        if (!selectedItem) {
            showMessage("Επίλεξε πρώτα ένα αρχείο.", "error");
            return;
        }

        const updateUrl = window.MEDIAHUB.urls.updateBase.replace("/0/", `/${selectedItem.id}/`);

        const formData = new FormData();
        formData.append("title", titleInput.value);
        formData.append("show_gallery", showGalleryInput.checked ? "true" : "false");
        formData.append("show_news", showNewsInput.checked ? "true" : "false");

        try {
            const response = await fetch(updateUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });

            const data = await response.json();

            if (!response.ok || !data.ok) {
                showMessage(data.message || "Αποτυχία αποθήκευσης.", "error");
                return;
            }

            showMessage("Ο τίτλος αποθηκεύτηκε.");
            loadItems(currentPage);
        } catch (error) {
            showMessage("Σφάλμα αποθήκευσης.", "error");
        }
    });

    deleteBtn.addEventListener("click", async function () {
        if (!selectedItem) {
            showMessage("Επίλεξε πρώτα ένα αρχείο.", "error");
            return;
        }

        const confirmed = window.confirm(`Να διαγραφεί το αρχείο "${selectedItem.name}";`);
        if (!confirmed) return;

        const deleteUrl = window.MEDIAHUB.urls.deleteBase.replace("/0/", `/${selectedItem.id}/`);

        try {
            const response = await fetch(deleteUrl, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken()
                }
            });

            const data = await response.json();

            if (!response.ok || !data.ok) {
                showMessage(data.message || "Αποτυχία διαγραφής.", "error");
                return;
            }

            showMessage("Το αρχείο διαγράφηκε.");
            loadItems(1);
        } catch (error) {
            showMessage("Σφάλμα διαγραφής.", "error");
        }
    });

    useBtn.addEventListener("click", function () {
        if (!selectedItem) {
            showMessage("Επίλεξε πρώτα ένα αρχείο.", "error");
            return;
        }

        if (!targetFieldSelector) {
            showMessage("Δεν υπάρχει target field.", "error");
            return;
        }

        const targetField = document.querySelector(targetFieldSelector);
        if (!targetField) {
            showMessage("Το target field δεν βρέθηκε.", "error");
            return;
        }

        targetField.value = selectedItem.url;
        targetField.dispatchEvent(new Event("change", { bubbles: true }));
        closeModal();
    });
});