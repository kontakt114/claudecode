"use client";

import { useState } from "react";
import { MOOD_EMOJI, MOOD_LABEL, MoodEntry, Tag, TAGS } from "@/lib/types";

type Mood = MoodEntry["mood"];

export function MoodCheckin({
  onComplete,
}: {
  onComplete: (mood: Mood, tag: Tag) => void;
}) {
  const [mood, setMood] = useState<Mood | null>(null);
  const [tag, setTag] = useState<Tag | null>(null);

  if (mood === null) {
    return (
      <div className="space-y-4">
        <p className="text-lg font-medium text-center">Wie fühlst du dich gerade?</p>
        <div className="flex justify-center gap-3">
          {([1, 2, 3, 4, 5] as Mood[]).map((m) => (
            <button
              key={m}
              onClick={() => setMood(m)}
              className="flex flex-col items-center gap-1 rounded-xl border border-zinc-200 p-3 text-2xl transition hover:scale-110 hover:border-zinc-400"
              aria-label={MOOD_LABEL[m]}
            >
              <span>{MOOD_EMOJI[m]}</span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (tag === null) {
    return (
      <div className="space-y-4">
        <p className="text-lg font-medium text-center">Was prägt dein Gefühl gerade am meisten?</p>
        <div className="flex flex-wrap justify-center gap-2">
          {TAGS.map((t) => (
            <button
              key={t}
              onClick={() => {
                setTag(t);
                onComplete(mood, t);
              }}
              className="rounded-full border border-zinc-200 px-4 py-2 text-sm transition hover:border-zinc-400 hover:bg-zinc-50"
            >
              {t}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return null;
}
