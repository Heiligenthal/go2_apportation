# go2_nav2_bridge

`go2_nav2_bridge` ist die Runtime-Komponente zwischen Nav2 und dem offiziellen Unitree-Go2-Sportmode.

Produktiv gilt in diesem Paket:

- reale TF-Kette bleibt unverändert:
  - `map -> odom -> base_link -> sensor_frames`
- virtuelle Nav2-Basis kommt zusätzlich aus der Bridge:
  - `base_link -> base_link_nav2`
- Nav2 arbeitet mit:
  - `global_frame = map`
  - `local frame = odom`
  - `robot_base_frame = base_link_nav2`
- RTAB-Map, Localization und Sensorframes bleiben auf dem realen `base_link`

## Produktive Semantik

### Reale vs. virtuelle Basis

- `base_link` bleibt die reale Roboterbasis.
- `base_link_nav2` ist nur die virtuelle Nav2-Basis.
- Die Bridge publiziert produktiv **nur** den dynamischen TF:
  - Parent: `base_link`
  - Child: `base_link_nav2`
  - Translation: immer `0 0 0`
  - Rotation: `normalize(fake_yaw - real_yaw)`

Dadurch bleibt die reale Pose unverändert, Nav2 bekommt aber eine virtuelle Fahrtrichtung.

### Nav2-Eingang

- Nav2 publiziert auf `/cmd_vel_nav2`
- `angular.z` wird als Änderung der virtuellen Fahrtrichtung interpretiert
- die Bridge integriert daraus `fake_yaw`
- die reale Translation wird so kompensiert, dass die Bahn in `map` konsistent bleibt
- die reale Körperrotation folgt nur der Look-Regelung

### Direkte Eingänge

- `/look_yaw_delta`
  - relativer Yaw-Offset für die reale Blick-/Körperregelung
- `/balance_rpy_cmd`
  - `roll`, `pitch`, `yaw` für `BalanceStand + Euler`
- `/control_mode_cmd`
  - `velocity_move`
  - `balance_stand`

### Sportmode-State

- Eingang: `lf/sportmodestate`
- daraus liest die Bridge reale Position, reale Weltgeschwindigkeit und reale Yaw

## Modi

### `velocity_move`

- `cmd_vel_nav2` wird verarbeitet
- `fake_yaw` wird nur aus `angular.z` integriert
- Bewegung an den Roboter geht über `Move(vx, vy, vyaw)`
- bei ausbleibendem `cmd_vel_nav2` greift der Watchdog und sendet `StopMove()`

### `balance_stand`

- beim Wechsel sendet die Bridge zuerst `StopMove()`
- danach `BalanceStand()`
- anschließend fortlaufend `Euler(roll, pitch, yaw)`

Die Bridge übernimmt **nicht**:

- Nav2-Cancel-Ownership
- Missionslogik
- State-Wechsel-Ownership außerhalb ihres eigenen Nodes
- Würfel-/Tracking-/Manipulationslogik

## Legacy / Debug

Ein separater virtueller Odom-Pfad `odom_nav2 -> base_link_nav2` ist **nicht** mehr produktiver Standard.

Optional bleibt nur ein Legacy-/Debug-Pfad:

- `publish_legacy_nav2_odom: true`
- Topic: `/odom_nav2`
- Frame: `odom_nav2`

Produktiv bleibt dieser Pfad deaktiviert.

## Build im Runtime-Container

```bash
source /opt/ros/humble/setup.bash
source /workspace/repo/install_container/setup.bash
colcon build --build-base build_container --install-base install_container --packages-select go2_nav2_bridge
source /workspace/repo/install_container/setup.bash
ros2 pkg prefix go2_nav2_bridge
```

## Produktiver Startpfad

Host-seitig:

```bash
./scripts/rtabmap/run_nav2_bridge_with_rtabmap_localization.sh --map-yaml <map.yaml>
```

Dieser Wrapper nutzt den bestehenden Container-SOP und startet im Runtime-Pfad:

- `board_description`
- `realsense_board`
- `rtabmap_localization`
- `nav2_rtabmap`
- `go2_nav2_bridge` als Teil von `nav2_rtabmap.launch.py`

Wenn `go2_nav2_bridge` im Overlay noch nicht gebaut ist, versucht der Runner zuerst einen kleinen `colcon build --packages-select go2_nav2_bridge` im Runtime-Container.

## Smoke-Checks

Nach dem Start sollten diese Punkte gelten:

- `map -> odom -> base_link` bleibt auflösbar
- `base_link -> base_link_nav2` ist dynamisch vorhanden
- `base_link -> base_link_nav2` hat immer `xyz = 0 0 0`
- `/cmd_vel_nav2` ist sichtbar
- `go2_nav2_bridge` subscribt `/cmd_vel_nav2`
- Sensorframes bleiben unter `base_link`, nicht unter `base_link_nav2`

Reproduzierbarer Runtime-Smoke:

```bash
./scripts/rtabmap/smoke_test_nav2_bridge_runtime.sh
```

Der Smoke-Test prüft den realen Produktivpfad und validiert:

- `/go2_nav2_bridge` läuft
- `base_link -> base_link_nav2` ist auflösbar
- `/cmd_vel_nav2`, `/look_yaw_delta`, `/balance_rpy_cmd`, `/control_mode_cmd` sind an die Bridge verdrahtet
- `/odom_nav2` ist nicht als aktiver Produktivpfad sichtbar
- ein Zero-Twist auf `/cmd_vel_nav2` wird angenommen und endet danach per Watchdog wieder in `StopMove()`

## Laufzeit-Hinweise

- Ohne frischen `lf/sportmodestate` sendet die Bridge keine produktiven Bewegungsbefehle.
- Wenn `lf/sportmodestate` während der Laufzeit stale wird, sendet die Bridge `StopMove()` und loggt den Timeout klar.
- `linear.y` auf `/cmd_vel_nav2` wird im produktiven nicht-holonomen Modus verworfen und gewarnt.
- `look_yaw_delta` in `balance_stand` und `balance_rpy_cmd` in `velocity_move` werden diagnostisch gewarnt, aber nicht als Missionslogik interpretiert.
