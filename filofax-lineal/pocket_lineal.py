"""Lineal-Streifen für Filofax Pocket (Form wie Ref. 213609) als 3MF für Bambu Studio.
Erzeugt zwei Dateien:
  pocket_lineal_einfarbig.3mf  – Skala graviert, für Druck ohne AMS
  pocket_lineal_zweifarbig.3mf – Skala als bündige Einlage (2 Teile), für AMS
Alle Maße in mm. Parameter anpassen, dann: python3 pocket_lineal.py
"""
import zipfile, numpy as np
from manifold3d import Manifold, CrossSection, JoinType, OpType, FillRule
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

# --- Parameter ---------------------------------------------------------
L, H, DICKE = 131.5, 32.0, 1.0      # Länge, Höhe, Dicke
TIEFE = 0.4                          # Tiefe der Skala (Gravur bzw. Einlage)
LOCH_D, LOCH_Y = 5.5, 5.8            # Lochdurchmesser, Lochmitte ab Unterkante
LOCH_ABSTAND, LOCH_ANZAHL = 19.0, 6  # Pocket: 6 Ringe à 19 mm
SCHLITZ_B = 1.8                      # Schlitz von Loch zur Unterkante
NULLPUNKT, SKALA_MM = 5.9, 120       # Position 0 ab linker Kante, Skalenlänge
STRICH_B = 0.45
L1, L5, L10 = 3.0, 4.7, 7.0          # Strichlängen mm / 5 mm / cm
SCHRIFT_H, ZAHL_Y = 2.6, H - 10.2    # Ziffernhöhe, Ziffern-Unterkante
# ------------------------------------------------------------------------

def umriss():
    pts = [(0, 7.8), (0, H), (L - 1.6, H), (L, H - 2.0), (L, 10.0), (L - 9.5, 0), (8.5, 0)]
    cs = CrossSection([pts[::-1]])
    return cs.offset(-0.6, JoinType.Round, circular_segments=32).offset(0.6, JoinType.Round, circular_segments=32)

def rechteck(x0, y0, x1, y1):
    return CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])

FONT = FontProperties(family="DejaVu Sans", weight="bold")
def text(s, cx, y):
    p = TextPath((0, 0), s, size=1, prop=FONT)
    polys = [np.asarray(q) for q in p.to_polygons() if len(q) > 2]
    cs = CrossSection(polys, FillRule.EvenOdd)
    b = cs.bounds()  # (xmin, ymin, xmax, ymax)
    k = SCHRIFT_H / (b[3] - b[1])
    cs = cs.scale([k, k])
    b = cs.bounds()
    return cs.translate([cx - (b[0] + b[2]) / 2, y - b[1]])

def skala():
    teile = []
    for i in range(SKALA_MM + 1):
        x = NULLPUNKT + i
        ln = L10 if i % 10 == 0 else L5 if i % 5 == 0 else L1
        teile.append(rechteck(x - STRICH_B / 2, H - ln, x + STRICH_B / 2, H + 1))
        if i % 10 == 0 and 0 < i // 10 <= 11:
            teile.append(text(str(i // 10), x, ZAHL_Y))
    teile.append(text("CM", NULLPUNKT + 0.6, ZAHL_Y))
    return CrossSection.batch_boolean(teile, OpType.Add) ^ umriss()

def loecher():
    teile = []
    for k in range(LOCH_ANZAHL):
        x = L / 2 + (k - (LOCH_ANZAHL - 1) / 2) * LOCH_ABSTAND
        teile.append(CrossSection.circle(LOCH_D / 2, 64).translate([x, LOCH_Y]))
        teile.append(rechteck(x - SCHLITZ_B / 2, -1, x + SCHLITZ_B / 2, LOCH_Y))
    return CrossSection.batch_boolean(teile, OpType.Add)

form = umriss() - loecher()
koerper = Manifold.extrude(form, DICKE)
skala_3d = Manifold.extrude(skala(), TIEFE + 1).translate([0, 0, DICKE - TIEFE])
graviert = koerper - skala_3d
einlage = Manifold.extrude(skala() - loecher(), TIEFE).translate([0, 0, DICKE - TIEFE])
basis = koerper - Manifold.extrude(skala(), TIEFE + 1).translate([0, 0, DICKE - TIEFE])

def mesh_xml(m, oid, name):
    me = m.to_mesh()
    V, F = np.asarray(me.vert_properties)[:, :3], np.asarray(me.tri_verts)
    v = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in V)
    t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in F)
    return f'<object id="{oid}" type="model" name="{name}"><mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>'

def schreibe(datei, teile):
    objs = "".join(mesh_xml(m, i + 2, n) for i, (m, n) in enumerate(teile))
    comps = "".join(f'<component objectid="{i + 2}"/>' for i in range(len(teile)))
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="de-DE" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"><resources>' + objs +
             f'<object id="1" type="model" name="Pocket Lineal"><components>{comps}</components></object>'
             '</resources><build><item objectid="1" transform="1 0 0 0 1 0 0 0 1 60 100 0"/></build></model>')
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(datei, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct); z.writestr("_rels/.rels", rels); z.writestr("3D/3dmodel.model", model)

schreibe("pocket_lineal_einfarbig.3mf", [(graviert, "Lineal")])
schreibe("pocket_lineal_zweifarbig.3mf", [(basis, "Lineal"), (einlage, "Skala")])
for n, m in [("graviert", graviert), ("basis", basis), ("einlage", einlage)]:
    print(n, round(m.volume(), 1), "mm³", m.status())
