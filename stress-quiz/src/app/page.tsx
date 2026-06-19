"use client";

import { useState } from "react";
import { QuizFlow } from "@/components/QuizFlow";
import { CrisisNotice } from "@/components/CrisisNotice";
import { ResultCard } from "@/components/ResultCard";
import { scoreAnswers, ScoringResult } from "@/lib/scoring";
import { TYPE_CONTENT } from "@/lib/resultContent";
import { QuizOption } from "@/lib/types";

type Stage = "intro" | "quiz" | "result";

export default function Home() {
  const [stage, setStage] = useState<Stage>("intro");
  const [result, setResult] = useState<ScoringResult | null>(null);

  function handleFinish(answers: QuizOption[]) {
    setResult(scoreAnswers(answers));
    setStage("result");
  }

  return (
    <div className="min-h-screen bg-zinc-50 px-4 py-12">
      <main className="mx-auto flex max-w-md flex-col gap-8">
        <header className="text-center">
          <h1 className="text-2xl font-semibold text-zinc-900">Welcher Belastungstyp bist du?</h1>
          <p className="mt-1 text-sm text-zinc-500">
            8 kurze Fragen, sofort drei Tipps passend zu dir.
          </p>
        </header>

        {stage === "intro" && (
          <section className="space-y-4 rounded-2xl border border-zinc-200 bg-white p-6 text-center shadow-sm">
            <p className="text-sm text-zinc-600">
              Dieses Quiz dient der Selbstreflexion. Es ist <strong>kein Diagnose-</strong>{" "}
              und <strong>kein Therapieersatz</strong> und kann ärztliche oder
              psychotherapeutische Beratung nicht ersetzen.
            </p>
            <button
              onClick={() => setStage("quiz")}
              className="rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white transition hover:bg-indigo-700"
            >
              Quiz starten
            </button>
          </section>
        )}

        {stage === "quiz" && (
          <section className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
            <QuizFlow onFinish={handleFinish} />
          </section>
        )}

        {stage === "result" && result && (
          <>
            {result.severityFlagged && <CrisisNotice />}
            <ResultCard content={TYPE_CONTENT[result.type]} />
          </>
        )}

        <footer className="text-center text-xs text-zinc-400">
          Dieses Tool dient der Selbstreflexion und ersetzt keine professionelle Diagnose oder
          Therapie. In akuten Krisen wende dich an die Telefonseelsorge: 0800 111 0 111.
        </footer>
      </main>
    </div>
  );
}
