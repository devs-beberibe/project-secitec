(() => {
  "use strict";
  const root = document.getElementById("maintenance-dashboard");
  if (!root) return;
  const $ = selector => document.querySelector(selector);
  const auth = window.SECITECAuth;
  let sheets = [], components = [], selected = null, busy = false;
  let statusFilter = "ALL", canPerform = false, noticeTimer;
  const statusNames = {RCV: "Recebido", MNT: "Manutenção feita", DLV: "Entregue"};
  const today = () => { const value = new Date(); return `${value.getFullYear()}-${String(value.getMonth() + 1).padStart(2, "0")}-${String(value.getDate()).padStart(2, "0")}`; };
  const date = value => value ? String(value).slice(0, 10).split("-").reverse().join("/") : "—";
  const text = value => String(value ?? "");
  const statusOf = sheet => sheet.status || ({RECEIVED: "RCV", IN_MAINTENANCE: "MNT", DELIVERED: "DLV"})[sheet.situation];

  function errorText(data) {
    if (Array.isArray(data)) return data.map(errorText).join(" ");
    if (data && typeof data === "object") return Object.entries(data).map(([key, value]) => `${key === "detail" ? "" : `${key}: `}${errorText(value)}`).join("\n");
    return text(data || "Não foi possível concluir a operação.");
  }
  async function api(url, options = {}) {
    const response = await auth.fetch(url, {...options, credentials: "include", headers: {Accept: "application/json", ...(options.body ? {"Content-Type": "application/json", "X-CSRFToken": $("#receipt-form [name=csrfmiddlewaretoken]").value} : {})}});
    const data = (response.headers.get("content-type") || "").includes("application/json") ? await response.json() : null;
    if (!response.ok) throw new Error(data ? errorText(data) : `Falha HTTP ${response.status}.`);
    return data;
  }
  function formError(form, message = "") { const target = form.querySelector(".error"); target.textContent = message; target.hidden = !message; }
  function notice(message) { const target = $("#maintenance-notification"); target.textContent = message; target.hidden = false; clearTimeout(noticeTimer); noticeTimer = setTimeout(() => { target.hidden = true; }, 5500); }
  function node(tag, className, value) { const item = document.createElement(tag); if (className) item.className = className; if (value !== undefined) item.textContent = value; return item; }

  function render() {
    const query = $("#sheet-search").value.trim().toLocaleLowerCase("pt-BR");
    const filtered = sheets.filter(sheet => (statusFilter === "ALL" || statusOf(sheet) === statusFilter) && [sheet.id, sheet.serial_number, sheet.pc_responsible, sheet.sector_name, sheet.secretary_name].join(" ").toLocaleLowerCase("pt-BR").includes(query));
    const body = $("#sheets-body"); body.replaceChildren();
    filtered.forEach(sheet => {
      const status = statusOf(sheet), row = node("tr"), main = node("td"), details = node("button", "call-link");
      details.type = "button"; details.append(node("small", "", `#${String(sheet.id).padStart(4, "0")}`), node("strong", "", sheet.serial_number || "Sem tombo/série"));
      details.addEventListener("click", () => showDetails(sheet)); main.append(details, node("div", "requester", sheet.problem_description));
      const situation = node("td"); situation.append(node("span", `maintenance-status ${status}`, statusNames[status] || sheet.status_label));
      const actions = node("td"), group = node("div", "actions");
      if (status === "RCV" && canPerform) { const button = node("button", "", "Realizar manutenção"); button.type = "button"; button.addEventListener("click", () => openMaintenance(sheet)); group.append(button); }
      if (status === "MNT") { const button = node("button", "", "Registrar entrega"); button.type = "button"; button.addEventListener("click", () => openDelivery(sheet)); group.append(button); }
      actions.append(group);
      const cells = [main, node("td", "", sheet.sector_name), node("td", "", sheet.pc_responsible), node("td", "", date(sheet.receipt_date)), situation, actions];
      ["Ficha / equipamento", "Setor", "Responsável", "Recebimento", "Situação", "Ações"].forEach((label, index) => { cells[index].dataset.label = label; }); row.append(...cells); body.append(row);
    });
    $("#sheets-message").hidden = filtered.length > 0; $("#sheets-message").textContent = query ? "Nenhuma ficha corresponde à busca." : "Nenhuma ficha nesta situação.";
  }

  async function loadAllSheets() {
    const loaded = [], visited = new Set(); let url = new URL(root.dataset.sheetsUrl, location.origin).href;
    while (url) { if (visited.has(url)) throw new Error("A paginação retornou um endereço repetido."); visited.add(url); const data = await api(url); if (Array.isArray(data)) { loaded.push(...data); url = null; } else { loaded.push(...(data.results || [])); url = data.next ? new URL(data.next, url).href : null; } }
    return loaded;
  }
  async function load() {
    $("#sheets-list").setAttribute("aria-busy", "true");
    try { [sheets, components] = await Promise.all([loadAllSheets(), api(root.dataset.componentsUrl)]); renderComponents(); render(); }
    catch (error) { $("#sheets-message").hidden = false; $("#sheets-message").textContent = error.message; }
    finally { $("#sheets-list").setAttribute("aria-busy", "false"); }
  }
  function renderComponents() {
    const target = $("#component-fields"); target.replaceChildren();
    components.forEach(component => { const card = node("div", "component-card"), title = node("strong", "", component.name), select = document.createElement("select"), description = document.createElement("input"); select.name = `component_status_${component.id}`; select.required = true; select.append(new Option("Selecione o estado", ""), new Option("Contém e está em bom estado", "1"), new Option("Contém e está em mau estado", "2"), new Option("Não contém", "3")); description.name = `component_description_${component.id}`; description.maxLength = 200; description.placeholder = "Observação (opcional)"; card.append(title, select, description); target.append(card); });
  }

  const sectorData = [...$("#maintenance-sector-options").content.querySelectorAll("option")].map(option => ({id: option.value, name: option.textContent.trim(), secretary: option.dataset.secretaryId}));
  $("#maintenance-secretary").addEventListener("change", event => { const sector = $("#maintenance-sector"); sector.replaceChildren(new Option("Selecione o setor", "")); sectorData.filter(item => item.secretary === event.target.value).forEach(item => sector.append(new Option(item.name, item.id))); sector.disabled = !event.target.value || sector.options.length === 1; });
  $("#new-sheet").addEventListener("click", () => { const form = $("#receipt-form"); form.reset(); formError(form); form.elements.receipt_date.value = today(); $("#maintenance-sector").disabled = true; $("#receipt-dialog").showModal(); });
  function openMaintenance(sheet) { selected = sheet; const form = $("#maintenance-form"); form.reset(); formError(form); $("#maintenance-number").textContent = `Ficha #${sheet.id} · ${sheet.serial_number || "sem tombo/série"}`; $("#maintenance-dialog").showModal(); }
  function openDelivery(sheet) { selected = sheet; const form = $("#delivery-form"); form.reset(); formError(form); form.elements.delivery_date.value = today(); form.elements.delivery_date.min = sheet.receipt_date; form.elements.delivery_date.max = today(); $("#delivery-number").textContent = `Ficha #${sheet.id}`; $("#delivery-dialog").showModal(); }
  function showDetails(sheet) {
    const target = $("#sheet-details"); target.replaceChildren(); const list = node("dl", "sheet-detail-list");
    [["Situação", statusNames[statusOf(sheet)]], ["Tombo/série", sheet.serial_number || "Não informado"], ["Secretaria / setor", `${sheet.secretary_name} / ${sheet.sector_name}`], ["Responsável", sheet.pc_responsible], ["Contato", sheet.contact], ["Problema", sheet.problem_description], ["Observações", sheet.observation || "Não informada"], ["Recebido em", date(sheet.receipt_date)], ["Recebido por", sheet.receipt_name], ["Técnico", sheet.technician_name || "Ainda não atribuído"], ["Serviço realizado", sheet.realized_service || "Não informado"], ["Entrega", date(sheet.delivery_date)], ["Conferido por", sheet.search_by || "Não informado"], ["Entregue por", sheet.delivered_by_name || "Não informado"]].forEach(([label, value]) => list.append(node("dt", "", label), node("dd", "", value)));
    target.append(list); if ((sheet.components_status || []).length) { target.append(node("h3", "", "Componentes")); const summary = node("div", "component-summary"); sheet.components_status.forEach(item => { const row = node("div"); row.append(node("strong", "", item.component.name), node("span", "", item.status_label), node("small", "", item.description_report || "Sem observação")); summary.append(row); }); target.append(summary); }
    $("#sheet-details-title").textContent = `Ficha #${sheet.id}`; $("#sheet-details-dialog").showModal();
  }
  async function submit(form, url, payload, success) {
    if (busy) return; busy = true; formError(form); const button = form.querySelector("[type=submit]"), label = button.textContent; button.disabled = true; button.textContent = "Salvando…";
    try { await api(url, {method: "POST", body: JSON.stringify(payload)}); form.closest("dialog").close(); notice(success); await load(); }
    catch (error) { formError(form, error.message); } finally { busy = false; button.disabled = false; button.textContent = label; }
  }
  $("#receipt-form").addEventListener("submit", event => { event.preventDefault(); const form = event.currentTarget, values = new FormData(form); submit(form, root.dataset.receiptUrl, {receipt_date: values.get("receipt_date"), serial_number: text(values.get("serial_number")).trim(), receipt: Number(values.get("receipt")), secretary_sector: Number(values.get("secretary_sector")), pc_responsible: text(values.get("pc_responsible")).trim(), problem_description: text(values.get("problem_description")).trim(), contact: text(values.get("contact")).trim()}, "Equipamento recebido. Ficha criada com sucesso."); });
  $("#maintenance-form").addEventListener("submit", event => { event.preventDefault(); if (!selected) return; const form = event.currentTarget, values = new FormData(form), statuses = components.map(component => ({component: Number(component.id), status: Number(values.get(`component_status_${component.id}`)), description_report: text(values.get(`component_description_${component.id}`)).trim()})); if (statuses.some(item => !item.status)) return formError(form, "Informe o estado de todos os componentes."); submit(form, `${root.dataset.sheetsUrl}${encodeURIComponent(selected.id)}/manutencao/`, {technician: Number(values.get("technician")), observation: text(values.get("observation")).trim(), realized_service: text(values.get("realized_service")).trim(), components_status: statuses}, `Manutenção da ficha #${selected.id} concluída.`); });
  $("#delivery-form").addEventListener("submit", event => { event.preventDefault(); if (!selected) return; const form = event.currentTarget, values = new FormData(form); submit(form, `${root.dataset.sheetsUrl}${encodeURIComponent(selected.id)}/entrega/`, {search_by: text(values.get("search_by")).trim(), delivered_by: Number(values.get("delivered_by")), delivery_date: values.get("delivery_date")}, `Entrega da ficha #${selected.id} registrada.`); });
  document.querySelectorAll("[data-maintenance-close]").forEach(button => button.addEventListener("click", () => { if (!busy) button.closest("dialog").close(); }));
  document.querySelectorAll("[data-sheet-status]").forEach(button => button.addEventListener("click", () => { statusFilter = button.dataset.sheetStatus; document.querySelectorAll("[data-sheet-status]").forEach(item => { item.classList.toggle("active", item === button); item.setAttribute("aria-pressed", String(item === button)); }); render(); }));
  $("#sheet-search").addEventListener("input", render); $("#refresh-sheets").addEventListener("click", load);
  auth.ready.then(user => { if (!user) return location.replace($("#auth-config").dataset.homeUrl || "/"); const names = Array.isArray(user.groups) ? user.groups : []; const technician = names.includes("Tecnico"); const administrative = names.includes("Administrativo"); canPerform = technician || user.capabilities?.maintenance_perform === true; const canReceive = technician || administrative || user.capabilities?.maintenance_receive === true || user.capabilities?.maintenance_start === true; $("#new-sheet").hidden = !canReceive; load(); });
})();
