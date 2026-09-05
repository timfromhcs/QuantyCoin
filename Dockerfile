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

# Ports: P2P, RPC, Stratum V1, Stratum V2, GUI Suite
EXPOSE 19444 19445 3333 3334 8080

# Default command: Start QuantyCoin Node
ENTRYPOINT ["python", "-m", "node.daemon"]
CMD ["--port", "19444", "--rpcport", "19445"]
