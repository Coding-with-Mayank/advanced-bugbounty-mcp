# Project Structure

```
advanced-bugbounty-mcp/
├── .github/
│   └── workflows/
│       └── docker-build.yml       # CI/CD pipeline
│
├── mcp_server/                    # Main MCP server package
│   ├── __init__.py                # Server entry point
│   ├── __main__.py                # Main execution
│   ├── server.py                  # MCP server implementation
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
├── dashboard/                     # Web dashboard (Node.js)
│   ├── Dockerfile                 # Dashboard Docker config
│   ├── package.json               # Node.js dependencies
│   ├── server.js                  # Express server
│   ├── public/                    # Static files
│   │   └── index.html             # Dashboard UI
│   ├── .dockerignore              # Docker ignore file
│   └── README.md                  # Dashboard docs
│
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
├── .dockerignore                  # Docker ignore rules
├── Dockerfile                     # Main Dockerfile
├── docker-compose.yml             # Docker Compose config
├── requirements.txt               # Python dependencies
├── setup.sh                       # Installation script
├── Makefile                       # Make commands
├── mongo-init.js                  # MongoDB initialization
├── VERSION                        # Version file
├── LICENSE                        # MIT License
├── README.md                      # Main documentation
├── INSTALLATION.md                # Installation guide
├── QUICKSTART.md                  # Quick start guide
├── CONTRIBUTING.md                # Contributing guidelines
├── CHANGELOG.md                   # Version changelog
└── PROJECT_STRUCTURE.md           # This file
```

## Key Components

### MCP Server (`mcp_server/`)
Implements the Model Context Protocol for Claude integration.

**Features:**
- `server.py` - Main MCP server with tool implementations
- Tool: `cdn_detection` - NEW in v2.1.0 - CDN provider identification
- Tool: `recon_full` - Comprehensive reconnaissance
- Tool: `subdomain_enum` - Subdomain enumeration
- Tool: `scan_vulnerabilities` - Vulnerability scanning

### Dashboard (`dashboard/`)
Node.js/Express web dashboard for monitoring and visualization.

**Components:**
- Express.js API server
- MongoDB integration for data display
- Real-time statistics
- Beautiful, responsive UI
- Health monitoring
- Scan history tracking

**Access:**
- Dashboard: http://localhost:3000
- API: http://localhost:3000/api
- Health: http://localhost:3000/api/health

### Core Modules
- Configuration management
- Database connections (MongoDB, Redis)
- Scope validation
- Rate limiting
- CDN detection engine

### Tools & Features
- **Reconnaissance**: Subdomain enum, port scanning, technology detection
- **CDN Detection**: Identify CDN providers, find origin IPs, WAF bypass
- **Discovery**: Cloud assets, JS analysis, API endpoints
- **Scanning**: XSS, SQLi, SSRF, IDOR, XXE, and 50+ vulnerability types
- **Intelligence**: Shodan, VirusTotal, Censys (v2 API), SecurityTrails, Hunter
- **Reporting**: Professional report generation with CVSS scoring

### Docker Services
1. **mcp-server**: Main Python application (ports 8080, 9090)
2. **mongodb**: Database storage (port 27017)
3. **redis**: Caching layer (port 6379)
4. **nuclei**: Vulnerability scanner (ProjectDiscovery)
5. **httpx**: HTTP probe (ProjectDiscovery)
6. **subfinder**: Subdomain finder (ProjectDiscovery)
7. **web-dashboard**: Node.js dashboard (port 3000)

### Configuration Files
- `.env` - Environment variables (API keys, database credentials)
- `docker-compose.yml` - Service orchestration
- `Dockerfile` - Main Python container
- `dashboard/Dockerfile` - Dashboard container

### Data Directories
- `data/` - Scan results and cached data
- `reports/` - Generated security reports
- `logs/` - Application logs
- `wordlists/` - Custom wordlists for fuzzing
- `nuclei-templates/` - Vulnerability detection templates

## Version 2.1.0 Updates

### New Components
- ✨ CDN Detection module in `mcp_server/server.py`
- ✨ Complete dashboard implementation in `dashboard/`
- 🔧 Updated Censys API integration (single key)
- 📚 Enhanced documentation

### Breaking Changes
- Censys API now uses `CENSYS_API_KEY` instead of ID + Secret
- VirusTotal integration uses `vt-py` instead of `python-virustotal`

## Development Notes

### Adding New Tools
1. Add tool definition in `mcp_server/server.py` -> `list_tools()`
2. Implement handler function (e.g., `handle_cdn_detection()`)
3. Add tool call in `call_tool()` function
4. Update documentation in README.md

### Dashboard Development
```bash
cd dashboard
npm install
npm run dev  # Development mode with hot reload
```

### Testing
```bash
# Run tests
make test

# Build containers
make build

# Start services
make start
```

## Port Mapping

| Service       | Internal Port | External Port |
|---------------|---------------|---------------|
| MCP Server    | 9090          | 9090          |
| API/Dashboard | 8080          | 8080          |
| Web Dashboard | 3000          | 3000          |
| MongoDB       | 27017         | 27017         |
| Redis         | 6379          | 6379          |

## Architecture

```
┌─────────────┐
│   Claude    │
│   Desktop   │
└──────┬──────┘
       │ MCP Protocol
       │
┌──────▼──────────────────────────────────────┐
│         MCP Server (Python)                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   Recon  │  │  Scanner │  │   Intel  │  │
│  └──────────┘  └──────────┘  └──────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │    CDN   │  │ Discovery│  │ Reporting│  │
│  └──────────┘  └──────────┘  └──────────┘  │
└─────────┬───────────────────────────────────┘
          │
    ┌─────▼─────┐
    │  MongoDB  │
    │   Redis   │
    └───────────┘
          │
    ┌─────▼─────────┐
    │   Dashboard   │
    │   (Node.js)   │
    └───────────────┘
```

## Security Considerations

- API keys stored in `.env` (never committed)
- Docker network isolation
- Rate limiting on all external APIs
- Scope validation before scanning
- Secure MongoDB authentication
- Redis password protection

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.