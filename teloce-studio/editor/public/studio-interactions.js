/* Progressive enhancement for the visual canvas. The project model remains
   the source of truth; this only translates native drag/drop into its API. */
(function () {
  let draggedType = "";
  const markPalette = () => document.querySelectorAll(".palette-item").forEach((item) => item.setAttribute("draggable", "true"));
  markPalette();
  new MutationObserver(markPalette).observe(document.documentElement, { childList: true, subtree: true });
  document.addEventListener("dragstart", (event) => {
    const item = event.target.closest?.(".palette-item");
    if (!item) return;
    draggedType = item.textContent.toLowerCase().includes("heading") ? "heading" : item.textContent.toLowerCase().includes("text") ? "text" : item.textContent.toLowerCase().includes("button") ? "button" : "card";
    event.dataTransfer?.setData("text/teloce-component", draggedType);
    event.dataTransfer?.setData("text/plain", draggedType);
  });
  document.addEventListener("dragover", (event) => {
    if (event.target.closest?.(".canvas-page")) event.preventDefault();
  });
  document.addEventListener("drop", (event) => {
    const canvas = event.target.closest?.(".canvas-page");
    if (!canvas || !window.teloceStudio?.state) return;
    event.preventDefault();
    const type = event.dataTransfer?.getData("text/teloce-component") || draggedType;
    if (type && typeof window.teloceStudio.state.addElement === "function") window.teloceStudio.state.addElement(type);
    draggedType = "";
  });
  document.addEventListener("click", async (event) => {
    const tab = event.target.closest?.(".tabs button");
    const state = window.teloceStudio?.state;
    if (tab && state) {
      const name = tab.textContent.trim().toLowerCase();
      if (["design", "code", "data"].includes(name)) {
        event.preventDefault();
        state.inspector = name;
        return;
      }
    }
    const row = event.target.closest?.(".event-row");
    if (!row || !state?.project?.id || !row.textContent.includes("API binding")) return;
    event.preventDefault();
    row.setAttribute("aria-busy", "true");
    try {
      const response = await fetch(`/api/projects/${state.project.id}/bindings`, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ name: "Data endpoint", method: "GET", path: "/api/data" })
      });
      const data = await response.json();
      if (!data.ok) throw new Error(data.error || "Could not add API binding");
      state.project = data.project;
      state.status = "API binding added";
      row.textContent = "✓ Data endpoint connected";
      row.classList.add("connected");
    } catch (error) {
      state.status = error.message;
    } finally {
      row.removeAttribute("aria-busy");
    }
  });
})();
