"use client";

import { useEffect, useState } from "react";
import { MoodCheckin } from "@/components/MoodCheckin";
import { PatternChart } from "@/components/PatternChart";
import { LeadGate } from "@/components/LeadGate";
import { addEntry, getEntries, isLeadCaptured, setLeadCaptured } from "@/lib/storage";
import { averageByWeekday, findInsight, shouldOfferLeadCapture } from "@/lib/patterns";
import { MoodEntry, Tag } from "@/lib/types";

export default function Home() {
  const [entries, setEntries] = useState<MoodEntry[]>([]);
  const [leadCaptured, setLeadCapturedState] = useState(false);
  const [justCheckedIn, setJustCheckedIn] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time hydration from localStorage on mount
    setEntries(getEntries());
    setLeadCapturedState(isLeadCaptured());
    setHydrated(true);
  }, []);

  if (!hydrated) return null;

  function handleCheckin(mood: MoodEntry["mood"], tag: Tag) {
    const entry: MoodEntry = {
      id: crypto.randomUUID(),
      mood,
      tag,
      createdAt: new Date().toISOString(),
    };
    setEntries(addEntry(entry));
    setJustCheckedIn(true);
  }

  const insight = findInsight(entries);
  const offerLeadCapture = shouldOfferLeadCapture(entries) && insight && !leadCaptured;
  const weekdayData = averageByWeekday(entries);

  return (
    <div className="min-h-screen bg-zinc-50 px-4 py-12">
      <main className="mx-auto flex max-w-md flex-col gap-8">
        <header className="text-center">
          <h1 className="text-2xl font-semibold text-zinc-900">Mood Check-in</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Ein Klick am Tag. Nach ein paar Einträgen zeigen wir dir dein Muster.
          </p>
        </header>

        <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
          {justCheckedIn ? (
            <p className="text-center text-zinc-600">
              Danke für deinen Eintrag heute! Komm morgen wieder. 🌱
            </p>
          ) : (
            <MoodCheckin onComplete={handleCheckin} />
          )}
        </section>

        {entries.length > 0 && (
          <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
            <h2 className="mb-3 text-sm font-medium text-zinc-700">
              Dein Verlauf ({entries.length} {entries.length === 1 ? "Eintrag" : "Einträge"})
            </h2>
            <PatternChart data={weekdayData} blurred={Boolean(offerLeadCapture)} />
          </section>
        )}

        {offerLeadCapture && insight && (
          <LeadGate
            insight={insight}
            onCaptured={() => {
              setLeadCaptured();
              setLeadCapturedState(true);
            }}
          />
        )}

        {leadCaptured && insight && (
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 text-center">
            <p className="font-semibold text-emerald-900">{insight.headline}</p>
            <p className="mt-1 text-sm text-emerald-700">{insight.detail}</p>
          </div>
        )}

        <footer className="text-center text-xs text-zinc-400">
          Dieses Tool dient der Selbstreflexion und ersetzt keine professionelle Diagnose oder
          Therapie. In akuten Krisen wende dich an die Telefonseelsorge: 0800 111 0 111.
        </footer>
      </main>
    </div>
  );
}
