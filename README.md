# Twitch/Kick Rewards — прототип (RU/EN/DE)

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
