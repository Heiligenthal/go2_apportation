# DECISION_TEMPLATES.md

Nicht verbindliche Vorschlagsstruktur zur Dokument-Nachpflege von `docs/Projektarbeit_dokument_002`.

Zweck:
- Entscheidungen fuer `Q001` bis `Q006` konsistent festhalten
- Dokument-Patches vorbereiten, ohne stillschweigende Architekturentscheidungen
- Implementierungsfreigabe pro Frage explizit machen

Hinweise:
- Quelle bleibt `docs/Projektarbeit_dokument_002`
- `config/contracts.yaml` bleibt technische Spiegelung, keine fachliche Quelle
- `cmd_vel` Ownership fuer Phase 1 Implementierung weiterhin abstrakt halten (Dokumententscheidung ist gepatcht; keine Laufzeitlogik daraus vorziehen)

## Eingegangene Entscheidungen (Benutzer; in Dokument 002 eingearbeitet, soweit unten nicht anders markiert)

- `Q005`: Option B (`Twist-Mux`, `/cmd_vel` Single Writer am Mux-Ausgang)
- `Q002`: Option C (kritische Topics jetzt festlegen)
- `Q003`: Option B (Minimal-Set Custom Interfaces)
- `Q006`: Option B (Pick = Action, Release = Service)
- `Q004`: Option C (Baseline Nav2, optional lokaler Yaw-Controller ueber Mux)
- `Q001`: Option A (`CmdVelNavTopic` Makro einfuehren)
- `Q007` (Folgefrage): `INTERRUPTED`, `MANUAL_OVERRIDE_ACTIVE`, `MANUAL_OVERRIDE_RELEASED`, kein Auto-Resume (weiter in Dokument 002 ausgerollt; BT-/Statechart-Details weiter offen)
- `Q008` (Folgefrage): Topic-Rename auf `/tracking/intercept_goal` (Typ bleibt `InterceptGoal.msg`) - in Dokument 002 eingearbeitet

## Q007 Status (Folgefrage, kein neues Entscheidungstemplate)

- Status: weiter in `docs/Projektarbeit_dokument_002` eingearbeitet (`INTERRUPTED`, `MANUAL_OVERRIDE_*`, Any-State-Regel, Ownership-Text, State-Actions, SM/BT-Design-Hinweis, Mode-Manager-Hinweistext)
- Verbleibende Restoffenheit: vollstaendige Ausrollung in allen BT-/Statechart-Detaildarstellungen (kein Auto-Resume beibehalten)
- Keine neue Fachentscheidung in dieser Datei eingefuehrt; nur Patch-Status/Restumfang markiert

## Q008 Status (Folgefrage, kein neues Entscheidungstemplate)

- Status: in `docs/Projektarbeit_dokument_002` eingearbeitet (Topicname dokumentweit auf `/tracking/intercept_goal` nachgezogen; Typ bleibt `InterceptGoal.msg`)
- Verbleibende Restoffenheit: keine fachliche Restoffenheit; optional spaeter Deprecation-/Alias-Hinweis nur bei echter Runtime-Kompatibilitaetsanforderung
- Keine neue Fachentscheidung in dieser Datei eingefuehrt; nur Patch-Status/Restumfang markiert

## Allgemeines Template (optional)

- Frage-ID:
- Entscheidungsdatum:
- Entscheider:
- Status: offen / entschieden / zurueckgestellt
- Gewaehlte Option:
- Begruendung (1-3 Saetze):
- Dokument-Patch erforderlich: Ja/Nein
- Betroffene Dokumentstellen:
- Folgeaufgaben im Repo (nur Struktur/Stubs oder konkret):

## Q001 Template - `CmdVelNavTopic` im Nav2-Appendix

- Frage-ID: `Q001`
- Ziel der Entscheidung: Aufloesung des fehlenden Makros/Platzhalters fuer `cmd_vel_in_topic` in der Nav2-Appendix.
- Betroffene Dokumentstellen (voraussichtlich):
  - Runtime-Contract-Makros am Dokumentanfang
  - Appendix `nav2_params.yaml (Baseline)`

- Optionen (Vorschlagsstruktur, nicht verbindlich):
  - Option A: Neues Makro `CmdVelNavTopic` im Makroblock definieren
  - Option B: Kein neues Makro; `cmd_vel_in_topic` im Appendix direkt mit finalem Topic-Namen dokumentieren
  - Option C: Bestehendes Makro/Benennung verwenden (falls Namensfehler im Appendix)

- Konsequenzen:
  - Option A: Saubere Makro-Konsistenz im Appendix, aber neue Contract-Stelle im Dokument muss gepflegt werden
  - Option B: Weniger Makros, aber geringere Einheitlichkeit zwischen Appendix-Templates
  - Option C: Schnellster Patch, wenn klarer Tippfehler; benoetigt Bestaetigung der Zielbenennung

- Auszufuellen:
  - Gewaehlte Option: Option A (Benutzerentscheidung eingegangen)
  - Finale Benennung (falls relevant): `CmdVelNavTopic` = `/nav2/cmd_vel`
  - Patch-Hinweis (konkrete Textstelle): Makroblock am Dokumentanfang erweitern; Appendix `nav2_params.yaml` Eintrag `cmd_vel_in_topic` auf neues Makro referenziert lassen
  - Dokument-Patch-Status: erledigt in `docs/Projektarbeit_dokument_002`; Repo-Spiegelung/Appendix-Extrakt separat prüfen

## Q002 Template - Finale Runtime-Topic-/Frame-Namen

- Frage-ID: `Q002`
- Ziel der Entscheidung: Platzhalter aus Dokument 002 in eine konsistente erste Runtime-Benennung ueberfuehren.
- Betroffene Dokumentstellen (voraussichtlich):
  - Runtime-Contract-Makros am Dokumentanfang
  - `Pakete & Schnittstellen` / `Schnittstellen-Contracts`
  - Appendix-YAMLs (`nav2_params.yaml`, `rtabmap_params.yaml`, `realsense.yaml`)

- Optionen (Vorschlagsstruktur, nicht verbindlich):
  - Option A: Dokumentweit feste Topic-Namen jetzt definieren (Baseline fuer reale Bringups)
  - Option B: Platzhalter im Haupttext behalten, aber ein separates Tabellen-Appendix mit konkreter Baseline-Benennung hinzufuegen
  - Option C: Hybrid: nur kritische Topics jetzt festlegen (`odom`, `cmd_vel`, Kamera, LiDAR), Rest weiter offen lassen

- Konsequenzen:
  - Option A: Schnellere Implementierbarkeit/Bringup, aber hoehere Aenderungskosten bei Hardware-/Treiberwechsel
  - Option B: Haupttext bleibt generisch, aber mehr Pflegeaufwand zwischen Tabelle und Appendix-Dateien
  - Option C: Gute Balance fuer Phase 1/2, jedoch weiterhin partielle Platzhalter in Teilen des Systems

- Minimale Liste zum Ausfuellen (mindestens):
  - Gewaehlte Option: Option C (Benutzerentscheidung eingegangen)
  - `ODOM_TOPIC` = `/odom`
  - `CMD_VEL_TOPIC` = `/cmd_vel` (Twist-Mux Ausgang; einziges finales Base-Motion-Topic)
  - `CMD_VEL_NAV_TOPIC` = `/nav2/cmd_vel` (zusaetzlich fuer Nav2-vor-Mux Pfad / Q001-Q005)
  - `LIDAR_CLOUD_TOPIC` = `/lidar/points`
  - `RGB_TOPIC` = `/camera/color/image_raw`
  - `DEPTH_TOPIC` = `/camera/aligned_depth_to_color/image_raw`
  - `CAMERA_INFO_TOPIC` = `/camera/color/camera_info`
  - `IMU_TOPIC` = `""` (D415-Baseline ohne IMU; optional/nicht verwendet)
  - Abweichende Frame-Namen geg. Dokument-Defaults? Nein (Dokument-Defaults bleiben)
  - Zusatzhinweis fuer Dokumentpatch: RealSense-Treiber kann zusaetzliche optical frames publizieren (z. B. `camera_color_optical_frame`); Nutzung nur via sauberem URDF/TF-Referenzieren
  - Dokument-Patch-Status: erledigt in `docs/Projektarbeit_dokument_002`; `contracts.yaml`/Appendix-Extrakte spiegeln

## Q003 Template - Message-/Action-Spezifikationen (Custom Interfaces)

- Frage-ID: `Q003`
- Ziel der Entscheidung: Custom-Interfaces konkretisieren oder bewusst reduzieren.
- Betroffene Dokumentstellen (voraussichtlich):
  - Kapitel `Message-& Service-Spezifikationen`
  - Kapitel `Objekt-Tracking & Prädiktion`
  - Kapitel `Orchestrierung & Zustandslogik`
  - Kapitel `Manipulation & Handover`

- Optionen (Vorschlagsstruktur, nicht verbindlich):
  - Option A: Vollstaendige Custom-Msg/Action-Spezifikation jetzt im Dokument nachziehen
  - Option B: Minimal-Set an Custom-Msgs spezifizieren, Rest auf Standardtypen belassen
  - Option C: Vorlaeufig nur Topic-Semantik dokumentieren, Msg/Action-Felder spaeter (nicht empfohlen fuer Implementierungsfreigabe)

- Konsequenzen:
  - Option A: Hohe Klarheit fuer Implementierung, mehr initialer Dokumentaufwand
  - Option B: Schneller Fortschritt fuer Phase 2, aber spaetere Erweiterung muss sauber versioniert werden
  - Option C: Hohe Spekulationsgefahr bei Implementierung und potenzielle Rework-Kosten

- Auszufuellen (pro Interface):
  - Gewaehlte Option: Option B (Benutzerentscheidung eingegangen)
  - Verbindliches Minimal-Set Custom Msgs: `Detection3D`, `Detection3DArray`, `ObjectState`, `ThrowStatus`, `PredictedRegion` (empfohlen: ja), `InterceptGoal` (empfohlen: ja fuer klare Semantik)
  - Standardtypen vorerst bevorzugt fuer einfache Ziele: `geometry_msgs/PoseStamped`, bei Unsicherheitskontext `geometry_msgs/PoseWithCovarianceStamped`
  - `std_msgs/String` nicht fuer zentrale Steuer-/Statuspfade (nur Debug/temporar)
  - Pflicht-Interfaces fuer Implementierbarkeit: `PickObject.action`, `ReleaseObject.srv`
  - Interface-Freeze-Regel (empfohlen): Dokumentmarkierung als `Baseline v002-patchX (draft/frozen)`; keine stillen Feldaenderungen im Repo ohne Doku-Update
  - Dokument-Patch-Status: teilweise erledigt (Minimal-Set + `PredictedRegion`/`InterceptGoal` + `PickObject`/`ReleaseObject` textuell gepatcht)
  - Noch nachzuziehen im Dokument: vollstaendige IDL-Listings/Dateisignaturen (optional/empfohlen), Status von `BallState`/`Trajectory` in v002-patchX final klären

## Q004 Template - OBSERVE_HAND Yaw-Align (Nav2-Goal-Updates vs. Controller)

- Frage-ID: `Q004`
- Ziel der Entscheidung: OBSERVE_HAND Verhalten konsistent machen.
- Betroffene Dokumentstellen (voraussichtlich):
  - `Orchestrierung & Zustandslogik` -> state-spezifische Notes (`OBSERVE_HAND`)
  - `Pipeline je Missionsschritt` -> `OBSERVE_HAND`

- Optionen (Vorschlagsstruktur, nicht verbindlich):
  - Option A: Nur Nav2-kompatibles Goal-Streaming / kleine Pose-Updates (kein separater Controller)
  - Option B: Eigener lokaler Yaw-Align-Controller (mit explizitem Ownership-/Mux-Contract)
  - Option C: Zwei Modi dokumentieren (Baseline A, optional B), mit klaren Aktivierungsbedingungen

- Konsequenzen:
  - Option A: Konsistent mit dokumentierter Baseline `cmd_vel`-Ownership, weniger Parallelitaetsrisiko
  - Option B: Hoehere Reaktivitaet moeglich, aber neue Safety-/Arbitration-Spezifikation zwingend
  - Option C: Flexibel, aber Dokument wird komplexer und benoetigt klare Guardrails

- Auszufuellen:
  - Gewaehlte Option: Option C (Benutzerentscheidung eingegangen)
  - Baseline (verbindlich): Yaw-Align in `OBSERVE_HAND` via Nav2-kompatible Goal-/Pose-Updates; kein direkter lokaler Controller auf `/cmd_vel`
  - Follow bleibt Nav2-basiertes Goal-Streaming (kein eigener Follow-Controller)
  - Optionaler lokaler Yaw-Controller ist zulaessig, aber nur via Mux-Quelle `/tracking/yaw_cmd_vel` (niemals direkt `/cmd_vel`)
  - Aktivierungsbedingungen (verbindlich): nur `OBSERVE_HAND`, optional `TRACK_THROWN` (wenn dokumentiert); Target valide; Teleop nicht aktiv; Safety frei; `|yaw_error|` ueber Schwellwert; nur Rotation (`angular.z`), keine Translation
  - Ownership/Mux: Prioritaet unter Teleop, ueber Nav2 (siehe Q005)
  - Disable-Regel: bei Tracking stale/lost (`T_track_stale`, z. B. 300 ms) Quelle deaktivieren, Stop auf Quelltopic, Rueckfall auf Baseline-Verhalten
  - Updatebedarf in Ownership-Abschnitt: Ja (Mux-/Prioritaetsbezug explizit verlinken)
  - Parameter-Baseline (zusätzlich festgezogen): `tracking_yaw_enable=false`, `tracking_yaw_allowed_states=[OBSERVE_HAND]`, `tracking_yaw_error_threshold_deg=5.0`,
    `tracking_target_stale_timeout_ms=300`, `tracking_yaw_max_ang_z_rad_s=0.5`, `tracking_yaw_cmd_timeout_ms=200`, `tracking_yaw_only_rotation=true`
  - Dokument-Patch-Status: erledigt in `docs/Projektarbeit_dokument_002` (Notes + Pipeline-Abschnitt)

## Q005 Template - `cmd_vel` Ownership (inkl. Teleop/Twist-Mux)

- Frage-ID: `Q005`
- Ziel der Entscheidung: Verbindlichen Ownership-Contract fuer Base-Motion festlegen.
- Betroffene Dokumentstellen (voraussichtlich):
  - `Systemarchitektur` (Datenfluesse / Navigation-Interfaces)
  - `Orchestrierung & Zustandslogik` -> `cmd_vel Ownership und Safety Gate (verbindlich)`
  - Sicherheitskapitel (falls Prioritaeten/Safety-Gate erweitert werden)

- Optionen (Vorschlagsstruktur, nicht verbindlich):
  - Option A: Baseline beibehalten (`/cmd_vel` nur Nav2 / Single Writer)
  - Option B: Twist-Mux/Arbitrator einfuehren, aber `/cmd_vel` weiterhin Single Writer am Ausgang des Mux
  - Option C: Mehrere direkte Writer auf `/cmd_vel` zulassen (nicht empfohlen)

- Konsequenzen:
  - Option A: Einfachster und sicherster Contract, aber Teleop-/Override-Pfade muessen anders integriert werden
  - Option B: Flexibler Betrieb (Teleop/Recovery/Tests), aber Prioritaeten, Safety-Gate und Quellen muessen exakt spezifiziert werden
  - Option C: Hohe Kollisions-/Sicherheitsgefahr, widerspricht bisheriger Dokumentrichtung

- Auszufuellen (Minimum):
  - Gewaehlte Option: Option B (Benutzerentscheidung eingegangen)
  - Single-Writer-Regel: Nur Twist-Mux publiziert auf `/cmd_vel`; keine andere Komponente direkt auf `/cmd_vel`
  - Erlaubte Motion-Quellen: `/teleop/cmd_vel`, `/nav2/cmd_vel`, optional `/tracking/yaw_cmd_vel` (standardmaessig deaktiviert)
  - Nicht erlaubte direkte Quellen auf `/cmd_vel`: Perception, Tracking (ausser optionaler Yaw-Pfad via Mux), Follow-Node, MoveIt/Manipulation, Debug-/Testscripte (ohne expliziten Mux-Testpfad)
  - Prioritaetsreihenfolge: Safety/E-Stop Gate (wirkt quellenunabhaengig) > Teleop > TrackingYaw (optional) > Nav2
  - Fallback ohne TrackingYaw-Implementierung: Teleop > Nav2
  - Teleop-Timeout: `1000 ms`
  - Teleop-Timeout Verhalten: Stop-Twist `(0,0,0)` am Mux-Ausgang; Rueckgabe an normale Quellen; keine automatische Missionsfortsetzung ohne Orchestrator-Regel/neues Kommando
  - Orchestrator-Reaktion (verbindliche Baseline): Event `MANUAL_OVERRIDE_ACTIVE`; Zustand `INTERRUPTED` (nicht resume-by-default); laufende Nav2-Action canceln oder als unterbrochen markieren
  - Nach Teleop-Timeout: Zustand bleibt unterbrochen bis explizites `resume` oder neues Sprachkommando
  - Safety-Gate-Position (vor/nach Mux): logisch vor bzw. integriert in den effektiven Bewegungsausgangspfad; muss jede Quelle blockieren koennen
  - Logging/Diagnose-Anforderung (Minimum): aktive Quelle, Quellenwechsel, Timeout-Ereignisse, Safety-Block aktiv/inaktiv
  - Dokument-Patch-Status: Kerncontract in `docs/Projektarbeit_dokument_002` gepatcht; vollständige Tabellen/BT-Ausrollung weiter prüfen

## Q006 Template - Manipulationsschnittstellen / Greifstrategie / Handover

- Frage-ID: `Q006`
- Ziel der Entscheidung: `PICK`/`HANDOVER_RELEASE` fachlich und schnittstellenseitig implementierbar machen.
- Betroffene Dokumentstellen (voraussichtlich):
  - Kapitel `Manipulation & Handover`
  - Kapitel `Orchestrierung & Zustandslogik` (Transitions/State Actions fuer `PICK`, `HANDOVER_RELEASE`)
  - Kapitel `Message-& Service-Spezifikationen`

- Optionen (Vorschlagsstruktur, nicht verbindlich):
  - Option A: Pick/Release als Actions spezifizieren (inkl. Feedback/Result)
  - Option B: Pick als Action, Release als Service (nah an aktuellem Dokumenthinweis)
  - Option C: Vorlaeufig nur High-Level Endpoints benennen, Detailsemantik spaeter (nur fuer sehr fruehe Stub-Phasen)

- Konsequenzen:
  - Option A: Einheitliches Muster fuer Orchestrator, aber groesserer Spezifikationsaufwand
  - Option B: Pragmatich fuer einfaches Release, aber gemischtes Interface-Modell im Orchestrator
  - Option C: Schnell fuer Platzhalter, blockiert belastbare Orchestrator-/Retry-/Timeout-Logik

- Auszufuellen (Minimum):
  - Gewaehlte Option: Option B (Benutzerentscheidung eingegangen)
  - Pick Interface-Typ: `PickObject.action`
  - Release Interface-Typ: `ReleaseObject.srv`
  - `PickObject.action` Goal (Minimum): `std_msgs/Header header`, `geometry_msgs/PoseStamped target_pose`, `uint32 object_class_id` (optional, empfohlen; `0=unknown`), `float32 position_tolerance_m`, `float32 orientation_tolerance_rad`, `bool allow_replan`
  - Wichtige Regel fuer Dokumenttext: Base-Repositioning ist nicht Teil von `PickObject`; bei Unerreichbarkeit Fehlercode `OUT_OF_REACH`, Orchestrator entscheidet Nav2-Umstellen + Retry
  - `PickObject.action` Result (Minimum): `bool success`, `uint16 result_code`, `string message`, optional `geometry_msgs/PoseStamped grasp_pose_used`
  - `PickObject.action` Result-Codes (Minimum): `SUCCESS`, `NO_TARGET`, `TARGET_STALE`, `OUT_OF_REACH`, `PLAN_FAILED`, `EXECUTION_FAILED`, `GRASP_FAILED`, `TIMEOUT`, `SAFETY_ABORT`
  - `PickObject.action` Feedback (Minimum): `uint8 stage`, `string stage_text`; empfohlene Stages `VALIDATE_TARGET`, `PLAN_APPROACH`, `EXECUTE_APPROACH`, `CLOSE_GRIPPER`, `VERIFY_GRASP`, `DONE`, `FAILED`
  - `ReleaseObject.srv` Request (Minimum): `uint8 release_mode`, optional `bool verify_open`
  - `ReleaseObject.srv` release_mode (empfohlen): `OPEN_GRIPPER`, `DROP_SAFE`, `HANDOVER_RELEASE`
  - `ReleaseObject.srv` Response (Minimum): `bool success`, `uint16 result_code`, `string message`
  - `ReleaseObject.srv` Result-Codes (Minimum): `SUCCESS`, `NOT_HOLDING_OBJECT`, `ACTUATION_FAILED`, `TIMEOUT`, `SAFETY_ABORT`
  - Retry-/Timeout-Regeln (Baseline): Pick-Timeout dokumentieren (z. B. `10-20 s`, spaeter messbasiert); Pick-Retry-Budget im Orchestrator (nicht im Action-Server verstecken); Release-Timeout kurz (z. B. `2-5 s`); Fehler transparent codieren, Recovery-Entscheidung im Orchestrator
  - Festgezogene Defaults: `pick_timeout_s=15.0`, `release_timeout_s=3.0`; Pick- und Release-Result-Codes numerisch definiert (siehe Dokument-Patch)
  - Dokument-Patch-Status: textuelle Semantik in `docs/Projektarbeit_dokument_002` gepatcht; vollständige IDL-Listings optional noch offen
