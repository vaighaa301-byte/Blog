# Simple Blog

A beginner-friendly blog application built with Django. It uses Django's built-in user authentication, a SQLite database, Django ModelForms, templates, and the Django admin site.

## Features

- Register, log in, and log out with Django authentication.
- Browse and search posts by title; the list is paginated.
- Open a post to read its full content and optional featured image.
- Logged-in users can create posts. Each new post is automatically assigned to its author.
- Authors can edit and delete only their own posts.
- Django admin can manage users and posts, search post titles/content, and filter by dates.
- Post titles and content are required and display form validation errors.

## Requirements

- Python 3.10 or newer
- pip

## Git

The project folder is initialized as a local Git repository. To review and save your changes:

```powershell
git status
git add .
git commit -m "Create beginner Django blog"
```

To publish it online, create an empty repository on your Git hosting service, then add its URL and push:

```powershell
git remote add origin <repository-url>
git branch -M main
git push -u origin main
```

## Setup

Open a terminal in the project folder and create a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell does not allow activation, run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Set a development secret key for the current PowerShell window:

```powershell
$env:DJANGO_SECRET_KEY = python -c "import secrets; print(secrets.token_urlsafe(50))"
```

The secret key is read from the environment and is not stored in the project. Set it again in a new terminal window. For a deployed site, also set `DJANGO_DEBUG=False` and configure `ALLOWED_HOSTS` in `config/settings.py` for your domain.

## Database migrations

Create and apply the database tables:

```powershell
python manage.py makemigrations
python manage.py migrate
```

SQLite database and uploaded images are stored locally in `db.sqlite3` and `media/`. During local development, uploaded images are served by Django from `/media/`. In production, configure your web server or storage service to serve media files; Django's development media route is only enabled when `DEBUG=True`.

## Create an admin user

```powershell
python manage.py createsuperuser
```

Follow the prompts to choose an admin username and password. Visit `/admin/` after starting the site to manage users and posts.

## Run the website

```powershell
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. The main pages are:

- `/` — blog listing, title search, and pagination
- `/register/` — create an account
- `/login/` — log in
- `/logout/` — log out using the site's POST button
- `/posts/create/` — create a post
- `/posts/<id>/` — view a post
- `/posts/<id>/edit/` — edit your own post
- `/posts/<id>/delete/` — confirm deletion of your own post
- `/admin/` — Django admin
