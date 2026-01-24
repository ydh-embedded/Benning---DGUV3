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
    echo "FLASK_ENV=development" > .env
    echo "FLASK_DEBUG=True" >> .env
    echo "SECRET_KEY=dev-secret-key-change-in-production" >> .env
    echo "DB_HOST=localhost" >> .env
    echo "DB_PORT=3307" >> .env
    echo "DB_USER=benning" >> .env
    echo "DB_PASSWORD=benning" >> .env
    echo "DB_NAME=benning_device_manager" >> .env
    echo "UPLOAD_FOLDER=static/uploads" >> .env
    echo "MAX_CONTENT_LENGTH=10485760" >> .env
    echo "LOG_LEVEL=DEBUG" >> .env
end

echo "✓ Setup abgeschlossen!"
echo ""
echo "Starten mit: python src/main.py"
echo "Browser: http://localhost:5000"
