# 3novatorTech — AI Receptionist

> A full stack, production ready AI receptionist web application powered by **Groq** and **LLaMA 3.3**. Authenticate, chat with an intelligent AI receptionist, and manage appointments — all through a polished, responsive browser interface.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Booking via Chat](#booking-via-chat)
- [Frontend Pages](#frontend-pages)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [License](#license)
- [Author](#author)

---

## Overview

The **3novatorTech AI Receptionist** is a full stack web application that replaces a traditional front desk receptionist with a conversational AI. Users register and log in securely, then interact with an AI assistant that can answer general questions and guide them through booking an appointment all in natural language.

The backend is built with **Python + Flask**, the AI is powered by the **Groq cloud API**, and all data is persisted in a lightweight **SQLite** database. The frontend is pure HTML, CSS, and JavaScript, served directly by Flask with no separate build step.

---

## Features

- **JWT Authentication** : secure register and login flow; all protected routes require a Bearer token
- **AI Chatbot** : conversational receptionist powered by Groq's LLaMA 3.3 70B model
- **Voice Input & Output** : speak to the receptionist via the browser microphone; replies are read aloud using the Web Speech API
- **Intelligent Booking Flow** : guided multi-step conversation that collects name and date, confirms with the user, then saves the appointment automatically
- **Booking Form** : manual appointment creation with name, email, date, time, and reason fields
- **Appointment Dashboard** : view your personal appointment history, refreshable on demand
- **Modular Backend** : Flask Blueprints, a dedicated service layer, and clean separation of concerns
- **No Local Model Required** : runs entirely through the Groq cloud API; works on any machine
- **Responsive UI** : dark theme interface that adapts to desktop and mobile screens
- **Zero config Database** : SQLite database is created automatically on first run; no setup needed

---

## Tech Stack

| Layer        | Technology                                      |
|--------------|-------------------------------------------------|
| Backend      | Python 3.10+ · Flask 3 · Flask-CORS             |
| Authentication | PyJWT · Werkzeug password hashing             |
| AI           | Groq API · LLaMA 3.3 70B Versatile             |
| Database     | SQLite (via Python `sqlite3`, no server needed) |
| Frontend     | HTML5 · CSS3 · Vanilla JavaScript               |
| Voice        | Web Speech API (SpeechRecognition + SpeechSynthesis) |
| Config       | python-dotenv                                   |

---

## Project Structure

```
ai receptionist/
├── run.py                        # Entry point : run this to start the app
├── .env                          # API keys and secrets (never commit this)
├── .gitignore
├── requirements.txt
├── README.md
│
├── backend/
│   ├── app.py                    # App factory : creates Flask app, registers blueprints
│   ├── config.py                 # Centralised config (DB path, Groq key/model, secret key)
│   │
│   ├── routes/
│   │   ├── auth.py               # POST /api/auth/register  POST /api/auth/login
│   │   ├── chat.py               # POST /api/chat/
│   │   └── booking.py            # POST /api/booking/  GET /api/booking/
│   │
│   ├── services/
│   │   ├── llm_service.py        # Groq API integration — sends messages, returns replies
│   │   ├── booking_service.py    # Appointment persistence helpers
│   │   └── session_store.py      # In-memory booking conversation state machine
│   │
│   ├── models/
│   │   ├── appointment.py        # Appointment dataclass
│   │   └── user.py               # User dataclass
│   │
│   ├── database/
│   │   └── db.py                 # SQLite connection, init_db(), safe migrations
│   │
│   └── utils/
│       └── helpers.py            # json_success() / json_error() response helpers
│
└── frontend/
    ├── index.html                # Main dashboard — chat panel + booking panel
    ├── login.html                # Sign-in page
    ├── register.html             # Registration page
    ├── chat.html                 # Standalone chat-only page (no auth required)
    ├── auth.js                   # Auth helpers — token storage, login, register, logout
    ├── script.js                 # Chat, voice, booking, and appointments logic
    ├── style.css                 # Responsive dark-theme design system
    └── logo.png                  # Brand logo
```

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- A free [Groq API key](https://console.groq.com)

### Step 1 — Clone the repository

```bash
git clone https://github.com/your-username/ai-receptionist.git
cd "ai receptionist"
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Configure environment variables

Create a `.env` file in the project root (see [Environment Variables](#environment-variables)):

```
GROQ_API_KEY=gsk_your_key_here
SECRET_KEY=your-random-secret-key-here
```

> **Never commit `.env`** — it is already listed in `.gitignore`.

### Step 4 — Start the server

Run this from the **project root** (not inside `backend/`):

```bash
python run.py
```

The server starts at `http://localhost:5000`.

### Step 5 — Open the app

Navigate to [http://localhost:5000](http://localhost:5000) in your browser.  
You will be redirected to the login page. Register a new account to get started.

Flask serves all frontend files directly — no separate dev server or build step is needed.

---

## Environment Variables

Create a `.env` file in the project root with the following keys:

| Variable       | Required | Description                                                               |
|----------------|--------|-----------------------------------------------------------------------------|
| `GROQ_API_KEY` |  Yes   | Your Groq API key. Get one free at [console.groq.com](https://console.groq.com) |
| `SECRET_KEY`   |  Yes   | A long random string used to sign JWT tokens. Use any secure random value. |
| `GROQ_MODEL`   |  No    | Override the default Groq model. Default: `llama-3.3-70b-versatile`        |

Example `.env`:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
SECRET_KEY=change-this-to-a-long-random-string-in-production
GROQ_MODEL=llama-3.3-70b-versatile
```

To use a different Groq model:

```
GROQ_MODEL=llama3-70b-8192
```

---

## API Reference

All endpoints except `/api/auth/register` and `/api/auth/login` require an `Authorization` header:

```
Authorization: Bearer <token>
```

The token is returned by the register and login endpoints and must be included in every subsequent request.

---

### `POST /api/auth/register`

Register a new user account.

```json
// Request body
{
  "name": "Alice",
  "email": "alice@example.com",
  "password": "secret"
}

// Response 201 — Created
{
  "success": true,
  "data": {
    "token": "<jwt>",
    "name": "Alice"
  }
}
```

| Status | Meaning |
|--------|---------|
| `201`  | Account created successfully |
| `400`  | Missing required fields |
| `409`  | Email already registered |

---

### `POST /api/auth/login`

Authenticate an existing user.

```json
// Request body
{
  "email": "alice@example.com",
  "password": "secret"
}

// Response 200 — OK
{
  "success": true,
  "data": {
    "token": "<jwt>",
    "name": "Alice"
  }
}
```

| Status | Meaning |
|--------|---------|
| `200`  | Login successful |
| `400`  | Missing fields |
| `401`  | Incorrect password |
| `404`  | No account found for that email |

---

### `POST /api/chat/`

Send a message to the AI receptionist. Requires authentication.

```json
// Request body
{
  "message": "I'd like to book an appointment"
}

// Response 200 — OK
{
  "success": true,
  "data": {
    "reply": "Of course. Could I get your name please?"
  }
}
```

| Status | Meaning |
|--------|---------|
| `200`  | Reply returned successfully |
| `400`  | Missing `message` field |
| `401`  | Missing or invalid token |

---

### `POST /api/booking/`

Create a new appointment manually. Requires authentication.

```json
// Request body
{
  "name": "Alice",
  "date": "2025-09-01",
  "time": "10:00",
  "email": "alice@example.com",
  "reason": "General consultation"
}

// Response 201 — Created
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 3,
    "name": "Alice",
    "email": "alice@example.com",
    "date": "2025-09-01",
    "time": "10:00",
    "reason": "General consultation"
  }
}
```

| Status | Meaning |
|--------|---------|
| `201`  | Appointment created |
| `400`  | Missing `name`, `date`, or `time` |
| `401`  | Missing or invalid token |

---

### `GET /api/booking/`

Retrieve the authenticated user's appointments (most recent 20).

```json
// Response 200 — OK
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "Alice",
      "email": "alice@example.com",
      "date": "2025-09-01",
      "time": "10:00",
      "reason": "General consultation"
    }
  ]
}
```

---

### Error Response Format

All errors follow a consistent envelope:

```json
{
  "success": false,
  "error": "Human-readable error message"
}
```

---

## Booking via Chat

The AI receptionist handles appointment booking through a guided, multi-step conversation. Simply mention booking in any natural way to trigger the flow.

**Trigger phrases** (examples):
- `"book an appointment"`
- `"I'd like to book"`
- `"schedule appointment"`
- `"make appointment"`
- `"book a slot"`

**Example conversation:**

```
You  →  "I'd like to book an appointment"
Bot  →  "Of course. Could I get your name please?"

You  →  "Haris"
Bot  →  "Thank you, Haris. What date would you prefer? (e.g. 2025-08-20)"

You  →  "2025-09-01"
Bot  →  "Please confirm your appointment details — Name: Haris, Date: 2025-09-01.
         Reply 'yes' to confirm or 'no' to cancel."

You  →  "yes"
Bot  →  "Your appointment has been confirmed for 2025-09-01. We look forward to seeing you."
```

To cancel at any point, reply with: `no`, `cancel`, `stop`, or `exit`.

Any message outside the booking flow is answered directly by the Groq-powered AI.

---

## Frontend Pages

| Page              | URL                  | Description                                      |
|-------------------|----------------------|--------------------------------------------------|
| Login             | `/login.html`        | Sign in to your account                          |
| Register          | `/register.html`     | Create a new account                             |
| Dashboard         | `/index.html`        | Main app — chat panel + booking panel side by side |
| Standalone Chat   | `/chat.html`         | Minimal chat-only interface (no auth required)   |

---

## Deployment

The recommended deployment platform is **Render** — it supports Python, has a free tier, and requires no configuration files beyond what is already in this repo.

| Component | Platform |
|-----------|----------|
| Backend + Frontend | [Render](https://render.com) — free tier, Python support |

### Steps to deploy on Render

1. Push this repository to GitHub
2. Create a new **Web Service** on Render and connect your repo
3. Set the **Start Command** to: `python run.py`
4. Add the following **Environment Variables** in the Render dashboard:
   - `GROQ_API_KEY` — your Groq API key
   - `SECRET_KEY` — a long random secret string
5. Deploy — Render will install dependencies from `requirements.txt` automatically

> Never hardcode secrets. Always use environment variables in production.

---

## Roadmap

- [x] JWT-based user authentication (register / login / logout)
- [x] AI chat powered by Groq LLaMA 3.3
- [x] Voice input and voice output
- [x] Guided multi-step booking flow via chat
- [x] Manual booking form with full field set
- [x] Per-user appointment history
- [x] Responsive dark-theme UI
- [ ] Persist full chat history to the database
- [ ] Conflict detection for double-booked time slots
- [ ] Email confirmation on appointment booking
- [ ] Admin panel to view and manage all appointments
- [ ] Docker setup for one-command local startup
- [ ] Rate limiting on API endpoints

---

## License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## Author

**Haris Hussain**  
Developer 3novatorTech  

Built with Python, Flask, and the Groq API.
