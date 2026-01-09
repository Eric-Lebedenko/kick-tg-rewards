# 🎮 Drops Crypto

**Full-stack platform for crypto drops with Twitch OAuth and wallet integration.**  
Designed for streamers, viewers, and Web3-native reward mechanics.

---

## 🌍 Languages / Языки / Sprachen / Języki

- [🇷🇺 Русский](#-русский)
- [🇬🇧 English](#-english)
- [🇩🇪 Deutsch](#-deutsch)
- [🇵🇱 Polski](#-polski)

---

## 🧭 Project Structure

```text
drops-crypto/
├── drops-crypto-api/   # Backend (NestJS, Prisma, PostgreSQL)
├── drops-crypto-app/   # Mobile App (React Native, Expo)
└── README.md
```

---

## 🔐 Core Features

- Twitch OAuth 2.0 authentication
- Secure JWT-based authorization
- Crypto wallet linking (EVM-ready)
- Stream-based reward logic (Drops)
- Mobile-first UX (iOS / Android)
- Scalable backend architecture

---

## 🧩 Architecture Overview

**Auth Flow**
1. User clicks "Connect Twitch"
2. OAuth redirect to Twitch
3. Callback handled by Backend
4. JWT issued and returned to App

**Data Flow**
- App → API (Authorization: Bearer)
- API → PostgreSQL via Prisma
- Wallets linked to user identity

---

## 🇷🇺 Русский

### 📌 Описание

**Drops Crypto** — это full-stack приложение для реализации крипто-дропов на базе Twitch.  
Пользователи авторизуются через Twitch, привязывают криптокошельки и получают награды за активность на стримах.

---

### 🧱 Технологический стек

**Backend**
- NestJS
- Prisma ORM
- PostgreSQL
- Docker / Docker Compose
- Twitch OAuth 2.0
- JWT

**Mobile**
- React Native
- Expo
- TypeScript

---

### 🚀 Установка и запуск

#### Backend

```bash
cd drops-crypto-api
npm install
docker compose up -d
cp .env.example .env
npx prisma migrate dev --name init
npm run start:dev
```

API доступно на: `http://localhost:3000`

---

#### ngrok

```bash
ngrok http 3000
```

Обновите `.env`:

```env
PUBLIC_BASE_URL=https://xxxx.ngrok.io
TWITCH_REDIRECT_URI=https://xxxx.ngrok.io/auth/twitch/callback
```

Добавьте Redirect URL в **Twitch Developer Console**.

---

#### Mobile App

```bash
cd drops-crypto-app
npm install
npm start
```

- Обновите `API_BASE` в `App.tsx`
- Используйте **Expo Go** или эмулятор

---

### ✅ Проверка

- `/health` отвечает
- Twitch OAuth успешен
- JWT возвращается в приложение

---

## 🇬🇧 English

### 📌 Overview

**Drops Crypto** is a full-stack application for Twitch-based crypto drops.  
Users authenticate via Twitch, link wallets, and earn rewards for stream engagement.

---

### 🚀 Getting Started

```bash
cd drops-crypto-api
npm install
docker compose up -d
npm run start:dev
```

```bash
cd drops-crypto-app
npm install
npm start
```

---

## 🇩🇪 Deutsch

### 📌 Beschreibung

**Drops Crypto** ist eine Full-Stack-Plattform für Krypto-Drops mit Twitch-Integration.  
Nutzer authentifizieren sich über Twitch und erhalten Belohnungen für Stream-Aktivität.

---

## 🇵🇱 Polski

### 📌 Opis

**Drops Crypto** to aplikacja full-stack do crypto dropsów oparta o Twitch OAuth.  
Użytkownicy zdobywają nagrody za aktywność na streamach.

---

## 🛣 Roadmap

- User profiles
- Wallet verification
- Streamer dashboards
- Smart contract integration
- Production deployment

---

## 🤝 Contributing

Pull requests are welcome.  
For major changes, please open an issue first to discuss what you would like to change.

---

## 🔒 Security

- Secrets stored in `.env`
- OAuth tokens never exposed to client
- JWT expiration enforced

---
## 🔐 Security
Please see [SECURITY.md](./SECURITY.md) for vulnerability reporting.

## 📄 License

MIT License

Copyright (c) 2026 Drops Crypto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
