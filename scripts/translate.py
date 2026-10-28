#!/usr/bin/env python3
"""Translate batches via translate.googleapis.com gtx endpoint. Free, no key."""
import json, os, sys, time, urllib.parse, urllib.request

KEEP = {  # technical terms left as-is
    "TUN","MTU","DNS","DoH","DoT","UDP","TCP","TLS","SNI","REALITY","XHTTP","VLESS","VMess",
    "trojan","hysteria2","tuic","anytls","masque","naive","wireguard","WireGuard","AmneziaWG",
    "AWG","Amnezia","socks","SOCKS","SOCKS5","HTTP","HTTPS","QUIC","gRPC","WebDAV","API","JSON",
    "YAML","URL","URI","IP","CIDR","IPv4","IPv6","GeoSite","GeoIP","SRS","Clash","sing-box",
    "Tailscale","DERP","WARP","SSH","VPN","LAN","WAN","NAT","MTU","RTT","ID","UUID","HWID",
    "macOS","Windows","Linux","Android","iOS","Go","Rust","Dart","Fyne","Tauri","MCP","CDN",
    "EC2","VPS","NAS","CPU","GPU","RAM","KB","MB","GB","ms","px","UI","UX","FAQ","PID","EOF",
}

def gtx(text, tries=3):
    if not text or not text.strip():
        return text
    url = ("https://translate.googleapis.com/translate_a/single"
           "?client=gtx&sl=en&tl=zh-CN&dt=t&q=" + urllib.parse.quote(text))
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
            out = "".join(seg[0] for seg in data[0] if seg and seg[0])
            return out
        except Exception as e:
            if attempt == tries - 1:
                print(f"    ! translate failed for {text!r}: {e}", file=sys.stderr)
                return text
            time.sleep(1.5 * (attempt + 1))
    return text

def main():
    manifest = json.load(open("work/manifest.json", encoding="utf-8"))
    os.makedirs("work/out", exist_ok=True)
    for item in manifest:
        src_fn, out_fn = item["file"], item["file"].replace("batch_", "out/batch_")
        if os.path.exists(out_fn):
            print(f"skip {out_fn}")
            continue
        rows = json.load(open(src_fn, encoding="utf-8"))
        res = []
        for row in rows:
            key = row["key"]
            if key in KEEP:
                val = key
            else:
                val = gtx(key)
            entry = {"key": key, "value": val}
            if row.get("special"):
                entry["special"] = {}
                for sp in row["special"]:
                    # plural forms: value already translated; store as-is
                    entry["special"][sp] = {"value": val}
            res.append(entry)
            time.sleep(0.12)
        json.dump(res, open(out_fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"done {out_fn} ({len(res)})")

if __name__ == "__main__":
    main()