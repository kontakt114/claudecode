import { QuizOption, StressType } from "./types";

export interface ScoringResult {
  type: StressType;
  severityFlagged: boolean;
}

export function scoreAnswers(answers: QuizOption[]): ScoringResult {
  const counts: Record<StressType, number> = {
    uebererreger: 0,
    vermeider: 0,
    gruebler: 0,
    erschoepft: 0,
    resilient: 0,
  };

  let severityFlagged = false;

  for (const answer of answers) {
    counts[answer.type] += 1;
    if (answer.severityFlag) severityFlagged = true;
  }

  const type = (Object.keys(counts) as StressType[]).reduce((best, current) =>
    counts[current] > counts[best] ? current : best
  );

  return { type, severityFlagged };
}
