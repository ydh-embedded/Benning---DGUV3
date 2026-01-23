# Benning Device Manager - Flask Edition

Leichtgewichtige Web-Anwendung für Geräte-Management und DGUV3-Prüfungen.

## Features

- ✅ Dashboard mit Statistiken
- ✅ Schnellerfassung für neue Geräte
- ✅ Geräteliste mit Details
- ✅ QR-Code-Generierung
- ✅ Dark Rose-Gold Theme
- ✅ MySQL-Datenbank

## Installation

```bash
cd ~/Dokumente/vsCode/Benning-DGUV3/Software/PRG
source venv/bin/activate  # oder venv/bin/activate.fish für Fish Shell
python app.py
```

## Datenbank

Verwenden Sie `install_py_db.sh` zur Einrichtung der MySQL-Datenbank.

## Technologie

- Python 3.8+
- Flask 3.0
- MySQL 8.0
- QRCode
- ReportLab

## Dateien

- `app.py` - Haupt-Anwendung
- `templates/` - HTML-Templates
- `static/css/` - Stylesheets
- `.env` - Konfiguration (nicht in Git)

## Lizenz

Proprietär - Benning Device Manager
