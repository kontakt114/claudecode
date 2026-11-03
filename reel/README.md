# Reel-Pipeline

Talking-Head-Video rein, fertiges 9:16-Reel raus: Jump Cuts, Punch-ins, Wort-für-Wort-Captions, Hook, Serien-Badge, fliegende Effekte, Sounds.

## Benutzen

In einer Claude-Code-Session in diesem Repo:

```
/reel https://drive.google.com/file/d/<ID>/view  Movember Tag 9, ca. 40 s, Pointe: Copper am Ende
```

Der Ablauf und der Stil stehen in `.claude/skills/reel/SKILL.md`. Das Werkzeug ist `reel/reel.py` (`python3 reel/reel.py -h`).

## Einmalig einrichten

1. **Netzwerk** (Umgebung → *Edit* → *Network access* → *Allowed domains*):
   `drive.usercontent.google.com`, `huggingface.co`, `*.hf.co`
2. **Setup-Script** (Umgebung → *Edit* → *Setup script*): Inhalt von `reel/setup.sh` einfügen.

## Pro Video

- Video in Google Drive auf **„Jeder mit dem Link“** stellen. Nach dem Download kann die Freigabe wieder zurück.

## Pausen kürzen

`/pausen <Drive-Link>` kürzt jede Pause über einer Sekunde auf eine Sekunde. Das klappt für Audio und Video. Werkzeug: `audio/pausen.py`, Ablauf: `.claude/skills/pausen/SKILL.md`. Eine andere Länge gibst du im Briefing an, zum Beispiel `/pausen <Link> max 0,7 s`.
