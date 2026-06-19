import { QuizQuestion } from "./types";

export const QUESTIONS: QuizQuestion[] = [
  {
    id: "sleep",
    prompt: "Wie schläfst du in letzter Zeit?",
    options: [
      { label: "Gut, ich fühle mich erholt", type: "resilient" },
      { label: "Ich liege oft wach und denke nach", type: "gruebler" },
      { label: "Ich bin angespannt und schrecke leicht auf", type: "uebererreger" },
      { label: "Ich schlafe viel, fühle mich trotzdem müde", type: "erschoepft" },
      { label: "Ich vermeide es, ins Bett zu gehen", type: "vermeider" },
    ],
  },
  {
    id: "social",
    prompt: "Wie ist es gerade mit Verabredungen und Kontakt zu anderen?",
    options: [
      { label: "Ich treffe Leute gern, das tut mir gut", type: "resilient" },
      { label: "Ich sage oft ab, es ist mir zu viel", type: "vermeider" },
      { label: "Ich grüble danach noch lange über Gesprächen", type: "gruebler" },
      { label: "Ich bin schnell gereizt in Gesellschaft", type: "uebererreger" },
      { label: "Mir fehlt einfach die Energie dafür", type: "erschoepft" },
    ],
  },
  {
    id: "tension",
    prompt: "Wie fühlt sich dein Körper im Alltag an?",
    options: [
      { label: "Meistens entspannt", type: "resilient" },
      { label: "Angespannt, wie auf dem Sprung", type: "uebererreger" },
      { label: "Schwer und kraftlos", type: "erschoepft" },
      { label: "Ich merke kaum noch, wie es mir geht", type: "vermeider" },
      { label: "Verkrampft, wenn ich an Probleme denke", type: "gruebler" },
    ],
  },
  {
    id: "thoughts",
    prompt: "Was passiert, wenn ein Problem auftaucht?",
    options: [
      { label: "Ich gehe es an und finde meist eine Lösung", type: "resilient" },
      { label: "Ich denke immer wieder in Schleifen darüber nach", type: "gruebler" },
      { label: "Ich schiebe es so lange wie möglich auf", type: "vermeider" },
      { label: "Ich werde sofort nervös und unruhig", type: "uebererreger" },
      { label: "Es fühlt sich einfach zu anstrengend an", type: "erschoepft" },
    ],
  },
  {
    id: "energy",
    prompt: "Wie ist dein Energielevel über den Tag verteilt?",
    options: [
      { label: "Stabil, ich komme gut durch den Tag", type: "resilient" },
      { label: "Ich bin schon morgens erschöpft", type: "erschoepft" },
      { label: "Ich bin unruhig, aber nicht erschöpft", type: "uebererreger" },
      { label: "Ich vermeide Aufgaben, die Energie kosten", type: "vermeider" },
      { label: "Es schwankt stark, je nachdem was mir im Kopf herumgeht", type: "gruebler" },
    ],
  },
  {
    id: "irritability",
    prompt: "Wie reagierst du auf kleine Störungen (Lärm, Nachfragen, Verspätungen)?",
    options: [
      { label: "Meist gelassen", type: "resilient" },
      { label: "Schnell gereizt oder überfordert", type: "uebererreger" },
      { label: "Ich ziehe mich zurück, statt zu reagieren", type: "vermeider" },
      { label: "Ich grüble danach noch, warum mich das so getroffen hat", type: "gruebler" },
      { label: "Es ist mir eigentlich egal, ich habe keine Kraft mich aufzuregen", type: "erschoepft" },
    ],
  },
  {
    id: "avoidance",
    prompt: "Wie gehst du mit Aufgaben um, vor denen du dich drückst?",
    options: [
      { label: "Ich packe sie meist zeitnah an", type: "resilient" },
      { label: "Ich schiebe sie auf, so lange es geht", type: "vermeider" },
      { label: "Ich denke ständig daran, ohne anzufangen", type: "gruebler" },
      { label: "Ich werde davon richtig unruhig", type: "uebererreger" },
      { label: "Allein der Gedanke daran erschöpft mich", type: "erschoepft" },
    ],
  },
  {
    id: "outlook",
    prompt: "Wie blickst du aktuell auf die nächsten Tage?",
    options: [
      { label: "Hoffnungsvoll, ich freue mich auf einiges", type: "resilient" },
      { label: "Es geht so, mal besser, mal schlechter", type: "gruebler" },
      { label: "Eher bedrückt, vieles fühlt sich schwer an", type: "erschoepft" },
      { label: "Ich vermeide es, daran überhaupt zu denken", type: "vermeider" },
      {
        label: "Ich sehe aktuell keinen Ausweg, es fühlt sich aussichtslos an",
        type: "erschoepft",
        severityFlag: true,
      },
    ],
  },
];
