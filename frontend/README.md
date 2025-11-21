# FinMentor AI - React Frontend

A modern, responsive React application with authentication and theme toggle functionality.

## Features

- ✅ **User Authentication**: Sign-up with username, email, and password
- ✅ **Password Security**: Client-side bcrypt hashing before transmission
- ✅ **Dashboard**: Complete dashboard with navigation sidebar
- ✅ **6 Navigation Pages**: Home, Profile, Contact Us, FinAdvisor, FinBuilder, FinFinder
- ✅ **Theme Toggle**: Light and dark mode with persistent preference
- ✅ **Responsive Design**: Flexbox-based layout for all screen sizes
- ✅ **Mobile Menu**: Collapsible sidebar with hamburger menu
- ✅ **Form Validation**: Real-time validation with helpful error messages
- ✅ **FastAPI Integration**: Seamless backend communication via Axios

## Tech Stack

- **React 18.2.0**: Modern UI library
- **Vite 5.0.8**: Fast build tool and dev server
- **React Router DOM 6.20.0**: Client-side routing
- **Axios 1.6.2**: HTTP client for API calls
- **bcryptjs 2.4.3**: Password hashing
- **CSS3**: Custom styling with flexbox and CSS variables

## Theme Colors

- **Light Mode**: `#8FABD4` (Soft blue)
- **Dark Mode**: `#435663` (Dark gray-blue)

## Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # React components
│   │   ├── Dashboard.jsx  # Dashboard with navigation
│   │   ├── Dashboard.css  # Dashboard styles
│   │   ├── SignUp.jsx     # Sign-up form component
│   │   └── SignUp.css     # Sign-up styles
│   ├── contexts/          # React contexts
│   │   └── ThemeContext.jsx  # Theme state management
│   ├── services/          # API services
│   │   └── authService.js # Authentication API calls
│   ├── App.jsx            # Main app component with routing
│   ├── main.jsx           # React entry point
│   └── index.css          # Global styles and CSS variables
├── index.html             # HTML entry point
├── vite.config.js         # Vite configuration
├── package.json           # Dependencies and scripts
├── README.md              # This file
├── SETUP.md               # Setup instructions
├── VIEW_WITHOUT_BACKEND.md # Guide to test without backend
├── QUICK_TEST_GUIDE.md    # Quick testing reference
└── DASHBOARD_IMPLEMENTATION.md # Dashboard details
```

## Installation

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

## Development

1. **Start the development server**:
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:3000`

2. **Make sure the backend is running**:
   The frontend is configured to proxy API requests to `http://localhost:8000`

## Build for Production

```bash
npm run build
```

The optimized production build will be in the `dist/` folder.

## Preview Production Build

```bash
npm run preview
```

## API Endpoints

The frontend communicates with the following backend endpoints:

- **POST /api/auth/signup**: Create a new user account
  - Request body: `{ username, email, hashed_password }`
  - Response: User object with id, username, email, etc.

## Form Validation

### Username
- Minimum 3 characters
- Maximum 20 characters
- Only letters, numbers, and underscores

### Email
- Valid email format (RFC 5322)
- Example: `user@example.com`

### Password
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number

## Theme Management

The theme is managed using React Context API and persisted in `localStorage`.

### Using the Theme
```jsx
import { useTheme } from './contexts/ThemeContext';

function MyComponent() {
  const { theme, toggleTheme, isDark } = useTheme();
  
  return (
    <button onClick={toggleTheme}>
      {isDark ? 'Light Mode' : 'Dark Mode'}
    </button>
  );
}
```

## Security

- Passwords are hashed with bcrypt on the client side before transmission
- 10 salt rounds used for bcrypt hashing
- HTTPS recommended for production deployment
- No sensitive data stored in localStorage (only theme preference)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Troubleshooting

### Port 3000 already in use
```bash
# Find and kill the process
npx kill-port 3000

# Or use a different port
npm run dev -- --port 3001
```

### Backend API not reachable
- Ensure the FastAPI backend is running on `http://localhost:8000`
- Check the proxy configuration in `vite.config.js`

### Theme not persisting
- Check browser console for localStorage errors
- Ensure cookies/localStorage are enabled in browser settings

## Future Enhancements

- [ ] Login page
- [ ] Password reset functionality
- [ ] Dashboard after successful signup
- [ ] Profile management
- [ ] Session management with JWT tokens
- [ ] Remember me functionality
- [ ] Social authentication (Google, GitHub)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is part of the FinMentor AI portfolio builder.
