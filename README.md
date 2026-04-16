# Prompt Optimization System
### Powered by Gemini 2.5 Flash | FastAPI Backend

---

## What Is This Project?

Most developers write a chatbot system prompt once and never improve it.
This system **scientifically scores, improves, and tests system prompts** — 
turning prompt engineering from guesswork into a measurable process.

---

## Features

| Feature | Endpoint | What It Does |
|---|---|---|
| Evaluate | `POST /api/evaluate` | Score any prompt across 7 quality dimensions |
| Optimize | `POST /api/optimize` | Auto-improve a prompt using Gemini 2.5 Flash |
| Variants | `POST /api/variants` | Generate N styled versions of a prompt |
| Compare (A/B) | `POST /api/compare` | Test 2 prompts with the same user message, pick winner |
| Test | `POST /api/test` | Run a user message through a prompt, score the response |
| Full Pipeline | `POST /api/pipeline` | Evaluate → Optimize → Test all in one shot |
| Suggest | `POST /api/suggest` | Generate a prompt from scratch for any domain/use-case |
| Templates | `GET/POST /api/templates` | Save and reuse your best prompts |
| History | `GET /api/history` | All past optimizations with scores |
| Stats | `GET /api/stats` | Dashboard metrics |
| Domains | `GET /api/domains` | Supported domain list |

---

## How the Evaluation Works (7 Dimensions)

Every prompt is scored 0–10 on each dimension. Overall score = weighted average → Grade A+ to F.

| Dimension | What It Checks |
|---|---|
| **Clarity** | Are the instructions unambiguous and easy to follow? |
| **Specificity** | Is the AI told exactly what to do (not vague)? |
| **Role Definition** | Does the prompt define WHO the AI is? |
| **Context Richness** | Does it provide enough background information? |
| **Output Format** | Does it specify HOW the AI should respond? |
| **Constraints** | Does it set limits (what NOT to do, tone, length)? |
| **Tone Consistency** | Is the desired tone clear and consistent? |

---

## Setup & Run

### 1. Clone / Navigate to the project folder

```bash
cd prompt_optimizer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add your Gemini API Key

```bash
cp .env.example .env
# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here
```

Get your key at: https://aistudio.google.com/app/apikey

### 4. Run the server

```bash
uvicorn main:app --reload --port 8000
```

### 5. Open Swagger UI (auto-generated docs)

```
http://localhost:8000/docs
```

---

## API Usage Examples

### Evaluate a Prompt
```json
POST /api/evaluate
{
  "prompt": "You are a helpful assistant.",
  "domain": "customer_support"
}
```

### Optimize a Prompt
```json
POST /api/optimize
{
  "prompt": "You are a helpful assistant.",
  "domain": "customer_support",
  "optimization_goal": "improve clarity and add role definition"
}
```

### A/B Compare Two Prompts
```json
POST /api/compare
{
  "prompt_a": "You are a helpful assistant.",
  "prompt_b": "You are Alex, a friendly customer support agent for TechCorp. Always greet users by name, solve issues step-by-step, and escalate if unsure.",
  "test_input": "My order hasn't arrived in 10 days.",
  "domain": "customer_support"
}
```

### Full Pipeline
```json
POST /api/pipeline
{
  "prompt": "You are a helpful assistant.",
  "test_inputs": ["What is your return policy?", "I want a refund"],
  "domain": "ecommerce",
  "optimization_goal": "make it sound more professional and helpful"
}
```

### Generate Variants
```json
POST /api/variants
{
  "prompt": "You are a helpful assistant.",
  "domain": "education",
  "count": 3,
  "style": "friendly"
}
```

### Suggest a Prompt from Scratch
```
POST /api/suggest?domain=healthcare&use_case=appointment booking chatbot
```

---

## Frontend Connection (Antigravity / Any Framework)

This backend exposes a clean REST API with CORS enabled for all origins.

**Base URL:** `http://localhost:8000`  
**All responses follow:** `{ "success": true, "data": {...} }`

### Key endpoints for your UI:

| UI Screen | API Call |
|---|---|
| Prompt input + score | `POST /api/evaluate` |
| Improve button | `POST /api/optimize` |
| Before/After comparison | `POST /api/pipeline` |
| A/B test | `POST /api/compare` |
| Saved prompts library | `GET /api/templates` |
| Dashboard / stats | `GET /api/stats` |

---

## Tech Stack

- **Backend:** FastAPI (Python)
- **AI Model:** Gemini 2.5 Flash (gemini-2.5-flash)
- **Database:** SQLite via SQLAlchemy (no setup needed, auto-created)
- **API Docs:** Swagger UI at `/docs`, ReDoc at `/redoc`

---

## Project Structure

```
prompt_optimizer/
├── main.py          — FastAPI app + all 11 routes
├── services.py      — All Gemini AI logic (evaluate, optimize, compare, etc.)
├── database.py      — SQLite tables (OptimizationRecord, Template, TestResult, CompareRecord)
├── models.py        — Pydantic request/response schemas
├── requirements.txt
├── .env.example     — Add your GEMINI_API_KEY here
└── README.md
```
