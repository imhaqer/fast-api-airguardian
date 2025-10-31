FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files FIRST
COPY pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

# Copy ALL application code
COPY . .

# Set Python path to include src directory
ENV PYTHONPATH=/app/src

EXPOSE 8000

# Run the application from the src directory
CMD ["uvicorn", "fast_api_airguardian.main:app", "--host", "0.0.0.0", "--port", "8000"]