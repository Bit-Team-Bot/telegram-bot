# 🌐 Cloudflare Tunnel für Userbot-Service

## Übersicht

Cloudflare Tunnel macht den Userbot-Service (Port 8001) über das Internet erreichbar, ohne Port-Forwarding oder Firewall-Konfiguration.

## 🚀 Schnelle Einrichtung

### 1. Cloudflare Tunnel installieren

```bash
# Für Linux (Raspberry Pi)
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Oder mit snap
sudo snap install cloudflared
```

### 2. Tunnel authentifizieren

```bash
# Bei Cloudflare anmelden
cloudflared tunnel login

# Browser öffnet sich automatisch
# Folge den Anweisungen und wähle deine Domain aus
```

### 3. Tunnel erstellen

```bash
# Tunnel für Userbot-Service erstellen
cloudflared tunnel create userbot-service

# Tunnel-ID anzeigen (wird für config.yml benötigt)
cloudflared tunnel list
```

### 4. Konfigurationsdatei erstellen

```bash
# Konfigurationsverzeichnis erstellen
mkdir ~/.cloudflared

# Konfigurationsdatei erstellen
nano ~/.cloudflared/config.yml
```

**Inhalt für `~/.cloudflared/config.yml`:**
```yaml
tunnel: [TUNNEL-ID-HIER-EINFÜGEN]
credentials-file: ~/.cloudflared/[TUNNEL-ID-HIER-EINFÜGEN].json

ingress:
  # Userbot-Service auf Port 8001
  - hostname: userbot.bit-team-bot.online
    service: http://localhost:8001
    originRequest:
      noTLSVerify: true
  
  # Catch-all für unbekannte Hosts
  - service: http_status:404
```

### 5. Tunnel starten

```bash
# Tunnel im Vordergrund starten (für Tests)
cloudflared tunnel run userbot-service

# Oder als Service starten
sudo cloudflared service install
```

## 🔧 Automatisierte Einrichtung

### Skript für automatische Einrichtung

```bash
#!/bin/bash

echo "🚀 Cloudflare Tunnel für Userbot-Service einrichten..."

# Prüfe ob cloudflared installiert ist
if ! command -v cloudflared &> /dev/null; then
    echo "📦 Installiere cloudflared..."
    wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i cloudflared-linux-amd64.deb
    rm cloudflared-linux-amd64.deb
fi

# Tunnel erstellen
echo "🌐 Erstelle Tunnel..."
TUNNEL_ID=$(cloudflared tunnel create userbot-service | grep -o '[a-f0-9-]\{36\}')

if [ -z "$TUNNEL_ID" ]; then
    echo "❌ Fehler beim Erstellen des Tunnels"
    exit 1
fi

echo "✅ Tunnel erstellt: $TUNNEL_ID"

# Konfigurationsverzeichnis erstellen
mkdir -p ~/.cloudflared

# Konfigurationsdatei erstellen
cat > ~/.cloudflared/config.yml << EOF
tunnel: $TUNNEL_ID
credentials-file: ~/.cloudflared/$TUNNEL_ID.json

ingress:
  - hostname: userbot.bit-team-bot.online
    service: http://localhost:8001
    originRequest:
      noTLSVerify: true
  - service: http_status:404
EOF

echo "✅ Konfiguration erstellt"

# Tunnel starten
echo "🚀 Starte Tunnel..."
cloudflared tunnel run userbot-service
```

## 🔄 Systemd Service (empfohlen)

### 1. Service-Datei erstellen

```bash
sudo nano /etc/systemd/system/cloudflared-userbot.service
```

**Inhalt:**
```ini
[Unit]
Description=Cloudflare Tunnel für Userbot-Service
After=network.target

[Service]
Type=simple
User=manny
ExecStart=/usr/local/bin/cloudflared tunnel run userbot-service
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 2. Service aktivieren

```bash
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-userbot
sudo systemctl start cloudflared-userbot
sudo systemctl status cloudflared-userbot
```

## 🧪 Testing

### 1. Tunnel-Status prüfen

```bash
# Tunnel-Status
cloudflared tunnel list

# Service-Status
sudo systemctl status cloudflared-userbot

# Logs anzeigen
sudo journalctl -u cloudflared-userbot -f
```

### 2. Verbindung testen

```bash
# HTTP-Test
curl https://userbot.bit-team-bot.online/

# API-Test
curl https://userbot.bit-team-bot.online/status

# CORS-Test
curl -X OPTIONS https://userbot.bit-team-bot.online/start \
  -H "Origin: https://webui.bit-team-bot.online" \
  -H "Access-Control-Request-Method: POST"
```

### 3. Frontend-Test

```bash
cd webui
node debug-production.js
```

## 🔧 DNS-Konfiguration

### 1. DNS-Record in Cloudflare erstellen

1. Gehe zu deiner Cloudflare-Dashboard
2. Wähle deine Domain `bit-team-bot.online`
3. Gehe zu **DNS** → **Records**
4. Erstelle einen neuen CNAME-Record:
   - **Name**: `userbot`
   - **Target**: `[TUNNEL-ID].cfargotunnel.com`
   - **Proxy status**: Proxied (Orange Wolke)

### 2. Automatische DNS-Konfiguration

```bash
# DNS-Record automatisch konfigurieren
cloudflared tunnel route dns userbot-service userbot.bit-team-bot.online
```

## 🚨 Troubleshooting

### Häufige Probleme

1. **Tunnel nicht erreichbar**
   ```bash
   # Logs prüfen
   sudo journalctl -u cloudflared-userbot -f
   
   # Tunnel neu starten
   sudo systemctl restart cloudflared-userbot
   ```

2. **DNS nicht aufgelöst**
   ```bash
   # DNS-Record prüfen
   nslookup userbot.bit-team-bot.online
   
   # CNAME prüfen
   dig userbot.bit-team-bot.online CNAME
   ```

3. **CORS-Fehler**
   - Prüfe ob der Tunnel läuft
   - Prüfe die Origin-Header im Userbot-Service

### Logs anzeigen

```bash
# Cloudflared Logs
sudo journalctl -u cloudflared-userbot -f

# Userbot-Service Logs
tail -f userbot_service/nohup.out
```

## ✅ Erfolgreiche Konfiguration

Nach korrekter Einrichtung:

1. **Tunnel läuft**: `sudo systemctl status cloudflared-userbot`
2. **DNS aufgelöst**: `nslookup userbot.bit-team-bot.online`
3. **Service erreichbar**: `curl https://userbot.bit-team-bot.online/`
4. **Frontend funktioniert**: Login über Webinterface

## 🎯 Nächste Schritte

1. **Tunnel einrichten** (siehe oben)
2. **DNS konfigurieren**
3. **Frontend neu bauen**: `cd webui && ./build-production.sh`
4. **Testen**: `node debug-production.js`

**Der Userbot-Service ist dann über `https://userbot.bit-team-bot.online` erreichbar!** 🌐 