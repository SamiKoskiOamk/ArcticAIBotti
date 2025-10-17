#Tämä scripti käynnistää virtual environmentin bottidevausta varten
# Ajetaan source start_venv.sh

#!/bin/bash
# start_venv.sh

PROJECT_DIR="$HOME/Intrabot"
VENV_DIR="$PROJECT_DIR/intrabot-venv"

cd "$PROJECT_DIR" || exit 1

# Luo venv jos sitä ei ole
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtuaaliympäristöä ei löytynyt, luodaan uusi..."
    python3 -m venv "$VENV_DIR" || { echo "Venvin luonti epäonnistui"; exit 1; }
fi

# Aktivoi venv nykyisessä shellissä
echo "Aktivoidaan virtuaaliympäristö..."
source "$VENV_DIR/bin/activate"

# Tarkista että ollaan venvissä
echo "Python-polku: $(which python3)"
echo "Virtuaaliympäristö aktivoitu."
