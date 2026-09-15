# Job Hunt CRM

A Django app for tracking job applications: companies, contacts, application
status pipeline, and a dashboard with basic analytics (response rate, pipeline
funnel, follow-up reminders).

## Features

- **Companies** — name, website, location, notes, and per-company contacts
- **Applications** — job title, status (Applied → Phone Screen → Interview →
  Offer / Rejected / Withdrawn), salary range, notes
- **Automatic status history** — every status change is logged with a
  timestamp via a Django signal, so each application has a full audit trail
- **Dashboard** — total/active application counts, response rate, a visual
  pipeline funnel, a "needs follow-up" list (applied 7+ days ago with no
  movement), and a recent-activity feed
- **Per-user data isolation** — everything is scoped to the logged-in user;
  one user can't see another's companies or applications
- **Search & filter** — filter the application list by status or search by
  job title / company name
- **Django admin** — full admin access to all models, including inline
  contacts and status history

## Requirements

- Python 3.10+
- pip

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Create an admin user (optional, for /admin/)
python manage.py createsuperuser

# 5. Run the dev server
python manage.py runserver
```

Then visit **http://127.0.0.1:8000/** and sign up for an account (or log in
with the superuser you created).

## Project layout

```
jobhunt_crm/
├── jobhunt_crm/          # project settings, root urls
├── tracker/               # the main app
│   ├── models.py          # Company, Contact, Application, StatusHistory
│   ├── signals.py         # auto-logs status changes to StatusHistory
│   ├── views.py           # dashboard + CRUD views (class-based + function)
│   ├── forms.py           # ModelForms for Company, Contact, Application
│   ├── admin.py           # admin registrations
│   ├── urls.py            # app-level routes
│   └── templates/
│       ├── base.html
│       ├── registration/  # login, signup
│       └── tracker/       # dashboard, list/detail/form templates
├── static/css/style.css   # status badge colors, dashboard card styling
├── manage.py
└── requirements.txt
```

## How the status history works

`tracker/signals.py` hooks into `pre_save` (to stash the application's
*current* status before the update lands) and `post_save` (to compare it
against the *new* status and write a `StatusHistory` row if it changed, or
on first creation). This keeps the logging logic out of the views entirely —
whether you update an application through the UI, the admin, the shell, or a
future API, the history gets recorded the same way.

## Ideas for extending this

- **Reminders** — a management command + Celery/cron to email a digest of
  applications that `needs_follow_up`
- **File uploads** — attach resume/cover-letter versions per application
- **REST API** — add Django REST Framework and reuse the same models to
  power a React/mobile frontend
- **CSV/PDF export** — export the application list for backup or sharing
- **Interview scheduling** — a dedicated `Interview` model linked to
  `Application`, with round number and date

## Notes

- `DEBUG = True` and `SECRET_KEY` in `settings.py` are fine for local
  development only — regenerate the secret key and set `DEBUG = False` with
  a proper `ALLOWED_HOSTS` before deploying anywhere public.
- Uses SQLite by default (zero setup). Swap `DATABASES` in `settings.py` for
  Postgres/MySQL when you're ready to deploy.
