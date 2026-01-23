#!/usr/bin/env fish

################################################################################
# BENNING DEVICE MANAGER - FISH SHELL STARTUP SCRIPT
#
# Dieses Skript startet die Benning Device Manager Anwendung mit
# Fish Shell und CachyOS-Optimierungen.
#
# Verwendung: fish start_fish.fish
################################################################################

# Farben
set -l RED '\033[0;31m'
set -l GREEN '\033[0;32m'
set -l YELLOW '\033[1;33m'
set -l BLUE '\033[0;34m'
set -l CYAN '\033[0;36m'
set -l NC '\033[0m'

# Funktionen
function print_header
    echo -e "\n$CYAN╔════════════════════════════════════════════════════════════╗$NC"
    echo -e "$CYAN║$NC $argv[1]"
    echo -e "$CYAN╚════════════════════════════════════════════════════════════╝$NC\n"
end

function print_success
    echo -e "$GREEN✓ $argv[1]$NC"
end

function print_error
    echo -e "$RED✗ $argv[1]$NC"
end

function print_info
    echo -e "$YELLOW ℹ $argv[1]$NC"
end

function print_step
    echo -e "$BLUE→ $argv[1]$NC"
end

# Header
print_header "🚀 BENNING DEVICE MANAGER - Fish Shell Edition"

# Überprüfe Verzeichnis
print_step "Überprüfe Projektverzeichnis..."
if not test -f "src/main.py"
    print_error "src/main.py nicht gefunden!"
    exit 1
end
print_success "Projektverzeichnis gefunden"

# Überprüfe Virtual Environment
print_step "Überprüfe Virtual Environment..."
if not test -f "venv/bin/activate.fish"
    print_error "Virtual Environment nicht gefunden!"
    print_info "Führen Sie zuerst aus: python -m venv venv"
    exit 1
end
print_success "Virtual Environment gefunden"

# Aktiviere Virtual Environment
source venv/bin/activate.fish
print_success "Virtual Environment aktiviert"

# Setze Python-Pfad
set -x PYTHONPATH (pwd):$PYTHONPATH
print_success "PYTHONPATH gesetzt: $PYTHONPATH"

# CachyOS Optimierungen
print_step "Aktiviere CachyOS-Optimierungen..."
set -x PYTHONOPTIMIZE 2
set -x PYTHONHASHSEED 0
print_success "Python-Optimierungen aktiviert"

# Überprüfe Konfiguration
print_step "Überprüfe Konfiguration..."
if not test -f ".env"
    print_info "Erstelle .env Datei..."
    cat > .env << 'EOF'
# Flask Konfiguration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Datenbank (Docker MySQL auf Port 3307)
DB_HOST=localhost
DB_PORT=3307
DB_USER=benning
DB_PASSWORD=benning
DB_NAME=benning_device_manager

# Upload Folder
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=10485760

# Logging
LOG_LEVEL=DEBUG

# Fish Shell Spezifisch
PYTHONOPTIMIZE=2
PYTHONHASHSEED=0
EOF
    print_success ".env erstellt"
else
    print_success ".env existiert bereits"
end

# Überprüfe Docker Container
print_step "Überprüfe Docker MySQL Container..."
set -l container_status (docker ps --filter "name=benning-flask-mysql" --format "{{.Status}}" 2>/dev/null)

if test -z "$container_status"
    print_error "Docker MySQL Container nicht gefunden oder nicht aktiv!"
    print_info "Starten Sie den Container mit:"
    echo "  docker start benning-flask-mysql"
    exit 1
else
    print_success "Docker MySQL Container läuft: $container_status"
end

# Erstelle Upload-Verzeichnis
mkdir -p static/uploads
print_success "Upload-Verzeichnis vorbereitet"

# Zeige Systeminformationen
print_header "📊 System-Informationen"
echo -e "Python Version: $CYAN(python --version)$NC"
echo -e "Pip Version: $CYAN(pip --version | cut -d' ' -f2)$NC"
echo -e "CPU Kerne: $CYAN(nproc)$NC"
echo -e "Shell: $CYAN$SHELL$NC"
echo ""

# Zeige Docker Container Info
print_header "🐳 Docker MySQL Container"
docker ps --filter "name=benning-flask-mysql" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Starte Anwendung
print_header "✨ Starte Benning Device Manager"

echo -e "$YELLOW Öffne Browser:$NC"
echo "  http://localhost:5000"
echo ""
echo -e "$YELLOW Zum Beenden:$NC"
echo "  Ctrl+C"
echo ""
echo -e "$YELLOW Datenbank-Status:$NC"
echo "  docker ps | grep benning"
echo ""
echo -e "$YELLOW Datenbank-Logs:$NC"
echo "  docker logs -f benning-flask-mysql"
echo ""

# Starte mit CachyOS-Optimierungen
exec python src/main.py
