# Manual Sensor Extrinsics Calibration

Produktive Betriebsvariante:

- Extension Board / Runtime-Container:
  - Sensoren
  - TF
  - Robot Model Quelle
  - interaktiver Terminal-Helfer
- Ubuntu-Laptop:
  - RViz nativ als externer ROS2-Teilnehmer

Board-Start:

```bash
./scripts/rtabmap/run_manual_sensor_calibration.sh
```

Der Runner startet auf dem Board:

- `launch/manual_sensor_calibration.launch.py`
- RealSense
- `robot_state_publisher` mit repo-eigenem `go2_description/urdf/go2.urdf`
- `go2_tf_tools/zero_joint_state_publisher`
- manuellen TF-Helfer
- manuelle RViz-Cloud-Themen:
  - `/manual_calibration/lidar_cloud`
  - `/manual_calibration/camera_cloud`

Der Board-Runner startet standardmäßig **kein RViz im Container**.

Ubuntu-Laptop-RViz:

```bash
./scripts/rtabmap/run_manual_sensor_calibration_rviz.sh
```

Auf dem Ubuntu-Laptop muss lokal vorhanden und gesourced sein:

- `/opt/ros/humble/setup.bash`
- ein lokaler Workspace-Overlay mit `go2_description`
- `rviz2`

Warum `go2_description` lokal nötig ist:

- Das Robot Model wird in RViz über `package://go2_description/...`-Meshes aufgelöst.
- Deshalb braucht der Ubuntu-Laptop eine lokal verfügbare und gesourcte `go2_description`-Installation.

Wichtige Live-Annahmen:

- gleicher `ROS_DOMAIN_ID` auf Board und Ubuntu-Laptop
- kein Sim-Time-/Replay-Pfad
- Fixed Frame in RViz: `base_link`

Manuelle RViz-Cloud-Themen:

- Input vom Board:
  - LiDAR: `/utlidar/cloud` oder `/utlidar/cloud_base`
  - Kamera-PointCloud2: erkannter `/camera/*/depth/color/points`-Pfad
- Für RViz neu publiziert:
  - `/manual_calibration/lidar_cloud`
  - `/manual_calibration/camera_cloud`
- Diese manuellen RViz-Themen behalten den Sensor-`frame_id`, werden aber mit `stamp=now` neu publiziert.

Initialwerte:

1. `artifacts/manual_calibration/latest/manual_sensor_extrinsics.env`
2. danach getrennt:
   - `artifacts/manual_calibration/latest/camera_manual_extrinsics.env`
   - `artifacts/manual_calibration/latest/lidar_manual_extrinsics.env`
3. danach:
   - Kamera: letzter Kamera-Mount-Kalibrierlauf
   - LiDAR: `config/mapping_test_extrinsics.env`

Hotkeys:

- `1/2/3` Schrittweite
- `TAB` Sensor wechseln
- `q/a` x +/-
- `w/s` y +/-
- `e/d` z +/-
- `r/f` roll +/-
- `t/g` pitch +/-
- `y/h` yaw +/-
- `p` speichern
- `x` beenden

Gespeicherte Dateien:

- `artifacts/manual_calibration/<timestamp>/manual_sensor_extrinsics.env`
- `artifacts/manual_calibration/<timestamp>/camera_manual_extrinsics.env`
- `artifacts/manual_calibration/<timestamp>/lidar_manual_extrinsics.env`
- `artifacts/manual_calibration/latest -> <timestamp>`
