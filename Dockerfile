FROM python:3.11-slim

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
    golang-go \
    ruby \
    ruby-dev \
    nodejs \
    npm \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Set Go environment
ENV GOPATH=/root/go
ENV PATH=$PATH:/root/go/bin:/usr/local/go/bin

# Install Go tools (with error handling)
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest || true && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest || true && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest || true && \
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest || true && \
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest || true && \
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest || true && \
    go install -v github.com/projectdiscovery/tlsx/cmd/tlsx@latest || true && \
    go install -v github.com/tomnomnom/assetfinder@latest || true && \
    go install -v github.com/tomnomnom/waybackurls@latest || true && \
    go install -v github.com/tomnomnom/gf@latest || true && \
    go install -v github.com/tomnomnom/httprobe@latest || true && \
    go install -v github.com/lc/gau/v2/cmd/gau@latest || true && \
    go install -v github.com/hakluke/hakrawler@latest || true && \
    go install -v github.com/ffuf/ffuf/v2@latest || true && \
    go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest || true && \
    go install -v github.com/projectdiscovery/uncover/cmd/uncover@latest || true && \
    go install -v github.com/jaeles-project/gospider@latest || true

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .

# Upgrade pip and install dependencies with better error handling
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt || \
    (echo "Some packages failed to install, continuing with available packages..." && exit 0)

# Install additional tools (optional)
RUN gem install wpscan || true && \
    npm install -g retire@latest || true

# Download wordlists
RUN mkdir -p /app/wordlists && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt -O /app/wordlists/subdomains.txt || true && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O /app/wordlists/directories.txt || true && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -O /app/wordlists/parameters.txt || true && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/XSS/XSS-Jhaddix.txt -O /app/wordlists/xss-payloads.txt || true && \
    wget -q https://raw.githubusercontent.com/payloadbox/sql-injection-payload-list/master/Intruder/exploit/Auth_Bypass.txt -O /app/wordlists/sqli-payloads.txt || true

# Download Nuclei templates (if nuclei installed)
RUN nuclei -update-templates || echo "Nuclei not available, skipping template update"

# Create necessary directories
RUN mkdir -p /app/data /app/reports /app/logs /app/nuclei-templates/custom /app/config

# Copy application code
COPY . /app/

# Set permissions
RUN chmod +x /app/*.sh || true

# Expose ports
EXPOSE 8080 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 9090), timeout=5)" || exit 1

# Run the MCP server
CMD ["python", "-m", "mcp_server"]