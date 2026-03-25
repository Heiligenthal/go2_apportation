# IMPLEMENTATION_STATUS.md

Quelle:
- fachlich: `docs/Projektarbeit_dokument_002`
- technischer Ist-Stand: aktuelle Repo-Dateien (siehe Dateiliste unten)

## Statusuebersicht (Ist-Code)

- Phase: 2.x (Spezifikationsspiegel + deterministischer Runtime-Kern + Board-Minimal R1)
- Laufzeitlogik: teilweise implementiert (Transition-Resolver/Engine + Runtime-Core vorhanden)
- Steuerungslogik/Fahrlogik: keine direkte `cmd_vel`-Runtime-Arbitration im Repo umgesetzt
- Perzeptionslogik: nicht implementiert (keine produktive Person-/Objekt-Perception-Nodes)
- Manipulationslogik: nur Skill-Interfaces/Stubs + Mock-Server
- Orchestrierungslogik: Runtime-Node vorhanden (Event rein, State/Status raus), mit Skill-Dispatch

## Umgesetzt (faktisch im Repo vorhanden)

- Board-Minimal Bringup (R1):
  - `launch/board_minimal.launch.py`
  - `scripts/bringup/run_board_minimal.sh`
  - `src/go2_tf_tools/go2_tf_tools/odom_to_tf_broadcaster.py`
  - Inhaltlich: TF-Adapter fuer `odom->base_link` aus `/utlidar/robot_odom`.

- Orchestrator Runtime-Kern:
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_spec.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_resolver.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_engine_pure.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_context.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/orchestrator_runtime_core.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/orchestrator_runtime_node.py`
  - Inhaltlich: deterministische Auswahl/Anwendung von Transitionen, Guard-Auswertung fuer bekannte Guard-Tokens, Statusausgabe.

- Action-Token-Dispatch + Skills:
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/action_token_dispatcher.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/skill_bundle.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_stub.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_ros_client.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_real_client.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/manipulation_skill_stub.py`
  - `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/manipulation_skill_ros_client.py`
  - Inhaltlich: Dispatch fuer `nav_goal`, `nav_cancel`, `pick`, `pick_cancel`, `release`; Real-Nav2-Client mit Result->Event-Hook.

- Messages/Interfaces:
  - `src/go2_apportation_msgs/msg/Detection3D.msg`
  - `src/go2_apportation_msgs/msg/Detection3DArray.msg`
  - `src/go2_apportation_msgs/msg/ThrowStatus.msg`
  - `src/go2_apportation_msgs/msg/ObjectState.msg`
  - `src/go2_apportation_msgs/action/PickObject.action`
  - `src/go2_apportation_msgs/srv/ReleaseObject.srv`

- Mock-Backend / Demo:
  - `src/go2_apportation_mocks/go2_apportation_mocks/mock_nav2_server.py`
  - `src/go2_apportation_mocks/go2_apportation_mocks/mock_manipulation_server.py`
  - `scripts/run_mock_demo.sh`

- Spezifikations-/Config-Spiegel:
  - `config/contracts.yaml`
  - `config/nav2_params.yaml`
  - `config/rtabmap_params.yaml`
  - `config/realsense.yaml`
  - `launch/bringup_minimal.launch.py`

## Stub-only / bewusst unvollstaendig

- Produktive Nav2/RTAB-Map/MoveIt2 Runtime-Integration ist nicht fertig integriert.
- `launch/bringup_minimal.launch.py` ist weiterhin ein strukturelles Template mit Platzhaltercharakter.
- Mehrere Action-Tokens aus `transition_spec.py` werden derzeit nicht fachlich ausgefuehrt (nur Dispatcher-Stubs/Unhandle-Status).
- Vollstaendige IDL-Reife fuer alle in `OPEN_QUESTIONS.md` genannten Schnittstellen bleibt offen (`Q003`, `Q006`).

## Validierungsstand (technisch)

- Unit-/Komponententests vorhanden:
  - `tests/test_transition_resolver.py`
  - `tests/test_transition_engine_pure.py`
  - `tests/test_orchestrator_runtime_core.py`
  - `tests/test_action_token_dispatcher.py`
  - `tests/test_nav2_skill_real_client.py`
  - `tests/test_odom_to_tf_broadcaster.py`
  - weitere Tests unter `tests/`
- Diese Datei beschreibt den Codebestand; ob Build/Tests in der aktuellen Umgebung erfolgreich liefen, wird jeweils pro Arbeitsrunde separat berichtet.

## Offene Punkte (Status-Artefakt-Ebene)

- `OPEN_QUESTIONS.md` fuehrt verbleibende Spezifikationsluecken (insb. `Q003`, `Q006`, `Q007`, `Q009`).
- `ASSUMPTIONS_PROPOSED.md` enthaelt unverbindliche Best-Effort-Annahme fuer `ObjectState.msg`.

## Minimalruntime Freeze-Umsetzung (2026-03-14)

Aus Dokument 002 plus geklaerten Freeze-Entscheidungen jetzt lokal umgesetzt:
- Neues Paket `src/go2_person_perception/`
  - `go2_person_perception/contracts.py`
  - `go2_person_perception/person_surface_logic.py`
  - `go2_person_perception/person_surface_node.py`
  - `launch/person_surface.launch.py`
  - Inhaltlich: nur Frozen-Surface fuer
    - `/perception/person_visible`
    - `/perception/person_pose`
    - `/perception/person_last_seen`
  - jetzt ueber Stub hinaus umgesetzt:
    - lokale, private Adapter-Eingaenge fuer `PoseStamped` in `map` und optional `Bool` fuer Sichtbarkeit
    - `person_last_seen` wird nur bei gueltiger `map`-Pose aktualisiert
    - keine Pose-Ausgabe bei fehlender/ungueltiger Pose
  - weiterhin bewusst klein gehalten:
    - keine Base-Steuerung
    - kein `cmd_vel`
    - keine spekulative Detector-/Tracking-Logik
    - `frame_id` wird auf `map` normiert

- Neues Paket `src/go2_manipulation_runtime/`
  - `go2_manipulation_runtime/pick_result_mapping.py`
  - `go2_manipulation_runtime/release_result_mapping.py`
  - `go2_manipulation_runtime/d1_reuse_points.py`
  - `go2_manipulation_runtime/backend_adapter.py`
  - Inhaltlich:
    - lokale normative Result-Code-Helfer fuer Pick/Release
    - lokale fachliche Ableitung auf Event-/Missionslabels
    - bewusste Wiederverwendungspunkte fuer bestehenden D1-550-Bestand
    - duenne Trennung zwischen technischer Backend-Ebene und normativer Result-Code-Ebene
  - bewusst nicht umgesetzt:
    - keine neue Pick-Action-/Release-Service-Definition
    - keine Base-Repositionierung
    - keine doppelte MoveIt-/Controller-/DDS-Architektur

- Tests lokal hinzugefuegt:
  - `tests/test_person_surface_contracts.py`
  - `tests/test_manipulation_runtime_mappings.py`
  - Inhaltlich:
    - Person-Topic-Namen
    - `frame_id=map` fuer Pose-Surface
    - `person_last_seen` nur bei gueltiger Pose
    - keine direkte Steuerungslogik im Person-Surface
    - Pick-/Release-Mapping gemaess Freeze
    - Backend-Adapterrahmen getrennt von normativer Mapping-Ebene
    - D1-550-Reuse-Punkte als lokale Runtime-Basis

- Dokument 002 nachgeschaerft:
  - Person-Topic-Typen inklusive `person_last_seen : PoseStamped(frame_id=map)`
  - Follow/Return nur ueber rate-limitiertes `navigate_to_pose` Goal-Streaming
  - kein direkter Controllerpfad / kein `cmd_vel` fuer Follow
  - Trennung normative Pick-Result-Code-Ebene vs fachliche Orchestrator-Ebene
  - Release-Auswertung ueber `(release_mode, result_code)`
  - Manipulationsposturen bleiben lokal und nicht Shared Surface

Lokal/implementierungsspezifisch und ausdruecklich NICHT Shared Surface:
- Manipulationsposturen `safe`, `carry`, `offer`, `pregrasp`
- technische D1-550 Named States `home`, `ready`, `stow`, `open`, `closed`

## Phase-1 Shared-Surface-Audit (2026-03-13)

Auditquellen in dieser Runde:
- `src/go2_apportation_msgs/`
- `config/contracts.yaml`
- `src/go2_apportation_orchestrator/`
- orchestratornahe Tests unter `tests/`

### Aus Dokument 002 ableitbar und im Repo bereits vorhanden

- Messages vorhanden:
  - `Detection3D.msg`
  - `Detection3DArray.msg`
  - `ObjectState.msg`
  - `ThrowStatus.msg`
- Action vorhanden:
  - `PickObject.action`
- Service vorhanden:
  - `ReleaseObject.srv`
- Dokumentnahe Orchestrator-States/Transitions sind als statische Spiegel in `transition_spec.py` vorhanden, einschliesslich:
  - `SEARCH_PERSON`
  - `OBSERVE_HAND`
  - `TRACK_THROWN`
  - `SEARCH_OBJECT_LOCAL`
  - `SEARCH_OBJECT_GLOBAL`
  - `INTERCEPT`
  - `PICK`
  - `RETURN_TO_PERSON`
  - `HOLD_AND_FOLLOW`
- Minimale Skill-Endpunkte im Orchestrator sind vorhanden fuer:
  - Nav2 `request_navigate` / `request_cancel`
  - Manipulation `request_pick` / `request_pick_cancel` / `request_release`

### Im Repo vorhanden, aber nur vorbereitet / stub-only / teilverbunden

- `ObjectState.msg` und `ThrowStatus.msg` sind angelegt, werden im Orchestrator aber aktuell nicht produktiv konsumiert.
- `PickObject.action` und `ReleaseObject.srv` sind im ROS-Client verdrahtet, aber nur mit minimalem Request-Aufbau; dokumentierte Result-Codes/Stufen sind nicht als Konstanten oder fachliche Auswertung im Orchestrator gespiegelt.
- `config/contracts.yaml` spiegelt nur Basis-Topics und Frames (`/odom`, `/cmd_vel`, `/nav2/cmd_vel`, Kamera/LiDAR, Frames), nicht den vollen missionsweiten Shared Surface aus Dokument 002.
- `behavior_trees/mission_flow_stub.xml` reserviert nur den BT-Ablageort; keine Missionslogik.
- `orchestrator_runtime_node.py` arbeitet eventgetrieben ueber `/orchestrator/event`, `/orchestrator/state`, `/orchestrator/status`; die im Dokument 002 genannten globalen Eingabetopics (`/voice/command`, `/perception/*`, `/tracking/*`) sind dort noch nicht angebunden.

### Im Audit als Luecke bestaetigt

- Fehlende Dokument-002-Interfaces im Msg-Paket:
  - `PredictedRegion.msg`
  - `InterceptGoal.msg`
- Fehlende technische Spiegel fuer dokumentierte globale Contracts:
  - `/voice/command`
  - `/perception/person_pose`
  - `/perception/person_visible`
  - `/perception/person_last_seen`
  - `/perception/object_pose_6d`
  - `/perception/object_visible`
  - `/perception/object_last_seen`
  - `/tracking/detections3d_fast`
  - `/tracking/object_state`
  - `/tracking/throw_status`
  - `/tracking/predicted_region`
  - `/tracking/intercept_goal`
  - `/follow_waypoints`
- Legacy-/Stale-Pfad im Orchestratorpaket:
  - `state_contracts.py` / `orchestrator_node.py` bilden nicht denselben Shared Surface ab wie `transition_spec.py` / `orchestrator_runtime_core.py`.

### Explizite Audit-Einschaetzung fuer die neun angefragten Schritte

- `SEARCH_PERSON`: zustandsseitig sauber gespiegelt; Shared Surface zu Person-Perception nur dokumentiert, noch nicht technisch angebunden.
- `OBSERVE_HAND`: zustandsseitig gespiegelt; Hand-/Objekt-Wahrnehmung nur dokumentiert, kein Wire-Up.
- `TRACK_THROWN`: zustandsseitig gespiegelt; ohne `PredictedRegion.msg`/`InterceptGoal.msg` nicht voll abbildbar.
- `SEARCH_OBJECT_LOCAL`: zustandsseitig gespiegelt; benoetigt dokumentierte, aber noch nicht gespiegelt/verdrahtete Objekt-Topics.
- `SEARCH_OBJECT_GLOBAL`: zustandsseitig gespiegelt; `follow_waypoints` ist dokumentiert, aber im Orchestrator noch nicht als Skill-/Client-Surface vorhanden.
- `INTERCEPT`: Guard/Transition vorhanden; echtes Intercept-Contract bleibt unvollstaendig ohne `InterceptGoal.msg`.
- `PICK`: minimal abbildbar ueber `PickObject.action`.
- `RETURN_TO_PERSON`: zustandsseitig gespiegelt; Person-Perception-Contract fehlt als technischer Anschluss.
- `HOLD_AND_FOLLOW`: zustandsseitig gespiegelt; Follow bleibt nur als dokumentierte Nav2-Goal-Streaming-Semantik, kein spezifischer technischer Contract im Repo.

### Verifikationsnotiz dieser Runde

- `pytest ...` ueber das Default-`pytest` der Umgebung scheiterte, weil Python 2.7 statt Python 3 verwendet wurde.
- `python3 -m pytest ...` scheiterte in dieser Umgebung frueh an fehlenden ROS-Python-Abhaengigkeiten (`ModuleNotFoundError: action_msgs`).
- Deshalb ist in dieser Runde nur der statische Audit verifiziert, nicht ein vollstaendiger Testlauf.

## Phase-2 Orchestrator-Audit (2026-03-13)

### Dateikategorien im Paket

Dokumentnaher Runtime-Kern:
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_spec.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_context.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_resolver.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_engine_pure.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/orchestrator_runtime_core.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/orchestrator_runtime_node.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/action_token_dispatcher.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/interfaces.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/skill_bundle.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_stub.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_ros_client.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_real_client.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/manipulation_skill_stub.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/manipulation_skill_ros_client.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/release_mode_constants.py`

Legacy-/alternative Stub-Pfade:
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/state_contracts.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/orchestrator_node.py`
- `src/go2_apportation_orchestrator/behavior_trees/mission_flow_stub.xml`

### Reale technische Bestandsaufnahme

States im Runtime-Kern technisch vorhanden:
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

Events im Runtime-Kern technisch vorhanden:
- Voice: `vc_lets_play`, `vc_search`, `vc_release`, `vc_abort`, `vc_pause`, `vc_resume`
- Perception/Nav/Manipulation: `person_detected`, `person_lost`, `object_detected`, `object_lost`, `throw_suspected`, `throw_confirmed`, `approach_reached`, `intercept_reached`, `nav_failed`, `object_unreachable`, `grasp_ok`, `grasp_failed`, `object_dropped`
- Safety/Override: `e_stop`, `timeout`, `localization_lost`, `battery_low`, `MANUAL_OVERRIDE_ACTIVE`, `MANUAL_OVERRIDE_RELEASED`

Action-/Service-/Topic-Bridges real im Code erkennbar:
- Runtime-Topics:
  - `/orchestrator/event`
  - `/orchestrator/state`
  - `/orchestrator/status`
- Nav2-Bridge:
  - real/stub Adapter fuer `/navigate_to_pose`
  - Cancel-Pfad vorhanden
- Manipulations-Bridge:
  - real/stub Adapter fuer `/manipulation/pick`
  - real/stub Adapter fuer `/manipulation/release`
  - Pick-Cancel-Pfad vorhanden

Nicht real verdrahtet, nur nominell/stub:
- `/voice/command` ist nur in `STATE_ACTIONS_BASELINE` als Dokumentspiegel genannt, nicht im Runtime-Node angeschlossen.
- `/follow_waypoints` ist nur in `STATE_ACTIONS_BASELINE` als Dokumentspiegel genannt, nicht als echter Skill-/Client-Pfad umgesetzt.
- `SEARCH_OBJECT_GLOBAL` nutzt technisch denselben generischen `nav_goal(...)`-Dispatch wie andere Nav2-Ziele; ein eigener Waypoint-Adapter fehlt.
- `HOLD_AND_FOLLOW` existiert als State/Transition-Logik, aber ohne periodischen Nav2-Goal-Update-Mechanismus im Code.
- `RETURN_TO_PERSON` existiert als echter State und Transition-Pfad, aber ohne direkte Person-Topic-Anbindung im Runtime-Node.
- `PICK` ist real an `PickObject.action` gekoppelt, jedoch nur ueber minimale Action-Client-/Stub-Ansteuerung ohne fachliche Zielbefuellung.

### Testabdeckung nach Pfaden

Deutlich vom Runtime-Kern getragen:
- `tests/test_transition_resolver.py`
- `tests/test_transition_engine_pure.py`
- `tests/test_orchestrator_runtime_core.py`
- `tests/test_action_token_dispatcher.py`
- `tests/test_nav2_skill_real_client.py`
- `tests/test_mode_updates.py`
- `tests/test_skill_bundle_factory.py`
- `tests/test_release_mode_constants.py`

Keine explizite Abdeckung des alten Stub-Pfads gefunden:
- `state_contracts.py`
- `orchestrator_node.py`
- `mission_flow_stub.xml`

## Kleiner Shared-Surface-Freeze fuer Person-Perception und MoveIt-nahe Missionsauswertung (2026-03-13)

### Technisch gespiegelt

In `config/contracts.yaml` jetzt zusaetzlich gespiegelt:
- `/perception/person_visible`
- `/perception/person_pose`
- `/perception/person_last_seen`

Der bestehende Mirror wurde dabei nicht strukturell erweitert, sondern nur innerhalb des vorhandenen `topics`-Blocks ergaenzt.

### Nur dokumentiert, bewusst nicht technisch gespiegelt

- Typbindung:
  - `/perception/person_visible` -> `std_msgs/Bool`
  - `/perception/person_pose` -> `geometry_msgs/PoseStamped`
  - `/perception/person_last_seen` -> `geometry_msgs/PoseStamped`
- Framebindung:
  - `person_pose.frame_id = map`
  - `person_last_seen.frame_id = map`
- Nav-Freeze:
  - fuer Return/Follow ist aktuell nur `/navigate_to_pose` verpflichtender Shared Surface
  - `/follow_waypoints` bleibt ausserhalb des aktuellen Pflicht-Surface
- Missionsseitige Pick-/Release-Auswertung:
  - normative Wire-/Runtime-Ebene: `PickObject.result_code` mit `PICK_SUCCESS`, `PICK_FAILED`, `OBJECT_DROPPED`, `PICK_UNREACHABLE`, `PICK_TIMEOUT`, `SAFETY_ABORTED`
  - davon abgeleitete Orchestrator-Events: `PICK_SUCCESS -> grasp_ok`, `PICK_FAILED -> grasp_failed`, `OBJECT_DROPPED -> object_dropped`, `PICK_UNREACHABLE -> object_unreachable`, `PICK_TIMEOUT -> timeout`, `SAFETY_ABORTED -> safety_abort`
  - Ist-Stand: die ersten fuenf Ziel-Events sind im Runtime-Kern bereits als Eventnamen sichtbar; `safety_abort` ist fuer diese Pick-Auswertung dokumentiert, aber noch nicht als eigener Runtime-Eventname gespiegelt
  - `ReleaseObject` wird missionsseitig aus `(release_mode, result_code)` ausgewertet
- Manipulationsposturen:
  - `safe`, `carry`, `offer`, `pregrasp` bleiben lokal in der Manipulationsruntime

### Warum nur dokumentiert

- Der vorhandene `config/contracts.yaml`-Mirror bildet Topic-/Frame-Werte ab, nicht den vollstaendigen Typ-/Semantik-/Event-Mapping-Raum.
- Fuer Pick-/Release-Missionsauswertung existiert im aktuellen Repo keine bereits etablierte, nicht-spekulative Mirror-Struktur.
- Deshalb wurde der Shared Surface absichtlich klein gehalten und nur dort technisch gespiegelt, wo die bestehende Struktur es bereits sauber zulaesst.

## Kleiner Shared-Surface-Freeze fuer Wuerfel-/Tracking-Minimum (2026-03-14)

### Technisch gespiegelt

In `config/contracts.yaml` jetzt zusaetzlich gespiegelt:
- `/perception/object_visible`
- `/perception/object_pose_6d`
- `/perception/object_last_seen`
- `/tracking/detections3d_fast`

Der bestehende Mirror wurde weiterhin nicht strukturell erweitert, sondern nur um eindeutig benennbare Topic-Eintraege und Freeze-Notizen ergaenzt.

### Nur dokumentiert, bewusst nicht technisch gespiegelt

- Typ-/Semantik-Freeze:
  - `/perception/object_visible` -> `std_msgs/Bool`
  - `/perception/object_pose_6d` -> `geometry_msgs/PoseStamped`
  - `/perception/object_last_seen` -> `geometry_msgs/PoseStamped`
  - `/tracking/detections3d_fast` -> `go2_apportation_msgs/Detection3DArray`
- Shared-Surface-Regeln:
  - keine Covariance-Pflicht fuer `/perception/object_pose_6d`
  - keine Covariance-Pflicht fuer `/perception/object_last_seen`
  - Wuerfel-Semantik: 180-Grad-aequivalente Kantenorientierung gilt fuer Greifzwecke als derselbe Zustand
  - FAST-/tracking-relevante Outputs bleiben `odom`-gefuehrt
  - PRECISE-/pick-relevante Pose muss ein gueltiges `frame_id` tragen und TF-transformierbar nach `odom`/`map` bleiben
  - Tracking/Prediction liefert nur Zustand/Praediktion, keine Motion
- CR / Arbeitspaket:
  - keine weiteren Msg-Arbeitspakete in diesem Freeze-Block; `PredictedRegion` und `InterceptGoal` werden unten als umgesetzt nachgezogen

### Warum nur dokumentiert

- Der vorhandene `config/contracts.yaml`-Mirror traegt Topic-Namen und knappe Freeze-Notizen, aber keinen vollen Typ-/IDL-/CR-Schema-Raum.
- Fuer `PredictedRegion.msg` und `InterceptGoal.msg` werden nur die aus Dokument 002 direkt ableitbaren Minimalfelder eingefroren.
- Dokument 002 und der abgestimmte Freeze unterscheiden sich aktuell beim Ziel-Frame von `/perception/object_last_seen` (`odom` im Dokument, `map` im Freeze); diese Kante wird dokumentiert statt im Code kaschiert.

## Kleiner Shared-Surface-Freeze fuer `/tracking/object_state` und `/tracking/throw_status` (2026-03-14)

### Technisch gespiegelt

In `config/contracts.yaml` jetzt zusaetzlich gespiegelt:
- `/tracking/object_state`
- `/tracking/throw_status`

Der bestehende Mirror wurde weiterhin nicht strukturell erweitert, sondern nur um Topic-Eintraege und knappe Freeze-Notizen ergaenzt.

### Nur dokumentiert, bewusst nicht technisch gespiegelt

- Oeffentliche Wire-Types:
  - `/tracking/object_state` -> `go2_apportation_msgs/ObjectState`
  - `/tracking/throw_status` -> `go2_apportation_msgs/ThrowStatus`
- Minimalsemantik:
  - `ObjectState` steht fuer trackingseitigen Objektzustand fuer Praediktion / ETA
  - Kernbedeutung von `ObjectState`: Pose / Velocity / Covariance
  - `ObjectState` ist `odom`-gefuehrt
  - `ThrowStatus` steht fuer groben Wurf-/Freigabe-Lebenszyklus
  - weder `ObjectState` noch `ThrowStatus` tragen Motion-/`cmd_vel`-Semantik
- Eingefrorene oeffentliche `ThrowStatus`-Zustaende:
  - `IDLE`
  - `HELD`
  - `RELEASE_SUSPECTED`
  - `THROWN`
  - `LANDED`
  - `LOST`

### Kompatibilitaet der bestehenden Msgs

- `src/go2_apportation_msgs/msg/ObjectState.msg`: kompatibel
  - nutzt `PoseWithCovariance` plus `TwistWithCovariance`
  - damit ist die geforderte Kernbedeutung `pose / velocity / covariance` bereits abgedeckt
  - kein Feld-Refactoring noetig
- `src/go2_apportation_msgs/msg/ThrowStatus.msg`: kompatibel
  - enthaelt genau die eingefrorenen oeffentlichen Statuskonstanten
  - keine Zusatzstatuswerte, die fuer diesen Freeze bereinigt werden muessten

### Weiterhin offen / nicht erzwungen

- Sichtbarkeit bleibt ausserhalb von `ObjectState` auf `/perception/object_visible`
- zusaetzliche Plausibilitaets-/Track-FSM-Felder werden nicht neu eingefroren
- Debounce-/Timing-Heuristiken fuer `ThrowStatus` werden nicht erzwungen
- spaetere Tracking-/Intercept-Logik bleibt ausserhalb dieses Msg-Freezes

## Shared-Surface-Freeze fuer `PredictedRegion` und `InterceptGoal` (2026-03-14)

### Technisch umgesetzt

Im Msg-Paket neu angelegt:
- `src/go2_apportation_msgs/msg/PredictedRegion.msg`
- `src/go2_apportation_msgs/msg/InterceptGoal.msg`

Im Build nachgezogen:
- `src/go2_apportation_msgs/CMakeLists.txt`

Im technischen Mirror zusaetzlich gespiegelt:
- `/tracking/predicted_region`
- `/tracking/intercept_goal`

### Eingefrorene oeffentliche Surface-Definition

- `/tracking/predicted_region` -> `go2_apportation_msgs/PredictedRegion`
- `/tracking/intercept_goal` -> `go2_apportation_msgs/InterceptGoal`

`PredictedRegion.msg`
- `std_msgs/Header header`
- `geometry_msgs/Pose center`
- `geometry_msgs/Vector3 size`
- `float32 confidence`
- `builtin_interfaces/Duration valid_for`

`InterceptGoal.msg`
- `std_msgs/Header header`
- `geometry_msgs/PoseStamped target_pose`
- `float32 approach_radius_m`
- `float32 goal_tolerance_m`
- `float32 confidence`
- `builtin_interfaces/Duration valid_for`
- `bool is_dynamic_estimate`

### Nur dokumentiert, bewusst nicht weiter aufgeblasen

- `PredictedRegion` bleibt oeffentliche Unsicherheitsregion fuer die vorhergesagte Objektlage
- `InterceptGoal` bleibt replannbares Intercept-Ziel fuer Navigation/Orchestrator
- beide Surface-Typen bleiben `odom`-gefuehrt und motion-frei
- keine `cmd_vel`-, Velocity-, Acceleration- oder Controller-Sollwerte
- keine Mehrhypothesen, Rohtrajektorien, Kandidatenlisten, Ranking-/Scoring-Logik oder planner-spezifischen Zusatzparameter

## Bridge-nahe Runtime-Contracts und Directive-Freeze (2026-03-18)

### Technisch umgesetzt

Im Msg-Paket neu angelegt:
- `src/go2_apportation_msgs/msg/TrackingDirective.msg`

Im Msg-Build nachgezogen:
- `src/go2_apportation_msgs/CMakeLists.txt`

Im Orchestrator minimal vorbereitet:
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/runtime_contracts.py`
- `src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_spec.py`

Im technischen Mirror zusaetzlich gespiegelt:
- `/cmd_vel_nav2`
- `/look_yaw_delta`
- `/balance_rpy_cmd`
- `/control_mode_cmd`
- `/tracking/tracking_directive`
- Frame `base_link_nav2`

### Klar getrennt nach Herkunft

Sicher aus Dokument 002 ableitbar:
- realer TF-Hauptpfad bleibt `map -> odom -> base_link -> sensor_frames`
- Orchestrator bleibt zustaendig fuer State-Wechsel, Nav2-Ziele, Cancel und Pick-Gating
- Tracking-/Prediction-Surface bleibt motion-frei
- `ObjectState` bleibt `odom`-gefuehrt

Expliziter Projekt-Freeze dieser Runde:
- `base_link_nav2` als offizieller technischer Runtime-Integrationsframe
- `odom_nav2` nur legacy/debug, nicht produktiver Standard
- `/cmd_vel_nav2`, `/look_yaw_delta`, `/balance_rpy_cmd`, `/control_mode_cmd` als zentral gespiegeltete runtime-nahe technische Contracts
- `/tracking/predicted_region` und `/tracking/intercept_goal` oeffentlich kanonisch `map`-basiert
- `TrackingDirective.msg` als kompakter diskreter Empfehlungskanal
- Look-Regelung direkt Perception/Tracking -> Bridge
- `SEARCH_OBJECT_LOCAL` bleibt in `velocity_move`

### Minimaler Orchestrator-Nachzug

- parsebare neue Directive-Events vorhanden:
  - `request_intercept`
  - `request_local_search`
  - `request_global_search`
  - `request_pick_ready`
  - `request_pick_abort`
- neue Runtime-Konstanten/Mappings dokumentiert:
  - `INTERCEPT -> velocity_move`
  - `SEARCH_OBJECT_LOCAL -> velocity_move`
  - `OBSERVE_HAND -> balance_stand`
- keine neuen Transitionen
- keine neue Runtime-Bridge
- keine Fahrlogik

### Weiterhin offen / nicht erzwungen

- `PICK_REACQUIRE` ist kein aktueller Runtime-State und wurde daher nicht als State eingefuehrt
- `ObjectState` wird in diesem Task nicht auf `map` umgefroren
- bridge-seitige Implementierung ausserhalb des Ownership-Bereichs bleibt unberuehrt
