(() => {
  "use strict";
  const form = document.getElementById("tracking-form");
  if (!form) return;
  const result = document.getElementById("tracking-result");
  const error = form.querySelector(".error");
  const submit = form.querySelector("[type=submit]");
  const formatDate = value => value ? String(value).slice(0, 10).split("-").reverse().join("/") : "—";
  function add(list, label, value) { const dt = document.createElement("dt"), dd = document.createElement("dd"); dt.textContent = label; dd.textContent = value || "—"; list.append(dt, dd); }
  function showError(message) { error.textContent = message; error.hidden = false; }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    const query = String(new FormData(form).get("query") || "").trim();
    error.hidden = true; result.hidden = true;
    if (!query) return showError("Digite o número da ficha, tombamento ou setor.");
    const endpoint = form.dataset.searchUrl;
    if (!endpoint) return showError("A rota de consulta das fichas não está configurada.");
    const url = new URL(endpoint, location.origin); url.searchParams.set("q", query);
    submit.disabled = true; submit.textContent = "Consultando…";
    try {
      const response = await fetch(url, {credentials: "include", cache: "no-store", headers: {Accept: "application/json"}});
      const isJSON = (response.headers.get("content-type") || "").includes("application/json");
      const data = isJSON ? await response.json() : null;
      if (response.status === 404) throw new Error("Ficha não encontrada.");
      if (!response.ok) throw new Error(data?.detail || "Não foi possível consultar a ficha.");
      if (!Array.isArray(data)) throw new Error("A API retornou um formato inesperado.");
      result.replaceChildren();
      data.forEach(sheet => {
        const card = document.createElement("article"); card.className = "tracking-sheet";
        card.tabIndex = 0;
        card.setAttribute("role", "button");
        card.setAttribute("aria-label", `Abrir detalhes da ficha ${sheet.id}`);
        const heading = document.createElement("div"); heading.className = "tracking-sheet-heading";
        const title = document.createElement("h3"); title.textContent = `Ficha #${sheet.id}`;
        const badge = document.createElement("span"); badge.className = `maintenance-status ${sheet.status}`; badge.textContent = sheet.status_label;
        const list = document.createElement("dl");
        add(list, "Tombo/série", sheet.serial_number || "Não informado"); add(list, "Setor", sheet.sector_name);
        add(list, "Técnico responsável", sheet.technician_name || "Ainda não atribuído"); add(list, "Problema", sheet.problem_description);
        add(list, "Serviço realizado", sheet.realized_service || "Ainda não informado"); add(list, "Observações", sheet.observation || "Nenhuma observação");
        add(list, "Recebimento", formatDate(sheet.receipt_date)); add(list, "Entrega", formatDate(sheet.delivery_date));
        const hint = document.createElement("span");
        hint.className = "tracking-sheet-hint";
        hint.textContent = "Clique para ver detalhes →";
        heading.append(title, badge); card.append(heading, list, hint);
        card.addEventListener("click", () => showDetails(sheet));
        card.addEventListener("keydown", event => {
          if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            showDetails(sheet);
          }
        });
        result.append(card);
      });
      result.hidden = false;
    } catch (exception) { showError(exception.message); }
    finally { submit.disabled = false; submit.textContent = "Consultar"; }
  });

  function showDetails(sheet) {
    const target = document.getElementById("tracking-details");
    const title = document.getElementById("tracking-details-title");
    const list = document.createElement("dl");
    list.className = "sheet-detail-list";
    add(list, "Situação", sheet.status_label);
    add(list, "Tombo/série", sheet.serial_number || "Não informado");
    add(list, "Setor", sheet.sector_name);
    add(list, "Técnico responsável", sheet.technician_name || "Ainda não atribuído");
    add(list, "Problema", sheet.problem_description);
    add(list, "Serviço realizado", sheet.realized_service || "Ainda não informado");
    add(list, "Observações", sheet.observation || "Nenhuma observação");
    add(list, "Recebimento", formatDate(sheet.receipt_date));
    add(list, "Entrega", formatDate(sheet.delivery_date));

    const componentTitle = document.createElement("h3");
    componentTitle.textContent = "Componentes";
    const componentList = document.createElement("div");
    componentList.className = "component-summary";
    const components = Array.isArray(sheet.components_status)
      ? sheet.components_status
      : [];
    if (components.length) {
      components.forEach(item => {
        const row = document.createElement("div");
        const name = document.createElement("strong");
        const status = document.createElement("span");
        const observation = document.createElement("small");
        name.textContent = item.component?.name || "Componente";
        status.textContent = item.status_label || "Estado não informado";
        observation.textContent = item.description_report || "Sem observação";
        row.append(name, status, observation);
        componentList.append(row);
      });
    } else {
      componentList.append(
        Object.assign(document.createElement("p"), {
          textContent: "Os componentes ainda não foram conferidos.",
        })
      );
    }
    title.textContent = `Ficha #${sheet.id}`;
    target.replaceChildren(list, componentTitle, componentList);
    document.getElementById("tracking-details-dialog").showModal();
  }

  document.querySelectorAll("[data-tracking-close]").forEach(button => {
    button.addEventListener("click", () => {
      button.closest("dialog").close();
    });
  });
})();
