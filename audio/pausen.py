#!/usr/bin/env python3
"""Pausen kürzen: Jede Pause über MAX Sekunden wird auf MAX Sekunden gekürzt.

Kürzere Pausen bleiben unangetastet. Geschnitten wird in der Mitte der Pause, Satzanfang und
-ende bleiben stehen. An jeder Schnittstelle gibt es eine kurze Blende, damit nichts knackt.

Der Schwellwert für "Stille" wird automatisch aus dem Grundrauschen der Aufnahme bestimmt
(Grundrauschen + 12 dB), außer er wird mit --noise vorgegeben.

Audio rein -> Audio raus (Format nach Endung: .mp3 .m4a .wav .flac ...).
Video rein -> Video raus, Bild und Ton synchron (Schnitte liegen auf dem Bildraster).

  python3 audio/pausen.py IN OUT [--max 1.0] [--noise -40] [--dry-run]
"""
import argparse, json, os, subprocess, sys, tempfile
import numpy as np

WIN = 0.02      # Analysefenster 20 ms
FADE = 0.005    # Blende an jeder Schnittstelle 5 ms (ändert die Länge nicht)


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=index,codec_type,sample_rate,channels,r_frame_rate:format=duration",
                          "-of", "json", path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    aud = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    vid = next((s for s in d["streams"] if s["codec_type"] == "video"
                and s.get("r_frame_rate", "0/0") != "0/0"), None)
    if not aud:
        sys.exit("Keine Tonspur gefunden.")
    fps = None
    if vid:
        n, m = vid["r_frame_rate"].split("/")
        fps = float(n) / float(m)
        if fps > 120: vid, fps = None, None   # Cover-Bild in MP3/M4A, kein echtes Video
    return int(aud["sample_rate"]), int(aud["channels"]), fps


def decode(path, sr, ch):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-map", "0:a:0", "-f", "f32le",
                          "-ar", str(sr), "-ac", str(ch), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, ch)


def analyse(x, sr, noise):
    hop = int(sr * WIN)
    mono = x.mean(axis=1)
    n = len(mono) // hop
    rms = np.sqrt(np.mean(mono[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms)
    floor = float(np.percentile(db, 10))
    speech = float(np.percentile(db, 90))
    # Relativ zur Sprechlautstärke: Handys filtern das Rauschen oft auf fast digitale Stille,
    # dann wäre "Rauschen + x dB" zu streng und Atemgeräusche am Pausenrand blieben stehen.
    thr = noise if noise is not None else float(np.clip(max(floor + 6, speech - 15), -50, -25))
    silent = db < thr
    # Klicks und Rascheln unter 60 ms zählen zur Pause (jedes gesprochene Wort ist länger)
    for s, e in runs(~silent):
        if s > 0 and e < len(silent) and (e - s) * WIN < 0.06:
            silent[s:e] = True
    return silent, floor, speech, thr, hop


def runs(mask):
    """Zusammenhängende True-Bereiche als (start_index, end_index)."""
    d = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    return list(zip(np.where(d == 1)[0], np.where(d == -1)[0]))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src"); p.add_argument("out")
    p.add_argument("--max", type=float, default=1.0, help="Pausen länger als das werden auf genau das gekürzt")
    p.add_argument("--noise", type=float, help="Schwellwert in dB (Standard: automatisch)")
    p.add_argument("--dry-run", action="store_true", help="Nur messen und berichten, nichts schreiben")
    a = p.parse_args()

    sr, ch, fps = probe(a.src)
    x = decode(a.src, sr, ch)
    total = len(x) / sr
    silent, floor, speech, thr, hop = analyse(x, sr, a.noise)

    cuts, pauses = [], []
    for s, e in runs(silent):
        ts, te = s * hop / sr, e * hop / sr
        if te - ts <= a.max:
            continue
        pauses.append((ts, te))
        c0, c1 = ts + a.max / 2, te - a.max / 2          # Mitte raus, je MAX/2 bleibt stehen
        if fps:                                           # aufs Bildraster, damit es synchron bleibt
            c0, c1 = round(c0 * fps) / fps, round(c1 * fps) / fps
        if c1 > c0:
            cuts.append((c0, c1))

    keep, t = [], 0.0
    for c0, c1 in cuts:
        if c0 > t: keep.append((t, c0))
        t = c1
    if t < total: keep.append((t, total))
    new = sum(b - a_ for a_, b in keep)

    mmss = lambda s: f"{int(s // 60)}:{s % 60:04.1f}"
    print(f"Grundrauschen {floor:.1f} dB, Sprache {speech:.1f} dB, Schwelle {thr:.1f} dB")
    print(f"{len(cuts)} Pausen über {a.max:g} s gekürzt, gespart {total - new:.1f} s")
    print(f"Länge {mmss(total)} -> {mmss(new)}")
    for ts, te in sorted(pauses, key=lambda p_: p_[0] - p_[1])[:5]:
        print(f"  längste: {ts:8.2f} s  {te - ts:5.1f} s -> {a.max:g} s")
    if a.dry_run:
        return
    if not cuts:
        print("Nichts zu kürzen."); return

    fl = int(sr * FADE)
    ramp = np.linspace(0, 1, fl, dtype=np.float32)[:, None]
    parts = []
    for i, (s, e) in enumerate(keep):
        seg = x[int(round(s * sr)):int(round(e * sr))].copy()
        if len(seg) > 2 * fl:
            if i > 0: seg[:fl] *= ramp
            if i < len(keep) - 1: seg[-fl:] *= ramp[::-1]
        parts.append(seg)
    y = np.concatenate(parts)

    with tempfile.TemporaryDirectory() as tmp:
        wav = os.path.join(tmp, "a.wav")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", str(ch), "-i", "-",
                        "-c:a", "pcm_s24le", wav], input=y.tobytes(), check=True)
        if fps:
            expr = "+".join(f"between(t,{s:.4f},{e - 0.5 / fps:.4f})" for s, e in keep)
            script = os.path.join(tmp, "f.txt")
            open(script, "w").write(f"[0:v]select='{expr}',setpts=N/FRAME_RATE/TB[v]")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-i", wav,
                            "-filter_complex_script", script, "-map", "[v]", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                            "-r", f"{fps:g}", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                            a.out], check=True)
        else:
            ext = os.path.splitext(a.out)[1].lower()
            codec = {".mp3": ["-c:a", "libmp3lame", "-b:a", "192k"], ".wav": ["-c:a", "pcm_s16le"],
                     ".flac": ["-c:a", "flac"], ".ogg": ["-c:a", "libvorbis", "-q:a", "6"],
                     ".opus": ["-c:a", "libopus", "-b:a", "128k"]}.get(ext, ["-c:a", "aac", "-b:a", "192k"])
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, *codec, a.out], check=True)
    print(a.out)


if __name__ == "__main__":
    main()
