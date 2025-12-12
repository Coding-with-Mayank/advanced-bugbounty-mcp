# Multi-stage build for optimized container size
FROM golang:1.24-alpine AS go-builder

# Install build dependencies
RUN apk add --no-cache git build-base

# Set Go environment
ENV GOPATH=/root/go
ENV PATH=$PATH:/root/go/bin

# Install all Go-based security tools with latest versions
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest && \
    go install -v github.com/projectdiscovery/tlsx/cmd/tlsx@latest && \
    go install -v github.com/projectdiscovery/notify/cmd/notify@latest && \
    go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest && \
    go install -v github.com/projectdiscovery/uncover/cmd/uncover@latest && \
    go install -v github.com/projectdiscovery/cloudlist/cmd/cloudlist@latest && \
    go install -v github.com/projectdiscovery/alterx/cmd/alterx@latest && \
    go install -v github.com/projectdiscovery/cvemap/cmd/cvemap@latest && \
    go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest && \
    go install -v github.com/projectdiscovery/mapcidr/cmd/mapcidr@latest && \
    go install -v github.com/projectdiscovery/asnmap/cmd/asnmap@latest && \
    go install -v github.com/tomnomnom/assetfinder@latest && \
    go install -v github.com/tomnomnom/waybackurls@latest && \
    go install -v github.com/tomnomnom/gf@latest && \
    go install -v github.com/tomnomnom/httprobe@latest && \
    go install -v github.com/tomnomnom/anew@latest && \
    go install -v github.com/tomnomnom/unfurl@latest && \
    go install -v github.com/tomnomnom/meg@latest && \
    go install -v github.com/lc/gau/v2/cmd/gau@latest && \
    go install -v github.com/hakluke/hakrawler@latest && \
    go install -v github.com/hakluke/hakcheckurl@latest && \
    go install -v github.com/hakluke/hakrevdns@latest && \
    go install -v github.com/ffuf/ffuf/v2@latest && \
    go install -v github.com/jaeles-project/gospider@latest && \
    go install -v github.com/OWASP/Amass/v4/...@latest && \
    go install -v github.com/OJ/gobuster/v3@latest && \
    go install -v github.com/d3mondev/puredns/v2@latest && \
    go install -v github.com/hahwul/dalfox/v2@latest && \
    go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest && \
    go install -v github.com/sensepost/gowitness@latest && \
    go install -v github.com/glebarez/cero@latest

# Final stage
FROM python:3.12-slim

LABEL maintainer="Advanced Bug Bounty MCP"
LABEL version="2.0.0"
LABEL description="Comprehensive Bug Bounty Hunting Environment - 2025 Edition"

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
    yq \
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
    postgresql-client \
    redis-tools \
    vim \
    nano \
    screen \
    tmux \
    net-tools \
    iputils-ping \
    ca-certificates \
    gnupg \
    lsb-release \
    && rm -rf /var/lib/apt/lists/*

# Copy Go binaries from builder
COPY --from=go-builder /root/go/bin/* /usr/local/bin/

# Install Ruby gems
RUN gem install wpscan webrick && \
    gem install bundler

# Install Node.js tools
RUN npm install -g retire@latest \
    npm-check-updates \
    snyk \
    @apideck/portman \
    js-beautify

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .

# Upgrade pip and install Python packages
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# Install additional Python security tools
RUN pip install --no-cache-dir \
    arjun \
    corsy \
    wafw00f \
    gittools \
    trufflehog \
    cloudsplaining \
    prowler \
    checkov \
    semgrep \
    bandit \
    safety

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

# Download essential wordlists
RUN cd /app/wordlists && \
    # Subdomain wordlists
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt -O subdomains-top1m.txt && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/dns-Jhaddix.txt -O subdomains-jhaddix.txt && \
    # Directory wordlists
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O directories-common.txt && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/raft-large-directories.txt -O directories-raft.txt && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/big.txt -O directories-big.txt && \
    # Parameter wordlists
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -O parameters.txt && \
    # Payload wordlists
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/XSS/XSS-Jhaddix.txt -O xss-payloads.txt && \
    wget -q https://raw.githubusercontent.com/payloadbox/sql-injection-payload-list/master/Intruder/exploit/Auth_Bypass.txt -O sqli-payloads.txt && \
    wget -q https://raw.githubusercontent.com/payloadbox/open-redirect-payload-list/master/Open-Redirect-payloads.txt -O open-redirect-payloads.txt && \
    wget -q https://raw.githubusercontent.com/payloadbox/command-injection-payload-list/master/README.md -O command-injection-payloads.txt || true

# Download and update Nuclei templates
RUN nuclei -update-templates -ut || echo "Nuclei template update will continue in background"

# Install gf patterns for filtering
RUN mkdir -p /root/.gf && \
    cd /root/.gf && \
    git clone https://github.com/1ndianl33t/Gf-Patterns.git && \
    mv Gf-Patterns/*.json . && \
    rm -rf Gf-Patterns && \
    git clone https://github.com/tomnomnom/gf.git /tmp/gf && \
    cp /tmp/gf/examples/*.json . || true && \
    rm -rf /tmp/gf

# Copy application code
COPY . /app/

# Set permissions
RUN chmod +x /app/*.sh || true && \
    chmod +x /app/scripts/*.sh || true

# Configure Nuclei rate limiting and other settings
RUN echo "rate-limit: 150" > /root/.config/nuclei/config.yaml && \
    echo "templates-directory: /root/nuclei-templates" >> /root/.config/nuclei/config.yaml && \
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
