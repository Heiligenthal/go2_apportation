# README_DEV.md

## Testausfuehrung

Alle Befehle im Repository-Root ausfuehren (`/home/alex/Projektarbeit/repository`).

Falls `pytest` noch nicht installiert ist:

```bash
python3 -m pip install pytest
```

Tests starten:

```bash
python3 -m pytest -q
```

## Build & Tests (Container)

```bash
scripts/docker/run_checks_in_container.sh
scripts/docker/run_humble_ros_base.sh
```

Hinweis: Host-`pytest` kann auf manchen Systemen Python2 verwenden. Fuer reproduzierbare Ergebnisse den Container-Runner nutzen (`python3 -m pytest` im Humble-Container).
Default ist Host-UID/GID im Container; optional kann mit `--as-root` gestartet werden.
Nav2-abhaengige Tests sind mit Marker `nav2` gekennzeichnet und benoetigen `nav2_msgs` (im `ros:humble-ros-base` Baseline-Run werden sie ggf. geskippt).
`community_sdk/` ist per `COLCON_IGNORE` aus Default-Builds ausgeschlossen. Fuer explizite Community-Builds `COLCON_IGNORE` entfernen und separat bauen.

Optionaler schneller Python-Syntaxcheck:

```bash
python3 -m py_compile \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/action_token_dispatcher.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/orchestrator_runtime_core.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/orchestrator_runtime_node.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_ros_client.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_real_client.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/manipulation_skill_ros_client.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/release_mode_constants.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/nav2_skill_stub.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/manipulation_skill_stub.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/skills/skill_bundle.py \
  src/go2_apportation_mocks/go2_apportation_mocks/mock_nav2_server.py \
  src/go2_apportation_mocks/go2_apportation_mocks/mock_manipulation_server.py \
  src/go2_tf_tools/go2_tf_tools/odom_to_tf_broadcaster.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_context.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_engine_pure.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_spec.py \
  src/go2_apportation_orchestrator/go2_apportation_orchestrator/transition_resolver.py \
  tests/test_action_token_dispatcher.py \
  tests/test_mode_updates.py \
  tests/test_release_mode_constants.py \
  tests/test_skill_bundle_factory.py \
  tests/test_transition_resolver.py \
  tests/test_transition_engine_pure.py \
  tests/test_orchestrator_runtime_core.py \
  tests/test_odom_to_tf_broadcaster.py
```

## Humble Container Start (CLI)

Minimaler Start fuer eine Humble CLI im Board-Umfeld (host network, optional privileged):

```bash
chmod +x scripts/docker/run_humble_ros_base.sh
scripts/docker/run_humble_ros_base.sh
ENABLE_PRIVILEGED=1 scripts/docker/run_humble_ros_base.sh
```

## TF Adapter Start

Der Adapter publisht nur `odom->base_link` aus `/utlidar/robot_odom`:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run go2_tf_tools odom_to_tf_broadcaster
ros2 run go2_tf_tools odom_to_tf_broadcaster --ros-args -p odom_topic:=/utlidar/robot_odom -p parent_frame:=odom -p child_frame:=base_link
```

## go2_description robot_state_publisher

```bash
ros2 launch go2_description robot_state_publisher.launch.py
```

Hinweis: Das Launchfile liefert statische Ketten unterhalb der Basis aus dem URDF. `odom->base_link` bleibt weiterhin Aufgabe des TF-Adapters (`go2_tf_tools`).

## Bring up TF + URDF frames on board

```bash
scripts/bringup/run_board_description_in_container.sh
```

Hinweis: Dieses Bringup verbindet `odom->base_link` mit dem URDF-Teilbaum (`base` als URDF-Wurzel) ueber einen statischen Identity-Transform.

## Board Minimal Bringup (R1)

Minimaler Board-Start als Launch-Datei + Docker-Wrapper:

```bash
chmod +x scripts/bringup/run_board_minimal.sh
scripts/bringup/run_board_minimal.sh
```

Optional mit `--privileged` am Container:

```bash
ENABLE_PRIVILEGED=1 scripts/bringup/run_board_minimal.sh
```

Pruefen, dass TF verfuegbar ist:

```bash
ros2 topic echo /tf --once
ros2 run tf2_ros tf2_echo odom base_link
```

Hinweis: Ein `/utlidar/robot_odom -> /odom` Relay wird in R1 bewusst nicht gestartet, um keine zusaetzliche Relay-Abhaengigkeit einzufuehren.

## Verify board_minimal

```bash
scripts/bringup/verify_board_minimal.sh
scripts/bringup/verify_board_minimal.sh --start-bringup
```

Logs werden unter `artifacts/board_minimal_verify/<timestamp>/` geschrieben.

## RTAB-Map Launch Scaffold (R3)

Neue Launch-Scaffolds:
- `launch/rtabmap_mapping.launch.py`
- `launch/rtabmap_localization.launch.py`

Required args (derzeit ohne Default):
- `rgb_topic`
- `depth_topic`
- `camera_info_topic`

Topic discovery (Beispiel auf laufendem System):

```bash
ros2 topic list | grep -E "(image_raw|aligned_depth|camera_info)"
```

Beispiel Mapping:

```bash
ros2 launch launch/rtabmap_mapping.launch.py \
  rgb_topic:=<RGB_TOPIC> \
  depth_topic:=<DEPTH_TOPIC> \
  camera_info_topic:=<CAMERA_INFO_TOPIC>
```

Beispiel Localization:

```bash
ros2 launch launch/rtabmap_localization.launch.py \
  rgb_topic:=<RGB_TOPIC> \
  depth_topic:=<DEPTH_TOPIC> \
  camera_info_topic:=<CAMERA_INFO_TOPIC> \
  database_path:=<RTABMAP_DB_PATH>

# RealSense Beispiel (Board):
ros2 launch launch/rtabmap_localization.launch.py \
  rgb_topic:=/camera/realsense2_camera/color/image_raw \
  depth_topic:=/camera/realsense2_camera/aligned_depth_to_color/image_raw \
  camera_info_topic:=/camera/realsense2_camera/color/camera_info \
  database_path:=<RTABMAP_DB_PATH>
```

## R3 Mapping (E2E one command)

```bash
scripts/rtabmap/run_r3_mapping_e2e.sh --duration-seconds 180 --localization-smoke
```

Hinweis: Waehrend des Mapping-Fensters muss der Roboter manuell bewegt werden (Teleop/Operator).
Der erfolgreiche Lauf erzeugt in `artifacts/maps/<timestamp>/` sowohl die Lokalisierungsdatenbank (`rtabmap.db`) als auch die statische Nav2-Karte (`map.yaml` + `map.pgm`).

### Mapping audit: baseline vs. test extrinsics

Der aktuell reproduzierbare Mapping-Pfad im Repo ist:
- `scripts/rtabmap/run_r3_mapping_e2e.sh`
- intern mit `launch/realsense_board.launch.py`
- `launch/board_description.launch.py`
- `launch/rtabmap_mapping.launch.py`
- Export nach `artifacts/maps/<timestamp>/`

Wichtiger Ist-Zustand:
- `odom->base_link` kommt aus `go2_tf_tools/odom_to_tf_broadcaster` via `/utlidar/robot_odom`
- `base_link->base` kommt aus `go2_description/launch/base_link_bridge.launch.py`
- `base->camera_link` existiert bereits in `src/go2_description/urdf/go2.urdf`
- `base->lidar_frame` existiert bereits in `src/go2_description/urdf/go2.urdf`
- das Mapping-E2E-Skript nutzt fuer den beobachteten LiDAR-Frame `utlidar_lidar` weiterhin eine separate statische TF

Baseline-Lauf mit aktuellem Repo-Verhalten:

```bash
scripts/rtabmap/run_r3_mapping_e2e.sh \
  --duration-seconds 180 \
  --privileged \
  --allow-uncalibrated-lidar
```

Testlauf mit experimentellen Extrinsics:

```bash
scripts/rtabmap/run_r3_mapping_e2e.sh \
  --duration-seconds 180 \
  --privileged \
  --use-test-extrinsics
```

`--use-test-extrinsics` laedt `config/mapping_test_extrinsics.env` und setzt:
- Kamera aus URDF-Pfad (`camera_tf_source=urdf`), damit kein zusaetzlicher statischer `base_link->camera_link` Publisher erzeugt wird
- LiDAR-Testextrinsics fuer `base_link -> utlidar_lidar`

Auswertung eines einzelnen Laufs:

```bash
python3 scripts/rtabmap/evaluate_map_artifacts.py \
  --map-dir artifacts/maps/<timestamp> \
  --run-dir artifacts/r3_mapping/<timestamp>
```

Vergleich Baseline vs. Test-Extrinsics:

```bash
python3 scripts/rtabmap/evaluate_map_artifacts.py \
  --map-dir artifacts/maps/<test_timestamp> \
  --run-dir artifacts/r3_mapping/<test_timestamp> \
  --compare-map-dir artifacts/maps/<baseline_timestamp> \
  --compare-run-dir artifacts/r3_mapping/<baseline_timestamp>
```

Kompakter Board-Vergleichslauf fuer beide Varianten hintereinander:

```bash
scripts/rtabmap/run_mapping_extrinsics_compare.sh --duration-seconds 180 --privileged
```

Der Wrapper schreibt:
- `artifacts/mapping_compare/<timestamp>/comparison_summary.txt`
- `artifacts/mapping_compare/<timestamp>/evaluation.txt`

Die Auswertung protokolliert:
- Existenz von `map.pgm` und `map.yaml`
- Dateigroesse sowie PGM-Abmessungen
- einfache Leer-/Dunkelheits-Heuristiken fuer die Karte
- TF-/Timestamp-/Sync-Warnungen aus den Mapping-Logs
- heuristische Gesamtbewertung `better`, `equal` oder `worse`

## RTAB-Map localization visualization

```bash
scripts/rtabmap/run_r3_localization_visualize.sh --privileged
```

Hinweis: Danach RViz auf dem Laptop mit `ROS_DOMAIN_ID=0` oeffnen und `/map` + `/cloud_map` anzeigen.
Hinweis: Fuer Mapping-Experimente sollte die Kamera-TF-Quelle bewusst gewaehlt werden. Die URDF enthaelt bereits `base->camera_link`; ein zusaetzlicher statischer `base_link->camera_link` Publisher kann die TF-Kette inkonsistent machen.

## Nav2 bringup with RTAB-Map localization

```bash
scripts/nav2/run_nav2_with_rtabmap_localization.sh --privileged --allow-uncalibrated-lidar --db <path/to/rtabmap.db> --map-yaml <path/to/map.yaml>
```

Hinweis: Fuer diesen Bringup werden sowohl RTAB-Map-DB (Lokalisierungs-TF `map->odom`) als auch exportiertes `map.yaml` benoetigt.
In diesem Bringup ist `/map` exklusiv `nav2_map_server`; RTAB-Map-Map-Ausgabe wird nicht-autoritativ auf `/rtabmap/map` gelegt.
Dies ist der unterstuetzte Dry-Run-Pfad fuer Goal-Pose-Readiness (Nav2 aktiv, Planner/Controller-Interfaces sichtbar, `/nav2/cmd_vel` aufloesbar), ohne direkte Robot-Motion-Verdrahtung.

## LiDAR-only Mapping (slam_toolbox)

```bash
scripts/slam_toolbox/run_lidar_mapping_e2e.sh --duration-seconds 180 --allow-uncalibrated-lidar --privileged
```

## Visualize map artifacts

Export:

```bash
scripts/rtabmap/export_map_artifacts.sh
```

2D view:

`artifacts/maps/<timestamp>/map.pgm`

RViz (laptop):

Nutze `map.yaml` als Map-Quelle (z.B. Map Display oder `nav2_map_server`).

## Board Runtime (Variant A)

1) Build image once:

```bash
scripts/docker/build_board_runtime_image.sh
```

Das Image enthaelt nun `realsense2_camera`, `rtabmap_ros` (`rtabmap_sync`), `slam_toolbox`, `nav2_map_server` (inkl. `map_saver_cli`) und `pointcloud_to_laserscan`.

2) Start runtime container:

```bash
scripts/bringup/run_board_runtime.sh
```

3) Then launch realsense:

```bash
docker exec -it go2_board_runtime bash -lc "source /opt/ros/humble/setup.bash && (test -f /workspace/repo/install_container/setup.bash && source /workspace/repo/install_container/setup.bash || test -f /workspace/repo/install/setup.bash && source /workspace/repo/install/setup.bash || true) && ros2 launch launch/realsense_board.launch.py"
```

## HIL Smoke Test (on-board)

```bash
scripts/diagnostics/hil_smoke_test.sh
```

Hinweis: Kamera muss angesteckt sein und Docker muss verfuegbar sein.

## Runtime Skeleton Start

Nach Build/Overlay-Setup kann die Runtime-Skeleton-Node so gestartet werden:

```bash
ros2 run go2_apportation_orchestrator orchestrator_runtime
```

Mit ROS-Backend gegen Mocks (`skills_backend` in `stub|mock|ros`):

```bash
ros2 run go2_apportation_orchestrator orchestrator_runtime --ros-args -p skills_backend:=mock
```

## Mock Server Start (Phase 2.6)

```bash
ros2 run go2_apportation_mocks mock_nav2_server
ros2 run go2_apportation_mocks mock_manipulation_server
```

Beispiel-Event publizieren:

```bash
ros2 topic pub /orchestrator/event std_msgs/msg/String \"{data: object_detected}\" -1
```

## Mock E2E Demo

Reproduzierbarer End-to-End Ablauf ohne echte Robotik-Stacks (nur Mocks + ROS-Client-Backend):

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
DEMO_CASE=nav_success BACKEND=ros bash scripts/run_mock_demo.sh
```

Szenarien (Phase 2.8/3.1):

```bash
DEMO_CASE=nav_success BACKEND=ros bash scripts/run_mock_demo.sh
DEMO_CASE=nav_fail BACKEND=ros bash scripts/run_mock_demo.sh
DEMO_CASE=nav_hang_cancel BACKEND=ros bash scripts/run_mock_demo.sh
DEMO_CASE=pick_hang_cancel BACKEND=ros bash scripts/run_mock_demo.sh
DEMO_CASE=real_nav2_goal_send bash scripts/run_mock_demo.sh
DEMO_CASE=real_nav2_cancel bash scripts/run_mock_demo.sh
DEMO_CASE=real_nav2_auto_result_success bash scripts/run_mock_demo.sh
DEMO_CASE=real_nav2_auto_result_fail bash scripts/run_mock_demo.sh
```

Optional:

```bash
CHECK_UNKNOWN_GUARDS=1 DEMO_CASE=nav_success BACKEND=ros bash scripts/run_mock_demo.sh
BACKEND=stub DEMO_CASE=nav_success bash scripts/run_mock_demo.sh
```

Der Demo-Pfad nutzt eine vorhandene Transition aus `transition_spec.py`:
- Startzustand `SEARCH_OBJECT_GLOBAL`
- Event `object_detected`
- Transition nach `INTERCEPT` mit Action-Token `nav_goal(intercept_goal)`

Manueller 3-Terminal-Ablauf (optional statt Skript):

```bash
# Terminal 1
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run go2_apportation_mocks mock_nav2_server
```

```bash
# Terminal 2
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run go2_apportation_mocks mock_manipulation_server
```

```bash
# Terminal 3
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run go2_apportation_orchestrator orchestrator_runtime --ros-args -p skills_backend:=ros -p initial_state:=SEARCH_OBJECT_GLOBAL
ros2 topic pub /orchestrator/event std_msgs/msg/String "{data: object_detected}" -1
ros2 topic echo /orchestrator/status --once --full-length
```

Verifikation:
- Skript meldet `PASS case=<...>` oder `FAIL`
- `/orchestrator/status` enthaelt `last_dispatched_actions_count > 0` (bei `BACKEND=ros`)
- `/orchestrator/status` enthaelt `active_backend`, `chosen_transition_summary`, `timeout_key`,
  `last_unhandled_tokens_count`, `unknown_guard_count`, `enable_real_motion`, `enable_demo_pose`
- Mock-Logs zeigen je nach Case `RESULT_SUCCEEDED`, `RESULT_ABORTED` oder `CANCEL_RECEIVED`/`RESULT_CANCELED`
- Optional: `ros2 action list` und `ros2 service list`

`pick_hang_cancel` Event-Sequenz:
- `object_detected` -> `INTERCEPT`
- `intercept_reached` -> `PICK` (dispatch `start_pick(...)`)
- `vc_abort` -> `IDLE`
- PASS-Kriterien: Manip-Log enthaelt `pick cancel received` und `pick result=canceled`, Status zeigt `IDLE` und Context-Reset-Updates.

`real_nav2_goal_send` Event-Sequenz:
- Start mit `skills_backend=real_nav2`, `enable_real_motion=true`, `enable_demo_pose=true`
- `object_detected` -> `INTERCEPT` (dispatch `nav_goal(...)`)
- PASS-Kriterien: Status `active_backend=real_nav2`, `last_nav_goal_pose_provided=true`, Mock-Nav2-Log enthaelt `GOAL_RECEIVED`.

`real_nav2_cancel` Event-Sequenz:
- wie `real_nav2_goal_send`, aber Nav2-Mock `scenario=hang`
- danach `vc_abort`
- PASS-Kriterien: Status `state=IDLE`, Mock-Nav2-Log enthaelt `CANCEL_RECEIVED` und `RESULT_CANCELED`.

`real_nav2_auto_result_success` Event-Sequenz:
- Start mit `skills_backend=real_nav2`, `enable_real_motion=true`, `enable_demo_pose=true`
- Startzustand `SEARCH_PERSON`, Event `person_detected` (dispatch `nav_goal(person+offset)`)
- Nav2-Result `SUCCEEDED` wird im `real_nav2` Backend automatisch auf `approach_reached` gemappt und in den Core injiziert
- PASS-Kriterien: Status wechselt auf `OBSERVE_HAND`, `last_event=approach_reached`, Summary enthaelt `--approach_reached--> OBSERVE_HAND`.

`real_nav2_auto_result_fail` Event-Sequenz:
- identischer Startpfad wie `real_nav2_auto_result_success`, aber Nav2-Mock `scenario=fail`
- Nav2-Result `ABORTED` wird automatisch auf `nav_failed` gemappt und in den Core injiziert
- PASS-Kriterien: Status wechselt auf `SEARCH_PERSON`, `last_event=nav_failed`, Summary enthaelt `--nav_failed--> SEARCH_PERSON`.

Hinweis: Unit-Tests weiterhin mit `python3 -m pytest -q`.

## Real Nav2 Backend (safe)

Der Backend-Name `real_nav2` (Alias: `real`) nutzt einen echten `NavigateToPose` ActionClient.
Default-Schutz: `enable_real_motion=false` bedeutet, dass keine Goals gesendet werden (nur Diagnostics/History).

Sicherer Start ohne Bewegung:

```bash
ros2 run go2_apportation_orchestrator orchestrator_runtime --ros-args \
  -p skills_backend:=real_nav2 \
  -p enable_real_motion:=false \
  -p nav2_action_name:=/navigate_to_pose
```

Aktive Bewegung nur bewusst einschalten:

```bash
ros2 run go2_apportation_orchestrator orchestrator_runtime --ros-args \
  -p skills_backend:=real_nav2 \
  -p enable_real_motion:=true \
  -p nav2_action_name:=/navigate_to_pose
```

`enable_real_motion:=true` nur verwenden, wenn der Roboter sicher steht und Nav2 korrekt laeuft.

Release-Mode Werte (Baseline):
- `OPEN_GRIPPER=0`
- `DROP_SAFE=1`
- `HANDOVER_RELEASE=2`

## Core-REPL Beispiel (ohne ROS spin)

```bash
python3 - <<'PY'
from src.go2_apportation_orchestrator.go2_apportation_orchestrator.orchestrator_runtime_core import OrchestratorCore
from src.go2_apportation_orchestrator.go2_apportation_orchestrator.transition_spec import TransitionState

core = OrchestratorCore(initial_state=TransitionState.SEARCH_OBJECT_GLOBAL)
status = core.step("object_detected")
print(status["state"], status["last_transition_summary"])
print(core.skills.nav2.history)
PY
```
