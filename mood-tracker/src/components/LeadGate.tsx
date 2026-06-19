"use client";

import { useState } from "react";
import { Insight } from "@/lib/patterns";

export function LeadGate({
  insight,
  onCaptured,
}: {
  insight: Insight;
  onCaptured: (email: string) => void;
}) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "submitting" | "error">("idle");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("submitting");
    try {
      const res = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, insightHeadline: insight.headline }),
      });
      if (!res.ok) throw new Error("Request failed");
      onCaptured(email);
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="space-y-3 rounded-xl border border-indigo-200 bg-indigo-50 p-5 text-center">
      <p className="font-semibold text-indigo-900">{insight.headline}</p>
      <p className="text-sm text-indigo-700">
        Wir haben ein Muster in deinen Einträgen erkannt. Trag deine E-Mail ein, um die volle
        Auswertung zu sehen und sie nicht zu verlieren.
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
          {status === "submitting" ? "Wird gesendet…" : "Muster freischalten"}
        </button>
      </form>
      {status === "error" && (
        <p className="text-sm text-red-600">Da ist etwas schiefgelaufen. Versuch es nochmal.</p>
      )}
    </div>
  );
}
