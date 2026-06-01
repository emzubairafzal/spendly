# Spec: Login and Logout

## Overview
This feature wires up the `/login` form so users can authenticate and start a session, and replaces the `/logout` stub with a real implementation that clears that session. Flask's built-in `session` dict (backed by the already-configured `app.secret_key`) is used to store the logged-in user's `id` across requests. On a successful login the user is redirected to `/profile`; on logout they are redirected to `/`. The `base.html` nav is updated to show login/logout links depending on session state, making auth status visible across the whole app from this step forward.

## Depends on
- Step 01 — Database Setup (`users` table must exist, `get_db()` must work)
- Step 02 — Registration (users must exist in the DB to log in)

## Routes
- `GET /login` — render the login form — public (already exists, no change to GET behaviour)
- `POST /login` — validate credentials, set session, redirect to `/profile` — public
- `GET /logout` — clear session, redirect to `/` — logged-in (safe to call even when not logged in)

## Database changes
No schema changes. A new helper `get_user_by_email(email)` is added to `database/db.py` to look up a user row by email; it returns a `sqlite3.Row` or `None`.

## Templates
- **Create:** none
- **Modify:**
  - `templates/login.html` — add `method="POST"` to the form; add `action="{{ url_for('login') }}"` attribute; display `{{ error }}` inline when set; keep email field populated after a failed submission using `{{ email or '' }}`
  - `templates/base.html` — update the nav to show a "Log out" link (`url_for('logout')`) when `session.user_id` is set, and "Log in" / "Register" links when it is not

## Files to change
- `app.py` — convert `/login` to `methods=["GET", "POST"]`; add POST handler with validation, `check_password_hash`, session assignment (`session['user_id'] = user['id']`), and redirect; implement `/logout` to call `session.clear()` and redirect to `/`; import `session` and `check_password_hash`
- `database/db.py` — add `get_user_by_email(email)` helper
- `templates/login.html` — wire up POST form, error display, and email retention
- `templates/base.html` — add session-aware nav links

## Files to create
No new files.

## New dependencies
No new dependencies. `werkzeug.security.check_password_hash` is already available as a Flask dependency.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use string formatting in SQL
- Passwords verified with `werkzeug.security.check_password_hash` — never compare plain text
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- Import `session` from flask at the top of `app.py` alongside the existing flask imports
- On login failure, re-render `login.html` with `error=` and `email=` — do not redirect
- Use a single generic error message for both "email not found" and "wrong password" to avoid user enumeration: "Invalid email or password."
- `session.clear()` on logout — do not selectively pop keys
- The `get_user_by_email` helper must open and close its own connection (consistent with `get_db()` usage in the registration route)
- Redirect to `url_for('profile')` after successful login; redirect to `url_for('landing')` after logout

## Definition of done
- [ ] Submitting the login form with correct email and password sets `session['user_id']` and redirects to `/profile`
- [ ] Submitting with an unknown email shows "Invalid email or password." and the form re-renders
- [ ] Submitting with the correct email but wrong password shows "Invalid email or password." and the form re-renders
- [ ] After a failed login, the email field retains the submitted value
- [ ] Visiting `/logout` clears the session and redirects to `/`
- [ ] `base.html` nav shows "Log in" and "Register" when no user is in session
- [ ] `base.html` nav shows "Log out" when `session['user_id']` is set
- [ ] The demo user (`demo@spendly.com` / `demo123`) can log in successfully
