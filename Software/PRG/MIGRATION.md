# Migrationsanleitung: Von Monolith zu Hexagonaler Architektur

## Übersicht

Diese Anleitung beschreibt die schrittweise Migration vom alten monolithischen Code zur neuen hexagonalen Architektur.

## Phase 1: Parallele Implementierung

1. Neue Struktur wurde bereits erstellt
2. Alte `app.py` bleibt unverändert
3. Neue Module unter `src/` werden parallel entwickelt

## Phase 2: Schrittweise Route-Migration

### Schritt 1: Device Routes migrieren

```python
# Alt (app.py)
@app.route('/devices')
def devices():
    conn = get_db_connection()
    # ... Logik ...

# Neu (src/adapters/web/routes/device_routes.py)
@device_bp.route('/')
def list_devices(self):
    devices = self.list_devices_uc.execute()
    # ... Response ...
```

### Schritt 2: Use Cases verwenden

```python
# Alt: Geschäftslogik in Route
# Neu: Geschäftslogik in Use Case
device = self.get_device_uc.execute(device_id)
```

## Phase 3: Datenbank-Adapter

Die MySQL-Implementierung befindet sich in:
- `src/adapters/persistence/mysql_device_repository.py`

Dies ermöglicht einfachen Wechsel zu anderen Datenbanken.

## Phase 4: Alte Struktur entfernen

Nach vollständiger Migration können gelöscht werden:
- Alte `app.py`
- Alte Hilfsfunktionen
- Alte Route-Implementierungen

## Rollback-Strategie

Falls Probleme auftreten:

1. Alte `app.py` ist noch vorhanden
2. Kann jederzeit als Fallback verwendet werden
3. Neue Struktur läuft parallel

## Testing während Migration

```bash
# Alte Tests
pytest tests/old/

# Neue Tests
pytest tests/unit/
pytest tests/integration/

# Beide
pytest
```

## Häufige Probleme

### Problem: Import-Fehler

```
ModuleNotFoundError: No module named 'src'
```

**Lösung**: Stelle sicher, dass `src/` im Python-Pfad ist:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Problem: Datenbank-Verbindung

**Lösung**: Überprüfe `.env` Datei und Datenbank-Konfiguration

### Problem: Fehlende Dependencies

**Lösung**: Installiere alle Requirements:

```bash
pip install -r requirements_hexagon.txt
```

## Zeitplan

- **Woche 1**: Core & Use Cases implementieren
- **Woche 2**: Adapter implementieren
- **Woche 3**: Routes migrieren
- **Woche 4**: Testing & Dokumentation

## Support

Bei Fragen oder Problemen siehe:
- `README_HEXAGON.md` - Überblick
- `src/` - Quellcode mit Dokumentation
- `tests/` - Beispiel-Tests
