# syntax=docker/dockerfile:1
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app
COPY run_uvicorn.py ./

RUN pip install --upgrade pip && pip install .

# Railway sets PORT at runtime. Use Python (not shell) so PORT is never passed as the literal "$PORT".
EXPOSE 8000

CMD ["python", "run_uvicorn.py"]
