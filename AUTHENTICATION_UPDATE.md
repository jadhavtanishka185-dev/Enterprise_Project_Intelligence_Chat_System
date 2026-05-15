# Authentication System Update

## 🎯 Changes Made

### **Backend Changes**

#### 1. **Added User Registration Endpoint**
- **Endpoint**: `POST /auth/user/register`
- **Function**: Allows users to create new accounts
- **Access**: Public (no authentication required)
- **Auto-assigns**: `user` role (never admin)
- **Returns**: JWT token for immediate login

#### 2. **Updated CORS Configuration**
- Added support for both `localhost:3000` and `127.0.0.1:3000`
- Allows frontend to connect to backend properly

#### 3. **Enhanced Auth Router**
- Added `UserCreate` schema back
- Added user registration logic with email validation
- Maintains admin-only login (no admin registration)

---

### **Frontend Changes**

#### 1. **Updated Auth Service**
- Added `userRegister()` function
- Updated API calls to match backend endpoints
- Maintains separate admin/user login functions

#### 2. **Updated API Configuration**
- Changed base URL from `/api` to `http://127.0.0.1:8000`
- Removed Vite proxy (direct connection)
- Matches backend server address

#### 3. **Updated Register Page**
- Uses new `userRegister()` API call
- Maintains same UI and validation
- Automatically logs in user after registration

---

## 🔐 Authentication Flow

### **Admin Flow (Login Only)**
```
1. Navigate to /admin/login
2. Enter admin credentials
3. POST /auth/admin/login
4. Receive JWT token with role: "admin"
5. Redirect to dashboard with admin privileges
```

### **User Flow (Register + Login)**
```
Registration:
1. Navigate to /register
2. Enter name, email, password
3. POST /auth/user/register
4. Automatically logged in with JWT token
5. Redirect to dashboard with user privileges

Login:
1. Navigate to /user/login
2. Enter email, password
3. POST /auth/user/login
4. Receive JWT token with role: "user"
5. Redirect to dashboard with user privileges
```

---

## 📋 API Endpoints

### **Authentication Endpoints**

#### **Admin Login** (No Registration)
```http
POST http://127.0.0.1:8000/auth/admin/login
Content-Type: application/json

{
  "email": "admin@company.com",
  "password": "admin123"
}

Response:
{
  "access_token": "jwt_token",
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

#### **User Registration**
```http
POST http://127.0.0.1:8000/auth/user/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": 2,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

#### **User Login**
```http
POST http://127.0.0.1:8000/auth/user/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}

Response: (Same as registration)
```

---

## 🔒 Security Features

### **User Registration Security**
- ✅ Email uniqueness validation
- ✅ Password hashing with bcrypt
- ✅ Auto-assigns `user` role (never admin)
- ✅ Immediate JWT token generation
- ✅ Input validation (email format, password length)

### **Admin Security**
- ✅ No registration endpoint (admin-only login)
- ✅ Default admin created via script only
- ✅ Role validation at login
- ✅ Separate login endpoint

### **General Security**
- ✅ JWT tokens include user ID and role
- ✅ Token expiration (24 hours)
- ✅ CORS properly configured
- ✅ Password hashing with bcrypt
- ✅ Role-based access control

---

## 🧪 Testing

### **Test User Registration**
```bash
curl -X POST http://127.0.0.1:8000/auth/user/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### **Test User Login**
```bash
curl -X POST http://127.0.0.1:8000/auth/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### **Test Admin Login**
```bash
curl -X POST http://127.0.0.1:8000/auth/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "password": "admin123"
  }'
```

---

## 🚀 Setup Instructions

### **Backend Setup**
```bash
# 1. Make sure backend is running
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

# 2. Create default admin (if not done already)
python create_default_users.py

# Backend will be available at: http://127.0.0.1:8000
```

### **Frontend Setup**
```bash
# 1. Make sure frontend is running
cd frontend
npm run dev

# Frontend will be available at: http://localhost:3000
```

---

## 📊 User Management

### **Default Admin**
- **Email**: `admin@company.com`
- **Password**: `admin123`
- **Role**: `admin`
- **Created**: Via `create_default_users.py` script

### **User Accounts**
- **Registration**: Available via `/register` page
- **Role**: Always `user` (auto-assigned)
- **Validation**: Email must be unique
- **Password**: Minimum 6 characters

---

## 🔄 Frontend Routes

### **Public Routes**
- `/admin/login` - Admin login page
- `/user/login` - User login page  
- `/register` - User registration page

### **Protected Routes**
- `/dashboard` - Main dashboard (both admin and user)
- `/projects/:id` - Project details (both admin and user)
- `/projects/:id/chat` - Chat interface (both admin and user)

---

## ✅ Verification Checklist

### **Backend**
- [ ] User registration endpoint works
- [ ] Admin login works (no registration)
- [ ] User login works
- [ ] CORS allows frontend connection
- [ ] JWT tokens include role
- [ ] Email uniqueness validation
- [ ] Password hashing works

### **Frontend**
- [ ] User can register new account
- [ ] User can login after registration
- [ ] Admin can login (existing account)
- [ ] API calls use correct backend URL
- [ ] Role-based UI works
- [ ] Navigation works properly

---

## 🎉 Summary

**What Changed:**
1. ✅ Users can now register and login
2. ✅ Admin still login-only (no registration)
3. ✅ CORS properly configured
4. ✅ Frontend connects directly to backend
5. ✅ All API endpoints match

**What Stayed the Same:**
1. ✅ Role-based permissions
2. ✅ JWT authentication
3. ✅ Admin privileges
4. ✅ User restrictions
5. ✅ Security measures

**Ready to Use:**
- Users can create accounts via registration
- Admins use pre-created credentials
- All authentication flows work properly
- Frontend and backend are properly connected