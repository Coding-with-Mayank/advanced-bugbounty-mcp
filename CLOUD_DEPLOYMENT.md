# ============================================
# Cloud Deployment Guide
# Advanced Bug Bounty MCP Server - 2025
# ============================================

This guide covers deployment to major cloud providers.

## Table of Contents
1. [AWS EC2 Deployment](#aws-ec2)
2. [Google Cloud Compute Engine](#gcp-compute)
3. [Azure VM Deployment](#azure-vm)
4. [DigitalOcean Droplet](#digitalocean)
5. [Linode](#linode)
6. [Hetzner Cloud](#hetzner)

---

## Prerequisites

- Cloud provider account
- SSH key pair
- Basic understanding of cloud infrastructure
- Docker installed (will be installed by script)

---

## Quick Deploy (Any Provider)

### 1. Launch Instance

**Recommended Specs:**
- **Minimum:** 2 vCPU, 4 GB RAM, 50 GB SSD
- **Recommended:** 4 vCPU, 8 GB RAM, 100 GB SSD
- **Optimal:** 8 vCPU, 16 GB RAM, 200 GB SSD
- **OS:** Ubuntu 22.04 LTS or Debian 12

### 2. One-Line Install

```bash
curl -fsSL https://raw.githubusercontent.com/Coding-with-Mayank/advanced-bugbounty-mcp/main/cloud-deploy.sh | bash
```

Or manual steps:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y curl git docker.io docker-compose

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Clone repository
git clone https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp.git
cd advanced-bugbounty-mcp

# Configure environment
cp .env.example .env
nano .env  # Add your API keys

# Deploy
docker-compose up -d
```

---

## AWS EC2 Deployment

### Launch Instance

```bash
# Using AWS CLI
aws ec2 run-instances \
  --image-id ami-0557a15b87f6559cf \
  --instance-type t3.large \
  --key-name YOUR_KEY_NAME \
  --security-group-ids YOUR_SECURITY_GROUP \
  --subnet-id YOUR_SUBNET \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":100,"VolumeType":"gp3"}}]' \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=BugBounty-MCP}]'
```

### Security Group Rules

```bash
# SSH
Port 22 (TCP) from Your IP

# Web Dashboard
Port 8080 (TCP) from Your IP

# MCP Server
Port 9090 (TCP) from Localhost only
```

### Connect and Deploy

```bash
ssh -i your-key.pem ubuntu@your-instance-ip
curl -fsSL https://raw.githubusercontent.com/Coding-with-Mayank/advanced-bugbounty-mcp/main/cloud-deploy.sh | bash
```

### AWS ECS Deployment (Container Service)

See `deployment/aws-ecs/` directory for Terraform configuration.

---

## GCP Compute Engine

### Using gcloud CLI

```bash
# Create instance
gcloud compute instances create bugbounty-mcp \
  --zone=us-central1-a \
  --machine-type=n2-standard-2 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --tags=bugbounty,http-server

# Configure firewall
gcloud compute firewall-rules create allow-bugbounty \
  --allow=tcp:8080,tcp:22 \
  --source-ranges=YOUR_IP/32 \
  --target-tags=bugbounty
```

### Connect and Deploy

```bash
gcloud compute ssh bugbounty-mcp --zone=us-central1-a
curl -fsSL https://raw.githubusercontent.com/Coding-with-Mayank/advanced-bugbounty-mcp/main/cloud-deploy.sh | bash
```

---

## Azure VM Deployment

### Using Azure CLI

```bash
# Create resource group
az group create --name BugBountyRG --location eastus

# Create VM
az vm create \
  --resource-group BugBountyRG \
  --name BugBountyMCP \
  --image Ubuntu2204 \
  --size Standard_D2s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --os-disk-size-gb 100

# Open ports
az vm open-port --port 8080 --resource-group BugBountyRG --name BugBountyMCP --priority 1001
az vm open-port --port 22 --resource-group BugBountyRG --name BugBountyMCP --priority 1002
```

---

## DigitalOcean Droplet

### Using doctl CLI

```bash
# Create droplet
doctl compute droplet create bugbounty-mcp \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --region nyc1 \
  --ssh-keys YOUR_SSH_KEY_ID \
  --enable-monitoring \
  --enable-ipv6

# Get droplet IP
doctl compute droplet list
```

### Or via Web Console

1. Go to DigitalOcean Dashboard
2. Create Droplet → Ubuntu 22.04
3. Choose: 4GB RAM / 2 vCPUs / 80GB SSD ($24/mo)
4. Add SSH key
5. Launch

### Deploy

```bash
ssh root@your-droplet-ip
curl -fsSL https://raw.githubusercontent.com/Coding-with-Mayank/advanced-bugbounty-mcp/main/cloud-deploy.sh | bash
```

---

## Linode

### Using linode-cli

```bash
# Create instance
linode-cli linodes create \
  --type g6-standard-2 \
  --region us-east \
  --image linode/ubuntu22.04 \
  --root_pass YOUR_ROOT_PASSWORD \
  --label bugbounty-mcp
```

---

## Hetzner Cloud

### Using hcloud CLI

```bash
# Create server
hcloud server create \
  --name bugbounty-mcp \
  --type cpx21 \
  --image ubuntu-22.04 \
  --ssh-key YOUR_SSH_KEY_NAME \
  --location nbg1
```

---

## Docker Swarm Deployment (Multi-Node)

For production deployments with high availability:

```bash
# Initialize swarm on manager node
docker swarm init --advertise-addr YOUR_MANAGER_IP

# On worker nodes
docker swarm join --token YOUR_SWARM_TOKEN YOUR_MANAGER_IP:2377

# Deploy stack
docker stack deploy -c docker-stack.yml bugbounty
```

---

## Kubernetes Deployment

For enterprise-scale deployments:

```bash
# Apply Kubernetes manifests
kubectl apply -f deployment/kubernetes/

# Check deployment
kubectl get pods -n bugbounty
kubectl get services -n bugbounty
```

See `deployment/kubernetes/` directory for full configuration.

---

## Environment Variables for Cloud

```bash
# Required
SHODAN_API_KEY=your_key
VIRUSTOTAL_API_KEY=your_key
CENSYS_API_ID=your_id
CENSYS_API_SECRET=your_secret

# Cloud-specific
CLOUD_PROVIDER=aws  # or gcp, azure, digitalocean
ENABLE_MONITORING=true
AUTO_BACKUP=true
BACKUP_INTERVAL=daily
S3_BACKUP_BUCKET=your-backup-bucket  # For AWS
```

---

## Persistent Storage

### AWS EBS Volume

```bash
# Create and attach volume
aws ec2 create-volume --size 200 --availability-zone us-east-1a --volume-type gp3
aws ec2 attach-volume --volume-id vol-xxxxx --instance-id i-xxxxx --device /dev/sdf

# Mount
sudo mkfs -t ext4 /dev/sdf
sudo mount /dev/sdf /app/data
```

### GCP Persistent Disk

```bash
gcloud compute disks create bugbounty-data --size=200GB --zone=us-central1-a
gcloud compute instances attach-disk bugbounty-mcp --disk=bugbounty-data --zone=us-central1-a
```

---

## Monitoring & Logs

### Access Logs

```bash
# Application logs
docker-compose logs -f mcp-server

# System logs
sudo journalctl -u docker -f
```

### Monitoring Stack

Deploy with monitoring enabled:

```bash
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d
```

Access:
- Grafana: `http://your-ip:3000` (admin/admin)
- Prometheus: `http://your-ip:9091`

---

## Security Best Practices

1. **Firewall Configuration**
   ```bash
   sudo ufw enable
   sudo ufw allow 22/tcp
   sudo ufw allow 8080/tcp from YOUR_IP
   ```

2. **SSL/TLS**
   ```bash
   # Use Let's Encrypt
   sudo apt install certbot
   sudo certbot certonly --standalone -d your-domain.com
   ```

3. **API Key Security**
   - Never commit .env file
   - Use secrets management (AWS Secrets Manager, GCP Secret Manager)
   - Rotate keys regularly

4. **Regular Updates**
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Update containers
   docker-compose pull
   docker-compose up -d
   ```

---

## Cost Optimization

### AWS
- Use Spot Instances for non-critical workloads
- Enable auto-shutdown during off-hours
- Use S3 Glacier for log archival

### All Providers
- Right-size instances based on usage
- Use reserved instances for long-term
- Enable auto-scaling for variable workloads
- Set up billing alerts

---

## Troubleshooting

### Can't connect to instance
```bash
# Check security groups/firewall
# Verify SSH key
# Check instance state
```

### Docker not starting
```bash
sudo systemctl status docker
sudo systemctl restart docker
sudo docker ps -a
```

### Out of memory
```bash
# Check usage
free -h
docker stats

# Increase instance size or add swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## Backup & Recovery

### Automated Backups

```bash
# Backup script (runs daily via cron)
./scripts/backup.sh

# Restore from backup
./scripts/restore.sh /path/to/backup.tar.gz
```

### Manual Backup

```bash
# Backup data
docker run --rm --volumes-from bugbounty-mcp -v $(pwd):/backup ubuntu tar czf /backup/bugbounty-backup.tar.gz /app/data

# Restore data
docker run --rm --volumes-from bugbounty-mcp -v $(pwd):/backup ubuntu tar xzf /backup/bugbounty-backup.tar.gz
```

---

## Support

- 📧 Email: support@example.com
- 💬 Discord: [Join Server](https://discord.gg/yourserver)
- 🐛 Issues: [GitHub Issues](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/issues)
- 📚 Docs: [Full Documentation](https://docs.example.com)

---

## License

MIT License - See LICENSE file for details
