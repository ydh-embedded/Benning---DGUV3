# Benning Device Manager - Hexagonal Architecture

## Überblick

Dies ist eine Refactored-Version der Benning Device Manager Anwendung mit einer **hexagonalen Softwarearchitektur** (auch bekannt als Ports & Adapters Pattern).

## Architektur

### Struktur

```
src/
├── core/                    # Geschäftslogik (Framework-unabhängig)
│   ├── domain/             # Domain Models (Entities, Value Objects)
│   ├── usecases/           # Anwendungs-spezifische Geschäftsregeln
│   └── ports/              # Schnittstellen (Abstraktion)
├── adapters/               # Konkrete Implementierungen
│   ├── persistence/        # Datenbank-Adapter
│   ├── web/                # Web-Framework Adapter (Flask)
│   ├── file_storage/       # Datei-Speicherung
│   └── qr_generation/      # QR-Code Generierung
└── config/                 # Konfiguration & DI
```

## Installation

### 1. Virtuelle Umgebung erstellen

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows
```

### 2. Dependencies installieren

```bash
pip install -r requirements_hexagon.txt
```

### 3. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
# Bearbeite .env mit deinen Einstellungen
```

### 4. Datenbank initialisieren

```bash
# Stelle sicher, dass MySQL läuft
mysql -u root -p < database/schema.sql
```

### 5. Anwendung starten

```bash
python src/main.py
```

Die Anwendung läuft unter `http://localhost:5000`

## Vorteile der Hexagonalen Architektur

- **Testbarkeit**: Geschäftslogik ist vom Framework unabhängig
- **Wartbarkeit**: Klare Trennung der Verantwortlichkeiten
- **Flexibilität**: Adapter können einfach ausgetauscht werden
- **Wiederverwendbarkeit**: Use Cases können in verschiedenen Kontexten genutzt werden

## Testing

### Unit Tests ausführen

```bash
pytest tests/unit/
```

### Integration Tests ausführen

```bash
pytest tests/integration/
```

### Mit Coverage

```bash
pytest --cov=src tests/
```

## API-Endpoints

### Geräte

- `GET /devices` - Alle Geräte auflisten
- `GET /devices/<device_id>` - Gerät abrufen
- `POST /devices` - Neues Gerät erstellen

### Health Check

- `GET /health` - Anwendungs-Status

## Migrationsanleitung

Siehe `MIGRATION.md` für Anweisungen zur Migration vom alten Code.

## Lizenz

MIT
