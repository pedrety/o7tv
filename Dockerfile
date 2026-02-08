FROM python:3.12-slim
WORKDIR /app
EXPOSE 8000

COPY pyproject.toml ./

ENV PYTHONPATH="/app/src"

RUN pip install --no-cache-dir \
    uvicorn \
    fastapi \
    aiohttp \
    jinja2 \
    python-multipart \
    ffmpeg-python \
    requests

RUN apt-get update && apt-get install -y ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]