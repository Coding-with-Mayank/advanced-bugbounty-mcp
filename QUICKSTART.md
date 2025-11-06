# Quick Start Guide

Get started with Advanced Bug Bounty MCP Server in 5 minutes!

## 🚀 One-Line Installation

```bash
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git && cd advanced-bugbounty-mcp && chmod +x setup.sh && ./setup.sh
```

## 📋 Prerequisites Checklist

- [ ] Docker Desktop installed
- [ ] WSL2 enabled (Windows users)
- [ ] 8GB+ RAM available
- [ ] API keys ready (see below)

## 🔑 Get Your API Keys (5 minutes)

### Required Keys

1. **Shodan** (Free tier available)
   - Visit: https://account.shodan.io/
   - Sign up → Copy API key

2. **VirusTotal** (Free tier available)
   - Visit: https://www.virustotal.com/gui/my-apikey
   - Sign up → Copy API key

3. **Censys** (Free tier available)
   - Visit: https://search.censys.io/account/api
   - Sign up → Copy API ID & Secret

4. **GitHub Token**
   - Visit: https://github.com/settings/tokens
   - Generate new token → Select `repo`, `read:org` → Copy

5. **SecurityTrails** (Free tier available)
   - Visit: https://securitytrails.com/app/account/credentials
   - Sign up → Copy API key

6. **Hunter** (Free tier available)
   - Visit: https://hunter.how/
   - Sign up → Copy API key

## ⚡ Quick Setup

```bash
# 1. Clone repository
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp

# 2. Run setup
chmod +x setup.sh
./setup.sh

# 3. Add API keys when prompted
# The script will open .env file automatically

# 4. Start services (already done by setup.sh)
# If needed: docker-compose up -d
```

## 🔌 Connect to Claude Desktop

### macOS
```bash
# Edit config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Add this:
{
  "mcpServers": {
    "bugbounty": {
      "command": "docker",
      "args": ["exec", "-i", "bugbounty-mcp", "python", "-m", "mcp_server"]
    }
  }
}
```

### Linux
```bash
# Edit config
nano ~/.config/Claude/claude_desktop_config.json

# Add same config as macOS
```

### Windows (WSL)
```powershell
# Edit config
notepad %APPDATA%\Claude\claude_desktop_config.json

# Add this:
{
  "mcpServers": {
    "bugbounty": {
      "command": "wsl",
      "args": ["docker", "exec", "-i", "bugbounty-mcp", "python", "-m", "mcp_server"]
    }
  }
}
```

**Restart Claude Desktop after editing!**

## ✅ Verify Installation

```bash
# Check services
docker-compose ps

# All services should show "Up (healthy)"

# Test in Claude Desktop
# Open Claude and type:
"List available bug bounty tools"
```

## 🎯 Your First Scan

In Claude Desktop, try:

```
Run a passive reconnaissance on example.com
```

Or:

```
Find subdomains for example.com
```

## 📊 Access Dashboard

Open browser: http://localhost:8080

## 🆘 Quick Troubleshooting

### Services won't start
```bash
docker-compose logs
docker-compose restart
```

### Claude can't connect
```bash
# Verify container is running
docker ps | grep bugbounty

# Test manually
docker exec -it bugbounty-mcp python -m mcp_server
```

### Port conflicts
```bash
# Edit docker-compose.yml
# Change ports from 8080:8080 to 8081:8080
```

## 📖 Next Steps

1. Read [README.md](README.md) for detailed features
2. Check [INSTALLATION.md](INSTALLATION.md) for troubleshooting
3. Explore all 20+ tools in Claude
4. Set up continuous monitoring
5. Generate your first professional report

## 💡 Pro Tips

- **Start passive**: Use `passive_only: true` for initial recon
- **Scope validation**: Always validate targets are in scope
- **Rate limits**: Be respectful of API rate limits
- **Legal**: Only test authorized targets
- **Backups**: Regularly backup your data

## 🎓 Example Workflows

### Workflow 1: Full Recon
```
1. Run full recon on target.com
2. List all found subdomains
3. Scan top 10 subdomains for vulnerabilities
4. Generate a report
```

### Workflow 2: Quick Check
```
1. Check if target.com has exposed S3 buckets
2. Search Shodan for target.com services
3. Look for secrets in JavaScript files
```

### Workflow 3: Deep Scan
```
1. Enumerate subdomains for target.com
2. Run port scan on all subdomains
3. Identify technologies used
4. Run Nuclei templates for known CVEs
5. Generate comprehensive report
```

## 🔗 Useful Links

- **Repository**: https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp
- **Issues**: https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/issues
- **Discussions**: https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/discussions

## ⚖️ Legal Reminder

Always ensure you have authorization before testing any target. This tool is for ethical security testing only.

---

**Ready to hunt bugs? Start with Claude Desktop now!** 🎯
