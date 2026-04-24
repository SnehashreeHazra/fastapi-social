<h1 align="center">🌐 FastAPI Social</h1>
<p align="center">
  A backend social media API built with <strong>FastAPI</strong> — JWT auth, posts, users, and more.
</p>
<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLAlchemy-red?style=flat&logo=python&logoColor=white"/>
  <a href="https://lnkd.in/gCHtngN7"><img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white"/></a>
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white"/>
</p>

---

## ✨ Features

- 🔐 JWT authentication & authorization
- 👤 User registration & login
- 📝 Create, read, update, delete posts
- 🗄️ PostgreSQL with SQLAlchemy ORM & Alembic migrations
- ⚡ Auto-generated Swagger docs at `/docs`
- 🐳 Dockerized — separate backend & frontend Dockerfiles
- 🚀 GitHub Actions CI/CD pipeline

---

## 🛠️ Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Python, Uvicorn |
| Database | PostgreSQL, SQLAlchemy, Alembic |
| Auth | JWT (python-jose), Passlib, bcrypt |
| DevOps | Docker, GitHub Actions |
| Config | Pydantic Settings, python-dotenv |

---

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.12+

### Run with Docker

```bash
git clone https://github.com/SnehashreeHazra/fastapi-social.git
cd fastapi-social
docker build -f Dockerfile.backend -t fastapi-social-backend .
docker build -f Dockerfile.frontend -t fastapi-social-frontend .
```

### Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

- API: `http://localhost:8000`
- Swagger Docs: `http://localhost:8000/docs`

---

## 📁 Project Structure

fastapi-social/  
├── app/ ───────────── Core app (routes, models, schemas, auth)  
├── .github/workflows/ ─ CI/CD pipeline  
├── main.py ────────── App entry point  
├── frontend.py ────── Frontend entry point  
├── Dockerfile.backend  
├── Dockerfile.frontend  
├── requirements.txt  
└── README.md  

---

## 👩‍💻 Author

**Snehashree Hazra** — [LinkedIn](https://www.linkedin.com/in/snehashreehazra1) · [GitHub](https://github.com/SnehashreeHazra)
