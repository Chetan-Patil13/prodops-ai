Frontend

| Layer     | Choice         | Why                              |
| --------- | -------------- | -------------------------------- |
| Framework | React + Vite   | Fast, modern, recruiter-friendly |
| Styling   | Tailwind / CSS | Simple, clean UI                 |
| Hosting   | Vercel         | Free, CI/CD built-in             |

Backend

| Layer   | Choice                       | Why                  |
| ------- | ---------------------------- | -------------------- |
| API     | FastAPI                      | Async, clean, Python |
| Agent   | LangChain                    | Industry standard    |
| LLM     | GPT-4.1-mini / GPT-4o-mini   | Cheap + reliable     |
| ORM     | SQLAlchemy                   | Safe DB access       |
| Auth    | Lightweight JWT / fake login | Pilot scope          |
| Hosting | Render / Railway             | Low-cost             |

Data
| Component | Choice | Why |
| --------- | ------------------ | ----------------------------- |
| DB | PostgreSQL (cloud) | Free tier, portable |
| Vector DB | FAISS | Free, local |
| Data | Synthetic | No dependency on real systems |

Observability & Ops
| Area | Tool | Why |
| ------- | -------------- | ---------------- |
| Logging | Python logging | Simple |
| Tracing | LangSmith | Agent visibility |
| CI/CD | GitHub Actions | Standard |
| Secrets | Env vars | Simple & safe |
