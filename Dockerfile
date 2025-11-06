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

# Install Go tools
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest && \
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest && \
    go install -v github.com/projectdiscovery/tlsx/cmd/tlsx@latest && \
    go install -v github.com/tomnomnom/assetfinder@latest && \
    go install -v github.com/tomnomnom/waybackurls@latest && \
    go install -v github.com/tomnomnom/gf@latest && \
    go install -v github.com/tomnomnom/httprobe@latest && \
    go install -v github.com/lc/gau/v2/cmd/gau@latest && \
    go install -v github.com/hakluke/hakrawler@latest && \
    go install -v github.com/ffuf/ffuf/v2@latest && \
    go install -v github.com/projectdiscovery/chaos-client/cmd/chaos@latest && \
    go install -v github.com/projectdiscovery/uncover/cmd/uncover@latest && \
    go install -v github.com/jaeles-project/gospider@latest

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional tools
RUN gem install wpscan && \
    npm install -g retire@latest

# Download wordlists
RUN mkdir -p /app/wordlists && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt -O /app/wordlists/subdomains.txt && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O /app/wordlists/directories.txt && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -O /app/wordlists/parameters.txt && \
    wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Fuzzing/XSS/XSS-Jhaddix.txt -O /app/wordlists/xss-payloads.txt && \
    wget -q https://raw.githubusercontent.com/payloadbox/sql-injection-payload-list/master/Intruder/exploit/Auth_Bypass.txt -O /app/wordlists/sqli-payloads.txt

# Download Nuclei templates
RUN nuclei -update-templates

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