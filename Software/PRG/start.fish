#!/usr/bin/env fish

# Benning Device Manager - Start Script mit .env Unterstützung

source venv/bin/activate.fish
set -x PYTHONPATH (pwd):$PYTHONPATH

# Lade .env Datei
if test -f ".env"
    set -gx DOTENV_LOADED true
    echo "✓ .env Datei geladen"
end

# Finde freien Port
set PORT 5000
while ss -tlnp 2>/dev/null | grep -q ":$PORT "
    set PORT (math $PORT + 1)
end

echo "🚀 Benning Device Manager"
echo "📍 http://localhost:$PORT"
echo "🗄️  MySQL Port: 3307"
echo ""

python -c "
import sys
import os
from pathlib import Path

# Lade .env Datei
env_file = Path('.env')
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

sys.path.insert(0, '.')
from src.main import create_app
app = create_app()
app.run(host='0.0.0.0', port=$PORT, debug=True)
"
