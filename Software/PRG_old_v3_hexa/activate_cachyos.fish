#!/usr/bin/env fish

# CachyOS Virtual Environment Aktivierungsskript für fish shell
# Verwendung: source activate_cachyos.fish

set -l PROJECT_DIR (cd (dirname (status -f)) && pwd)
set -l VENV_DIR "$PROJECT_DIR/venv"

if not test -d "$VENV_DIR"
    echo "❌ Virtual Environment nicht gefunden: $VENV_DIR"
    return 1
end

# CachyOS Optimierungen
set -gx CFLAGS "-march=native -O3"
set -gx CXXFLAGS "-march=native -O3"
set -gx LDFLAGS "-march=native -O3"
set -gx PYTHONOPTIMIZE 2
set -gx PIP_NO_CACHE_DIR 1

# Aktiviere venv
source "$VENV_DIR/bin/activate.fish"

echo "✓ CachyOS Virtual Environment aktiviert"
echo "  Python: "(which python)
echo "  Optimierungen: Native CPU (-march=native -O3)"
