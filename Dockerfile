# ═══════════════════════════════════════════════════════════════
#  Bug Bounty MCP Server - Dockerfile
#  Multi-stage: Go tools → Python runtime
#  Compatible with Claude Desktop, Claude CLI, Gemini CLI
# ═══════════════════════════════════════════════════════════════

# ── Stage 1: Build all Go-based security tools ──────────────────
FROM golang:1.23-alpine AS go-builder

RUN apk add --no-cache git build-base ca-certificates libpcap-dev

ENV GOPATH=/root/go
ENV PATH=$PATH:/root/go/bin
ENV CGO_ENABLED=1

WORKDIR /build

# Install each tool as a separate layer for better caching
# If one fails it logs a warning and continues — build never breaks
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.6.6    2>&1 || echo "WARN: subfinder install failed"
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@v1.6.10              2>&1 || echo "WARN: httpx install failed"
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.3.9          2>&1 || echo "WARN: nuclei install failed"
RUN go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@v2.3.3            2>&1 || echo "WARN: naabu install failed"
RUN go install -v github.com/projectdiscovery/katana/cmd/katana@v1.1.2             2>&1 || echo "WARN: katana install failed"
RUN go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@v1.2.2                 2>&1 || echo "WARN: dnsx install failed"
RUN go install -v github.com/tomnomnom/waybackurls@v0.1.0                          2>&1 || echo "WARN: waybackurls install failed"
RUN go install -v github.com/lc/gau/v2/cmd/gau@v2.2.3                              2>&1 || echo "WARN: gau install failed"
RUN go install -v github.com/ffuf/ffuf/v2@v2.1.0                                   2>&1 || echo "WARN: ffuf install failed"
RUN go install -v github.com/OJ/gobuster/v3@v3.6.0                                 2>&1 || echo "WARN: gobuster install failed"
RUN go install -v github.com/sensepost/gowitness@v2.5.1                            2>&1 || echo "WARN: gowitness install failed"
RUN go install -v github.com/tomnomnom/anew@v0.1.1                                 2>&1 || echo "WARN: anew install failed"
RUN go install -v github.com/tomnomnom/httprobe@v0.2.0                             2>&1 || echo "WARN: httprobe install failed"
RUN go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest 2>&1 || echo "WARN: interactsh install failed"

# ── Stage 2: Python runtime ──────────────────────────────────────
FROM python:3.12-slim

LABEL version="3.0.0"
LABEL description="Bug Bounty MCP Server — Works with Claude Desktop, Claude CLI, Gemini CLI"
LABEL maintainer="Coding-with-Mayank"

# System packages: nmap, whois, dnsutils, jq, chromium (for screenshots)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget curl nmap dnsutils whois jq \
    build-essential libssl-dev libffi-dev \
    chromium chromium-driver \
    libpcap-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy all Go binaries
COPY --from=go-builder /root/go/bin/ /usr/local/bin/

# Set Chrome binary for gowitness / httpx screenshots
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage"

WORKDIR /app

# Install Python dependencies first (cached if requirements.txt unchanged)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data /app/reports /app/logs /app/screenshots \
             /root/.config/nuclei /root/.config/subfinder \
             /root/.config/gowitness

# Update Nuclei templates (graceful failure if no internet)
RUN nuclei -update-templates 2>/dev/null || echo "Nuclei template update skipped"

# Copy application code
COPY . /app/

RUN chmod +x /app/setup.sh 2>/dev/null || true

# Volumes for persistent data
VOLUME ["/app/data", "/app/reports", "/app/logs", "/app/screenshots"]

# MCP server runs on stdio — no port needed for MCP protocol
# Port 8080 = optional REST API / web dashboard
EXPOSE 8080

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default: run MCP server (Claude/Gemini connects via docker exec)
CMD ["python", "-m", "mcp_server"]
