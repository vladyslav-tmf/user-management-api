ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS base
LABEL maintainer="vladislav.tmf@gmail.com"

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install netcat for checking database connection in entrypoint script
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock* /app/

# Install Python dependencies
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy the source code into the container.
COPY . /app/

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/app" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

RUN chmod +x /app/entrypoint.sh \
    && chown -R appuser:appuser /app \
    && chmod -R 755 /app

# Switch to the non-privileged user to run the application.
USER appuser

# Expose the port that the application listens on.
EXPOSE 5000

# Run the application.
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0"]
