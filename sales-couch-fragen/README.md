# Reel-Fragen · Die Sales Couch

Ein Fragen-Generator für Reels. Prinzip: dokumentieren statt erfinden.
Du denkst dir kein Thema aus. Du beantwortest eine Frage zu deinem Tag.

Alles steckt in einer Datei: `index.html`. Kein Server, keine Installation.

---

## 1. API-Key in der Claude Console anlegen

1. Öffne [console.anthropic.com](https://console.anthropic.com) und melde dich an (oder registriere dich).
2. Unter **Settings → Billing** Guthaben aufladen. Ohne Guthaben funktioniert der Key nicht.
3. Unter **Settings → API Keys** auf **Create Key** klicken.
4. Einen Namen vergeben, z. B. `Reel-Fragen`, und bestätigen.
5. Den Key (beginnt mit `sk-ant-…`) sofort kopieren. Er wird nur einmal angezeigt.

Tipp: Unter **Settings → Limits** kannst du ein monatliches Ausgabenlimit setzen. Eine Runde Fragen kostet nur Bruchteile eines Cents.

**Wichtig:** Der Key liegt nur im Browser des Geräts, auf dem du ihn einträgst (localStorage). Gib die Datei weiter – der Key geht nicht mit. Teile das Gerät nicht mit Leuten, die den Key nicht haben sollen. Wenn du den Verdacht hast, dass er in falsche Hände geraten ist: in der Console löschen und neu anlegen.

## 2. Datei öffnen

**Am Rechner:** Doppelklick auf `index.html`. Sie öffnet sich im Browser.

**Beim ersten Start** fragt die Seite nach dem API-Key. Einfügen, **Speichern**, fertig.
Ohne Key läuft die Seite trotzdem – dann kommen die Fragen aus einem festen Pool von 60 Fragen.

Über das Zahnrad oben rechts kannst du den Key ändern oder löschen und den Verlauf leeren.

**Aufs Handy bringen:** Damit „Zum Homescreen“ sauber klappt, sollte die Datei über eine Web-Adresse erreichbar sein, nicht als lokale Datei. Einfache Wege:

- **GitHub Pages:** Repository → **Settings → Pages** → Branch auswählen → speichern. Danach ist die Seite unter `https://<nutzername>.github.io/<repo>/sales-couch-fragen/` erreichbar.
- **Netlify Drop:** [app.netlify.com/drop](https://app.netlify.com/drop) öffnen und den Ordner `sales-couch-fragen` hineinziehen. Du bekommst sofort eine Adresse.
- Oder die Datei auf die eigene Website hochladen.

Die Seite enthält keinen Key. Du kannst sie also öffentlich hosten. Den Key trägst du dann auf dem Handy einmal selbst ein.

## 3. Auf den Homescreen legen

**iPhone (Safari):**
1. Adresse in Safari öffnen.
2. Unten auf das **Teilen-Symbol** tippen (Quadrat mit Pfeil nach oben).
3. **Zum Home-Bildschirm** wählen.
4. Namen bestätigen (`Reel-Fragen`) → **Hinzufügen**.

**Android (Chrome):**
1. Adresse in Chrome öffnen.
2. Oben rechts auf die **drei Punkte** tippen.
3. **Zum Startbildschirm hinzufügen** wählen → **Hinzufügen**.

Danach startet die Seite wie eine App, im Vollbild, im Dark Mode.

Hinweis: Der Homescreen-Eintrag hat seinen eigenen Speicher. Beim ersten Öffnen vom Homescreen fragt die Seite deshalb noch einmal nach dem Key.

---

## Anpassen

Oben im `<script>`-Teil von `index.html` stehen die Stellschrauben:

- `MODEL` – das Modell. Standard ist `claude-sonnet-5`. Für schneller und günstiger: `claude-haiku-4-5`.
- `SYSTEM_PROMPT` – Ton und Regeln für die Fragen.
- `TOPICS` – die drei Themenfelder und ihre Stichworte.
- `POOL` – die 60 Fallback-Fragen, 20 pro Themenfeld.
- `HISTORY_LIMIT` – wie viele alte Fragen gegen Wiederholungen mitgeschickt werden (Standard: 50).

## Was die Seite speichert

Alles im localStorage des Browsers, nichts auf einem Server:

- deinen API-Key,
- die letzten 50 Fragen (damit nichts doppelt kommt),
- deine gemerkten Fragen,
- den zuletzt gewählten Filter.

Die Stichworte aus „Was war heute los?“ gehen nur an die Claude-API und werden nicht gespeichert.
