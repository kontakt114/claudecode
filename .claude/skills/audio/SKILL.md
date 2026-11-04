---
name: audio
description: Komplette Audio-Nachbearbeitung für eine Podcast-Folge aus Google Drive - Pausen über 1 s kürzen, Transkript (TXT + SRT), Kapitelmarken in der MP3, Shownotes mit Titelvorschlägen, drei Zitat-Clips als 9:16-Audiogramme mit Captions; Texte zurück in den Drive-Ordner der Quelle. Nutzen, wenn der User eine Folge/Aufnahme "fertig machen", kürzen und transkribieren will oder /audio mit einem Drive-Link aufruft.
---

# /audio

Pausen kürzen + Transkript + Kapitel + Shownotes + Clips + Ablage in Drive. Ein Lauf, keine Rückfragen, wenn ein Link da ist. Will der User nur einen Teil ("nur Pausen und Transkript"), nur den machen.

Werkzeuge:
- `python3 -I reel/reel.py fetch FILE_ID OUT` - Drive-Datei laden
- `python3 -I audio/pausen.py IN OUT [--max 1.0] [--noise DB] [--dry-run]` - Pausen kürzen (Details: Skill `pausen`)
- `python3 -I audio/transkript.py IN BASE [--prompt "Namen"]` - BASE.txt + BASE.srt
- `python3 -I audio/extras.py chapters|clip|audiogram ...` - Kapitelmarken, Zitat-Clips, 9:16-Audiogramme (`-h`)

## Fest eingetragen
- **Host:** Gordon Schönwälder. Whisper hört den Nachnamen falsch (Schönenwälder, Schönmelder). `transkript.py` korrigiert das automatisch. In Captions immer `--fix`, in Shownotes und Clip-Texten genau so schreiben.
- **Podcast:** hauptberuflich depressiv (klein geschrieben, wie im Intro). Audiogramm: `--show "hauptberuflich depressiv"`.

Arbeitsordner: neuer Unterordner im Scratchpad. Mediendateien nie ins Repo committen.

## Ablauf

1. **Metadaten:** Drive-Tool `get_file_metadata` mit der ID aus `/d/<ID>/`. Merken: `title` (Dateiname), `fileExtension`, `parentId` (Zielordner).
2. **Laden:** `fetch <ID> src.<ext>`.
3. **Pausen messen:** `pausen.py src.<ext> x.<ext> --dry-run`, dann mit `--noise` ±5 dB um die gemeldete Schwelle. Die Zahl der Pausen soll stabil bleiben. Bei Ersparnis über 40 % oder sehr wenigen Pausen: Schwelle nach Skill `pausen` anpassen.
4. **Schneiden:** direkt in den Zielnamen `<titel>_gekuerzt.<ext>`. Danach nichts mehr umbenennen.
5. **Kontrolle:** `pausen.py <gekuerzt> x --max 1.05 --noise <Schwelle> --dry-run`. Erwartet: praktisch 0 s gespart.
6. **Transkript im Hintergrund** (`run_in_background`, ~1 min Rechenzeit pro 2 min Audio):
   `transkript.py <gekuerzt> <titel>_transkript`
   Immer aus der **gekürzten** Datei, damit die Zeitmarken zur Endfassung passen. Host und Podcast sind fest eingetragen (siehe unten), Prompt und Namenskorrektur laufen automatisch. Für andere Gäste oder Begriffe `--prompt` ergänzen, Namen nie raten. Die gekürzte MP3 schon vorher mit `SendUserFile` schicken.
7. **Kapitel:** Das Transkript ganz lesen. 8–12 Kapitel an inhaltlichen Wendepunkten setzen, meist dort, wo der Host selbst eine neue Frage stellt. Titel kurz, konkret, in seinen Worten. Erstes Kapitel bei 00:00. Als `kapitel.txt` (`mm:ss Titel`), dann:
   `extras.py chapters <gekuerzt> <titel>_final.<ext> kapitel.txt` schreibt ID3-Kapitel (nur MP3), das Audio wird kopiert. Mit `ffprobe -show_chapters` prüfen.
8. **Shownotes** `<titel>_shownotes.txt`: 3 Titelvorschläge, Beschreibung (3–4 kurze Absätze, Ich-Form des Hosts, kein Werbesprech), Kapitelliste `mm:ss Titel` (Spotify macht daraus Kapitel), Feedback-Aufruf, Clip-Texte. Nichts erfinden, was nicht in der Folge vorkommt. Platzhalter für Links in `[...]`. Bei Themen wie Depression oder Krise: Hinweis auf die Telefonseelsorge (0800 111 0 111 / 0800 111 0 222).
9. **Zitat-Clips:** 3 Stellen, 25–40 s, die ohne Kontext funktionieren: ein klarer Satz, ein Bild, eine Wendung.
   ```bash
   python3 -I audio/extras.py clip <gekuerzt> clipN.mp3 --from mm:ss --to mm:ss   # rastet auf Pausen ein
   python3 -I reel/reel.py transcribe clipN.mp3 clipN.json --prompt "Gordon Schönwälder, hauptberuflich depressiv, ACT"   # Wortzeiten
   ```
   Die ersten Wörter in `clipN.json` prüfen. Beginnt der Clip mit einem Satzrest, Startzeit = Lücke vor dem ersten echten Wort, neu schneiden mit `--exact`, neu transkribieren. Dasselbe fürs Ende.
   ```bash
   python3 -I reel/reel.py captions clipN.json clipN.ass --fix Schönenwälder=Schönwälder --fix Schönmelder=Schönwälder
   python3 -I audio/extras.py audiogram clipN.mp3 clipN.ass clipN.mp4 --show "<Podcast-Name>" --hook 'Zeile 1\NZeile 2'
   ```
   Hook: max. 2 kurze Zeilen, sagt den Kern des Clips. Ein Standbild ziehen (`ffmpeg -ss 12 -i clipN.mp4 -frames:v 1 f.png`) und ansehen.
10. **Drive-Ablage:** TXT-Transkript und Shownotes je mit `create_file` in `parentId`: `textContent` = Dateiinhalt (vorher komplett lesen), `contentMimeType: text/plain`, `disableConversionToGoogleType: true`. Danach `fileSize` aus der Antwort mit `wc -c` vergleichen.
11. **Liefern:** `SendUserFile`: finale MP3, TXT, SRT, Shownotes (`attach`), die Clip-Videos (`render`).

## Was nicht nach Drive geht
- **MP3/Video:** Das Drive-Tool nimmt Inhalte nur inline. 40 MB Audio sind dafür zu groß, einen anderen Drive-Zugang gibt es im Container nicht. Finale MP3 und Clips legt der User selbst in den Ordner. Den Ordner-Link nennen: `https://drive.google.com/drive/folders/<parentId>`.
- **SRT:** nur auf Wunsch hochladen, wie TXT, aber mit `contentMimeType: application/x-subrip`. Sie ist etwa 1,4-mal so groß wie die TXT.

## Bericht
- Pausen: Anzahl, gesparte Zeit, alte → neue Länge, längste Pause vorher, Schwelle, Stabilität ±5 dB.
- Transkript: Zeilen, Wörter. Stellen nennen, an denen Whisper andere Namen unterschiedlich schreibt.
- Kapitel: die Liste. Clips: Zitat, Länge, Hook.
- Lautheit nur messen (`ffmpeg -af ebur128=peak=true`), nicht ändern. Melden, falls weit weg von −16 LUFS.
- Drive: was liegt im Ordner, was der User noch hochladen muss.
- Hinweis: Der Container ist vergänglich.

## Wenn etwas hakt
- `fetch` 403 / HTML statt Datei: siehe Skill `pausen`.
- Whisper lädt das Modell beim ersten Lauf (~1,5 GB). Bricht der Lauf ab, Ausgabe-Log lesen, nicht blind neu starten.
