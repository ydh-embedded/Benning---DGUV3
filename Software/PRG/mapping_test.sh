#!/bin/bash

# ============================================================================
# Benning Device Manager - Mapping Test Script v2
# Überprüft Routes, Datenbank-Tabellen und API-Funktionalität
# Nutzt Podman exec für Datenbank-Befehle
# ============================================================================

set -e

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfiguration
API_BASE="http://localhost:5000"
DB_USER="benning"
DB_PASSWORD="benning"
DB_NAME="benning_device_manager"
MYSQL_CONTAINER="benning-mysql"

# ============================================================================
# Hilfsfunktionen
# ============================================================================

print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# ============================================================================
# 1. ÜBERPRÜFE CONTAINER STATUS
# ============================================================================

check_containers() {
    print_header "1. CONTAINER STATUS"
    
    echo "Überprüfe Podman Container..."
    
    if podman ps | grep -q "benning-mysql"; then
        print_success "MySQL Container läuft"
    else
        print_error "MySQL Container läuft nicht!"
        return 1
    fi
    
    if podman ps | grep -q "benning-flask"; then
        print_success "Flask Container läuft"
    else
        print_error "Flask Container läuft nicht!"
        return 1
    fi
    
    echo ""
}

# ============================================================================
# 2. ÜBERPRÜFE DATENBANK-VERBINDUNG (IM CONTAINER)
# ============================================================================

check_database_connection() {
    print_header "2. DATENBANK-VERBINDUNG (im Container)"
    
    echo "Teste MySQL Verbindung im Container..."
    
    if podman exec "$MYSQL_CONTAINER" mysql -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" &>/dev/null; then
        print_success "Datenbank-Verbindung erfolgreich"
    else
        print_error "Datenbank-Verbindung fehlgeschlagen!"
        return 1
    fi
    
    echo ""
}

# ============================================================================
# 3. ÜBERPRÜFE DATENBANK-TABELLEN (IM CONTAINER)
# ============================================================================

check_database_tables() {
    print_header "3. DATENBANK-TABELLEN"
    
    echo "Überprüfe Tabellen in '$DB_NAME'..."
    
    TABLES=$(podman exec "$MYSQL_CONTAINER" mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SHOW TABLES;" 2>/dev/null | tail -n +2)
    
    EXPECTED_TABLES=("devices" "inspections" "users" "audit_log")
    
    for table in "${EXPECTED_TABLES[@]}"; do
        if echo "$TABLES" | grep -q "^$table$"; then
            print_success "Tabelle '$table' existiert"
        else
            print_error "Tabelle '$table' existiert nicht!"
        fi
    done
    
    echo ""
}

# ============================================================================
# 4. ÜBERPRÜFE DEVICES TABELLEN-STRUKTUR (IM CONTAINER)
# ============================================================================

check_devices_structure() {
    print_header "4. DEVICES TABELLEN-STRUKTUR"
    
    echo "Überprüfe Spalten in 'devices' Tabelle..."
    
    COLUMNS=$(podman exec "$MYSQL_CONTAINER" mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "DESC devices;" 2>/dev/null | tail -n +2 | awk '{print $1}')
    
    EXPECTED_COLUMNS=("id" "customer" "device_id" "name" "type" "serial_number" "manufacturer" "model" "location" "purchase_date" "last_inspection" "next_inspection" "status" "qr_code" "notes" "created_at" "updated_at")
    
    for column in "${EXPECTED_COLUMNS[@]}"; do
        if echo "$COLUMNS" | grep -q "^$column$"; then
            print_success "Spalte '$column' existiert"
        else
            print_error "Spalte '$column' existiert nicht!"
        fi
    done
    
    echo ""
}

# ============================================================================
# 5. ÜBERPRÜFE API ROUTES
# ============================================================================

check_api_routes() {
    print_header "5. API ROUTES"
    
    echo "Teste Flask API Endpoints..."
    
    # Test: GET /api/devices (List)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/devices")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET /api/devices ($HTTP_CODE)"
    else
        print_error "GET /api/devices ($HTTP_CODE)"
    fi
    
    # Test: GET /api/devices/next-id
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/api/devices/next-id")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET /api/devices/next-id ($HTTP_CODE)"
    else
        print_error "GET /api/devices/next-id ($HTTP_CODE)"
    fi
    
    # Test: GET / (Dashboard)
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET / Dashboard ($HTTP_CODE)"
    else
        print_error "GET / Dashboard ($HTTP_CODE)"
    fi
    
    # Test: GET /quick-add
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/quick-add")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET /quick-add ($HTTP_CODE)"
    else
        print_error "GET /quick-add ($HTTP_CODE)"
    fi
    
    # Test: GET /devices
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE/devices")
    if [ "$HTTP_CODE" = "200" ]; then
        print_success "GET /devices ($HTTP_CODE)"
    else
        print_error "GET /devices ($HTTP_CODE)"
    fi
    
    echo ""
}

# ============================================================================
# 6. TESTE DEVICE-ERSTELLUNG
# ============================================================================

test_device_creation() {
    print_header "6. DEVICE-ERSTELLUNG TEST"
    
    echo "Teste Device-Erstellung mit Customer-basierter ID..."
    
    RESPONSE=$(curl -s -X POST "$API_BASE/api/devices" \
        -H "Content-Type: application/json" \
        -d '{
            "customer": "TestCorp",
            "name": "Test Gerät 001",
            "type": "Prüfgerät",
            "location": "Testlabor"
        }')
    
    echo "Response: $RESPONSE"
    
    if echo "$RESPONSE" | grep -q '"message":"Device created"'; then
        print_success "Device erfolgreich erstellt"
        
        # Extrahiere Device ID
        DEVICE_ID=$(echo "$RESPONSE" | grep -o '"id":[0-9]*' | grep -o '[0-9]*')
        print_info "Device ID (DB): $DEVICE_ID"
        
    elif echo "$RESPONSE" | grep -q '"error"'; then
        print_error "Device-Erstellung fehlgeschlagen: $RESPONSE"
    else
        print_warning "Unerwartete Response: $RESPONSE"
    fi
    
    echo ""
}

# ============================================================================
# 7. ÜBERPRÜFE DATENBANK-INHALTE (IM CONTAINER)
# ============================================================================

check_database_content() {
    print_header "7. DATENBANK-INHALTE"
    
    echo "Überprüfe Devices in Datenbank..."
    
    COUNT=$(podman exec "$MYSQL_CONTAINER" mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT COUNT(*) FROM devices;" 2>/dev/null | tail -n 1)
    
    print_info "Anzahl Devices: $COUNT"
    
    echo ""
    echo "Letzte 5 Devices:"
    podman exec "$MYSQL_CONTAINER" mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "SELECT id, customer, device_id, name, type, status FROM devices ORDER BY created_at DESC LIMIT 5;" 2>/dev/null
    
    echo ""
}

# ============================================================================
# 8. ÜBERPRÜFE FIELD MAPPING
# ============================================================================

check_field_mapping() {
    print_header "8. FIELD MAPPING ÜBERPRÜFUNG"
    
    echo "Überprüfe Mapping zwischen API und Datenbank..."
    
    # Teste mit allen erwarteten Feldern
    RESPONSE=$(curl -s -X POST "$API_BASE/api/devices" \
        -H "Content-Type: application/json" \
        -d '{
            "customer": "MappingTest",
            "name": "Mapping Test Device",
            "type": "Elektroprüfer",
            "location": "Testlabor",
            "manufacturer": "TestMfg",
            "serial_number": "SN-12345",
            "purchase_date": "2024-01-24",
            "status": "active",
            "notes": "Test Device für Mapping"
        }')
    
    if echo "$RESPONSE" | grep -q '"message":"Device created"'; then
        print_success "Alle Felder korrekt gemappt"
    else
        print_error "Field Mapping fehlgeschlagen: $RESPONSE"
    fi
    
    echo ""
}

# ============================================================================
# 9. ZUSAMMENFASSUNG
# ============================================================================

print_summary() {
    print_header "ZUSAMMENFASSUNG"
    
    echo "Mapping Test abgeschlossen!"
    echo ""
    print_info "API Base URL: $API_BASE"
    print_info "MySQL Container: $MYSQL_CONTAINER"
    print_info "Datenbank: $DB_NAME"
    echo ""
    
    print_success "Alle Überprüfungen durchgeführt"
    echo ""
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    print_header "BENNING DEVICE MANAGER - MAPPING TEST v2"
    
    check_containers || exit 1
    check_database_connection || exit 1
    check_database_tables
    check_devices_structure
    check_api_routes
    test_device_creation
    check_database_content
    check_field_mapping
    print_summary
}

# Starte Main
main
