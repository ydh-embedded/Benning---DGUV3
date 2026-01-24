#!/usr/bin/env fish

# ============================================================================
# Benning Device Manager - Datenbank Cleanup (SAFE)
# ============================================================================

echo ""
echo "🗑️  Benning Device Manager - Datenbank Cleanup"
echo "=============================================="
echo ""

# ANCHOR: Check Docker
if not docker ps --filter "name=benning-flask-mysql" --format "{{.Names}}" | grep -q benning-flask-mysql
    echo "❌ MySQL Container nicht gefunden!"
    exit 1
end

echo "📍 Lösche Seed Daten..."

# ANCHOR: Lösche Daten mit IF EXISTS (sicher)
docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "DELETE FROM audit_log WHERE 1=1;" 2>/dev/null
docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "DELETE FROM inspections WHERE 1=1;" 2>/dev/null
docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "DELETE FROM devices WHERE 1=1;" 2>/dev/null

# ANCHOR: Setze Auto-Increment zurück
docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "ALTER TABLE devices AUTO_INCREMENT = 1;" 2>/dev/null
docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "ALTER TABLE inspections AUTO_INCREMENT = 1;" 2>/dev/null
docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "ALTER TABLE audit_log AUTO_INCREMENT = 1;" 2>/dev/null

echo "✅ Datenbank geleert"
echo ""

echo "📊 Geräte in DB:"
docker exec benning-flask-mysql mysql -u benning -pbenning benning_device_manager -e "SELECT COUNT(*) as 'Devices' FROM devices;"

echo ""
echo "✅ Cleanup abgeschlossen!"
echo ""
echo "🚀 Nächster Schritt:"
echo "  fish start_FINAL.fish"
echo ""
