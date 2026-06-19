import { StressType, TypeContent } from "./types";

export const TYPE_CONTENT: Record<StressType, TypeContent> = {
  uebererreger: {
    title: "Der Übererreger",
    summary:
      "Dein Nervensystem steht oft auf Hochtouren. Kleine Störungen wirken wie große Reize, dein Körper ist auf Anspannung geschaltet.",
    tips: [
      "Probiere die 4-7-8-Atemtechnik (4 Sek. einatmen, 7 halten, 8 ausatmen) bei akuter Anspannung",
      "Baue feste, kurze Pausen ohne Bildschirm in deinen Tag ein – schon 5 Minuten helfen",
      "Bewegung mit Rhythmus (Gehen, Schwimmen) hilft, überschüssige Anspannung abzubauen",
    ],
  },
  vermeider: {
    title: "Der Vermeider",
    summary:
      "Du gehst Belastendem lieber aus dem Weg, statt dich damit auseinanderzusetzen. Kurzfristig entlastet das, langfristig wächst der Druck im Hintergrund.",
    tips: [
      "Teile große, vermiedene Aufgaben in einen einzigen, sehr kleinen ersten Schritt auf",
      "Setz dir ein festes Zeitfenster von nur 10 Minuten, um etwas Aufgeschobenes anzugehen",
      "Sprich mit jemandem über das, was du vermeidest – das nimmt oft den Druck",
    ],
  },
  gruebler: {
    title: "Der Grübler",
    summary:
      "Du denkst Dinge immer wieder durch, oft ohne zu einer Lösung zu kommen. Dein Kopf ist viel beschäftigt, dein Handeln bleibt manchmal stehen.",
    tips: [
      "Schreib grüblerische Gedanken auf Papier – das gibt dem Kopf eine Pause vom Kreisen",
      "Setz dir eine feste 'Grübelzeit' von 15 Minuten am Tag, statt es überall zuzulassen",
      "Frag dich bei einem Gedanken: 'Kann ich daran jetzt etwas ändern?' – wenn nein, leg ihn bewusst zur Seite",
    ],
  },
  erschoepft: {
    title: "Der Erschöpfte",
    summary:
      "Deine Reserven sind aktuell knapp. Dinge, die früher leichtfielen, kosten jetzt viel Kraft – das ist ein Signal, kürzerzutreten.",
    tips: [
      "Plane bewusst Erholung ein, nicht erst wenn nichts mehr geht, sondern vorbeugend",
      "Reduziere für eine Woche bewusst eine Verpflichtung, auf die du am ehesten verzichten kannst",
      "Sprich mit jemandem, dem du vertraust, darüber, wie es dir wirklich geht",
    ],
  },
  resilient: {
    title: "Der Ausgeglichene",
    summary:
      "Du kommst aktuell gut mit Belastungen zurecht und hast Strategien, die für dich funktionieren. Das ist eine gute Basis, die sich lohnt zu pflegen.",
    tips: [
      "Halte fest, was dir aktuell gut hilft – das ist wertvoll für schwierigere Phasen",
      "Pflege bewusst die Routinen, die dir Stabilität geben (Schlaf, Bewegung, Kontakte)",
      "Biete anderen, denen es schwerer fällt, ein offenes Ohr – das stärkt auch dich",
    ],
  },
};
