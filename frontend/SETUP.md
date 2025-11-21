# Frontend Setup Instructions

Follow these steps to set up and run the React frontend application.

## Prerequisites

- Node.js 16.x or higher
- npm 8.x or higher
- FastAPI backend running on `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

Open a terminal in the `frontend/` directory and run:

```bash
cd frontend
npm install
```

This will install all required packages:
- react (18.2.0)
- react-dom (18.2.0)
- react-router-dom (6.20.0)
- axios (1.6.2)
- bcryptjs (2.4.3)
- vite (5.0.8)
- @vitejs/plugin-react (4.2.1)

### 2. Start Development Server

```bash
npm run dev
```

The app will start on `http://localhost:3000` by default.

You should see output like:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

### 3. Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the Sign-Up page with:
- Username field
- Email field
- Password field
- Confirm Password field
- Theme toggle button (🌙 for dark mode, ☀️ for light mode)
- Sign Up button

## Backend Setup

The frontend requires the FastAPI backend to be running. Make sure you've started the backend server:

### Starting the Backend

```bash
# From the project root directory
cd backend

# Activate virtual environment (if using one)
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend should be accessible at `http://localhost:8000`.

## Testing the Sign-Up Flow

1. **Open the application** at `http://localhost:3000`

2. **Fill in the form**:
   - Username: `testuser123` (3-20 chars, alphanumeric + underscore)
   - Email: `test@example.com` (valid email format)
   - Password: `TestPass123` (min 8 chars, 1 upper, 1 lower, 1 number)
   - Confirm Password: `TestPass123` (must match password)

3. **Toggle the theme** by clicking the moon/sun icon in the top-right

4. **Submit the form**:
   - Click "Sign Up" button
   - Password will be bcrypt-hashed on the client side
   - Request will be sent to `POST /api/auth/signup`
   - Success message will appear on successful registration

## Available Scripts

### `npm run dev`
Starts the development server with hot module replacement (HMR).
- URL: `http://localhost:3000`
- API proxy: Requests to `/api/*` are proxied to `http://localhost:8000`

### `npm run build`
Creates an optimized production build in the `dist/` folder.
- Minified and optimized JavaScript
- CSS extracted and optimized
- Assets with content hashes for caching

### `npm run preview`
Serves the production build locally for testing.
- Previews the built app before deployment
- URL: `http://localhost:4173` (default)

## Configuration

### Vite Configuration (`vite.config.js`)

The Vite dev server is configured to:
- Use port 3000
- Proxy API requests to `http://localhost:8000`
- Enable React Fast Refresh

### API Base URL

The API base URL is configured in `src/services/authService.js`:
```javascript
const API_BASE_URL = '/api';
```

All API requests are relative to this base URL and will be proxied to the backend.

## Troubleshooting

### Issue: Port 3000 is already in use

**Solution 1**: Kill the process using port 3000
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:3000 | xargs kill -9
```

**Solution 2**: Use a different port
```bash
npm run dev -- --port 3001
```

### Issue: API requests failing (CORS errors)

**Check**:
1. Backend is running on `http://localhost:8000`
2. Backend has CORS enabled for `http://localhost:3000`
3. Vite proxy is configured correctly in `vite.config.js`

**Backend CORS configuration** (should be in `backend/main.py`):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Theme not persisting

**Check**:
1. Browser console for localStorage errors
2. Browser settings allow localStorage
3. Not in private/incognito mode (localStorage may be disabled)

### Issue: Form validation not working

**Check**:
1. Browser console for JavaScript errors
2. All form fields have the correct `name` attributes
3. `authService.js` validation functions are imported correctly

### Issue: bcryptjs errors

**Solution**: Reinstall bcryptjs
```bash
npm uninstall bcryptjs
npm install bcryptjs
```

## Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. When you save a file:
- React components update without full page reload
- Component state is preserved
- Changes appear in <200ms

### React DevTools

Install React DevTools browser extension:
- Chrome: [React DevTools](https://chrome.google.com/webstore/detail/react-developer-tools/fmkadmapgofadopljbjfkapdkoienihi)
- Firefox: [React DevTools](https://addons.mozilla.org/en-US/firefox/addon/react-devtools/)

### Console Logging

Check the browser console (F12) for:
- API request/response logs
- Form validation errors
- Theme changes
- Navigation events

### Network Tab

Monitor API calls in the Network tab (F12):
- Filter by "Fetch/XHR"
- Check request payload (should have `hashed_password`)
- Check response status (200 for success)
- Check response body (user object)

## Production Deployment

### Build for Production

```bash
npm run build
```

This creates a `dist/` folder with optimized assets:
```
dist/
├── assets/
│   ├── index-[hash].js      # Minified JavaScript
│   └── index-[hash].css     # Optimized CSS
├── index.html               # HTML entry point
└── vite.svg                 # Vite logo
```

### Serve Static Files

You can serve the `dist/` folder using:

**Option 1: http-server (npm package)**
```bash
npx http-server dist -p 3000
```

**Option 2: Nginx**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /path/to/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Option 3: FastAPI Static Files**
Mount the frontend as static files in your FastAPI app:
```python
from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
```

## Environment Variables

For production, you may want to use environment variables:

### Create `.env` file (frontend root)
```env
VITE_API_BASE_URL=https://api.yourapp.com
```

### Update `authService.js`
```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
```

## Next Steps

After successful setup:

1. **Test the complete flow**:
   - Sign up with a new user
   - Check database for new user record
   - Verify password is bcrypt-hashed

2. **Add more features**:
   - Login page (`/login`)
   - Dashboard page (`/dashboard`)
   - Profile management
   - Password reset

3. **Enhance security**:
   - Add CSRF tokens
   - Implement rate limiting
   - Add captcha for bot protection
   - Use HTTPS in production

4. **Improve UX**:
   - Add loading spinners
   - Add success animations
   - Add error toasts
   - Add form auto-complete

## Need Help?

If you encounter any issues:

1. Check the browser console (F12) for errors
2. Check the terminal running `npm run dev` for build errors
3. Verify the backend is running and accessible
4. Check the Network tab for failed API requests
5. Review the `README.md` for detailed feature documentation

## Resources

- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [React Router Documentation](https://reactrouter.com/)
- [Axios Documentation](https://axios-http.com/)
- [bcrypt.js Documentation](https://www.npmjs.com/package/bcryptjs)

---

**Happy Coding! 🚀**
