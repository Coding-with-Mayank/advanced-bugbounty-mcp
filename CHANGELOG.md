# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-11-06

### Added
- **CDN Detection Tool**: New MCP tool for comprehensive CDN analysis
  - DNS CNAME-based detection for major CDN providers
  - HTTP header fingerprinting (Cloudflare, Akamai, Fastly, CloudFront, etc.)
  - IP range matching for CDN identification
  - Bug bounty-specific insights and recommendations
  - Detection methods tracking (CNAME, headers, IP ranges)
  - Origin IP discovery guidance for WAF bypass techniques
  - Support for 10+ major CDN providers
  - Detailed response header analysis
  - Security implications and next steps for bug bounty hunters

### Changed
- **BREAKING CHANGE**: Updated Censys API integration to use single API key
  - Changed from `CENSYS_API_ID` + `CENSYS_API_SECRET` to `CENSYS_API_KEY`
  - Updated `.env.example` with new format
  - Simplified authentication flow
  - ⚠️ **Action Required**: Users must update their `.env` file with new Censys API key format
- Enhanced documentation with CDN detection examples
- Updated README with comprehensive CDN detection usage
- Added CDN configuration section to `.env.example`

### Fixed
- Improved error handling in MCP server
- Enhanced logging for debugging CDN detection issues

### Security
- Updated Censys API integration to use current authentication method
- Improved credential handling for single API key format

### Documentation
- Added CDN detection examples to README
- Updated troubleshooting guide
- Added acknowledgment to ExternalAttacker-MCP for CDN detection inspiration
- Enhanced "What's New" section with version details
- Updated configuration examples with new Censys format

## [1.0.0] - 2025-11-06

### Added
- Initial release of Advanced Bug Bounty MCP Server
- MCP protocol integration with Claude
- Comprehensive reconnaissance tools
  - Subdomain enumeration from multiple sources
  - Port scanning with service detection
  - Technology stack detection
- Asset discovery features
  - Cloud storage enumeration (S3, Azure, GCS)
  - JavaScript analysis for secrets
  - API endpoint discovery
- Vulnerability scanning
  - XSS, SQLi, SSRF, IDOR, XXE detection
  - Nuclei integration with 5000+ templates
  - Custom vulnerability checks
- Intelligence integrations
  - Shodan API integration
  - VirusTotal integration
  - Censys integration (legacy format)
  - SecurityTrails integration
  - Hunter.io integration
  - GitHub dorking
- Reporting system
  - Professional report generation
  - CVSS v3.1 scoring
  - Multiple output formats (Markdown, PDF, JSON, HTML)
- Continuous monitoring
  - Asset change detection
  - Notification system
- Docker & Docker Compose setup
- Automated installation script
- Comprehensive documentation
- Web dashboard
- CI/CD pipeline with GitHub Actions

### Security
- Scope validation before scanning
- Rate limiting on all API calls
- Secure credential storage
- Docker network isolation

## [Unreleased]

### Planned
- Machine learning-based vulnerability prediction
- Advanced exploit chain detection
- Browser automation for complex scenarios
- Integration with more bug bounty platforms
- Real-time collaboration features
- Mobile app for monitoring
- Advanced reporting templates
- Custom payload generator
- Automated vulnerability validation
- Integration with CI/CD pipelines
- TLS/SSL configuration analysis (inspired by ExternalAttacker-MCP)
- Advanced DNS enumeration capabilities
- Directory and endpoint fuzzing integration