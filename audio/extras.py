#!/usr/bin/env python3
"""Extras für eine fertige Podcast-Folge: Kapitelmarken, Zitat-Clips, Audiogramme.

  chapters   Kapitel als ID3-Kapitel in die MP3 schreiben (Audio wird nur kopiert)
             python3 audio/extras.py chapters IN.mp3 OUT.mp3 kapitel.txt
             kapitel.txt: eine Zeile pro Kapitel, "mm:ss Titel" oder "hh:mm:ss Titel"

  clip       Ausschnitt schneiden, Grenzen rasten auf die nächste Sprechpause ein
             python3 audio/extras.py clip IN OUT.mp3 --from 10:13 --to 10:50 [--noise -30] [--exact]

  audiogram  9:16-Video aus einem Clip: Titel oben, Hook, Wellenform, Captions (.ass von reel.py captions)
             python3 audio/extras.py audiogram CLIP.mp3 CAPS.ass OUT.mp4 --show "PODCAST" --hook "Zeile 1\\NZeile 2"
"""
import argparse, os, subprocess, sys, tempfile
import numpy as np

SR = 16000
WIN = 0.02


def ff(*args):
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", *args], check=True)


def secs(t):
    p = [float(x) for x in t.split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p)))


def hms(t):
    return f"{int(t // 3600):02d}:{int(t % 3600 // 60):02d}:{int(t % 60):02d}"


def duration(path):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 path], capture_output=True, text=True, check=True).stdout)


# ---------------------------------------------------------------- chapters
def read_chapters(path):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line: continue
        t, title = line.split(" ", 1)
        out.append((secs(t), title.strip()))
    if not out or out[0][0] != 0:
        sys.exit("Erstes Kapitel muss bei 00:00 beginnen.")
    if any(b[0] <= a[0] for a, b in zip(out, out[1:])):
        sys.exit("Kapitel müssen aufsteigend sortiert sein.")
    return out


def cmd_chapters(a):
    ch = read_chapters(a.chapters)
    dur = duration(a.src)
    esc = lambda s: s.replace("\\", "\\\\").replace("=", "\\=").replace(";", "\\;").replace("#", "\\#")
    meta = [";FFMETADATA1"]
    for i, (t, title) in enumerate(ch):
        end = ch[i + 1][0] if i + 1 < len(ch) else dur
        meta += ["[CHAPTER]", "TIMEBASE=1/1000", f"START={int(t * 1000)}", f"END={int(end * 1000)}",
                 f"title={esc(title)}"]
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
        f.write("\n".join(meta) + "\n")
    ff("-i", a.src, "-i", f.name, "-map", "0:a", "-map_metadata", "0", "-map_chapters", "1",
       "-c", "copy", "-id3v2_version", "3", a.out)
    os.unlink(f.name)
    n = subprocess.run(["ffprobe", "-v", "error", "-show_chapters", "-of", "csv=p=0", a.out],
                       capture_output=True, text=True).stdout.strip().count("\n") + 1
    print(f"{n} Kapitel in {a.out}")
    for t, title in ch:
        print(f"{hms(t)} {title}")


# ---------------------------------------------------------------- clip
def envelope(path, start, length):
    raw = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(max(0, start)), "-t", str(length),
                          "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    n = int(SR * WIN)
    x = x[: len(x) // n * n].reshape(-1, n)
    return 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)


def snap(path, t, noise, prefer, reach=2.0, min_gap=0.12):
    """Mitte der nächsten Pause (>= min_gap) um t. prefer=-1: lieber davor, +1: lieber danach."""
    t0 = max(0.0, t - reach)
    db = envelope(path, t0, 2 * reach)
    quiet = db < noise
    runs, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]: j += 1
            if (j - i) * WIN >= min_gap:
                runs.append(t0 + (i + j) / 2 * WIN)
            i = j
        else:
            i += 1
    if not runs:
        return t, False
    # Pausen auf der bevorzugten Seite zählen halb so weit
    return min(runs, key=lambda c: abs(c - t) * (0.5 if (c - t) * prefer >= 0 else 1.0)), True


def cmd_clip(a):
    if a.exact:
        (A, ok1), (B, ok2) = (secs(a.start), True), (secs(a.end), True)
    else:
        A, ok1 = snap(a.src, secs(a.start), a.noise, -1)
        B, ok2 = snap(a.src, secs(a.end), a.noise, +1)
    L = B - A
    fade_out = min(0.4, L / 4)
    ff("-ss", f"{A:.3f}", "-t", f"{L:.3f}", "-i", a.src,
       "-af", f"afade=t=in:d=0.02,afade=t=out:st={L - fade_out:.3f}:d={fade_out:.3f}",
       "-c:a", "libmp3lame", "-b:a", "192k", a.out)
    warn = "" if ok1 and ok2 else "  (keine Pause gefunden, Grenze unverändert)"
    print(f"{a.out}: {A:.2f} -> {B:.2f} s, {L:.1f} s{warn}")


# ---------------------------------------------------------------- audiogram
def ass_text(s):
    return s.replace("\\N", "\x00").replace("\\", "").replace("\x00", "\\N").replace("{", "(").replace("}", ")")


def cmd_audiogram(a):
    L = duration(a.clip)
    font = "Inter Black"
    head = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 0\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
            "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
            "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            f"Style: Show,{font},44,&H00D4FF&,&H00D4FF&,&H000000&,&H000000&,0,0,0,0,100,100,6,0,1,0,0,8,80,80,0,1\n"
            f"Style: Hook,{font},74,&HFFFFFF&,&HFFFFFF&,&H000000&,&H000000&,0,0,0,0,100,100,0,0,1,0,0,8,90,90,0,1\n\n"
            "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    end = f"{int(L // 3600)}:{int(L % 3600 // 60):02d}:{L % 60:05.2f}"
    ev = [f"Dialogue: 0,0:00:00.00,{end},Show,,0,0,0,,{{\\pos(540,250)}}{ass_text(a.show.upper())}",
          f"Dialogue: 0,0:00:00.00,{end},Hook,,0,0,0,,{{\\pos(540,360)}}{ass_text(a.hook)}"]
    tmp = tempfile.mkdtemp()
    top = os.path.join(tmp, "top.ass")
    open(top, "w", encoding="utf-8").write(head + "\n".join(ev) + "\n")
    caps = os.path.join(tmp, "caps.ass")
    subprocess.run(["cp", a.captions, caps], check=True)
    fc = (f"color=c=0x14161c:s=1080x1920:r=30:d={L:.3f}[bg];"
          f"[0:a]showwaves=s=900x380:mode=cline:draw=full:rate=30:colors=0xFFD400:scale=sqrt,"
          f"colorkey=black:0.1:0,format=yuva420p[w];"
          f"[bg][w]overlay=90:820[v1];"
          f"[v1]ass={top},ass={caps}[v]")
    ff("-i", a.clip, "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
       "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a.out)
    print(f"{a.out} {L:.1f} s")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("chapters"); s.add_argument("src"); s.add_argument("out"); s.add_argument("chapters")
    s.set_defaults(f=cmd_chapters)
    s = sp.add_parser("clip"); s.add_argument("src"); s.add_argument("out")
    s.add_argument("--from", dest="start", required=True); s.add_argument("--to", dest="end", required=True)
    s.add_argument("--noise", type=float, default=-30)
    s.add_argument("--exact", action="store_true", help="Grenzen nicht einrasten (Sekunden genau so schneiden)")
    s.set_defaults(f=cmd_clip)
    s = sp.add_parser("audiogram"); s.add_argument("clip"); s.add_argument("captions"); s.add_argument("out")
    s.add_argument("--show", default=""); s.add_argument("--hook", default="")
    s.set_defaults(f=cmd_audiogram)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
