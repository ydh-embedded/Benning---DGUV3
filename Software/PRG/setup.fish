#!/usr/bin/env fish

# Benning Device Manager - Setup Script für Fish Shell

set PROJECT_DIR (pwd)

echo "🚀 Benning Device Manager Setup"
echo "================================"
echo ""

# 1. Virtual Environment
if not test -d "venv"
    echo "📦 Erstelle Virtual Environment..."
    python -m venv venv
end

echo "✓ Virtual Environment aktiviert"
source venv/bin/activate.fish

# 2. Pip upgrade
echo "📦 Upgrade pip..."
pip install --upgrade pip setuptools wheel -q

# 3. Abhängigkeiten
echo "📦 Installiere Abhängigkeiten..."
pip install -r requirements_hexagon.txt -q

echo "✓ Abhängigkeiten installiert"
echo ""

# 4. .env
if not test -f ".env"
    echo "⚙️  Erstelle .env Datei..."
    cat > .env << 'EOF'
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
DB_HOST=localhost
DB_PORT=3307
DB_USER=benning
DB_PASSWORD=benning
DB_NAME=benning_device_manager
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=10485760
LOG_LEVEL=DEBUG
EOF
end

echo "✓ Setup abgeschlossen!"
echo ""
echo "Starten mit: python src/main.py"
echo "Browser: http://localhost:5000"
