# How to View Frontend Without Backend Connection

This guide shows you how to test and view the React frontend without connecting to the FastAPI backend.

## Quick Start (No Backend Required)

### 1. Start the Development Server

```bash
cd frontend
npm run dev
```

### 2. Access the Application

Open your browser and go to:
```
http://localhost:3000
```

## What You Can View Without Backend

### ✅ **Fully Functional (No Backend Needed)**

#### Dashboard Pages
- **Home Dashboard**: `http://localhost:3000/dashboard`
  - See "Finmentor is a fundamental analyst" hero text
  - View feature cards (FinAdvisor, FinBuilder, FinFinder)
  - Navigate between pages using sidebar menu
  - Toggle theme (light/dark mode)
  - Responsive sidebar (collapsible on mobile)

#### All Navigation Pages
- **Profile**: `http://localhost:3000/dashboard/profile`
- **Contact Us**: `http://localhost:3000/dashboard/contact`
- **FinAdvisor**: `http://localhost:3000/dashboard/finadvisor`
- **FinBuilder**: `http://localhost:3000/dashboard/finbuilder`
- **FinFinder**: `http://localhost:3000/dashboard/finfinder`

#### Sign-Up Page
- **Sign Up Form**: `http://localhost:3000/signup`
  - View the complete sign-up form
  - Test form validation (without submitting)
  - Toggle theme
  - See error messages for invalid inputs

### ⚠️ **Limited Without Backend**

#### Sign-Up Submission
- Form will show an error when you click "Sign Up"
- Error message: "An error occurred during sign up"
- This is expected since there's no backend to receive the request

## Testing the Frontend UI

### 1. Test Dashboard Navigation

1. Open `http://localhost:3000/dashboard`
2. Click on sidebar menu items:
   - Home
   - Profile
   - Contact Us
   - FinAdvisor
   - FinBuilder
   - FinFinder
3. Watch the URL change and content update
4. Test hover effects on menu items

### 2. Test Theme Toggle

1. Click the moon (🌙) icon in the sidebar header
2. Watch the theme switch to dark mode
3. Click the sun (☀️) icon to switch back to light mode
4. Refresh the page - theme should persist

### 3. Test Responsive Design

#### Desktop View (> 768px)
- Sidebar stays visible on the left
- Content area takes up remaining space
- All features visible

#### Mobile View (< 768px)
1. Resize browser to mobile size (or use DevTools)
2. Sidebar automatically hides
3. Hamburger menu (☰) appears in top-left
4. Click hamburger to open sidebar
5. Click outside sidebar (overlay) to close it
6. Click menu item - sidebar closes automatically

### 4. Test Sign-Up Form Validation (Without Submitting)

1. Go to `http://localhost:3000/signup`
2. **Test Username Validation**:
   - Type "ab" (too short) - see error
   - Type "validusername123" - error clears
3. **Test Email Validation**:
   - Type "invalidemail" - see error
   - Type "valid@email.com" - error clears
4. **Test Password Validation**:
   - Type "weak" - see error
   - Type "StrongPass123" - error clears
5. **Test Confirm Password**:
   - Type different password - see error
   - Type matching password - error clears

## Developer Tools Testing

### Open DevTools (F12)

#### 1. Responsive Design Mode
```
Chrome: Ctrl+Shift+M (Windows) or Cmd+Shift+M (Mac)
Firefox: Ctrl+Shift+M (Windows) or Cmd+Shift+M (Mac)
```

Test different screen sizes:
- iPhone SE: 375px
- iPhone 12: 390px
- iPad: 768px
- Desktop: 1920px

#### 2. Check Console
- No errors should appear (except API errors when submitting form)
- Theme changes should log successfully

#### 3. Check Network Tab
- Filter by "Fetch/XHR"
- When you submit sign-up form, you'll see a failed request to `/api/auth/signup`
- This is expected without backend

#### 4. Check Application Tab (Storage)
- localStorage → Theme should be saved as "light" or "dark"
- This proves theme persistence is working

## Simulating Backend Success (Optional)

If you want to test the success flow without a real backend, you can temporarily modify the code:

### Option 1: Mock Success in authService.js

Open `src/services/authService.js` and temporarily replace the `signUp` function:

```javascript
export const signUp = async (username, email, password) => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  // Return mock success response
  return {
    success: true,
    data: {
      id: "mock-user-id",
      username: username,
      email: email,
      created_at: new Date().toISOString()
    }
  };
};
```

Now when you submit the sign-up form:
1. See "Creating Account..." loading state
2. See "Account created successfully! Redirecting..." message
3. Automatically redirect to Dashboard after 2 seconds

**Remember to revert this change before connecting to real backend!**

## What to Look For

### ✅ **Working Correctly**

- Dashboard loads at `http://localhost:3000/dashboard`
- Sidebar shows all 6 menu items
- "Finmentor is a fundamental analyst" text displays prominently
- Feature cards show FinAdvisor, FinBuilder, FinFinder
- Theme toggle button in sidebar header
- Clicking menu items navigates between pages
- Active menu item highlights correctly
- Theme persists after page reload
- Mobile hamburger menu works on small screens
- Sidebar closes automatically on mobile after navigation
- Sign-up form shows validation errors
- No email icon visible (removed the autocomplete icon issue)

### ❌ **Expected Limitations (No Backend)**

- Sign-up form submission shows error
- No real user authentication
- No data persistence (except theme in localStorage)
- API calls fail (this is normal without backend)

## Live Editing While Running

With Vite's hot module replacement (HMR), you can edit files and see changes instantly:

### Try This:

1. Open `src/components/Dashboard.jsx`
2. Change the hero text from "Finmentor is a fundamental analyst" to "Welcome to FinMentor"
3. Save the file
4. Watch the browser update automatically (no refresh needed!)
5. Change it back and save again

### Edit Styles:

1. Open `src/components/Dashboard.css`
2. Change `.hero-text` font-size from `32px` to `40px`
3. Save
4. See the text size change instantly

## Quick URLs Reference

```
Main Dashboard:     http://localhost:3000/dashboard
Profile:           http://localhost:3000/dashboard/profile
Contact Us:        http://localhost:3000/dashboard/contact
FinAdvisor:        http://localhost:3000/dashboard/finadvisor
FinBuilder:        http://localhost:3000/dashboard/finbuilder
FinFinder:         http://localhost:3000/dashboard/finfinder
Sign Up:           http://localhost:3000/signup
```

## Stop the Dev Server

When you're done testing:

```bash
# In the terminal where npm run dev is running
Ctrl + C
```

## Restart After Changes

```bash
npm run dev
```

## Build for Production (Without Backend)

You can also build the static site:

```bash
npm run build
```

Then preview it:

```bash
npm run preview
```

Access at `http://localhost:4173`

## Troubleshooting

### Issue: Port 3000 already in use
```bash
# Kill the process
npx kill-port 3000

# Or use different port
npm run dev -- --port 3001
```

### Issue: Changes not reflecting
1. Stop dev server (Ctrl+C)
2. Clear browser cache (Ctrl+Shift+Delete)
3. Restart dev server (`npm run dev`)
4. Hard refresh browser (Ctrl+F5)

### Issue: Theme not persisting
- Check browser console for errors
- Verify localStorage is enabled (not in private mode)
- Try different browser

### Issue: Sidebar not opening on mobile
- Clear browser cache
- Check browser console for JavaScript errors
- Test in different browser

## Summary

**You can fully test the frontend UI without any backend connection!**

✅ Dashboard navigation
✅ Theme toggle
✅ Responsive design
✅ Form validation
✅ All page layouts
✅ Hover effects
✅ Mobile menu

❌ Only thing that won't work: Actual sign-up submission (needs backend)

---

**Enjoy exploring the frontend! 🚀**
