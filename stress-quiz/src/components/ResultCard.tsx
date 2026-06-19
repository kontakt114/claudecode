"use client";

import { useState } from "react";
import { TypeContent } from "@/lib/types";

export function ResultCard({ content }: { content: TypeContent }) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "done" | "error">("idle");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("submitting");
    try {
      const res = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, resultType: content.title }),
      });
      if (!res.ok) throw new Error("Request failed");
      setStatus("done");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="space-y-5">
      <div className="rounded-2xl border border-zinc-200 bg-white p-6 text-center shadow-sm">
        <p className="text-sm text-zinc-400">Dein Ergebnis</p>
        <h2 className="mt-1 text-2xl font-semibold text-zinc-900">{content.title}</h2>
        <p className="mt-2 text-sm text-zinc-600">{content.summary}</p>
      </div>

      <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
        <h3 className="mb-3 text-sm font-medium text-zinc-700">Drei Tipps für dich</h3>
        <ul className="space-y-2">
          {content.tips.map((tip) => (
            <li key={tip} className="flex gap-2 text-sm text-zinc-700">
              <span className="text-indigo-600">•</span>
              <span>{tip}</span>
            </li>
          ))}
        </ul>
      </div>

      {status === "done" ? (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5 text-center text-sm text-emerald-800">
          Danke! Deine 5-Tage-Tipp-Serie zu &quot;{content.title}&quot; ist auf dem Weg in dein
          Postfach.
        </div>
      ) : (
        <div className="space-y-3 rounded-xl border border-indigo-200 bg-indigo-50 p-5 text-center">
          <p className="font-semibold text-indigo-900">Willst du mehr davon?</p>
          <p className="text-sm text-indigo-700">
            Wir schicken dir eine 5-Tage-Serie mit weiteren Tipps passend zu deinem Typ.
          </p>
          <form onSubmit={handleSubmit} className="flex flex-col gap-2 sm:flex-row">
            <input
              type="email"
              required
              placeholder="deine@email.de"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1 rounded-lg border border-indigo-300 px-3 py-2 text-sm"
            />
            <button
              type="submit"
              disabled={status === "submitting"}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-60"
            >
              {status === "submitting" ? "Wird gesendet…" : "Tipps zuschicken"}
            </button>
          </form>
          {status === "error" && (
            <p className="text-sm text-red-600">Da ist etwas schiefgelaufen. Versuch es nochmal.</p>
          )}
        </div>
      )}
    </div>
  );
}
