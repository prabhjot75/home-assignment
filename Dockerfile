# ====================================================================
# STAGE 1: Base Environment Builder
# ====================================================================
FROM python:3.13-slim AS base

WORKDIR /app

# Prevent Python from writing .pyc files and force unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install essential system tools required for compilation/native builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency catalogs and install to base layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ====================================================================
# STAGE 2: Test Automation Suite Pipeline
# ====================================================================
FROM base AS test-runner

# Install specific test utilities if not embedded in production requirements
RUN pip install --no-cache-dir openapi-spec-validator pytest

# Copy the entire source directory tree into the test execution sandbox
COPY . .

# Run the complete test suite automatically during image building phase.
# If any validation, auth, or edge case test fails, the build halts.
RUN python -m pytest -v

# ====================================================================
# STAGE 3: Service Deployment Stage
# ====================================================================
FROM base AS production

# Create a non-privileged system user for runtime application execution security
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

# Copy over system application logic structures explicitly from local directory
COPY ./app ./app
COPY ./run.py .

# Open up standard ASGI web gateway communication interface port
EXPOSE 9500

# Fire up production web runner binding to standard container pipeline networks
CMD ["python", "run.py"]