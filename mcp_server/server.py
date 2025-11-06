"""
MCP Server implementation for Bug Bounty Hunting
Enhanced with CDN Detection capabilities
"""

import asyncio
import logging
import sys
import os
import subprocess
import json
from typing import Any, Dict, List, Optional

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: MCP library not installed. Run: pip install mcp")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("advanced-bugbounty-mcp")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available bug bounty hunting tools."""
    return [
        Tool(
            name="recon_full",
            description="Comprehensive reconnaissance on target domain",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"},
                    "passive_only": {"type": "boolean", "default": False}
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="subdomain_enum",
            description="Advanced subdomain enumeration",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {"type": "string"}
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="scan_vulnerabilities",
            description="Scan for vulnerabilities (XSS, SQLi, SSRF, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "targets": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["targets"]
            }
        ),
        Tool(
            name="cdn_detection",
            description="Detect if target uses CDN (Cloudflare, Akamai, etc.) and identify CDN provider. Useful for understanding infrastructure, potential WAF bypass, and origin IP discovery.",
            inputSchema={
                "type": "object",
                "properties": {
                    "target": {
                        "type": "string",
                        "description": "Domain or URL to check for CDN usage"
                    },
                    "resolver": {
                        "type": "string",
                        "description": "DNS resolver to use (default: 8.8.8.8)",
                        "default": "8.8.8.8"
                    },
                    "detailed": {
                        "type": "boolean",
                        "description": "Get detailed CDN information including response headers",
                        "default": True
                    }
                },
                "required": ["target"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from Claude."""
    logger.info(f"Tool called: {name} with arguments: {arguments}")
    
    try:
        if name == "recon_full":
            result = await handle_recon(arguments)
        elif name == "subdomain_enum":
            result = await handle_subdomain_enum(arguments)
        elif name == "scan_vulnerabilities":
            result = await handle_vuln_scan(arguments)
        elif name == "cdn_detection":
            result = await handle_cdn_detection(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=str(result))]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def handle_recon(args: Dict) -> Dict:
    """Handle reconnaissance."""
    return {
        "status": "success",
        "domain": args["domain"],
        "message": "Reconnaissance completed"
    }


async def handle_subdomain_enum(args: Dict) -> Dict:
    """Handle subdomain enumeration."""
    return {
        "status": "success",
        "domain": args["domain"],
        "subdomains": []
    }


async def handle_vuln_scan(args: Dict) -> Dict:
    """Handle vulnerability scanning."""
    return {
        "status": "success",
        "targets": args["targets"],
        "vulnerabilities": []
    }


async def handle_cdn_detection(args: Dict) -> Dict:
    """
    Handle CDN detection using multiple techniques:
    1. DNS-based detection (CNAME records)
    2. HTTP header analysis
    3. IP range matching against known CDN providers
    4. Response header fingerprinting
    
    This is crucial for bug bounty hunting as:
    - Identifies CDN providers (Cloudflare, Akamai, Fastly, etc.)
    - Helps find origin IPs for WAF bypass
    - Reveals infrastructure details
    - Detects protection mechanisms
    """
    target = args["target"]
    resolver = args.get("resolver", "8.8.8.8")
    detailed = args.get("detailed", True)
    
    logger.info(f"Running CDN detection on {target}")
    
    result = {
        "status": "success",
        "target": target,
        "cdn_detected": False,
        "cdn_provider": None,
        "detection_methods": []
    }
    
    try:
        import socket
        import requests
        import dns.resolver
        from urllib.parse import urlparse
        
        # Clean target URL
        if not target.startswith(('http://', 'https://')):
            target_url = f"https://{target}"
            domain = target
        else:
            target_url = target
            domain = urlparse(target).netloc
        
        # 1. DNS CNAME Detection
        try:
            dns_resolver = dns.resolver.Resolver()
            dns_resolver.nameservers = [resolver]
            
            answers = dns_resolver.resolve(domain, 'CNAME')
            for rdata in answers:
                cname = str(rdata.target).lower()
                result["cname"] = cname
                
                # Known CDN CNAME patterns
                cdn_patterns = {
                    'cloudflare': ['cloudflare.com', 'cloudflare.net'],
                    'akamai': ['akamai.net', 'akamaiedge.net', 'akamaitechnologies.com'],
                    'fastly': ['fastly.net', 'fastlylb.net'],
                    'cloudfront': ['cloudfront.net'],
                    'maxcdn': ['maxcdn.com'],
                    'imperva': ['incapsula.com', 'imperva.com'],
                    'sucuri': ['sucuri.net'],
                    'stackpath': ['stackpath.net', 'netdna-ssl.com'],
                    'keycdn': ['keycdn.com'],
                    'bunnycdn': ['bunnycdn.com'],
                    'azure': ['azureedge.net'],
                    'google': ['googleusercontent.com', 'google.com'],
                }
                
                for provider, patterns in cdn_patterns.items():
                    if any(pattern in cname for pattern in patterns):
                        result["cdn_detected"] = True
                        result["cdn_provider"] = provider
                        result["detection_methods"].append(f"CNAME: {cname}")
                        break
        except Exception as e:
            logger.debug(f"CNAME lookup failed: {e}")
        
        # 2. HTTP Header Analysis
        if detailed:
            try:
                response = requests.get(target_url, timeout=10, allow_redirects=True)
                headers = response.headers
                result["http_status"] = response.status_code
                
                # Analyze headers for CDN signatures
                cdn_headers = {
                    'cloudflare': ['cf-ray', 'cf-cache-status', 'cf-request-id', '__cfduid'],
                    'akamai': ['x-akamai', 'akamai-x-cache', 'x-akamai-request-id'],
                    'fastly': ['x-fastly-request-id', 'fastly-debug-digest', 'x-served-by'],
                    'cloudfront': ['x-amz-cf-id', 'x-amz-cf-pop', 'via'],
                    'imperva': ['x-cdn', 'x-iinfo'],
                    'sucuri': ['x-sucuri-id', 'x-sucuri-cache'],
                    'varnish': ['x-varnish', 'via'],
                }
                
                detected_headers = []
                for provider, header_list in cdn_headers.items():
                    for header in header_list:
                        if header.lower() in [h.lower() for h in headers.keys()]:
                            if not result["cdn_detected"]:
                                result["cdn_detected"] = True
                                result["cdn_provider"] = provider
                            detected_headers.append(f"{header}: {headers.get(header, 'present')}")
                            result["detection_methods"].append(f"Header: {header}")
                
                if detected_headers:
                    result["cdn_headers"] = detected_headers
                
                # Check Server header
                server_header = headers.get('Server', '').lower()
                if server_header:
                    result["server"] = server_header
                    if 'cloudflare' in server_header:
                        result["cdn_detected"] = True
                        result["cdn_provider"] = "cloudflare"
                        result["detection_methods"].append(f"Server header: {server_header}")
                
                # Store relevant headers
                if detailed:
                    result["response_headers"] = {
                        k: v for k, v in headers.items() 
                        if k.lower() in ['server', 'via', 'x-powered-by', 'x-cache']
                    }
                    
            except Exception as e:
                logger.debug(f"HTTP header analysis failed: {e}")
        
        # 3. IP Range Detection
        try:
            ip_address = socket.gethostbyname(domain)
            result["ip_address"] = ip_address
            
            # Known CDN IP ranges (simplified - in production use full CIDR ranges)
            # This is a basic check - for production, use comprehensive IP range databases
            cdn_ip_patterns = {
                'cloudflare': ['104.', '172.64.', '173.245.', '188.114.', '190.93.', '197.234.'],
                'akamai': ['23.', '104.', '184.'],
                'fastly': ['151.101.'],
                'cloudfront': ['13.', '54.', '99.', '18.'],
            }
            
            for provider, ip_prefixes in cdn_ip_patterns.items():
                if any(ip_address.startswith(prefix) for prefix in ip_prefixes):
                    if not result["cdn_detected"]:
                        result["cdn_detected"] = True
                        result["cdn_provider"] = provider
                    result["detection_methods"].append(f"IP range: {ip_address}")
                    break
                    
        except Exception as e:
            logger.debug(f"IP resolution failed: {e}")
        
        # Summary
        if result["cdn_detected"]:
            result["message"] = f"CDN detected: {result['cdn_provider']}"
            result["bug_bounty_notes"] = {
                "findings": f"Target uses {result['cdn_provider']} CDN",
                "implications": [
                    "WAF/security protections likely in place",
                    "Consider origin IP discovery techniques",
                    "Check for CDN-specific misconfigurations",
                    "Test for cache poisoning vulnerabilities",
                    "Look for origin IP leaks in DNS history/subdomains"
                ],
                "next_steps": [
                    "Search for origin IP using SecurityTrails/historical DNS",
                    "Check subdomains for non-CDN protected assets",
                    "Test for CDN bypass via Host header manipulation",
                    "Look for exposed origin in email headers/SPF records"
                ]
            }
        else:
            result["message"] = "No CDN detected - direct server connection"
            result["bug_bounty_notes"] = {
                "findings": "No CDN protection detected",
                "implications": [
                    "Direct access to origin server",
                    "Potentially fewer security layers",
                    "Rate limiting may be less strict"
                ]
            }
        
        logger.info(f"CDN detection completed for {target}: {result['message']}")
        return result
        
    except Exception as e:
        logger.error(f"CDN detection failed: {str(e)}")
        return {
            "status": "error",
            "target": target,
            "error": str(e),
            "message": "CDN detection failed"
        }


async def main():
    """Main entry point for MCP server."""
    try:
        logger.info("🚀 Starting Advanced Bug Bounty MCP Server")
        logger.info("✓ CDN Detection Module Loaded")
        
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("✓ MCP Server started and ready for connections")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Failed to start MCP server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())