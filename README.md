# WellMind AI

A mental-wellness chatbot with RAG, safety guardrails, and persistent memory. Built on FastAPI + PostgreSQL + Qdrant + OpenAI + LangGraph.

## Architecture

```
POST /chat  →  JWT auth  →  LangGraph workflow:

  ensure_conversation → load_memory → classify_safety
                                           │
                            ┌──────────────┴──────────────┐
                            │ risky                       │ normal
                            ▼                             ▼
                     canned safety reply         retrieve → generate
                            │                   → validate → save
                            │                   → update_memory
                            └─────────────── END ──────────┘
```

Three sources of context merge in the prompt:
- **Knowledge base** (Qdrant, dense cosine, threshold 0.35) — the only factual source
- **Chat history** (last 6 messages) — resolves pronouns
- **User memory** (saved preferences) — personalization only, never medical facts

## Stack

| Layer | Tech |
|---|---|
| API | FastAPI + uvicorn |
| Auth | JWT (HS256) + 6-digit OTP, bcrypt passwords |
| DB | PostgreSQL (`users`, `conversations`, `messages`, `user_memories`, `feedbacks`, `otp_verifications`) |
| Vector store | Qdrant (local), `text-embedding-3-small` (1536-dim, cosine) |
| LLM | OpenAI `gpt-4o-mini`, temperature 0 |
| Workflow | LangGraph |
| Chunking | LangChain `RecursiveCharacterTextSplitter` (300 chars / 50 overlap) |

## Setup

```bash
# 1. Create venv & install
python3 -m venv venv
./venv/bin/pip install -r app/requirements.txt

# 2. Configure app/.env
#    DATABASE_URL=postgresql://user:pass@host:5432/dbname
#    OPENAI_API_KEY=sk-...
#    JWT_SECRET_KEY=<random>

# 3. Create tables
PYTHONPATH=. ./venv/bin/python -m app.models.create_tables

# 4. Seed knowledge base (optional)
PYTHONPATH=. ./venv/bin/python seed_knowledge.py

# 5. Run
./venv/bin/uvicorn app.main:app --reload
```

Swagger UI: http://127.0.0.1:8000/docs

## API

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/auth/signup` | - | Create user |
| POST | `/auth/send-otp` | - | Send verification OTP |
| POST | `/auth/verify-otp` | - | Verify + activate |
| POST | `/auth/login` | - | Returns JWT |
| POST | `/chat` | user | Ask a question |
| POST | `/chat/feedback` | user | Rate an answer |
| POST | `/documents/upload` | admin | Upload PDF/TXT, auto-ingest |
| GET | `/documents/sources` | admin | List indexed sources |
| GET | `/documents/sample` | admin | Peek chunks from one source |
| DELETE | `/documents/by-source` | admin | Remove all chunks for a filename |

## Project Layout

```
app/
  main.py              FastAPI app
  api/                 Route handlers (auth, chat, documents)
  agents/              LangGraph: state, nodes, graph
  services/            Business logic (chat, auth, memory, safety, document)
  repositories/        DB access
  rag/                 loader, chunker, retriever, generator
  models/              SQLAlchemy ORM
  schemas/             Pydantic request/response
  db/                  Engine + session factory
  utils/               JWT, password helpers
data/                  Source docs to ingest
uploads/               Admin-uploaded files
tests/                 evaluate.py + eval_dataset.json
seed_knowledge.py      Idempotent bootstrap ingestion
```

## Safety Model

Three defense layers:

1. **Input classifier** (`safety_service.classify_safety`) — rule-based, categories: `SELF_HARM`, `MEDICATION`, `DIAGNOSIS`, `EMERGENCY`, `NORMAL`. Risky inputs short-circuit before RAG.
2. **Retrieval threshold** — if no chunk scores ≥0.35, returns fallback instead of guessing.
3. **Output validator** — scans generated answer for forbidden phrases ("you have depression", "take this medicine"), swaps with disclaimer.

Risky messages are not written to long-term memory.

## Production deploy on EC2 with free domain + HTTPS

```bash
# ON AWS CONSOLE
# 1. Allocate an Elastic IP, associate with the EC2 instance.
#    (So the IP never changes between reboots.)
# 2. Security Group inbound rules: allow TCP 80 and TCP 443 from 0.0.0.0/0.

# ON DUCKDNS (free)
# 3. https://www.duckdns.org -> log in with GitHub/Google
#    Create a subdomain, e.g. "wellmind-demo"
#    Point it at your Elastic IP -> yourname.duckdns.org

# ON THE EC2 INSTANCE
cd ~/mental-health-chatbot
git pull origin development
echo "DOMAIN=wellmind-demo.duckdns.org" >> .env.docker   # <-- your actual subdomain
docker compose --profile production up -d --build

# Caddy auto-requests a Let's Encrypt cert on first HTTPS request.
# Give it ~30 seconds, then open:
# https://wellmind-demo.duckdns.org
```

Then share the HTTPS URL. Clean, secure, no port number, no browser warnings.

**To stop:** `docker compose --profile production down`
**For local dev** (no Caddy, no HTTPS): just `docker compose up -d` as before.

## Run with Docker

```bash
# 1. Create .env.docker from the example
cp .env.docker.example .env.docker
# edit .env.docker and set OPENAI_API_KEY + JWT_SECRET_KEY

# 2. Build + start all services (app, postgres, redis)
docker compose up -d --build

# 3. Create tables on first run
docker compose exec app python -m app.models.create_tables

# 4. Seed knowledge base from data/ (optional)
docker compose exec app python seed_knowledge.py

# 5. Open http://127.0.0.1:8000/docs
```

Stop everything: `docker compose down`. Reset data (deletes volumes): `docker compose down -v`.

**Ports (host → container):** app `8000→8000`, postgres `5433→5432`, redis `6380→6379`. Host ports are offset so they don't clash with locally installed Postgres/Redis.

**Volumes (named, persist across restarts):** `postgres_data`, `redis_data`, `qdrant_data` (embedded Qdrant storage), `uploads_data` (admin-uploaded files). `./data` is bind-mounted read-only for the seed script.

**Migrating existing host DB data into the container** (optional):
```bash
pg_dump -h localhost -U postgres ai_hr > /tmp/host-dump.sql
docker compose exec -T postgres psql -U postgres -d wellmind < /tmp/host-dump.sql
```

**Known limit of this setup:** Qdrant runs embedded inside the app container (one worker). Moving Qdrant to its own container is tracked in [KAM-13](https://linear.app/kenvue325/issue/KAM-13).

## Evaluation

```bash
PYTHONPATH=. ./venv/bin/python tests/evaluate.py
```

Runs seed questions through `process_chat`, scores pass/fail per category with latency. Dataset in `tests/eval_dataset.json` — extend it.

## Known Limits

- Qdrant runs embedded (single-process). Production: run as a server.
- Safety and memory extraction are keyword-based. Upgrade with LLM classifier.
- Ingestion is synchronous. Large files should go through a job queue.
- `create_all` is used instead of migrations. Add Alembic before schema changes get painful.
- OTP prints to server log. Replace with email delivery for production.
- No rate limiting, no HTTPS enforcement.
