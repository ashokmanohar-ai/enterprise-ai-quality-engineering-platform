FROM python:3.12.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN useradd --create-home --uid 10001 aiq
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --upgrade pip && python -m pip install .
COPY config ./config
COPY datasets ./datasets
COPY prompts ./prompts
COPY knowledge_base ./knowledge_base
USER aiq
ENTRYPOINT ["python", "-m", "ai_quality.cli"]
CMD ["validate"]
