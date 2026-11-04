#!/usr/bin/env python3
"""Transkript einer Audio- oder Videodatei mit faster-whisper.

Schreibt BASE.txt (eine Zeile pro Satz, mit [hh:mm:ss]) und BASE.srt (Untertitel).
Dekodiert selbst mit ffmpeg, weil die PyAV-Version im Container nicht zu faster-whisper passt.

  python3 audio/transkript.py IN BASE [--model medium] [--lang de] [--prompt "Namen, Begriffe"]

--prompt: Schreibweisen, die Whisper kennen soll (Namen, Podcast-Titel, Fachwörter).
--fix:    REGEX=ERSATZ, wird nach dem Transkribieren auf jede Zeile angewendet (mehrfach möglich).

Standard: Host Gordon Schönwälder, Podcast "hauptberuflich depressiv". Whisper verhört den
Nachnamen trotz Prompt (Schönenwälder, Schönmelder), deshalb korrigiert FIX ihn immer.
"""
import argparse, re, subprocess
import numpy as np

PROMPT = "Gordon Schönwälder, hauptberuflich depressiv, ACT, Akzeptanz- und Commitment-Therapie."
FIX = [(r"\bGordon\s+Sch[öo]\w+", "Gordon Schönwälder"), (r"\bSch[öo]n\w*w[äa]lder\b", "Schönwälder")]


def ts(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("src"); p.add_argument("base")
    p.add_argument("--model", default="medium"); p.add_argument("--lang", default="de")
    p.add_argument("--prompt", default=PROMPT)
    p.add_argument("--fix", action="append", default=[], help="REGEX=ERSATZ")
    a = p.parse_args()

    fixes = FIX + [tuple(f.split("=", 1)) for f in a.fix]
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", a.src, "-map", "0:a:0", "-ac", "1",
                          "-ar", "16000", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    m = WhisperModel(a.model, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(audio, language=a.lang, vad_filter=True, beam_size=5,
                           initial_prompt=a.prompt or None)
    n = 0
    with open(a.base + ".srt", "w") as srt, open(a.base + ".txt", "w") as txt:
        for n, s in enumerate(segs, 1):
            t = s.text.strip()
            for pat, rep in fixes:
                t = re.sub(pat, rep, t)
            srt.write(f"{n}\n{ts(s.start)} --> {ts(s.end)}\n{t}\n\n")
            txt.write(f"[{ts(s.start)[:8]}] {t}\n")
            srt.flush(); txt.flush()
            print(n, ts(s.start)[:8], t[:60], flush=True)
    print(f"{n} Segmente -> {a.base}.txt, {a.base}.srt")


if __name__ == "__main__":
    main()
