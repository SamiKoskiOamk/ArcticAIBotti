#!/bin/bash

# Aktivoi venv ArcticAIBotti-projektille
VENV_PATH="$HOME/Hakubotti/.venv"

if [ -d "$VENV_PATH" ]; then
  echo "Aktivoidaan virtuaaliympäristö: $VENV_PATH"
  source "$VENV_PATH/bin/activate"
else
  echo "Virhe: Virtuaaliympäristöä ei löytynyt polusta $VENV_PATH"
fi
