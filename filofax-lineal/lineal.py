"""Filofax-Pocket-Lineal als 3MF. Alle Maße in mm. Parameter oben anpassen, dann: python3 lineal.py"""
import zipfile, numpy as np
from manifold3d import Manifold, CrossSection, JoinType, OpType

# --- Parameter ---------------------------------------------------------
BREITE, HOEHE, DICKE = 76.0, 118.0, 1.0   # Seite Pocket = 81 x 120, etwas kleiner damit nichts übersteht
ECKRADIUS = 3.0
LOCH_D, LOCH_RAND = 6.5, 6.0              # Lochdurchmesser, Lochmitte ab linker Kante
LOCH_ABSTAND, LOCH_ANZAHL = 19.0, 6       # Pocket: 6 Ringe, je 19 mm
SCHLITZ = True                            # Schlitz zur Kante: einklipsen ohne Ringe zu öffnen
SCHLITZ_B = 2.2
TIEFE = 0.45                              # Gravurtiefe der Striche/Ziffern
STRICH_B = 0.5
L1, L5, L10 = 2.5, 4.0, 6.0               # Strichlängen mm / 5 mm / cm
RECHTS_CM, OBEN_CM = 10, 6                # Skalenlängen
# ------------------------------------------------------------------------

def box(x0, y0, x1, y1, z0, z1):
    return Manifold.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])

def platte():
    r = ECKRADIUS
    cs = CrossSection.square([BREITE - 2*r, HOEHE - 2*r]).translate([r, r]).offset(r, JoinType.Round, circular_segments=64)
    return Manifold.extrude(cs, DICKE)

SEG = {  # 7-Segment: a b c d e f g
    '0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc',
    '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
ZW, ZH, ZS = 1.8, 3.0, 0.45  # Ziffer breit, hoch, Strich

def ziffer(ch, x, y):
    w, h, s = ZW, ZH, ZS
    r = {'a': (0, h - s, w, h), 'g': (0, h/2 - s/2, w, h/2 + s/2), 'd': (0, 0, w, s),
         'f': (0, h/2, s, h), 'e': (0, 0, s, h/2), 'b': (w - s, h/2, w, h), 'c': (w - s, 0, w, h/2)}
    return [box(x + a, y + b, x + c, y + d, DICKE - TIEFE, DICKE + 1) for a, b, c, d in (r[k] for k in SEG[ch])]

def zahl(text, cx, cy):
    gap = 0.6
    total = len(text) * ZW + (len(text) - 1) * gap
    x = cx - total / 2
    out = []
    for ch in text:
        out += ziffer(ch, x, cy - ZH / 2)
        x += ZW + gap
    return out

def laenge(i):
    return L10 if i % 10 == 0 else L5 if i % 5 == 0 else L1

teile = []
# rechte Skala, von unten nach oben
y0 = 4.0
for i in range(RECHTS_CM * 10 + 1):
    y, L = y0 + i, laenge(i)
    teile.append(box(BREITE - L, y - STRICH_B/2, BREITE + 1, y + STRICH_B/2, DICKE - TIEFE, DICKE + 1))
    if i % 10 == 0:
        teile += zahl(str(i // 10), BREITE - L10 - 1.2 - ZW * len(str(i // 10)) / 2 - 0.3, y)
# obere Skala, von links nach rechts (startet hinter den Löchern)
x0 = 14.0
for i in range(OBEN_CM * 10 + 1):
    x, L = x0 + i, laenge(i)
    teile.append(box(x - STRICH_B/2, HOEHE - L, x + STRICH_B/2, HOEHE + 1, DICKE - TIEFE, DICKE + 1))
    if i % 10 == 0:
        teile += zahl(str(i // 10), x, HOEHE - L10 - 1.2 - ZH / 2)
# Löcher
mitte = HOEHE / 2
for k in range(LOCH_ANZAHL):
    y = mitte + (k - (LOCH_ANZAHL - 1) / 2) * LOCH_ABSTAND
    teile.append(Manifold.cylinder(DICKE * 3, LOCH_D / 2, LOCH_D / 2, 64).translate([LOCH_RAND, y, -DICKE]))
    if SCHLITZ:
        teile.append(box(-1, y - SCHLITZ_B/2, LOCH_RAND, y + SCHLITZ_B/2, -1, DICKE + 1))

modell = platte() - Manifold.batch_boolean(teile, OpType.Add)

mesh = modell.to_mesh()
V, F = np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts)

verts = "".join(f'<vertex x="{x:.4f}" y="{y:.4f}" z="{z:.4f}"/>' for x, y, z in V)
tris = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in F)
model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="de-DE" '
         'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">'
         '<metadata name="Title">Filofax Pocket Lineal</metadata><resources>'
         f'<object id="1" type="model" name="Filofax Pocket Lineal"><mesh><vertices>{verts}</vertices>'
         f'<triangles>{tris}</triangles></mesh></object></resources><build><item objectid="1"/></build></model>')
ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
with zipfile.ZipFile("filofax_pocket_lineal.3mf", "w", zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml", ct)
    z.writestr("_rels/.rels", rels)
    z.writestr("3D/3dmodel.model", model)
print("ok:", len(V), "Vertices,", len(F), "Dreiecke, Volumen", round(modell.volume(), 1), "mm³, Genus", modell.genus())
