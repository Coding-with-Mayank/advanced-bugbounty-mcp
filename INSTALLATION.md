# Installation Guide

Complete installation guide for the Advanced Bug Bounty MCP Server on Windows (WSL2), macOS, and Linux.

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp

# Run automated setup
chmod +x setup.sh
./setup.sh
```

For detailed platform-specific instructions, see the sections below.

## Prerequisites

- Docker Desktop (20.10.0+)
- Docker Compose (2.0.0+)
- Git
- 8GB+ RAM recommended
- 20GB+ disk space

## API Keys Required

1. **Shodan** - https://account.shodan.io/
2. **VirusTotal** - https://www.virustotal.com/gui/my-apikey
3. **Censys** - https://search.censys.io/account/api
4. **GitHub** - https://github.com/settings/tokens
5. **SecurityTrails** - https://securitytrails.com/app/account/credentials
6. **Hunter** - https://hunter.how/

## Platform-Specific Instructions

### Windows (WSL2)

1. Install WSL2:
```powershell
wsl --install
wsl --set-default-version 2
wsl --install -d Ubuntu-22.04
```

2. Install Docker Desktop and enable WSL integration

3. In WSL Ubuntu:
```bash
sudo apt update && sudo apt upgrade -y
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp
chmod +x setup.sh
./setup.sh
```

### macOS

1. Install Docker Desktop from https://www.docker.com/products/docker-desktop

2. Install Homebrew (if needed):
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3. Clone and setup:
```bash
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp
chmod +x setup.sh
./setup.sh
```

### Linux (Ubuntu/Debian)

```bash
# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
newgrp docker

# Clone and setup
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp
chmod +x setup.sh
./setup.sh
```

## Configuration

Edit `.env` file with your API keys:

```bash
nano .env
```

Add your API keys:
```env
SHODAN_API_KEY=your_key_here
VIRUSTOTAL_API_KEY=your_key_here
CENSYS_API_ID=your_id_here
CENSYS_API_SECRET=your_secret_here
GITHUB_TOKEN=your_token_here
SECURITYTRAILS_API_KEY=your_key_here
HUNTER_API_KEY=your_key_here
```

## Claude Desktop Integration

### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Linux
Edit `~/.config/Claude/claude_desktop_config.json` with same configuration.

### Windows
Edit `%APPDATA%/Claude/claude_desktop_config.json` and use:

```json
{
  "mcpServers": {
    "bugbounty": {
      "command": "wsl",
      "args": [
        "docker",
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

Restart Claude Desktop after configuration.

## Verification

```bash
# Check services
docker-compose ps

# Test MCP server
docker exec bugbounty-mcp python -c "import mcp_server; print('OK')"

# View logs
docker-compose logs -f
```

## Troubleshooting

### Container won't start
```bash
docker-compose logs mcp-server
docker-compose build --no-cache
docker-compose up -d
```

### Claude can't connect
1. Verify container is running: `docker ps | grep bugbounty`
2. Check config file path
3. Restart Claude Desktop

### Port conflicts
```bash
# Change ports in docker-compose.yml
ports:
  - "8081:8080"  # Change 8080 to 8081
```

## Next Steps

1. Read [README.md](README.md) for usage examples
2. Configure monitoring and notifications
3. Set up continuous scanning
4. Explore the web dashboard at http://localhost:8080

## Getting Help

- Issues: https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/issues
- Discussions: https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/discussions