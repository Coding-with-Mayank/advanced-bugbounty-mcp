# 🔥 Advanced Bug Bounty MCP Server

**The most comprehensive AI-powered bug bounty hunting platform integrated with Claude via MCP protocol.**

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)

## 🎯 Features

### Core Capabilities
- **🤖 AI-Powered Analysis**: Integrates with Claude through MCP for intelligent vulnerability detection
- **🔍 Advanced Reconnaissance**: Multi-source subdomain enumeration, port scanning, technology detection
- **🌐 Asset Discovery**: Cloud storage buckets (S3, Azure, GCS), API endpoints, JavaScript analysis
- **🛡️ Vulnerability Scanning**: XSS, SQLi, SSRF, IDOR, XXE, CORS, and 50+ vulnerability types
- **📊 Intelligence Integration**: Shodan, VirusTotal, Censys, SecurityTrails, Hunter, GitHub
- **🔐 CDN Detection**: Identify CDN providers, find origin IPs, and detect protection mechanisms
- **📝 Auto-Reporting**: Generates professional bug bounty reports with CVSS scoring
- **🔄 Continuous Monitoring**: Real-time asset monitoring and change detection
- **🐋 Production Ready**: Docker & Docker Compose with health checks and logging

### Advanced Features
- **ML-Based Vulnerability Prediction**: Learns from disclosed HackerOne reports
- **Exploit Chain Detection**: Identifies vulnerability combinations for higher impact
- **Rate Limiting & Stealth**: Respects rate limits, randomized user agents, proxy support
- **Multi-Threading**: Parallel scanning with configurable workers
- **Scope Validation**: Auto-validates targets against bug bounty program scopes
- **Nuclei Integration**: 5000+ community templates for vulnerability detection
- **Custom Payloads**: Adaptive payloads based on target technology stack

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- WSL2 (for Windows users)
- 8GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp

# Create .env file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Run automated setup
chmod +x setup.sh
./setup.sh

# Or use Make
make install
```

### Connecting to Claude Desktop

1. **Add to Claude Desktop Config** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "bugbounty": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "bugbounty-mcp",
        "python",
        "-m",
        "mcp_server"
      ]
    }
  }
}
```

2. **Restart Claude Desktop**

3. **Test Connection**:
   - Open Claude and ask: "List available bug bounty tools"
   - You should see all MCP tools available

## 📚 Available MCP Tools

### Reconnaissance
- `recon_full` - Comprehensive reconnaissance
- `subdomain_enum` - Advanced subdomain enumeration
- `port_scan` - Fast port scanning with service detection
- `cdn_detection` - **NEW!** Detect CDN providers and analyze infrastructure

### Asset Discovery
- `cloud_enum` - Enumerate cloud storage buckets
- `js_analysis` - Extract secrets from JavaScript
- `api_discovery` - Discover API endpoints

### Vulnerability Scanning
- `scan_vulnerabilities` - Comprehensive vulnerability scanning
- `nuclei_scan` - Run Nuclei templates
- `xss_scan` - Advanced XSS scanning
- `sqli_scan` - SQL Injection detection

### Intelligence Gathering
- `shodan_search` - Query Shodan
- `virustotal_analyze` - Analyze with VirusTotal
- `censys_search` - Search Censys (now with simplified API key)
- `github_dorking` - Search GitHub for secrets

### Exploitation & Reporting
- `exploit_chain` - Identify exploit chains
- `validate_finding` - Validate vulnerabilities
- `generate_report` - Generate professional reports

## 🎓 Usage Examples

### Example 1: Basic Recon
```
I want to start bug bounty hunting on example.com. Run a full passive reconnaissance.
```

### Example 2: CDN Detection (NEW!)
```
Check if example.com uses a CDN and identify potential bypass techniques.
```

### Example 3: Vulnerability Hunt
```
I found subdomains for example.com. Scan them for XSS and SQL injection vulnerabilities.
```

### Example 4: Cloud Enumeration
```
Check if example.com has any exposed AWS S3 buckets or Azure containers.
```

### Example 5: Intelligence Gathering
```
Search Shodan for all services related to example.com and check for known vulnerabilities.
```

### Example 6: Complete Workflow
```
1. Run full recon on example.com
2. Check for CDN usage and identify infrastructure
3. Scan all found assets for vulnerabilities
4. Validate findings
5. Generate a professional report for the high-severity issues
```

## 🔧 Configuration

### Required API Keys (.env)

**⚠️ IMPORTANT: Censys API has changed!**

Censys now uses a **single API key** instead of separate ID and Secret:

```env
SHODAN_API_KEY=your_shodan_key
VIRUSTOTAL_API_KEY=your_virustotal_key
CENSYS_API_KEY=your_censys_api_key          # NEW FORMAT - single key only!
GITHUB_TOKEN=your_github_token
SECURITYTRAILS_API_KEY=your_securitytrails_key
HUNTER_API_KEY=your_hunter_key
```

**Old format (no longer valid):**
```env
CENSYS_API_ID=your_censys_id                # DEPRECATED
CENSYS_API_SECRET=your_censys_secret        # DEPRECATED
```

Get your Censys API key at: https://search.censys.io/account/api

### Optional AI Providers

```env
GROQ_API_KEY=your_groq_key
OPENAI_API_KEY=your_openai_key
```

## 🆕 What's New

### Version 2.1.0 (Latest)
- ✨ **CDN Detection Tool**: Identify CDN providers (Cloudflare, Akamai, Fastly, etc.)
  - DNS CNAME analysis
  - HTTP header fingerprinting
  - IP range matching
  - Bug bounty-specific insights for WAF bypass and origin IP discovery
- 🔧 **Updated Censys API**: Now uses single API key format (breaking change)
- 📚 Enhanced documentation with CDN detection examples
- 🛡️ Improved infrastructure analysis capabilities

### CDN Detection Features
The new `cdn_detection` tool helps identify:
- CDN provider (Cloudflare, Akamai, Fastly, CloudFront, etc.)
- Protection mechanisms in place
- Potential origin IP leakage
- Next steps for bug bounty hunters
- WAF bypass techniques

This is crucial for bug bounty hunting because:
- Helps understand the security posture
- Identifies potential CDN misconfigurations
- Reveals origin IPs for direct testing
- Assists in cache poisoning detection
- Guides WAF bypass strategies

## 📊 Dashboard & Monitoring

Access the web dashboard at `http://localhost:8080`

**Features:**
- Real-time scan progress
- Vulnerability timeline
- Asset inventory
- Historical reports
- API usage statistics
- CDN detection results

## 🛠️ Useful Commands

```bash
# Start services
make start

# View logs
make logs

# Stop services
make stop

# Run tests
make test

# Update templates
make nuclei-update

# Check health
make health

# Clean everything
make clean
```

## 🐛 Troubleshooting

See [INSTALLATION.md](INSTALLATION.md) for detailed troubleshooting steps.

Common issues:
- Container won't start: `make rebuild`
- Claude can't connect: Check config file location
- High memory usage: Reduce `MAX_THREADS` in .env
- API errors: Verify API keys in .env (especially new Censys format!)
- CDN detection failing: Ensure `dnspython` and `requests` are installed

## 📖 Documentation

- [Installation Guide](INSTALLATION.md)
- [Project Structure](PROJECT_STRUCTURE.md)
- [API Documentation](docs/API.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## ⚠️ Legal Disclaimer

This tool is for authorized security testing only. Always:
- Get written permission before testing
- Stay within defined scopes
- Follow bug bounty program rules
- Comply with local laws
- Don't cause damage or access data unnecessarily

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

```bash
# Fork the repository
# Create feature branch
git checkout -b feature/amazing-feature

# Commit changes
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

Built with insights from:
- HackerOne disclosed reports
- OWASP Top 10
- Bug Bounty community
- awesome-bugbounty-tools
- ProjectDiscovery tools
- [ExternalAttacker-MCP](https://github.com/MorDavid/ExternalAttacker-MCP) for CDN detection inspiration

## 📞 Support

- Issues: [GitHub Issues](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/issues)
- Discussions: [GitHub Discussions](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/discussions)

---

**Made with ❤️ for the bug bounty community**

⭐ Star this repo if you find it useful!