# OPEN_QUESTIONS.md

Format follows `docs/IMPLEMENTATION_RULES_FOR_CODEX.md`.
Source of truth: `docs/Projektarbeit_dokument_002`.

## Phase-1 Shared-Surface-Audit Delta (2026-03-13)

Auditbereich in dieser Runde:
- `src/go2_apportation_msgs/`
- `config/contracts.yaml`
- `src/go2_apportation_orchestrator/`
- orchestratornahe Tests unter `tests/`

Nur aus Dokument 002 abgeleitete Audit-Befunde:
- Das im Dokument 002 genannte Minimal-Set Custom Interfaces ist inzwischen fuer `PredictedRegion.msg` und `InterceptGoal.msg` auch als IDL-Dateien im Repo gespiegelt.
- Der globale Shared Surface aus Dokument 002 ist nur teilweise technisch gespiegelt: `config/contracts.yaml` deckt Sensor-/Basis-Topics, Frames und inzwischen die eingefrorenen Person-Topics ab, aber noch nicht den restlichen missionsrelevanten Surface (`/tracking/*`, `/voice/command`, Manipulationssemantik, ggf. weitere Topics/Actions).
- Im Orchestrator existieren zwei Pfade mit unterschiedlichem Reifegrad: der Runtime-Kern (`transition_spec.py`, `orchestrator_runtime_core.py`) bildet die Dokument-States weitgehend ab; der aeltere Stub-Pfad (`state_contracts.py`, `orchestrator_node.py`) ist dagegen nicht mehr deckungsgleich.

Neu vorgeschlagen / nicht aus Dokument 002:
- Keine neuen fachlichen Defaults in dieser Audit-Runde. Offene Punkte werden unten als Fragen dokumentiert statt im Code vorweggenommen.
- Der kleine Pick-Freeze trennt inzwischen explizit zwischen normativen `PickObject.result_code`-Werten und daraus abgeleiteten Orchestrator-Events; offen bleibt nur, ob `safety_abort` spaeter auch als eigener Runtime-Eventname gespiegelt werden soll.
- Der kleine Wuerfel-/Tracking-Freeze setzt `object_last_seen` aktuell auf `map`, waehrend Dokument 002 die Topic-Frame-Policy dafuer noch `odom`-gefuehrt beschreibt; diese Harmonisierung bleibt offen.

## Minimalruntime Folgefragen nach lokalem Freeze-Run (2026-03-14)

Nur aus Dokument 002 plus geklaerten Freeze-Entscheidungen:
- `src/go2_person_perception/` ist jetzt ein kleiner lokaler Adapterrahmen. Er akzeptiert private lokale Eingänge, publiziert aber nach außen weiterhin nur die eingefrorenen Person-Topics.
- `src/go2_manipulation_runtime/` bildet bewusst nur Result-Code-/Semantik-Mapping, einen technischen Backend-Adapterrahmen und D1-550-Reuse-Punkte ab. Es ersetzt weder MoveIt noch den D1-550-Hardwarepfad.
- Die Manipulationsposturen `safe`, `carry`, `offer`, `pregrasp` bleiben lokal und werden nicht als Shared Surface hochgezogen.

- ID: Q015
  Titel: Minimaler Upstream-Anschluss fuer `go2_person_perception` noch offen
  Nachpflege-Prioritaet: 2 (lokale Integrationsfrage, kein Shared-Surface-Blocker)
  Entscheidungsstand (Benutzer): offen
  Dokument-Patch-Status: keine Dokumentaenderung noetig in diesem Run
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: `src/go2_person_perception/`
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 definiert die ausgehenden Person-Topics, aber nicht den internen lokalen Anschluss eines konkreten Detector-Nodes an dieses Surface-Paket.
  Warum blockiert das Implementierung konkret?: Der private Minimal-Anschluss auf lokales `PoseStamped`/`Bool` ist jetzt vorhanden; offen bleibt nur, welcher erste echte Detector-/Tracker-Pfad spaeter auf diese privaten Eingänge geschaltet wird.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss spaeter festlegen, ob der erste reale Anschluss direkt `PoseStamped` in `map` liefert oder ob ein lokaler Detector-Wrapper die Normierung übernimmt.
  Best-Effort Vorschlag (optional, klar markiert): Den ersten Realanschluss als kleinen lokalen Wrapper halten und keine weiteren globalen Person-Topics einführen.
  Entscheidung durch Mensch noetig: Ja

- ID: Q016
  Titel: Lokale normative Pick-/Release-Result-Codes muessen spaeter an echte Manipulationsausfuehrung gekoppelt werden
  Nachpflege-Prioritaet: 1 (naechster realer Manipulationsschritt)
  Entscheidungsstand (Benutzer): offen
  Dokument-Patch-Status: keine Dokumentaenderung noetig in diesem Run
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: `src/go2_manipulation_runtime/`, bestehender D1-550-/MoveIt-Bestand
  Was im Dokument 002 fehlt/unklar ist: Die Freeze-Semantik ist nun klar; offen ist nur noch die konkrete technische Ableitung aus MoveIt-/Controller-/Greiferfehlern auf diese lokale normative Ebene.
  Warum blockiert das Implementierung konkret?: Das Mapping ist jetzt als Helfer plus technischer Backend-Adapterrahmen vorhanden, aber noch nicht an einen echten `/manipulation/pick`- oder `/manipulation/release`-Adapter gebunden.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss spaeter festlegen, welche konkreten MoveIt-/Execution-Fehler als `PICK_FAILED`, `PICK_UNREACHABLE`, `PICK_TIMEOUT` oder `SAFETY_ABORTED` zaehlen.
  Best-Effort Vorschlag (optional, klar markiert): Erst einen sehr duennen Adapter auf den vorhandenen D1-550-/MoveIt-Bestand bauen und dabei die Result-Codes an genau einer Stelle ableiten.
  Entscheidung durch Mensch noetig: Ja

## Priorisierte Reihenfolge fuer verbleibende Dokument-/Spiegelungsarbeiten (Q001-Q013)

Ziel der Priorisierung: nur verbleibende Restoffenheiten nach bereits eingearbeiteten Dokument-Patches priorisieren (inkl. Spiegelung/Konsistenz).

1. `Q003` Restoffenheiten Message-/Action-Spezifikationen (IDL-Listings, BallState/Trajectory, vollstaendige Signaturen)
2. `Q007` Manual-Override Event/State Ausrollung (BT-/Statechart-Detailkonsistenz weiterhin offen)
3. `Q006` Restoffenheiten Manipulationsschnittstellen (IDL-Dateisignaturen / optionale numerische Enums in IDL)
4. `Q010` Konkrete RGB/Depth/CameraInfo Topicwerte fuer RTAB-Map Launch-Defaults fehlen in Repo-Configs
5. `Q009` Dokument-Encoding/Mojibake verursacht Mirror-Diffs (rtabmap-Appendix-Kommentar)
6. `Q004` Optionale Param-Sammelstelle fuer Yaw-Controller (Dokumentstruktur, nicht Fachinhalt)
7. `Q001/Q002/Q005/Q008` nur noch Regression-/Spiegelungschecks (weitgehend erledigt)
8. `Q011` URDF Basis-Frame (`base`) vs Runtime-Contract (`base_link`) fuer TF-Konsistenz
9. `Q012` Optionales xacro im Baseline-Container (`ros:humble-ros-base`)
10. `Q013` Verbindliche apt-Paketliste fuer Variant-A Board-Runtime (RealSense/RTAB-Map)

Hinweis:
- Q001/Q002/Q004/Q005/Q006 wurden in `docs/Projektarbeit_dokument_002` bereits textuell gepatcht; hier bleiben nur Restoffenheiten/Spiegelungsarbeiten.
- `Q007` ist als Folgefrage aus Q005 entstanden und im Dokument weiter ausgerollt (inkl. SM/BT- und Unterbrechungs-Hinweisen), aber noch nicht vollstaendig in BT-/Statechart-Detaildarstellungen ausformuliert.

## Fragen

- ID: Q001
  Titel: Unaufgeloester Platzhalter fuer cmd_vel_in_topic in Nav2-Appendix
  Nachpflege-Prioritaet: 6 (kleiner, lokaler Dokumentfehler / Appendix-Detail)
  Entscheidungsstand (Benutzer): Option A gewaehlt (`CmdVelNavTopic` Makro einfuehren)
  Dokument-Patch-Status: GEPATCHT in `docs/Projektarbeit_dokument_002` (Makro + Appendix-Referenz)
  Repo-Spiegelungs-Status: GEPATCHT (`config/contracts.yaml`, `config/nav2_params.yaml`)
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: `config/nav2_params.yaml`, `config/contracts.yaml`
  Was im Dokument 002 fehlt/unklar ist: Fachlich nichts mehr; nur als Trace-Eintrag fÃ¼r den behobenen Makrofehler.
  Warum blockiert das Implementierung konkret?: Aktuell nicht mehr blockierend (Dokument + relevante Mirrors synchronisiert).
  Minimalentscheidung (1 Satz), die ich treffen muss: Keine.
  Dokument-Patch-Hinweis: Makroblock am Dokumentanfang (Runtime-Contracts) und Appendix `nav2_params.yaml` (Section `nav2_params.yaml (Baseline)`).
  Best-Effort Vorschlag (optional, klar markiert): Keinen neuen Platzhalter in Code/Contracts erfinden; Appendix-Zeile unveraendert als Dokumentspiegelung belassen, bis Dokument 002 gepatcht ist.
  Entscheidung durch Mensch noetig: Nein

- ID: Q002
  Titel: Konkrete Runtime-Topic-Namen bleiben offen
  Nachpflege-Prioritaet: 2 (breiter Interface-Blocker fuer Integrationsarbeit)
  Entscheidungsstand (Benutzer): Option C gewaehlt und kritischer Topic-Satz konkretisiert (inkl. `CMD_VEL_NAV_TOPIC=/nav2/cmd_vel`)
  Dokument-Patch-Status: GEPATCHT in `docs/Projektarbeit_dokument_002` (Makros + relevante Textstellen)
  Repo-Spiegelungs-Status: TEILWEISE GEPATCHT (`config/contracts.yaml` synchronisiert; Appendix-Extrakte teilweise, siehe Q009)
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: `config/contracts.yaml`, Bringup/Perception/Nav2-Integration, Appendix-Templates
  Was im Dokument 002 fehlt/unklar ist: Fachlich nichts Kritisches mehr; verbleibende Mirror-Abweichung betrifft einen Encoding-Kommentar in `rtabmap_params` (siehe Q009).
  Warum blockiert das Implementierung konkret?: Aktuell nur geringe Doku-/Mirror-Divergenz (Kommentartext), kein fachlicher Topic-Blocker mehr.
  Minimalentscheidung (1 Satz), die ich treffen muss: Keine.
  Dokument-Patch-Hinweis: Runtime-Contract-Makros (Dokumentanfang), Kapitel `Pakete & Schnittstellen` / `Schnittstellen-Contracts`, Appendix-YAMLs (`nav2_params.yaml`, `rtabmap_params.yaml`, `realsense.yaml`).
  Best-Effort Vorschlag (optional, klar markiert): `contracts.yaml` und Appendix-Extrakte kontrolliert spiegeln und Abweichungen explizit dokumentieren.
  Entscheidung durch Mensch noetig: Nein

- ID: Q003
  Titel: Message- und Action-Spezifikationen unvollstaendig
  Nachpflege-Prioritaet: 3 (starker Interface-Blocker fuer Orchestrator/Tracking/Manipulation)
  Entscheidungsstand (Benutzer): Option B gewaehlt und Minimal-Set benannt (`Detection3D`, `Detection3DArray`, `ObjectState`, `ThrowStatus`, `PredictedRegion`, `InterceptGoal`; Pflicht: `PickObject.action`, `ReleaseObject.srv`)
  Dokument-Patch-Status: TEILWEISE GEPATCHT in `docs/Projektarbeit_dokument_002` (Minimal-Set, `PredictedRegion`, `InterceptGoal`, `PickObject`, `ReleaseObject` textuell spezifiziert)
  Blocker-Level: BLOCKER
  Betroffene Dateien/Komponenten: `src/go2_apportation_msgs`, Tracking-/Manipulation-Interfaces, spaetere Actions
  Was im Dokument 002 fehlt/unklar ist: `PredictedRegion`, `InterceptGoal`, `PickObject`, `ReleaseObject` sind textuell nachgezogen; offen sind vollstÃ¤ndige IDL-Listings/Dateisignaturen sowie die Rolle von `BallState`/`Trajectory` (nur als spÃ¤tere Erweiterung markiert).
  Warum blockiert das Implementierung konkret?: Ohne Felddefinitionen und Request/Result/Feedback-Semantik koennen Actions/Msgs nur als spekulative Stubs angelegt werden, was spaetere Inkompatibilitaeten erzeugt.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss entscheiden, ob die aktuellen textuellen Spezifikationen zusÃ¤tzlich als vollstÃ¤ndige IDL-Listings im Dokument festgeschrieben werden und wie `BallState`/`Trajectory` in v002-patchX behandelt werden.
  Dokument-Patch-Hinweis: Kapitel `Message-& Service-Spezifikationen` (Sections `BallState, Trajectory, InterceptGoal`, `Action Definitionen`), plus Rueckverweise in Tracking-/Orchestrator-/Manipulationskapiteln.
  Best-Effort Vorschlag (optional, klar markiert): `Detection3D/Array`, `ObjectState`, `ThrowStatus`, `PredictedRegion` und `InterceptGoal` koennen als dokumentnah eingefrorene Minimal-Interfaces behandelt werden; offen bleiben vor allem spaetere erweiterte Tracking-Semantiken.
  Entscheidung durch Mensch noetig: Ja (Detailspezifikation/Felder noch offen)

- ID: Q004
  Titel: OBSERVE_HAND Yaw-Align Beschreibung ist intern uneinheitlich
  Nachpflege-Prioritaet: 5 (Design-Inkonsistenz, aber Phase-1 ohne Laufzeitlogik noch handhabbar)
  Entscheidungsstand (Benutzer): Option C gewaehlt und Aktivierungs-/Ownership-Rahmen konkretisiert (Baseline Nav2, optional lokaler Yaw-Controller nur via Mux)
  Dokument-Patch-Status: GEPATCHT in `docs/Projektarbeit_dokument_002` (OBSERVE_HAND Notes/Pipeline + Parameter-Baseline)
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: Orchestrator/OBSERVE_HAND Stub, spaetere Beobachtungs-/Tracking-Integration
  Was im Dokument 002 fehlt/unklar ist: Die Inkonsistenz wurde aufgelÃ¶st; offen bleibt nur die Frage, ob/wo die Parameter zusÃ¤tzlich in einer zentralen Parametertabelle/Appendix gesammelt werden sollen.
  Warum blockiert das Implementierung konkret?: Die Wahl bestimmt, ob ein separater Regelkreis/Node benoetigt wird oder ob OBSERVE_HAND nur rate-limitierte Nav2-Goal-Updates erzeugt, was unterschiedliche Schnittstellen erzeugt.
  Minimalentscheidung (1 Satz), die ich treffen muss: Keine neue Fachentscheidung; ich muss nur festlegen, ob die Q004-Parameter zusÃ¤tzlich in einem zentralen Param-Listing/Appendix gespiegelt werden.
  Dokument-Patch-Hinweis: Kapitel `Orchestrierung & Zustandslogik` (state-spezifische Notes zu `OBSERVE_HAND`) und Abschnitt `Pipeline je Missionsschritt` -> `OBSERVE_HAND`.
  Best-Effort Vorschlag (optional, klar markiert): Phase 1 nur abstrakte OBSERVE_HAND-Schnittstelle/Stub ohne Controller-Implementierung.
  Entscheidung durch Mensch noetig: Nein (nur optionale Dokumentstrukturfrage)

- ID: Q005
  Titel: cmd_vel Ownership Erweiterung (Teleop/Twist-Mux) noch nicht dokumentiert
  Nachpflege-Prioritaet: 1 (architektur- und safety-relevant, wirkt auf viele Folgeentscheidungen)
  Entscheidungsstand (Benutzer): Option B gewaehlt und konkretisiert (Twist-Mux, `/cmd_vel` Single Writer am Mux-Ausgang; Quellen/Prioritaeten/Timeout/Safety-Position definiert)
  Dokument-Patch-Status: GEPATCHT in `docs/Projektarbeit_dokument_002` (Architektur/Datenfluss, Nav2-Interfaces, Ownership/Safety, Orchestrator-Integration)
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: Orchestrator/Safety/Ownership-Abstraktion, Nav2/Teleop-Integration, spaetere Bringup-Architektur
  Was im Dokument 002 fehlt/unklar ist: Kerncontract ist nachgezogen; offene Restpunkte sind in Q007 (Ausrollung) und Q009 (Encoding-/Mirror-Diff) ausgelagert.
  Warum blockiert das Implementierung konkret?: Ohne dokumentierten Ownership-Contract ist unklar, welche Komponenten spaeter `cmd_vel` oder Vorstufen-Topics schreiben duerfen und wie Safety/Arbitration modelliert werden muss.
  Minimalentscheidung (1 Satz), die ich treffen muss: Keine neue Fachentscheidung; ich muss nur die dokumentweite Konsistenz des bereits gepatchten Twist-Mux-Contracts prÃ¼fen und Reststellen angleichen.
  Dokument-Patch-Hinweis: Kapitel `Systemarchitektur` (Datenfluesse, Schnittstellen-Contracts `Navigation (Nav2)`), Kapitel `Orchestrierung & Zustandslogik` (`cmd_vel Ownership und Safety Gate`), ggf. Sicherheitskapitel.
  Best-Effort Vorschlag (optional, klar markiert): In Phase 1 Ownership nur abstrakt modellieren; keine harte Nav2-only Enforcement-Logik implementieren, bis Dokument 002 aktualisiert ist.
  Entscheidung durch Mensch noetig: Nein

- ID: Q006
  Titel: Konkrete Manipulationsschnittstellen und Greifstrategie fehlen
  Nachpflege-Prioritaet: 4 (groesser fachlicher Blocker, aber nach Interface-/Ownership-Klaerung besser nachziehbar)
  Entscheidungsstand (Benutzer): Option B gewaehlt und Kernsemantik konkretisiert (Pick=Action, Release=Service; Mindestfelder/Fehlercodes/Timeout-Rahmen beschrieben)
  Dokument-Patch-Status: GEPATCHT in `docs/Projektarbeit_dokument_002` (Manipulation/Handover + Action/Service-Spezifikation textuell)
  Blocker-Level: BLOCKER
  Betroffene Dateien/Komponenten: spaetere Manipulation package/action stubs, Orchestrator `PICK/HANDOVER`, MoveIt2-Integration
  Was im Dokument 002 fehlt/unklar ist: Kernsemantik ist dokumentiert; offen sind vollstÃ¤ndige IDL-Dateisignaturen/Appendix-Listings und ggf. formale Enum-Konstanten in den IDL-Dateien.
  Warum blockiert das Implementierung konkret?: Ohne Greif-/Release-Semantik, Kontaktbedingungen und Action-Contracts lassen sich `PICK` und `HANDOVER_RELEASE` nur als rein symbolische States ohne belastbare Schnittstellen implementieren.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss entscheiden, ob die textuellen Signaturen/Result-Codes zusÃ¤tzlich als vollstÃ¤ndige `.action`/`.srv`-Listings im Dokument-Appendix festgeschrieben werden.
  Dokument-Patch-Hinweis: Kapitel `Manipulation & Handover` (Sections `Greifstrategie & Kontaktbedingungen`, `Gripper-Schnittstellen (Actions)`, `Uebergabeprotokoll & Events`, `Fail-Safe Ablegen`) sowie Kapitel `Message-& Service-Spezifikationen`.
  Best-Effort Vorschlag (optional, klar markiert): Nur Namens-/Endpoint-Hinweise und State-Platzhalter belassen; keine fachliche Manipulationslogik oder Action-Definitionen erfinden.
  Entscheidung durch Mensch noetig: Ja (vollstÃ¤ndige IDL-Listings/Appendix-Reife noch offen)

- ID: Q007
  Titel: Manual-Override Event/State im Zustandsautomaten noch nicht in Dokumentstruktur verankert
  Nachpflege-Prioritaet: 4 (Folgefrage aus Q005; notwendig fuer konsistente Transition-Tabellen)
  Entscheidungsstand (Benutzer): Verhalten vorgegeben; Dokument verwendet jetzt `INTERRUPTED`, `MANUAL_OVERRIDE_ACTIVE`, `MANUAL_OVERRIDE_RELEASED`, no-auto-resume
  Dokument-Patch-Status: TEILWEISE GEPATCHT in `docs/Projektarbeit_dokument_002` (State/Event-Liste, Diagramm, Any-State, State-Actions, Ownership-Abschnitt, SM/BT-Design-Hinweis, Mode-Manager-Hinweistext)
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: Orchestrator-Events/States/Transition-Table, Teleop/Mux-Integration, spaetere BT/State-Machine Implementierung
  Was im Dokument 002 fehlt/unklar ist: Kernintegration ist erfolgt und weiter ausgerollt; offen bleibt die vollstaendige Ausrollung in allen relevanten BT-/Statechart-Detaildarstellungen (z. B. konkrete Resume-/Reentry-Regeln jenseits Any-State/Ownership/Mode-Manager-Hinweisen).
  Warum blockiert das Implementierung konkret?: Der Kern blockiert nicht mehr; verbleibend ist ein Konsistenz-/Reife-Thema fuer spaetere konkrete BT-/Statechart-Ausrollung (Resume-/Reentry-Verhalten dokumentweit gleich halten).
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss nur noch entscheiden, wie `INTERRUPTED`/Resume in spaeteren BT-/Statechart-Detaildarstellungen explizit modelliert wird (ohne Auto-Resume beizubehalten).
  Dokument-Patch-Hinweis: Kapitel `Zustandsautomat & Events` (Zustaende + Events), `Orchestrierung & Zustandslogik` (Any-State Regeln, Transition Table, State-Actions fuer Pause/Interrupted), `State Machine / Behavior Tree Design`, `Mode Manager (SMACC2/BT)`.
  Best-Effort Vorschlag (optional, klar markiert): `INTERRUPTED` als alleinigen Unterbrechungszustand beibehalten und Resume nur ueber explizite `vc_resume`-/Mode-Kommandos in einer kurzen Zusatz-Transitionstabelle oder BT-Resume-Policy nachziehen.
  Entscheidung durch Mensch noetig: Ja (vollstaendige Transition-/BT-Ausrollung noch offen)
- ID: Q008
  Titel: Topicname fuer Intercept-Ziel auf `intercept_goal` umbenennen (Semantik passend zu `InterceptGoal.msg`)
  Nachpflege-Prioritaet: 6 (Trace-/Regressionseintrag; Dokument-Patch erfolgt)
  Entscheidungsstand (Benutzer): Topicname auf `/tracking/intercept_goal` festgelegt (Typ bleibt `go2_apportation_msgs/InterceptGoal.msg`)
  Dokument-Patch-Status: GEPATCHT in `docs/Projektarbeit_dokument_002` (Topiclisten, Tracking-Outputs, Orchestrator-Aktionsreferenz)
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: Tracking-Topic-Contracts, Tracking-Output-Semantik, spaetere Msg-/Node-Implementierung
  Was im Dokument 002 fehlt/unklar ist: Fachlich nichts Kritisches mehr; ggf. spaeter optionaler Deprecation-/Alias-Hinweis nur falls Runtime-Kompatibilitaet mit Alt-Tools relevant wird.
  Warum blockiert das Implementierung konkret?: Aktuell nicht mehr blockierend; Benennungs-/Semantikkonsistenz ist im Dokument nachgezogen.
  Minimalentscheidung (1 Satz), die ich treffen muss: Keine.
  Dokument-Patch-Hinweis: `Pakete & Schnittstellen` -> `Tracking & Throw-Logic`, Kapitel `Objekt-Tracking & Praediktion` -> `Trajektorien & ETA (Region statt Punkt)`, Transition-Tabellenaktionen (`nav_goal(intercept_goal)`).
  Best-Effort Vorschlag (optional, klar markiert): Falls spaeter Alt-Tools existieren, Deprecation-Hinweis oder Alias nur explizit und zeitlich befristet dokumentieren.
  Entscheidung durch Mensch noetig: Nein
- ID: Q009
  Titel: Dokument-Encoding/Mojibake erzeugt Mirror-Diff im `rtabmap_params`-Appendix
  Nachpflege-Prioritaet: 5 (Dokumenthygiene/Konsistenz, kein Fachentscheidungs-Blocker)
  Entscheidungsstand (Benutzer): keine Entscheidung erforderlich; technischer Konsistenzpunkt
  Dokument-Patch-Status: OFFEN (bekanntes Dokument-Encoding-Thema)
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: `docs/Projektarbeit_dokument_002`, `config/rtabmap_params.yaml` (Extraktvergleich)
  Was im Dokument 002 fehlt/unklar ist: Ein Kommentar im RTAB-Map-Appendix enthÃ¤lt Mojibake im Dokumenttext; der extrahierte Repo-Extrakt hat die lesbare Variante.
  Warum blockiert das Implementierung konkret?: Fachlich nicht blockierend, aber automatische Dok->Repo-Spiegelvergleiche melden unnÃ¶tige Diffs.
  Minimalentscheidung (1 Satz), die ich treffen muss: Keine Fachentscheidung; ich muss nur entscheiden, ob die Doku-Encoding-Bereinigung jetzt oder gesammelt spÃ¤ter erfolgt.
  Dokument-Patch-Hinweis: Appendix `rtabmap_params.yaml` Kommentarzeile zu ``phantom obstacles''.
  Best-Effort Vorschlag (optional, klar markiert): Repo-Datei vorerst nicht auf Mojibake-Text spiegeln; Encoding-Bereinigung als separate Doku-Hygiene-Runde durchfÃ¼hren.
  Entscheidung durch Mensch noetig: Nein

- ID: Q010
  Titel: RTAB-Map Scaffolds koennen RGB/Depth/CameraInfo Defaults nicht aus Config konkret ableiten
  Nachpflege-Prioritaet: 5 (Launcher nutzbar, aber nur mit expliziten CLI-Args)
  Entscheidungsstand (Benutzer): offen
  Dokument-Patch-Status: OFFEN
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: `config/rtabmap_params.yaml`, `config/realsense.yaml`, `launch/rtabmap_mapping.launch.py`, `launch/rtabmap_localization.launch.py`
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 benennt Makros (`RgbTopic`, `DepthTopic`, `CameraInfoTopic`), die Repo-Config `config/rtabmap_params.yaml` enthaelt jedoch nur Makro-Platzhalterstrings und keine konkreten Runtime-Topics. `config/realsense.yaml` liefert ebenfalls keine eindeutigen Runtime-Topicnamen/Namespaces.
  Warum blockiert das Implementierung konkret?: Launch-Defaults fuer `rgb_topic`, `depth_topic`, `camera_info_topic` sind ohne Spekulation nicht hart setzbar; Scaffolds muessen diese Topics aktuell als required args erzwingen (mit separater Discovery-Hilfe).
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss entscheiden, ob konkrete Runtime-Topicnamen (oder ein standardisiertes Mapping) in den Repo-Configs festgeschrieben werden, damit die RTAB-Map Launches ohne Pflicht-CLI-Args starten koennen.
  Dokument-Patch-Hinweis: Runtime-Contracts/Makro-Block und RTAB-Map Appendix-Abschnitt (`rtabmap_params.yaml`) sowie zugehoerige Repo-Mirror-Dateien.
  Best-Effort Vorschlag (optional, klar markiert): Bis zur Klaerung bleiben `rgb_topic`, `depth_topic`, `camera_info_topic` als verpflichtende Launch-Argumente ohne Default.
  Entscheidung durch Mensch noetig: Ja

- ID: Q011
  Titel: URDF Basis-Frame ist `base`, waehrend Runtime-Vertrag `base_link` fordert
  Nachpflege-Prioritaet: 2 (direkter TF-Integrationspunkt fuer robot_state_publisher + TF-Adapter)
  Entscheidungsstand (Benutzer): offen
  Dokument-Patch-Status: OFFEN
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: `src/go2_description/urdf/go2.urdf`, `src/go2_tf_tools/go2_tf_tools/odom_to_tf_broadcaster.py`, `launch/board_minimal.launch.py`
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 setzt den TF-Vertrag auf `map -> odom -> base_link`; die aktuell eingebundene Go2-URDF hat als Hauptbasis-Link `base` statt `base_link`.
  Warum blockiert das Implementierung konkret?: Ohne explizite Angleichung entstehen getrennte TF-Teilbaeume (`odom->base_link` Adapterpfad versus `base` als URDF-Wurzel), wodurch Sensor-/Manipulator-Frames nicht automatisch unter `base_link` haengen.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss festlegen, ob die URDF auf `base_link` umbenannt wird oder ein expliziter fixer `base_link->base` Frame-Bridge-Ansatz als Standard gilt.
  Dokument-Patch-Hinweis: TF-/Frame-Contract Abschnitte (`map->odom->base_link`) und URDF/RSP-Hinweise.
  Best-Effort Vorschlag (optional, klar markiert): Kurzfristig URDF unveraendert lassen und die Frame-Angleichung als explizite Integrationsentscheidung nachziehen.
  Entscheidung durch Mensch noetig: Ja

- ID: Q012
  Titel: Xacro ist im Baseline-Image `ros:humble-ros-base` nicht verfuegbar
  Nachpflege-Prioritaet: 4 (kein Blocker fuer URDF-Pfad, aber relevant fuer xacro-basierte Modelle)
  Entscheidungsstand (Benutzer): offen
  Dokument-Patch-Status: OFFEN
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: `src/go2_description/launch/robot_state_publisher.launch.py`, Container-Baseline `ros:humble-ros-base`
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 fordert URDF/TF-Infrastruktur, legt aber keine Container-Paketliste fuer optionale xacro-Auswertung fest.
  Warum blockiert das Implementierung konkret?: Das neue Launchfile unterstuetzt `.xacro`, kann im aktuellen Baseline-Container jedoch nur plain-URDF sicher starten, solange `xacro` nicht installiert ist.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss entscheiden, ob `xacro` in die Baseline-Containerumgebung aufgenommen wird oder `.xacro` nur in erweiterten Images erlaubt ist.
  Dokument-Patch-Hinweis: Plattform-/Runtime-Baseline und URDF/TF-Bereitstellung.
  Best-Effort Vorschlag (optional, klar markiert): Default auf `urdf/go2.urdf` beibehalten und xacro nur optional per `model:=...xacro` aktivieren.
  Entscheidung durch Mensch noetig: Ja

- ID: Q013
  Titel: Verbindliche apt-Paketliste fuer Variant-A Board-Runtime (RealSense/RTAB-Map) im `ros:humble-ros-base`
  Nachpflege-Prioritaet: 3 (entscheidet Reproduzierbarkeit auf Board-Containern)
  Entscheidungsstand (Benutzer): Verifiziert (2026-03-04, ARM64, `ros:humble-ros-base`)
  Dokument-Patch-Status: OFFEN
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: `scripts/docker/install_realsense_deps.sh`, Board Runtime Container, spaeterer RTAB-Map Runtime-Stack
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 fixiert Architektur/Komponenten, aber keine konkrete apt-Paketliste fuer den Baseline-Container.
  Warum blockiert das Implementierung konkret?: Der Verifikationsschritt ist erfolgt; verbleibend ist nur optionale Entscheidung, ob zusaetzliche Repos fuer `librealsense2-*` eingebunden werden sollen.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss nur entscheiden, ob ich fuer optionales `librealsense2-utils` zusaetzliche apt-Repos zulasse.
  Dokument-Patch-Hinweis: Plattform-/Runtime-Baseline und Bringup-Abschnitte.
  Verifizierte Evidenz: `artifacts/apt/20260304_185914/01_apt_update.log`, `02_apt_cache_search_realsense.log`, `03_apt_policy_ros_humble_realsense2_camera.log`, `04_apt_policy_librealsense_candidates.log`, `05_librealsense_resolution_check.log`.
  Verifizierte Paketlage (ARM64, `ros:humble-ros-base`): `ros-humble-realsense2-camera` verfuegbar (Candidate `4.56.4-2jammy.20260219.025051`); `librealsense2-utils`, `librealsense2-dev`, `librealsense2-dkms` nicht in den konfigurierten Repos auffindbar.
  Best-Effort Vorschlag (optional, klar markiert): Minimal reproduzierbar nur `ros-humble-realsense2-camera` als Pflicht installieren; optionales `librealsense2-utils` nur dann, wenn spaeter ein Candidate in `apt-cache policy` erscheint.
  Entscheidung durch Mensch noetig: Nein (fuer Minimalbaseline); Ja (nur falls zusaetzliche librealsense-Repos gewuenscht sind)

- ID: Q014
  Titel: `PredictedRegion.msg` und `InterceptGoal.msg` fehlen trotz Dokument-002-Minimal-Set
  Nachpflege-Prioritaet: 1 (direkte Shared-Surface-Luecke fuer Tracking/Intercept)
  Entscheidungsstand (Benutzer): Msg-Nachzug fuer diese Runde freigegeben
  Dokument-Patch-Status: Fachlich GEPATCHT in `docs/Projektarbeit_dokument_002`, Repo-Umsetzung GEPATCHT
  Blocker-Level: INFO
  Betroffene Dateien/Komponenten: `src/go2_apportation_msgs/`, Tracking, `INTERCEPT`, orchestratornahe Spaeterintegration
  Was im Dokument 002 fehlt/unklar ist: Fuer den aktuellen Minimal-Nachzug nichts Blockierendes; spaetere Erweiterungen ueber das dokumentierte Minimalfeldset hinaus bleiben offen.
  Warum blockiert das Implementierung konkret?: Aktuell nicht mehr blockierend; die Wire-Types fuer `/tracking/predicted_region` und `/tracking/intercept_goal` sind jetzt angelegt.
  Minimalentscheidung (1 Satz), die ich treffen muss: Keine weitere Minimalentscheidung fuer diese Msgs.
  Dokument-Patch-Hinweis: Kapitel `Message-& Service-Spezifikationen` und Tracking-Abschnitte in `docs/Projektarbeit_dokument_002`.
  Best-Effort Vorschlag (optional, klar markiert): Keine weiteren Felder oder Bewegungssemantiken auf diese Msgs aufsetzen, solange dafuer kein neuer Dokumententscheid vorliegt.
  Entscheidung durch Mensch noetig: Nein

- ID: Q015
  Titel: `config/contracts.yaml` spiegelt den missionsrelevanten Shared Surface nur teilweise
  Nachpflege-Prioritaet: 2 (Audit-/Freeze-Reife, aber kein Laufzeitblocker)
  Entscheidungsstand (Benutzer): offen
  Dokument-Patch-Status: OFFEN
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: `config/contracts.yaml`, spaetere Integrationspruefungen
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 nennt den vollen Shared Surface, legt aber nicht explizit fest, wie weit `config/contracts.yaml` als technischer Mirror reichen muss.
  Warum blockiert das Implementierung konkret?: Der Repo-Mirror deckt inzwischen Basis-Sensorik/Nav2/Frames und die eingefrorenen Person-Topics ab, bleibt aber fuer den restlichen missionsweiten Surface bewusst partiell; ohne klare Spiegelungsgrenze entstehen leicht uneinheitliche Teil-Mirrors.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss festlegen, ob `config/contracts.yaml` kuenftig nur Runtime-Basiswerte spiegelt oder auch den missionsweiten Shared Surface (Perception/Tracking/Voice/Manipulation/Follow) explizit aufnehmen soll.
  Dokument-Patch-Hinweis: Kapitel `Pakete & Schnittstellen`, `Tracking & Throw-Logic`, `Manipulation`, `Voice Interface` in `docs/Projektarbeit_dokument_002`.
  Best-Effort Vorschlag (optional, klar markiert): Fuer den Minimal-Freeze zunaechst nur dokumentieren, dass `contracts.yaml` ein Teilspiegel ist; keine ungeprueften neuen YAML-Keys einfuehren.
  Entscheidung durch Mensch noetig: Ja

- ID: Q016
  Titel: Alter Orchestrator-Stub ist nicht mehr deckungsgleich zum dokumentnahen Runtime-Kern
  Nachpflege-Prioritaet: 3 (Stale Surface im erlaubten Bereich)
  Entscheidungsstand (Benutzer): offen
  Dokument-Patch-Status: nicht relevant; Repo-Konsistenzfrage
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: `src/go2_apportation_orchestrator/go2_apportation_orchestrator/state_contracts.py`, `src/go2_apportation_orchestrator/go2_apportation_orchestrator/orchestrator_node.py`
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 ist hier klar; die Unklarheit betrifft den Repo-Status, weil `state_contracts.py`/`orchestrator_node.py` noch einen aelteren, kleineren Contract spiegeln.
  Warum blockiert das Implementierung konkret?: Fuer den Shared-Surface-Audit existieren im gleichen Paket zwei konkurrierende Contract-Sichten; z. B. fehlen dort `INTERRUPTED`, `MANUAL_OVERRIDE_ACTIVE`, `MANUAL_OVERRIDE_RELEASED`, waehrend ein nicht mehr im Runtime-Kern genutztes `false_throw_suspected` weitergefuehrt wird.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss entscheiden, ob der Alt-Stub in Phase 2 ausgerichtet, explizit als legacy markiert oder ganz entfernt werden soll.
  Dokument-Patch-Hinweis: keines; dies ist ein Repo-Auditpunkt.
  Best-Effort Vorschlag (optional, klar markiert): Vorerst nur als stale/unconnected dokumentieren und keinen Refactor in dieser Audit-Runde erzwingen.
  Entscheidung durch Mensch noetig: Ja

- ID: Q017
  Titel: `SEARCH_OBJECT_GLOBAL` ist technisch nur nominell vorhanden, aber nicht an einen echten `/follow_waypoints`-Surface gekoppelt
  Nachpflege-Prioritaet: 2 (direkter Orchestrator-Blocker fuer globale Suche)
  Entscheidungsstand (Benutzer): offen
  Dokument-Patch-Status: fachlich klar in `docs/Projektarbeit_dokument_002`, Repo-Umsetzung OFFEN
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_spec.py`, Skills/Adapter, spaetere globale Suchpfade
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 nennt `/follow_waypoints` klar als Nav2-Action und beschreibt SEARCH_OBJECT_GLOBAL als waypoint-/exploration-basiert; unklar ist nur, ob der Orchestrator in der aktuellen Repo-Stufe schon einen separaten Adapterpunkt dafuer tragen soll.
  Warum blockiert das Implementierung konkret?: Der State `SEARCH_OBJECT_GLOBAL` existiert technisch, aber die aktuelle Bridge-Lage bietet nur `/navigate_to_pose`; damit ist globale Suche im Paketkern nicht ueber einen eigenen Waypoint-Surface gekoppelt.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss festlegen, ob ein minimaler eigener `/follow_waypoints`-Adapterpunkt in der naechsten Phase noetig ist oder ob SEARCH_OBJECT_GLOBAL vorerst bewusst nominell bleibt.
  Dokument-Patch-Hinweis: Kapitel `Pakete & Schnittstellen` (`Navigation (Nav2)`), `State-Actions` fuer `SEARCH_OBJECT_GLOBAL`, `Pipeline je Missionsschritt`.
  Best-Effort Vorschlag (optional, klar markiert): In dieser Runde nur als nominell/teilverbunden dokumentieren; keinen spekulativen Waypoint-Client bauen.
  Entscheidung durch Mensch noetig: Ja

- ID: Q018
  Titel: Harmonisierung fuer `/perception/object_last_seen` zwischen Dokument 002 und abgestimmtem Minimal-Freeze
  Nachpflege-Prioritaet: 2 (Shared-Surface-Konsistenzpunkt)
  Entscheidungsstand (Benutzer): abgestimmter Freeze fuer diese Runde setzt `geometry_msgs/PoseStamped` in `map`
  Dokument-Patch-Status: OFFEN
  Blocker-Level: PARTIAL
  Betroffene Dateien/Komponenten: `docs/Projektarbeit_dokument_002`, `config/contracts.yaml`, spaetere Perception-/Orchestrator-Anbindung
  Was im Dokument 002 fehlt/unklar ist: Dokument 002 beschreibt `/perception/object_last_seen` als Pose + Timestamp und in der Frame-Policy `odom`-gefuehrt; der abgestimmte Freeze dieser Runde setzt den Topic-Zielframe dagegen auf `map`.
  Warum blockiert das Implementierung konkret?: Ohne Harmonisierung bleibt unklar, ob Reacquire-/Return-nahe Komponenten `object_last_seen` als lokalen Tracking-Anker (`odom`) oder als globaleren Referenzpunkt (`map`) behandeln sollen.
  Minimalentscheidung (1 Satz), die ich treffen muss: Ich muss entscheiden, ob Dokument 002 auf `map` nachgezogen wird oder ob der Freeze spaeter wieder auf `odom` zurueckgefuehrt werden soll.
  Dokument-Patch-Hinweis: Kapitel `Pakete & Schnittstellen` (`Perception (Object)`) und Tabelle `Topic--Frame Zuordnung (Contract)`.
  Best-Effort Vorschlag (optional, klar markiert): Bis zur Harmonisierung den Freeze explizit als abgestimmte Abweichung markieren und keine weitere technische Semantik darauf aufbauen.
  Entscheidung durch Mensch noetig: Ja
