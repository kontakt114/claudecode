import { NextResponse } from "next/server";
import { supabase } from "@/lib/supabase";

export async function POST(request: Request) {
  const { email, resultType } = await request.json();

  if (typeof email !== "string" || !email.includes("@")) {
    return NextResponse.json({ error: "Invalid email" }, { status: 400 });
  }

  if (supabase) {
    const { error } = await supabase
      .from("leads")
      .insert({ email, result_type: resultType ?? null });

    if (error) {
      return NextResponse.json({ error: error.message }, { status: 500 });
    }
  } else {
    console.log("[lead-capture] Supabase not configured, lead not persisted:", email);
  }

  return NextResponse.json({ ok: true });
}
