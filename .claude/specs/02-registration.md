# Spec: Registration

## Overview
This feature wires up the existing `/register` form so users can actually create accounts. The template and form markup already exist; this step adds the POST handler to `app.py`, validates all inputs server-side, checks for duplicate emails, hashes the password with werkzeug, and inserts the new user into the `users` table. On success the user is redirected to the login page. On failure the form re-renders with an inline error message using the `error` variable the template already supports.

## Depends on
- Step 01 — Database Setup (`users` table must exist, `get_db()` must work)

## Routes
- `GET /register` — render the registration form — public (already exists, no change needed)
- `POST /register` — validate input, insert user, redirect to `/login` — public

## Database changes
No database changes. The `users` table created in Step 01 already has all required columns: `name`, `email`, `password_hash`, `created_at`.

## Templates
- **Create:** none
- **Modify:**
  - `templates/register.html` — add a "Confirm password" field between the password field and the submit button; re-populate `name` and `email` fields with `{{ request.form.name }}` / `{{ request.form.email }}` after a failed submission so the user doesn't have to retype them

## Files to change
- `app.py` — add `POST` method to `/register` route; import `request` and `redirect` from flask; import `url_for`; add `app.secret_key`; import `generate_password_hash` from werkzeug

## Files to create
No new files.

## New dependencies
No new dependencies. `werkzeug` is already installed as a Flask dependency.

## Rules for implementation
- No SQLAlchemy or ORMs
- Parameterised queries only — never use string formatting in SQL
- Passwords hashed with `werkzeug.security.generate_password_hash`
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- `app.secret_key` must be set before any session/flash usage (set it in `app.py` before routes)
- Re-render the form with `error=` on validation failure — do not use Flask `flash()` (session not set up until Step 03)
- Validation order: name not blank → valid email format → password >= 8 chars → passwords match → email not already taken
- Close the DB connection after every query (use `conn.close()` in a `finally` block or call it explicitly)
- On duplicate email, show: "An account with that email already exists."

## Definition of done
- [ ] Submitting the form with all valid fields creates a new row in `users` and redirects to `/login`
- [ ] The password stored in the DB is a hash, not plain text
- [ ] Submitting with an empty name shows an inline error and keeps the email field populated
- [ ] Submitting with a password shorter than 8 characters shows an inline error
- [ ] Submitting with mismatched passwords shows an inline error
- [ ] Submitting with an email that already exists shows "An account with that email already exists."
- [ ] After a failed submission, the name and email fields retain the submitted values
- [ ] The confirm password field is visible on the registration page
- [ ] Visiting `/register` as a GET request still renders the form with no errors
