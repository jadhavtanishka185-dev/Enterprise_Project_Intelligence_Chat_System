# Login System Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         ENTRY POINTS                             │
└─────────────────────────────────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌───────────────────┐     ┌───────────────────┐
        │  /admin/login     │     │  /user/login      │
        │  (AdminLoginPage) │     │  (UserLoginPage)  │
        └───────────────────┘     └───────────────────┘
                    │                         │
                    │                         │
        ┌───────────▼───────────┐ ┌──────────▼──────────┐
        │ POST /auth/admin/login│ │ POST /auth/user/login│
        │ email: string         │ │ email: string        │
        │ password: string      │ │ password: string     │
        └───────────┬───────────┘ └──────────┬──────────┘
                    │                         │
                    │                         │
        ┌───────────▼───────────┐ ┌──────────▼──────────┐
        │ Response:             │ │ Response:            │
        │ - access_token        │ │ - access_token       │
        │ - user: {             │ │ - user: {            │
        │     role: "admin"     │ │     role: "user"     │
        │   }                   │ │   }                  │
        └───────────┬───────────┘ └──────────┬──────────┘
                    │                         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Store in Context     │
                    │   - localStorage       │
                    │   - AuthContext        │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │   Navigate to          │
                    │   /dashboard           │
                    └────────────┬───────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                         DASHBOARD                                │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Header Section                         │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  if (user.role === 'admin')                        │  │  │
│  │  │    ✅ Show "New Project" Button                    │  │  │
│  │  │  else                                               │  │  │
│  │  │    ❌ Hide "New Project" Button                    │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   Projects Grid                           │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  ProjectCard                                       │  │  │
│  │  │  ┌──────────────────────────────────────────────┐ │  │  │
│  │  │  │  if (user.role === 'admin')                  │ │  │  │
│  │  │  │    ✅ Show Delete Button                     │ │  │  │
│  │  │  │  else                                         │ │  │  │
│  │  │  │    ❌ Hide Delete Button                     │ │  │  │
│  │  │  └──────────────────────────────────────────────┘ │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Sidebar                                │  │
│  │  ┌────────────────────────────────────────────────────┐  │  │
│  │  │  User Avatar:                                      │  │  │
│  │  │    if (user.role === 'admin')                      │  │  │
│  │  │      🔴 Red Background                             │  │  │
│  │  │      Badge: "admin" (red text)                     │  │  │
│  │  │    else                                             │  │  │
│  │  │      🔵 Blue Background                            │  │  │
│  │  │      Badge: "user" (blue text)                     │  │  │
│  │  └────────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ (Logout)
                                 ▼
                    ┌────────────────────────┐
                    │  Clear localStorage    │
                    │  Clear AuthContext     │
                    └────────────┬───────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
        ┌───────────────────┐     ┌───────────────────┐
        │  if role='admin'  │     │  if role='user'   │
        │  → /admin/login   │     │  → /user/login    │
        └───────────────────┘     └───────────────────┘
```

---

## Component Hierarchy

```
App.jsx
├── PublicRoute
│   ├── AdminLoginPage (/admin/login)
│   └── UserLoginPage (/user/login)
│
└── PrivateRoute
    ├── DashboardPage (/dashboard)
    │   ├── Sidebar
    │   │   └── User Info (role-based styling)
    │   ├── Header
    │   │   └── New Project Button (admin only)
    │   └── ProjectCard (multiple)
    │       └── Delete Button (admin only)
    │
    ├── ProjectPage (/projects/:id)
    │   ├── Sidebar
    │   └── DocumentUpload
    │
    └── ChatPage (/projects/:id/chat)
        ├── Sidebar
        └── Chat Interface
```

---

## Permission Matrix

| Feature                    | Admin | User |
|----------------------------|-------|------|
| Login via /admin/login     | ✅    | ❌   |
| Login via /user/login      | ❌    | ✅   |
| View Dashboard             | ✅    | ✅   |
| Create New Project         | ✅    | ❌   |
| Delete Project             | ✅    | ❌   |
| View Projects              | ✅    | ✅   |
| Upload Documents           | ✅    | ✅   |
| Chat with AI               | ✅    | ✅   |
| View Chat History          | ✅    | ✅   |
| See "New Project" Button   | ✅    | ❌   |
| See Delete Button          | ✅    | ❌   |
| Red Role Badge             | ✅    | ❌   |
| Blue Role Badge            | ❌    | ✅   |

---

## State Management Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      AuthContext                             │
│                                                              │
│  State:                                                      │
│    - user: { id, name, email, role }                        │
│    - loading: boolean                                        │
│                                                              │
│  Methods:                                                    │
│    - login(token, userData)                                  │
│    - logout()                                                │
│                                                              │
│  Storage:                                                    │
│    - localStorage.setItem('token', token)                    │
│    - localStorage.setItem('user', JSON.stringify(user))      │
│                                                              │
│  API Interceptor:                                            │
│    - Attaches Bearer token to all requests                   │
│    - Handles 401 errors globally                             │
└─────────────────────────────────────────────────────────────┘
```

---

## API Request Flow

```
Frontend Component
      │
      ▼
authService.adminLogin(email, password)
      │
      ▼
axios.post('/api/auth/admin/login', { email, password })
      │
      ▼
Vite Proxy (port 3000 → 8000)
      │
      ▼
Backend API (http://localhost:8000/auth/admin/login)
      │
      ▼
Response: { access_token, user: { role: 'admin' } }
      │
      ▼
AuthContext.login(token, user)
      │
      ▼
localStorage + State Update
      │
      ▼
Navigate to /dashboard
```

---

## Role Detection Logic

```javascript
// In any component
import { useAuth } from '../context/AuthContext'

function MyComponent() {
  const { user } = useAuth()
  
  // Check if admin
  const isAdmin = user?.role === 'admin'
  
  // Conditional rendering
  return (
    <>
      {isAdmin && <AdminOnlyButton />}
      {!isAdmin && <UserMessage />}
    </>
  )
}
```

---

## Security Notes

⚠️ **Frontend role checking is for UI purposes only**

The backend MUST enforce all permissions:
- Verify JWT token on every request
- Check user role before allowing operations
- Never trust client-side role information
- Validate permissions server-side for:
  - Project creation
  - Project deletion
  - Document upload
  - Any sensitive operations

Frontend role checking only controls what UI elements are visible, not what operations are actually allowed.
