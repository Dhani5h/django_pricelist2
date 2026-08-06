# Price book

A small Django app for looking up wholesale and retail prices by item.
Employees use a plain search page; you (or any staff user) manage items
through the built-in Django admin.

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser   # this is your staff login
python manage.py runserver
```

Then open:

- `http://127.0.0.1:8000/` — the employee search page (no login needed)
- `http://127.0.0.1:8000/admin/` — add/edit/delete items and categories (staff login)
- `http://127.0.0.1:8000/bulk-add/` — paste in many items at once, staff login required

## Bulk-loading your first batch of items

Go to `/bulk-add/` while logged in as staff, and paste lines like:

```
A-102, 16oz claw hammer, Hand tools, 8.50, 14.99
B-014, Galvanized bucket 5gal, Storage, 3.20, 6.99
```

Format: `code, name, category, wholesale price, retail price`. Categories
are created automatically if they don't exist yet. Re-running a code
updates that item instead of duplicating it, so it's safe to re-paste an
updated list later.

## Deploying so employees can use it on their phones

The project is already set up for deployment: environment-driven settings,
`gunicorn` as the production server, `whitenoise` to serve static files
(no separate CDN needed), and Postgres support via `DATABASE_URL`.

### Railway

1. Push this project to a GitHub repo
2. On [railway.app](https://railway.app), "New Project" → "Deploy from GitHub repo" → pick it
3. Railway auto-detects the `Procfile` and installs `requirements.txt`
4. Add a Postgres database: "New" → "Database" → "PostgreSQL" — Railway sets
   `DATABASE_URL` automatically, no config needed on your end
5. In your app service's "Variables" tab, add:
   - `SECRET_KEY` — a long random string (e.g. generate one with
     `python -c "import secrets; print(secrets.token_urlsafe(50))"`)
   - `DEBUG` = `False`
   - `ALLOWED_HOSTS` = the `.up.railway.app` domain Railway gives you
   - `CSRF_TRUSTED_ORIGINS` = `https://` + that same domain
6. Railway runs `release: python manage.py migrate` automatically from the
   `Procfile` before each deploy, so tables get created/updated for you
7. Once deployed, visit the Railway URL, then run in Railway's shell (or
   locally against the same `DATABASE_URL`):
   ```bash
   python manage.py createsuperuser
   ```
8. Bookmark the Railway URL on employee phones — that's the whole rollout

### Render

Same idea, slightly different dashboard:

1. Push to GitHub, then "New" → "Web Service" on [render.com](https://render.com), pick the repo
2. Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn priceshop.wsgi`
4. Add a Postgres instance from Render's dashboard, copy its "Internal
   Database URL" into your web service's `DATABASE_URL` env var
5. Add the same `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS`,
   `CSRF_TRUSTED_ORIGINS` env vars as above, using your `.onrender.com` domain
6. Render doesn't run the `Procfile` release step automatically — add
   `python manage.py migrate` as a "Pre-Deploy Command" in the dashboard,
   or run it manually once via Render's shell
7. `python manage.py createsuperuser` via Render's shell, then share the URL

### Local development still works the same way

None of this changes your local workflow — with no environment variables
set, it falls back to `DEBUG=True` and SQLite automatically:

```bash
python manage.py migrate
python manage.py runserver
```

## Project structure

```
priceshop/
  manage.py
  priceshop/          # project settings, URLs
  catalog/            # the app: models, admin, views, templates
    models.py         # Category, Item
    admin.py           # staff CRUD via Django admin
    views.py           # search page + bulk add
    templates/catalog/
```
