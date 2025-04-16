FROM python:3.13-slim as builder

WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install uv && \
    uv pip install -e .

FROM python:3.13-slim

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .

ENV PATH="/opt/venv/bin:$PATH"

CMD ["python", "main.py"]
