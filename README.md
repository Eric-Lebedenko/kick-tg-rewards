# Twitch/Kick Rewards — прототип (RU/EN/DE)

Навигация / Navigation / Navigation:
- [Русский](#русский)
- [English](#english)
- [Deutsch](#deutsch)

## Русский

Минимальный стек: FastAPI (OAuth Kick/Twitch) + SQLModel/SQLite, статичный фронт профиля, телеграм-бот. Порты по умолчанию: API `8000`, фронт `8001`.

Minimal stack: FastAPI (Kick/Twitch OAuth) + SQLModel/SQLite, static profile front-end, Telegram bot. Default ports: API `8000`, front `8001`.

Minimaler Stack: FastAPI (Kick/Twitch OAuth) + SQLModel/SQLite, statische Profil-UI, Telegram-Bot. Standard-Ports: API `8000`, Frontend `8001`.

## Что внутри / What’s inside / Was ist drin
- `backend-python/` — FastAPI: PKCE OAuth Kick, OAuth Twitch, SQLModel + SQLite (User, AuthToken, Follow, steam_trade_link), моковые rewards, health.
- `backend-csharp/` — ASP.NET Core minimal API (optional): health + rewards (in-memory).
- `frontend/` — статичная страница профиля: Kick/Twitch карточки, Steam trade link, статус участия, локализация RU/EN/DE, переключение темы, список отслеживаемых.
- `bot/` — Telegram-бот (python-telegram-bot) с кнопками «Открыть» (WebApp) и «Авторизоваться в Kick».

## Запуск локально / Run locally / Lokal starten
### Python API
```bash
cd backend-python
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Проверка: `http://localhost:8000/health` → `{ "ok": true }`. БД: `sqlite:///./db.sqlite3` (меняется через `DB_URL`), таблицы создаются сами.

### Фронтенд
```bash
python -m http.server 8001 --directory frontend
```
Открыть `http://localhost:8001`. После успешной авторизации Kick/Twitch фронт читает параметры (`kick_user`, `twitch_user`, `user_id`, аватары) из URL и обновляет карточки.

### Telegram-бот
```bash
cd bot
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set BOT_TOKEN=ваш_токен
set FRONTEND_URL=http://localhost:8001
set BACKEND_URL=http://localhost:8000
python main.py
```
Команды: `/start`, `/profile`. Для инлайн-кнопок нужны публичные https-URL (ngrok/хостинг).

### C# API (опционально)
```bash
cd backend-csharp
dotnet restore
dotnet run --urls "http://localhost:5000"
```
Проверка: `http://localhost:5000/health`.

## Основные эндпоинты (Python) / Key endpoints
- `GET /health`
- `GET/POST /rewards`, `GET/DELETE /rewards/{id}` — моковые награды
- `GET /auth/kick/start`, `GET /auth/kick/callback` — PKCE OAuth Kick, сохраняет профиль/токены, редиректит на FRONTEND_URL с `user_id`
- `GET /auth/twitch/start`, `GET /auth/twitch/callback` — OAuth Twitch, сохраняет профиль/токены, редиректит на FRONTEND_URL с `user_id`
- `GET /steam/link`, `POST /steam/link` — хранение Steam trade link в БД (по `user_id`)
- `GET /streamers/following` — отдаёт сохранённые подписки (Follow) для пользователя; фронт добавляет фолбек из локальных Kick/Twitch аккаунтов

## Настройка Kick OAuth / Kick OAuth setup
`backend-python/.env`:
```
KICK_CLIENT_ID=...
KICK_CLIENT_SECRET=...
KICK_REDIRECT_URI=http://localhost:8000/auth/kick/callback
KICK_AUTH_URL=https://id.kick.com/oauth/authorize
KICK_TOKEN_URL=https://id.kick.com/oauth/token
KICK_USER_URL=https://api.kick.com/public/v1/users
KICK_SCOPE=user:read
FRONTEND_URL=http://localhost:8001
```
Redirect URI в консоли Kick должен совпадать точно. После Allow редирект на FRONTEND_URL с параметрами профиля и `user_id`.

## Настройка Twitch OAuth / Twitch OAuth setup
`backend-python/.env`:
```
TWITCH_CLIENT_ID=...
TWITCH_CLIENT_SECRET=...
TWITCH_REDIRECT_URI=http://localhost:8000/auth/twitch/callback
FRONTEND_URL=http://localhost:8001
```
Redirect URI в консоли Twitch — точное совпадение.

## Фронтенд — основные фичи / Frontend highlights
- Локализация RU/EN/DE (через `data-i18n`), переключатель языка.
- Переключение темы (dark/light), состояние хранится в localStorage.
- Карточки Kick/Twitch: аватар, ник, кнопка подключить/отвязать; состояние берётся из redirect-параметров и localStorage.
- Steam trade link: ввод/копирование/удаление, синхронизация в API + localStorage.
- Статус участия: зелёный, если привязан Kick или Twitch и есть Steam link.
- Список отслеживаемых: данные с `/streamers/following?user_id=...` + фолбек из локально привязанных аккаунтов.

## Что дальше
- Вынести бэкенд/фронт на публичный https (ngrok/хостинг), подключить бота к прод-URL.
- Добавить реальное получение подписок из Kick/Twitch, refresh токены, auth/JWT для клиентов.
- Расширить схему наград/призов и хранить в БД.

## Лицензия
Проект распространяется по лицензии MIT (см. файл `LICENSE`).

## Как внести вклад
- Форк или ветка от `main`.
- Соблюдать стиль: форматирование по умолчанию (black/ruff для Python, eslint/prettier не подключены), ASCII-комментарии.
- PR: короткое описание задачи, список изменений, шаги проверки.
- Не коммитить `.env` и любые токены — используйте `.env.example`.

## Безопасность и секреты
- Все токены/ключи хранить только локально в `.env`; примеры — в `.env.example`.
- Для публичных кнопок бота использовать публичный https (ngrok/хостинг).
- Перед публикацией проверяйте, что в репозитории нет секретов (`git status`, поиск по `TOKEN`, `SECRET`).

## Roadmap и ветки
- Roadmap: см. `ROADMAP.md`.
- Ветки и роли: см. `TEAM_BRANCHES.md`.

---

## English
Minimal stack: FastAPI (Kick/Twitch OAuth) + SQLModel/SQLite, static profile front-end, Telegram bot. Default ports: API `8000`, front `8001`.

What’s inside:
- `backend-python/`: FastAPI with PKCE OAuth Kick, OAuth Twitch, SQLModel + SQLite (User, AuthToken, Follow, steam_trade_link), mock rewards, health.
- `backend-csharp/`: ASP.NET Core minimal API (optional): health + rewards (in-memory).
- `frontend/`: static profile page with Kick/Twitch cards, Steam trade link, participation badge, localization RU/EN/DE, theme switcher, followed list.
- `bot/`: Telegram bot (python-telegram-bot) with “Open” WebApp and “Authorize in Kick”.

Run locally:
- API: `cd backend-python && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000`
- Front: `python -m http.server 8001 --directory frontend`
- Bot: `cd bot && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && set BOT_TOKEN=... && set FRONTEND_URL=http://localhost:8001 && set BACKEND_URL=http://localhost:8000 && python main.py`
- C# (optional): `cd backend-csharp && dotnet restore && dotnet run --urls "http://localhost:5000"`

Key endpoints (Python):
- `GET /health`
- `GET/POST /rewards`, `GET/DELETE /rewards/{id}`
- `GET /auth/kick/start`, `/auth/kick/callback` (PKCE, saves profile/tokens, redirects with `user_id`)
- `GET /auth/twitch/start`, `/auth/twitch/callback` (saves profile/tokens, redirects with `user_id`)
- `GET/POST /steam/link` (per `user_id`)
- `GET /streamers/following` (saved follows; front adds local fallback)

Front highlights:
- Localization RU/EN/DE (`data-i18n`), theme switch (dark/light).
- Kick/Twitch cards with avatar/nick, connect/unlink; state from redirect params + localStorage.
- Steam trade link edit/copy/delete, synced to API + localStorage.
- Participation badge: active if Kick or Twitch + Steam link.
- Followed list from API + local fallback.

Security:
- Keep secrets in local `.env`; use `.env.example` for placeholders.
- Use public https for bot buttons (ngrok/hosting).
- Never commit tokens/DB (`.env` and `db.sqlite3` are gitignored).

---

## Deutsch
Minimaler Stack: FastAPI (Kick/Twitch OAuth) + SQLModel/SQLite, statische Profilseite, Telegram-Bot. Standard-Ports: API `8000`, Frontend `8001`.

Inhalt:
- `backend-python/`: FastAPI mit PKCE OAuth Kick, OAuth Twitch, SQLModel + SQLite (User, AuthToken, Follow, steam_trade_link), Mock-Rewards, Health.
- `backend-csharp/`: ASP.NET Core Minimal-API (optional): Health + Rewards (In-Memory).
- `frontend/`: statische Profilseite mit Kick/Twitch-Karten, Steam-Trade-Link, Teilnahme-Status, Lokalisierung RU/EN/DE, Theme-Switch, Follow-Liste.
- `bot/`: Telegram-Bot mit „Open“ (WebApp) und „In Kick autorisieren“.

Lokal starten:
- API: `cd backend-python && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000`
- Frontend: `python -m http.server 8001 --directory frontend`
- Bot: `cd bot && python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt && set BOT_TOKEN=... && set FRONTEND_URL=http://localhost:8001 && set BACKEND_URL=http://localhost:8000 && python main.py`
- C# (optional): `cd backend-csharp && dotnet restore && dotnet run --urls "http://localhost:5000"`

Wichtige Endpunkte (Python):
- `GET /health`
- `GET/POST /rewards`, `GET/DELETE /rewards/{id}`
- `GET /auth/kick/start`, `/auth/kick/callback` (PKCE, speichert Profil/Tokens, Redirect mit `user_id`)
- `GET /auth/twitch/start`, `/auth/twitch/callback` (speichert Profil/Tokens, Redirect mit `user_id`)
- `GET/POST /steam/link` (pro `user_id`)
- `GET /streamers/following` (gespeicherte Follows; Front fügt lokalen Fallback hinzu)

Frontend-Highlights:
- Lokalisierung RU/EN/DE (`data-i18n`), Theme-Switch (dark/light).
- Kick/Twitch-Karten mit Avatar/Nickname, Connect/Unlink; Zustand aus Redirect + localStorage.
- Steam-Trade-Link: Bearbeiten/Kopieren/Löschen, Sync zu API + localStorage.
- Teilnahme-Status: aktiv, wenn Kick oder Twitch + Steam-Link.
- Follow-Liste aus API + lokalem Fallback.

Sicherheit:
- Secrets nur lokal in `.env`; `.env.example` als Vorlage.
- Öffentliche https-URL für Bot-Buttons (ngrok/Hosting).
- Keine Tokens/DB commiten (`.env`, `db.sqlite3` stehen in .gitignore).
