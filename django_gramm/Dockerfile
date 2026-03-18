FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN adduser --disabled-password --gecos '' appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser

CMD ["gunicorn", "django_gramm.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]