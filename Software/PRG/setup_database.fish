#!/usr/bin/env fish

# ============================================================================
# Benning Device Manager - Datenbank Setup Script
# ============================================================================
# Dieses Script erstellt eine saubere Datenbank und lädt das Schema

echo ""
echo "🗄️  Benning Device Manager - Datenbank Setup"
echo "=============================================="
echo ""

# ANCHOR: Check Docker
echo "📍 Überprüfe Docker..."
if not command -v docker &> /dev/null
    echo "❌ Docker nicht installiert!"
    exit 1
end
echo "✅ Docker vorhanden"
echo ""

# ANCHOR: Check MySQL Container
echo "📍 Überprüfe MySQL Container..."
set mysql_container (docker ps --filter "name=benning-flask-mysql" --format "{{.Names}}")

if test -z "$mysql_container"
    echo "❌ MySQL Container nicht gefunden!"
    echo "Starten Sie zuerst den Container:"
    echo "  docker run -d --name benning-flask-mysql -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=benning_device_manager -e MYSQL_USER=benning -e MYSQL_PASSWORD=benning -p 3307:3306 mysql:8.0"
    exit 1
end
echo "✅ MySQL Container läuft: $mysql_container"
echo ""

# ANCHOR: Wait for MySQL to be ready
echo "⏳ Warte auf MySQL Startup..."
sleep 3
echo "✅ MySQL bereit"
echo ""

# ANCHOR: Load schema
echo "📋 Lade Datenbankschema..."
docker exec benning-flask-mysql mysql -u benning -pbenning < benning_schema.sql

if test $status -eq 0
    echo "✅ Schema erfolgreich geladen"
else
    echo "❌ Fehler beim Laden des Schemas!"
    exit 1
end
echo ""

# ANCHOR: Verify database
echo "🔍 Überprüfe Datenbank..."
docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "SELECT COUNT(*) as 'Devices' FROM devices;"
echo ""

# ANCHOR: Show connection info
echo "✅ Datenbank erfolgreich erstellt!"
echo ""
echo "📊 Verbindungsinformationen:"
echo "  Host: localhost"
echo "  Port: 3307"
echo "  User: benning"
echo "  Password: benning"
echo "  Database: benning_device_manager"
echo ""

echo "🚀 Nächster Schritt:"
echo "  fish start_FINAL.fish"
echo ""
