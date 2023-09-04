#!/bin/bash

# Finde den Pfad zur Python3-Installation
PYTHON_PATH=$(which python3)

# Überprüfe, ob Python3 gefunden wurde
if [ -z "$PYTHON_PATH" ]; then
    echo "Python3 wurde nicht gefunden. Bitte stellen Sie sicher, dass es installiert ist."
    exit 1
fi

# Bestimme die Shell des Benutzers
if [[ "$SHELL" == "/bin/zsh" ]]; then
    PROFILE_FILE="$HOME/.zshrc"
elif [[ "$SHELL" == "/bin/bash" ]]; then
    PROFILE_FILE="$HOME/.bash_profile"
else
    echo "Unbekannte Shell: $SHELL. Das Skript unterstützt zsh und bash."
    exit 1
fi

# Füge Python zum PATH hinzu, falls noch nicht vorhanden
if ! grep -q "$PYTHON_PATH" "$PROFILE_FILE"; then
    echo "export PATH=\"$PYTHON_PATH:\$PATH\"" >> "$PROFILE_FILE"
    echo "Python3 wurde zum PATH in $PROFILE_FILE hinzugefügt."
else
    echo "Python3 ist bereits im PATH in $PROFILE_FILE."
fi

# Aktualisiere die aktuelle Shell-Sitzung
source "$PROFILE_FILE"

echo "Fertig!"
