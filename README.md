# 🔥 Advanced Bug Bounty MCP Server - 2025 Edition

**The most comprehensive AI-powered bug bounty hunting platform integrated with Claude via MCP protocol.**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-2.0.1-brightgreen)](VERSION)
[![Cloud](https://img.shields.io/badge/Cloud-Ready-orange)](#-cloud-deployment)

## 🚀 What's New in 2.0.1

- 🔥 **CRITICAL FIX** - Docker build failures resolved (100% success rate)
- ✅ **Minimal build** - Only essential 10 tools for guaranteed success
- 📌 **Pinned versions** - All tools use verified stable versions
- ⚡ **Fast builds** - 3-5 minutes, 1-2 minutes cached
- 🛠️ **10 core tools** - nuclei, subfinder, httpx, katana, naabu, dnsx, waybackurls, gau, ffuf, gobuster
- 📚 **Complete docs** - DOCKERFILE_FIX.md explains everything
- 🔧 **Optional full build** - Dockerfile.full has 30+ tools for advanced users

[See DOCKERFILE_FIX.md](DOCKERFILE_FIX.md) | [Full Upgrade Notes](UPGRADE_NOTES.md)

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
- **☁️ Cloud Native**: Deploy anywhere - local, AWS, GCP, Azure, DigitalOcean

### 🛠️ Essential Tool Suite (10 Core Tools)

**Minimal Build (Default - Guaranteed to Work):**
- **nuclei v3.6.0** - Fast vulnerability scanner with 10K+ templates
- **subfinder v2.6.7** - Passive subdomain enumeration
- **httpx v1.6.10** - HTTP toolkit
- **katana v1.1.1** - Web crawler
- **naabu v2.3.4** - Port scanner
- **dnsx v1.2.3** - DNS toolkit
- **waybackurls v0.1.0** - Historical URL enumeration
- **gau v2.2.3** - URL fetcher
- **ffuf v2.1.0** - Web fuzzer
- **gobuster v3.6.0** - Directory/DNS fuzzer

**Full Build (Optional - Use Dockerfile.full):**
- All 30+ tools including alterx, asnmap, dalfox, puredns, and more

---

## ☁️ Cloud Deployment

Deploy to any cloud provider in minutes!

### Quick Deploy

```bash
# One-line install
curl -fsSL https://raw.githubusercontent.com/Coding-with-Mayank/advanced-bugbounty-mcp/main/cloud-deploy.sh | bash
```

### Supported Providers

| Provider | Instance | Monthly Cost | Setup Time |
|----------|----------|--------------|------------|
| DigitalOcean | 4GB/2vCPU | $24 | 3 min |
| AWS EC2 | t3.large | ~$60 | 5 min |
| GCP | n2-standard-2 | ~$50 | 5 min |

[See Full Cloud Guide](CLOUD_DEPLOYMENT.md)

---

## 🚀 Quick Start

```bash
# Clone
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp

# Setup
cp .env.example .env
nano .env  # Add API keys

# Build (minimal - fast and reliable)
docker-compose build

# Or use full build (30+ tools)
docker-compose -f docker-compose.full.yml build

# Start
docker-compose up -d
```

### Connect to Claude

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

Restart Claude Desktop and test: "List bug bounty tools"

---

## 📚 Available MCP Tools

- `recon_full` - Full reconnaissance
- `subdomain_enum` - Subdomain enumeration
- `port_scan` - Port scanning
- `cdn_detection` - CDN detection
- `nuclei_scan` - Vulnerability scanning
- `xss_scan` - XSS detection
- `sqli_scan` - SQL injection testing
- And more...

---

## 🔧 Configuration

### Required API Keys

```env
SHODAN_API_KEY=your_key
VIRUSTOTAL_API_KEY=your_key
CENSYS_API_KEY=your_key
GITHUB_TOKEN=your_token
```

---

## 🐛 Troubleshooting

**Build fails?**
```bash
# Use minimal build (default)
docker-compose build

# Or build without tools first
docker-compose build --build-arg INSTALL_TOOLS=false
```

**Still having issues?** See [DOCKERFILE_FIX.md](DOCKERFILE_FIX.md)

---

## 📖 Documentation

- [Dockerfile Fix](DOCKERFILE_FIX.md) - Understanding the fix
- [Cloud Deployment](CLOUD_DEPLOYMENT.md) - Deploy to cloud
- [Installation Guide](INSTALLATION.md) - Detailed setup
- [Upgrade Notes](UPGRADE_NOTES.md) - What's new

---

## ⚠️ Legal Disclaimer

**Authorized security testing only.**
- ✅ Get written permission
- ✅ Stay within scope
- ✅ Follow program rules
- ✅ Comply with laws

---

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- ProjectDiscovery tools
- Bug bounty community
- OWASP

---

## 📞 Support

- 🐛 [GitHub Issues](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/issues)
- ⭐ [Star this repo](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp)

---

**Version 2.0.1** | Built for 2025 | Cloud Native | AI-Powered | ✅ Production Ready

⭐ **Star** ⭐ **Fork** ⭐ **Contribute** ⭐