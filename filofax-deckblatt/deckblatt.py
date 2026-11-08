"""Deckblatt für Filofax Personal (95 x 171 mm) mit weißem Schriftzug als bündige Einlage.
Zwei Teile in einer 3MF: "Blatt" (Grundfarbe) und "Schrift" (weiß). Für Profil 0.20mm Standard.
Schrift: Pacifico (SIL Open Font License). Alle Maße in mm. Aufruf: python3 deckblatt.py
"""
import zipfile, numpy as np
from manifold3d import Manifold, CrossSection, JoinType, OpType, FillRule
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

# --- Parameter ---------------------------------------------------------
B, H, DICKE = 95.0, 171.0, 1.2        # Personal-Seite, 6 Schichten à 0,2
EINLAGE = 0.6                         # Schrift 3 Schichten tief, damit Weiß deckt
ECKRADIUS = 3.0
LOCH_D, LOCH_X, SCHLITZ_B = 6.0, 6.5, 2.0
LOCH_ABSTAENDE = [19, 19, 51, 19, 19] # Personal: 2 Gruppen à 3 Ringe
ZEILEN = ["Mentale", "Gesundheit"]
TEXT_BREITE = 68.0                    # Breite der längsten Zeile
TEXT_MITTE_X = 52.0                   # rechts der Löcher zentriert
TEXT_MITTE_Y = H * 0.58
ZEILEN_ABSTAND = 1.25                 # × Zeilenhöhe
HERZ = True
FONT = FontProperties(fname="Pacifico-Regular.ttf")
# ------------------------------------------------------------------------

def blatt():
    r = ECKRADIUS
    return CrossSection.square([B - 2*r, H - 2*r]).translate([r, r]).offset(r, JoinType.Round, circular_segments=48)

def loecher():
    ys = np.concatenate([[0], np.cumsum(LOCH_ABSTAENDE)])
    ys = ys - ys[-1] / 2 + H / 2
    teile = []
    for y in ys:
        teile.append(CrossSection.circle(LOCH_D / 2, 64).translate([LOCH_X, y]))
        teile.append(CrossSection.square([LOCH_X + 1, SCHLITZ_B]).translate([-1, y - SCHLITZ_B / 2]))
    return CrossSection.batch_boolean(teile, OpType.Add)

def zeile(s):
    p = TextPath((0, 0), s, size=10, prop=FONT)
    return CrossSection([np.asarray(q) for q in p.to_polygons() if len(q) > 2], FillRule.NonZero)

def schrift():
    zs = [zeile(s) for s in ZEILEN]
    breit = max(z.bounds()[2] - z.bounds()[0] for z in zs)
    k = TEXT_BREITE / breit
    zh = 10 * k * ZEILEN_ABSTAND
    teile = []
    for i, z in enumerate(zs):
        z = z.scale([k, k]); b = z.bounds()
        y = TEXT_MITTE_Y + ((len(zs) - 1) / 2 - i) * zh
        teile.append(z.translate([TEXT_MITTE_X - (b[0] + b[2]) / 2, y]))
    if HERZ:
        t = np.linspace(0, 2 * np.pi, 120)
        x = 16 * np.sin(t) ** 3
        y = 13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)
        herz = CrossSection([(np.c_[x, y] * 0.35)[::-1]])
        aussen, innen = herz, herz.offset(-1.0, JoinType.Round)
        unten = TEXT_MITTE_Y - (len(zs) - 1) / 2 * zh - 10 * k * 0.9
        teile.append((aussen - innen).translate([TEXT_MITTE_X, unten - 8]))
    return CrossSection.batch_boolean(teile, OpType.Add)

form = blatt() - loecher()
s = schrift() ^ form
grund = Manifold.extrude(form, DICKE) - Manifold.extrude(s, EINLAGE + 1).translate([0, 0, DICKE - EINLAGE])
text3d = Manifold.extrude(s, EINLAGE).translate([0, 0, DICKE - EINLAGE])

def mesh_xml(m, oid, name):
    me = m.to_mesh()
    V, F = np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts)
    v = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in V)
    t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in F)
    return f'<object id="{oid}" type="model" name="{name}"><mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>'

def schreibe(datei, teile, name):
    objs = "".join(mesh_xml(m, i + 2, n) for i, (m, n) in enumerate(teile))
    comps = "".join(f'<component objectid="{i + 2}"/>' for i in range(len(teile)))
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="de-DE" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>' + objs +
             f'<object id="1" type="model" name="{name}"><components>{comps}</components></object>'
             '</resources><build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 80 40 0"/></build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(datei, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("3D/3dmodel.model", model)

schreibe("deckblatt_mentale_gesundheit.3mf", [(grund, "Blatt"), (text3d, "Schrift")], "Deckblatt Mentale Gesundheit")
print("Blatt", round(grund.volume(), 1), grund.status(), "| Schrift", round(text3d.volume(), 1), text3d.status())
