import { MoodEntry } from "./types";

const WEEKDAYS = [
  "Sonntag",
  "Montag",
  "Dienstag",
  "Mittwoch",
  "Donnerstag",
  "Freitag",
  "Samstag",
];

export interface WeekdayAverage {
  weekday: string;
  average: number;
  count: number;
}

export function averageByWeekday(entries: MoodEntry[]): WeekdayAverage[] {
  const sums = new Array(7).fill(0);
  const counts = new Array(7).fill(0);

  for (const entry of entries) {
    const day = new Date(entry.createdAt).getDay();
    sums[day] += entry.mood;
    counts[day] += 1;
  }

  return WEEKDAYS.map((weekday, day) => ({
    weekday,
    average: counts[day] > 0 ? sums[day] / counts[day] : 0,
    count: counts[day],
  }));
}

export interface Insight {
  headline: string;
  detail: string;
}

const MIN_ENTRIES_FOR_PATTERN = 5;

export function findInsight(entries: MoodEntry[]): Insight | null {
  if (entries.length < MIN_ENTRIES_FOR_PATTERN) return null;

  const weekdayAverages = averageByWeekday(entries).filter((d) => d.count > 0);
  if (weekdayAverages.length < 2) return null;

  const worst = weekdayAverages.reduce((a, b) => (a.average <= b.average ? a : b));
  const best = weekdayAverages.reduce((a, b) => (a.average >= b.average ? a : b));

  if (worst.weekday === best.weekday) return null;

  const tagCounts = new Map<string, number>();
  for (const entry of entries) {
    tagCounts.set(entry.tag, (tagCounts.get(entry.tag) ?? 0) + 1);
  }
  const topTag = [...tagCounts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0];

  return {
    headline: `Du fühlst dich am ${worst.weekday} am gestresstesten`,
    detail: `An ${best.weekday}en geht es dir im Schnitt deutlich besser als an ${worst.weekday}en.${
      topTag ? ` Am häufigsten genannter Grund: "${topTag}".` : ""
    }`,
  };
}

export function shouldOfferLeadCapture(entries: MoodEntry[]): boolean {
  return entries.length >= MIN_ENTRIES_FOR_PATTERN;
}
