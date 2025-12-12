# 🔥 Advanced Bug Bounty MCP Server - 2025 Edition

**The most comprehensive AI-powered bug bounty hunting platform integrated with Claude via MCP protocol.**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen)](VERSION)
[![Cloud](https://img.shields.io/badge/Cloud-Ready-orange)](#-cloud-deployment)

## 🚀 What's New in 2.0.0

- ✨ **40+ Latest Security Tools** - All ProjectDiscovery tools updated to latest versions
- ☁️ **Cloud-Ready Deployment** - One-command deployment to AWS, GCP, Azure, DigitalOcean
- 🏗️ **Multi-Stage Docker Builds** - 50% smaller images, faster builds
- 🔧 **20+ New Tools** - alterx, cvemap, asnmap, interactsh, puredns, dalfox, and more
- 🎯 **Nuclei v3** - Latest templates with 10,000+ vulnerability checks
- 📊 **Enhanced MCP Integration** - Better AI-powered analysis with Claude
- 🛡️ **Advanced Security** - Latest crypto libraries and security tools
- 🚀 **Performance Boost** - Python 3.12, Go 1.24, optimized configurations

[See Full Upgrade Notes](UPGRADE_NOTES.md)

---

## 🎯 Features

### Core Capabilities
- **🤖 AI-Powered Analysis**: Integrates with Claude via MCP for intelligent vulnerability detection
- **🔍 Advanced Reconnaissance**: Multi-source subdomain enumeration, port scanning, tech detection
- **🌐 Asset Discovery**: Cloud storage buckets (S3, Azure, GCS), API endpoints, JavaScript analysis
- **🛡️ Vulnerability Scanning**: XSS, SQLi, SSRF, IDOR, XXE, CORS, and 100+ vulnerability types
- **📊 Intelligence Integration**: Shodan, VirusTotal, Censys, SecurityTrails, Hunter, GitHub
- **🔐 Infrastructure Analysis**: CDN detection, WAF identification, origin IP discovery
- **📝 Auto-Reporting**: Generates professional bug bounty reports with CVSS scoring
- **🔄 Continuous Monitoring**: Real-time asset monitoring and change detection
- **☁️ Cloud Native**: Deploy anywhere - local, AWS, GCP, Azure, DigitalOcean, Linode, Hetzner

### 🛠️ Comprehensive Tool Suite (40+ Tools)

#### Reconnaissance & Discovery
- **subfinder** - Fast passive subdomain enumeration
- **alterx** - Advanced subdomain permutation generator
- **assetfinder** - Find related domains and subdomains
- **amass** - In-depth attack surface mapping
- **asnmap** - ASN enumeration and mapping

#### Active Scanning
- **naabu** - Fast port scanner
- **httpx** - Multi-purpose HTTP toolkit
- **katana** - Next-gen web crawler
- **nuclei v3** - Fast vulnerability scanner with 10K+ templates
- **dnsx** - Fast and multi-purpose DNS toolkit

#### Web Application Testing
- **dalfox** - XSS scanner and parameter analyzer
- **ffuf** - Fast web fuzzer
- **hakrawler** - Web crawler for gathering URLs and JavaScript
- **gospider** - Fast web spider
- **gowitness** - Web screenshot utility

#### Intelligence & OSINT
- **uncover** - Query Shodan, Censys, Fofa, etc.
- **cvemap** - CVE mapping and enrichment
- **tlsx** - TLS/SSL analysis
- **chaos** - ProjectDiscovery's Chaos data client

#### Utilities
- **interactsh** - OOB interaction testing
- **notify** - Stream output to Slack, Discord, etc.
- **mapcidr** - CIDR manipulation utility
- **gf** - Wrapper for grep-like pattern matching
- **anew** - Add new lines to files
- **unfurl** - URL parser for extracting elements

---

## ☁️ Cloud Deployment

Deploy to any major cloud provider in minutes!

### Quick Deploy (Any Provider)

```bash
# One-line install
curl -fsSL https://raw.githubusercontent.com/Coding-with-Mayank/advanced-bugbounty-mcp/upgrade-2025/cloud-deploy.sh | bash
```

### Supported Providers

| Provider | Instance Type | Monthly Cost | Setup Time |
|----------|--------------|--------------|------------|
| AWS EC2 | t3.large (2 vCPU, 8GB) | ~$60 | 5 min |
| GCP Compute | n2-standard-2 | ~$50 | 5 min |
| Azure VM | Standard_D2s_v3 | ~$70 | 5 min |
| DigitalOcean | 4GB/2vCPU | $24 | 3 min |
| Linode | 4GB Dedicated | $36 | 3 min |
| Hetzner | CPX21 | €8.46 | 3 min |

[See Detailed Cloud Deployment Guide](CLOUD_DEPLOYMENT.md)

---

## 🚀 Local Installation

### Prerequisites
- Docker & Docker Compose
- 8GB+ RAM recommended
- 50GB+ disk space

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp

# Checkout latest version
git checkout upgrade-2025

# Setup environment
cp .env.example .env
nano .env  # Add your API keys

# Deploy
docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

### Connect to Claude Desktop

1. **Edit Claude Config** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "bugbounty": {
      "command": "docker",
      "args": ["exec", "-i", "bugbounty-mcp", "python", "-m", "mcp_server"]
    }
  }
}
```

2. **Restart Claude Desktop**

3. **Test**: Ask Claude "List available bug bounty tools"

---

## 📚 Available MCP Tools

### Reconnaissance
- `recon_full` - Comprehensive reconnaissance with all tools
- `subdomain_enum` - Advanced subdomain enumeration (subfinder, alterx, amass)
- `port_scan` - Fast port scanning with service detection (naabu)
- `cdn_detection` - Detect CDN providers and infrastructure

### Asset Discovery
- `cloud_enum` - Enumerate cloud storage (S3, Azure, GCS)
- `js_analysis` - Extract secrets and APIs from JavaScript
- `api_discovery` - Discover API endpoints
- `tech_detection` - Identify technologies and frameworks

### Vulnerability Scanning
- `nuclei_scan` - Run Nuclei v3 templates (10K+ checks)
- `xss_scan` - Advanced XSS detection with dalfox
- `sqli_scan` - SQL Injection detection
- `ssrf_scan` - SSRF vulnerability testing
- `vulnerability_comprehensive` - Full vulnerability assessment

### Intelligence Gathering
- `shodan_search` - Query Shodan intelligence
- `censys_search` - Search Censys datasets
- `virustotal_analyze` - Analyze with VirusTotal
- `github_dorking` - Search GitHub for secrets and leaks
- `wayback_enum` - Historical URL enumeration

### Exploitation & Validation
- `oob_testing` - Out-of-band testing with interactsh
- `exploit_chain` - Identify vulnerability chains
- `validate_finding` - Validate discovered vulnerabilities
- `generate_report` - Generate professional bug bounty reports

---

## 🎓 Usage Examples

### Example 1: Full Recon on Target
```
Claude: Run a complete reconnaissance on example.com using all available tools. Start with passive enumeration, then active scanning.
```

### Example 2: Cloud Asset Discovery
```
Claude: Check example.com for any exposed cloud storage buckets on AWS S3, Azure Blob, and Google Cloud Storage.
```

### Example 3: Vulnerability Hunt
```
Claude: I found these subdomains for example.com: [list]. Scan them for XSS, SQLi, and SSRF vulnerabilities. Prioritize by severity.
```

### Example 4: CDN Analysis
```
Claude: Analyze example.com's CDN setup. Identify the provider, check for origin IP leaks, and suggest potential bypass techniques.
```

### Example 5: API Security Testing
```
Claude: Discover all API endpoints on example.com and test them for common vulnerabilities like broken authentication and excessive data exposure.
```

### Example 6: Complete Bug Bounty Workflow
```
Claude: I want to hunt on example.com. Please:
1. Run full passive and active recon
2. Identify all subdomains and services
3. Check for cloud asset exposure
4. Scan for critical vulnerabilities
5. Test for authentication bypasses
6. Generate a report with exploitation steps
```

---

## 🔧 Configuration

### Required API Keys

```env
# Security Intelligence
SHODAN_API_KEY=your_shodan_key
VIRUSTOTAL_API_KEY=your_vt_key
CENSYS_API_KEY=your_censys_key
GITHUB_TOKEN=your_github_token

# Optional but Recommended
SECURITYTRAILS_API_KEY=your_st_key
HUNTER_API_KEY=your_hunter_key
CHAOS_API_KEY=your_chaos_key

# AI Providers (Optional)
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

### Performance Tuning

```env
# Scanning
MAX_THREADS=50
RATE_LIMIT=100
TIMEOUT=30

# Nuclei
NUCLEI_RATE_LIMIT=150
NUCLEI_BULK_SIZE=50
NUCLEI_CONCURRENCY=25

# Memory
MAX_MEMORY=4G
```

---

## 📊 Dashboard & Monitoring

Access the web dashboard at `http://localhost:8080` (or `http://your-cloud-ip:8080`)

**Features:**
- Real-time scan progress
- Vulnerability timeline and statistics
- Asset inventory and mapping
- Historical reports and findings
- API usage and rate limits
- Tool performance metrics
- Cloud deployment status

**Monitoring Stack** (Optional):
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9091`

---

## 🛠️ Useful Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose stop

# Restart services
docker-compose restart

# Update containers
docker-compose pull && docker-compose up -d

# Check health
docker-compose ps

# Run specific tool
docker exec -it bugbounty-mcp nuclei -version
docker exec -it bugbounty-mcp subfinder -version

# Update Nuclei templates
docker exec -it bugbounty-mcp nuclei -update-templates

# Clean everything
docker-compose down -v
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Claude Desktop                      │
│                   (MCP Client)                       │
└──────────────────┬──────────────────────────────────┘
                   │ MCP Protocol
                   ▼
┌─────────────────────────────────────────────────────┐
│               MCP Server (Python)                    │
│   ┌─────────────────────────────────────────────┐  │
│   │  Tool Orchestration & AI Integration       │  │
│   └─────────────────────────────────────────────┘  │
│   ┌──────────┬──────────┬──────────┬───────────┐  │
│   │  Recon   │  Scan    │  Intel   │  Exploit  │  │
│   └──────────┴──────────┴──────────┴───────────┘  │
└──────────────┬───────────────────────┬──────────────┘
               │                       │
       ┌───────┴───────┐      ┌───────┴────────┐
       │  40+ Tools    │      │   Databases    │
       │  (Docker)     │      │  (Mongo/Redis) │
       └───────────────┘      └────────────────┘
```

---

## 🐛 Troubleshooting

### Common Issues

**Container won't start:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

**Claude can't connect:**
- Check config file location
- Verify container is running: `docker ps`
- Check logs: `docker-compose logs mcp-server`

**High memory usage:**
- Reduce `MAX_THREADS` in .env
- Reduce `NUCLEI_CONCURRENCY`
- Use smaller instance type

**API errors:**
- Verify API keys in .env
- Check rate limits
- Test API keys individually

**Tools not found:**
- Rebuild containers: `docker-compose build --no-cache`
- Verify Go binaries: `docker exec -it bugbounty-mcp which nuclei`

---

## 📖 Documentation

- 📘 [Cloud Deployment Guide](CLOUD_DEPLOYMENT.md) - Deploy to any cloud provider
- 📗 [Installation Guide](INSTALLATION.md) - Detailed setup instructions  
- 📙 [Upgrade Notes](UPGRADE_NOTES.md) - What's new in v2.0
- 📕 [Project Structure](PROJECT_STRUCTURE.md) - Codebase overview
- 📔 [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- 📓 [Changelog](CHANGELOG.md) - Version history

---

## ⚠️ Legal Disclaimer

**This tool is for authorized security testing only.**

Always ensure you have:
- ✅ Written permission before testing
- ✅ Staying within defined scopes
- ✅ Following bug bounty program rules
- ✅ Compliance with local laws
- ✅ Not causing damage or unauthorized data access

**Unauthorized access to computer systems is illegal.**

---

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and commit
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

---

## 🙏 Acknowledgments

Built with insights from:
- HackerOne disclosed reports
- ProjectDiscovery tools and community
- OWASP Top 10 & API Security
- Bug Bounty community best practices
- awesome-bugbounty-tools
- ExternalAttacker-MCP inspiration

Special thanks to all contributors and testers!

---

## 📞 Support & Community

- 🐛 [GitHub Issues](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/issues)
- 💬 [GitHub Discussions](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/discussions)
- ⭐ [Star this repo](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp) if you find it useful!

---

## 🎯 Roadmap

- [ ] Kubernetes deployment manifests
- [ ] Terraform/IaC configurations
- [ ] Enhanced GUI dashboard
- [ ] AI-powered vulnerability analysis
- [ ] Integration with HackerOne/Bugcrowd
- [ ] Mobile app for monitoring
- [ ] Automated exploitation modules
- [ ] Team collaboration features

---

**Made with ❤️ for the bug bounty community**

**Version 2.0.0** | Built for 2025 | Cloud Native | AI-Powered

⭐ **Star** ⭐ **Fork** ⭐ **Contribute** ⭐
