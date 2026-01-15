document.addEventListener("DOMContentLoaded", () => {
  const BACKEND_URL = window.BACKEND_URL || "http://localhost:8000";
  const STEAM_KEY = "steamTradeLink";
  const KICK_KEY = "kickProfile";
  const TWITCH_KEY = "twitchProfile";
  const USER_ID_KEY = "currentUserId";
  const LOCALE_KEY = "uiLocale";
  const THEME_KEY = "uiTheme";
  const NOTIFY_KEY = "notifyPrefs";

  const followList = document.getElementById("followList");
  const copyBtn = document.getElementById("copyLink");
  const linkInput = document.getElementById("steamLink");
  const kickAction = document.getElementById("kickAction");
  const kickName = document.getElementById("kickName");
  const kickEmail = document.getElementById("kickEmail");
  const kickAvatar = document.getElementById("kickAvatar");
  const twitchAction = document.getElementById("twitchAction");
  const twitchName = document.getElementById("twitchName");
  const twitchHandle = document.getElementById("twitchHandle");
  const twitchAvatar = document.getElementById("twitchAvatar");
  const participationCard = document.getElementById("participationCard");
  const participationBadge = document.getElementById("participationBadge");
  const participationText = document.getElementById("participationText");
  const steamLink = document.getElementById("steamLink");
  const steamEdit = document.getElementById("steamEdit");
  const steamDelete = document.getElementById("steamDelete");
  const themeToggle = document.getElementById("themeToggle");
  const localeSelect = document.getElementById("localeSelect");
  const notifyToggle = document.getElementById("notifyToggle");
  const settingsLink = document.getElementById("settingsLink");
  const settingsSection = document.getElementById("settings");
  const settingsClose = document.getElementById("settingsClose");

  // --- Localization ---
  const translations = {
    ru: {
      page_title: "Drops | Morgan's version - Профиль",
      logo: "Drops | Morgan's version",
      top_user: "@twitchDrops_gitversionbot",
      profile_title: "Профиль",
      participation_label: "Участие в розыгрышах",
      participation_desc: "Вы можете участвовать в розыгрышах",
      participation_need: "Требуется привязать Kick/Twitch и Steam trade link",
      participation_badge_active: "Активно",
      participation_badge_inactive: "Неактивно",
      kick_label: "Kick аккаунт",
      kick_not_connected: "Kick не подключен",
      twitch_label: "Twitch аккаунт",
      twitch_not_connected: "Twitch не подключен",
      steam_label: "Ссылка обмена Steam",
      steam_desc: "Профиль и инвентарь должны быть открыты в настройках приватности Steam.",
      btn_copy: "Скопировать",
      btn_save: "Сохранить",
      btn_delete: "Удалить",
      btn_connect: "Подключить",
      btn_disconnect: "Отвязать",
      stat_prizes: "Призов",
      stat_total: "Суммарно",
      stat_month: "За месяц",
      streamers_label: "Отслеживаемые стримеры",
      streamers_empty_title: "Нет данных",
      streamers_empty_desc: "Отслеживаемых стримеров пока нет",
      followers_word: "подписчиков",
      show_all: "Показать все →",
      prizes_label: "Мои призы",
      prizes_empty_title: "Нет призов",
      prizes_empty_desc: "У вас пока нет полученных призов",
      menu_settings: "Настройки",
      menu_support: "Техподдержка",
      menu_stream: "Начать стримить",
      settings_title: "Настройки",
      settings_subtitle: "Тема, язык, уведомления",
      theme_title: "Тема",
      theme_desc: "Светлая или тёмная",
      theme_toggle: "Тёмная",
      lang_title: "Язык",
      lang_desc: "Интерфейс и подписи",
      notify_title: "Уведомления",
      notify_desc: "Получать апдейты о призах",
      close_btn: "Закрыть",
    },
    en: {
      page_title: "Drops | Morgan's version - Profile",
      logo: "Drops | Morgan's version",
      top_user: "@twitchDrops_gitversionbot",
      profile_title: "Profile",
      participation_label: "Raffle participation",
      participation_desc: "You can join giveaways",
      participation_need: "Connect Kick/Twitch and Steam trade link",
      participation_badge_active: "Active",
      participation_badge_inactive: "Inactive",
      kick_label: "Kick account",
      kick_not_connected: "Kick not connected",
      twitch_label: "Twitch account",
      twitch_not_connected: "Twitch not connected",
      steam_label: "Steam trade link",
      steam_desc: "Profile and inventory must be public in Steam privacy settings.",
      btn_copy: "Copy",
      btn_save: "Save",
      btn_delete: "Delete",
      btn_connect: "Connect",
      btn_disconnect: "Unlink",
      stat_prizes: "Prizes",
      stat_total: "Total",
      stat_month: "This month",
      streamers_label: "Followed streamers",
      streamers_empty_title: "No data",
      streamers_empty_desc: "You have no followed streamers yet",
      followers_word: "followers",
      show_all: "Show all →",
      prizes_label: "My prizes",
      prizes_empty_title: "No prizes",
      prizes_empty_desc: "You have no prizes yet",
      menu_settings: "Settings",
      menu_support: "Support",
      menu_stream: "Start streaming",
      settings_title: "Settings",
      settings_subtitle: "Theme, language, notifications",
      theme_title: "Theme",
      theme_desc: "Light or dark",
      theme_toggle: "Dark",
      lang_title: "Language",
      lang_desc: "UI and labels",
      notify_title: "Notifications",
      notify_desc: "Get prize updates",
      close_btn: "Close",
    },
  };
  let currentLocale = localStorage.getItem(LOCALE_KEY) || "ru";
  const t = (key) => (translations[currentLocale] || translations.ru)[key] || key;

  const applyLocale = (loc) => {
    currentLocale = loc;
    const dict = translations[loc] || translations.ru;
    document.querySelectorAll("[data-i18n]").forEach((el) => {
      const key = el.dataset.i18n;
      if (dict[key]) el.textContent = dict[key];
    });
    if (themeToggle && dict.theme_toggle) themeToggle.textContent = dict.theme_toggle;
    if (settingsClose && dict.close_btn) settingsClose.textContent = dict.close_btn;
    document.title = dict.page_title || document.title;
  };

  if (localeSelect) {
    localeSelect.value = currentLocale;
    localeSelect.addEventListener("change", (e) => {
      const loc = e.target.value;
      localStorage.setItem(LOCALE_KEY, loc);
      applyLocale(loc);
      renderKick(getProfile(KICK_KEY));
      renderTwitch(getProfile(TWITCH_KEY));
      updateParticipation();
      renderFollowList(localFollowFallback());
    });
  }
  applyLocale(currentLocale);

  // --- Theme toggle ---
  const applyTheme = (mode) => {
    document.body.dataset.theme = mode;
    if (themeToggle) {
      themeToggle.textContent = t("theme_toggle");
    }
  };
  const savedTheme = localStorage.getItem(THEME_KEY) || "dark";
  applyTheme(savedTheme);
  themeToggle?.addEventListener("click", () => {
    const next = document.body.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem(THEME_KEY, next);
    applyTheme(next);
  });

  // --- Helpers ---
  const getProfile = (key) => {
    try {
      return JSON.parse(localStorage.getItem(key) || "null");
    } catch {
      return null;
    }
  };

  copyBtn?.addEventListener("click", async () => {
    try {
      const value = linkInput?.value || "";
      if (!value) return;
      await navigator.clipboard.writeText(value);
      copyBtn.innerText = "✓";
      setTimeout(() => (copyBtn.innerText = "⧉"), 1200);
    } catch (err) {
      console.error("Не удалось скопировать:", err);
    }
  });

  // Auth params from URL
  const params = new URLSearchParams(window.location.search);
  const urlKickUser = params.get("kick_user");
  const urlKickEmail = params.get("kick_email");
  const urlKickId = params.get("kick_id");
  const urlKickAvatar = params.get("kick_avatar");
  const urlTwitchUser = params.get("twitch_user");
  const urlTwitchId = params.get("twitch_id");
  const urlTwitchAvatar = params.get("twitch_avatar");
  const urlUserId = params.get("user_id");

  if (urlKickUser) {
    localStorage.setItem(KICK_KEY, JSON.stringify({ user: urlKickUser, email: urlKickEmail, id: urlKickId, avatar: urlKickAvatar }));
  }
  if (urlTwitchUser) {
    localStorage.setItem(TWITCH_KEY, JSON.stringify({ user: urlTwitchUser, id: urlTwitchId, avatar: urlTwitchAvatar }));
  }
  if (urlUserId) {
    localStorage.setItem(USER_ID_KEY, urlUserId);
  }

  // --- Steam link ---
  const loadSteam = async () => {
    const local = localStorage.getItem(STEAM_KEY);
    if (local) {
      steamLink.value = local;
      return;
    }
    try {
      const userId = localStorage.getItem(USER_ID_KEY);
      const resp = await fetch(userId ? `${BACKEND_URL}/steam/link?user_id=${userId}` : `${BACKEND_URL}/steam/link`);
      if (resp.ok) {
        const data = await resp.json();
        if (data.steamTradeLink) {
          steamLink.value = data.steamTradeLink;
          localStorage.setItem(STEAM_KEY, data.steamTradeLink);
        }
      }
    } catch (e) {
      console.warn("Не удалось загрузить steam link", e);
    }
  };
  const persistSteam = async (value) => {
    localStorage.setItem(STEAM_KEY, value);
    try {
      const userId = localStorage.getItem(USER_ID_KEY);
      const target = userId ? `${BACKEND_URL}/steam/link?user_id=${userId}` : `${BACKEND_URL}/steam/link`;
      await fetch(target, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ steamTradeLink: value }),
      });
    } catch (e) {
      console.warn("Не удалось сохранить steam link", e);
    }
  };
  loadSteam();

  steamEdit?.addEventListener("click", () => {
    steamLink.value = (steamLink.value || "").trim();
    persistSteam(steamLink.value);
    updateParticipation();
  });
  steamDelete?.addEventListener("click", () => {
    steamLink.value = "";
    localStorage.removeItem(STEAM_KEY);
    persistSteam("");
    updateParticipation();
  });

  // --- Render Kick ---
  const renderKick = (profile) => {
    const connected = profile && profile.user;
    kickName.textContent = connected ? profile.user : t("kick_not_connected");
    kickEmail.textContent = connected ? profile.email || "@—" : "@—";
    kickAvatar.src = connected && profile.avatar ? profile.avatar : "https://i.pravatar.cc/64?img=11";
    if (connected) {
      kickAction.textContent = t("btn_disconnect");
      kickAction.classList.remove("btn-success", "ghost");
      kickAction.classList.add("btn-danger");
      kickAction.href = "#";
    } else {
      kickAction.textContent = t("btn_connect");
      kickAction.classList.add("btn-success", "ghost");
      kickAction.classList.remove("btn-danger");
      kickAction.href = `${BACKEND_URL}/auth/kick/start`;
    }
  };
  renderKick(getProfile(KICK_KEY));
  kickAction?.addEventListener("click", (e) => {
    const current = getProfile(KICK_KEY);
    if (current?.user) {
      e.preventDefault();
      localStorage.removeItem(KICK_KEY);
      renderKick(null);
      loadFollows();
      updateParticipation();
    }
  });

  // --- Render Twitch ---
  const renderTwitch = (profile) => {
    const connected = profile && profile.user;
    twitchName.textContent = connected ? profile.user : t("twitch_not_connected");
    twitchHandle.textContent = connected ? `@${profile.user || ""}` : "@—";
    twitchAvatar.src = connected && profile.avatar ? profile.avatar : "https://i.pravatar.cc/64?img=11";
    if (connected) {
      twitchAction.textContent = t("btn_disconnect");
      twitchAction.classList.remove("btn-success", "ghost");
      twitchAction.classList.add("btn-danger");
      twitchAction.href = "#";
    } else {
      twitchAction.textContent = t("btn_connect");
      twitchAction.classList.add("btn-success", "ghost");
      twitchAction.classList.remove("btn-danger");
      twitchAction.href = `${BACKEND_URL}/auth/twitch/start`;
    }
  };
  renderTwitch(getProfile(TWITCH_KEY));
  twitchAction?.addEventListener("click", (e) => {
    const current = getProfile(TWITCH_KEY);
    if (current?.user) {
      e.preventDefault();
      localStorage.removeItem(TWITCH_KEY);
      renderTwitch(null);
      loadFollows();
      updateParticipation();
    }
  });

  // --- Participation ---
  const updateParticipation = () => {
    const hasKick = !!getProfile(KICK_KEY)?.user;
    const hasTwitch = !!getProfile(TWITCH_KEY)?.user;
    const hasSteam = steamLink && steamLink.value && steamLink.value.trim().length > 0;
    const active = (hasKick || hasTwitch) && hasSteam;
    if (active) {
      participationCard.classList.remove("inactive");
      participationBadge.classList.remove("badge-danger");
      participationBadge.classList.add("badge-success");
      participationBadge.textContent = t("participation_badge_active");
      participationText.textContent = t("participation_desc");
    } else {
      participationCard.classList.add("inactive");
      participationBadge.classList.remove("badge-success");
      participationBadge.classList.add("badge-danger");
      participationBadge.textContent = t("participation_badge_inactive");
      participationText.textContent = t("participation_need");
    }
  };
  updateParticipation();

  // --- Notifications toggle ---
  if (notifyToggle) {
    const savedNotify = localStorage.getItem(NOTIFY_KEY) === "on";
    notifyToggle.checked = savedNotify;
    notifyToggle.addEventListener("change", (e) => {
      localStorage.setItem(NOTIFY_KEY, e.target.checked ? "on" : "off");
    });
  }

  // --- Followed streamers ---
  const localFollowFallback = () => {
    const res = [];
    const kick = getProfile(KICK_KEY);
    if (kick?.user) {
      res.push({ platform: "kick", login: kick.user, display_name: kick.user, followers: 0, avatar: kick.avatar });
    }
    const tw = getProfile(TWITCH_KEY);
    if (tw?.user) {
      res.push({ platform: "twitch", login: tw.user, display_name: tw.user, followers: 0, avatar: tw.avatar });
    }
    return res;
  };

  const renderFollowList = (items) => {
    if (!followList) return;
    followList.innerHTML = "";
    if (!items || !items.length) {
      const empty = document.createElement("div");
      empty.className = "empty-state";
      empty.innerHTML = `<div class="title">${t("streamers_empty_title")}</div><div class="muted">${t("streamers_empty_desc")}</div>`;
      followList.appendChild(empty);
      return;
    }
    items.forEach((item) => {
      const row = document.createElement("div");
      row.className = "streamer";
      row.innerHTML = `
        <div class="streamer-meta">
          <img src="${item.avatar || "https://i.pravatar.cc/48?img=55"}" alt="${item.display_name || item.login}">
          <div>
            <div class="title">${item.display_name || item.login}</div>
            <div class="muted">${item.platform} · ${item.followers ?? 0} ${t("followers_word")}</div>
          </div>
        </div>
        <button class="icon-btn" title="Управление">👤</button>
      `;
      followList.appendChild(row);
    });
  };

  const loadFollows = async () => {
    try {
      const userId = localStorage.getItem(USER_ID_KEY);
      const url = userId ? `${BACKEND_URL}/streamers/following?user_id=${userId}` : `${BACKEND_URL}/streamers/following`;
      const resp = await fetch(url);
      const base = resp.ok ? await resp.json() : [];
      const fallback = localFollowFallback();
      const merged = [...(Array.isArray(base) ? base : [])];
      const keys = new Set(merged.map((x) => `${x.platform}:${x.login}`));
      fallback.forEach((x) => {
        const k = `${x.platform}:${x.login}`;
        if (!keys.has(k)) merged.push(x);
      });
      renderFollowList(merged.length ? merged : fallback);
    } catch (e) {
      console.warn("Не удалось загрузить отслеживаемых стримеров", e);
      renderFollowList(localFollowFallback());
    }
  };
  loadFollows();

  // --- Settings panel open/close ---
  const showSettings = () => {
    settingsSection?.classList.add("active");
    requestAnimationFrame(() => settingsSection?.scrollIntoView({ behavior: "smooth" }));
  };
  const hideSettings = () => {
    settingsSection?.classList.remove("active");
  };
  settingsLink?.addEventListener("click", (e) => {
    e.preventDefault();
    showSettings();
  });
  settingsClose?.addEventListener("click", hideSettings);

  // Live updates
  kickAction?.addEventListener("click", () => setTimeout(updateParticipation, 200));
  steamLink?.addEventListener("input", updateParticipation);
  steamLink?.addEventListener("blur", () => {
    steamLink.value = (steamLink.value || "").trim();
    persistSteam(steamLink.value);
    updateParticipation();
  });
});
