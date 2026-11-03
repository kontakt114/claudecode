---
name: pausen
description: Kürzt in einer Audio- oder Videodatei jede Pause über einer Sekunde (oder einem anderen Wert) auf genau diese Länge, mit weichen Übergängen und bei Video lippensynchron. Nutzen, wenn der User Pausen kürzen, Stille entfernen, Luft rausnehmen oder ein Podcast/Interview straffen will oder /pausen aufruft.
---

# /pausen

Werkzeug: `python3 -I audio/pausen.py IN OUT [--max 1.0] [--noise -40] [--dry-run]`

Arbeitsordner: neuer Unterordner im Scratchpad. Mediendateien nie ins Repo committen.

## Briefing

| Feld | Default |
|---|---|
| Quelle | Drive-Link → File-ID aus `/d/<ID>/` |
| Max. Pause | 1,0 s (`--max`) |
| Ausgabe | Gleiches Format wie die Quelle (Endung von OUT bestimmt den Codec: .mp3 .m4a .wav .flac .ogg .opus, Video → .mp4) |

Keine Rückfragen, wenn ein Link da ist. Andere Länge nur, wenn der User sie nennt.

## Ablauf

```bash
python3 -I reel/reel.py fetch <FILE_ID> src.<endung>     # Drive, "Jeder mit dem Link"
python3 -I audio/pausen.py src.<endung> out.<endung> --dry-run   # erst messen
python3 -I audio/pausen.py src.<endung> out.<endung>
python3 -I audio/pausen.py out.<endung> x --max 1.05 --noise <Schwelle aus Lauf 1> --dry-run   # Kontrolle: 0 Pausen
```

Die Endung von `src` aus dem Drive-Dateinamen nehmen (Metadaten via Drive-Tool `get_file_metadata`).

### Schwelle prüfen
Das Werkzeug setzt die Schwelle automatisch: 15 dB unter der Sprechlautstärke, mindestens 6 dB über dem Grundrauschen, begrenzt auf −50 bis −25 dB. Im `--dry-run` auf Plausibilität achten:
- **Sehr wenige Pausen** bei einer langen Aufnahme, oder Grundrauschen nahe an der Sprache (Musikbett, Lüfter, Raumhall): Die Schwelle ist zu niedrig. Mit `--noise` 3–5 dB höher erneut messen.
- **Auffällig viele Pausen, Ersparnis über 40 %:** Die Schwelle ist zu hoch, leise Wörter könnten als Pause zählen. Mit `--noise` niedriger messen.
Die Zahl soll stabil bleiben, wenn man die Schwelle um ±5 dB verschiebt. Bleibt sie stabil, passt die Schwelle.

## Was das Werkzeug macht
- Pausen ≤ max bleiben unangetastet. Längere werden in der Mitte gekürzt, je max/2 bleibt vor und nach dem Satz stehen.
- Klicks und Rascheln unter 60 ms zählen zur Pause.
- 5 ms Blende an jeder Schnittstelle, ändert die Länge nicht.
- Video: Schnitte liegen auf dem Bildraster, Bild und Ton bleiben synchron. Das Bild wird neu kodiert (H.264, CRF 18).

## Liefern
- `SendUserFile` mit absolutem Scratchpad-Pfad (Audio: `display: attach`, Video: `render`).
- Berichten: Anzahl gekürzter Pausen, gesparte Zeit, alte → neue Länge, die längste Pause vorher, die Schwelle.
- Hinweis: Der Container ist vergänglich, die Datei runterladen.

## Wenn etwas hakt
- `fetch` 403: Domain `drive.usercontent.google.com` fehlt in den Netzwerk-Einstellungen. HTML statt Datei: Freigabe fehlt.
- Sehr lange Dateien (> 2 h) brauchen viel RAM (ca. 0,7 GB pro Stunde Stereo). Bei Speicherproblemen in Teilen verarbeiten.
