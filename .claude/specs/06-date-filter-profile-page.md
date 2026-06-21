# Spec: Date Filter for Profile Page

## Overview
Step 6 adds a date range filter to the profile page so users can narrow
all four data sections — summary stats, transaction list, and category
breakdown — to a chosen window of time. The filter is a simple HTML form
(two `<input type="date">` fields and a submit button) that appends
`start` and `end` query parameters to `GET /profile`. When no params are
present the page behaves exactly as before, showing all-time data. This
step requires no new routes and no schema changes; it extends the three
query helpers in `database/queries.py` to accept optional date bounds and
updates the profile route and template to wire them together.

## Depends on
- Step 1: Database setup (`expenses.date` TEXT column, ISO format `YYYY-MM-DD`)
- Step 5: Backend connection (`get_summary_stats`, `get_recent_transactions`,
  `get_category_breakdown` exist in `database/queries.py`; `/profile` uses them)

## Routes
No new routes. `GET /profile` is modified to read optional `start` and `end`
query parameters (both `YYYY-MM-DD` strings) and pass them to queries and
the template.

## Database changes
No database changes. `expenses.date` is already stored as ISO-format TEXT;
SQLite lexicographic comparison on ISO dates is correct for range queries.

## Templates
- **Modify:** `templates/profile.html`
  - Add a date filter form above the stats row containing:
    - `<input type="date" name="start">` pre-filled with the active `start` value
    - `<input type="date" name="end">` pre-filled with the active `end` value
    - A submit button labelled "Apply"
    - A "Clear" link to `url_for('profile')` that is only rendered when at
      least one filter param is active
  - Show a banner / notice when a filter is active (e.g. "Showing results
    from X to Y") so the user knows the data is scoped

## Files to change
- `app.py` — update `profile()` to read `request.args.get("start")` and
  `request.args.get("end")`; validate that if both are present `start <= end`
  (if not, treat both as `None`); pass `start_date` / `end_date` to each
  query helper; pass `start` and `end` strings back to the template context
- `database/queries.py` — add optional `start_date=None` and `end_date=None`
  keyword arguments to `get_summary_stats`, `get_recent_transactions`, and
  `get_category_breakdown`; append `AND date >= ?` / `AND date <= ?` clauses
  only when the corresponding argument is not `None`
- `templates/profile.html` — date filter form and active-filter banner (above)
- `static/css/profile.css` — styles for `.date-filter` form and `.filter-active`
  banner; use CSS variables only — no hardcoded hex values

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`
- Parameterised queries only — never string-format values into SQL
- Use CSS variables — never hardcode hex values
- All templates extend `base.html`
- No inline `<style>` tags
- The three query helpers must remain backwards-compatible — callers that
  omit `start_date`/`end_date` must continue to get all-time data
- Date validation in the route: if both params are supplied and `start > end`,
  silently reset both to `None` (show all-time data, no error page)
- `get_recent_transactions` must respect the date filter **in addition to**
  its existing `limit` parameter; filtered results are still ordered newest-first
- The "Clear" link must use `url_for('profile')` — never a hardcoded path
- Category breakdown and summary stats must reflect only the filtered date range
  when a filter is active

## Definition of done
- [ ] Visiting `/profile` with no query params shows all 8 seed transactions
      and ₹346.24 total (unchanged from Step 5)
- [ ] Visiting `/profile?start=2026-05-01&end=2026-05-08` shows exactly 4
      transactions (May 1, 3, 5, 8), total ₹172.50, top category "Bills"
- [ ] Visiting `/profile?start=2026-05-10` (no end) shows exactly 4
      transactions (May 10, 12, 14, 16) and total ₹123.74
- [ ] Visiting `/profile?end=2026-05-05` (no start) shows exactly 3
      transactions (May 1, 3, 5) and total ₹142.50
- [ ] Category breakdown updates to reflect only the filtered expenses
- [ ] Date inputs are pre-filled with the active filter values after applying
- [ ] A "Clear" link is visible when a filter is active and returns to
      unfiltered view when clicked
- [ ] Submitting start=2026-05-10 and end=2026-05-01 (end before start)
      shows all-time data — no error, no crash
- [ ] A logged-out user visiting `/profile?start=2026-05-01&end=2026-05-08`
      is redirected to `/login` (auth guard unchanged)
