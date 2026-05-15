# Enterprise Project Intelligence Chat System - Backend

FastAPI backend with PostgreSQL, JWT authentication, and RAG (Retrieval-Augmented Generation) capabilities.

## 🏗️ Architecture

- **Framework**: FastAPI
- **Database**: PostgreSQL with AsyncPG
- **Authentication**: JWT with bcrypt password hashing
- **Vector Store**: ChromaDB for document embeddings
- **AI Providers**: OpenAI or Google Gemini

---

## 📋 Prerequisites

- Python 3.10+
- PostgreSQL 14+
- OpenAI API Key or Google Gemini API Key

---

## 🚀 Quick Start

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Setup PostgreSQL Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE knowledge_assistant;

-- Create user (optional)
CREATE USER kiro_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE knowledge_assistant TO kiro_user;
```

### 4. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:your_password@localhost:5432/knowledge_assistant

# JWT
SECRET_KEY=your-super-secret-key-change-in-production-use-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI Provider - choose "openai" or "gemini"
AI_PROVIDER=openai

# OpenAI
OPENAI_API_KEY=sk-your-openai-api-key

# Gemini (if using Google)
GOOGLE_API_KEY=your-google-api-key

# ChromaDB
CHROMA_PERSIST_DIR=./chroma_db

# File uploads
UPLOAD_DIR=./uploads
MAX_FILE_SIZE_MB=50
```

**Generate a secure SECRET_KEY:**
```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Or using OpenSSL
openssl rand -hex 32
```

### 5. Initialize Database

The database tables will be created automatically on first run. To manually create them:

```bash
python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"
```

### 6. Create Default Users

Run the script to create default admin and test users:

```bash
python create_default_users.py
```

This creates:
- **Admin**: `admin@company.com` / `admin123`
- **Test User**: `user@company.com` / `user123`

⚠️ **IMPORTANT**: Change these passwords in production!

### 7. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

Server will be available at: `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

---

## 🔐 Authentication System

### User Roles

1. **Admin** (`role: "admin"`)
   - Can create and delete projects
   - Can upload documents
   - Can access all projects
   - Can chat with AI

2. **User** (`role: "user"`)
   - Can view projects
   - Can view documents
   - Can chat with AI
   - Cannot create/delete projects
   - Cannot upload documents

### API Endpoints

#### Admin Login
```http
POST /auth/admin/login
Content-Type: application/json

{
  "email": "admin@company.com",
  "password": "admin123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "System Administrator",
    "email": "admin@company.com",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### User Login
```http
POST /auth/user/login
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "user123"
}

Response:
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "name": "Test User",
    "email": "user@company.com",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>

Response:
{
  "id": 1,
  "name": "System Administrator",
  "email": "admin@company.com",
  "role": "admin",
  "created_at": "2024-01-01T00:00:00Z"
}
```

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py       # User model with roles
│   │   ├── project.py    # Project model
│   │   ├── document.py   # Document model
│   │   └── chat.py       # Chat history model
│   ├── routers/          # API endpoints
│   │   ├── auth.py       # Authentication (admin/user login)
│   │   ├── projects.py   # Project management (admin-only create/delete)
│   │   ├── documents.py  # Document upload (admin-only)
│   │   └── chat.py       # Chat with AI
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py       # User schemas
│   │   ├── project.py    # Project schemas
│   │   ├── document.py   # Document schemas
│   │   └── chat.py       # Chat schemas
│   ├── services/         # Business logic
│   │   └── document_service.py  # Document processing
│   ├── rag/              # RAG pipeline
│   │   ├── document_processor.py  # PDF/DOCX processing
│   │   ├── embeddings.py          # Text embeddings
│   │   ├── vector_store.py        # ChromaDB operations
│   │   └── rag_pipeline.py        # Query & retrieval
│   ├── utils/            # Utilities
│   │   └── auth.py       # JWT & password hashing
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   └── main.py           # FastAPI app
├── create_default_users.py  # Script to create admin/users
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

---

## 🔒 Permission Matrix

| Endpoint | Admin | User | Method |
|----------|-------|------|--------|
| `POST /auth/admin/login` | ✅ | ❌ | Public |
| `POST /auth/user/login` | ❌ | ✅ | Public |
| `GET /auth/me` | ✅ | ✅ | Protected |
| `GET /projects` | ✅ (all) | ✅ (own) | Protected |
| `POST /projects` | ✅ | ❌ | Admin Only |
| `GET /projects/{id}` | ✅ (all) | ✅ (own) | Protected |
| `DELETE /projects/{id}` | ✅ | ❌ | Admin Only |
| `POST /projects/{id}/upload` | ✅ | ❌ | Admin Only |
| `GET /projects/{id}/documents` | ✅ | ✅ | Protected |
| `POST /chat/{project_id}` | ✅ | ✅ | Protected |
| `GET /chat/history/{project_id}` | ✅ | ✅ | Protected |

---

## 🧪 Testing

### Manual Testing with cURL

**Admin Login:**
```bash
curl -X POST http://localhost:8000/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@company.com","password":"admin123"}'
```

**Create Project (Admin Only):**
```bash
curl -X POST http://localhost:8000/projects \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"name":"Test Project","description":"A test project"}'
```

**Upload Document (Admin Only):**
```bash
curl -X POST http://localhost:8000/projects/1/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"
```

**User Login:**
```bash
curl -X POST http://localhost:8000/auth/user/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@company.com","password":"user123"}'
```

**List Projects:**
```bash
curl -X GET http://localhost:8000/projects \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🔧 Database Management

### Create New User Manually

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from app.models.user import User, UserRole
from app.utils.auth import hash_password

async def create_user():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        user = User(
            name="New User",
            email="newuser@company.com",
            password_hash=hash_password("password123"),
            role=UserRole.user  # or UserRole.admin
        )
        session.add(user)
        await session.commit()
        print(f"✅ Created user: {user.email}")
    
    await engine.dispose()

asyncio.run(create_user())
```

### Reset Admin Password

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from app.config import settings
from app.models.user import User
from app.utils.auth import hash_password

async def reset_admin_password():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == "admin@company.com")
        )
        admin = result.scalar_one_or_none()
        
        if admin:
            admin.password_hash = hash_password("new_password")
            await session.commit()
            print("✅ Admin password reset successfully")
        else:
            print("❌ Admin user not found")
    
    await engine.dispose()

asyncio.run(reset_admin_password())
```

---

## 🐛 Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -U postgres -h localhost -d knowledge_assistant

# Check if database exists
psql -U postgres -c "\l"

# Check if tables exist
psql -U postgres -d knowledge_assistant -c "\dt"
```

### JWT Token Issues

```python
# Decode JWT token to check payload
from jose import jwt
from app.config import settings

token = "your_token_here"
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
print(payload)
# Should show: {'sub': '1', 'role': 'admin', 'exp': ...}
```

### Permission Denied Errors

- Ensure user has correct role in database
- Check JWT token includes role in payload
- Verify Authorization header format: `Bearer <token>`

---

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "service": "AI Knowledge Assistant"
}
```

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🚀 Production Deployment

### Environment Variables

```env
# Use strong secrets
SECRET_KEY=<generate-with-openssl-rand-hex-32>

# Use production database
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db:5432/knowledge_assistant

# Longer token expiry for production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Production AI keys
OPENAI_API_KEY=sk-prod-key
```

### Run with Gunicorn

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 📝 Notes

- **Security**: Always use HTTPS in production
- **Passwords**: Change default passwords immediately
- **Secrets**: Never commit `.env` file to version control
- **Backups**: Regularly backup PostgreSQL database
- **Monitoring**: Set up logging and monitoring in production

---

## 🆘 Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the troubleshooting section
3. Check application logs
4. Verify environment variables

---

## ✅ Checklist

- [ ] PostgreSQL installed and running
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] `.env` file configured
- [ ] Database created
- [ ] Default users created
- [ ] Server running successfully
- [ ] Can login as admin
- [ ] Can login as user
- [ ] Admin can create projects
- [ ] User cannot create projects
- [ ] Frontend connected to backend
