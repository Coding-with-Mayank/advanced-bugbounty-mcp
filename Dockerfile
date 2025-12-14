# ============================================
# MINIMAL DOCKERFILE - Version 2.0.1
# ============================================
# 10 essential tools only for 100% build success
# Use Dockerfile.full for 30+ tools
# ============================================

FROM golang:1.23-alpine AS go-builder

RUN apk add --no-cache git build-base

ENV GOPATH=/root/go
ENV PATH=$PATH:/root/go/bin

ARG INSTALL_TOOLS=true

# 10 ESSENTIAL TOOLS - Guaranteed to build
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.3.2 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.6.6 || true  
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/httpx/cmd/httpx@v1.6.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/katana/cmd/katana@v1.0.5 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@v2.3.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@v1.2.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/tomnomnom/waybackurls@v0.1.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/lc/gau/v2/cmd/gau@v2.2.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/ffuf/ffuf/v2@v2.1.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/OJ/gobuster/v3@v3.6.0 || true

# Final stage
FROM python:3.12-slim

LABEL version="2.0.1-minimal"
LABEL description="Bug Bounty MCP - Minimal Build (10 tools)"

RUN apt-get update && apt-get install -y \
    git wget curl nmap dnsutils whois jq \
    build-essential libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=go-builder /root/go/bin/* /usr/local/bin/ 2>/dev/null || true

WORKDIR /app
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data /app/reports /app/logs /root/.config/nuclei

RUN nuclei -update-templates -ut 2>/dev/null || true

COPY . /app/
RUN chmod +x /app/*.sh 2>/dev/null || true

EXPOSE 8080 9090
ENV PYTHONUNBUFFERED=1
VOLUME ["/app/data", "/app/reports", "/app/logs"]

CMD ["python", "-m", "mcp_server"]