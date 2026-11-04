---
name: audio
description: Komplette Audio-Nachbearbeitung für eine Podcast-Folge aus Google Drive - Pausen über 1 s kürzen, Transkript (TXT + SRT) erstellen, Transkript zurück in den Drive-Ordner der Quelle legen. Nutzen, wenn der User eine Folge/Aufnahme "fertig machen", kürzen und transkribieren will oder /audio mit einem Drive-Link aufruft.
---

# /audio

Pausen kürzen + Transkript + Ablage in Drive. Ein Lauf, keine Rückfragen, wenn ein Link da ist.

Werkzeuge:
- `python3 -I reel/reel.py fetch FILE_ID OUT` - Drive-Datei laden
- `python3 -I audio/pausen.py IN OUT [--max 1.0] [--noise DB] [--dry-run]` - Pausen kürzen (Details: Skill `pausen`)
- `python3 -I audio/transkript.py IN BASE [--prompt "Namen"]` - BASE.txt + BASE.srt

Arbeitsordner: neuer Unterordner im Scratchpad. Mediendateien nie ins Repo committen.

## Ablauf

1. **Metadaten:** Drive-Tool `get_file_metadata` mit der ID aus `/d/<ID>/`. Merken: `title` (Dateiname), `fileExtension`, `parentId` (Zielordner).
2. **Laden:** `fetch <ID> src.<ext>`.
3. **Pausen messen:** `pausen.py src.<ext> x.<ext> --dry-run`, dann mit `--noise` ±5 dB um die gemeldete Schwelle. Die Zahl der Pausen soll stabil bleiben. Bei Ersparnis über 40 % oder sehr wenigen Pausen: Schwelle nach Skill `pausen` anpassen.
4. **Schneiden:** direkt in den Zielnamen `<titel>_gekuerzt.<ext>`. Danach nichts mehr umbenennen.
5. **Kontrolle:** `pausen.py <gekuerzt> x --max 1.05 --noise <Schwelle> --dry-run`. Erwartet: praktisch 0 s gespart.
6. **Transkript im Hintergrund** (`run_in_background`, ~1 min Rechenzeit pro 2 min Audio):
   `transkript.py <gekuerzt> <titel>_transkript --prompt "<Host-Name, Podcast-Titel>"`
   Immer aus der **gekürzten** Datei, damit die Zeitmarken zur Endfassung passen. Den Namen fürs `--prompt` aus früheren Transkripten oder vom User nehmen, nie raten. Die gekürzte MP3 schon vorher mit `SendUserFile` schicken.
7. **Drive-Ablage:** TXT mit `create_file` in `parentId`: `textContent` = Dateiinhalt (vorher komplett lesen), `contentMimeType: text/plain`, `disableConversionToGoogleType: true`. Danach `fileSize` aus der Antwort mit `wc -c` vergleichen.
8. **Liefern:** `SendUserFile` für TXT + SRT (`display: attach`).

## Was nicht nach Drive geht
- **MP3/Video:** Das Drive-Tool nimmt Inhalte nur inline. 40 MB Audio sind dafür zu groß, einen anderen Drive-Zugang gibt es im Container nicht. Die gekürzte Datei schickt der User selbst in den Ordner. Den Ordner-Link nennen: `https://drive.google.com/drive/folders/<parentId>`.
- **SRT:** nur auf Wunsch hochladen, wie TXT, aber mit `contentMimeType: application/x-subrip`. Sie ist etwa 1,4-mal so groß wie die TXT.

## Bericht
- Pausen: Anzahl, gesparte Zeit, alte → neue Länge, längste Pause vorher, Schwelle, Stabilität ±5 dB.
- Transkript: Zeilen, Wörter. Stellen nennen, an denen Whisper Namen unterschiedlich schreibt.
- Drive: was liegt im Ordner, was der User noch hochladen muss.
- Hinweis: Der Container ist vergänglich.

## Wenn etwas hakt
- `fetch` 403 / HTML statt Datei: siehe Skill `pausen`.
- Whisper lädt das Modell beim ersten Lauf (~1,5 GB). Bricht der Lauf ab, Ausgabe-Log lesen, nicht blind neu starten.
