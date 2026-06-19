"use client";

import { useState } from "react";
import { QUESTIONS } from "@/lib/questions";
import { QuizOption } from "@/lib/types";

export function QuizFlow({ onFinish }: { onFinish: (answers: QuizOption[]) => void }) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<QuizOption[]>([]);

  const question = QUESTIONS[step];

  function selectOption(option: QuizOption) {
    const next = [...answers, option];
    if (step + 1 < QUESTIONS.length) {
      setAnswers(next);
      setStep(step + 1);
    } else {
      onFinish(next);
    }
  }

  return (
    <div className="space-y-6">
      <div className="h-1.5 w-full rounded-full bg-zinc-100">
        <div
          className="h-1.5 rounded-full bg-seafoam-500 transition-all"
          style={{ width: `${((step + 1) / QUESTIONS.length) * 100}%` }}
        />
      </div>
      <p className="text-xs text-zinc-400">
        Frage {step + 1} von {QUESTIONS.length}
      </p>
      <p className="text-lg font-medium text-zinc-900">{question.prompt}</p>
      <div className="flex flex-col gap-2">
        {question.options.map((option) => (
          <button
            key={option.label}
            onClick={() => selectOption(option)}
            className="rounded-lg border border-zinc-200 px-4 py-3 text-left text-sm transition hover:border-seafoam-400 hover:bg-seafoam-50"
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}
