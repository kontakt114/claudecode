export function CrisisNotice() {
  return (
    <div
      role="alert"
      className="space-y-3 rounded-xl border-2 border-red-300 bg-red-50 p-5 text-center"
    >
      <p className="font-semibold text-red-900">
        Es klingt, als ginge es dir aktuell sehr schwer.
      </p>
      <p className="text-sm text-red-800">
        Dieses Quiz kann dir hier nicht weiterhelfen – aber es gibt Menschen, die sofort für
        dich da sind. Bitte wende dich jetzt an eine dieser Stellen:
      </p>
      <div className="space-y-1 text-sm font-medium text-red-900">
        <p>Telefonseelsorge (kostenlos, 24/7): 0800 111 0 111 oder 0800 111 0 222</p>
        <p>Notruf: 112</p>
        <p>Oder begib dich direkt in die Notaufnahme des nächstgelegenen Krankenhauses</p>
      </div>
      <p className="text-xs text-red-700">
        Das gilt unabhängig davon, wie der Rest dieses Quiz ausgeht. Du musst nicht allein
        damit bleiben.
      </p>
    </div>
  );
}
