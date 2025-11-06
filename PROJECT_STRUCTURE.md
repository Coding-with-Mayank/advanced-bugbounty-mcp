# Project Structure

```
advanced-bugbounty-mcp/
├── .github/
│   └── workflows/
│       └── docker-build.yml       # CI/CD pipeline
│
├── mcp_server/                    # Main MCP server package
│   ├── __init__.py                # Server entry point
│   ├── core/                      # Core functionality
│   ├── recon/                     # Reconnaissance modules
│   ├── discovery/                 # Asset discovery
│   ├── scanner/                   # Vulnerability scanners
│   ├── intelligence/              # Intelligence gathering
│   ├── exploitation/              # Exploitation modules
│   ├── reporting/                 # Reporting system
│   ├── monitoring/                # Monitoring system
│   ├── ml/                        # Machine learning
│   └── utils/                     # Utility functions
│
├── dashboard/                     # Web dashboard
├── tests/                         # Test suite
├── scripts/                       # Utility scripts
├── config/                        # Configuration files
├── data/                          # Data directory
├── reports/                       # Generated reports
├── logs/                          # Log files
├── wordlists/                     # Wordlists
├── nuclei-templates/              # Nuclei templates
├── docs/                          # Documentation
│
├── .env.example                   # Environment template
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Main Dockerfile
├── docker-compose.yml             # Docker Compose config
├── requirements.txt               # Python dependencies
├── setup.sh                       # Installation script
├── Makefile                       # Make commands
├── README.md                      # Main documentation
└── INSTALLATION.md                # Installation guide
```

## Key Components

### MCP Server
Implements the Model Context Protocol for Claude integration.

### Core Modules
- Configuration management
- Database connections
- Scope validation
- Rate limiting

### Tools
- Reconnaissance: Subdomain enum, port scanning
- Discovery: Cloud assets, JS analysis, API endpoints
- Scanning: XSS, SQLi, SSRF, and 50+ vulnerability types
- Intelligence: Shodan, VirusTotal, Censys integrations
- Reporting: Professional report generation

### Docker Services
1. mcp-server: Main application
2. mongodb: Database
3. redis: Caching
4. nuclei: Vulnerability scanner
5. httpx: HTTP probe
6. subfinder: Subdomain finder
7. web-dashboard: Web UI