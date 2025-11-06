#!/bin/bash

# ============================================
# Advanced Bug Bounty MCP Server Setup Script
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if running on WSL
check_wsl() {
    if grep -qi microsoft /proc/version; then
        print_success "Running on WSL"
        return 0
    else
        print_info "Not running on WSL"
        return 1
    fi
}

# Check Docker installation
check_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker is installed"
        docker --version
    else
        print_error "Docker is not installed"
        print_info "Please install Docker Desktop: https://www.docker.com/products/docker-desktop"
        exit 1
    fi
}

# Check Docker Compose installation
check_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
        print_success "Docker Compose is installed"
        docker-compose --version 2>/dev/null || docker compose version
    else
        print_error "Docker Compose is not installed"
        exit 1
    fi
}

# Create necessary directories
create_directories() {
    print_info "Creating necessary directories..."
    mkdir -p data reports logs wordlists nuclei-templates/custom config/subfinder
    print_success "Directories created"
}

# Setup environment file
setup_env() {
    if [ ! -f .env ]; then
        print_info "Creating .env file from template..."
        cp .env.example .env
        print_success ".env file created"
        print_warning "Please edit .env file and add your API keys!"
        print_info "Required API keys:"
        echo "  - SHODAN_API_KEY"
        echo "  - VIRUSTOTAL_API_KEY"
        echo "  - CENSYS_API_ID and CENSYS_API_SECRET"
        echo "  - GITHUB_TOKEN"
        echo "  - SECURITYTRAILS_API_KEY"
        echo "  - HUNTER_API_KEY"
        echo ""
        read -p "Press Enter to open .env file in nano (or Ctrl+C to exit and edit manually)..."
        nano .env || vi .env || echo "Please edit .env manually"
    else
        print_success ".env file already exists"
    fi
}

# Download wordlists
download_wordlists() {
    print_info "Downloading wordlists..."
    
    cd wordlists
    
    # Subdomain wordlist
    if [ ! -f subdomains.txt ]; then
        wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-110000.txt -O subdomains.txt
        print_success "Downloaded subdomain wordlist"
    fi
    
    # Directory wordlist
    if [ ! -f directories.txt ]; then
        wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O directories.txt
        print_success "Downloaded directory wordlist"
    fi
    
    # Parameter wordlist
    if [ ! -f parameters.txt ]; then
        wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/burp-parameter-names.txt -O parameters.txt
        print_success "Downloaded parameter wordlist"
    fi
    
    cd ..
}

# Build Docker images
build_images() {
    print_info "Building Docker images (this may take a few minutes)..."
    docker-compose build --no-cache
    print_success "Docker images built successfully"
}

# Start services
start_services() {
    print_info "Starting services..."
    docker-compose up -d
    print_success "Services started"
    
    # Wait for services to be healthy
    print_info "Waiting for services to be ready..."
    sleep 10
    
    # Check service status
    docker-compose ps
}

# Setup Claude Desktop integration
setup_claude_integration() {
    print_header "Claude Desktop Integration Setup"
    
    print_info "To connect this MCP server to Claude Desktop, you need to:"
    echo ""
    echo "1. Open Claude Desktop config file:"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        CONFIG_PATH="~/Library/Application Support/Claude/claude_desktop_config.json"
        echo "   ${CONFIG_PATH}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        CONFIG_PATH="~/.config/Claude/claude_desktop_config.json"
        echo "   ${CONFIG_PATH}"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        CONFIG_PATH="%APPDATA%/Claude/claude_desktop_config.json"
        echo "   ${CONFIG_PATH}"
    fi
    
    echo ""
    echo "2. Add the following configuration:"
    echo ""
    cat << 'EOF'
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
EOF
    echo ""
    echo "3. Restart Claude Desktop"
    echo ""
    
    read -p "Would you like to automatically add this configuration? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            CONFIG_FILE="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
            mkdir -p "$(dirname "$CONFIG_FILE")"
            
            if [ -f "$CONFIG_FILE" ]; then
                # Backup existing config
                cp "$CONFIG_FILE" "${CONFIG_FILE}.backup"
                print_success "Backed up existing config to ${CONFIG_FILE}.backup"
            fi
            
            # Create or update config
            cat > "$CONFIG_FILE" << 'EOF'
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
EOF
            print_success "Configuration added to Claude Desktop"
            print_warning "Please restart Claude Desktop for changes to take effect"
        else
            print_warning "Automatic configuration only supported on macOS"
            print_info "Please manually add the configuration shown above"
        fi
    fi
}

# Display status and next steps
display_status() {
    print_header "Setup Complete!"
    
    echo ""
    print_success "Advanced Bug Bounty MCP Server is running!"
    echo ""
    
    print_info "Service URLs:"
    echo "  • Web Dashboard: http://localhost:8080"
    echo "  • MCP Server: http://localhost:9090"
    echo "  • MongoDB: mongodb://localhost:27017"
    echo "  • Redis: redis://localhost:6379"
    echo ""
    
    print_info "Useful commands:"
    echo "  • View logs:           docker-compose logs -f"
    echo "  • Stop services:       docker-compose stop"
    echo "  • Restart services:    docker-compose restart"
    echo "  • Remove everything:   docker-compose down -v"
    echo "  • Update containers:   docker-compose pull && docker-compose up -d"
    echo ""
    
    print_info "Testing the MCP server:"
    echo "  docker exec -it bugbounty-mcp python -c \"from mcp_server import app; print('MCP Server OK')\""
    echo ""
    
    print_info "Next steps:"
    echo "  1. Ensure all API keys are set in .env file"
    echo "  2. Configure Claude Desktop integration (see above)"
    echo "  3. Open Claude and test: 'List available bug bounty tools'"
    echo "  4. Review README.md for detailed usage instructions"
    echo ""
}

# Test installation
test_installation() {
    print_header "Testing Installation"
    
    print_info "Testing Docker containers..."
    if docker-compose ps | grep -q "Up"; then
        print_success "Docker containers are running"
    else
        print_error "Some containers are not running"
        docker-compose ps
        return 1
    fi
    
    print_info "Testing database connection..."
    if docker exec bugbounty-mongo mongosh --eval "db.version()" > /dev/null 2>&1; then
        print_success "MongoDB is accessible"
    else
        print_warning "MongoDB connection test failed"
    fi
    
    print_success "Basic installation tests passed"
}

# Main installation flow
main() {
    clear
    print_header "Advanced Bug Bounty MCP Server Setup"
    echo ""
    
    # Check prerequisites
    print_header "Checking Prerequisites"
    check_wsl
    check_docker
    check_docker_compose
    echo ""
    
    # Setup
    print_header "Setting Up Project"
    create_directories
    setup_env
    echo ""
    
    # Ask if user wants to download wordlists
    read -p "Download wordlists? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        download_wordlists
    fi
    echo ""
    
    # Build and start
    print_header "Building and Starting Services"
    build_images
    start_services
    echo ""
    
    # Test installation
    test_installation
    echo ""
    
    # Claude integration
    setup_claude_integration
    echo ""
    
    # Display final status
    display_status
    
    print_success "Installation complete! 🎉"
}

# Run main installation
main
