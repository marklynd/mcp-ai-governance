# syntax=docker/dockerfile:1
FROM python:3.12-slim AS build

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src

RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim

LABEL org.opencontainers.image.title="mcp-ai-governance" \
      org.opencontainers.image.description="MCP server exposing AI governance and compliance mapping as callable tools." \
      org.opencontainers.image.source="https://github.com/marklynd/mcp-ai-governance" \
      org.opencontainers.image.licenses="MIT"

COPY --from=build /install /usr/local

# Run as a non-root user. The server speaks MCP over stdio.
RUN useradd --create-home --uid 10001 mcp
USER mcp
WORKDIR /home/mcp

ENTRYPOINT ["mcp-ai-governance"]
