# 🎮 Drops Crypto

**Full-stack application for crypto drops with Twitch OAuth and wallet integration.**  
Built for streamers, viewers, and crypto-native reward mechanics.

---

## 🌍 Languages / Языки / Sprachen / Języki

- [🇷🇺 Русский](#-русский)
- [🇬🇧 English](#-english)
- [🇩🇪 Deutsch](#-deutsch)
- [🇵🇱 Polski](#-polski)

---

## 🧭 Project Navigation

- [`drops-crypto-api/`](./drops-crypto-api) — Backend (NestJS, Prisma, PostgreSQL)
- [`drops-crypto-app/`](./drops-crypto-app) — Mobile App (React Native, Expo)

---

## 🇷🇺 Русский

### 📌 Описание

**Drops Crypto** — это full-stack платформа для крипто-дропов, интегрированная с Twitch OAuth и пользовательскими кошельками.  
Пользователи могут авторизоваться через Twitch, участвовать в стримах и получать награды.

---

### 🧱 Стек технологий

**Backend**
- NestJS
- Prisma ORM
- PostgreSQL
- Docker
- Twitch OAuth 2.0

**Mobile**
- React Native
- Expo
- TypeScript

---

### 🚀 Быстрый старт

#### Backend

```bash
cd drops-crypto-api
npm install
docker compose up -d
cp .env.example .env
npx prisma migrate dev --name init
npm run start:dev
```

---

#### ngrok

```bash
ngrok http 3000
```

---

#### Mobile App

```bash
cd drops-crypto-app
npm install
npm start
```

---

## 🇬🇧 English

### 📌 Overview

**Drops Crypto** is a full-stack platform for crypto drops integrated with Twitch OAuth and user wallets.

---

## 🇩🇪 Deutsch

### 📌 Beschreibung

**Drops Crypto** ist eine Full-Stack-Anwendung für Krypto-Drops mit Twitch-OAuth-Integration.

---

## 🇵🇱 Polski

### 📌 Opis

**Drops Crypto** to aplikacja full-stack do crypto dropsów z integracją Twitch OAuth.

---

## 📄 License

MIT
