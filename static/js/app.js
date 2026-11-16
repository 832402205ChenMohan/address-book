/* Address Book client-side logic: rendering, form handling, import and export. */

const state = {
  contacts: [],
  stats: { contacts: 0, favorites: 0, methods: 0 },
  keyword: "",
  favoriteOnly: false,
};

const METHOD_KINDS = ["phone", "email", "wechat", "address", "other"];
const METHOD_LABELS = {
  phone: "PHONE",
  email: "EMAIL",
  wechat: "WECHAT",
  address: "ADDR",
  other: "OTHER",
};
const PALETTE = ["#159386", "#2f7fd9", "#b97a1f", "#8a4ecd", "#cf5a47", "#3d8f57", "#c2487d"];

const el = {
  list: document.getElementById("list"),
  empty: document.getElementById("empty"),
  search: document.getElementById("search"),
  favorites: document.getElementById("btn-favorites"),
  counter: document.getElementById("counter"),
  statContacts: document.getElementById("stat-contacts"),
  statFavorites: document.getElementById("stat-favorites"),
  statMethods: document.getElementById("stat-methods"),
  dialog: document.getElementById("contact-dialog"),
  form: document.getElementById("contact-form"),
  dialogTitle: document.getElementById("dialog-title"),
  fieldId: document.getElementById("f-id"),
  name: document.getElementById("f-name"),
  company: document.getElementById("f-company"),
  title: document.getElementById("f-title"),
  notes: document.getElementById("f-notes"),
  favorite: document.getElementById("f-favorite"),
  methods: document.getElementById("methods"),
  importInput: document.getElementById("import-input"),
  toast: document.getElementById("toast"),
};

let toastTimer = null;

function toast(message, isError) {
  el.toast.textContent = message;
  el.toast.classList.toggle("error", Boolean(isError));
  el.toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.toast.classList.remove("show"), 3000);
}

async function api(path, options) {
  const response = await fetch(path, options);
  let payload = null;
  try {
    payload = await response.json();
  } catch (error) {
    payload = null;
  }
  if (!response.ok) {
    throw new Error((payload && payload.error) || "Request failed with status " + response.status);
  }
  return payload;
}

function initials(name) {
  const parts = String(name || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function colorFor(name) {
  let hash = 0;
  const text = String(name || "");
  for (let index = 0; index < text.length; index += 1) {
    hash = (hash * 31 + text.charCodeAt(index)) % 9973;
  }
  return PALETTE[hash % PALETTE.length];
}

function buildCard(contact) {
  const card = document.createElement("article");
  card.className = "card";
  card.dataset.id = contact.id;

  const head = document.createElement("div");
  head.className = "card-head";

  const avatar = document.createElement("div");
  avatar.className = "avatar";
  avatar.textContent = initials(contact.name);
  avatar.style.background = colorFor(contact.name);

  const who = document.createElement("div");
  who.className = "who";

  const name = document.createElement("h2");
  name.className = "name";
  name.textContent = contact.name;
  if (contact.is_favorite) {
    const badge = document.createElement("span");
    badge.className = "fav-badge";
    badge.textContent = "FAVORITE";
    name.appendChild(badge);
  }

  const org = document.createElement("p");
  org.className = "org";
  const orgText = [contact.company, contact.title].filter(Boolean).join(" · ");
  org.textContent = orgText || "No company recorded";
  org.title = orgText;

  who.append(name, org);

  const star = document.createElement("button");
  star.type = "button";
  star.className = "star-btn" + (contact.is_favorite ? " on" : "");
  star.textContent = contact.is_favorite ? "\u2605" : "\u2606";
  star.title = contact.is_favorite ? "Remove from favorites" : "Add to favorites";
  star.addEventListener("click", () => toggleFavorite(contact));
  star.dataset.role = "star";

  head.append(avatar, who, star);
  card.appendChild(head);

  const chips = document.createElement("div");
  chips.className = "chips";
  if (contact.methods.length === 0) {
    const hint = document.createElement("span");
    hint.className = "method-chip";
    hint.innerHTML = '<span class="tag">NONE</span><span class="value">No contact method yet</span>';
    chips.appendChild(hint);
  } else {
    contact.methods.slice(0, 6).forEach((method) => {
      const chip = document.createElement("span");
      chip.className = "method-chip";
      const tag = document.createElement("span");
      tag.className = "tag";
      tag.textContent = METHOD_LABELS[method.kind] || "OTHER";
      const value = document.createElement("span");
      value.className = "value";
      value.textContent = method.value;
      value.title = method.label ? method.value + " (" + method.label + ")" : method.value;
      chip.append(tag, value);
      chips.appendChild(chip);
    });
    if (contact.methods.length > 6) {
      const more = document.createElement("span");
      more.className = "method-chip";
      more.innerHTML = '<span class="value">+' + (contact.methods.length - 6) + " more</span>";
      chips.appendChild(more);
    }
  }
  card.appendChild(chips);

  if (contact.notes) {
    const notes = document.createElement("p");
    notes.className = "notes";
    notes.textContent = contact.notes;
    card.appendChild(notes);
  }

  const actions = document.createElement("div");
  actions.className = "card-actions";

  const edit = document.createElement("button");
  edit.type = "button";
  edit.className = "link-btn";
  edit.textContent = "Edit";
  edit.addEventListener("click", () => openDialog(contact));

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "link-btn danger";
  remove.textContent = "Delete";
  remove.addEventListener("click", () => removeContact(contact));

  actions.append(edit, remove);
  card.appendChild(actions);

  return card;
}

function render() {
  el.list.innerHTML = "";
  state.contacts.forEach((contact) => el.list.appendChild(buildCard(contact)));

  const total = state.contacts.length;
  el.counter.textContent = total + (total === 1 ? " contact" : " contacts");
  el.empty.classList.toggle("hidden", total > 0);

  el.statContacts.textContent = state.stats.contacts;
  el.statFavorites.textContent = state.stats.favorites;
  el.statMethods.textContent = state.stats.methods;
}

async function loadContacts() {
  const params = new URLSearchParams();
  if (state.keyword) params.set("q", state.keyword);
  if (state.favoriteOnly) params.set("favorite", "1");
  const data = await api("/api/contacts?" + params.toString());
  state.contacts = data.contacts;
  state.stats = data.stats;
  render();
}

async function toggleFavorite(contact) {
  try {
    const updated = await api("/api/contacts/" + contact.id + "/favorite", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ favorite: !contact.is_favorite }),
    });
    toast(updated.is_favorite ? contact.name + " added to favorites" : contact.name + " removed from favorites");
    await loadContacts();
  } catch (error) {
    toast(error.message, true);
  }
}

async function removeContact(contact) {
  if (!window.confirm("Delete " + contact.name + " and all of their contact methods?")) {
    return;
  }
  try {
    await api("/api/contacts/" + contact.id, { method: "DELETE" });
    toast(contact.name + " deleted");
    await loadContacts();
  } catch (error) {
    toast(error.message, true);
  }
}

function addMethodRow(method) {
  const row = document.createElement("div");
  row.className = "method-row";

  const select = document.createElement("select");
  select.className = "m-kind";
  METHOD_KINDS.forEach((kind) => {
    const option = document.createElement("option");
    option.value = kind;
    option.textContent = kind.charAt(0).toUpperCase() + kind.slice(1);
    select.appendChild(option);
  });
  select.value = (method && method.kind) || "phone";

  const label = document.createElement("input");
  label.className = "m-label";
  label.placeholder = "label (mobile, work)";
  label.value = (method && method.label) || "";

  const value = document.createElement("input");
  value.className = "m-value";
  value.placeholder = "phone number, email, address...";
  value.value = (method && method.value) || "";

  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "icon-btn remove";
  remove.textContent = "\u00d7";
  remove.title = "Remove this method";
  remove.addEventListener("click", () => row.remove());

  row.append(select, label, value, remove);
  el.methods.appendChild(row);
  return row;
}

function openDialog(contact) {
  el.form.reset();
  el.methods.innerHTML = "";
  el.dialogTitle.textContent = contact ? "Edit Contact" : "New Contact";
  el.fieldId.value = contact ? contact.id : "";
  el.name.value = contact ? contact.name : "";
  el.company.value = contact && contact.company ? contact.company : "";
  el.title.value = contact && contact.title ? contact.title : "";
  el.notes.value = contact && contact.notes ? contact.notes : "";
  el.favorite.checked = Boolean(contact && contact.is_favorite);

  if (contact && contact.methods.length) {
    contact.methods.forEach((method) => addMethodRow(method));
  } else {
    addMethodRow(null);
  }

  el.dialog.showModal();
  el.name.focus();
}

function collectPayload() {
  const methods = [];
  el.methods.querySelectorAll(".method-row").forEach((row) => {
    const kind = row.querySelector(".m-kind").value;
    const label = row.querySelector(".m-label").value.trim();
    const value = row.querySelector(".m-value").value.trim();
    if (value) {
      methods.push({ kind: kind, label: label, value: value });
    }
  });
  return {
    name: el.name.value.trim(),
    company: el.company.value.trim(),
    title: el.title.value.trim(),
    notes: el.notes.value.trim(),
    is_favorite: el.favorite.checked,
    methods: methods,
  };
}

async function submitForm(event) {
  event.preventDefault();
  const payload = collectPayload();
  if (!payload.name) {
    toast("Contact name is required", true);
    el.name.focus();
    return;
  }
  const contactId = el.fieldId.value;
  try {
    if (contactId) {
      await api("/api/contacts/" + contactId, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      toast(payload.name + " updated");
    } else {
      await api("/api/contacts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      toast(payload.name + " saved");
    }
    el.dialog.close();
    await loadContacts();
  } catch (error) {
    toast(error.message, true);
  }
}

async function importFile(file) {
  const form = new FormData();
  form.append("file", file);
  try {
    const result = await api("/api/import", { method: "POST", body: form });
    const parts = ["Imported " + result.imported];
    if (result.merged) parts.push("merged " + result.merged);
    if (result.skipped) parts.push("skipped " + result.skipped);
    toast(parts.join(", ") + " row(s)");
    await loadContacts();
  } catch (error) {
    toast(error.message, true);
  }
}

function debounce(fn, delay) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

el.search.addEventListener(
  "input",
  debounce(() => {
    state.keyword = el.search.value.trim();
    loadContacts().catch((error) => toast(error.message, true));
  }, 250)
);

el.favorites.addEventListener("click", () => {
  state.favoriteOnly = !state.favoriteOnly;
  el.favorites.setAttribute("aria-pressed", String(state.favoriteOnly));
  loadContacts().catch((error) => toast(error.message, true));
});

document.getElementById("btn-new").addEventListener("click", () => openDialog(null));
document.getElementById("btn-close").addEventListener("click", () => el.dialog.close());
document.getElementById("btn-cancel").addEventListener("click", () => el.dialog.close());
document.getElementById("btn-add-method").addEventListener("click", () => addMethodRow(null));
el.form.addEventListener("submit", submitForm);

document.getElementById("btn-import").addEventListener("click", () => el.importInput.click());
el.importInput.addEventListener("change", () => {
  const file = el.importInput.files[0];
  if (file) importFile(file);
  el.importInput.value = "";
});

document.getElementById("btn-export").addEventListener("click", async () => {
  if (state.stats.contacts === 0) {
    toast("Nothing to export yet", true);
    return;
  }
  window.location.href = "/api/export";
  toast("Export started: contacts.xlsx");
});

loadContacts().catch((error) => toast(error.message, true));
