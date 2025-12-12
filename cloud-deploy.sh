#!/bin/bash

# ============================================
# Cloud Deployment Script
# Advanced Bug Bounty MCP Server - 2025
# ============================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Detect cloud provider
detect_cloud_provider() {
    print_info "Detecting cloud provider..."
    
    if [ -f /sys/hypervisor/uuid ] && [ `head -c 3 /sys/hypervisor/uuid` == ec2 ]; then
        CLOUD_PROVIDER="AWS"
    elif curl -s -f -m 1 http://metadata.google.internal/computeMetadata/v1/ -H "Metadata-Flavor: Google" > /dev/null 2>&1; then
        CLOUD_PROVIDER="GCP"
    elif curl -s -f -m 1 -H Metadata:true "http://169.254.169.254/metadata/instance?api-version=2021-02-01" > /dev/null 2>&1; then
        CLOUD_PROVIDER="Azure"
    elif curl -s -f -m 1 http://169.254.169.254/metadata/v1/ > /dev/null 2>&1; then
        CLOUD_PROVIDER="DigitalOcean"
    else
        CLOUD_PROVIDER="Unknown"
    fi
    
    print_success "Cloud provider detected: $CLOUD_PROVIDER"
}

# Check system requirements
check_requirements() {
    print_info "Checking system requirements..."
    
    # Check CPU
    CPU_CORES=$(nproc)
    if [ "$CPU_CORES" -lt 2 ]; then
        print_warning "System has $CPU_CORES CPU cores. Recommended: 2 or more"
    else
        print_success "CPU cores: $CPU_CORES"
    fi
    
    # Check RAM
    TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_RAM" -lt 4 ]; then
        print_warning "System has ${TOTAL_RAM}GB RAM. Recommended: 4GB or more"
    else
        print_success "RAM: ${TOTAL_RAM}GB"
    fi
    
    # Check disk space
    DISK_SPACE=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_SPACE" -lt 20 ]; then
        print_warning "Available disk space: ${DISK_SPACE}GB. Recommended: 50GB or more"
    else
        print_success "Disk space: ${DISK_SPACE}GB available"
    fi
}

# Update system
update_system() {
    print_info "Updating system packages..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update -qq
        sudo apt-get upgrade -y -qq
        print_success "System updated (apt)"
    elif command -v yum &> /dev/null; then
        sudo yum update -y -q
        print_success "System updated (yum)"
    elif command -v dnf &> /dev/null; then
        sudo dnf update -y -q
        print_success "System updated (dnf)"
    fi
}

# Install Docker
install_docker() {
    if command -v docker &> /dev/null; then
        print_success "Docker already installed: $(docker --version)"
        return
    fi
    
    print_info "Installing Docker..."
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    
    # Start Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Add current user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed: $(docker --version)"
}

# Install Docker Compose
install_docker_compose() {
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1; then
        print_success "Docker Compose already installed"
        return
    fi
    
    print_info "Installing Docker Compose..."
    
    # Install Docker Compose V2 (as Docker plugin)
    sudo apt-get install -y docker-compose-plugin -qq || {
        # Fallback to standalone installation
        sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
    }
    
    print_success "Docker Compose installed"
}

# Install additional tools
install_tools() {
    print_info "Installing additional tools..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get install -y -qq \
            git \
            curl \
            wget \
            vim \
            nano \
            htop \
            tmux \
            screen \
            jq \
            unzip \
            ca-certificates \
            gnupg \
            lsb-release
    fi
    
    print_success "Additional tools installed"
}

# Setup firewall
setup_firewall() {
    print_info "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        # Allow SSH
        sudo ufw allow 22/tcp
        
        # Allow web dashboard (with restrictions)
        sudo ufw allow from any to any port 8080 proto tcp
        
        # Enable firewall
        echo "y" | sudo ufw enable
        
        print_success "Firewall configured (ufw)"
    elif command -v firewalld &> /dev/null; then
        sudo systemctl start firewalld
        sudo firewall-cmd --permanent --add-port=22/tcp
        sudo firewall-cmd --permanent --add-port=8080/tcp
        sudo firewall-cmd --reload
        
        print_success "Firewall configured (firewalld)"
    else
        print_warning "No firewall found. Please configure manually."
    fi
}

# Clone repository
clone_repository() {
    print_info "Cloning repository..."
    
    INSTALL_DIR="/opt/advanced-bugbounty-mcp"
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Directory already exists. Updating..."
        cd "$INSTALL_DIR"
        git pull
    else
        sudo git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git "$INSTALL_DIR"
        sudo chown -R $USER:$USER "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    
    print_success "Repository ready at $INSTALL_DIR"
}

# Configure environment
configure_environment() {
    print_info "Configuring environment..."
    
    if [ ! -f .env ]; then
        cp .env.example .env
        print_warning "Created .env file. Please edit and add your API keys:"
        echo ""
        echo "  Required API Keys:"
        echo "  - SHODAN_API_KEY"
        echo "  - VIRUSTOTAL_API_KEY"
        echo "  - CENSYS_API_ID and CENSYS_API_SECRET"
        echo "  - GITHUB_TOKEN"
        echo ""
        
        read -p "Do you want to edit .env now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ${EDITOR:-nano} .env
        fi
    else
        print_success ".env file already exists"
    fi
}

# Build and start containers
deploy_containers() {
    print_info "Building and starting containers..."
    
    # Pull latest images
    docker-compose pull
    
    # Build custom images
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    print_success "Containers deployed"
}

# Setup systemd service
setup_systemd() {
    print_info "Setting up systemd service..."
    
    sudo tee /etc/systemd/system/bugbounty-mcp.service > /dev/null <<EOF
[Unit]
Description=Advanced Bug Bounty MCP Server
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/advanced-bugbounty-mcp
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable bugbounty-mcp.service
    
    print_success "Systemd service configured"
}

# Setup auto-updates
setup_auto_updates() {
    print_info "Setting up automatic updates..."
    
    # Create update script
    sudo tee /opt/advanced-bugbounty-mcp/update.sh > /dev/null <<'EOF'
#!/bin/bash
cd /opt/advanced-bugbounty-mcp
git pull
docker-compose pull
docker-compose up -d
docker system prune -f
EOF
    
    sudo chmod +x /opt/advanced-bugbounty-mcp/update.sh
    
    # Add cron job for weekly updates
    (crontab -l 2>/dev/null; echo "0 2 * * 0 /opt/advanced-bugbounty-mcp/update.sh >> /var/log/bugbounty-update.log 2>&1") | crontab -
    
    print_success "Auto-updates configured (weekly, Sunday 2 AM)"
}

# Setup monitoring
setup_monitoring() {
    print_info "Setting up monitoring..."
    
    # Deploy monitoring stack if available
    if [ -f docker-compose.monitoring.yml ]; then
        docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
        print_success "Monitoring stack deployed"
    else
        print_info "Monitoring configuration not found, skipping..."
    fi
}

# Setup backup
setup_backup() {
    print_info "Setting up backups..."
    
    # Create backup script
    sudo tee /opt/advanced-bugbounty-mcp/backup.sh > /dev/null <<'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/bugbounty-mcp"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup data
docker run --rm --volumes-from bugbounty-mcp \
    -v $BACKUP_DIR:/backup \
    ubuntu tar czf /backup/data-$DATE.tar.gz /app/data

# Backup database
docker exec bugbounty-mongo mongodump --out=/tmp/dump
docker cp bugbounty-mongo:/tmp/dump $BACKUP_DIR/mongo-$DATE/

# Keep only last 7 backups
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
find $BACKUP_DIR -type d -name "mongo-*" -mtime +7 -exec rm -rf {} +
EOF
    
    sudo chmod +x /opt/advanced-bugbounty-mcp/backup.sh
    
    # Add cron job for daily backups
    (crontab -l 2>/dev/null; echo "0 3 * * * /opt/advanced-bugbounty-mcp/backup.sh >> /var/log/bugbounty-backup.log 2>&1") | crontab -
    
    print_success "Backups configured (daily, 3 AM)"
}

# Display final information
display_info() {
    print_header "Deployment Complete!"
    
    INSTANCE_IP=$(curl -s http://checkip.amazonaws.com || hostname -I | awk '{print $1}')
    
    echo ""
    print_success "Advanced Bug Bounty MCP Server is now running!"
    echo ""
    
    print_info "Access URLs:"
    echo "  • Web Dashboard: http://$INSTANCE_IP:8080"
    echo "  • MCP Server: http://localhost:9090"
    echo ""
    
    print_info "Useful commands:"
    echo "  • View logs:          docker-compose logs -f"
    echo "  • Stop services:      docker-compose stop"
    echo "  • Start services:     docker-compose start"
    echo "  • Restart services:   docker-compose restart"
    echo "  • Update system:      /opt/advanced-bugbounty-mcp/update.sh"
    echo "  • Backup data:        /opt/advanced-bugbounty-mcp/backup.sh"
    echo ""
    
    print_info "Service management:"
    echo "  • Status:             sudo systemctl status bugbounty-mcp"
    echo "  • Enable on boot:     sudo systemctl enable bugbounty-mcp"
    echo "  • Disable on boot:    sudo systemctl disable bugbounty-mcp"
    echo ""
    
    if [ "$CLOUD_PROVIDER" != "Unknown" ]; then
        print_info "Cloud Provider: $CLOUD_PROVIDER"
        
        case "$CLOUD_PROVIDER" in
            "AWS")
                echo "  • Don't forget to configure Security Groups for port 8080"
                ;;
            "GCP")
                echo "  • Don't forget to configure Firewall rules for port 8080"
                ;;
            "Azure")
                echo "  • Don't forget to configure Network Security Groups for port 8080"
                ;;
            "DigitalOcean")
                echo "  • Don't forget to configure Cloud Firewall for port 8080"
                ;;
        esac
        echo ""
    fi
    
    print_warning "IMPORTANT: Edit .env file and add your API keys!"
    echo "  cd /opt/advanced-bugbounty-mcp && nano .env"
    echo ""
    
    print_info "Documentation:"
    echo "  • GitHub: https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp"
    echo "  • Cloud Guide: /opt/advanced-bugbounty-mcp/CLOUD_DEPLOYMENT.md"
    echo ""
    
    print_success "Happy Bug Hunting! 🎯"
}

# Main installation flow
main() {
    clear
    print_header "Advanced Bug Bounty MCP - Cloud Deployment"
    echo ""
    
    print_warning "This script will install and configure the Bug Bounty MCP Server"
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Installation cancelled"
        exit 1
    fi
    
    echo ""
    detect_cloud_provider
    check_requirements
    echo ""
    
    update_system
    install_docker
    install_docker_compose
    install_tools
    echo ""
    
    setup_firewall
    echo ""
    
    clone_repository
    configure_environment
    echo ""
    
    deploy_containers
    setup_systemd
    setup_auto_updates
    setup_monitoring
    setup_backup
    echo ""
    
    display_info
}

# Run main installation
main
