export type Tag = "Stress" | "Schlaf" | "Sozial" | "Arbeit" | "Energie";

export const TAGS: Tag[] = ["Stress", "Schlaf", "Sozial", "Arbeit", "Energie"];

export interface MoodEntry {
  id: string;
  mood: 1 | 2 | 3 | 4 | 5;
  tag: Tag;
  createdAt: string; // ISO timestamp
}

export const MOOD_EMOJI: Record<MoodEntry["mood"], string> = {
  1: "😞",
  2: "😕",
  3: "😐",
  4: "🙂",
  5: "😄",
};

export const MOOD_LABEL: Record<MoodEntry["mood"], string> = {
  1: "Sehr schlecht",
  2: "Schlecht",
  3: "Okay",
  4: "Gut",
  5: "Sehr gut",
};
