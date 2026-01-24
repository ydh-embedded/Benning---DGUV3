#!/usr/bin/env fish

# ============================================================================
# Benning Device Manager - Startup mit Datenbank-Initialisierung
# ============================================================================

echo ""
echo "🚀 Benning Device Manager - Startup"
echo "===================================="
echo ""

# ANCHOR: Lade .env
if test -f .env
    echo "📋 Lade .env Datei..."
    set -x (cat .env | grep -v '^#' | grep -v '^$')
    echo "✅ .env geladen"
else
    echo "⚠️  .env nicht gefunden"
end

echo ""

# ANCHOR: Aktiviere Virtual Environment
if test -d venv
    echo "🐍 Aktiviere Virtual Environment..."
    source venv/bin/activate.fish
    echo "✅ venv aktiviert"
else
    echo "❌ venv nicht gefunden!"
    exit 1
end

echo ""

# ANCHOR: Überprüfe Datenbank
echo "🗄️  Überprüfe Datenbank..."

# Versuche Verbindung
set db_check (docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "SELECT COUNT(*) FROM devices;" 2>&1)

if string match -q "*ERROR*" $db_check
    echo "⚠️  Datenbank-Problem erkannt"
    echo "🔧 Initialisiere Datenbank..."
    
    # Führe Cleanup durch
    docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "DELETE FROM audit_log WHERE 1=1;" 2>/dev/null
    docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "DELETE FROM inspections WHERE 1=1;" 2>/dev/null
    docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "DELETE FROM devices WHERE 1=1;" 2>/dev/null
    docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "ALTER TABLE devices AUTO_INCREMENT = 1;" 2>/dev/null
    
    echo "✅ Datenbank initialisiert"
else
    echo "✅ Datenbank OK"
end

echo ""

# ANCHOR: Starte Flask App
echo "🌐 Starte Flask Anwendung..."
echo ""

# Finde freien Port
set port 5000
while netstat -tuln 2>/dev/null | grep -q ":$port "
    set port (math $port + 1)
end

echo "📍 Starte auf http://localhost:$port"
echo ""

# Setze PYTHONPATH
set -x PYTHONPATH (pwd):$PYTHONPATH

# Starte Flask
python src/main.py --host=0.0.0.0 --port=$port

echo ""
echo "✅ Anwendung beendet"
echo ""
