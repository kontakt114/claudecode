"use client";

import { useRef, useState } from "react";
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
  const quizSectionRef = useRef<HTMLDivElement>(null);

  function startQuiz() {
    setStage("quiz");
    requestAnimationFrame(() => {
      quizSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  function handleFinish(answers: QuizOption[]) {
    setResult(scoreAnswers(answers));
    setStage("result");
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      {/* Hero */}
      <section className="px-4 pt-20 pb-16 text-center">
        <div className="mx-auto max-w-2xl">
          <span className="inline-block rounded-full bg-seafoam-100 px-4 py-1 text-xs font-medium tracking-wide text-seafoam-700">
            2 Minuten · keine Anmeldung nötig
          </span>
          <h1 className="mt-6 text-4xl font-semibold leading-tight text-zinc-900 sm:text-5xl">
            Welcher Belastungstyp bist du?
          </h1>
          <p className="mx-auto mt-5 max-w-md text-lg leading-relaxed text-zinc-500">
            Acht kurze Fragen. Sofort drei Tipps, die zu dir passen – ganz ohne Fachjargon.
          </p>
          <button
            onClick={startQuiz}
            className="mt-8 rounded-full bg-seafoam-500 px-8 py-3.5 text-sm font-medium text-white shadow-sm shadow-seafoam-200 transition hover:bg-seafoam-600"
          >
            Quiz starten
          </button>
          <p className="mt-4 text-xs text-zinc-400">
            Dient der Selbstreflexion – kein Diagnose- oder Therapieersatz.
          </p>
        </div>
      </section>

      {/* Calm divider wave */}
      <div className="h-px w-full max-w-xs mx-auto bg-seafoam-200" />

      {/* Why this helps */}
      <section className="mx-auto max-w-3xl px-4 py-16">
        <div className="grid gap-8 sm:grid-cols-3">
          <div className="text-center">
            <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-seafoam-100 text-seafoam-600">
              1
            </div>
            <p className="text-sm text-zinc-500">Acht Fragen zu Schlaf, Anspannung, Energie und mehr</p>
          </div>
          <div className="text-center">
            <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-seafoam-100 text-seafoam-600">
              2
            </div>
            <p className="text-sm text-zinc-500">Dein Belastungstyp und drei sofort nutzbare Tipps</p>
          </div>
          <div className="text-center">
            <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-seafoam-100 text-seafoam-600">
              3
            </div>
            <p className="text-sm text-zinc-500">Optional: eine 5-Tage-Serie mit weiteren Tipps per Mail</p>
          </div>
        </div>
      </section>

      {/* Quiz / Result section */}
      <section ref={quizSectionRef} className="px-4 pb-24">
        <div className="mx-auto max-w-md">
          {stage === "quiz" && (
            <div className="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
              <QuizFlow onFinish={handleFinish} />
            </div>
          )}

          {stage === "result" && result && (
            <div className="space-y-5">
              {result.severityFlagged && <CrisisNotice />}
              <ResultCard content={TYPE_CONTENT[result.type]} />
            </div>
          )}
        </div>
      </section>

      <footer className="px-4 pb-12 text-center text-xs text-zinc-400">
        Dieses Tool dient der Selbstreflexion und ersetzt keine professionelle Diagnose oder
        Therapie. In akuten Krisen wende dich an die Telefonseelsorge: 0800 111 0 111.
      </footer>
    </div>
  );
}
