#!/bin/bash
# Setup für die Reel-Pipeline. Inhalt in die Umgebungs-Einstellungen unter "Setup script" kopieren.
# Installiert die Spracherkennung und lädt das Modell vor, damit /reel sofort loslegen kann.
set -e
pip install -q faster-whisper
python3 -c "from faster_whisper import WhisperModel; WhisperModel('medium', device='cpu', compute_type='int8')"
