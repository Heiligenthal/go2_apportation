# TECH_FREEZE_LOG.md

Quelle:
- fachlich verbindlich: `docs/Projektarbeit_dokument_002`
- technischer Ist-Stand: Repo-Audit vom 2026-03-13

## Phase 1 - Shared Surface Audit + minimaler Freeze

Scope dieser Runde:
- `src/go2_apportation_msgs/`
- `config/contracts.yaml`
- `src/go2_apportation_orchestrator/`
- orchestratornahe Tests

Wichtig:
- Dieses Log ist ein Audit-/Freeze-Artefakt.
- Es fuehrt keine neue fachliche Quelle ein.
- Neue Vorschlaege sind klar getrennt markiert.

## A. Aus Dokument 002 ableitbare Freeze-Kandidaten

Diese Punkte koennen auf Basis von Dokument 002 und dem aktuellen Repo bereits als kleinster gemeinsamer Shared Surface gelten:

- Zustandsnamen des Missionsflusses:
  - `IDLE`
  - `SEARCH_PERSON`
  - `APPROACH_PERSON`
  - `OBSERVE_HAND`
  - `TRACK_THROWN`
  - `SEARCH_OBJECT_LOCAL`
  - `SEARCH_OBJECT_GLOBAL`
  - `INTERCEPT`
  - `PICK`
  - `RETURN_TO_PERSON`
  - `HOLD_AND_FOLLOW`
  - `HANDOVER_RELEASE`
  - `INTERRUPTED`
  - `FAILSAFE_ABORT`
- Kern-Eventnamen des Orchestrators aus `transition_spec.py`:
  - Voice: `vc_lets_play`, `vc_search`, `vc_release`, `vc_abort`, `vc_pause`, `vc_resume`
  - Perception/Nav/Manipulation/Safety: `person_detected`, `person_lost`, `object_detected`, `object_lost`, `throw_suspected`, `throw_confirmed`, `approach_reached`, `intercept_reached`, `nav_failed`, `object_unreachable`, `grasp_ok`, `grasp_failed`, `object_dropped`, `e_stop`, `timeout`, `localization_lost`, `battery_low`
  - Manual Override: `MANUAL_OVERRIDE_ACTIVE`, `MANUAL_OVERRIDE_RELEASED`
- Bereits real vorhandene IDL-Dateien:
  - `Detection3D.msg`
  - `Detection3DArray.msg`
  - `ObjectState.msg`
  - `ThrowStatus.msg`
  - `PickObject.action`
  - `ReleaseObject.srv`
- Bereits gespiegelt in `config/contracts.yaml`:
  - Frames `map`, `odom`, `base_link`, `camera_link`, `lidar_frame`, `imu_link`
  - Basis-Topics `/odom`, `/cmd_vel`, `/nav2/cmd_vel`, Kamera-/LiDAR-Basistopics
- Bereits minimal verdrahtete Orchestrator-Endpunkte:
  - `/navigate_to_pose`
  - `/manipulation/pick`
  - `/manipulation/release`

## B. Aus Dokument 002 ableitbare, aber noch nicht freeze-reife Punkte

- `PredictedRegion.msg` fehlt als echte ROS-Message.
- `InterceptGoal.msg` fehlt als echte ROS-Message.
- Der dokumentierte missionsweite Shared Surface ist nicht als technischer Mirror komplett erfasst:
  - `/voice/command`
  - `/perception/person_*`
  - `/perception/object_*`
  - `/tracking/*`
  - `/follow_waypoints`
- Pick-/Release-Result-Codes sind textlich dokumentiert, aber noch nicht als maschinenlesbare Konstanten oder Orchestrator-Auswertung gespiegelt.
- Person-, Tracking- und Object-Perception sind im Repo fuer den Shared Surface weitgehend nur dokumentiert, nicht technisch angebunden.

## C. Schrittweiser Audit-Befund fuer die angefragten Missionsschritte

- `SEARCH_PERSON`
  - Freeze-Status: teilfreeze-faehig
  - Begruendung: State/Event/Transition vorhanden; Person-Topics nur dokumentiert, nicht verdrahtet.
- `OBSERVE_HAND`
  - Freeze-Status: teilfreeze-faehig
  - Begruendung: State/Event/Transition vorhanden; Hand-/Objekt-Wahrnehmung noch ohne technischen Surface.
- `TRACK_THROWN`
  - Freeze-Status: nicht freeze-reif
  - Begruendung: ohne `PredictedRegion.msg` und `InterceptGoal.msg` ist der dokumentierte Shared Surface unvollstaendig.
- `SEARCH_OBJECT_LOCAL`
  - Freeze-Status: teilfreeze-faehig
  - Begruendung: State/Transition vorhanden; benoetigte Objekt-Topics nur dokumentiert.
- `SEARCH_OBJECT_GLOBAL`
  - Freeze-Status: teilfreeze-faehig
  - Begruendung: State/Transition vorhanden; `/follow_waypoints` nicht als Skill-/Client-Surface ausgepraegt.
- `INTERCEPT`
  - Freeze-Status: nicht freeze-reif
  - Begruendung: Schritt verweist fachlich auf `intercept_goal`, aber dazu fehlt der konkrete Msg-Contract.
- `PICK`
  - Freeze-Status: freeze-faehig als Minimal-Interface
  - Begruendung: `PickObject.action` existiert bereits.
- `RETURN_TO_PERSON`
  - Freeze-Status: teilfreeze-faehig
  - Begruendung: State/Transition vorhanden; `person_pose`-Zulieferung fehlt als technischer Anschluss.
- `HOLD_AND_FOLLOW`
  - Freeze-Status: teilfreeze-faehig
  - Begruendung: Semantik als Nav2 Goal Streaming ist dokumentiert, aber noch nicht als eigener technischer Surface konkretisiert.

## D. Minimale Freeze-Entscheidungen fuer diese Runde

Jetzt stabil haltbar:
- State- und Event-Namen aus dem dokumentnahen Runtime-Kern
- bereits vorhandene Minimal-Interfaces `Detection3D`, `Detection3DArray`, `ObjectState`, `ThrowStatus`, `PickObject`, `ReleaseObject`
- Basis-Frames und Basis-Nav2-/Sensor-Topics aus `config/contracts.yaml`
- Verbot direkter `cmd_vel`-Steuerung aus Perception/Tracking/Manipulation/Follow ausserhalb des dokumentierten Mux-/Nav2-Contracts

Offen lassen:
- komplette Tracking-Shared-Surface-Freeze ohne `PredictedRegion.msg` und `InterceptGoal.msg`
- technische Auspraegung von Follow ueber `/follow_waypoints` versus reines `navigate_to_pose` Goal Streaming
- konkrete Verdrahtung der globalen `/perception/*`- und `/tracking/*`-Topics in produktive Nodes

Neutraler Stub/Interface reicht vorerst:
- BT-Datei bleibt Stub
- dokumentnahe Transition-Spiegel bleiben statisch
- Skill-Clients fuer Pick/Release/Nav2 duerfen minimal bleiben, solange keine neue Fachlogik behauptet wird

## E. Neu vorgeschlagen / nicht aus Dokument 002

Nur als unverbindlicher Minimalvorschlag fuer die naechste Freeze-Stufe:
- Wenn vor Phase 2 genau eine technische Shared-Surface-Luecke geschlossen werden soll, dann zuerst `PredictedRegion.msg` und `InterceptGoal.msg`, weil damit `TRACK_THROWN` und `INTERCEPT` erstmals sauber auf Wire-Level repräsentierbar werden.

## Phase 2 - Orchestrator Audit (2026-03-13)

### Dokumentnaher Runtime-Kern

Als paketgetragener Hauptpfad erkennbar:
- `transition_spec.py`
- `transition_context.py`
- `transition_resolver.py`
- `transition_engine_pure.py`
- `orchestrator_runtime_core.py`
- `orchestrator_runtime_node.py`
- `action_token_dispatcher.py`
- `skills/*` ausser `real_backend_placeholder.py`

Begruendung:
- dieser Pfad bildet die Dokument-002-States/Ereignisse weitgehend ab
- dieser Pfad wird durch die vorhandenen orchestratornahen Tests direkt getragen
- dieser Pfad bietet die realen Adapterpunkte fuer `/navigate_to_pose`, `/manipulation/pick`, `/manipulation/release`

### Legacy-/Stub-nahe Pfade

- `state_contracts.py`
- `orchestrator_node.py`
- `behavior_trees/mission_flow_stub.xml`

Beobachtung:
- kein eigener Testpfad stuetzt diese Dateien direkt
- der inhaltliche Umfang ist kleiner als im Runtime-Kern
- sie dienen aktuell eher als Alt-Stubs bzw. Reservierungsartefakte

### Minimale Freeze-Kandidaten aus dem Orchestrator-Audit

State-Namen:
- `IDLE`
- `SEARCH_PERSON`
- `APPROACH_PERSON`
- `OBSERVE_HAND`
- `TRACK_THROWN`
- `SEARCH_OBJECT_LOCAL`
- `SEARCH_OBJECT_GLOBAL`
- `INTERCEPT`
- `PICK`
- `RETURN_TO_PERSON`
- `HOLD_AND_FOLLOW`
- `HANDOVER_RELEASE`
- `INTERRUPTED`
- `FAILSAFE_ABORT`

Event-Namen:
- `vc_lets_play`
- `vc_search`
- `vc_release`
- `vc_abort`
- `vc_pause`
- `vc_resume`
- `person_detected`
- `person_lost`
- `object_detected`
- `object_lost`
- `throw_suspected`
- `throw_confirmed`
- `approach_reached`
- `intercept_reached`
- `nav_failed`
- `object_unreachable`
- `grasp_ok`
- `grasp_failed`
- `object_dropped`
- `e_stop`
- `timeout`
- `localization_lost`
- `battery_low`
- `MANUAL_OVERRIDE_ACTIVE`
- `MANUAL_OVERRIDE_RELEASED`

### Noch nicht freeze-reif im Orchestrator

- `SEARCH_OBJECT_GLOBAL` als echter Waypoint-/`/follow_waypoints`-Pfad
- `HOLD_AND_FOLLOW` als echter Goal-Streaming-Adapterpunkt
- Person-/Object-/Tracking-Topic-Anbindung an den Runtime-Node
- Auswertung fachlicher Pick-/Release-Result-Codes im Orchestrator
- Vereinheitlichung oder explizite Bereinigung des alten Stub-Pfads

## Phase 2.1 - Kleiner Shared-Surface-Freeze fuer Person-Perception und MoveIt-nahe Missionsauswertung (2026-03-13)

### Aus Dokument 002 / Projektkontext ableitbar

Person-Perception:
- `/perception/person_visible` ist als `std_msgs/Bool` dokumentiert.
- `/perception/person_pose` ist als `geometry_msgs/PoseStamped` dokumentiert.
- `/perception/person_pose` ist im Frame `map` gedacht.
- `RETURN_TO_PERSON` und `HOLD_AND_FOLLOW` arbeiten fachlich auf Basis einer Personenpose und Nav2.

Follow / Return-to-Person:
- Follow bleibt dokumentnah Nav2-Goal-Streaming.
- Kein eigener Follow-Controller.
- Kein direkter `cmd_vel`-Pfad.
- `navigate_to_pose` ist bereits real im Orchestratorpfad erkennbar.

Manipulation / Wire-Level:
- `PickObject.action` bleibt die Pick-Schnittstelle.
- `ReleaseObject.srv` bleibt die Release-Schnittstelle.
- `ReleaseObject.srv` verwendet wire-level Moden `OPEN_GRIPPER`, `DROP_SAFE`, `HANDOVER_RELEASE`.
- `result_code` bleibt auf Wire-Level mode-agnostisch.

### Neu vorgeschlagen / nicht aus Dokument 002, aber fuer diesen Freeze verbindlich gesetzt

Person-Perception Minimal-Freeze:
- `/perception/person_last_seen` wird fuer diesen Freeze als `geometry_msgs/PoseStamped` festgehalten.
- `frame_id` fuer `/perception/person_last_seen` ist `map`.
- Es wird vorerst keine neue Custom-Msg fuer Person-Perception eingefroren.

Navigation Shared Surface:
- Fuer den aktuellen Minimal-Freeze ist ausschliesslich `/navigate_to_pose` der verbindliche Nav-Surface.
- `/follow_waypoints` ist vorerst nicht Teil des verpflichtenden Shared Surface.

PickObject Benennungsklarstellung:
- Die normativen Wire-/Runtime-Werte sind die `PickObject.result_code`-Konstanten:
  - `PICK_SUCCESS`
  - `PICK_FAILED`
  - `OBJECT_DROPPED`
  - `PICK_UNREACHABLE`
  - `PICK_TIMEOUT`
  - `SAFETY_ABORTED`
- Der Orchestrator leitet daraus die fachlichen Events ab:
  - `PICK_SUCCESS` -> `grasp_ok`
  - `PICK_FAILED` -> `grasp_failed`
  - `OBJECT_DROPPED` -> `object_dropped`
  - `PICK_UNREACHABLE` -> `object_unreachable`
  - `PICK_TIMEOUT` -> `timeout`
  - `SAFETY_ABORTED` -> `safety_abort`
- Klarstellung zum Ist-Stand:
  - die Trennung `result_code` versus fachliches Event ist fuer den Freeze normativ
  - im aktuellen Runtime-Kern sind `grasp_ok`, `grasp_failed`, `object_dropped`, `object_unreachable`, `timeout` bereits als Eventnamen vorhanden
  - `safety_abort` ist damit fuer diese Pick-Auswertung benannt, aber im aktuellen Runtime-Kern noch nicht als eigener Eventname gespiegelt

Release-Missionsauswertung:
- `HANDOVER_RELEASE` + Erfolg -> `HANDOVER_RELEASE_SUCCESS`
- `DROP_SAFE` + Erfolg -> missionsseitig `DROP_RELEASE_SUCCESS`
- jeder Modus + Timeout -> `RELEASE_TIMEOUT`
- jeder Modus + Safety-Abbruch -> `SAFETY_ABORTED`
- jeder Modus + generischer Fehlschlag -> `RELEASE_FAILED`

### Begruendung fuer bewusst kleinen Shared Surface

Warum `/follow_waypoints` vorerst nicht verpflichtend ist:
- Dokument 002 kennt zwar `/follow_waypoints`, aber der aktuelle paketgetragene Orchestratorpfad hat real nur `/navigate_to_pose`.
- Der Freeze soll entblocken, nicht einen zweiten Nav-Surface spekulativ erzwingen.
- Follow bleibt weiterhin dokumentnah als rate-limitiertes Goal-Streaming ueber Nav2 gedacht.

Warum Manipulationsposturen lokal bleiben:
- `safe`, `carry`, `offer`, `pregrasp` sind im Dokument 002 keine eingefrorenen globalen Shared-Surface-Begriffe.
- Sie betreffen die lokale Manipulationsruntime und sollen aktuell keinen globalen Orchestrator-/Wire-Contract vergroessern.

### Mirror-Status

Technisch gespiegelt in `config/contracts.yaml`:
- `/perception/person_visible`
- `/perception/person_pose`
- `/perception/person_last_seen`
- Notiz: `person_pose` und `person_last_seen` sind `map`-gefuehrt

Nur dokumentiert, nicht technisch gespiegelt:
- Pick-Wire-Codes und daraus abgeleitete Orchestrator-Events
- Release-Missionsereignisse (`RELEASE_FAILED`, usw.)
- Reduktion des verpflichtenden Nav-Surface auf `/navigate_to_pose`
- Ausschluss von `/follow_waypoints` aus dem aktuellen Pflicht-Surface
- Lokalitaet der Manipulationsposturen

## Phase 2.2 - Kleiner Shared-Surface-Freeze fuer Wuerfel-/Tracking-Minimum (2026-03-14)

### Aus Dokument 002 / Projektstand ableitbar

Objekt- und Tracking-Surface:
- `/perception/object_visible` ist als `std_msgs/Bool` dokumentiert.
- `/perception/object_pose_6d` ist als `geometry_msgs/PoseStamped` oder `PoseWithCovarianceStamped` dokumentiert.
- `/perception/object_last_seen` ist als Pose + Timestamp dokumentiert.
- `/tracking/detections3d_fast` ist als `Detection3DArray` oder funktional aequivalentes eigenes Msg dokumentiert.
- Tracking-relevante Outputs `/tracking/*` sind in Dokument 002 `odom`-gefuehrt.
- Dokument 002 beschreibt Tracking/Prediction als Zustands-/Praediktionssurface, nicht als Motion-/`cmd_vel`-Pfad.
- `PredictedRegion.msg` und `InterceptGoal.msg` werden in Dokument 002 textlich beschrieben, sind im Repo aber noch nicht als echte Shared-Surface-Dateien vorhanden.

### Neu vorgeschlagen / nicht direkt aus Dokument 002, aber fuer diesen Freeze verbindlich gesetzt

Wuerfel-/Tracking-Minimal-Freeze:
- `/perception/object_pose_6d` wird als oeffentlicher Shared Surface auf `geometry_msgs/PoseStamped` eingegrenzt.
- Fuer `/perception/object_pose_6d` besteht keine Covariance-Pflicht im Shared Surface.
- Semantik von `/perception/object_pose_6d`: symmetriekanonisierte greifrelevante Pose.
- Fuer den Wuerfel gilt eine 180-Grad-aequivalente Kantenorientierung fuer Greifzwecke als derselbe Zustand.
- `/perception/object_last_seen` wird fuer diesen Freeze als `geometry_msgs/PoseStamped` festgehalten.
- `/perception/object_last_seen` fuehrt Pose + Timestamp ueber `PoseStamped`.
- Ziel-Frame fuer `/perception/object_last_seen` ist fuer diesen Freeze `map`.
- Fuer `/perception/object_last_seen` besteht keine Covariance-Pflicht im Shared Surface.
- `/tracking/detections3d_fast` wird als oeffentlicher Wire-Contract auf `go2_apportation_msgs/Detection3DArray` festgelegt.
- Funktional aequivalente interne Repräsentationen bleiben nur hinter Adaptern zulaessig, nicht als oeffentlicher Contract.
- FAST-/tracking-relevante Outputs bleiben `odom`-gefuehrt.
- PRECISE-/pick-relevante Pose muss ein gueltiges `frame_id` tragen und sauber per TF nach `odom`/`map` transformierbar sein.
- Tracking/Prediction publiziert keine Motion, sondern nur Zustand/Praediktion.

### Fehlende Shared-Surface-Punkte als CR / Arbeitspaket

Zum Stand dieser Runde verbleiben hier keine offenen Msg-Arbeitspakete mehr fuer `PredictedRegion` und `InterceptGoal`.
Die technische Nachziehung erfolgt in Phase 2.4 unten.

### Mirror-Status

Technisch gespiegelt in `config/contracts.yaml`:
- `/perception/object_visible`
- `/perception/object_pose_6d`
- `/perception/object_last_seen`
- `/tracking/detections3d_fast`

Nur dokumentiert, nicht technisch gespiegelt:
- Typbindung `/perception/object_pose_6d -> geometry_msgs/PoseStamped`
- Typbindung `/perception/object_last_seen -> geometry_msgs/PoseStamped`
- Symmetrie-Semantik fuer den Wuerfel
- Frame-/Transformationsregeln FAST vs. PRECISE
- spaetere Tracking-/Intercept-Logik oberhalb der Msg-/Topic-Surface

### Offene Harmonisierung

- Dokument 002 beschreibt `/perception/object_last_seen` derzeit als `odom`-gefuehrt.
- Der abgestimmte Freeze dieser Runde setzt `/perception/object_last_seen` auf `map`.
- Diese Abweichung wird bewusst dokumentiert und nicht stillschweigend als bereits dokumentkonform ausgegeben.

## Phase 2.3 - Kleiner Shared-Surface-Freeze fuer `/tracking/object_state` und `/tracking/throw_status` (2026-03-14)

### Aus Dokument 002 / Projektstand ableitbar

- `/tracking/object_state` ist als eigener Msg-Contract fuer Pose, Velocity und Covariance beschrieben.
- `/tracking/object_state` ist `odom`-gefuehrt und dient Tracking, Praediktion und ETA.
- `/tracking/throw_status` ist als grober Wurf-/Freigabe-Lebenszyklus beschrieben.
- Dokument 002 nennt fuer `/tracking/throw_status` die oeffentlichen Zustaende:
  - `IDLE`
  - `HELD`
  - `RELEASE_SUSPECTED`
  - `THROWN`
  - `LANDED`
  - `LOST`
- Tracking-Surface bleibt zustands-/praediktionsorientiert und enthaelt keine Motion-/`cmd_vel`-Semantik.

### Jetzt projektweit eingefroren

- Oeffentlicher Wire-Type von `/tracking/object_state` ist `go2_apportation_msgs/ObjectState`.
- Oeffentlicher Wire-Type von `/tracking/throw_status` ist `go2_apportation_msgs/ThrowStatus`.
- Mindestsemantik fuer `/tracking/object_state`:
  - trackingseitiger Objektzustand fuer Praediktion / ETA
  - Kernbedeutung: Pose / Velocity / Covariance
  - `odom`-gefuehrt
  - keine Motion-/`cmd_vel`-Semantik
- Eingefrorene oeffentliche Zustaende fuer `/tracking/throw_status`:
  - `IDLE`
  - `HELD`
  - `RELEASE_SUSPECTED`
  - `THROWN`
  - `LANDED`
  - `LOST`
- Mindestsemantik fuer `/tracking/throw_status`:
  - grober Wurf-/Freigabe-Lebenszyklus
  - keine Motion-Ausgabe

### Kompatibilitaetscheck der bestehenden Msgs

- `ObjectState.msg`: kompatibel mit dem Freeze
  - vorhanden als `std_msgs/Header + geometry_msgs/PoseWithCovariance + geometry_msgs/TwistWithCovariance`
  - `TwistWithCovariance` deckt die benoetigte Velocity-/Covariance-Bedeutung ab
  - keine zusaetzlichen Sichtbarkeits- oder Motion-Felder vorhanden
- `ThrowStatus.msg`: kompatibel mit dem Freeze
  - vorhanden mit genau den oeffentlichen Zustandskonstanten `IDLE`, `HELD`, `RELEASE_SUSPECTED`, `THROWN`, `LANDED`, `LOST`
  - keine zusaetzlichen oeffentlichen Statuswerte vorhanden

### Weiterhin offen / nicht erzwungen

- Sichtbarkeit bleibt primaer auf `/perception/object_visible`; sie wird nicht in `/tracking/object_state` hineingefroren.
- Debounce-/Timing-Heuristiken oder eine komplette interne Track-/Throw-FSM werden nicht eingefroren.
- Zusatzzustaende fuer `/tracking/throw_status` werden nicht erfunden.
- `PredictedRegion.msg`, `InterceptGoal.msg`, `/tracking/predicted_region` und `/tracking/intercept_goal` bleiben separate fehlende Shared-Surface-Arbeitspakete.

### Mirror-Status

Technisch gespiegelt in `config/contracts.yaml`:
- `/tracking/object_state`
- `/tracking/throw_status`

Nur dokumentiert, nicht technisch gespiegelt:
- Minimalsemantik von `ObjectState`
- eingefrorene oeffentliche Zustaende von `ThrowStatus`
- ausdruecklicher Ausschluss von Motion-/`cmd_vel`-Semantik

## Phase 2.4 - Shared-Surface-Freeze fuer `PredictedRegion` und `InterceptGoal` (2026-03-14)

### Aus Dokument 002 / Projektstand ableitbar

- Dokument 002 beschreibt `PredictedRegion.msg` mit:
  - `std_msgs/Header header`
  - `geometry_msgs/Pose center`
  - `geometry_msgs/Vector3 size`
  - `float32 confidence`
  - `builtin_interfaces/Duration valid_for`
- Dokument 002 beschreibt `InterceptGoal.msg` mit:
  - `std_msgs/Header header`
  - `geometry_msgs/PoseStamped target_pose`
  - `float32 approach_radius_m`
  - `float32 goal_tolerance_m`
  - `float32 confidence`
  - `builtin_interfaces/Duration valid_for`
  - `bool is_dynamic_estimate`
- `/tracking/predicted_region` und `/tracking/intercept_goal` sind dokumentierte `odom`-gefuehrte Tracking-Outputs.
- Beide Shared-Surface-Typen sind motion-frei; sie tragen keine `cmd_vel`-, Velocity-, Acceleration- oder Controller-Sollwerte.

### Jetzt projektweit eingefroren

- `src/go2_apportation_msgs/msg/PredictedRegion.msg` ist als oeffentlicher Wire-Type angelegt.
- `src/go2_apportation_msgs/msg/InterceptGoal.msg` ist als oeffentlicher Wire-Type angelegt.
- Topic-Mirror:
  - `/tracking/predicted_region` -> `go2_apportation_msgs/PredictedRegion`
  - `/tracking/intercept_goal` -> `go2_apportation_msgs/InterceptGoal`
- Mindestsemantik `PredictedRegion`:
  - oeffentliche Unsicherheitsregion fuer die vorhergesagte Objektlage
  - `odom`-gefuehrt ueber `header.frame_id`
  - motion-frei
- Mindestsemantik `InterceptGoal`:
  - replannbares Intercept-Ziel fuer Navigation/Orchestrator
  - `odom`-gefuehrt
  - motion-frei
  - kein `cmd_vel`

### Endgueltige Msg-Definitionen

`PredictedRegion.msg`
```text
std_msgs/Header header
geometry_msgs/Pose center
geometry_msgs/Vector3 size
float32 confidence
builtin_interfaces/Duration valid_for
```

`InterceptGoal.msg`
```text
std_msgs/Header header
geometry_msgs/PoseStamped target_pose
float32 approach_radius_m
float32 goal_tolerance_m
float32 confidence
builtin_interfaces/Duration valid_for
bool is_dynamic_estimate
```

### Weiterhin offen / nicht erzwungen

- Mehrhypothesen
- Rohtrajektorien
- Filterinterna
- Debug-/Score-Zusatzdaten
- Kandidatenlisten
- Ranking-/Scoring-Logik
- interne Abfangstrategie
- planner-spezifische Zusatzparameter

## Phase 2.5 - Bridge-nahe Runtime-Contracts und Directive-Freeze (2026-03-18)

### Aus Dokument 002 / Projektstand ableitbar

- Dokument 002 fixiert weiterhin den realen TF-Hauptpfad:
  - `map -> odom -> base_link -> sensor_frames`
- Dokument 002 fuehrt den Orchestrator als zustaendig fuer:
  - State-Wechsel
  - Nav2-Ziele
  - Cancel
  - Pick-Gating
- Dokument 002 haelt fest:
  - Tracking-/Prediction-Surface bleibt motion-frei
  - Look-/Yaw-Regelung darf nicht als direkter `cmd_vel`-Pfad aus Tracking/Perception auf den finalen Bewegungsoutput gehen
  - `ObjectState` bleibt `odom`-gefuehrt

### Expliziter Projekt-Freeze dieser Runde, nicht 1:1 aus Dokument 002

Bridge-/TF-Grundlage:
- zusaetzlicher virtueller Runtime-Integrationsframe:
  - `base_link -> base_link_nav2`
- `base_link_nav2` ist offizieller technischer Runtime-Integrationsframe
- `odom_nav2` ist nicht produktiver Standard, hoechstens legacy/debug

Bridge-nahe technische Runtime-Contracts:
- `/cmd_vel_nav2`
- `/look_yaw_delta`
- `/balance_rpy_cmd`
- `/control_mode_cmd`
- Frame `base_link_nav2`

Tracking-/Intercept-Geometrie:
- `/tracking/predicted_region` ist oeffentlich kanonisch `map`-basiert
- `/tracking/intercept_goal` ist oeffentlich kanonisch `map`-basiert
- `odom` bleibt fuer diese beiden hoechstens intern/lokal ableitbar

Directive-Contract:
- `TrackingDirective.msg` wird als einzelner kompakter diskreter Empfehlungskanal eingefuehrt
- keine Geometrie
- keine Motion-/`cmd_vel`-Semantik
- keine Bool-Topic-Flut

Orchestrator-/Bridge-Semantik:
- Look-Regelung laeuft direkt Perception/Tracking -> Bridge, nicht ueber den Orchestrator
- `SEARCH_OBJECT_LOCAL` bleibt in `velocity_move`
- `INTERCEPT` bleibt in `velocity_move`
- `OBSERVE_HAND` bleibt in `balance_stand`
- `PICK_REACQUIRE` ist als Mapping-Idee dokumentiert, aber kein aktueller Runtime-State
- `ObjectState` wird in diesem Task nicht auf `map` umgefroren

### Technischer Nachzug

Im Msg-Paket:
- `TrackingDirective.msg` neu angelegt

Im Orchestrator:
- neue parsebare Directive-Events vorbereitet:
  - `request_intercept`
  - `request_local_search`
  - `request_global_search`
  - `request_pick_ready`
  - `request_pick_abort`
- neuer kleiner Runtime-Contractpfad dokumentiert in `runtime_contracts.py`
- keine neuen Transitionen
- keine neue Fahrlogik
- keine Bridge-Implementierung

### Endgueltige Definition `TrackingDirective.msg`

```text
std_msgs/Header header
uint8 NONE=0
uint8 REQUEST_INTERCEPT=1
uint8 REQUEST_LOCAL_SEARCH=2
uint8 REQUEST_GLOBAL_SEARCH=3
uint8 REQUEST_PICK_READY=4
uint8 REQUEST_PICK_ABORT=5

uint8 REASON_UNSPECIFIED=0
uint8 TARGET_NOT_CENTERABLE=1
uint8 TARGET_MOVING=2
uint8 TARGET_LOST=3
uint8 TARGET_STABLE=4
uint8 TARGET_NOT_VISIBLE=5
uint8 TARGET_MOVED_DURING_PICK=6

uint8 directive
uint8 reason
builtin_interfaces/Duration valid_for
```

### Weiterhin offen / nicht erzwungen

- Breaking Change an `ObjectState`
- direkte Bridge-Implementierung in diesem Ownership-Bereich
- neue Fahr-/Nav2-Logik
- reiche Heuristikfelder in `TrackingDirective`
- Bool-Ersatztopics fuer dieselbe Directive-Funktion
