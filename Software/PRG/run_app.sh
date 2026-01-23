#!/bin/bash

################################################################################
# Run App - Startet die Benning Device Manager Anwendung
# Mit korrektem Python-Pfad-Handling
#
# Verwendung: bash run_app.sh
################################################################################

set -e

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} $1"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

print_header "🚀 Benning Device Manager - Startup"

# Überprüfe Verzeichnis
if [ ! -f "src/main.py" ]; then
    echo "❌ src/main.py nicht gefunden!"
    echo "Stelle sicher, dass du im Projektverzeichnis bist:"
    echo "  cd ~/Dokumente/vsCode/Benning-DGUV3/Software/PRG"
    exit 1
fi

print_success "Projektverzeichnis gefunden"

# Überprüfe venv
if [ ! -f "venv/bin/python" ]; then
    echo "❌ Virtual Environment nicht gefunden!"
    exit 1
fi

print_success "Virtual Environment gefunden"

# Setze Python-Pfad
export PYTHONPATH="${PWD}:${PYTHONPATH}"

print_info "Python-Pfad: $PYTHONPATH"
print_info "Python: $(venv/bin/python --version)"

# Überprüfe Konfiguration
if [ ! -f ".env" ]; then
    print_info "Erstelle .env aus .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env erstellt"
    else
        print_info ".env.example nicht gefunden - verwende Defaults"
    fi
fi

print_header "✨ Starte Anwendung"

echo -e "${YELLOW}Öffne Browser:${NC}"
echo "  http://localhost:5000"
echo ""
echo -e "${YELLOW}Zum Beenden:${NC}"
echo "  Ctrl+C"
echo ""

# Starte Anwendung mit korrektem Pfad
cd "$(dirname "$0")" || exit 1
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Nutze die venv Python
exec venv/bin/python -c "
import sys
import os
sys.path.insert(0, os.getcwd())
from src.main import create_app
app = create_app()
print('🚀 Benning Device Manager startet...')
print('📍 http://localhost:5000')
print('🔧 Debug-Modus: aktiviert')
print('')
app.run(host='0.0.0.0', port=5000, debug=True)
"
