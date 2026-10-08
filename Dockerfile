# Production Dockerfile for Rough Set Clinical Diagnostic Support System Backend
FROM python:3.11-slim

WORKDIR /app

# Set environment variables for production execution
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app/backend \
    PORT=8000 \
    HOST=0.0.0.0

# Install production dependencies
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy backend application source and precomputed research artifacts
COPY backend /app/backend
COPY data/.gitkeep /app/data/.gitkeep

# Expose container application port
EXPOSE 8000

# Container healthcheck querying production /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

# Launch production server binding to 0.0.0.0
CMD ["python", "-m", "uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
