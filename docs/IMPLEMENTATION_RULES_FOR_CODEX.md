Du arbeitest an einer ROS2-Humble Projektarbeit für den Unitree Go2 EDU:
Autonomes Apportieren mit Nav2, RTAB-Map (RGB-D), MoveIt2 + D1-550-85.

WICHTIGSTE REGEL (Single Source of Truth):
Die Datei "Projektarbeit_dokument_002" (PDF/LaTeX/TXT) ist die einzige verbindliche fachliche Referenz.
Nutze ausschließlich deren Inhalt als Grundlage.
Keine Fakten aus älteren Versionen, Tutorials, Blogposts oder Beispiel-Repos als verbindliche Projektentscheidung übernehmen.

Ziel deines Arbeitsmodus (best effort):
- Implementiere möglichst viel produktiv nutzbaren Code auf Basis des Dokuments 002.
- Wenn etwas fehlt oder unklar ist, mache einen konkreten Vorschlag (best effort),
  aber kennzeichne ihn IMMER klar als "neu vorgeschlagen / nicht aus Dokument 002".
- Erfinde keine stillen Annahmen.
- Bei sicherheits- oder steuerungsrelevanten Punkten: lieber stoppen + markieren als raten.

======================================================================
ARBEITSMODUS (BEST EFFORT, ABER STRIKT)
======================================================================

1) Dokument zuerst lesen
- Lies "Projektarbeit_dokument_002" vollständig ein, bevor du Änderungen machst.

2) Vor jeder Implementierung: Spezifikations-Check
Erstelle eine kurze Einschätzung:
- Was ist im Dokument 002 eindeutig spezifiziert?
- Was ist unklar/fehlend?
- Was kannst du trotzdem als neutralen Stub/Interface vorbereiten?

3) Best-Effort erlaubt, aber nur mit Kennzeichnung
Wenn eine Spezifikation fehlt, darfst du:
- eine implementierbare Default-Lösung vorschlagen,
- Stubs/Interfaces/TODOs anlegen,
- Platzhalterwerte verwenden,
ABER nur wenn du klar trennst zwischen:
- "Aus Dokument 002 abgeleitet"
- "Neu vorgeschlagen (Best-Effort)"

4) Keine stillschweigenden Architekturentscheidungen
Wenn zwei echte Varianten offen sind (z. B. BT vs SMACC2, Topic-Namen, Perception-Modell):
- keine verdeckte Wahl treffen,
- Varianten kurz benennen,
- wenn möglich neutrales Interface/Stub implementieren.

5) Sicherheits-/Steuerungsregeln nicht verletzen
Insbesondere:
- Keine direkte cmd_vel-Publikation aus Tracking/Perception/Follow/Manipulation,
  wenn das Dokument dies nicht explizit erlaubt.
- Wenn Bewegung nötig wäre, aber der Contract fehlt: dokumentiere den Konflikt und stoppe an der Stelle.
- Keine "Quick Hacks" für Steuerung in produktionsnahen Pfaden.

6) Implementierungsstil
- ROS2 Humble Zielarchitektur
- syntaktisch korrekte YAML/Launchfiles
- saubere ROS2 Nodes / Topics / Actions / TF-Contracts
- klare TODOs mit Grund ("welche Dokumentlücke blockiert das?")
- kleine, überprüfbare Schritte statt großer Umbauten

======================================================================
AUSGABEFORMAT (BEI JEDER ARBEITSRUNDE)
======================================================================

Gib bei jeder Runde IMMER diese 4 Blöcke aus:

A) Was ich sicher aus Dokument 002 ableiten konnte
B) Was ich implementiert/geändert habe
C) Was unklar ist / welche Spezifikationslücken bestehen
D) Welche minimalen Entscheidungen der Mensch treffen muss

Wenn du Best-Effort-Vorschläge machst, zusätzlich:
E) Neu vorgeschlagene Defaults/Annahmen (klar markiert, nicht verbindlich)

======================================================================
ARBEITSROUTINE PRO TASK (VERBINDLICH)
======================================================================

1) Nenne die betroffenen Dateien, die du erstellen/ändern willst.
2) Begründe jede Datei mit Bezug auf Dokument 002.
3) Implementiere in kleinen Schritten.
4) Nach jedem Schritt: liste offene Fragen / Annahmen.
5) Erzeuge keine großen Refactorings ohne explizite Zustimmung.
6) Wenn ein Teil blockiert ist, implementiere Interfaces/Stubs statt ungetesteter Logik.

======================================================================
UMGANG MIT FEHLENDEN DETAILS (SEHR WICHTIG)
======================================================================

Wenn Werte fehlen (z. B. Topic-Namen, Frame-Namen, Parameterwerte, Device-Namen, konkrete API-Namen):
- Keine Fakten erfinden.
- Platzhalter verwenden.
- In OPEN_QUESTIONS.md dokumentieren.
- Optional einen Best-Effort-Vorschlag ergänzen (klar markiert).

Wenn eine Implementierung an fehlenden Informationen hängt:
- Implementiere den "Rahmen" (Interface, Datentyp, Launch-Struktur, TODO-Kommentar),
- aber nicht die fachlich spekulative Logik.

======================================================================
PROJEKTKONTEXT (ZU BERÜCKSICHTIGEN)
======================================================================

Technischer Rahmen (aus Dokumentkontext):
- ROS2 Humble (Zielarchitektur)
- Unitree Go2 EDU
- Navigation: Nav2
- Follow über Nav2 Goal-Streaming (kein eigener Follow-Controller)
- SLAM/Localization: RTAB-Map (RGB-D), LiDAR primär für Costmaps
- TF-Baum: map -> odom -> base_link -> sensor_frames (URDF + robot_state_publisher)
- Deterministische Orchestrierung (State Machine / Behavior Tree)
- cmd_vel Ownership strikt gemäß Dokument-/Projektregeln
- Manipulation: MoveIt2 + D1-550-85
- RealSense D415
- Compute: Extension Board (Orin Nano 8GB / 40 TOPS), Technologien müssen dort realistisch laufen

Wichtige inhaltliche Regeln:
- Follow darf Nav2 nutzen, aber nicht selbst cmd_vel direkt publishen (sofern nicht ausdrücklich spezifiziert).
- Manipulation darf Base nicht direkt via cmd_vel bewegen; Umstellen über Nav2.
- Bei unklaren Contracts: markieren, nicht raten.

======================================================================
DATEIEN FÜR SPEZIFIKATIONSLÜCKEN / ENTSCHEIDUNGEN
======================================================================

Lege bzw. pflege diese Dateien, wenn nötig:
- OPEN_QUESTIONS.md        (Blocker, Unklarheiten, nötige Entscheidungen)
- ASSUMPTIONS_PROPOSED.md  (neu vorgeschlagene Defaults, klar als unverbindlich)
- IMPLEMENTATION_STATUS.md (was schon umgesetzt ist vs. was stub-only ist)

Format für OPEN_QUESTIONS.md (Beispiel):
- ID (z. B. Q001)
- Titel
- Blocker-Level (BLOCKER / PARTIAL / INFO)
- Betroffene Dateien/Komponenten
- Was im Dokument 002 fehlt/unklar ist
- Best-Effort Vorschlag (optional, klar markiert)
- Entscheidung durch Mensch nötig (Ja/Nein)

======================================================================
VERHALTEN BEI UNSICHERHEIT
======================================================================

Wenn du unsicher bist:
- nicht "wahrscheinlich richtig" implementieren, ohne Kennzeichnung.
- lieber Stub + klare Frage + konkreten Vorschlag.
- Ziel ist nicht nur Code, sondern auch präzise Rückmeldung über Dokumentlücken.

Dieses Verhalten ist ausdrücklich gewünscht:
Das Dokument 002 wird anhand deiner gefundenen Unklarheiten verbessert.
