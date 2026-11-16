(() => {
  "use strict";
  const config = document.getElementById("auth-config");
  if (!config) return;
  const state = {user: null};
  let expirationTask = null;
  let checkingUser = null;
  let generation = 0;
  let loggingOut = false;
  const subscribers = new Set();
  const csrf = () => config.querySelector("[name=csrfmiddlewaretoken]").value;

  function notifyUser(user) {
    state.user = user;
    const signedIn = Boolean(user);
    const login = document.getElementById("account-login");
    const logout = document.getElementById("account-logout");
    const calls = document.getElementById("account-calls");
    const maintenance = document.getElementById("account-maintenance");
    const username = document.getElementById("account-username");
    const notice = document.getElementById("auth-notice");
    if (login) login.hidden = signedIn;
    if (logout) logout.hidden = !signedIn;
    const capabilities = user?.capabilities || {};
    const groups = Array.isArray(user?.groups) ? user.groups : [];
    const isTeam = groups.includes("Tecnico") || groups.includes("Administrativo");
    if (calls) {
      calls.hidden = !signedIn || !(capabilities.calls_view ?? isTeam);
    }
    if (maintenance) {
      maintenance.hidden = !signedIn || !(capabilities.maintenance_view ?? isTeam);
    }
    if (username) {
      username.hidden = !signedIn;
      username.textContent = user?.username || user?.nome || user?.name || user?.email || "Usuário autenticado";
    }
    if (notice) notice.hidden = signedIn;
    subscribers.forEach(callback => callback(user));
  }

  function url(value) {
    if (!value) throw new Error("Configure as URLs da autenticação no base.html.");
    const result = new URL(value, location.origin);
    if (result.origin !== location.origin) throw new Error("A autenticação precisa usar o mesmo domínio do sistema.");
    return result;
  }

  async function rawFetch(value, options = {}) {
    const controller = new AbortController();
    let timedOut = false;
    const abort = () => controller.abort();
    if (options.signal?.aborted) abort();
    options.signal?.addEventListener("abort", abort, {once: true});
    const timer = setTimeout(() => {timedOut = true; abort();}, 15000);
    try {
      return await fetch(url(value), {
        ...options,
        signal: controller.signal,
        credentials: "include",
        cache: "no-store",
        headers: {
          Accept: "application/json",
          ...(options.method && options.method !== "GET" ? {"X-CSRFToken": csrf()} : {}),
          ...options.headers,
        },
      });
    } catch (error) {
      if (timedOut) throw new Error("O servidor de autenticação demorou para responder.");
      if (error instanceof TypeError) throw new Error("Não foi possível conectar à API de autenticação.");
      throw error;
    } finally {
      clearTimeout(timer);
      options.signal?.removeEventListener("abort", abort);
    }
  }

  async function readJSON(response) {
    const isJSON = (response.headers.get("content-type") || "").includes("application/json");
    if (!isJSON) throw new Error("A rota da API de autenticação não retornou JSON.");
    return response.json();
  }

  function errorText(data) {
    if (typeof data === "string") return data;
    if (Array.isArray(data)) return data.map(errorText).join(" ");
    if (data && typeof data === "object") return Object.values(data).map(errorText).join("\n");
    return "Não foi possível concluir a autenticação.";
  }

  async function clearCookies() {
    const response = await rawFetch(config.dataset.logoutUrl, {method: "POST"});
    if (!response.ok) throw new Error(errorText(await readJSON(response)));
  }

  async function expireSession() {
    if (expirationTask) return expirationTask;
    const hadUser = Boolean(state.user);
    generation++;
    notifyUser(null);
    if (hadUser) {
      const status = document.getElementById("account-status");
      if (status) {
        status.hidden = false;
        status.textContent = "Sua sessão expirou. Entre novamente.";
      }
    }
    // HttpOnly cookies are cleared by the existing logout API.
    // The private interface is already closed even if this request fails.
    expirationTask = clearCookies().catch(error => {
      console.warn("Não foi possível limpar os cookies da sessão:", error.message);
    });
    try { await expirationTask; }
    finally { expirationTask = null; }
  }

  async function authenticatedFetch(value, options = {}) {
    const response = await rawFetch(value, options);
    // Do not renew the expired access token automatically.
    if (response.status === 401 && !loggingOut) await expireSession();
    return response;
  }

  async function currentUser() {
    if (checkingUser) return checkingUser;
    const startedGeneration = generation;
    checkingUser = (async () => {
      const response = await rawFetch(config.dataset.userUrl);
      if (startedGeneration !== generation) return state.user;
      // UsuarioView requires authentication only: 403 may represent a missing
      // cookie when DRF has no WWW-Authenticate header.
      if ([401, 403].includes(response.status)) {
        await expireSession();
        return null;
      }
      const data = await readJSON(response);
      if (!response.ok) throw new Error(errorText(data));
      if (startedGeneration !== generation) return state.user;
      notifyUser(data);
      return data;
    })();
    try { return await checkingUser; }
    finally { checkingUser = null; }
  }

  // Cookies are HttpOnly. Check the server while signed in, including when
  // returning to a suspended/background tab; never decode cookies in JS.
  function checkSession() {
    if (!state.user || loggingOut || document.hidden) return;
    currentUser().catch(() => {
      // Network errors do not establish that the token expired.
    });
  }
  setInterval(checkSession, 15000);
  window.addEventListener("focus", checkSession);
  window.addEventListener("pageshow", checkSession);
  document.addEventListener("visibilitychange", checkSession);

  const auth = {
    get user() {return state.user;},
    fetch: authenticatedFetch,
    currentUser,
    subscribe(callback) {
      subscribers.add(callback);
      return () => subscribers.delete(callback);
    },
  };
  window.SECITECAuth = auth;

  auth.ready = currentUser().catch(error => {
    notifyUser(null);
    const status = document.getElementById("account-status");
    if (status) status.textContent = error.message;
    return null;
  }).finally(() => {
    const status = document.getElementById("account-status");
    if (status?.textContent.trim() === "Verificando conta…") status.hidden = true;
  });

  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    const feedback = loginForm.querySelector(".error");
    const submit = loginForm.querySelector("[type=submit]");
    auth.ready.then(user => {if (user) location.assign(config.dataset.homeUrl || "/");});
    loginForm.addEventListener("submit", async event => {
      event.preventDefault();
      if (submit.disabled) return;
      submit.disabled = true;
      submit.textContent = "Entrando…";
      feedback.hidden = true;
      try {
        // Aguarda a verificação inicial antes de criar novos cookies.
        await auth.ready;
        const values = new FormData(loginForm);
        const response = await rawFetch(config.dataset.loginUrl, {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            [loginForm.dataset.identityField || "username"]: values.get("identity").trim(),
            password: values.get("password"),
          }),
        });
        const data = await readJSON(response);
        if (!response.ok) throw new Error(errorText(data));
        // Confirma que o navegador armazenou os cookies e a API reconhece o usuário.
        if (!await currentUser()) throw new Error("O login respondeu com sucesso, mas os cookies não foram reconhecidos. Confira a configuração de cookies do servidor.");
        location.assign(config.dataset.homeUrl || "/");
      } catch (error) {
        feedback.textContent = error.message;
        feedback.hidden = false;
      } finally {
        submit.disabled = false;
        submit.textContent = "Entrar →";
      }
    });
  }

  const logout = document.getElementById("account-logout");
  logout?.addEventListener("click", async () => {
    if (loggingOut) return;
    loggingOut = true;
    logout.disabled = true;
    try {
      await auth.ready;
      generation++;
      if (expirationTask) await expirationTask;
      await clearCookies();
      notifyUser(null);
      location.assign(config.dataset.homeUrl || "/");
    } catch (error) {
      const status = document.getElementById("account-status");
      if (status) {status.hidden = false; status.textContent = error.message;}
    } finally {
      loggingOut = false;
      logout.disabled = false;
    }
  });
})();
