# Upgrade Notes - Version 2.0.0 (2025)

## What's New

### 🚀 Major Updates

1. **Latest Tool Versions (2025)**
   - Nuclei v3 with latest templates (10.3.1+)
   - ProjectDiscovery tools updated to latest versions
   - Added 20+ new reconnaissance tools
   - Python 3.12 for better performance
   - Go 1.24 for latest tool compatibility

2. **New Tools Added**
   - alterx - Advanced permutation generator
   - cvemap - CVE vulnerability mapper
   - asnmap - ASN enumeration and mapping
   - interactsh-client - OOB interaction testing
   - mapcidr - CIDR manipulation
   - puredns - Fast DNS resolver
   - dalfox - XSS scanner
   - gowitness - Web screenshot utility
   - anew, unfurl, meg - Additional utilities

3. **Cloud Deployment Ready**
   - One-command cloud deployment script
   - Support for AWS, GCP, Azure, DigitalOcean, Linode, Hetzner
   - Auto-detection of cloud provider
   - Optimized Docker multi-stage builds
   - Persistent volume support
   - Auto-backup and monitoring setup

4. **Enhanced MCP Server**
   - More comprehensive tool integrations
   - Better error handling
   - Improved logging
   - Rate limiting support
   - API integrations for cloud services

5. **Performance Improvements**
   - Multi-stage Docker builds (smaller images)
   - Optimized wordlist downloads
   - Better caching strategies
   - Resource-efficient configurations

6. **Security Enhancements**
   - Updated cryptography libraries
   - Latest security scanning tools
   - Improved secret management
   - Firewall configuration scripts

### 📦 Tool Versions

| Tool | Old Version | New Version |
|------|-------------|-------------|
| Nuclei | v2.x | v3.x |
| Subfinder | v2.x | v2.x (latest) |
| HTTPX | Old | Latest |
| Python | 3.11 | 3.12 |
| Go | 1.21 | 1.24 |
| All others | Various | Latest |

### 🔧 Breaking Changes

1. **Docker Configuration**
   - Now uses multi-stage builds
   - Some environment variables renamed
   - Volume structure changed

2. **Python Dependencies**
   - Several packages updated with new APIs
   - Some deprecated packages removed

3. **Tool Locations**
   - All Go tools now in `/usr/local/bin`
   - Config files standardized in `/root/.config/`

### 📋 Migration Guide

From v1.x to v2.0:

1. **Backup Your Data**
   ```bash
   docker-compose down
   docker run --rm --volumes-from bugbounty-mcp -v $(pwd):/backup ubuntu tar czf /backup/data-backup.tar.gz /app/data
   ```

2. **Update Repository**
   ```bash
   git pull origin main
   git checkout upgrade-2025
   ```

3. **Update Environment Variables**
   - Review `.env.example` for new variables
   - Update your `.env` file accordingly

4. **Rebuild Containers**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

5. **Verify Installation**
   ```bash
   docker-compose ps
   docker-compose logs -f mcp-server
   ```

### 🌐 Cloud Deployment

New one-line deployment for cloud instances:

```bash
curl -fsSL https://raw.githubusercontent.com/Coding-with-Mayank/advanced-bugbounty-mcp/upgrade-2025/cloud-deploy.sh | bash
```

See `CLOUD_DEPLOYMENT.md` for detailed instructions.

### 📚 Documentation Updates

- New: `CLOUD_DEPLOYMENT.md` - Comprehensive cloud deployment guide
- Updated: `README.md` - New features and usage
- Updated: `INSTALLATION.md` - Cloud-specific instructions

### 🐛 Bug Fixes

- Fixed Nuclei template update issues
- Resolved Docker build failures on ARM architectures
- Fixed API key configuration persistence
- Improved error handling in MCP server
- Fixed wordlist download failures

### 🎯 Future Plans

- Kubernetes deployment manifests
- Terraform configurations for IaC
- GUI dashboard improvements
- AI-powered vulnerability analysis
- Integration with more bug bounty platforms

### 💡 Tips

1. **For Production Use**
   - Use recommended instance sizes (4+ vCPU, 8+ GB RAM)
   - Enable auto-backups
   - Configure monitoring
   - Use SSL/TLS for web access

2. **For Development**
   - Use smaller instances (2 vCPU, 4 GB RAM)
   - Enable debug logging
   - Mount local directories for development

3. **Performance Tuning**
   - Adjust Nuclei rate limits in config
   - Configure Redis for better caching
   - Use SSD storage for databases

### 🙏 Acknowledgments

Thanks to:
- ProjectDiscovery team for amazing tools
- Bug bounty community for feedback
- Contributors and testers

### 📞 Support

- GitHub Issues: [Report bugs](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/issues)
- Discussions: [Ask questions](https://github.com/Coding-with-Mayank/advanced-bugbounty-mcp/discussions)

---

**Full Changelog**: See [CHANGELOG.md](CHANGELOG.md) for complete details.