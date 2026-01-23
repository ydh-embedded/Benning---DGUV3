#!/usr/bin/env fish

source venv/bin/activate.fish
set -x PYTHONPATH (pwd):$PYTHONPATH

# Finde freien Port
set PORT 5000
while ss -tlnp 2>/dev/null | grep -q ":$PORT "
    set PORT (math $PORT + 1)
end

echo "🚀 Starte auf Port $PORT"
echo "📍 http://localhost:$PORT"
echo ""

python -c "
import sys
sys.path.insert(0, '.')
from src.main import create_app
app = create_app()
app.run(host='0.0.0.0', port=$PORT, debug=True)
"
