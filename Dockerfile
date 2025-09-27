# Multi-stage build for OBCMS production optimization
FROM python:3.12-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/ requirements/
RUN pip install -r requirements/base.txt

# Development stage
FROM base as development
RUN pip install -r requirements/development.txt
USER app

# Production stage
FROM base as production
COPY --chown=app:app . /app/
RUN python src/manage.py collectstatic --noinput --settings=obc_management.settings_minimal
USER app

# Default command
CMD ["gunicorn", "--chdir", "src", "--bind", "0.0.0.0:8000", "obc_management.wsgi:application"]