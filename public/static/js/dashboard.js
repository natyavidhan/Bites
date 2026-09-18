(function () {
  "use strict";

  const tbody = document.getElementById("sites-tbody");
  const emptyState = document.getElementById("empty-state");
  const table = document.getElementById("sites-table");

  const backdrop = document.getElementById("modal-backdrop");
  const modalTitle = document.getElementById("modal-title");
  const form = document.getElementById("site-form");
  const formError = document.getElementById("form-error");
  const siteIdField = document.getElementById("site-id");
  const titleField = document.getElementById("title");
  const slugField = document.getElementById("slug");
  const slugPreview = document.getElementById("slug-preview");
  const protectedCheckbox = document.getElementById("protected");
  const protectFields = document.getElementById("protect-fields");
  const protectPasswordHint = document.getElementById("protect-password-hint");
  const protectPasswordField = document.getElementById("protect_password");
  const fileField = document.getElementById("file");
  const contentField = document.getElementById("content");

  let slugTouched = false;
  let editingSiteId = null;

  function slugify(text) {
    return (text || "")
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "");
  }

  function showToast(message, isError) {
    const toast = document.createElement("div");
    toast.className = "toast" + (isError ? " error" : "");
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str == null ? "" : str;
    return div.innerHTML;
  }

  function formatDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  async function fetchSites() {
    const res = await fetch("/dashboard/api/sites");
    if (res.status === 401) {
      window.location.href = "/login";
      return;
    }
    const data = await res.json();
    renderTable(data.sites || []);
  }

  function renderTable(sites) {
    tbody.innerHTML = "";
    if (sites.length === 0) {
      table.style.display = "none";
      emptyState.style.display = "block";
      return;
    }
    table.style.display = "";
    emptyState.style.display = "none";

    for (const site of sites) {
      const tr = document.createElement("tr");
      const url = "/" + site.slug;
      tr.innerHTML = `
        <td>${escapeHtml(site.title)}</td>
        <td><a class="site-link" href="${url}" target="_blank" rel="noopener">${url}</a></td>
        <td><span class="badge type-${site.source_type}">${site.source_type}</span></td>
        <td>
          <label class="switch">
            <input type="checkbox" data-action="toggle" data-id="${site.id}" ${site.is_public ? "checked" : ""}>
            <span class="slider"></span>
          </label>
        </td>
        <td>${site.protected ? "Yes" : "&mdash;"}</td>
        <td class="muted">${formatDate(site.updated_at)}</td>
        <td>
          <div class="row-actions">
            <button type="button" data-action="edit" data-id="${site.id}">Edit</button>
            <button type="button" class="btn-danger" data-action="delete" data-id="${site.id}">Delete</button>
          </div>
        </td>
      `;
      tbody.appendChild(tr);
    }
  }

  function resetForm() {
    form.reset();
    siteIdField.value = "";
    editingSiteId = null;
    slugTouched = false;
    formError.style.display = "none";
    protectFields.classList.add("hidden");
    protectPasswordHint.style.display = "none";
    protectPasswordField.required = false;
    fileField.required = false;
    switchTab("upload");
  }

  function openCreateModal() {
    resetForm();
    modalTitle.textContent = "New site";
    backdrop.classList.remove("hidden");
  }

  async function openEditModal(id) {
    resetForm();
    const res = await fetch(`/dashboard/api/sites/${id}`);
    if (!res.ok) {
      showToast("Could not load site.", true);
      return;
    }
    const data = await res.json();
    const site = data.site;

    editingSiteId = id;
    siteIdField.value = id;
    slugTouched = true;
    modalTitle.textContent = "Edit site";
    titleField.value = site.title;
    slugField.value = site.slug;
    updateSlugPreview();
    document.getElementById("is_public").checked = site.is_public;
    contentField.value = site.raw_content || "";
    document.getElementById("source_type").value = site.source_type;
    switchTab("paste");

    if (site.protected) {
      protectedCheckbox.checked = true;
      protectFields.classList.remove("hidden");
      document.getElementById("protect_username").value = site.protect_username || "";
      protectPasswordHint.style.display = "block";
    }

    backdrop.classList.remove("hidden");
  }

  function closeModal() {
    backdrop.classList.add("hidden");
  }

  function updateSlugPreview() {
    const base = window.location.origin;
    slugPreview.textContent = slugField.value ? `${base}/${slugField.value}` : "";
  }

  function switchTab(name) {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.classList.toggle("active", btn.dataset.tab === name);
    });
    document.querySelectorAll(".tab-panel").forEach((panel) => {
      panel.classList.toggle("active", panel.dataset.panel === name);
    });
  }

  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  titleField.addEventListener("input", () => {
    if (!slugTouched) {
      slugField.value = slugify(titleField.value);
      updateSlugPreview();
    }
  });

  slugField.addEventListener("input", () => {
    slugTouched = true;
    slugField.value = slugify(slugField.value);
    updateSlugPreview();
  });

  protectedCheckbox.addEventListener("change", () => {
    protectFields.classList.toggle("hidden", !protectedCheckbox.checked);
  });

  document.getElementById("new-site-btn").addEventListener("click", openCreateModal);
  document.getElementById("cancel-btn").addEventListener("click", closeModal);
  backdrop.addEventListener("click", (e) => {
    if (e.target === backdrop) closeModal();
  });

  tbody.addEventListener("click", async (e) => {
    const btn = e.target.closest("button[data-action]");
    if (btn) {
      const id = btn.dataset.id;
      if (btn.dataset.action === "edit") {
        openEditModal(id);
      } else if (btn.dataset.action === "delete") {
        if (confirm("Delete this site? This cannot be undone.")) {
          const res = await fetch(`/dashboard/api/sites/${id}`, { method: "DELETE" });
          if (res.ok) {
            showToast("Site deleted.");
            fetchSites();
          } else {
            showToast("Could not delete site.", true);
          }
        }
      }
      return;
    }

    const toggle = e.target.closest('input[data-action="toggle"]');
    if (toggle) {
      const id = toggle.dataset.id;
      const res = await fetch(`/dashboard/api/sites/${id}/toggle-visibility`, { method: "POST" });
      if (!res.ok) {
        toggle.checked = !toggle.checked;
        showToast("Could not update visibility.", true);
      }
    }
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    formError.style.display = "none";

    const activePanel = document.querySelector(".tab-panel.active").dataset.panel;
    const formData = new FormData();
    formData.append("title", titleField.value.trim());
    formData.append("slug", slugField.value.trim());
    formData.append("is_public", document.getElementById("is_public").checked ? "true" : "false");
    formData.append("protected", protectedCheckbox.checked ? "true" : "false");

    if (protectedCheckbox.checked) {
      formData.append("protect_username", document.getElementById("protect_username").value.trim());
      if (protectPasswordField.value) {
        formData.append("protect_password", protectPasswordField.value);
      }
    }

    if (activePanel === "upload" && fileField.files.length > 0) {
      formData.append("file", fileField.files[0]);
    } else if (activePanel === "paste" && contentField.value.trim() !== "") {
      formData.append("content", contentField.value);
      formData.append("source_type", document.getElementById("source_type").value);
    } else if (!editingSiteId) {
      formError.textContent = "Upload a file or paste content for the site.";
      formError.style.display = "block";
      return;
    }

    const url = editingSiteId ? `/dashboard/api/sites/${editingSiteId}` : "/dashboard/api/sites";
    const method = editingSiteId ? "PATCH" : "POST";

    const saveBtn = document.getElementById("save-btn");
    saveBtn.disabled = true;
    try {
      const res = await fetch(url, { method, body: formData });
      const data = await res.json();
      if (!res.ok) {
        formError.textContent = data.error || "Something went wrong.";
        formError.style.display = "block";
        return;
      }
      showToast(editingSiteId ? "Site updated." : "Site created.");
      closeModal();
      fetchSites();
    } catch (err) {
      formError.textContent = "Network error. Please try again.";
      formError.style.display = "block";
    } finally {
      saveBtn.disabled = false;
    }
  });

  fetchSites();
})();
