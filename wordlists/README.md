# Wordlists

This directory contains wordlists for various fuzzing and enumeration tasks.

## Included Wordlists

- `subdomains.txt` - Subdomain enumeration (110,000 entries)
- `directories.txt` - Directory bruteforcing
- `parameters.txt` - Parameter fuzzing
- `xss-payloads.txt` - XSS testing payloads
- `sqli-payloads.txt` - SQL injection payloads

## Auto-Download

Wordlists are automatically downloaded during setup. To manually download:

```bash
make wordlists
```

## Custom Wordlists

Place custom wordlists in this directory and reference them in your scans.

## Sources

- [SecLists](https://github.com/danielmiessler/SecLists)
- [PayloadBox](https://github.com/payloadbox)
- [Assetnote Wordlists](https://wordlists.assetnote.io/)