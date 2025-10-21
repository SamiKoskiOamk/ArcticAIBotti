#!/bin/bash
# run_web.sh
# Käynnistää paikallisen testipalvelimen ja avaa index.html-sivun selaimessa

PORT=8080
URL="http://127.0.0.1:$PORT/index.html"

echo "🌐 Käynnistetään paikallinen HTTP-palvelin porttiin $PORT..."
# Aja palvelin taustalle
python3 -m http.server $PORT >/dev/null 2>&1 &

SERVER_PID=$!
sleep 1

echo "🚀 Avataan sivu selaimessa: $URL"
# Linux/WSL
if command -v xdg-open &> /dev/null; then
  xdg-open "$URL"
# macOS
elif command -v open &> /dev/null; then
  open "$URL"
# Windows WSL
elif grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null; then
  powershell.exe start "$URL"
else
  echo "Avaa manuaalisesti selaimessa: $URL"
fi

# Odota, kunnes käyttäjä painaa Ctrl+C
echo "🛑 Paina Ctrl+C pysäyttääksesi palvelimen."
wait $SERVER_PID
