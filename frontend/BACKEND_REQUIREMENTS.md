# Backend Requirements for Dual Login System

## Required API Endpoints

### 1. Admin Login
```http
POST /auth/admin/login
Content-Type: application/json

Request Body:
{
  "email": "admin@company.com",
  "password": "securepassword"
}

Success Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Admin User",
    "email": "admin@company.com",
    "role": "admin"  // ⚠️ MUST be "admin"
  }
}

Error Response (401 Unauthorized):
{
  "detail": "Invalid admin credentials"
}
```

### 2. User Login
```http
POST /auth/user/login
Content-Type: application/json

Request Body:
{
  "email": "user@company.com",
  "password": "securepassword"
}

Success Response (200 OK):
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "name": "Regular User",
    "email": "user@company.com",
    "role": "user"  // ⚠️ MUST be "user"
  }
}

Error Response (401 Unauthorized):
{
  "detail": "Invalid user credentials"
}
```

---

## Critical Requirements

### ⚠️ Role Field is MANDATORY

The `user` object in the response **MUST** include a `role` field with one of these exact values:
- `"admin"` - for administrators
- `"user"` - for regular users

**Example:**
```json
{
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "admin"  // ← This field is required!
  }
}
```

---

## Database Schema Updates

### User Table
Add a `role` column if it doesn't exist:

```sql
-- PostgreSQL
ALTER TABLE users 
ADD COLUMN role VARCHAR(20) DEFAULT 'user' 
CHECK (role IN ('admin', 'user'));

-- Create index for faster role lookups
CREATE INDEX idx_users_role ON users(role);
```

**Recommended User Model:**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")  # "admin" or "user"
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

---

## Backend Permission Enforcement

### ⚠️ CRITICAL: Server-Side Validation

**Never trust the frontend!** Always validate permissions on the backend.

### Example: Project Creation Endpoint
```python
from fastapi import HTTPException, Depends
from app.utils.auth import get_current_user

@router.post("/projects")
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user)
):
    # ✅ Verify user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can create projects"
        )
    
    # Create project logic...
    return created_project
```

### Example: Project Deletion Endpoint
```python
@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    # ✅ Verify user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only administrators can delete projects"
        )
    
    # Delete project logic...
    return {"message": "Project deleted"}
```

---

## Permission Matrix (Backend Enforcement)

| Endpoint | Admin | User | Enforcement |
|----------|-------|------|-------------|
| `POST /auth/admin/login` | ✅ | ❌ | Check credentials against admin users |
| `POST /auth/user/login` | ❌ | ✅ | Check credentials against regular users |
| `GET /projects` | ✅ | ✅ | No restriction |
| `GET /projects/{id}` | ✅ | ✅ | No restriction |
| `POST /projects` | ✅ | ❌ | **Check role === "admin"** |
| `DELETE /projects/{id}` | ✅ | ❌ | **Check role === "admin"** |
| `POST /projects/{id}/upload` | ✅ | ✅ | No restriction |
| `GET /projects/{id}/documents` | ✅ | ✅ | No restriction |
| `POST /chat/{project_id}` | ✅ | ✅ | No restriction |
| `GET /chat/history/{project_id}` | ✅ | ✅ | No restriction |

---

## Implementation Options

### Option 1: Separate Login Endpoints (Recommended)

```python
# routes/auth.py

@router.post("/auth/admin/login")
async def admin_login(credentials: LoginRequest):
    user = authenticate_user(credentials.email, credentials.password)
    
    # Verify user is admin
    if not user or user.role != "admin":
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }

@router.post("/auth/user/login")
async def user_login(credentials: LoginRequest):
    user = authenticate_user(credentials.email, credentials.password)
    
    # Verify user is regular user
    if not user or user.role != "user":
        raise HTTPException(status_code=401, detail="Invalid user credentials")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }
```

### Option 2: Single Login with Role Check

```python
@router.post("/auth/login")
async def login(credentials: LoginRequest):
    user = authenticate_user(credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role  # Frontend will handle routing based on role
        }
    }
```

---

## JWT Token Structure

Include the role in the JWT payload for easier verification:

```python
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "sub": data["sub"],      # user email
        "role": data["role"]     # user role
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Decoded Token Example:**
```json
{
  "sub": "admin@company.com",
  "role": "admin",
  "exp": 1234567890
}
```

---

## Dependency for Role Checking

```python
# utils/auth.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    user = get_user_by_email(email)
    if user is None:
        raise credentials_exception
    
    return user

async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency that requires admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user
```

**Usage:**
```python
@router.post("/projects")
async def create_project(
    project: ProjectCreate,
    admin: User = Depends(require_admin)  # ✅ Only admins can access
):
    # Create project...
    pass
```

---

## Testing Checklist

### Backend Tests

- [ ] Admin can login via `/auth/admin/login`
- [ ] User can login via `/auth/user/login`
- [ ] Admin login rejects user credentials
- [ ] User login rejects admin credentials
- [ ] Response includes `role` field
- [ ] JWT token includes role in payload
- [ ] Admin can create projects
- [ ] User cannot create projects (403 error)
- [ ] Admin can delete projects
- [ ] User cannot delete projects (403 error)
- [ ] Both roles can view projects
- [ ] Both roles can upload documents
- [ ] Both roles can chat

### Example Test Cases

```python
# test_auth.py

def test_admin_login_success():
    response = client.post("/auth/admin/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["role"] == "admin"
    assert "access_token" in data

def test_user_cannot_create_project():
    # Login as user
    login_response = client.post("/auth/user/login", json={
        "email": "user@test.com",
        "password": "user123"
    })
    token = login_response.json()["access_token"]
    
    # Try to create project
    response = client.post(
        "/projects",
        json={"name": "Test Project"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "admin" in response.json()["detail"].lower()
```

---

## Migration Script

If you have existing users, run this migration:

```python
# migrations/add_role_to_users.py

from app.database import SessionLocal
from app.models.user import User

def migrate_users():
    db = SessionLocal()
    
    # Set first user as admin
    first_user = db.query(User).first()
    if first_user:
        first_user.role = "admin"
    
    # Set all other users as regular users
    other_users = db.query(User).filter(User.id != first_user.id).all()
    for user in other_users:
        user.role = "user"
    
    db.commit()
    db.close()
    
    print("✅ User roles migrated successfully")

if __name__ == "__main__":
    migrate_users()
```

---

## Environment Variables

Add these to your `.env` file:

```bash
# JWT Configuration
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Default Admin (for seeding)
DEFAULT_ADMIN_EMAIL=admin@company.com
DEFAULT_ADMIN_PASSWORD=changeme123
DEFAULT_ADMIN_NAME=System Administrator
```

---

## Summary

✅ **Must Have:**
1. Two login endpoints: `/auth/admin/login` and `/auth/user/login`
2. `role` field in user response (`"admin"` or `"user"`)
3. Server-side permission checks for admin-only operations
4. Role included in JWT token payload

✅ **Recommended:**
- Separate admin and user login logic
- Role-based dependency injection
- Comprehensive error messages
- Audit logging for admin actions

⚠️ **Security:**
- Never trust frontend role information
- Always validate permissions server-side
- Use HTTPS in production
- Implement rate limiting on login endpoints
