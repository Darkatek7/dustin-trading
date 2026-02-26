# 🔍 Dustin Search Tool

## Using SearXNG

**URL:** http://10.0.0.247:8070

### Quick Search:
```bash
curl -s "http://10.0.0.247:8070/search?q=QUERY&format=json&n=10"
```

---

## Example: Research for Trading

### Cooper Flagg:
```bash
curl -s "http://10.0.0.247:8070/search?q=Cooper+Flagg+NBA+stats&format=json" | jq '.results[:3]'
```

### Trump GTA VI Timeline:
```bash
curl -s "http://10.0.0.247:8070/search?q=Trump+president+resign+timeline&format=json"
```

### Europa League 2025:
```bash
curl -s "http://10.0.0.247:8070/search?q=Europa+League+2025+unbeaten+champion&format=json"
```

---

*Config: SEARXNG_URL=http://10.0.0.247:8070*
