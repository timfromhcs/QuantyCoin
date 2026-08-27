# QuantyCoin Production Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy codebase
COPY . /app/

# Install python dependencies
RUN pip install --no-cache-dir qrcode

# Ports: P2P, RPC, Stratum, GUI Suite
EXPOSE 19888 19889 3333 8080

# Default command: Start QuantyCoin Node
ENTRYPOINT ["python", "-m", "node.daemon"]
CMD ["--port", "19888", "--rpcport", "19889"]
