#!/bin/bash
# start_intrabot.sh

# Projektikansio
PROJECT_DIR="$HOME/Intrabot"
VENV_DIR="$PROJECT_DIR/venv"

# Siirrytään projektikansioon
cd "$PROJECT_DIR" || exit

# Jos venv-kansiota ei ole, luodaan se
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtuaaliympäristöä ei löytynyt, luodaan uusi..."
    python3 -m venv intrabot
fi

# Aktivoidaan virtuaaliympäristö
echo "Aktivoidaan virtuaaliympäristö..."
source "$VENV_DIR/bin/activate"

# Jätetään käyttäjä aktiiviseen ympäristöön
exec "$SHELL"
