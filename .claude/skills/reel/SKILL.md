---
name: reel
description: Macht aus einem Talking-Head-Video (Google-Drive-Link oder Datei) ein fertiges 9:16-Reel im Podcast-Helden-Stil - Jump Cuts, Punch-ins, Wort-für-Wort-Captions, Hook, Serien-Badge, fliegende Effekte und Sounds. Nutzen, wenn der User ein Reel, Short oder TikTok aus einem Video will oder /reel aufruft.
---

# /reel

Ziel: **ein Durchlauf, ein fertiger Entwurf**. Nicht in zehn Runden suchen, was gut aussieht. Der Stil unten ist abgestimmt. Erst liefern, dann Feinheiten.

Werkzeug: `python3 -I reel/reel.py <befehl>` (alle Befehle mit `-h`). Arbeitsordner: ein neuer Unterordner im Scratchpad, z. B. `$SCRATCH/reel-<name>/`. Videos nie ins Repo committen.

## Briefing

Aus der Nachricht ziehen, sonst die Defaults nehmen. Höchstens **eine** Rückfrage, und nur wenn ohne Antwort nichts geht.

| Feld | Default |
|---|---|
| Quelle | Drive-Link → File-ID aus `/d/<ID>/` |
| Serie/Badge | `MOVEMBER · TAG <n> VON 30` (Tag = Tagesdatum im November), sonst kein Badge |
| Länge | 35–45 s. Erklärung des Themas bleibt **am Anfang** drin |
| Hook | Ein Satz, der in 2 s sagt, worum es geht. Max. 2 Zeilen, `\N` trennt |
| Pointe | Was am Ende passiert (z. B. Katze Copper). Ende **ruhig** lassen |

## Ablauf

```bash
R=reel/reel.py
python3 -I $R fetch <FILE_ID> src.mov             # Datei muss "Jeder mit dem Link" sein
python3 -I $R frames src.mov overview.jpg --every 4 # Video ansehen (Read auf das JPG)
python3 -I $R transcribe src.mov t_src.json         # Inhalt verstehen
```

Mit Transkript + Kontaktabzug entscheiden:
- **Was fliegt raus:** Grübeln, Bücken, Aus-dem-Bild-Gehen, leerer Raum → `--drop A:B`
- **Was bleibt trotz Stille:** stumme Gags, Reaktionen, Grinsen → `--protect A:B`
- **Ruhiges Ende:** Pointen-Szene mit `--protect` und `--nopunch` schützen, damit keine hektischen Mini-Schnitte entstehen
- Zu lang? Mit `assemble` inhaltlich kürzen (Stücke `DATEI:A:B` in Wunschreihenfolge). Füllsätze raus, Thema-Erklärung drin lassen.

```bash
python3 -I $R cut src.mov cut.mp4 --drop A:B --protect A:B --nopunch A:B
python3 -I $R transcribe cut.mp4 t.json             # Zeiten passend zum Schnitt
```

Transkript **Korrektur lesen**. Whisper verhört sich bei Namen und Fachwörtern. Bekannte Fälle:
`--fix Körper=Copper --fix November=Movember --fix Bad=Bart --fix Oberlippenbad=Oberlippenbart --fix Damenbad=Damenbart`
Nur `--fix` setzen, wenn das falsche Wort im Transkript wirklich vorkommt. Gesprochenes nicht glätten (O-Ton bleibt).

Pointen festlegen (2–4 Stück: Zahlen, Kraftwörter, Call to Action, der Gag):

```bash
python3 -I $R captions t.json cap.ass --fix ... --hook 'Satz eins\NSatz zwei' \
   --skip <Fenster vom fliegenden Text> --move <Bart-Fenster>:1740
python3 -I $R badge "MOVEMBER · TAG 9 VON 30" badge.ass
python3 -I $R fx fx.ass --big "S:E:45" --label "S:E:740:690:COPPER · 0 % BART" \
   --stache-start S --stache T:X:Y --stache T:X:Y --stache-end E
python3 -I $R sfx sfx
python3 -I $R render cut.mp4 reel.mp4 --ass cap.ass --ass fx.ass --ass badge.ass \
   --zoom A:B --zoom A:B --sound whoosh@T --sound thud@T --sound pop@T@0.6
python3 -I $R frames reel.mp4 check.jpg --every 3   # Ergebnis prüfen, dann liefern
```

### Effekt-Regeln
- **Harter Zoom** (`--zoom`, 1.32) nur auf Pointen, nie im Pointen-Ende.
- **Fliegender Text** (`--big`): Zahl oder ein Wort. Im selben Fenster `--skip` bei den Captions, sonst doppelt. Sounds: `whoosh` 0.4 s vor Start+0.16, `thud` bei Start+0.16.
- **Schnurrbart** (`--stache`): Landet auf der Oberlippe. Positionen bestimmen: Frames im Fenster mit Raster ansehen:
  `ffmpeg -ss T -i cut.mp4 -frames:v 1 -vf "scale=iw*1.32:-2,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.28,drawgrid=w=108:h=96:t=2:c=red@0.6" g.png`
  (ohne `scale/crop`, wenn dort kein Zoom liegt). 3–4 Keyframes reichen. Captions im Fenster mit `--move …:1740` nach unten. Sounds: `whoosh` beim Start, `pop` bei der Landung.
- **Label** (`--label`): ploppt neben Haustier/Objekt auf, wenn es genannt wird. Sound: `pop`.

## Stil (fest)
- 1080×1920, H.264, −14 LUFS, Pausen > 0,5 s raus (Pad 0,15 s), Punch-in 1.18 jedes zweite Segment
- Captions: Inter Black 96, Versalien, aktives Wort gelb `#FFD400`, Mitte bei y=1450, 1–3 Wörter
- Hook: weiß auf schwarz, oben (y≈330), 3,2 s
- Badge: schwarz auf gelb, ganz oben (y≈190), durchgehend

## Liefern
- `SendUserFile` mit `display: render`, absoluter Pfad im Scratchpad.
- Kurz sagen, was drin ist, was du entschieden hast (Hook, Pointen, was rausflog) und welche Annahmen du getroffen hast (z. B. Tag-Nummer).
- Hinweisen: Der Container ist vergänglich, das Video runterladen.

## Wenn etwas hakt
- `fetch` → 403 vom Proxy: Domain `drive.usercontent.google.com` fehlt in den Netzwerk-Einstellungen. 404/HTML statt Video: Datei nicht auf "Jeder mit dem Link".
- `transcribe` lädt das Modell (1,5 GB) von `huggingface.co`, falls das Setup-Script es nicht vorgeladen hat.
- ffmpeg wird mit SIGKILL beendet: zu viele `trim`-Ketten in einem Filtergraph. `cut` arbeitet deshalb segmentweise, das nicht umbauen.
