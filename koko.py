import urllib.request
import urllib.error
import json
import sys
import os
import time
import base64

TOKEN = input("TOKEN BOT:")

BASE = "https://discord.com/api/v10"
CDN  = "https://cdn.discordapp.com"
 
DISCORD_EPOCH_MS = 1420070400000
OFFSET           = 1327569572
 
FLAGS = {
    1:      "Discord Staff",
    2:      "Partnered Server Owner",
    4:      "HypeSquad Events",
    8:      "Bug Hunter Lv.1",
    64:     "HypeSquad Bravery",
    128:    "HypeSquad Brilliance",
    256:    "HypeSquad Balance",
    512:    "Early Nitro Supporter",
    16384:  "Bug Hunter Lv.2",
    65536:  "Verified Bot",
    131072: "Early Verified Bot Dev",
    262144: "Moderator Alumni",
}
 
NITRO = {0: "None", 1: "Nitro Classic", 2: "Nitro", 3: "Nitro Basic"}
 
def r(code): return f"\033[{code}m"
 
RESET  = r(0)
BOLD   = r(1)
DIM    = r(2)
ITALIC = r(3)
 
def rgb(r_, g_, b_): return f"\033[38;2;{r_};{g_};{b_}m"
def bgrgb(r_, g_, b_): return f"\033[48;2;{r_};{g_};{b_}m"
 
def grad(t, steps):
    out = []
    n = max(len(t) - 1, 1)
    for i, ch in enumerate(t):
        p = i / n
        r_ = int(255 * (1 - p) + 0   * p)
        g_ = int(20  * (1 - p) + 255 * p)
        b_ = int(120 * (1 - p) + 220 * p)
        out.append(f"{rgb(r_, g_, b_)}{ch}")
    return "".join(out) + RESET
 
BANNER = r"""
 /$$   /$$            /$$$$$$                     /$$$$$$                     
| $$$ | $$           /$$__  $$                   /$$__  $$                    
| $$$$| $$  /$$$$$$ | $$  \__//$$$$$$   /$$$$$$ | $$  \__/  /$$$$$$   /$$$$$$$
| $$ $$ $$ /$$__  $$| $$$$   /$$__  $$ /$$__  $$|  $$$$$$  /$$__  $$ /$$_____/
| $$  $$$$| $$$$$$$$| $$_/  | $$$$$$$$| $$  \__/ \____  $$| $$$$$$$$| $$      
| $$\  $$$| $$_____/| $$    | $$_____/| $$       /$$  \ $$| $$_____/| $$      
| $$ \  $$|  $$$$$$$| $$    |  $$$$$$$| $$      |  $$$$$$/|  $$$$$$$|  $$$$$$$
|__/  \__/ \_______/|__/     \_______/|__/       \______/  \_______/ \_______/
""".strip("\n")
 
def print_banner():
    lines = BANNER.split("\n")
    for line in lines:
        print(grad(line, len(line)))
    print()
 
def divider(label=""):
    w = 72
    c = rgb(40, 200, 160)
    if label:
        pad = (w - len(label) - 4) // 2
        print(c + "─" * pad + "┤ " + BOLD + rgb(220, 255, 240) + label + RESET + c + " ├" + "─" * pad + RESET)
    else:
        print(c + "─" * w + RESET)
 
def kv(key, val, accent=False):
    k_col = rgb(120, 220, 180)
    v_col = rgb(220, 255, 240) if not accent else rgb(255, 180, 220)
    sym   = rgb(60, 180, 140) + "›" + RESET
    if val is None or val == "" or val == []:
        v_col = rgb(80, 80, 100)
        val   = "—"
    print(f"  {sym} {k_col}{BOLD}{key:<22}{RESET}  {v_col}{val}{RESET}")
 
def snowflake_to_date(uid):
    ts = (int(uid) >> 22) + 1420070400000
    t  = time.gmtime(ts / 1000)
    return time.strftime("%Y-%m-%d  %H:%M:%S UTC", t)
 
def avatar_url(uid, h, size=1024):
    if h:
        ext = "gif" if h.startswith("a_") else "png"
        return f"{CDN}/avatars/{uid}/{h}.{ext}?size={size}"
    return f"{CDN}/embed/avatars/{int(uid) % 6}.png"
 
def banner_url(uid, h, size=1024):
    if not h: return None
    ext = "gif" if h.startswith("a_") else "png"
    return f"{CDN}/banners/{uid}/{h}.{ext}?size={size}"
 
def deco_url(asset):
    return f"{CDN}/avatar-decoration-presets/{asset}.png" if asset else None
 
def resolve_flags(bits):
    return [name for v, name in FLAGS.items() if bits & v] or ["No public badges"]
 
def fetch(uid):
    req = urllib.request.Request(
        f"{BASE}/users/{uid}",
        headers={"Authorization": f"Bot {TOKEN}", "User-Agent": "NeferSec/1.0"}
    )
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())
 
def fmt_hex(n):
    return f"#{n:06X}" if n is not None else None
 
def token_anatomy(uid):
    p1 = base64.b64encode(uid.encode()).decode().rstrip("=")
    unix_ms = (int(uid) >> 22) + DISCORD_EPOCH_MS
    unix_s  = unix_ms // 1000
    val     = unix_s - OFFSET
    p2      = base64.b64encode(val.to_bytes(4, "big")).decode().rstrip("=")
    return p1, p2
 
def print_token_anatomy(uid):
    p1, p2 = token_anatomy(uid)
    print()
    divider("TOKEN ANATOMY")
    kv("ID Encoded (pt.1)",   p1)
    kv("Timestamp (pt.2)",    p2)
    kv("HMAC (pt.3)",         "[sha1·hmac — server-side only]")
    kv("Token Structure",     f"{p1}.{p2}.[sha1·hmac — server-side only]")
 
def print_profile(u):
    uid     = u["id"]
    uname   = u.get("username", "")
    gname   = u.get("global_name") or uname
    disc    = u.get("discriminator", "0")
    tag     = f"#{disc}" if disc != "0" else None
    created = snowflake_to_date(uid)
    av_url  = avatar_url(uid, u.get("avatar"))
    bn_url  = banner_url(uid, u.get("banner"))
    color   = fmt_hex(u.get("accent_color"))
    nitro   = NITRO.get(u.get("premium_type", 0), "Unknown")
    badges  = resolve_flags(u.get("public_flags", 0))
    is_bot  = u.get("bot", False)
    is_sys  = u.get("system", False)
    deco    = u.get("avatar_decoration_data")
    pg      = u.get("primary_guild")
    coll    = u.get("collectibles")
 
    print()
    divider("IDENTITY")
    kv("User ID",        uid)
    kv("Username",       uname)
    kv("Display Name",   gname)
    kv("Discriminator",  tag)
    kv("Account Type",   ("System" if is_sys else "Bot" if is_bot else "Human"), accent=is_bot or is_sys)
    kv("Created At",     created)
 
    print()
    divider("PROFILE")
    kv("Avatar URL",     av_url)
    kv("Banner URL",     bn_url)
    kv("Banner Color",   color)
    kv("Nitro Tier",     nitro)
 
    print()
    divider("BADGES")
    for b in badges:
        kv("Badge", b)
 
    if deco:
        print()
        divider("AVATAR DECORATION")
        kv("SKU ID",    deco.get("sku_id"))
        kv("Asset URL", deco_url(deco.get("asset")))
 
    if pg:
        print()
        divider("PRIMARY GUILD / CLAN")
        kv("Guild ID",  pg.get("identity_guild_id"))
        kv("Clan Tag",  pg.get("tag"))
        kv("Enabled",   str(pg.get("identity_enabled", False)))
 
    if coll:
        print()
        divider("COLLECTIBLES")
        np = coll.get("nameplate")
        if np:
            kv("Nameplate", np.get("label") or np.get("asset", "").split("/")[-1])
            kv("Palette",   np.get("palette"))
 
    print_token_anatomy(uid)
 
    print()
    divider()
    print()
 
def prompt():
    c  = rgb(255, 80, 180)
    l1 = (c + BOLD + "┌──(" + RESET
        + rgb(255, 80, 180) + BOLD + "nefersec" + RESET
        + rgb(200, 200, 200) + "@" + RESET
        + rgb(100, 255, 200) + BOLD + "root" + RESET
        + c + BOLD + ")" + RESET
        + rgb(160, 160, 180) + "─[~]" + RESET)
    l2 = c + BOLD + "└─$ " + RESET + rgb(220, 255, 240) + BOLD + "User ID: " + RESET
    print(f"\n{l1}")
    return input(l2).strip()
 
def clear():
    os.system("cls" if os.name == "nt" else "clear")
 
def bye():
    print()
 
def main():
    if TOKEN == "":
        print(rgb(255, 80, 80) + "\n  [!] Set your BOT TOKEN inside the script first.\n" + RESET)
        sys.exit(1)
 
    clear()
    print_banner()
 
    while True:
        uid = prompt()
 
        if not uid:
            print(rgb(255, 80, 80) + "  [!] No ID provided." + RESET)
            continue
 
        if not uid.isdigit():
            print(rgb(255, 80, 80) + "  [!] Invalid ID (numbers only)." + RESET)
            continue
 
        print(rgb(60, 180, 140) + "\n  ⟳  Fetching..." + RESET)
 
        try:
            data = fetch(uid)
            clear()
            print_banner()
            print_profile(data)
        except urllib.error.HTTPError as e:
            code = e.code
            msgs = {
                401: "Unauthorized — check your bot token.",
                404: "User not found.",
                429: "Rate limited. Wait a moment.",
            }
            print(rgb(255, 80, 80) + f"\n  [!] HTTP {code}: {msgs.get(code, e.reason)}\n" + RESET)
        except Exception as e:
            print(rgb(255, 80, 80) + f"\n  [!] Error: {e}\n" + RESET)
 
        again = rgb(120, 220, 180) + "\n  Lookup another user? (y/n): " + RESET
        try:
            ans = input(again).strip().lower()
        except (KeyboardInterrupt, EOFError):
            break
 
        if ans != "y":
            break
 
        clear()
        print_banner()
 
    bye()
 
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(RESET + "\n")
        sys.exit(0)
