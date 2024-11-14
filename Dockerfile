FROM python:3.8-slim

WORKDIR /app
COPY pyproject.toml pdm.lock ./
RUN pip install pdm && pdm install --prod

COPY src/ ./src/

CMD ["pdm", "run", "python", "-m", "src.main"]