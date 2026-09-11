# Celebi Server Mode — FastAPI proxy + LiteLLM (no GUI)
FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files first for caching
COPY api/pyproject.toml api/uv.lock ./

# Install dependencies
RUN uv sync --no-dev

# Copy application code
COPY api/ ./

# Generate litellm config from env vars
RUN echo 'model_list:' > app/config/litellm-config.yaml && \
    echo '  - model_name: ${CELEBI_MODEL:-gemini-3.5-flash-lite}' >> app/config/litellm-config.yaml && \
    echo '    litellm_params:' >> app/config/litellm-config.yaml && \
    echo '      model: ${CELEBI_LITELLM_MODEL:-gemini/gemini-3.5-flash-lite}' >> app/config/litellm-config.yaml && \
    echo '      api_key: os.environ/${CELEBI_ENV_KEY:-GEMINI_KEY}' >> app/config/litellm-config.yaml

EXPOSE 8000 4000

# Default: run both litellm and fastapi
CMD ["sh", "-c", "\
  python -m litellm --config app/config/litellm-config.yaml --port ${LITELLM_PORT:-4000} & \
  python -m uvicorn main:app --host 0.0.0.0 --port ${PROXY_PORT:-8000} \
"]
