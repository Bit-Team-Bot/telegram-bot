#!/bin/bash

# Telegram Bot System - Deployment Script
# Vollständiges Deployment aller Komponenten

set -e  # Exit on error

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging-Funktionen
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Prüfe ob als Root ausgeführt
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "Dieses Script sollte nicht als Root ausgeführt werden"
        exit 1
    fi
}

# Prüfe Voraussetzungen
check_prerequisites() {
    log_info "Prüfe Voraussetzungen..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 ist nicht installiert"
        exit 1
    fi
    
    # Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js ist nicht installiert"
        exit 1
    fi
    
    # Git
    if ! command -v git &> /dev/null; then
        log_error "Git ist nicht installiert"
        exit 1
    fi
    
    log_success "Alle Voraussetzungen erfüllt"
}

# Backup erstellen
create_backup() {
    log_info "Erstelle Backup..."
    
    BACKUP_DIR="/home/manny/backups/telegram-bot-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Datenbank backup
    if [ -f "/home/manny/telegram-bot/telegram_bot.db" ]; then
        cp /home/manny/telegram-bot/telegram_bot.db "$BACKUP_DIR/"
        log_success "Datenbank-Backup erstellt"
    fi
    
    # Konfigurationsdateien backup
    if [ -f "/home/manny/telegram-bot/.env" ]; then
        cp /home/manny/telegram-bot/.env "$BACKUP_DIR/"
        log_success "Konfigurations-Backup erstellt"
    fi
    
    log_success "Backup erstellt in: $BACKUP_DIR"
}

# Code aktualisieren
update_code() {
    log_info "Aktualisiere Code..."
    
    cd /home/manny/telegram-bot
    
    # Git Status prüfen
    if [ -d ".git" ]; then
        git fetch origin
        git pull origin main
        log_success "Code aktualisiert"
    else
        log_warning "Kein Git-Repository gefunden"
    fi
}

# Backend deployen
deploy_backend() {
    log_info "Deploye Backend..."
    
    cd /home/manny/telegram-bot/backend
    
    # Virtual Environment erstellen/aktualisieren
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Virtual Environment erstellt"
    fi
    
    # Dependencies installieren
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Backend-Dependencies installiert"
    
    # Import-Cleaner ausführen
    if [ -f "scripts/clean_imports.py" ]; then
        python scripts/clean_imports.py
        log_success "Imports bereinigt"
    fi
    
    # Datenbank-Migrationen
    if [ -f "alembic.ini" ]; then
        alembic upgrade head
        log_success "Datenbank-Migrationen ausgeführt"
    fi
    
    # Tests ausführen
    if [ -d "tests" ]; then
        python -m pytest tests/ -v --tb=short
        log_success "Backend-Tests erfolgreich"
    fi
    
    deactivate
}

# WebUI deployen
deploy_webui() {
    log_info "Deploye WebUI..."
    
    cd /home/manny/telegram-bot/webui
    
    # Dependencies installieren
    npm install
    log_success "WebUI-Dependencies installiert"
    
    # Build erstellen
    npm run build
    log_success "WebUI-Build erstellt"
    
    # Tests ausführen (falls vorhanden)
    if [ -f "package.json" ] && grep -q "test" package.json; then
        npm test
        log_success "WebUI-Tests erfolgreich"
    fi
}

# Bot deployen
deploy_bot() {
    log_info "Deploye Bot..."
    
    cd /home/manny/telegram-bot/bot
    
    # Virtual Environment erstellen/aktualisieren
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Bot Virtual Environment erstellt"
    fi
    
    # Dependencies installieren
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Bot-Dependencies installiert"
    
    deactivate
}

# Userbot deployen
deploy_userbot() {
    log_info "Deploye Userbot..."
    
    cd /home/manny/telegram-bot/userbot
    
    # Virtual Environment erstellen/aktualisieren
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        log_success "Userbot Virtual Environment erstellt"
    fi
    
    # Dependencies installieren
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    log_success "Userbot-Dependencies installiert"
    
    deactivate
}

# Services neu starten
restart_services() {
    log_info "Starte Services neu..."
    
    # Systemd Services
    sudo systemctl restart telegram-bot-backend
    sudo systemctl restart telegram-bot-bot
    sudo systemctl restart telegram-bot-userbot
    
    # Status prüfen
    sleep 5
    
    if sudo systemctl is-active --quiet telegram-bot-backend; then
        log_success "Backend-Service läuft"
    else
        log_error "Backend-Service startet nicht"
    fi
    
    if sudo systemctl is-active --quiet telegram-bot-bot; then
        log_success "Bot-Service läuft"
    else
        log_error "Bot-Service startet nicht"
    fi
    
    if sudo systemctl is-active --quiet telegram-bot-userbot; then
        log_success "Userbot-Service läuft"
    else
        log_error "Userbot-Service startet nicht"
    fi
}

# Health Check
health_check() {
    log_info "Führe Health Check durch..."
    
    # Backend API
    if curl -s http://localhost:8000/ > /dev/null; then
        log_success "Backend API erreichbar"
    else
        log_error "Backend API nicht erreichbar"
    fi
    
    # WebUI
    if curl -s http://localhost:3000/ > /dev/null; then
        log_success "WebUI erreichbar"
    else
        log_warning "WebUI nicht erreichbar (möglicherweise nicht gestartet)"
    fi
    
    # Datenbank
    if [ -f "/home/manny/telegram-bot/telegram_bot.db" ]; then
        log_success "Datenbank vorhanden"
    else
        log_warning "Datenbank nicht gefunden"
    fi
}

# Logs anzeigen
show_logs() {
    log_info "Aktuelle Logs:"
    
    echo -e "\n${BLUE}Backend Logs:${NC}"
    sudo journalctl -u telegram-bot-backend --no-pager -n 10
    
    echo -e "\n${BLUE}Bot Logs:${NC}"
    sudo journalctl -u telegram-bot-bot --no-pager -n 10
    
    echo -e "\n${BLUE}Userbot Logs:${NC}"
    sudo journalctl -u telegram-bot-userbot --no-pager -n 10
}

# Cleanup alte Backups
cleanup_backups() {
    log_info "Bereinige alte Backups..."
    
    # Lösche Backups älter als 30 Tage
    find /home/manny/backups -name "telegram-bot-*" -type d -mtime +30 -exec rm -rf {} \;
    log_success "Alte Backups bereinigt"
}

# Hauptfunktion
main() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                Telegram Bot System Deployment                ║"
    echo "║                        Version 1.0.0                        ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Prüfungen
    check_root
    check_prerequisites
    
    # Deployment-Schritte
    create_backup
    update_code
    deploy_backend
    deploy_webui
    deploy_bot
    deploy_userbot
    restart_services
    health_check
    cleanup_backups
    
    echo -e "\n${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    DEPLOYMENT ERFOLGREICH                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Logs anzeigen
    show_logs
    
    log_success "Deployment abgeschlossen!"
    log_info "System-Status:"
    log_info "- Backend: http://localhost:8000"
    log_info "- WebUI: http://localhost:3000"
    log_info "- API Docs: http://localhost:8000/docs"
}

# Script ausführen
main "$@" 