---
name: spendly-ui
description: >
  Build, edit, or redesign UI pages for the Spendly expense tracking web application.
  Use this skill any time the user wants to create a new page, redesign an existing
  template, add a new component, style a view, or modify any HTML/CSS/JS in the
  Spendly project. Triggers include: "add a page", "redesign the dashboard",
  "update the nav", "create a modal", "fix the layout", "style the form",
  "make it look better", "add a chart", "build the settings page", or any
  reference to Spendly templates, static files, or UI. Always use this skill
  when working on any visual or structural aspect of Spendly — even if the user
  just says "make it look nicer" or "add a feature" that implies a new screen.
---

# Spendly UI Skill

Spendly is a **Flask + Jinja2 expense tracking web app** (Python backend, SQLite
database via SQLAlchemy). All UI lives in `templates/` (Jinja2 HTML) and
`static/` (CSS, JS, images). There is no frontend build step — vanilla
HTML/CSS/JS only. No React, no Tailwind, no bundler.

---

## Project Structure
spendly/
├── app.py                  # Flask routes and logic
├── database/               # SQLAlchemy models
├── templates/              # Jinja2 HTML templates
│   ├── base.html           # Master layout (nav, sidebar, head)
│   ├── index.html          # Dashboard / home
│   ├── add_expense.html    # Add expense form
│   ├── expenses.html       # Expense list/history
│   ├── categories.html     # Category management
│   └── ...                 # Other pages
└── static/
├── css/
│   └── style.css       # Main stylesheet
├── js/                 # Vanilla JS files
└── images/             # Icons, logos

---

## Design System & Visual Identity

Spendly is a **personal finance / expense tracking app**. The aesthetic should
feel: **clean, trustworthy, data-forward**. Think modern fintech — not bank-cold,
but calm and focused.

### Colour Palette
Use CSS custom properties defined in `static/css/style.css`:

```css
:root {
  --color-primary:     #4F46E5;   /* Indigo — primary actions, active states */
  --color-primary-light: #EEF2FF; /* Indigo tint — hover backgrounds */
  --color-danger:      #EF4444;   /* Red — delete, overspend */
  --color-success:     #10B981;   /* Green — income, positive */
  --color-warning:     #F59E0B;   /* Amber — nearing budget limit */
  --color-neutral-900: #111827;   /* Almost black — headings */
  --color-neutral-600: #4B5563;   /* Body text */
  --color-neutral-300: #D1D5DB;   /* Borders, dividers */
  --color-neutral-100: #F3F4F6;   /* Page background */
  --color-white:       #FFFFFF;   /* Card backgrounds */
  --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace; /* amounts, numbers */
}
```

### Typography
- Body: `var(--font-sans)` at 14–16px
- Currency / numbers: `var(--font-mono)` — this is critical for alignment
- Headings: 600–700 weight, `var(--color-neutral-900)`
- Load Inter from Google Fonts in `base.html` `<head>` if not already present

### Spacing Scale
Use multiples of 4px: `4 / 8 / 12 / 16 / 20 / 24 / 32 / 48 / 64px`

---

## Jinja2 Template Rules

Every page MUST extend `base.html`:
```html
{% extends "base.html" %}

{% block title %}Page Title — Spendly{% endblock %}

{% block content %}
<!-- page content here -->
{% endblock %}
```

Pass Flask context variables using `{{ variable }}` syntax.
Use `{{ url_for('static', filename='css/style.css') }}` for static assets.
Use `{{ url_for('route_name') }}` for internal links — never hardcode URLs.
Flash messages come via `get_flashed_messages(with_categories=true)`.

---

## Component Patterns

### Cards
```html
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Title</h3>
  </div>
  <div class="card-body">
    <!-- content -->
  </div>
</div>
```
CSS: white bg, `var(--radius-md)`, `var(--shadow-sm)`, 20px padding.

### Stat / KPI Card
```html
<div class="stat-card">
  <span class="stat-label">Total Spent</span>
  <span class="stat-value">£{{ total | round(2) }}</span>
  <span class="stat-delta positive">↑ 12% vs last month</span>
</div>
```
Use `positive` / `negative` class for delta colour.

### Data Tables
```html
<table class="data-table">
  <thead>
    <tr>
      <th>Date</th><th>Category</th><th>Amount</th><th>Actions</th>
    </tr>
  </thead>
  <tbody>
    {% for expense in expenses %}
    <tr>
      <td>{{ expense.date }}</td>
      <td><span class="badge badge--{{ expense.category|lower }}">{{ expense.category }}</span></td>
      <td class="amount">£{{ "%.2f"|format(expense.amount) }}</td>
      <td class="actions">
        <a href="{{ url_for('edit_expense', id=expense.id) }}" class="btn btn--ghost btn--sm">Edit</a>
        <form method="POST" action="{{ url_for('delete_expense', id=expense.id) }}" style="display:inline">
          <input type="hidden" name="_method" value="DELETE">
          <button type="submit" class="btn btn--danger btn--sm">Delete</button>
        </form>
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
```

### Forms
```html
<form method="POST" class="form">
  {{ form.hidden_tag() if form }}  {# CSRF token if using Flask-WTF #}
  <div class="form-group">
    <label class="form-label" for="amount">Amount (£)</label>
    <input type="number" id="amount" name="amount" class="form-control"
           step="0.01" min="0" placeholder="0.00" required>
  </div>
  <button type="submit" class="btn btn--primary">Save</button>
</form>
```

### Buttons
```html
<button class="btn btn--primary">Primary</button>
<button class="btn btn--secondary">Secondary</button>
<button class="btn btn--danger">Delete</button>
<button class="btn btn--ghost">Ghost</button>
<!-- Sizes: btn--sm  btn--md (default)  btn--lg -->
```

### Flash Messages
```html
{% with messages = get_flashed_messages(with_categories=true) %}
  {% if messages %}
    {% for category, message in messages %}
      <div class="alert alert--{{ category }}">{{ message }}</div>
    {% endfor %}
  {% endif %}
{% endwith %}
```
Use categories: `success`, `danger`, `warning`, `info`.

### Empty States
Always handle empty lists gracefully:
```html
{% if not expenses %}
<div class="empty-state">
  <span class="empty-state__icon">💸</span>
  <p class="empty-state__title">No expenses yet</p>
  <p class="empty-state__body">Start tracking by adding your first expense.</p>
  <a href="{{ url_for('add_expense') }}" class="btn btn--primary">Add Expense</a>
</div>
{% endif %}
```

---

## Charts & Data Visualisation

Use **Chart.js** loaded from CDN (no npm). Include at the bottom of the template,
inside a `{% block scripts %}{% endblock %}` block in `base.html`:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
```

Pass data from Flask → Jinja2 → JS like this:
```html
<canvas id="spendChart"></canvas>
<script>
  const chartData = {{ chart_data | tojson }};
  const ctx = document.getElementById('spendChart').getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: { labels: chartData.labels, datasets: [{ data: chartData.values,
      backgroundColor: ['#4F46E5','#10B981','#F59E0B','#EF4444','#8B5CF6'] }] },
    options: { plugins: { legend: { position: 'bottom' } }, cutout: '65%' }
  });
</script>
```

---

## Page Inventory

| Template | Route | Purpose |
|---|---|---|
| `index.html` | `/` | Dashboard: KPI cards, recent expenses, charts |
| `add_expense.html` | `/add` | Form to log a new expense |
| `expenses.html` | `/expenses` | Full expense history, filters, pagination |
| `categories.html` | `/categories` | Manage spending categories |
| `base.html` | — | Shared layout: nav, sidebar, head, scripts |

When adding a new page: create the template, add a route in `app.py`, add a nav
link in `base.html`, and handle any empty/error states.

---

## Navigation / Sidebar

The sidebar (in `base.html`) should use active state detection:
```html
<a href="{{ url_for('index') }}"
   class="nav-link {% if request.endpoint == 'index' %}active{% endif %}">
  <span class="nav-icon">🏠</span> Dashboard
</a>
```

---

## Accessibility Checklist

Every page must pass:
- All form inputs have `<label>` with matching `for` / `id`
- Buttons have descriptive text or `aria-label`
- Colour contrast: text ≥ 4.5:1 against background
- Tables have `<thead>` with `<th scope="col">`
- Flash / alert messages have `role="alert"`
- Interactive elements are keyboard-navigable (correct tab order)

---

## Currency & Number Formatting

- Always format amounts as `£{{ "%.2f"|format(amount) }}`
- Use `var(--font-mono)` on `.amount` cells for alignment
- Negative amounts (if ever shown) get `class="amount amount--negative"` (red)
- Large numbers: add a Jinja filter or JS `toLocaleString()` for thousands separator

---

## Production Quality Checklist

Before finishing any page, verify:
- [ ] Extends `base.html` and fills all required blocks
- [ ] All links use `url_for()`, never hardcoded paths
- [ ] Empty states handled for every list/table
- [ ] Flash messages block present
- [ ] Form has CSRF if Flask-WTF is active
- [ ] Mobile-responsive: sidebar collapses on small screens
- [ ] Uses only CSS variables from the design system (no ad-hoc hex codes)
- [ ] Numbers/currency use monospace font class
- [ ] No inline styles except truly one-off cases
- [ ] Chart.js data passed via `| tojson` filter, never string concatenation
- [ ] Accessibility checklist above passes