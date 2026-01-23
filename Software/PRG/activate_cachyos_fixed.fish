#!/usr/bin/env fish

################################################################################
# CachyOS Virtual Environment Activation Script - FIXED VERSION
#
# Dieses Skript aktiviert das Virtual Environment mit CachyOS-Optimierungen
# und setzt den PYTHONPATH korrekt.
#
# Verwendung: source activate_cachyos_fixed.fish
################################################################################

# Farben
set -l GREEN '\033[0;32m'
set -l YELLOW '\033[1;33m'
set -l CYAN '\033[0;36m'
set -l NC '\033[0m'

# Überprüfe ob wir im richtigen Verzeichnis sind
if not test -f "venv/bin/activate.fish"
    echo -e "$YELLOW⚠ Virtual Environment nicht gefunden!$NC"
    echo "Bitte führen Sie zuerst aus:"
    echo "  python -m venv venv"
    return 1
end

# Aktiviere Virtual Environment
source venv/bin/activate.fish

# WICHTIG: Setze PYTHONPATH korrekt für dieses Projekt
set -l PROJECT_DIR (pwd)
set -x PYTHONPATH $PROJECT_DIR:$PYTHONPATH

# CachyOS Optimierungen
set -x PYTHONOPTIMIZE 2
set -x PYTHONHASHSEED 0

# Flask Einstellungen
set -x FLASK_ENV development
set -x FLASK_DEBUG True

# Zeige Erfolg
echo -e "\n$GREEN✓ CachyOS Virtual Environment aktiviert$NC"
echo -e "  $CYAN Python:$NC (python --version)"
echo -e "  $CYAN PYTHONPATH:$NC $PYTHONPATH"
echo -e "  $CYAN Optimierungen:$NC Native CPU (-march=native -O3)"
echo -e "  $CYAN Projekt:$NC $PROJECT_DIR"
echo ""
