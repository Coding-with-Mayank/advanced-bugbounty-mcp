#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════
Advanced Bug Bounty MCP Server — server.py
Compatible with: Claude Desktop · Claude CLI · Gemini CLI · any MCP client

Tools exposed:
  Recon:     subdomain_enum, subdomain_brute, alive_check, port_scan,
             dns_enum, screenshot, crawl, wayback, tech_detect, full_recon
  Scanning:  nuclei_scan, dir_fuzz, xss_scan, sqli_scan, cors_check
  Intel:     whois_lookup, cert_search, shodan_search
  Analysis:  analyze_findings, get_next_steps, generate_report
  Utility:   list_tools, check_scope, explain_finding
═══════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import shutil
import socket
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Any

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .config import settings
from .guidance import GuidanceEngine

# ── Setup ─────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("bugbounty.server")

server = Server("bugbounty-hunter")
guide = GuidanceEngine()


# ── Subprocess Helpers ────────────────────────────────────────────────────────

async def run_cmd(
    cmd: list[str],
    timeout: int = 120,
    stdin: str | None = None,
) -> tuple[str, str, int]:
    """
    Run a CLI command async.
    Returns (stdout, stderr, returncode).
    Never raises — errors go into stderr.
    """
    binary = cmd[0]
    if not shutil.which(binary):
        msg = (
            f"Tool '{binary}' not found in PATH.\n"
            f"Fix: rebuild the Docker container with `docker-compose build --no-cache`\n"
            f"Or install manually: go install github.com/projectdiscovery/{binary}/..."
        )
        return "", msg, 127

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE if stdin else None,
        )
        input_bytes = stdin.encode() if stdin else None
        stdout, stderr = await asyncio.wait_for(proc.communicate(input_bytes), timeout=timeout)
        return (
            stdout.decode("utf-8", errors="replace"),
            stderr.decode("utf-8", errors="replace"),
            proc.returncode or 0,
        )
    except asyncio.TimeoutError:
        try:
            proc.kill()
        except Exception:
            pass
        return "", f"Command timed out after {timeout}s. Try increasing timeout or reducing scope.", -1
    except Exception as exc:
        return "", str(exc), -1


def lines(output: str) -> list[str]:
    return [l.strip() for l in output.splitlines() if l.strip()]


def is_valid_domain(domain: str) -> bool:
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain.strip()))


def sanitize(s: str) -> str:
    """Remove shell-injection characters from user input."""
    return re.sub(r"[;&|`$(){}]", "", s).strip()


def result(
    tool: str,
    target: str,
    data: Any,
    guidance_ctx: dict | None = None,
) -> dict:
    """Wrap tool output with metadata + guidance."""
    guidance_ctx = guidance_ctx or {}
    guidance_ctx.update({"tool": tool, "target": target, "data": data})
    return {
        "tool": tool,
        "target": target,
        "timestamp": datetime.utcnow().isoformat(),
        "data": data,
        "guidance": guide.generate(guidance_ctx),
    }


# ── Tool Schemas ──────────────────────────────────────────────────────────────

TOOLS: list[types.Tool] = [
    # ── Recon ────────────────────────────────────────────────────────────────
    types.Tool(
        name="subdomain_enum",
        description=(
            "Passively enumerate subdomains using subfinder (uses public APIs, crt.sh, etc). "
            "Returns subdomains + smart guidance on suspicious patterns and next steps."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {"type": "string", "description": "Target domain, e.g. example.com"},
                "timeout": {"type": "integer", "description": "Scan timeout seconds (default 60)"},
            },
            "required": ["domain"],
        },
    ),
    types.Tool(
        name="subdomain_brute",
        description=(
            "Actively brute-force subdomains using a wordlist (ffuf + DNS). "
            "More aggressive than passive enum — use only on targets you have permission to test."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "wordlist": {
                    "type": "string",
                    "description": "Path to wordlist (default: /app/wordlists/subdomains.txt)",
                },
                "threads": {"type": "integer", "description": "Concurrent threads (default 50)"},
            },
            "required": ["domain"],
        },
    ),
    types.Tool(
        name="alive_check",
        description=(
            "Probe a list of hosts/URLs with httpx. Returns status codes, titles, "
            "web servers, and detected technologies. Identifies interesting endpoints."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URLs or domains to probe",
                },
                "timeout": {"type": "integer", "description": "Per-request timeout (default 10)"},
            },
            "required": ["targets"],
        },
    ),
    types.Tool(
        name="port_scan",
        description=(
            "Fast TCP port scan using naabu. Discovers open services. "
            "Returns port list with service guesses and investigation hints."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "IP address or hostname"},
                "ports": {
                    "type": "string",
                    "description": "Port range (default: top-100). Examples: '80,443,8080', '1-1000', 'top-1000'",
                },
                "timeout": {"type": "integer"},
            },
            "required": ["target"],
        },
    ),
    types.Tool(
        name="dns_enum",
        description="Enumerate DNS records (A, MX, NS, TXT, CNAME, SOA) for a domain using dnsx.",
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
            },
            "required": ["domain"],
        },
    ),
    types.Tool(
        name="screenshot",
        description=(
            "Take screenshots of web targets using gowitness. "
            "Screenshots saved to /app/screenshots/. Returns file paths + interesting observations."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of URLs to screenshot",
                },
                "timeout": {"type": "integer", "description": "Per-page timeout (default 15)"},
            },
            "required": ["targets"],
        },
    ),
    types.Tool(
        name="crawl",
        description=(
            "Crawl a website with katana to discover URLs, forms, JS files, and API endpoints. "
            "Great for finding hidden functionality."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "Starting URL"},
                "depth": {"type": "integer", "description": "Crawl depth (default 3)"},
                "timeout": {"type": "integer"},
            },
            "required": ["url"],
        },
    ),
    types.Tool(
        name="wayback",
        description=(
            "Retrieve historical URLs from Wayback Machine + gau. "
            "Useful for finding old endpoints, backup files, and forgotten parameters."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
            },
            "required": ["domain"],
        },
    ),
    types.Tool(
        name="tech_detect",
        description=(
            "Detect web technologies (frameworks, CDNs, CMS, servers) using httpx. "
            "Returns technology stack with known vulnerability hints."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["targets"],
        },
    ),
    types.Tool(
        name="full_recon",
        description=(
            "Run a complete automated recon pipeline on a domain: "
            "subdomain_enum → alive_check → port_scan → tech_detect → screenshot. "
            "Best starting point for a new target."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "screenshot": {"type": "boolean", "description": "Take screenshots (default true)"},
            },
            "required": ["domain"],
        },
    ),
    # ── Scanning ─────────────────────────────────────────────────────────────
    types.Tool(
        name="nuclei_scan",
        description=(
            "Run Nuclei vulnerability scanner with 10,000+ templates. "
            "Filter by severity. Returns findings with CVSSv3 scores and remediation guidance."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}},
                "severity": {
                    "type": "string",
                    "description": "Comma-separated severities: info,low,medium,high,critical (default: medium,high,critical)",
                },
                "templates": {
                    "type": "string",
                    "description": "Template tag or path (e.g. 'cve', 'misconfig', 'xss'). Blank = all.",
                },
                "timeout": {"type": "integer"},
            },
            "required": ["targets"],
        },
    ),
    types.Tool(
        name="dir_fuzz",
        description=(
            "Directory and file fuzzing with ffuf. Finds hidden paths, backup files, admin panels. "
            "Returns discovered paths with response analysis."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Target URL. FUZZ keyword optional (inserted at end if absent).",
                },
                "wordlist": {
                    "type": "string",
                    "description": "Wordlist path (default: /app/wordlists/directories.txt)",
                },
                "extensions": {
                    "type": "string",
                    "description": "File extensions to try, e.g. 'php,asp,bak,old'",
                },
                "threads": {"type": "integer"},
                "timeout": {"type": "integer"},
            },
            "required": ["url"],
        },
    ),
    types.Tool(
        name="xss_scan",
        description=(
            "Targeted XSS scanning using Nuclei XSS templates. "
            "Returns potential XSS vectors with PoC details and manual verification steps."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["targets"],
        },
    ),
    types.Tool(
        name="sqli_scan",
        description=(
            "SQL injection scanning using Nuclei SQLi templates. "
            "Returns potential injection points with evidence and manual testing steps."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["targets"],
        },
    ),
    types.Tool(
        name="cors_check",
        description=(
            "Check for CORS misconfigurations. "
            "Returns misconfigured endpoints with exploitation steps."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "targets": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["targets"],
        },
    ),
    # ── Intelligence ──────────────────────────────────────────────────────────
    types.Tool(
        name="whois_lookup",
        description="Retrieve WHOIS data for a domain or IP. Useful for identifying organization, registrar, and contact info.",
        inputSchema={
            "type": "object",
            "properties": {
                "target": {"type": "string", "description": "Domain or IP address"},
            },
            "required": ["target"],
        },
    ),
    types.Tool(
        name="cert_search",
        description=(
            "Search certificate transparency logs (crt.sh) for a domain. "
            "Often reveals subdomains that passive tools miss."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
            },
            "required": ["domain"],
        },
    ),
    types.Tool(
        name="shodan_search",
        description=(
            "Query Shodan for internet-exposed services. "
            "Requires SHODAN_API_KEY in .env. Returns open ports, banners, CVEs."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Shodan query e.g. 'hostname:example.com'"},
            },
            "required": ["query"],
        },
    ),
    # ── Analysis ──────────────────────────────────────────────────────────────
    types.Tool(
        name="analyze_findings",
        description=(
            "Analyze a collection of raw findings and get prioritized report: "
            "what's critical, what needs manual verification, and a full attack chain suggestion."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "findings": {
                    "type": "array",
                    "items": {"type": "object"},
                    "description": "List of finding objects from other tool calls",
                },
                "target": {"type": "string"},
            },
            "required": ["findings"],
        },
    ),
    types.Tool(
        name="explain_finding",
        description=(
            "Explain what a specific finding means, its severity, how to manually verify it, "
            "and how to write it up for a bug bounty report."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "finding": {
                    "type": "object",
                    "description": "A single finding object (from nuclei_scan, xss_scan, etc.)",
                },
            },
            "required": ["finding"],
        },
    ),
    types.Tool(
        name="generate_report",
        description="Generate a professional Markdown bug bounty report from collected findings.",
        inputSchema={
            "type": "object",
            "properties": {
                "target": {"type": "string"},
                "findings": {"type": "array", "items": {"type": "object"}},
                "program_name": {"type": "string"},
            },
            "required": ["target", "findings"],
        },
    ),
]


# ── Tool Registration ─────────────────────────────────────────────────────────

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    args = arguments or {}
    dispatch = {
        "subdomain_enum":   _subdomain_enum,
        "subdomain_brute":  _subdomain_brute,
        "alive_check":      _alive_check,
        "port_scan":        _port_scan,
        "dns_enum":         _dns_enum,
        "screenshot":       _screenshot,
        "crawl":            _crawl,
        "wayback":          _wayback,
        "tech_detect":      _tech_detect,
        "full_recon":       _full_recon,
        "nuclei_scan":      _nuclei_scan,
        "dir_fuzz":         _dir_fuzz,
        "xss_scan":         _xss_scan,
        "sqli_scan":        _sqli_scan,
        "cors_check":       _cors_check,
        "whois_lookup":     _whois_lookup,
        "cert_search":      _cert_search,
        "shodan_search":    _shodan_search,
        "analyze_findings": _analyze_findings,
        "explain_finding":  _explain_finding,
        "generate_report":  _generate_report,
    }

    handler = dispatch.get(name)
    if not handler:
        res = {"error": f"Unknown tool '{name}'", "available": list(dispatch.keys())}
        return [types.TextContent(type="text", text=json.dumps(res, indent=2))]

    try:
        res = await handler(args)
        return [types.TextContent(type="text", text=json.dumps(res, indent=2, default=str))]
    except Exception as exc:
        logger.exception(f"Tool '{name}' raised unhandled exception")
        err = {
            "error": str(exc),
            "tool": name,
            "guidance": guide.generate({"tool": name, "error": str(exc)}),
        }
        return [types.TextContent(type="text", text=json.dumps(err, indent=2))]


# ── Recon Handlers ────────────────────────────────────────────────────────────

async def _subdomain_enum(args: dict) -> dict:
    domain = sanitize(args.get("domain", ""))
    if not domain:
        return {"error": "domain is required"}
    timeout = int(args.get("timeout", 60))

    stdout, stderr, rc = await run_cmd(
        ["subfinder", "-d", domain, "-silent", "-all", "-recursive"],
        timeout=timeout,
    )

    subs = sorted(set(lines(stdout)))
    suspicious = guide.flag_suspicious_subdomains(subs)

    return result(
        "subdomain_enum", domain,
        {"count": len(subs), "subdomains": subs, "suspicious": suspicious},
        {"found": len(subs), "stderr": stderr},
    )


async def _subdomain_brute(args: dict) -> dict:
    """
    DNS-based subdomain brute-force using gobuster dns.
    Resolves each candidate via DNS — catches subdomains regardless of
    whether they serve HTTP/HTTPS, unlike HTTP-based approaches.
    """
    domain = sanitize(args.get("domain", ""))
    wordlist = args.get("wordlist", "/app/wordlists/subdomains.txt")
    threads = int(args.get("threads", 50))

    if not Path(wordlist).exists():
        return {
            "error": f"Wordlist not found: {wordlist}",
            "guidance": {
                "next_steps": [
                    "Run setup.sh — it downloads wordlists automatically",
                    "Or manually: wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-20000.txt -O /app/wordlists/subdomains.txt",
                ]
            },
        }

    # gobuster dns — resolves each candidate subdomain via DNS.
    # Much more accurate than HTTP-based ffuf for subdomain discovery.
    stdout, stderr, rc = await run_cmd(
        [
            "gobuster", "dns",
            "-d", domain,
            "-w", wordlist,
            "-t", str(threads),
            "--no-color",
            "-q",                # quiet: only show found subdomains
        ],
        timeout=300,
    )

    # gobuster dns output format: "Found: sub.domain.com"
    found = []
    for line in lines(stdout):
        line = line.strip()
        if line.startswith("Found:"):
            sub = line.replace("Found:", "").strip()
            if sub:
                found.append(sub)
        elif domain in line and not line.startswith("["):
            # fallback: grab any line containing the domain
            found.append(line.strip())

    found = sorted(set(found))
    suspicious = guide.flag_suspicious_subdomains(found)

    return result(
        "subdomain_brute", domain,
        {"count": len(found), "subdomains": found, "suspicious": suspicious},
        {"found": len(found)},
    )


async def _alive_check(args: dict) -> dict:
    targets = args.get("targets", [])
    timeout_s = int(args.get("timeout", 10))
    if not targets:
        return {"error": "targets list is required"}

    # Write targets to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(targets))
        tmp = f.name

    stdout, stderr, rc = await run_cmd(
        [
            "httpx", "-l", tmp,
            "-silent",
            "-status-code", "-title", "-tech-detect",
            "-web-server", "-content-length",
            "-follow-redirects",
            "-timeout", str(timeout_s),
            "-json",
        ],
        timeout=120,
    )
    Path(tmp).unlink(missing_ok=True)

    alive = []
    interesting = []
    for line in lines(stdout):
        try:
            obj = json.loads(line)
            alive.append(obj)
            if _is_interesting(obj):
                interesting.append(obj)
        except json.JSONDecodeError:
            pass

    return result(
        "alive_check", str(targets[:3]) + "...",
        {"count": len(alive), "hosts": alive, "interesting": interesting},
        {"alive_count": len(alive), "interesting_count": len(interesting)},
    )


def _is_interesting(httpx_obj: dict) -> bool:
    title = (httpx_obj.get("title") or "").lower()
    interesting_keywords = [
        "admin", "dashboard", "login", "portal", "manager", "console",
        "swagger", "api", "phpmyadmin", "jenkins", "grafana", "kibana",
        "test", "staging", "dev", "debug", "error", "exception",
    ]
    return any(kw in title for kw in interesting_keywords)


async def _port_scan(args: dict) -> dict:
    target = sanitize(args.get("target", ""))
    ports = args.get("ports", "")
    timeout = int(args.get("timeout", 120))

    cmd = ["naabu", "-host", target, "-silent", "-json"]
    if ports and ports != "top-100":
        if ports.startswith("top-"):
            cmd += ["-top-ports", ports[4:]]
        else:
            cmd += ["-p", ports]
    else:
        cmd += ["-top-ports", "100"]

    stdout, stderr, rc = await run_cmd(cmd, timeout=timeout)

    open_ports = []
    for line in lines(stdout):
        try:
            obj = json.loads(line)
            open_ports.append({"port": obj.get("port"), "protocol": obj.get("protocol", "tcp")})
        except json.JSONDecodeError:
            pass

    return result(
        "port_scan", target,
        {"count": len(open_ports), "ports": open_ports},
        {"ports": [p["port"] for p in open_ports]},
    )


async def _dns_enum(args: dict) -> dict:
    domain = sanitize(args.get("domain", ""))
    record_types = ["a", "mx", "ns", "txt", "cname", "soa", "aaaa"]

    stdout, stderr, rc = await run_cmd(
        ["dnsx", "-d", domain, "-silent", "-json", "-resp",
         "-a", "-mx", "-ns", "-txt", "-cname", "-soa"],
        timeout=60,
    )

    records: dict[str, list] = {}
    for line in lines(stdout):
        try:
            obj = json.loads(line)
            rtype = obj.get("type", "unknown").upper()
            records.setdefault(rtype, []).append(obj.get("value", obj.get("resp")))
        except json.JSONDecodeError:
            pass

    return result(
        "dns_enum", domain,
        {"records": records},
        {"record_types": list(records.keys())},
    )


async def _screenshot(args: dict) -> dict:
    targets = args.get("targets", [])
    timeout_s = int(args.get("timeout", 15))
    if not targets:
        return {"error": "targets required"}

    out_dir = Path("/app/screenshots")
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(targets))
        tmp = f.name

    # Try gowitness first, fall back to httpx screenshot
    screenshots = []
    if shutil.which("gowitness"):
        _, stderr, rc = await run_cmd(
            [
                "gowitness", "file",
                "-f", tmp,
                "--screenshot-path", str(out_dir),
                "--timeout", str(timeout_s),
                "--disable-db",
            ],
            timeout=timeout_s * len(targets) + 30,
        )
        for t in targets:
            # gowitness names files by URL slug
            slug = re.sub(r"[^a-zA-Z0-9._-]", "_", t.replace("://", "_"))
            candidates = list(out_dir.glob(f"*{slug[:30]}*"))
            if candidates:
                screenshots.append({"url": t, "file": str(candidates[0])})
            else:
                screenshots.append({"url": t, "file": None, "note": "screenshot may not have rendered"})
    else:
        # Fallback: httpx with screenshot flag (needs Chrome)
        _, stderr, rc = await run_cmd(
            ["httpx", "-l", tmp, "-screenshot", "-srd", str(out_dir), "-silent"],
            timeout=timeout_s * len(targets) + 30,
        )
        for f2 in out_dir.iterdir():
            if f2.suffix == ".png":
                screenshots.append({"file": str(f2)})

    Path(tmp).unlink(missing_ok=True)

    return result(
        "screenshot", str(targets[:3]),
        {"screenshots": screenshots, "output_dir": str(out_dir)},
        {"count": len(screenshots)},
    )


async def _crawl(args: dict) -> dict:
    url = args.get("url", "")
    depth = int(args.get("depth", 3))
    timeout = int(args.get("timeout", 120))

    stdout, stderr, rc = await run_cmd(
        ["katana", "-u", url, "-d", str(depth), "-silent",
         "-jc", "-fx", "-kf", "all"],
        timeout=timeout,
    )

    urls_found = lines(stdout)
    js_files = [u for u in urls_found if u.endswith(".js")]
    api_paths = [u for u in urls_found if "/api/" in u or "/v1/" in u or "/v2/" in u]
    interesting = [u for u in urls_found if any(kw in u for kw in
        ["admin", "config", "backup", "secret", ".env", "swagger", "upload", "debug"])]

    return result(
        "crawl", url,
        {
            "total_urls": len(urls_found),
            "all_urls": urls_found[:200],  # cap output
            "js_files": js_files,
            "api_paths": api_paths,
            "interesting": interesting,
        },
        {"total": len(urls_found), "interesting_count": len(interesting)},
    )


async def _wayback(args: dict) -> dict:
    domain = sanitize(args.get("domain", ""))

    # Run waybackurls and gau in parallel
    wb_task = run_cmd(["waybackurls", domain], timeout=90)
    gau_task = run_cmd(["gau", "--subs", domain], timeout=90)
    (wb_out, _, _), (gau_out, _, _) = await asyncio.gather(wb_task, gau_task)

    all_urls = sorted(set(lines(wb_out) + lines(gau_out)))
    interesting = [u for u in all_urls if any(ext in u for ext in
        [".bak", ".old", ".zip", ".tar", ".sql", ".log", ".env", ".config",
         "backup", "debug", "secret", "password", "token", "key", "admin"])]

    return result(
        "wayback", domain,
        {
            "total": len(all_urls),
            "urls": all_urls[:300],
            "interesting": interesting,
        },
        {"total": len(all_urls), "interesting": len(interesting)},
    )


async def _tech_detect(args: dict) -> dict:
    targets = args.get("targets", [])
    if not targets:
        return {"error": "targets required"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(targets))
        tmp = f.name

    stdout, stderr, rc = await run_cmd(
        ["httpx", "-l", tmp, "-silent", "-tech-detect", "-json", "-timeout", "10"],
        timeout=120,
    )
    Path(tmp).unlink(missing_ok=True)

    tech_map = {}
    for line in lines(stdout):
        try:
            obj = json.loads(line)
            url = obj.get("url", obj.get("input"))
            techs = obj.get("technologies", obj.get("tech", []))
            if url and techs:
                tech_map[url] = techs
        except json.JSONDecodeError:
            pass

    return result(
        "tech_detect", str(targets[:3]),
        {"technology_map": tech_map},
        {"tech_map": tech_map},
    )


async def _full_recon(args: dict) -> dict:
    domain = sanitize(args.get("domain", ""))
    do_screenshots = args.get("screenshot", True)
    if not domain:
        return {"error": "domain required"}

    pipeline = {}

    # Step 1: Subdomain enum
    pipeline["subdomains"] = await _subdomain_enum({"domain": domain})
    subs = pipeline["subdomains"].get("data", {}).get("subdomains", [])

    # Step 2: Alive check
    if subs:
        https_subs = [f"https://{s}" for s in subs[:100]]  # cap at 100 for speed
        pipeline["alive"] = await _alive_check({"targets": https_subs})
        alive_hosts = [h.get("url") for h in pipeline["alive"].get("data", {}).get("hosts", []) if h.get("url")]
    else:
        alive_hosts = [f"https://{domain}"]

    # Step 3: Port scan on main domain
    pipeline["ports"] = await _port_scan({"target": domain})

    # Step 4: Tech detect on alive hosts
    if alive_hosts:
        pipeline["tech"] = await _tech_detect({"targets": alive_hosts[:20]})

    # Step 5: Screenshots
    if do_screenshots and alive_hosts:
        pipeline["screenshots"] = await _screenshot({"targets": alive_hosts[:15], "timeout": 10})

    return {
        "tool": "full_recon",
        "target": domain,
        "timestamp": datetime.utcnow().isoformat(),
        "pipeline": pipeline,
        "guidance": guide.generate({
            "tool": "full_recon",
            "target": domain,
            "subdomains": len(subs),
            "alive": len(alive_hosts),
        }),
    }


# ── Scanning Handlers ─────────────────────────────────────────────────────────

async def _nuclei_scan(args: dict) -> dict:
    targets = args.get("targets", [])
    severity = args.get("severity", "medium,high,critical")
    templates = args.get("templates", "")
    timeout = int(args.get("timeout", 300))

    if not targets:
        return {"error": "targets required"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(targets))
        tmp = f.name

    cmd = [
        "nuclei", "-l", tmp,
        "-severity", severity,
        "-silent", "-json",
        "-rate-limit", "50",
        "-bulk-size", "25",
    ]
    if templates:
        cmd += ["-tags", templates]

    stdout, stderr, rc = await run_cmd(cmd, timeout=timeout)
    Path(tmp).unlink(missing_ok=True)

    findings = []
    for line in lines(stdout):
        try:
            obj = json.loads(line)
            findings.append({
                "template_id": obj.get("template-id"),
                "name": obj.get("info", {}).get("name"),
                "severity": obj.get("info", {}).get("severity"),
                "cvss": obj.get("info", {}).get("classification", {}).get("cvss-score"),
                "url": obj.get("matched-at", obj.get("host")),
                "description": obj.get("info", {}).get("description"),
                "reference": obj.get("info", {}).get("reference", []),
                "matcher_name": obj.get("matcher-name"),
                "extracted_results": obj.get("extracted-results", []),
            })
        except json.JSONDecodeError:
            pass

    by_severity: dict[str, list] = {}
    for f3 in findings:
        sev = f3.get("severity", "unknown")
        by_severity.setdefault(sev, []).append(f3)

    return result(
        "nuclei_scan", str(targets[:3]),
        {
            "total": len(findings),
            "by_severity": by_severity,
            "findings": findings,
        },
        {"total": len(findings), "severities": {k: len(v) for k, v in by_severity.items()}},
    )


async def _dir_fuzz(args: dict) -> dict:
    url = args.get("url", "")
    wordlist = args.get("wordlist", "/app/wordlists/directories.txt")
    extensions = args.get("extensions", "")
    threads = int(args.get("threads", 50))
    timeout = int(args.get("timeout", 180))

    if not Path(wordlist).exists():
        return {
            "error": f"Wordlist missing: {wordlist}",
            "guidance": {"next_steps": [
                "Run setup.sh to download wordlists automatically",
                "Or: wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt -O /app/wordlists/directories.txt"
            ]}
        }

    fuzz_url = url if "FUZZ" in url else url.rstrip("/") + "/FUZZ"
    cmd = [
        "ffuf", "-u", fuzz_url,
        "-w", wordlist,
        "-t", str(threads),
        "-mc", "200,201,204,301,302,307,401,403,405",
        "-ac",  # auto-calibrate to filter false positives
        "-json",
    ]
    if extensions:
        cmd += ["-e", "." + extensions.replace(",", ",.")]

    stdout, stderr, rc = await run_cmd(cmd, timeout=timeout)

    results_list = []
    try:
        data = json.loads(stdout)
        results_list = data.get("results", [])
    except json.JSONDecodeError:
        for line in lines(stdout):
            try:
                obj = json.loads(line)
                results_list.append(obj)
            except Exception:
                pass

    filtered = [
        {
            "url": r.get("url"),
            "status": r.get("status"),
            "length": r.get("length"),
            "words": r.get("words"),
            "lines": r.get("lines"),
        }
        for r in results_list
    ]

    return result(
        "dir_fuzz", url,
        {"count": len(filtered), "paths": filtered},
        {"found": len(filtered)},
    )


async def _nuclei_targeted(target_tag: str, args: dict) -> dict:
    targets = args.get("targets", [])
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("\n".join(targets))
        tmp = f.name

    stdout, stderr, rc = await run_cmd(
        ["nuclei", "-l", tmp, "-tags", target_tag, "-silent", "-json", "-rate-limit", "30"],
        timeout=180,
    )
    Path(tmp).unlink(missing_ok=True)

    findings = []
    for line in lines(stdout):
        try:
            findings.append(json.loads(line))
        except Exception:
            pass

    return result(
        f"{target_tag}_scan", str(targets[:3]),
        {"count": len(findings), "findings": findings},
        {"count": len(findings), "tag": target_tag},
    )


async def _xss_scan(args: dict) -> dict:
    return await _nuclei_targeted("xss", args)


async def _sqli_scan(args: dict) -> dict:
    return await _nuclei_targeted("sqli", args)


async def _cors_check(args: dict) -> dict:
    return await _nuclei_targeted("cors", args)


# ── Intelligence Handlers ─────────────────────────────────────────────────────

async def _whois_lookup(args: dict) -> dict:
    target = sanitize(args.get("target", ""))
    stdout, stderr, rc = await run_cmd(["whois", target], timeout=30)
    return result(
        "whois_lookup", target,
        {"raw": stdout, "error": stderr if rc != 0 else None},
        {},
    )


async def _cert_search(args: dict) -> dict:
    domain = sanitize(args.get("domain", ""))
    import httpx as _httpx
    try:
        async with _httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"https://crt.sh/?q=%.{domain}&output=json"
            )
            data = resp.json()
    except Exception as e:
        return {"error": str(e), "guidance": guide.generate({"tool": "cert_search", "error": str(e)})}

    names = sorted(set(
        entry.get("name_value", "").replace("*.", "")
        for entry in data
        if entry.get("name_value")
    ))
    unique_domains = [n for n in names if domain in n and "\n" not in n]

    return result(
        "cert_search", domain,
        {"count": len(unique_domains), "domains": unique_domains},
        {"found": len(unique_domains)},
    )


async def _shodan_search(args: dict) -> dict:
    query = args.get("query", "")
    api_key = settings.shodan_api_key
    if not api_key:
        return {
            "error": "SHODAN_API_KEY not set",
            "guidance": {
                "manual_alternative": [
                    f"Visit https://www.shodan.io/search?query={query}",
                    "Create a free account at shodan.io for API access",
                    "Add SHODAN_API_KEY=your_key to .env and restart",
                ]
            },
        }

    import httpx as _httpx
    try:
        async with _httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://api.shodan.io/shodan/host/search",
                params={"key": api_key, "query": query, "minify": True},
            )
            data = resp.json()
    except Exception as e:
        return {"error": str(e)}

    return result(
        "shodan_search", query,
        {
            "total": data.get("total", 0),
            "matches": data.get("matches", [])[:20],
        },
        {"total": data.get("total", 0)},
    )


# ── Analysis Handlers ─────────────────────────────────────────────────────────

async def _analyze_findings(args: dict) -> dict:
    findings = args.get("findings", [])
    target = args.get("target", "unknown")

    analysis = guide.analyze_collection(findings, target)
    return {
        "tool": "analyze_findings",
        "target": target,
        "timestamp": datetime.utcnow().isoformat(),
        "analysis": analysis,
    }


async def _explain_finding(args: dict) -> dict:
    finding = args.get("finding", {})
    explanation = guide.explain(finding)
    return {
        "tool": "explain_finding",
        "finding": finding,
        "explanation": explanation,
    }


async def _generate_report(args: dict) -> dict:
    target = args.get("target", "unknown")
    findings = args.get("findings", [])
    program = args.get("program_name", "Bug Bounty Program")

    report = guide.render_report(target, findings, program)
    report_path = Path(f"/app/reports/report_{target}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report)

    return {
        "tool": "generate_report",
        "report_path": str(report_path),
        "report": report,
    }


# ── Health API (port 8080) ────────────────────────────────────────────────────
# Runs in a background daemon thread so port 8080 is actually useful.
# Provides container health, tool availability, and basic stats.

def _start_health_server() -> None:
    """Start a minimal FastAPI server on :8080 in a background thread."""
    try:
        import uvicorn
        from fastapi import FastAPI
        from fastapi.responses import JSONResponse

        health_app = FastAPI(title="Bug Bounty MCP", version="3.0.0", docs_url=None)
        _start_time = datetime.utcnow()

        @health_app.get("/health")
        def health():
            tools_present = {
                t: bool(shutil.which(t))
                for t in ["subfinder", "httpx", "nuclei", "naabu", "katana",
                          "dnsx", "waybackurls", "gau", "ffuf", "gobuster",
                          "gowitness", "anew"]
            }
            missing = [t for t, ok in tools_present.items() if not ok]
            return JSONResponse({
                "status": "ok" if not missing else "degraded",
                "version": "3.0.0",
                "uptime_seconds": int((datetime.utcnow() - _start_time).total_seconds()),
                "mcp_tools": len(TOOLS),
                "go_tools": {
                    "available": sum(tools_present.values()),
                    "total": len(tools_present),
                    "missing": missing,
                },
            })

        @health_app.get("/tools")
        def list_mcp_tools():
            return JSONResponse({
                "count": len(TOOLS),
                "tools": [{"name": t.name, "description": t.description[:80]} for t in TOOLS],
            })

        uvicorn.run(health_app, host="0.0.0.0", port=8080, log_level="error", access_log=False)
    except Exception as exc:
        # Health server is non-critical — MCP stdio still works without it
        logger.warning(f"Health server on :8080 failed to start: {exc}")


# ── Entry point ───────────────────────────────────────────────────────────────

async def main() -> None:
    logger.info("Bug Bounty MCP Server v3.0.0 — Claude · Gemini · any MCP client")

    # Start health/status API on :8080 in background (non-blocking)
    health_thread = threading.Thread(target=_start_health_server, daemon=True)
    health_thread.start()
    logger.info("Health API starting on http://0.0.0.0:8080/health")

    # Run MCP protocol on stdio (this is the main loop)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
