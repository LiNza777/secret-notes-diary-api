FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app

RUN useradd -m appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=appuser:appuser . .

USER appuser

CMD alembic upgrade head && exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}