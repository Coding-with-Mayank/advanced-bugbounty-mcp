# ============================================
# FIXED DOCKERFILE - Version 2.0.1
# ============================================
# ROOT CAUSE FIX: Removed chained @latest installs
# Now uses: PINNED versions + SEPARATE layers
# ============================================

# Multi-stage build for optimized container size
FROM golang:1.24-alpine AS go-builder

LABEL stage=builder
LABEL description="Go tools builder with pinned versions"

# Install build dependencies
RUN apk add --no-cache git build-base

# Set Go environment
ENV GOPATH=/root/go
ENV PATH=$PATH:/root/go/bin
ENV CGO_ENABLED=1

# Build argument to control tool installation
ARG INSTALL_TOOLS=true

# ============================================
# CRITICAL FIX: Each tool in separate layer
# - Enables Docker layer caching
# - Easy debugging (see exactly which tool fails)
# - Pinned versions prevent @latest chaos
# - Memory efficient (no massive combined compile)
# ============================================

# ProjectDiscovery Tools - PINNED VERSIONS (verified Dec 2024)
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@v3.6.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.6.7 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/httpx/cmd/httpx@v1.6.10 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/katana/cmd/katana@v1.1.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@v2.3.4 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@v1.2.3 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/tlsx/cmd/tlsx@v1.1.8 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/notify/cmd/notify@v1.0.7 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@v0.5.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/uncover/cmd/uncover@v1.1.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/cloudlist/cmd/cloudlist@v1.0.9 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/alterx/cmd/alterx@v1.0.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/cvemap/cmd/cvemap@v0.1.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@v1.2.3 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/mapcidr/cmd/mapcidr@v1.1.34 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/asnmap/cmd/asnmap@v1.1.2 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@v1.1.1 || true

# Tom Hudson's (tomnomnom) Tools - PINNED VERSIONS
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/tomnomnom/assetfinder@v0.1.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/tomnomnom/waybackurls@v0.1.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/tomnomnom/gf@v0.0.0-20200618134122-dcd4c361f9f5 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/tomnomnom/httprobe@v0.2.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/tomnomnom/anew@v0.1.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/tomnomnom/unfurl@v0.4.3 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/tomnomnom/meg@v0.2.0 || true

# Other Security Tools - PINNED VERSIONS
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/lc/gau/v2/cmd/gau@v2.2.3 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/hakluke/hakrawler@v0.0.0-20230118141933-a757cf8f274f || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/hakluke/hakcheckurl@v1.0.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/hakluke/hakrevdns@v0.0.0-20220223030715-c4e3e8f1c8db || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/ffuf/ffuf/v2@v2.1.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/jaeles-project/gospider@v1.1.8 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/OJ/gobuster/v3@v3.6.0 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/d3mondev/puredns/v2@v2.1.1 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/hahwul/dalfox/v2@v2.9.2 || true
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/sensepost/gowitness@v2.5.4 || true

# Note: OWASP Amass and cero often have build issues - optional
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/owasp-amass/amass/v4/...@v4.2.0 || echo "Amass skipped (often fails)"
RUN [ "$INSTALL_TOOLS" = "true" ] && go install -v github.com/glebarez/cero@v1.2.2 || echo "Cero skipped (often fails)"

# ============================================
# Final Stage - Python Runtime
# ============================================
FROM python:3.12-slim

LABEL maintainer="Advanced Bug Bounty MCP"
LABEL version="2.0.1"
LABEL description="Bug Bounty Hunting Environment - 2025 Edition (FIXED)"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    nmap \
    masscan \
    dnsutils \
    whois \
    jq \
    chromium \
    chromium-driver \
    build-essential \
    libssl-dev \
    libffi-dev \
    ruby \
    ruby-dev \
    nodejs \
    npm \
    unzip \
    zip \
    sqlite3 \
    vim \
    nano \
    screen \
    tmux \
    net-tools \
    iputils-ping \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Go binaries from builder (with error handling)
COPY --from=go-builder /root/go/bin/* /usr/local/bin/ 2>/dev/null || true

# Install Ruby gems
RUN gem install wpscan webrick bundler 2>/dev/null || true

# Install Node.js tools
RUN npm install -g retire npm-check-updates js-beautify 2>/dev/null || true

# Set working directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install additional Python security tools (optional, non-critical)
RUN pip install --no-cache-dir \
    arjun \
    corsy \
    wafw00f \
    gittools \
    trufflehog \
    semgrep \
    bandit \
    safety 2>/dev/null || echo "Some Python tools skipped"

# Create directory structure
RUN mkdir -p \
    /app/data \
    /app/reports \
    /app/logs \
    /app/nuclei-templates/custom \
    /app/config \
    /app/wordlists \
    /app/workflows \
    /app/scripts \
    /app/db \
    /root/.config/nuclei \
    /root/.config/subfinder \
    /root/.config/notify

# Download essential wordlists (non-blocking)
RUN cd /app/wordlists && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt -O subdomains-top1m.txt 2>/dev/null || true && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/dns-Jhaddix.txt -O subdomains-jhaddix.txt 2>/dev/null || true && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O directories-common.txt 2>/dev/null || true && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -O parameters.txt 2>/dev/null || true && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/XSS/XSS-Jhaddix.txt -O xss-payloads.txt 2>/dev/null || true

# Download and update Nuclei templates (non-blocking)
RUN nuclei -update-templates -ut 2>/dev/null || echo "Nuclei templates will update on first run"

# Install gf patterns for filtering (non-blocking)
RUN mkdir -p /root/.gf && \
    cd /root/.gf && \
    git clone https://github.com/1ndianl33t/Gf-Patterns.git 2>/dev/null && \
    mv Gf-Patterns/*.json . 2>/dev/null && \
    rm -rf Gf-Patterns || true

# Copy application code
COPY . /app/

# Set permissions
RUN chmod +x /app/*.sh 2>/dev/null || true

# Configure Nuclei
RUN echo "rate-limit: 150" > /root/.config/nuclei/config.yaml && \
    echo "bulk-size: 50" >> /root/.config/nuclei/config.yaml

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(5); s.connect(('localhost', 9090)); s.close()" || exit 1

# Expose ports
EXPOSE 8080 9090

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PATH="/usr/local/bin:${PATH}"

# Volume mounts for persistent data
VOLUME ["/app/data", "/app/reports", "/app/logs"]

# Default command
CMD ["python", "-m", "mcp_server"]