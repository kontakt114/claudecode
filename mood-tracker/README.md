## Mood Check-in

Ein Mood-Tracker mit 3-Klick-Eingabe für Seiten rund um mentale Gesundheit. Nutzer trackt
seine Stimmung ohne Account; nach 5 Einträgen wird ein persönliches Muster erkannt
(z.B. "du fühlst dich montags am gestresstesten") und gegen eine E-Mail-Adresse
freigeschaltet.

### Lokal starten

```bash
npm install
npm run dev
```

Öffne http://localhost:3000. Ohne Supabase-Konfiguration funktioniert der Tracker komplett
lokal (LocalStorage); eingereichte E-Mails werden dann nur in der Server-Konsole geloggt.

### Mit Supabase persistieren

1. Supabase-Projekt anlegen, `supabase-schema.sql` im SQL-Editor ausführen.
2. `.env.example` zu `.env.local` kopieren und URL + Anon Key eintragen.
3. Neu starten – eingereichte Leads landen jetzt in der `leads`-Tabelle.

### Architektur

- `src/lib/types.ts` – Datenmodell (MoodEntry, Tags)
- `src/lib/storage.ts` – LocalStorage-Persistenz der Einträge
- `src/lib/patterns.ts` – Wochentags-Durchschnitt + Insight-Erkennung
- `src/components/MoodCheckin.tsx` – 3-Klick-Eingabeflow
- `src/components/PatternChart.tsx` – Balkendiagramm (geblurrt bis Lead erfasst)
- `src/components/LeadGate.tsx` – E-Mail-Formular zum Freischalten des Musters
- `src/app/api/lead/route.ts` – Speichert Leads in Supabase (falls konfiguriert)

### Nächste Schritte für Produktion

- E-Mail-Versand der Auswertung anbinden (z.B. Brevo/Mailchimp API in der `lead`-Route)
- Echtes Backend-Tracking statt reinem LocalStorage, falls Nutzer geräteübergreifend
  tracken sollen
- A/B-Test, ob das Muster vor oder nach der E-Mail-Abfrage angezeigt wird

---

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
