# Benning Device Manager - Hexagonal Architecture Edition

## 🏗️ Architektur

```
Web Layer (Flask)
       ↓
Ports (Abstraktion)
       ↓
Core (Geschäftslogik)
       ↓
Adapters (Implementierung)
```

## 📁 Verzeichnisstruktur

```
src/
├── core/              # Geschäftslogik
│   ├── domain/        # Domain Models
│   ├── usecases/      # Use Cases
│   └── ports/         # Abstraktion
├── adapters/          # Implementierungen
│   ├── persistence/   # Datenbank
│   └── web/           # Web-Framework
└── config/            # Konfiguration
```

## 🚀 Schnellstart

```bash
# 1. Aktiviere venv
source activate_cachyos.sh

# 2. Konfiguriere .env
cp .env.example .env
nano .env

# 3. Starte Anwendung
python src/main.py

# 4. Öffne Browser
# http://localhost:5000
```

## 📝 Befehle

```bash
pytest                  # Tests
black src/             # Formatieren
flake8 src/            # Linting
```
