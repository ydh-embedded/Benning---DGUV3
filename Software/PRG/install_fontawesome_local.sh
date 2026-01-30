#!/bin/bash

echo "🎨 Font Awesome lokal installieren"
echo "===================================="
echo ""

# Prüfe ob im richtigen Verzeichnis
if [ ! -d "static" ] || [ ! -d "templates" ]; then
    echo "❌ Fehler: Bitte führen Sie das Skript im PRG-Verzeichnis aus!"
    echo "   cd ~/Dokumente/vsCode/Benning-DGUV3/Software/PRG"
    exit 1
fi

# Prüfe ob Framework-Package existiert
if [ ! -d "../Tools/06_framework_package/fontawesome-free-7.1.0-web" ]; then
    echo "❌ Fehler: Font Awesome Package nicht gefunden!"
    echo "   Erwartet: ../Tools/06_framework_package/fontawesome-free-7.1.0-web"
    exit 1
fi

echo "📦 Kopiere Font Awesome CSS..."
cp -v ../Tools/06_framework_package/fontawesome-free-7.1.0-web/css/*.css static/css/

echo ""
echo "🔤 Kopiere Font Awesome Webfonts..."
cp -rv ../Tools/06_framework_package/fontawesome-free-7.1.0-web/webfonts static/

echo ""
echo "✅ Font Awesome wurde erfolgreich installiert!"
echo ""
echo "📋 Nächste Schritte:"
echo "  1. Kopieren Sie die aktualisierte base.html:"
echo "     cp ~/upload/base.html templates/"
echo ""
echo "  2. Flask neu starten:"
echo "     podman restart benning-flask"
echo ""
echo "  3. Testen Sie die Anwendung:"
echo "     http://localhost:5000"
echo ""
