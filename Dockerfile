FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY mate ./mate
COPY assets ./assets

ENV MATE_HOST=0.0.0.0
ENV MATE_PORT=8080
ENV MATE_DATA_DIR=/app/data
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python", "-m", "mate", "serve"]
