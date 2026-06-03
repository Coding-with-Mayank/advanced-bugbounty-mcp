# Bug Bounty MCP Server v3.0.0

> **The world's most practical bug bounty setup** — works with Claude Desktop, Claude CLI, Gemini CLI, and standalone terminal mode. One command to install. AI-guided findings with next steps built in.

```
⚠️  Legal Notice: Only test targets you have explicit written permission to test.
    Unauthorized scanning is illegal. This tool is for authorized security testing only.
```

---

## What's inside

| Tool | Purpose |
|------|---------|
| `subfinder` | Passive subdomain discovery (50+ sources) |
| `httpx` | HTTP probing, tech detection, screenshots |
| `nuclei` | 10,000+ vulnerability templates |
| `naabu` | Fast port scanner |
| `katana` | Web crawler |
| `ffuf` | Directory/parameter fuzzer |
| `gobuster` | Brute-force enumeration |
| `gowitness` | Web screenshots |
| `dnsx` | DNS enumeration |
| `waybackurls + gau` | Historical URL discovery |
| `anew` | Deduplicate output streams |

Everything ships in a single Docker container. No Go, no Python, no tool installation on your host.

---

## Quick Start (3 steps)

```bash
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp
cd advanced-bugbounty-mcp
./setup.sh
```

That's it. Setup auto-handles:
- Checking Docker is running
- Creating `.env` with random passwords
- Downloading wordlists
- Building the Docker image
- Configuring **Claude Desktop**, **Claude CLI**, and **Gemini CLI** automatically
- Starting all services

---

## Using with Claude Desktop

After setup, restart Claude Desktop. Then just ask naturally:

```
Find all subdomains of example.com
```
```
Run a full recon on example.com and tell me what's interesting
```
```
Scan https://example.com for vulnerabilities and explain any findings
```
```
Take screenshots of these URLs and tell me what looks like admin panels
```

Claude will call the right tools automatically and return findings with guidance on what's suspicious and what to do next.

---

## Using with Claude CLI

Setup auto-registers the server. To verify:
```bash
claude mcp list
# Should show: bugbounty
```

Then in a Claude CLI session:
```
claude> Run full_recon on example.com
```

Manual registration (if setup didn't catch it):
```bash
claude mcp add bugbounty -- docker exec -i bugbounty-mcp python -m mcp_server
```

---

## Using with Gemini CLI

Setup auto-writes `~/.gemini/settings.json`. To verify:
```bash
cat ~/.gemini/settings.json
```

In Gemini CLI:
```
gemini> @bugbounty subdomain_enum domain=example.com
```

Manual setup — add to `~/.gemini/settings.json`:
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

---

## Manual Terminal Mode (no AI client needed)

```bash
# Full recon pipeline
python hunt.py full example.com

# Just subdomains
python hunt.py recon example.com

# Vulnerability scan
python hunt.py scan https://example.com --severity high,critical

# Directory fuzzing
python hunt.py fuzz https://example.com/FUZZ --ext php,asp,bak

# Historical URLs
python hunt.py wayback example.com

# Screenshots
python hunt.py screenshot example.com

# Certificate transparency
python hunt.py cert example.com
```

Or run directly inside the Docker container:
```bash
docker exec -it bugbounty-mcp bash
# Now you have all tools available
subfinder -d example.com -silent
nuclei -u https://example.com -severity high,critical
```

---

## Available MCP Tools

### Recon
| Tool | Description |
|------|-------------|
| `full_recon` | Full automated pipeline: subdomains → alive → ports → tech → screenshots |
| `subdomain_enum` | Passive subdomain discovery with subfinder |
| `subdomain_brute` | Active brute-force with wordlist |
| `alive_check` | Probe hosts with httpx (status, title, tech) |
| `port_scan` | Fast TCP port scan with naabu |
| `dns_enum` | DNS records (A, MX, NS, TXT, CNAME) |
| `screenshot` | Web screenshots with gowitness |
| `crawl` | Website crawling with katana |
| `wayback` | Historical URLs from Wayback + gau |
| `tech_detect` | Technology detection with httpx |

### Scanning
| Tool | Description |
|------|-------------|
| `nuclei_scan` | Full vulnerability scan with 10k+ templates |
| `dir_fuzz` | Directory/file fuzzing with ffuf |
| `xss_scan` | Targeted XSS scanning |
| `sqli_scan` | SQL injection scanning |
| `cors_check` | CORS misconfiguration check |

### Intelligence
| Tool | Description |
|------|-------------|
| `whois_lookup` | WHOIS data |
| `cert_search` | Certificate transparency (crt.sh) |
| `shodan_search` | Shodan query (needs API key) |

### Analysis
| Tool | Description |
|------|-------------|
| `analyze_findings` | Prioritize and chain multiple findings |
| `explain_finding` | Explain what a finding means + write-up template |
| `generate_report` | Professional Markdown bug bounty report |

---

## AI Guidance System

Every tool response includes a `guidance` block explaining:

- **`risk_level`** — info / low / medium / high / critical
- **`suspicious_items`** — patterns that warrant investigation
- **`next_steps`** — exactly what to try next
- **`manual_steps`** — what to do when automated tools can't go further
- **`limitations`** — why the tool may have missed things

Example:
```json
{
  "tool": "subdomain_enum",
  "data": { "count": 0, "subdomains": [] },
  "guidance": {
    "risk_level": "info",
    "summary": "No subdomains found via passive recon.",
    "limitations": "Passive-only recon cannot find subdomains with no public footprint.",
    "next_steps": [
      "Try active brute-force: subdomain_brute tool",
      "Search cert logs: https://crt.sh/?q=%.example.com",
      "Google dork: site:*.example.com -www",
      "Check VirusTotal: https://virustotal.com/gui/domain/example.com/relations"
    ],
    "manual_steps": [
      "Zone transfer: dig axfr example.com @ns1.example.com",
      "Reverse DNS: for ip in $(host example.com | awk '{print $4}'); do host $ip; done"
    ]
  }
}
```

---

## n8n Workflow Automation (optional)

n8n gives you visual workflows for scheduled scans and notifications.

```bash
# Start with n8n
make n8n
# OR
docker-compose --profile automation up -d
```

Then open **http://localhost:5678** (admin / your N8N_PASSWORD from .env).

Use cases:
- **Scheduled daily recon** — cron trigger → subdomain_enum → diff against yesterday → alert on new
- **Vulnerability alerts** — nuclei_scan → filter critical → Slack/Telegram notification
- **Report pipeline** — findings → generate_report → save to Notion / email

---

## Scoping (legal protection)

Set your allowed targets in `.env`:
```bash
# Only test these — everything else is blocked
ALLOWED_SCOPE=example.com,*.example.com,192.168.1.0/24
```

The server will reject any target not in scope.

---

## Management

```bash
make up          # Start everything
make down        # Stop everything
make logs        # Follow MCP server logs
make status      # Check all tools are working
make shell       # bash inside the container
make rebuild     # Rebuild after code changes
make update      # Pull latest + rebuild + update Nuclei templates
make test        # Verify all tools
```

---

## Project Structure

```
advanced-bugbounty-mcp/
├── Dockerfile              # Multi-stage Go tools + Python runtime
├── docker-compose.yml      # MCP server + MongoDB + Redis + optional n8n
├── requirements.txt        # Python deps (slim)
├── .env.example            # Configuration template
├── setup.sh                # One-command installer
├── Makefile                # Convenience commands
├── hunt.py                 # Standalone manual CLI
├── mcp_server/
│   ├── __main__.py         # Entry point: python -m mcp_server
│   ├── server.py           # All 20 MCP tools
│   ├── guidance.py         # Smart guidance engine
│   └── config.py           # Settings
├── config/subfinder/       # Subfinder API config
├── wordlists/              # Downloaded by setup.sh
├── n8n-workflows/          # n8n automation workflows
├── reports/                # Generated reports (git-ignored)
├── screenshots/            # gowitness screenshots (git-ignored)
└── output/                 # Manual hunt output (git-ignored)
```

---

## Troubleshooting

**Build fails:**
```bash
docker-compose build --no-cache
```

**Tool missing inside container:**
```bash
make shell
# Check: which subfinder
# If missing, the Go build step for that tool failed.
# Usually a network issue during build — retry: make rebuild
```

**MCP server not showing in Claude:**
```bash
# Verify container is running
docker ps | grep bugbounty-mcp
# Restart Claude Desktop after running setup.sh
```

**Port conflict (27017/6379/8080):**
```bash
# Change ports in docker-compose.yml:
# "27018:27017" for Mongo, "6380:6379" for Redis
```

**Screenshots not working:**
```bash
# gowitness needs Chromium (included in Dockerfile)
# If still failing:
docker exec bugbounty-mcp gowitness single -u https://example.com --disable-db
```

---

## License

MIT — use freely for authorized security testing.

**Remember:** Authorization first, always.
