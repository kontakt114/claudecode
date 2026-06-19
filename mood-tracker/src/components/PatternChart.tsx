"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, XAxis, YAxis } from "recharts";
import { WeekdayAverage } from "@/lib/patterns";

export function PatternChart({ data, blurred }: { data: WeekdayAverage[]; blurred: boolean }) {
  const chartData = data.map((d) => ({ ...d, weekday: d.weekday.slice(0, 2) }));

  return (
    <div className={blurred ? "pointer-events-none select-none blur-sm" : ""}>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey="weekday" tickLine={false} axisLine={false} />
          <YAxis domain={[0, 5]} hide />
          <Bar dataKey="average" radius={[6, 6, 0, 0]} fill="#6366f1" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
