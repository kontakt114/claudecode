#!/usr/bin/env python3
"""Reel-Pipeline: Talking-Head-Video -> 9:16-Reel mit Jump Cuts, Captions, Effekten.

Befehle (Details: python3 reel/reel.py <befehl> -h):
  fetch       Drive-Datei laden (Datei muss "Jeder mit dem Link" sein)
  frames      Kontaktabzug mit Zeitstempeln, um ins Video zu schauen
  cut         Pausen rausschneiden, Punch-ins, Lautheit auf -14 LUFS
  assemble    Inhaltlicher Schnitt: Stücke aus einer oder mehreren Quellen aneinanderhängen
  transcribe  Transkript mit Wortzeiten (faster-whisper)
  captions    Wort-für-Wort-Captions (+ Hook) als .ass
  badge       Dauer-Badge oben, z. B. "MOVEMBER · TAG 2 VON 30"
  fx          Effekte: fliegender Text, Label, Schnurrbart
  sfx         Sounds erzeugen (whoosh, pop, thud)
  render      Alles einbrennen: Zooms, .ass-Ebenen, Sounds
"""
import argparse, json, os, re, subprocess, sys, tempfile

FONT = "Inter Black"
YELLOW = "&H00D4FF&"          # ASS-Farben sind BGR
CAP_Y = 1450                  # Caption-Höhe (Mitte), unter dem Kinn, über der IG-UI
ZOOM_FILTER = "scale=iw*{z}:-2,crop=1080:1920:(iw-1080)/2:(ih-1920)*0.28"
STACHE = ("m 170 32 b 140 0 92 2 62 30 b 44 48 22 56 0 40 b 8 82 52 102 92 88 b 122 78 150 62 170 56 "
          "b 190 62 218 78 248 88 b 288 102 332 82 340 40 b 318 56 296 48 278 30 b 248 2 200 0 170 32")
ENC_V = ["-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-r", "30"]
ENC_A = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
LOUD = "highpass=f=80,loudnorm=I=-14:TP=-1.5:LRA=11"


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def rng(s):
    a, b = s.split(":")
    return float(a), float(b)


def ts(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def ass_header(styles):
    return ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
            "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, "
            "Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n" + "\n".join(styles) +
            "\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")


# ---------------------------------------------------------------- fetch
def cmd_fetch(a):
    url = f"https://drive.usercontent.google.com/download?id={a.file_id}&export=download&confirm=t"
    subprocess.run(["curl", "-sSL", "--fail", "-o", a.out, url], check=True)
    print(a.out, os.path.getsize(a.out), "Bytes")


# ---------------------------------------------------------------- frames
def cmd_frames(a):
    # Beschriftung vor dem Ausdünnen, damit der Zeitstempel zum gezeigten Frame passt
    vf = (f"scale={a.width}:-1,"
          f"drawtext=text='%{{eif\\:t+{a.start}\\:d}}.%{{eif\\:mod((t+{a.start})*10\\,10)\\:d}}':"
          f"x=2:y=2:fontsize=16:fontcolor=yellow:box=1:boxcolor=black,"
          f"fps=1/{a.every},tile={a.cols}x{a.rows}")
    args = ["-ss", str(a.start)] + (["-t", str(a.length)] if a.length else []) + ["-i", a.src]
    ff(*args, "-vf", vf, "-frames:v", "1", a.out)
    print(a.out)


# ---------------------------------------------------------------- cut
def silences(src, noise, mind):
    r = subprocess.run(["ffmpeg", "-i", src, "-map", "0:a:0", "-af", f"silencedetect=noise={noise}:d={mind}",
                        "-f", "null", "-"], capture_output=True, text=True)
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(st, en + [duration(src)] * (len(st) - len(en))))


def cmd_cut(a):
    total = duration(a.src)
    protect = [rng(p) for p in a.protect]
    sil = []
    for s, e in silences(a.src, a.noise, a.min):
        # Stille in geschützten Bereichen bleibt (z. B. stumme Gags)
        for ps, pe in protect:
            if s < pe and e > ps:
                if s < ps: sil.append((s, ps))
                if e > pe: sil.append((pe, e))
                break
        else:
            sil.append((s, e))
    sil += [rng(d) for d in a.drop]
    sil.sort()
    keep, t = [], 0.0
    for s, e in sil:
        x = s + a.pad if s > 0 else s
        y = e - a.pad if e < total - 0.01 else e
        if x < y and x > t: keep.append((t, x))
        t = max(t, y)
    if t < total: keep.append((t, total))
    keep = [(round(x, 3), round(y, 3)) for x, y in keep if y - x > 0.05]
    nopunch = [rng(p) for p in a.nopunch] + protect
    print(f"{len(keep)} Segmente, {sum(y - x for x, y in keep):.1f} s von {total:.1f} s")
    with tempfile.TemporaryDirectory() as tmp:
        lst = open(os.path.join(tmp, "list.txt"), "w")
        for i, (x, y) in enumerate(keep):
            d = y - x
            zoom = a.punch if (i % 2 == 1 and a.punch > 1 and
                               not any(x < pe and y > ps for ps, pe in nopunch)) else 1.0
            vf = ZOOM_FILTER.format(z=zoom) if zoom > 1 else "null"
            p = os.path.join(tmp, f"s{i:03d}.mp4")
            ff("-ss", str(x), "-i", a.src, "-t", f"{d:.3f}", "-map", "0:v:0", "-map", "0:a:0", "-vf", vf,
               "-af", f"afade=t=in:d=0.02,afade=t=out:st={max(d - 0.02, 0):.3f}:d=0.02",
               *ENC_V, "-threads", "2", *ENC_A, p)
            lst.write(f"file '{p}'\n")
            print(f"  {i:02d}  {x:7.2f}-{y:7.2f}  zoom {zoom}", flush=True)
        lst.close()
        ff("-f", "concat", "-safe", "0", "-i", lst.name, "-c:v", "copy", "-af", LOUD, *ENC_A,
           "-movflags", "+faststart", a.out)
    print(a.out, f"{duration(a.out):.1f} s")


# ---------------------------------------------------------------- assemble
def cmd_assemble(a):
    srcs, parts = [], []
    for p in a.piece:
        src, x, y = p.rsplit(":", 2)
        if src not in srcs: srcs.append(src)
        parts.append((srcs.index(src), float(x), float(y)))
    f, labels = [], ""
    for i, (s, x, y) in enumerate(parts):
        f.append(f"[{s}:v:0]trim={x}:{y},setpts=PTS-STARTPTS[v{i}];"
                 f"[{s}:a:0]atrim={x}:{y},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,"
                 f"afade=t=out:st={y - x - 0.03:.3f}:d=0.03[a{i}]")
        labels += f"[v{i}][a{i}]"
    f.append(f"{labels}concat=n={len(parts)}:v=1:a=1[v][ac];[ac]{LOUD}[a]")
    ins = sum((["-i", s] for s in srcs), [])
    ff(*ins, "-filter_complex", ";".join(f), "-map", "[v]", "-map", "[a]", *ENC_V, "-threads", "4", *ENC_A,
       "-movflags", "+faststart", a.out)
    t = 0.0
    for i, (s, x, y) in enumerate(parts):
        print(f"  Stück {i}: {srcs[s]} {x}-{y}  ->  im Ergebnis ab {t:.2f} s")
        t += y - x
    print(a.out, f"{duration(a.out):.1f} s")


# ---------------------------------------------------------------- transcribe
def cmd_transcribe(a):
    import numpy as np
    from faster_whisper import WhisperModel
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.src, "-map", "0:a:0", "-f", "s16le", "-ac", "1",
                          "-ar", "16000", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    m = WhisperModel(a.model, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(audio, language=a.lang, word_timestamps=True, beam_size=5,
                           initial_prompt=a.prompt or None)
    out = []
    for s in segs:
        print(f"[{s.start:6.2f}-{s.end:6.2f}] {s.text.strip()}", flush=True)
        out.append({"start": s.start, "end": s.end, "text": s.text.strip(),
                    "words": [{"w": w.word, "s": w.start, "e": w.end} for w in s.words]})
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)


# ---------------------------------------------------------------- captions
STEMS = ["untersuchung", "vorsorge", "gesundheit", "checks", "krebs", "lippen", "bart", "männer", "monat",
          "therapie", "generation", "zeichen", "weise", "entwicklung", "kampagne"]


def split_long(w):
    """Lange Komposita für 1080 px Breite zerlegen: an Bindestrichen oder an bekannten Wortstämmen.
    Ohne passende Grenze bleibt das Wort ganz (die Schrift wird dann kleiner)."""
    t = w["w"]
    core = re.sub(r"[.,?!]$", "", t)
    if len(core) <= 16:
        return [w]
    pieces = core.split("-") if "-" in core.strip("-") else None
    if not pieces:
        low = core.lower()
        cuts = [i for i in range(4, len(core) - 3) if any(low.startswith(s, i) for s in STEMS)]
        if not cuts:
            return [w]
        k = min(cuts, key=lambda i: abs(i - len(core) / 2))
        pieces = [core[:k], core[k:]]
    pieces = [p for p in pieces if p]
    dur, n = w["e"] - w["s"], len(pieces)
    res = []
    for i, p in enumerate(pieces):
        txt = p + ("-" if i < n - 1 else t[len(core):])
        res.append({"w": txt, "s": w["s"] + dur * i / n, "e": w["s"] + dur * (i + 1) / n})
    return res


def cmd_captions(a):
    d = json.load(open(a.transcript))
    fix = dict(f.split("=", 1) for f in a.fix)
    words = []
    for s in d:
        for w in s["words"]:
            t = w["w"].strip()
            if t.startswith("-") and words:          # "Prostata" "-Krebs" -> "Prostata-" "Krebs"
                words[-1]["w"] = words[-1]["w"].rstrip("-") + "-"
                t = t[1:]
            core = re.sub(r"[^\wäöüÄÖÜß-]", "", t)
            if core in fix:
                t = t.replace(core, fix[core])
            words += split_long({"w": t, "s": w["s"], "e": w["e"]})
    chunks, cur = [], []
    for w in words:
        cand = cur + [w]
        txt = " ".join(x["w"] for x in cand)
        if cur and (len(cand) > 3 or len(txt) > 16 or w["s"] - cur[-1]["e"] > 0.6):
            chunks.append(cur)
            cur = [w]
        else:
            cur = cand
        if re.search(r"[.,?!]$", w["w"]):
            chunks.append(cur)
            cur = []
    if cur: chunks.append(cur)
    skip = [rng(s) for s in a.skip]
    moves = [(float(m.split(":")[0]), float(m.split(":")[1]), int(m.split(":")[2])) for m in a.move]
    up = lambda s: s.upper().replace("ß", "SS")
    ev = []
    for ci, c in enumerate(chunks):
        end = c[-1]["e"] + 0.25
        if ci + 1 < len(chunks): end = min(end, chunks[ci + 1][0]["s"])
        L = len(" ".join(x["w"] for x in c))
        fs = f"\\fs{min(96, int(96 * 13 / L))}" if L > 13 else ""
        for wi, w in enumerate(c):
            st = w["s"]
            en = c[wi + 1]["s"] if wi + 1 < len(c) else end
            if en <= st or any(x <= st < y for x, y in skip): continue
            y = next((my for x, y2, my in moves if x <= st < y2), a.y)
            txt = " ".join(("{\\c%s}" % (YELLOW if k == wi else "&HFFFFFF&")) + up(re.sub(r"[.,]$", "", x["w"]))
                           for k, x in enumerate(c))
            pop = r"{\fscx112\fscy112\t(0,90,\fscx100\fscy100)}" if wi == 0 else ""
            ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Cap,,0,0,0,,{{\\pos(540,{y}){fs}}}{pop}{txt}")
    if a.hook:
        ev.append(f"Dialogue: 1,{ts(0)},{ts(a.hook_len)},Hook,,0,0,0,,{{\\fad(0,250)}}{a.hook}")
    styles = [f"Style: Cap,{FONT},96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1",
              f"Style: Hook,{FONT},78,&H00FFFFFF,&H00FFFFFF,&H00000000,&HB4000000,0,0,0,0,100,100,0,0,3,22,0,8,60,60,330,1"]
    open(a.out, "w").write(ass_header(styles) + "\n".join(ev) + "\n")
    for c in chunks:
        print(f"{c[0]['s']:6.2f}  " + " ".join(x["w"] for x in c))


# ---------------------------------------------------------------- badge
def cmd_badge(a):
    styles = [f"Style: Badge,{FONT},50,&H00000000,&H00000000,&H0000D4FF,&H00000000,0,0,0,0,100,100,2,0,3,16,0,8,60,60,190,1"]
    open(a.out, "w").write(ass_header(styles) + f"Dialogue: 2,0:00:00.00,9:00:00.00,Badge,,0,0,0,,{a.text}\n")


# ---------------------------------------------------------------- fx
def cmd_fx(a):
    ev = []
    for b in a.big:                      # START:ENDE:TEXT  - fliegt von rechts rein, knallt, federt
        s, e, txt = b.split(":", 2)
        ev.append(f"Dialogue: 3,{ts(float(s))},{ts(float(e))},Big,,0,0,0,,{{\\move(1500,{a.big_y},540,{a.big_y},0,160)"
                  r"\frz-14\fscx170\fscy170\t(0,160,\fscx100\fscy100\frz-6)\t(160,240,\fscx118\fscy118)"
                  rf"\t(240,330,\fscx100\fscy100)\fad(0,120)}}{txt}")
    for l in a.label:                    # START:ENDE:X:Y:TEXT  - ploppt schräg auf
        s, e, x, y, txt = l.split(":", 4)
        ev.append(f"Dialogue: 3,{ts(float(s))},{ts(float(e))},Label,,0,0,0,,{{\\pos({x},{y})\\frz7\\fscx0\\fscy0"
                  rf"\t(0,140,\fscx118\fscy118)\t(140,240,\fscx100\fscy100)\fad(0,180)}}{txt}")
    if a.stache:                         # START  dann Keyframes T:X:Y ...  ENDE
        start, end = a.stache_start, a.stache_end
        kf = [tuple(float(v) for v in k.split(":")) for k in a.stache]
        t0, x0, y0 = kf[0]
        ev.append(f"Dialogue: 3,{ts(start)},{ts(t0)},Stache,,0,0,0,,{{\\move(-250,250,{x0:.0f},{y0:.0f})"
                  rf"\frz-200\t(\frz0)\fscx60\fscy60\t(\fscx115\fscy115)\p1}}{STACHE}")
        for i, (t, x, y) in enumerate(kf):
            nt, nx, ny = kf[i + 1] if i + 1 < len(kf) else (end, x, y)
            bounce = r"\fscx115\fscy115\t(0,90,\fscx92\fscy92)\t(90,180,\fscx100\fscy100)" if i == 0 else ""
            ev.append(f"Dialogue: 3,{ts(t)},{ts(nt)},Stache,,0,0,0,,{{\\move({x:.0f},{y:.0f},{nx:.0f},{ny:.0f})"
                      f"{bounce}\\p1}}{STACHE}")
    styles = [f"Style: Big,{FONT},330,&H0000D4FF,&H0000D4FF,&H00000000,&H78000000,0,0,0,0,100,100,0,0,1,12,8,5,0,0,0,1",
              "Style: Stache,Arial,20,&H00182434,&H00182434,&H00080C10,&H64000000,0,0,0,0,100,100,0,0,1,3,4,5,0,0,0,1",
              f"Style: Label,{FONT},58,&H00000000,&H00000000,&H00FFFFFF,&H00000000,0,0,0,0,100,100,1,0,3,18,0,5,0,0,0,1"]
    open(a.out, "w").write(ass_header(styles) + "\n".join(ev) + "\n")
    print(a.out, len(ev), "Effekt-Zeilen")


# ---------------------------------------------------------------- sfx
def cmd_sfx(a):
    os.makedirs(a.dir, exist_ok=True)
    ff("-f", "lavfi", "-i", "anoisesrc=d=0.5:c=pink:a=0.9:r=48000", "-af",
       "bandpass=f=1800:w=1500,afade=t=in:d=0.32:curve=exp,afade=t=out:st=0.32:d=0.18,volume=2.2",
       "-ac", "2", os.path.join(a.dir, "whoosh.wav"))
    ff("-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*(1100-850*t/0.11)*t)*exp(-28*t)':d=0.14:s=48000",
       "-ac", "2", os.path.join(a.dir, "pop.wav"))
    ff("-f", "lavfi", "-i", "aevalsrc='0.9*sin(2*PI*(140-80*t/0.2)*t)*exp(-14*t)':d=0.25:s=48000",
       "-ac", "2", os.path.join(a.dir, "thud.wav"))
    print("whoosh.wav pop.wav thud.wav ->", a.dir)


# ---------------------------------------------------------------- render
def cmd_render(a):
    fc, v = [], "[0:v]"
    if a.zoom:
        en = "+".join(f"between(t,{x},{y})" for x, y in (rng(z) for z in a.zoom))
        fc.append(f"{v}split=2[b][z];[z]{ZOOM_FILTER.format(z=a.zoom_factor)}[zz];[b][zz]overlay=0:0:enable='{en}'[o]")
        v = "[o]"
    chain = ",".join(f"ass={p}" for p in a.ass) or "null"
    fc.append(f"{v}{chain}[v]")
    ins, mix = ["-i", a.src], ["[0:a]"]
    for i, s in enumerate(a.sound):        # NAME@SEKUNDE[@LAUTSTÄRKE]
        parts = s.split("@")
        name, t = parts[0], float(parts[1])
        vol = parts[2] if len(parts) > 2 else ("0.9" if "thud" in name else "0.55")
        ins += ["-i", os.path.join(a.sfx_dir, name + ".wav")]
        ms = int(t * 1000)
        fc.append(f"[{i + 1}:a]adelay={ms}|{ms},volume={vol}[s{i}]")
        mix.append(f"[s{i}]")
    if a.sound:
        fc.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=first,alimiter=limit=0.89[a]")
        amap, acodec = "[a]", ENC_A
    else:
        amap, acodec = "0:a", ["-c:a", "copy"]
    ff(*ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", amap, *ENC_V, "-threads", "4", *acodec,
       "-movflags", "+faststart", a.out)
    print(a.out, f"{duration(a.out):.1f} s")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("fetch"); s.add_argument("file_id"); s.add_argument("out"); s.set_defaults(f=cmd_fetch)

    s = sp.add_parser("frames"); s.add_argument("src"); s.add_argument("out")
    s.add_argument("--start", type=float, default=0); s.add_argument("--length", type=float)
    s.add_argument("--every", type=float, default=2); s.add_argument("--cols", type=int, default=12)
    s.add_argument("--rows", type=int, default=4); s.add_argument("--width", type=int, default=120)
    s.set_defaults(f=cmd_frames)

    s = sp.add_parser("cut"); s.add_argument("src"); s.add_argument("out")
    s.add_argument("--noise", default="-35dB"); s.add_argument("--min", type=float, default=0.5)
    s.add_argument("--pad", type=float, default=0.15); s.add_argument("--punch", type=float, default=1.18)
    s.add_argument("--protect", action="append", default=[], help="A:B Stille hier behalten, kein Punch-in")
    s.add_argument("--drop", action="append", default=[], help="A:B zusätzlich rausschneiden")
    s.add_argument("--nopunch", action="append", default=[], help="A:B hier kein Punch-in")
    s.set_defaults(f=cmd_cut)

    s = sp.add_parser("assemble"); s.add_argument("out")
    s.add_argument("--piece", action="append", required=True, help="DATEI:A:B (Reihenfolge = Schnitt)")
    s.set_defaults(f=cmd_assemble)

    s = sp.add_parser("transcribe"); s.add_argument("src"); s.add_argument("out")
    s.add_argument("--model", default="medium"); s.add_argument("--lang", default="de")
    s.add_argument("--prompt", default="Movember, Copper, Oberlippenbart.", help="Begriffe, die Whisper kennen soll")
    s.set_defaults(f=cmd_transcribe)

    s = sp.add_parser("captions"); s.add_argument("transcript"); s.add_argument("out")
    s.add_argument("--fix", action="append", default=[], help="falsch=richtig")
    s.add_argument("--hook", default=None, help=r"Hook-Text oben, \N = Zeilenumbruch")
    s.add_argument("--hook-len", type=float, default=3.2)
    s.add_argument("--y", type=int, default=CAP_Y)
    s.add_argument("--move", action="append", default=[], help="A:B:Y Captions in diesem Fenster auf Höhe Y")
    s.add_argument("--skip", action="append", default=[], help="A:B hier keine Captions (z. B. fliegender Text)")
    s.set_defaults(f=cmd_captions)

    s = sp.add_parser("badge"); s.add_argument("text"); s.add_argument("out"); s.set_defaults(f=cmd_badge)

    s = sp.add_parser("fx"); s.add_argument("out")
    s.add_argument("--big", action="append", default=[], help="START:ENDE:TEXT")
    s.add_argument("--big-y", type=int, default=CAP_Y)
    s.add_argument("--label", action="append", default=[], help="START:ENDE:X:Y:TEXT")
    s.add_argument("--stache", action="append", default=[], help="Keyframe T:X:Y (Oberlippe), erster = Landung")
    s.add_argument("--stache-start", type=float, help="Anflug beginnt"); s.add_argument("--stache-end", type=float)
    s.set_defaults(f=cmd_fx)

    s = sp.add_parser("sfx"); s.add_argument("dir"); s.set_defaults(f=cmd_sfx)

    s = sp.add_parser("render"); s.add_argument("src"); s.add_argument("out")
    s.add_argument("--ass", action="append", default=[])
    s.add_argument("--zoom", action="append", default=[], help="A:B harter Zoom (Pointe)")
    s.add_argument("--zoom-factor", type=float, default=1.32)
    s.add_argument("--sound", action="append", default=[], help="whoosh@9.0  pop@31.8@0.6")
    s.add_argument("--sfx-dir", default="sfx")
    s.set_defaults(f=cmd_render)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
