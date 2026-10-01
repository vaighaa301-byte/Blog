# Simple Blog

A small beginner-friendly blog built with Python and Django. It demonstrates
Django models, views, templates, forms, authentication, URL routing, the ORM,
CRUD operations, and the Django admin.

Users can browse posts without an account. After registering or logging in,
they can write posts with an optional featured image and manage their own
posts. Visitors can search posts by title or content and browse results a few
posts at a time. The Django admin can manage users and all posts.

## Requirements

- Python 3.10 or newer
- Git

## Installation and setup (Windows PowerShell)

Open PowerShell in the project folder and create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt and run:

```cmd
.venv\Scripts\activate.bat
```

Install the packages:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Set a private Django secret key for this PowerShell session. This generates a
random key using Django; do not share it or commit it:

```powershell
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set the secret again in each new terminal session before running Django.

## Database migration

Create the local SQLite database tables:

```powershell
python manage.py migrate
```

## Create an admin user

Create a username and password when prompted:

```powershell
python manage.py createsuperuser
```

## Run the project

Start Django's development server:

```powershell
python manage.py runserver
```

Open <http://127.0.0.1:8000/> for the blog, or
<http://127.0.0.1:8000/admin/> for the admin panel. The development server is
for local development, not production hosting.

## Main pages

- `/` - list all posts
- Search by entering a word from the post title or content on the home page
- `/register/` - create an account
- `/login/` and `/logout/` - sign in and out
- `/posts/create/` - write a post
- `/posts/<id>/` - view a post
- `/posts/<id>/edit/` and `/posts/<id>/delete/` - manage your own post
- `/admin/` - Django admin

## Project layout

- `config/` - Django project settings and main URL configuration
- `blog/` - post model, forms, views, URLs, admin configuration, and tests
- `blog/migrations/` - database schema migrations
- `templates/` - shared `base.html` and organized page templates
- `static/` - stylesheet

## Git

This project is in a local Git repository. To save your changes:

```powershell
git status
git add .gitignore README.md requirements.txt blog config static templates manage.py
git commit -m "Build simple Django blog"
```

To publish it, first create an empty repository on your Git hosting service,
then connect and push your local repository:

```powershell
git remote add origin <repository-url>
git branch -M main
git push -u origin main
```

Do not add your `.env` file, secret key, database, or uploaded media to Git.

## Run tests

With the virtual environment active and `DJANGO_SECRET_KEY` set, run:

```powershell
python manage.py test
```
