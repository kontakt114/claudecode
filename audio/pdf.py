#!/usr/bin/env python3
"""Transkript als PDF: Kopf mit Folgen-Infos, Kapitelübersicht, Text in Absätzen unter Kapitelüberschriften.

  python3 audio/pdf.py TRANSKRIPT.txt OUT.pdf --title "Folgentitel" [--kapitel kapitel.txt]
         [--show "hauptberuflich depressiv"] [--host "Gordon Schönwälder"] [--datum 04.11.2026] [--dauer 27:23]

TRANSKRIPT.txt: Zeilen "[hh:mm:ss] Text" (von audio/transkript.py).
kapitel.txt:    Zeilen "mm:ss Titel" (wie für extras.py chapters).
Schrift: Helvetica (ohne Einbettung), damit die Datei klein bleibt.
"""
import argparse, re
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

INK, MUTED, ACCENT, RULE = HexColor("#1b1d23"), HexColor("#6b6f7a"), HexColor("#b8860b"), HexColor("#d9dbe0")
BODY = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=15.5, textColor=INK, alignment=TA_LEFT)
TIME = ParagraphStyle("time", fontName="Helvetica", fontSize=8, leading=15.5, textColor=MUTED)
H2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13, leading=17, textColor=INK, spaceBefore=14, spaceAfter=6)
SHOW = ParagraphStyle("show", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=ACCENT)
TITLE = ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=22, leading=27, textColor=INK, spaceBefore=4)
META = ParagraphStyle("meta", fontName="Helvetica", fontSize=9.5, leading=13, textColor=MUTED, spaceBefore=4)
TOC = ParagraphStyle("toc", fontName="Helvetica", fontSize=10, leading=14.5, textColor=INK)


def secs(t):
    p = [int(x) for x in t.split(":")]
    return sum(v * 60 ** i for i, v in enumerate(reversed(p)))


def mmss(s):
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60:02d}:{s % 60:02d}"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def read_lines(path):
    out = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"\[(\d\d:\d\d:\d\d)\]\s*(.*)", line.strip())
        if m: out.append((secs(m.group(1)), m.group(2)))
    return out


def read_chapters(path):
    if not path: return [(0, "")]
    ch = []
    for line in open(path, encoding="utf-8"):
        if line.strip():
            t, title = line.strip().split(" ", 1)
            ch.append((secs(t), title.strip()))
    return ch


def paragraphs(lines, max_chars=420):
    """Zeilen zu Absätzen: neuer Absatz nach Satzende, sobald genug Text zusammen ist."""
    paras, cur = [], []
    for t, txt in lines:
        cur.append((t, txt))
        n = sum(len(x) for _, x in cur)
        if n >= max_chars and re.search(r"[.?!]$", txt):
            paras.append(cur); cur = []
    if cur: paras.append(cur)
    return [(p[0][0], " ".join(x for _, x in p)) for p in paras]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--title", required=True); ap.add_argument("--kapitel")
    ap.add_argument("--show", default="hauptberuflich depressiv"); ap.add_argument("--host", default="Gordon Schönwälder")
    ap.add_argument("--datum", default=""); ap.add_argument("--dauer", default="")
    a = ap.parse_args()

    lines, ch = read_lines(a.src), read_chapters(a.kapitel)
    meta = " · ".join(x for x in [a.host, a.datum and f"Folge vom {a.datum}", a.dauer and f"{a.dauer} min"] if x)
    story = [Paragraph(esc(a.show.upper()), SHOW), Paragraph(esc(a.title), TITLE), Paragraph(esc(meta), META),
             Spacer(1, 8 * mm)]

    if a.kapitel:
        rows = [[Paragraph(mmss(t), TIME), Paragraph(esc(title), TOC)] for t, title in ch]
        toc = Table(rows, colWidths=[16 * mm, None], hAlign="LEFT")
        toc.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 1), ("TOPPADDING", (0, 0), (-1, -1), 1)]))
        story += [Paragraph("Kapitel", H2), toc, Spacer(1, 4 * mm)]

    bounds = [t for t, _ in ch] + [10 ** 9]
    for i, (t0, title) in enumerate(ch):
        part = [(t, x) for t, x in lines if t0 <= t < bounds[i + 1]]
        if not part: continue
        head = Paragraph(f'{esc(title)} <font size="9" color="#6b6f7a">&nbsp;&nbsp;{mmss(t0)}</font>', H2) if title else None
        for j, (pt, txt) in enumerate(paragraphs(part)):
            row = Table([[Paragraph(mmss(pt), TIME), Paragraph(esc(txt), BODY)]], colWidths=[16 * mm, None])
            row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                     ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
            story.append(KeepTogether([head, row]) if j == 0 and head else row)

    def footer(c, d):
        c.saveState()
        c.setStrokeColor(RULE); c.line(20 * mm, 14 * mm, A4[0] - 20 * mm, 14 * mm)
        c.setFont("Helvetica", 7.5); c.setFillColor(MUTED)
        c.drawString(20 * mm, 9.5 * mm, f"{a.show} · {a.title} · Maschinelles Transkript, Zeitmarken zur gekürzten Fassung")
        c.drawRightString(A4[0] - 20 * mm, 9.5 * mm, str(d.page))
        c.restoreState()

    doc = SimpleDocTemplate(a.out, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm,
                            bottomMargin=22 * mm, title=f"{a.show}: {a.title}", author=a.host,
                            subject="Transkript")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(a.out)


if __name__ == "__main__":
    main()
