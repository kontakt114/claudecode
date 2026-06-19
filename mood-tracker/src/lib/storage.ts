import { MoodEntry } from "./types";

const ENTRIES_KEY = "mood-tracker:entries";
const LEAD_CAPTURED_KEY = "mood-tracker:lead-captured";

export function getEntries(): MoodEntry[] {
  if (typeof window === "undefined") return [];
  const raw = window.localStorage.getItem(ENTRIES_KEY);
  if (!raw) return [];
  try {
    return JSON.parse(raw) as MoodEntry[];
  } catch {
    return [];
  }
}

export function addEntry(entry: MoodEntry): MoodEntry[] {
  const entries = [...getEntries(), entry];
  window.localStorage.setItem(ENTRIES_KEY, JSON.stringify(entries));
  return entries;
}

export function isLeadCaptured(): boolean {
  if (typeof window === "undefined") return false;
  return window.localStorage.getItem(LEAD_CAPTURED_KEY) === "true";
}

export function setLeadCaptured(): void {
  window.localStorage.setItem(LEAD_CAPTURED_KEY, "true");
}
