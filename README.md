# Django Gramm

Instagram-style social blog built with Django. Users can create posts with images, add tags and comments, like/dislike content, and follow each other. The project includes a simple frontend build step and a Docker setup for local or production-like runs.

Live demo: https://django-gramm.duckdns.org/

## Features
- User registration with email activation
- Login/logout + password reset and change
- Social login via Google and GitHub (OAuth)
- User profiles with bio and avatar
- Follow/unfollow users and view followers/following
- Feed of posts from followed users
- Create/edit/delete posts with multiple images
- Draft posts
- Tags on posts
- Comments with like/dislike
- Post like/dislike with instant counts
- Cloudinary media storage integration

## Tech Stack
- Django 5
- PostgreSQL
- Cloudinary for media
- social-auth-app-django for OAuth
- Webpack for frontend asset build
- Docker + docker-compose

## Project Structure
- `django_gramm/` Django project and apps
- `blog/` Posts, tags, comments, likes
- `users/` Profiles, auth flows, follow system
- `frontend/` Webpack build for static assets
- `static/` Static assets

## Environment Variables
Create a `.env` file in `django_gramm/` (see .env_example)

Required keys:
- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `CLOUD_NAME`, `API_KEY`, `API_SECRET`
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- `SOCIAL_AUTH_REDIRECT_IS_HTTPS`
- `CSRF_COOKIE_SECURE` (production)

## Local Development (without Docker)
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r django_gramm/requirements.txt
   ```
3. Set environment variables in `django_gramm/.env`.
4. Run migrations:
   ```bash
   python django_gramm/manage.py migrate
   ```
5. Start the server:
   ```bash
   python django_gramm/manage.py runserver
   ```
6. Open http://localhost:8000

Optional: populate sample data
```bash
python django_gramm/populate_fake.py
```

## Run with Docker
From `django_gramm/`:
```bash
docker-compose up --build
```
The app will be available at http://localhost:8000

## Tests
```bash
pytest
```

## Notes
- Media files are stored in Cloudinary (see environment variables).
- For production, set `DEBUG=False`, `SOCIAL_AUTH_REDIRECT_IS_HTTPS=True`, and `CSRF_COOKIE_SECURE=True`.

