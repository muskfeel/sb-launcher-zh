#!/usr/bin/env python3
"""Translate batches via Google gtx with glossary + context-aware post-processing."""
import json, os, sys, time, re, urllib.parse, urllib.request

# Terms that must never be translated.
KEEP = {
    "TUN","MTU","DNS","DoH","DoT","UDP","TCP","TLS","SNI","REALITY","XHTTP","VLESS","VMess",
    "trojan","hysteria2","tuic","anytls","masque","naive","wireguard","WireGuard","AmneziaWG",
    "AWG","Amnezia","socks","SOCKS","SOCKS5","HTTP","HTTPS","QUIC","gRPC","WebDAV","API","JSON",
    "YAML","URL","URI","IP","CIDR","IPv4","IPv6","GeoSite","GeoIP","SRS","Clash","sing-box",
    "Tailscale","DERP","WARP","SSH","VPN","LAN","WAN","NAT","RTT","ID","UUID","HWID",
    "macOS","Windows","Linux","Android","iOS","Go","Rust","Dart","Fyne","Tauri","MCP","CDN",
    "EC2","VPS","NAS","CPU","GPU","RAM","KB","MB","GB","ms","px","UI","UX","FAQ","PID","EOF",
}

# Post-translation term correction: gtx picks the wrong sense for these words.
FIX = [
    (r"紧密联系", "关闭连接"),
    (r"关闭联系", "关闭连接"),
    (r"紧密的联系", "连接"),
    (r"发布路线广告", "发布路由"),
    (r"路线广告", "路由通告"),
    (r"广告路由", "路由通告"),
    (r"发布路线", "发布路由"),
    (r"这个装置", "此设备"),
    (r"该装置", "此设备"),
    (r"装置", "设备"),
    (r"团体", "分组"),
    (r"小组", "分组"),
    (r"交换区", "交换项"),
    (r"交换", "交换"),
    (r"密钥", "密钥"),
]

# Context hint prepended to every request so the engine picks the networking sense.
PREFIX = "In a VPN/proxy client UI context. "
SUFFIX = " (networking UI label, translate concisely)"

def postprocess(text):
    for pat, repl in FIX:
        text = re.sub(pat, repl, text)
    return text

def gtx(text, tries=4):
    if not text or not text.strip():
        return text
    q = PREFIX + text + SUFFIX
    url = ("https://translate.googleapis.com/translate_a/single"
           "?client=gtx&sl=en&tl=zh-CN&dt=t&q=" + urllib.parse.quote(q))
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=30).read().decode("utf-8"))
            out = "".join(seg[0] for seg in data[0] if seg and seg[0])
            # strip the echoed prefix/suffix translation if it leaked in
            out = re.sub(r"^在\s*VPN\s*/?\s*代理客户端界面上下文中[，,]?\s*", "", out)
            out = re.sub(r"[（(]\s*网络界面标签[^）)]*[）)]\s*$", "", out)
            out = out.strip().rstrip("。")
            return postprocess(out)
        except Exception as e:
            if attempt == tries - 1:
                print(f"    ! failed {text!r}: {e}", file=sys.stderr)
                return text
            time.sleep(2.0 * (attempt + 1))
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
            val = key if key in KEEP else gtx(key)
            entry = {"key": key, "value": val}
            if row.get("special"):
                entry["special"] = {sp: {"value": val} for sp in row["special"]}
            res.append(entry)
            time.sleep(0.1)
        json.dump(res, open(out_fn, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"done {out_fn} ({len(res)})")

if __name__ == "__main__":
    main()