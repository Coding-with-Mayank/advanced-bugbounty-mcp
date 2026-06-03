#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
  hunt.py — Manual Bug Bounty CLI
  Works standalone: no Docker, no MCP client needed.
  Just run: python hunt.py <command> [options]

  Usage examples:
    python hunt.py recon example.com
    python hunt.py scan example.com --severity high,critical
    python hunt.py fuzz https://example.com/FUZZ
    python hunt.py full example.com
    python hunt.py cert example.com
    python hunt.py wayback example.com
    python hunt.py screenshot https://example.com
═══════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import asyncio
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import print as rprint
    RICH = True
except ImportError:
    RICH = False

console = Console() if RICH else None


# ── Colours for non-rich fallback ────────────────────────────────────────────

def c(text: str, color: str) -> str:
    colors = {"red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m",
              "blue": "\033[94m", "cyan": "\033[96m", "bold": "\033[1m", "reset": "\033[0m"}
    return f"{colors.get(color, '')}{text}{colors['reset']}"


def banner():
    print(c("""
  ██████╗ ██╗   ██╗ ██████╗     ██████╗  ██████╗ ██╗   ██╗███╗   ██╗████████╗██╗   ██╗
  ██╔══██╗██║   ██║██╔════╝     ██╔══██╗██╔═══██╗██║   ██║████╗  ██║╚══██╔══╝╚██╗ ██╔╝
  ██████╔╝██║   ██║██║  ███╗    ██████╔╝██║   ██║██║   ██║██╔██╗ ██║   ██║    ╚████╔╝
  ██╔══██╗██║   ██║██║   ██║    ██╔══██╗██║   ██║██║   ██║██║╚██╗██║   ██║     ╚██╔╝
  ██████╔╝╚██████╔╝╚██████╔╝    ██████╔╝╚██████╔╝╚██████╔╝██║ ╚████║   ██║      ██║
  ╚═════╝  ╚═════╝  ╚═════╝     ╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝   ╚═╝      ╚═╝
  Manual Bug Bounty CLI — v3.0.0
  ⚠️  Only test targets you have explicit permission to test.
""", "cyan"))


def check_tools():
    """Check which tools are available and warn about missing ones."""
    tools = {
        "subfinder": "passive subdomain enum",
        "httpx":     "alive check + tech detect",
        "naabu":     "port scanner",
        "nuclei":    "vulnerability scanner",
        "ffuf":      "directory/param fuzzer",
        "katana":    "web crawler",
        "waybackurls": "historical URLs",
        "gau":       "URL fetcher",
        "dnsx":      "DNS enumeration",
        "gowitness": "web screenshots",
        "gobuster":  "brute-force enumeration",
        "anew":      "deduplication",
    }
    available = {}
    missing = []
    for tool, desc in tools.items():
        if shutil.which(tool):
            available[tool] = desc
        else:
            missing.append((tool, desc))

    if missing:
        print(c(f"\n⚠  Missing tools ({len(missing)}/{len(tools)}):", "yellow"))
        for t, d in missing:
            print(c(f"   ✗ {t:<15}", "red") + f"  ({d})")
        print(c("\n  → Quickest fix: use Docker instead:", "yellow"))
        print(c("    docker-compose up -d\n    docker exec -it bugbounty-mcp bash\n", "cyan"))
    else:
        print(c(f"\n✓  All {len(tools)} tools available\n", "green"))

    return available


async def run(cmd: list[str], timeout: int = 120) -> tuple[str, str]:
    """Run command, return (stdout, stderr)."""
    if not shutil.which(cmd[0]):
        return "", f"Tool '{cmd[0]}' not found. Run: ./setup.sh"
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        out, err = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return out.decode(errors="replace"), err.decode(errors="replace")
    except asyncio.TimeoutError:
        return "", f"Timed out after {timeout}s"
    except Exception as e:
        return "", str(e)


def save_output(name: str, data: str | dict, target: str) -> Path:
    """Save output to ./output/<target>/ directory."""
    out_dir = Path(f"output/{target.replace('/', '_')}")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    fpath = out_dir / f"{name}_{ts}.{'json' if isinstance(data, dict) else 'txt'}"
    content = json.dumps(data, indent=2) if isinstance(data, dict) else data
    fpath.write_text(content)
    return fpath


# ── Commands ──────────────────────────────────────────────────────────────────

async def cmd_recon(domain: str, **kwargs):
    """Passive subdomain recon with subfinder + cert transparency."""
    print(c(f"\n[*] Subdomain Enum: {domain}", "cyan"))

    # subfinder
    out, err = await run(["subfinder", "-d", domain, "-silent", "-all"], timeout=60)
    subs_subfinder = [l.strip() for l in out.splitlines() if l.strip()]

    # crt.sh
    crt_subs = []
    try:
        import urllib.request, json as _json
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = _json.loads(r.read())
            for entry in data:
                val = entry.get("name_value", "")
                for v in val.splitlines():
                    v = v.strip().lstrip("*.")
                    if domain in v and v not in crt_subs:
                        crt_subs.append(v)
    except Exception as e:
        print(c(f"  crt.sh failed: {e}", "yellow"))

    all_subs = sorted(set(subs_subfinder + crt_subs))
    print(c(f"\n  Found {len(all_subs)} unique subdomains", "green"))
    print(c(f"  subfinder: {len(subs_subfinder)}  crt.sh: {len(crt_subs)}", "blue"))

    # Flag suspicious ones
    suspicious_prefixes = ["dev", "staging", "admin", "api", "internal", "test", "jenkins",
                           "gitlab", "grafana", "kibana", "elastic", "backup", "old", "vpn"]
    suspicious = [s for s in all_subs if any(s.startswith(p + ".") for p in suspicious_prefixes)]

    if suspicious:
        print(c(f"\n  🚨 Suspicious subdomains ({len(suspicious)}):", "red"))
        for s in suspicious:
            print(c(f"    ★ {s}", "yellow"))

    print(c("\n  All subdomains:", "blue"))
    for s in all_subs:
        print(f"    {s}")

    saved = save_output("subdomains", "\n".join(all_subs), domain)
    print(c(f"\n  Saved → {saved}", "green"))

    print(c("\n  Next steps:", "cyan"))
    print("    python hunt.py alive " + domain + " --list " + str(saved))
    print("    python hunt.py cert " + domain)
    print(f"    Check: https://www.virustotal.com/gui/domain/{domain}/relations")


async def cmd_alive(domain: str, list_file: str | None = None, **kwargs):
    """Check which subdomains are alive using httpx."""
    print(c(f"\n[*] Alive Check: {domain}", "cyan"))

    if list_file and Path(list_file).exists():
        targets_file = list_file
        print(c(f"  Using list: {list_file}", "blue"))
    else:
        # Quick subfinder first
        out, _ = await run(["subfinder", "-d", domain, "-silent"], timeout=45)
        subs = [l.strip() for l in out.splitlines() if l.strip()]
        if not subs:
            print(c("  No subdomains found. Try: python hunt.py recon " + domain, "yellow"))
            return
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("\n".join(f"https://{s}" for s in subs))
            targets_file = f.name

    out, err = await run(
        ["httpx", "-l", targets_file, "-silent", "-status-code",
         "-title", "-tech-detect", "-web-server", "-timeout", "10"],
        timeout=120,
    )

    lines = [l for l in out.splitlines() if l.strip()]
    print(c(f"\n  Alive hosts ({len(lines)}):\n", "green"))

    for line in lines:
        color = "red" if "[200]" in line else "yellow" if "[30" in line else "blue"
        print(c(f"    {line}", color))

    saved = save_output("alive", "\n".join(lines), domain)
    print(c(f"\n  Saved → {saved}", "green"))
    print(c("\n  Next steps:", "cyan"))
    print(f"    python hunt.py scan {domain}")
    print(f"    python hunt.py fuzz https://{domain}/FUZZ")
    print(f"    python hunt.py screenshot {domain} --list {saved}")


async def cmd_scan(target: str, severity: str = "medium,high,critical", **kwargs):
    """Nuclei vulnerability scan."""
    print(c(f"\n[*] Nuclei Scan: {target} (severity: {severity})", "cyan"))
    print(c("  This may take several minutes...\n", "yellow"))

    out, err = await run(
        ["nuclei", "-u", target, "-severity", severity,
         "-silent", "-rate-limit", "30", "-bulk-size", "20"],
        timeout=300,
    )

    findings = [l for l in out.splitlines() if l.strip()]
    if not findings:
        print(c("  No findings from Nuclei.", "yellow"))
        print(c("\n  This doesn't mean no vulnerabilities exist!", "yellow"))
        print(c("  Nuclei only covers known patterns. Manual testing is essential.\n", "yellow"))
        print(c("  Manual checks to do:", "cyan"))
        manual_checks = [
            "IDOR: change IDs in requests (user_id=1 → user_id=2)",
            "Auth bypass: remove cookies/JWT and retry privileged requests",
            "Mass assignment: add 'role:admin' to JSON body in profile update",
            "Race condition: send 10 simultaneous requests to checkout endpoint",
            "SSRF: modify URL parameters to point to http://169.254.169.254",
            "Open redirect: append ?redirect=https://evil.com to login page",
            "Rate limit: send 50 login requests in 10 seconds",
        ]
        for m in manual_checks:
            print(c(f"    → {m}", "blue"))
        return

    print(c(f"  Found {len(findings)} issues:\n", "red"))
    for finding in findings:
        severity_color = "red" if "[critical]" in finding or "[high]" in finding else "yellow"
        print(c(f"    {finding}", severity_color))

    saved = save_output("nuclei", "\n".join(findings), target)
    print(c(f"\n  Saved → {saved}", "green"))
    print(c("\n  ⚠  Always verify findings manually before reporting!", "yellow"))
    print(c("  Use Burp Suite to capture request/response as evidence.", "cyan"))


async def cmd_fuzz(url: str, wordlist: str | None = None, extensions: str = "", **kwargs):
    """Directory fuzzing with ffuf."""
    default_wordlists = [
        "/app/wordlists/directories.txt",
        "/usr/share/wordlists/dirb/common.txt",
        "/usr/share/seclists/Discovery/Web-Content/common.txt",
        str(Path.home() / "wordlists/common.txt"),
    ]
    wl = wordlist
    if not wl:
        for w in default_wordlists:
            if Path(w).exists():
                wl = w
                break
    if not wl:
        print(c("  No wordlist found. Download one:", "red"))
        print(c("  wget https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt", "cyan"))
        print(c("  -O /app/wordlists/directories.txt", "cyan"))
        return

    fuzz_url = url if "FUZZ" in url else url.rstrip("/") + "/FUZZ"
    print(c(f"\n[*] Dir Fuzz: {fuzz_url}", "cyan"))
    print(c(f"  Wordlist: {wl}\n", "blue"))

    cmd = ["ffuf", "-u", fuzz_url, "-w", wl, "-t", "50",
           "-mc", "200,201,204,301,302,307,401,403", "-ac", "-c"]
    if extensions:
        cmd += ["-e", "." + extensions.replace(",", ",.")]

    out, err = await run(cmd, timeout=180)
    if out.strip():
        print(out)
        saved = save_output("fuzz", out, url.split("//")[-1].split("/")[0])
        print(c(f"\n  Saved → {saved}", "green"))
    else:
        print(c("  No paths found.\n", "yellow"))
        print(c("  Tips:", "cyan"))
        print("    → Try a larger wordlist: SecLists/Discovery/Web-Content/raft-large-directories.txt")
        print("    → Try with extensions: python hunt.py fuzz URL --ext php,asp,bak")
        print("    → Target may have WAF — try slower: add -rate 10 to ffuf")


async def cmd_wayback(domain: str, **kwargs):
    """Get historical URLs from Wayback Machine + gau."""
    print(c(f"\n[*] Historical URLs: {domain}", "cyan"))

    wb_task = run(["waybackurls", domain], timeout=90)
    gau_task = run(["gau", "--subs", domain], timeout=90)
    (wb_out, _), (gau_out, _) = await asyncio.gather(wb_task, gau_task)

    all_urls = sorted(set(
        l.strip() for l in (wb_out + "\n" + gau_out).splitlines()
        if l.strip()
    ))

    interesting_kw = [".bak", ".old", ".zip", ".sql", ".env", ".log", ".config",
                      "backup", "admin", "secret", "password", "token", "key", "debug"]
    interesting = [u for u in all_urls if any(kw in u.lower() for kw in interesting_kw)]

    print(c(f"\n  Total URLs: {len(all_urls)}", "green"))
    if interesting:
        print(c(f"  🚨 Interesting URLs ({len(interesting)}):", "red"))
        for u in interesting[:30]:
            print(c(f"    ★ {u}", "yellow"))

    saved = save_output("wayback", "\n".join(all_urls), domain)
    print(c(f"\n  Saved → {saved}", "green"))

    print(c("\n  Manual analysis tips:", "cyan"))
    print("    Extract params: grep '?' " + str(saved) + " | sed 's/=.*/=FUZZ/' | sort -u > params.txt")
    print("    Find JS files: grep '\\.js$' " + str(saved))
    print("    Dead endpoints: cat " + str(saved) + " | httprobe")


async def cmd_cert(domain: str, **kwargs):
    """Search certificate transparency for subdomains."""
    print(c(f"\n[*] Certificate Transparency: {domain}", "cyan"))
    try:
        import urllib.request, json as _json
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        with urllib.request.urlopen(url, timeout=15) as r:
            data = _json.loads(r.read())
        names = sorted(set(
            v.strip().lstrip("*.")
            for entry in data
            for v in entry.get("name_value", "").splitlines()
            if domain in v
        ))
        print(c(f"\n  Found {len(names)} domains in CT logs:\n", "green"))
        for n in names:
            print(f"    {n}")
        saved = save_output("cert", "\n".join(names), domain)
        print(c(f"\n  Saved → {saved}", "green"))
    except Exception as e:
        print(c(f"  Error: {e}", "red"))
        print(c(f"  Manual: https://crt.sh/?q=%.{domain}", "cyan"))


async def cmd_screenshot(target: str, list_file: str | None = None, **kwargs):
    """Take screenshots of web targets."""
    print(c(f"\n[*] Screenshots: {target}", "cyan"))
    out_dir = Path(f"output/{target.replace('/', '_')}/screenshots")
    out_dir.mkdir(parents=True, exist_ok=True)

    targets_arg = []
    if list_file and Path(list_file).exists():
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(Path(list_file).read_text())
            targets_arg = ["file", "-f", f.name]
    else:
        targets_arg = ["single", "-u", f"https://{target}" if "://" not in target else target]

    if not shutil.which("gowitness"):
        print(c("  gowitness not found. Alternatives:", "yellow"))
        print(c("  → Use Docker container (has gowitness pre-installed)", "cyan"))
        print(c("  → Install: go install github.com/sensepost/gowitness@v2.5.1", "cyan"))
        print(c("  → Or use: httpx -screenshot flag inside the container", "cyan"))
        return

    cmd = ["gowitness"] + targets_arg + ["--screenshot-path", str(out_dir), "--disable-db"]
    out, err = await run(cmd, timeout=120)
    screenshots = list(out_dir.glob("*.png"))
    print(c(f"\n  {len(screenshots)} screenshots saved to {out_dir}", "green"))
    if screenshots:
        for s in screenshots[:5]:
            print(f"    {s}")


async def cmd_full(domain: str, **kwargs):
    """Run the full recon pipeline."""
    print(c(f"\n[*] Full Recon Pipeline: {domain}", "cyan"))
    print(c("  Steps: recon → alive → port scan → nuclei scan\n", "blue"))

    await cmd_recon(domain)

    sub_file = sorted(Path(f"output/{domain}").glob("subdomains_*.txt"))
    if sub_file:
        await cmd_alive(domain, list_file=str(sub_file[-1]))

    print(c(f"\n[*] Port Scan: {domain}", "cyan"))
    out, _ = await run(["naabu", "-host", domain, "-silent", "-top-ports", "100"], timeout=120)
    if out.strip():
        print(out)
        save_output("ports", out, domain)
    else:
        print(c("  No open ports found (top 100).", "yellow"))

    await cmd_scan(domain)

    print(c(f"\n\n{'═'*60}", "cyan"))
    print(c(f"  Full recon complete for {domain}", "bold"))
    print(c(f"  Results saved to: output/{domain}/", "green"))
    print(c(f"  Next: manual testing of discovered endpoints", "cyan"))
    print(c(f"{'═'*60}\n", "cyan"))


# ── CLI Entry Point ───────────────────────────────────────────────────────────

COMMANDS = {
    "recon":      (cmd_recon,      "Passive subdomain enum (subfinder + crt.sh)"),
    "alive":      (cmd_alive,      "Check which hosts are alive (httpx)"),
    "scan":       (cmd_scan,       "Nuclei vulnerability scan"),
    "fuzz":       (cmd_fuzz,       "Directory fuzzing (ffuf)"),
    "wayback":    (cmd_wayback,    "Historical URLs (waybackurls + gau)"),
    "cert":       (cmd_cert,       "Certificate transparency search"),
    "screenshot": (cmd_screenshot, "Web screenshots (gowitness)"),
    "full":       (cmd_full,       "Full recon pipeline"),
}


def usage():
    banner()
    check_tools()
    print(c("  Commands:\n", "bold"))
    for name, (_, desc) in COMMANDS.items():
        print(f"    {c(f'hunt.py {name:<12}', 'cyan')} {desc}")
    print(c("\n  Examples:\n", "bold"))
    print("    python hunt.py full example.com")
    print("    python hunt.py recon example.com")
    print("    python hunt.py scan https://example.com --severity high,critical")
    print("    python hunt.py fuzz https://example.com/FUZZ --ext php,asp,bak")
    print("    python hunt.py alive example.com --list subdomains.txt")
    print(c("\n  ⚠️  Only test targets you have written permission to test.\n", "red"))


def main():
    banner()
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        usage()
        return

    command = args[0]
    if command not in COMMANDS:
        print(c(f"Unknown command: {command}", "red"))
        usage()
        return

    # Parse positional target + kwargs
    target = args[1] if len(args) > 1 else None
    if not target:
        print(c(f"Target required: python hunt.py {command} <target>", "red"))
        return

    # Parse --flag value pairs
    kwargs: dict = {}
    i = 2
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            key = args[i][2:].replace("-", "_")
            kwargs[key] = args[i + 1]
            i += 2
        else:
            i += 1

    handler, _ = COMMANDS[command]
    asyncio.run(handler(target, **kwargs))


if __name__ == "__main__":
    main()
