#!/usr/bin/env python3
"""Download upstream ru.json as the key skeleton and split into translation batches."""
import json, os, sys, urllib.request

UPSTREAM = "https://raw.githubusercontent.com/Leadaxe/singbox-launcher/main/bin/locale/ru.json"
BATCH = 120

def main():
    raw = urllib.request.urlopen(UPSTREAM, timeout=60).read().decode("utf-8")
    src = json.loads(raw)
    os.makedirs("work", exist_ok=True)
    with open("work/ru.json", "w", encoding="utf-8") as f:
        json.dump(src, f, ensure_ascii=False, indent=1)
    keys = [k for k in src.keys() if k != "_display_name"]
    batches = [keys[i:i+BATCH] for i in range(0, len(keys), BATCH)]
    manifest = []
    for idx, chunk in enumerate(batches):
        payload = []
        for k in chunk:
            v = src[k]
            if isinstance(v, dict):
                payload.append({"key": k, "en": k, "special": list((v.get("special") or {}).keys())})
            else:
                payload.append({"key": k, "en": k, "special": []})
        fn = f"work/batch_{idx:03d}.json"
        with open(fn, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=1)
        manifest.append({"file": fn, "count": len(payload)})
    with open("work/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(f"total keys={len(keys)} batches={len(batches)} size={len(raw)}B")

if __name__ == "__main__":
    main()