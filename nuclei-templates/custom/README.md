# Custom Nuclei Templates

Place your custom Nuclei templates in this directory.

## Template Structure

```yaml
id: custom-vulnerability

info:
  name: Custom Vulnerability Check
  author: Your Name
  severity: high
  description: Description of the vulnerability
  tags: custom,vulnerability

requests:
  - method: GET
    path:
      - "{{BaseURL}}/endpoint"
    
    matchers:
      - type: word
        words:
          - "vulnerable pattern"
```

## Resources

- [Nuclei Template Guide](https://docs.projectdiscovery.io/templates/introduction)
- [Template Examples](https://github.com/projectdiscovery/nuclei-templates)

## Testing Templates

```bash
nuclei -t nuclei-templates/custom/ -u https://example.com
```