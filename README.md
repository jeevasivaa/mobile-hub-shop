# 📱 MobileHub — Mobile Phone Shop Website

A complete, production-ready mobile phone shop website built with **FastAPI**, **HTMX**, **Tailwind CSS**, and **PostgreSQL (Supabase)**.

---

## ✨ Features

### Public Website
- 🏠 Home page with hero section, featured products, offers banner
- 📱 Products page with **live search** and **brand filter** (HTMX — no page reload)
- 🔍 Product detail page with specs and WhatsApp enquiry
- 🏷️ Offers page with discount cards
- ℹ️ About page with Google Maps embed
- 📩 Contact page with HTMX form submission
- 💬 Floating WhatsApp button
- 📐 Fully mobile-responsive (Tailwind CSS)

### Admin Panel
- 🔐 Session-based login (bcrypt + signed cookies)
- 📊 Dashboard with stats
- ➕ Add / Edit / Delete Products (with image upload)
- 🏷️ Add / Edit / Delete Offers
- 📩 View & Delete Customer Enquiries
- 🔁 HTMX inline deletes (no page reload)

---

## 🗂️ Project Structure

```
mobile-shop/
├── app/
│   ├── main.py              ← FastAPI entry point
│   ├── core/
│   │   ├── config.py        ← Settings (pydantic-settings)
│   │   ├── database.py      ← SQLAlchemy engine + session
│   │   └── security.py      ← Password hashing + session tokens
│   ├── models/              ← SQLAlchemy ORM models
│   ├── schemas/             ← Pydantic validation schemas
│   ├── routers/             ← FastAPI route handlers
│   ├── services/            ← Business logic layer
│   ├── dependencies/        ← Reusable FastAPI dependencies
│   ├── utils/               ← File upload helpers
│   ├── templates/           ← Jinja2 HTML templates
│   └── static/              ← CSS, JS, uploaded images
├── alembic/                 ← Database migrations
├── tests/                   ← Pytest smoke tests
├── nginx/default.conf       ← Nginx reverse proxy config
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Setup

```bash
git clone <your-repo>
cd mobile-shop

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
```

Edit `.env` with your actual values:

```env
DATABASE_URL=postgresql://postgres:password@db.yourproject.supabase.co:5432/postgres
SECRET_KEY=your-random-secret-key
APP_NAME=MobileHub
WHATSAPP_NUMBER=+910000000000
```

### 3. Setup Database

#### Option A — Supabase (Recommended)
1. Go to [supabase.com](https://supabase.com) → New Project
2. Copy the **Connection String** (URI format) from Settings → Database
3. Paste it as `DATABASE_URL` in your `.env`

#### Option B — Local PostgreSQL
```bash
# Using Docker
docker run -d --name mobileshop_db -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
```

Set `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres`

### 4. Run Migrations

```bash
# Generate initial migration
alembic revision --autogenerate -m "initial tables"

# Apply migrations
alembic upgrade head
```

### 5. Create First Admin User

```bash
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()
admin = User(username='admin', password_hash=hash_password('changeme123'))
db.add(admin)
db.commit()
print('Admin created: admin / changeme123')
"
```

### 6. Run the App

```bash
uvicorn app.main:app --reload
```

Open: [http://localhost:8000](http://localhost:8000)  
Admin: [http://localhost:8000/admin/login](http://localhost:8000/admin/login)

---

## 🐳 Docker Deployment

### Build & Run with Docker Compose

```bash
# Copy env file
copy .env.example .env
# Edit .env with your Supabase DATABASE_URL

# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

Access at: [http://localhost](http://localhost) (via Nginx on port 80)

---

## ☁️ Deploy on Render

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set these settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `DATABASE_URL` ← Supabase connection string
   - `SECRET_KEY` ← Random secure string
   - `APP_NAME`, `WHATSAPP_NUMBER`, etc.
6. Click Deploy!

> **Note**: Render's free tier does not persist uploaded files. Use Supabase Storage for production image uploads.

---

## ☁️ Deploy on Railway

1. Push to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add environment variables (same as Render above)
4. Railway auto-detects the Dockerfile and deploys

---

## 🗄️ Supabase PostgreSQL Setup

1. Create account at [supabase.com](https://supabase.com)
2. Create new project (choose region closest to your users)
3. Go to **Settings → Database**
4. Copy the **URI** connection string
5. Replace `[YOUR-PASSWORD]` with your project password
6. Paste as `DATABASE_URL` in `.env`

Example format:
```
postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

Run migrations:
```bash
alembic upgrade head
```

---

## 🔑 Admin Setup

After first deployment, create your admin user:

```bash
# If running locally
python create_admin.py

# If running in Docker
docker-compose exec app python create_admin.py
```

Or directly via Python:
```python
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()
db.add(User(username="admin", password_hash=hash_password("your-secure-password")))
db.commit()
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `SECRET_KEY` | ✅ | Random secret for session signing |
| `APP_NAME` | ❌ | Shop name (default: MobileHub) |
| `WHATSAPP_NUMBER` | ❌ | WhatsApp number with country code |
| `SHOP_ADDRESS` | ❌ | Physical shop address |
| `GOOGLE_MAPS_EMBED_URL` | ❌ | Google Maps iframe embed URL |
| `DEBUG` | ❌ | Enable API docs (default: False) |
| `UPLOAD_DIR` | ❌ | Image upload directory |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | FastAPI |
| **Templates** | Jinja2 |
| **Frontend** | Tailwind CSS (CDN) + HTMX |
| **Database** | PostgreSQL (Supabase) |
| **ORM** | SQLAlchemy |
| **Validation** | Pydantic v2 |
| **Auth** | passlib[bcrypt] + itsdangerous |
| **Migrations** | Alembic |
| **Server** | Uvicorn |
| **Proxy** | Nginx |
| **Container** | Docker |

---

## 📝 License

MIT License — Free to use for personal and commercial projects.
