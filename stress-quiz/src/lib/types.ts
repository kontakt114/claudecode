export type StressType =
  | "uebererreger"
  | "vermeider"
  | "gruebler"
  | "erschoepft"
  | "resilient";

export interface QuizOption {
  label: string;
  type: StressType;
  /** Marks an answer as a signal for acute distress (hopelessness/safety) — overrides normal scoring flow */
  severityFlag?: boolean;
}

export interface QuizQuestion {
  id: string;
  prompt: string;
  options: QuizOption[];
}

export interface TypeContent {
  title: string;
  summary: string;
  tips: string[];
}
