#!/usr/bin/env python3
"""Merge translated batches into bin/locale/zh.json and validate integrity."""
import json, os, sys

def main():
    ru = json.load(open("work/ru.json", encoding="utf-8"))
    out = {"_display_name": "简体中文"}
    files = sorted(f for f in os.listdir("work/out") if f.endswith(".json"))
    total = 0
    for fn in files:
        for row in json.load(open(os.path.join("work/out", fn), encoding="utf-8")):
            k, v = row["key"], row["value"]
            if row.get("special"):
                out[k] = {"value": v, "special": row["special"]}
            else:
                out[k] = {"value": v}
            total += 1
    os.makedirs("out", exist_ok=True)
    with open("out/zh.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    # validation
    ru_keys = {k for k in ru if k != "_display_name"}
    zh_keys = {k for k in out if k != "_display_name"}
    missing = ru_keys - zh_keys
    extra = zh_keys - ru_keys
    untranslated = [k for k in zh_keys if out[k].get("value") == k and k not in ("OK","ID","IP")]
    print(f"total={total} ru_keys={len(ru_keys)} zh_keys={len(zh_keys)}")
    print(f"missing={len(missing)} extra={len(extra)} untranslated={len(untranslated)}")
    if missing:
        print("MISSING sample:", sorted(missing)[:10])
    if extra:
        print("EXTRA sample:", sorted(extra)[:10])
    if untranslated:
        print("UNTRANSLATED sample:", sorted(untranslated)[:15])
    with open("out/report.txt", "w", encoding="utf-8") as f:
        f.write(f"total={total}\nmissing={len(missing)}\nextra={len(extra)}\nuntranslated={len(untranslated)}\n")
    return 0 if not missing and not extra else 1

if __name__ == "__main__":
    sys.exit(main())