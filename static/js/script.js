(() => {
  "use strict";

  const root = document.getElementById("dashboard");
  if (!root) return;

  const $ = selector => document.querySelector(selector);
  const auth = window.SECITECAuth;

  let authenticated = false;

  const historyAvailable =
    root.dataset.historyAvailable === "true";

  const state = {
    calls: [],
    status: "ATIVOS",
    search: "",
    page: 1,
  };

  const pageSize = 10;

  let selected = null;
  let busy = false;
  let loadController;

  const privateDashboard = $("#private-dashboard");
  const secretarySelect = $("#secretary");
  const sectorSelect = $("#sector");

  const sectors = [
    ...$("#sector-options").content.querySelectorAll("option"),
  ].map(option => ({
    id: option.value,
    name: option.textContent.trim(),
    secretaryId: option.dataset.secretaryId,
    secretaryName: option.dataset.secretaryName,
  }));

  // Fallback caso a view tenha enviado setores, mas não secretarias.
  if (secretarySelect.options.length === 1) {
    const names = new Map(
      sectors.map(sector => [
        sector.secretaryId,
        sector.secretaryName,
      ])
    );

    [...names]
      .sort((a, b) => a[1].localeCompare(b[1], "pt-BR"))
      .forEach(([id, name]) => {
        secretarySelect.append(new Option(name, id));
      });
  }

  function updateSectors() {
    const chosen = secretarySelect.value;

    sectorSelect.replaceChildren(
      new Option(
        chosen
          ? "Selecione o setor"
          : "Selecione primeiro a secretaria",
        ""
      )
    );

    const available = sectors.filter(
      sector => sector.secretaryId === chosen
    );

    available.forEach(sector => {
      sectorSelect.append(new Option(sector.name, sector.id));
    });

    sectorSelect.disabled =
      !chosen || available.length === 0;

    $("#sector-help").textContent =
      chosen && !available.length
        ? "Esta secretaria ainda não possui setores disponíveis."
        : "";

    $("#open-form [type=submit]").disabled =
      !root.dataset.openUrl ||
      !chosen ||
      !available.length;
  }

  secretarySelect.addEventListener("change", updateSectors);
  updateSectors();

  const statusNames = {
    OPN: "Aberto",
    IMP: "Em andamento",
    CLS: "Finalizado",
  };

  const priorityNames = {
    0: "Alta",
    1: "Média",
    2: "Baixa",
  };

  const date = value =>
    value
      ? String(value).slice(0, 10).split("-").reverse().join("/")
      : "—";

  function element(tag, className, text) {
    const result = document.createElement(tag);

    if (className) result.className = className;
    if (text !== undefined) result.textContent = text;

    return result;
  }

  const token = () =>
    $("#open-form [name=csrfmiddlewaretoken]").value;

  function fieldErrors(data) {
    if (Array.isArray(data)) {
      return data.map(fieldErrors).join(" ");
    }

    if (data && typeof data === "object") {
      return Object.entries(data)
        .map(([key, value]) => {
          const label = key === "detail" ? "" : key + ": ";
          return label + fieldErrors(value);
        })
        .join("\n");
    }

    return String(data || "Não foi possível concluir a operação.");
  }

  async function api(url, options = {}) {
    const target = new URL(url, location.origin);

    if (target.origin !== location.origin) {
      throw new Error(
        "A API precisa estar no mesmo domínio do sistema."
      );
    }

    const controller = new AbortController();

    let timeout = false;

    const abort = () => controller.abort();

    if (options.signal?.aborted) abort();

    options.signal?.addEventListener("abort", abort, {
      once: true,
    });

    const timer = setTimeout(() => {
      timeout = true;
      abort();
    }, 15000);

    try {
      const response = await (auth ? auth.fetch : fetch)(
        target,
        {
          ...options,
          signal: controller.signal,
          credentials: "include",

          headers: {
            Accept: "application/json",

            ...(options.body
              ? {
                  "Content-Type": "application/json",
                  "X-CSRFToken": token(),
                }
              : {}),
          },
        }
      );

      const isJSON = (
        response.headers.get("content-type") || ""
      ).includes("application/json");

      const data = isJSON ? await response.json() : null;

      if (!response.ok) {
        if ([401, 403].includes(response.status)) {
          throw new Error(
            "Acesso negado ou sessão expirada. " +
            "Atualize a página e entre novamente."
          );
        }

        throw new Error(
          data
            ? fieldErrors(data)
            : `Falha na solicitação (HTTP ${response.status}).`
        );
      }

      if (data === null) {
        throw new Error(
          "A API não retornou JSON. Confira as rotas do sistema."
        );
      }

      return data;
    } catch (error) {
      if (timeout) {
        throw new Error(
          "O servidor demorou para responder. Tente novamente."
        );
      }

      if (error instanceof TypeError) {
        throw new Error(
          "Não foi possível conectar ao servidor."
        );
      }

      throw error;
    } finally {
      clearTimeout(timer);
      options.signal?.removeEventListener("abort", abort);
    }
  }

  function notice(message, error = false) {
    const target = $("#notification");

    target.textContent = message;
    target.hidden = false;
    target.classList.toggle("error", error);
  }

  function formError(form, message = "") {
    const target = form.querySelector(".error");

    target.textContent = message;
    target.hidden = !message;
  }

  function sectorName(call) {
  // Caso a API já envie o nome.
  if (call.sector_name) {
    return call.sector_name;
  }

  if (call.sector && typeof call.sector === "object") {
    return call.sector.sector_name || "Setor não informado";
  }

  // Busca o nome na lista de setores do formulário.
  const sectorId = call.sector ?? call.id_sector;

  const option = Array.from(
    document.querySelectorAll("#sector-options")
  )
    .flatMap(template =>
      Array.from(template.content.querySelectorAll("option"))
    )
    .find(option => option.value === String(sectorId));

  return option
    ? option.textContent.trim()
    : "Setor não informado";
}

  function showDialog(id) {
    const dialog = $(id);
    const form = dialog.querySelector("form");

    if (form) formError(form);

    dialog.showModal();
  }

  document.querySelectorAll("[data-close]").forEach(button => {
    button.addEventListener("click", () => {
      if (!busy) button.closest("dialog").close();
    });
  });

  document.querySelectorAll("dialog").forEach(dialog => {
    dialog.addEventListener("cancel", event => {
      if (busy) event.preventDefault();
    });
  });

  function showDetails(call) {
    $("#detail-title").textContent = `Chamado #${call.id}`;

    const details = $("#details");
    details.replaceChildren();

    const values = [
      ["Solicitante", call.requester],
      ["Setor", sectorName(call)],
      ["Problema", call.problem],
      ["Descrição", call.description || "Não informada"],
      ["Status", statusNames[call.status]],
      ["Prioridade", priorityNames[call.priority]],
      ["Abertura", date(call.date_start)],
      ["Conclusão", date(call.date_end)],
      ["Solução", call.solution || "Não registrada"],
      [
  "Técnicos",
  (call.tecs || [])
    .map(tecnico => tecnico.name)
    .filter(Boolean)
    .join(", ") || "Nenhum técnico informado",
],
    ];
    values.forEach(([label, value]) => {
      details.append(
        element("dt", "", label),
        element("dd", "", value || "—")
      );
    });

    showDialog("#detail-dialog");
  }

  function action(call, finish) {
    const button = element(
      "button",
      "",
      finish ? "Finalizar" : "Realizar"
    );

    button.type = "button";

    button.disabled =
      !authenticated ||
      call.status !== (finish ? "IMP" : "OPN");

    button.title = !authenticated
      ? "Entre para atender o chamado"
      : call.status === "CLS"
        ? "Chamado já finalizado"
        : finish
          ? "O chamado precisa estar em andamento"
          : "Iniciar atendimento";

    button.setAttribute(
      "aria-label",
      `${finish ? "Finalizar" : "Realizar"} chamado #${call.id}`
    );

    button.addEventListener("click", () => {
      selected = call;

      if (finish) {
        $("#finish-form").reset();

        $("#finish-number").textContent =
          `Registre a solução do chamado #${call.id}.`;

        const assigned = Array.isArray(call.tecs)
          ? call.tecs.map(tec => String(tec.id ?? tec))
          : [];

        document
          .querySelectorAll("#finish-form [name=tecs]")
          .forEach(input => {
            input.checked = assigned.includes(input.value);
          });

        showDialog("#finish-dialog");
      } else {
        $("#start-number").textContent =
          `chamado #${call.id}`;

        showDialog("#start-dialog");
      }
    });

    return button;
  }

  function priorityAction(call) {
    const button = element("button", "", "Prioridade");

    button.type = "button";

    button.disabled =
      !authenticated || call.status === "CLS";

    button.title = "Alterar a prioridade do chamado";

    button.setAttribute(
      "aria-label",
      `Editar prioridade do chamado #${call.id}`
    );

    button.addEventListener("click", () => {
      selected = call;

      $("#priority-form").reset();

      $("#priority-number").textContent =
        `Chamado #${call.id}. ` +
        "A mudança de prioridade não altera o andamento.";

      $("#new-priority").value = String(call.priority);

      showDialog("#priority-dialog");
    });

    return button;
  }

  function render() {
    const filtered = state.calls.filter(call => {
      const statusMatches =
        state.status === "ATIVOS"
          ? ["OPN", "IMP"].includes(call.status)
          : call.status === state.status;

      const text = [
        call.id,
        call.problem,
        call.description,
        call.requester,
        sectorName(call),
        call.secretary_name,
      ]
        .join(" ")
        .toLocaleLowerCase("pt-BR");

      return statusMatches && text.includes(state.search);
    });

    const pageCount = Math.max(
      1,
      Math.ceil(filtered.length / pageSize)
    );

    state.page = Math.min(state.page, pageCount);

    const rows = filtered.slice(
      (state.page - 1) * pageSize,
      state.page * pageSize
    );

    const body = $("#calls-body");
    body.replaceChildren();

    rows.forEach(call => {
      const row = element("tr");
      const main = element("td");
      const link = element("button", "call-link");

      link.type = "button";

      link.append(
        element(
          "small",
          "",
          `#${String(call.id).padStart(4, "0")}`
        ),
        element("strong", "", call.problem)
      );

      link.addEventListener("click", () => {
        showDetails(call);
      });

      main.append(
        link,
        element("div", "requester", call.requester)
      );

      const sector = element("td", "", sectorName(call));

      if (call.secretary_name) {
        sector.append(
          element("div", "secretary", call.secretary_name)
        );
      }

      const status = element("td");

      const statusClass = ["OPN", "IMP", "CLS"].includes(
        call.status
      )
        ? call.status
        : "";

      status.append(
        element(
          "span",
          `badge ${statusClass}`,
          statusNames[call.status] || call.status
        )
      );

      const priority = element("td");

      priority.append(
        element(
          "span",
          `priority${Number(call.priority) === 0 ? " high" : ""}`,
          priorityNames[call.priority] || "—"
        )
      );

      const opened = element(
        "td",
        "",
        date(call.date_start)
      );

      const actions = element("td");
      const buttons = element("div", "actions");

      buttons.append(
        action(call, false),
        action(call, true),
        priorityAction(call)
      );

      actions.append(buttons);

      [
        [sector, "Setor"],
        [status, "Status"],
        [priority, "Prioridade"],
        [opened, "Abertura"],
        [actions, "Ações"],
      ].forEach(([cell, label]) => {
        cell.dataset.label = label;
      });

      row.append(
        main,
        sector,
        status,
        priority,
        opened,
        actions
      );

      body.append(row);
    });

    $("#list-message").hidden = rows.length > 0;

    $("#list-message").textContent = state.search
      ? "Nenhum chamado corresponde à sua busca."
      : "Nenhum chamado neste status.";

    $("#page-label").textContent =
      `${filtered.length} chamados · ` +
      `Página ${state.page} de ${pageCount}`;

    $("#previous").disabled = state.page <= 1;
    $("#next").disabled = state.page >= pageCount;
  }

  function counters() {
    $("#count-active").textContent = state.calls.filter(
      call => ["OPN", "IMP"].includes(call.status)
    ).length;

    $("#count-open").textContent = state.calls.filter(
      call => call.status === "OPN"
    ).length;

    $("#count-progress").textContent = state.calls.filter(
      call => call.status === "IMP"
    ).length;

    if (historyAvailable) {
      $("#count-closed").textContent = state.calls.filter(
        call => call.status === "CLS"
      ).length;

      $("#closed-caption").textContent =
        "Atendimento concluído";

      $("#closed-filter").disabled = false;
      $("#closed-filter").removeAttribute("title");
    }
  }

  async function load() {
    if (!authenticated) return;

    loadController?.abort();

    const controller = new AbortController();
    loadController = controller;

    $("#list").setAttribute("aria-busy", "true");
    $("#calls-body").replaceChildren();

    $("#list-message").textContent = "Carregando chamados…";
    $("#list-message").hidden = false;

    $("#previous").disabled = true;
    $("#next").disabled = true;
    $("#page-label").textContent = "";

    ["active", "open", "progress", "closed"].forEach(name => {
      $(`#count-${name}`).textContent = "—";
    });

    try {
      if (!root.dataset.callsUrl) {
        throw new Error(
          "Configure a rota chamados-list no home.html."
        );
      }

      const loaded = [];
      const visited = new Set();

      let url = new URL(
        root.dataset.callsUrl,
        location.origin
      ).href;

      while (url) {
        if (visited.has(url)) {
          throw new Error(
            "A paginação da API retornou um endereço repetido."
          );
        }

        visited.add(url);

        const data = await api(url, {
          signal: controller.signal,
        });

        const items = Array.isArray(data)
          ? data
          : data.results;

        if (!Array.isArray(items)) {
          throw new Error(
            "A API precisa retornar uma lista " +
            "ou um objeto com results."
          );
        }

        loaded.push(...items);

        url =
          !Array.isArray(data) && data.next
            ? new URL(data.next, url).href
            : null;
      }

      if (loadController !== controller) return;

      state.calls = [
        ...new Map(
          loaded.map(call => [String(call.id), call])
        ).values(),
      ].sort(
        (a, b) =>
          Number(a.priority) - Number(b.priority) ||
          String(a.date_start).localeCompare(
            String(b.date_start)
          ) ||
          Number(a.id) - Number(b.id)
      );

      counters();
      render();

      $("#updated").textContent =
        "Atualizado às " +
        new Date().toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        });
    } catch (error) {
      if (
        controller.signal.aborted ||
        loadController !== controller
      ) {
        return;
      }

      state.calls = [];

      $("#list-message").textContent =
        `${error.message} Use Atualizar para tentar novamente.`;

      $("#updated").textContent = "Dados indisponíveis";
    } finally {
      if (loadController === controller) {
        $("#list").setAttribute("aria-busy", "false");
      }
    }
  }

  document.querySelectorAll("[data-status]").forEach(button => {
    button.addEventListener("click", () => {
      state.status = button.dataset.status;
      state.page = 1;

      document.querySelectorAll("[data-status]").forEach(item => {
        item.classList.toggle("active", item === button);

        item.setAttribute(
          "aria-pressed",
          String(item === button)
        );
      });

      render();
    });
  });

  $("#search").addEventListener("input", event => {
    state.search = event.target.value
      .trim()
      .toLocaleLowerCase("pt-BR");

    state.page = 1;
    render();
  });

  $("#refresh").addEventListener("click", load);

  $("#previous").addEventListener("click", () => {
    state.page--;
    render();
  });

  $("#next").addEventListener("click", () => {
    state.page++;
    render();
  });

  $("#open-call").addEventListener("click", () => {
    const form = $("#open-form");

    form.reset();
    updateSectors();

    if (!sectors.length) {
      $("#sector-help").textContent =
        "A lista de setores ainda não foi disponibilizada. " +
        "Entre em contato com a equipe responsável.";
    }

    showDialog("#open-dialog");

    if (!root.dataset.openUrl) {
      formError(
        form,
        "Configure a rota chamados-abrir no home.html."
      );
    }
  });

  const actionUrl = suffix =>
    `${root.dataset.callsUrl}` +
    `${encodeURIComponent(selected.id)}/${suffix}/`;

  async function save(
    form,
    url,
    data,
    message,
    method = "POST"
  ) {
    if (busy) return;

    busy = true;
    formError(form);

    const buttons = [...form.querySelectorAll("button")];
    const submit = form.querySelector("[type=submit]");
    const label = submit.textContent;

    buttons.forEach(button => {
      button.disabled = true;
    });

    submit.textContent = "Salvando…";

    try {
      await api(url, {
        method,
        body: JSON.stringify(data),
      });

      form.closest("dialog").close();
      form.reset();

      notice(message);

      state.page = 1;

      if (authenticated) await load();
    } catch (error) {
      formError(
        form,
        `${error.message}\n` +
        "Se houve uma falha de conexão, confira o painel " +
        "antes de enviar novamente."
      );
    } finally {
      buttons.forEach(button => {
        button.disabled = false;
      });

      submit.textContent = label;
      busy = false;
    }
  }

  $("#open-form").addEventListener("submit", event => {
    event.preventDefault();

    const form = event.currentTarget;
    const data = new FormData(form);

    const requester = data.get("requester").trim();
    const problem = data.get("problem").trim();
    const description = data.get("description").trim();

    if (!requester || !problem) {
      return formError(
        form,
        "Preencha o solicitante e o problema."
      );
    }

    const sector = sectors.find(
      item =>
        item.id === data.get("sector") &&
        item.secretaryId === data.get("secretary")
    );

    if (!sector) {
      return formError(
        form,
        "Selecione um setor da secretaria escolhida."
      );
    }

    save(
    form,
    root.dataset.openUrl,
    {
        requester,
        id_sector: Number(sector.id),
        problem,
        description,
    },
    "Chamado aberto com sucesso."
    );
  });

  $("#start-form").addEventListener("submit", event => {
    event.preventDefault();

    if (selected) {
      save(
        event.currentTarget,
        actionUrl("realizar"),
        {},
        `Chamado #${selected.id} em andamento.`
      );
    }
  });

  $("#finish-form").addEventListener("submit", event => {
    event.preventDefault();

    if (!selected) return;

    const form = event.currentTarget;
    const data = new FormData(form);
    const solution = data.get("solution").trim();
    const tecs = data;getAll("tecs").map(Number);

    if (!solution) {
      return formError(
        form,
        "Descreva a solução antes de finalizar."
      );
    }

   if (!tecs) {
    return formError(
      form,
      "Atribua um tecnico ao chamado"
    )
   }

    save(
      form,
      actionUrl("fechar-chamado"),
      payload,
      `Chamado #${selected.id} finalizado com sucesso.`
    );
  });

  $("#priority-form").addEventListener("submit", event => {
    event.preventDefault();

    if (!selected || !authenticated) return;

    const form = event.currentTarget;

    const priority = Number(
      new FormData(form).get("priority")
    );

    const detailUrl =
      root.dataset.callsUrl +
      encodeURIComponent(selected.id) +
      "/";

    save(
      form,
      detailUrl,
      {priority},
      `Prioridade do chamado #${selected.id} atualizada.`,
      "PATCH"
    );
  });

  function applyUser(user) {
    const wasAuthenticated = authenticated;

    authenticated = Boolean(user);
    privateDashboard.hidden = !authenticated;

    if (!authenticated) {
      loadController?.abort();

      state.calls = [];

      $("#calls-body").replaceChildren();

      ["active", "open", "progress", "closed"].forEach(name => {
        $(`#count-${name}`).textContent = "—";
      });

      document
        .querySelectorAll(
          "#start-dialog, #finish-dialog, " +
          "#priority-dialog, #detail-dialog"
        )
        .forEach(dialog => {
          if (dialog.open) dialog.close();
        });

    } else if (!wasAuthenticated) {
      load();

    } else if (
      $("#list").getAttribute("aria-busy") !== "true"
    ) {
      render();
    }
  }

  auth?.subscribe(applyUser);

  if (auth) {
    auth.ready.then(applyUser);
  }
})();