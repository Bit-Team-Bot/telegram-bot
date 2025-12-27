# WebUI Docker Setup

## 🐳 Docker-Integration

### Voraussetzungen
- Docker & Docker Compose installiert
- Bestehende Services (api, bot, userbot) laufen

### Schnellstart

#### 1. WebUI zu deinem Projekt hinzufügen

Kopiere den gesamten `webui/` Ordner in dein Projekt-Root:

```
your-project/
├── api/
├── bot/
├── userbot/
└── webui/        # <-- NEU
    ├── src/
    ├── Dockerfile
    ├── nginx.conf
    └── package.json
```

#### 2. docker-compose.yml anpassen

Füge den WebUI-Service zu deiner `docker-compose.yml` hinzu:

```yaml
services:
  # ... deine bestehenden Services

  webui:
    build: ./webui
    container_name: telegram-bot-webui
    ports:
      - "8080:80"
    environment:
      - VITE_API_URL=http://api:8000
      - VITE_USERBOT_URL=http://userbot:9000
    depends_on:
      - api
      - userbot
    networks:
      - telegram-bot-network
    restart: unless-stopped
```

#### 3. Container bauen und starten

```bash
# Nur WebUI bauen
docker compose build webui

# WebUI starten
docker compose up -d webui

# Oder alle Services neu starten
docker compose up -d --build
```

#### 4. Testen

Öffne im Browser: `http://localhost:8080`

### 🔧 Konfiguration

#### API-URLs anpassen

**Für lokales Docker-Netzwerk:**
- `VITE_API_URL=http://api:8000` (Container-Name)
- `VITE_USERBOT_URL=http://userbot:9000`

**Für externes Deployment:**
- `VITE_API_URL=https://api.deine-domain.com`
- `VITE_USERBOT_URL=https://userbot.deine-domain.com`

Bearbeite `.env.production` oder setze die Variablen in `docker-compose.yml`.

### 📝 Nützliche Befehle

```bash
# Logs anzeigen
docker compose logs -f webui

# Container neu starten
docker compose restart webui

# Container stoppen
docker compose stop webui

# Container komplett neu bauen
docker compose build --no-cache webui

# In Container einsteigen
docker compose exec webui sh

# WebUI aus Netzwerk entfernen und neu starten
docker compose down webui && docker compose up -d webui
```

### 🚀 Deployment auf Raspberry Pi

```bash
# 1. Code auf Pi kopieren
scp -r webui/ user@raspberry-pi:/home/user/your-project/

# 2. Auf Pi einloggen
ssh user@raspberry-pi

# 3. Zum Projekt wechseln
cd /home/user/your-project

# 4. Container bauen und starten
docker compose build webui
docker compose up -d webui

# 5. Status prüfen
docker compose ps
docker compose logs -f webui
```

### 🔍 Troubleshooting

**WebUI startet nicht:**
```bash
# Logs prüfen
docker compose logs webui

# Container Status
docker compose ps webui

# Ports prüfen
netstat -tuln | grep 8080
```

**API nicht erreichbar:**
- Prüfe ob API-Container läuft: `docker compose ps api`
- Prüfe Netzwerk: `docker network inspect telegram-bot-network`
- Teste API direkt: `curl http://localhost:8000/health`

**Build-Fehler:**
```bash
# Cache löschen und neu bauen
docker compose build --no-cache webui

# Node modules im Container prüfen
docker compose run --rm webui npm list
```

### 📊 Monitoring

```bash
# Ressourcen-Nutzung
docker stats webui

# Health Status
docker inspect --format='{{.State.Health.Status}}' telegram-bot-webui

# Nginx Access Logs
docker compose exec webui tail -f /var/log/nginx/access.log
```

### 🔐 Produktion

Für Produktion empfehle ich:

1. **HTTPS über Reverse Proxy (Traefik/nginx):**
```yaml
webui:
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.webui.rule=Host(`webui.deine-domain.com`)"
    - "traefik.http.routers.webui.entrypoints=websecure"
    - "traefik.http.routers.webui.tls.certresolver=letsencrypt"
```

2. **Environment Variables aus .env:**
```bash
# .env Datei
VITE_API_URL=https://api.deine-domain.com
VITE_USERBOT_URL=https://userbot.deine-domain.com
```

3. **Health Checks aktivieren:**
```yaml
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
  interval: 30s
  timeout: 3s
  retries: 3
```

### 📦 Image-Größe optimieren

Das aktuelle Multi-Stage Build erzeugt ein ~25MB Image (nginx:alpine + dist/).

Weitere Optimierungen:
- ✅ Multi-stage build (bereits implementiert)
- ✅ .dockerignore (bereits vorhanden)
- ✅ npm ci statt npm install
- ✅ Alpine Linux als Base

### 🆘 Support

Bei Problemen:
1. Prüfe Logs: `docker compose logs webui`
2. Prüfe Container-Status: `docker compose ps`
3. Teste API-Erreichbarkeit aus Container:
   ```bash
   docker compose exec webui wget -O- http://api:8000/health
   ```
