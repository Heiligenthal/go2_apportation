# Manual Sensor Extrinsics Calibration

Produktiver Startpfad:

```bash
./scripts/rtabmap/run_manual_sensor_calibration.sh
```

Optional:

```bash
./scripts/rtabmap/run_manual_sensor_calibration.sh --restart-container
./scripts/rtabmap/run_manual_sensor_calibration.sh --no-rviz
```

Was gestartet wird:

- `launch/manual_sensor_calibration.launch.py`
- RealSense über `launch/realsense_board.launch.py`
- `robot_state_publisher` mit Community-Go2-Modell `go2_robot_sdk/urdf/go2.urdf`
- RViz mit `config/manual_sensor_calibration.rviz`
- interaktiver Terminal-Helfer `scripts/rtabmap/manual_sensor_extrinsics_helper.py`

Warum dieses Robot Model der Default ist:

- Die repo-eigene `go2_description/urdf/go2.urdf` enthält bereits `camera_link` und `lidar_frame` als feste Sensorlinks.
- Für eine live verstellbare manuelle Kalibrierung würde das direkt eine zweite konkurrierende Quelle für dieselben Sensor-TFs erzeugen.
- Das Community-Modell zeigt den Roboter in RViz, ohne `camera_link` und `utlidar_lidar` als aktive Default-Sensor-TFs in denselben Frames zu erzwingen.

Im RViz prüfen:

- `Grid`
- `TF`
- `Robot Model`
- `LiDARCloud` auf `/utlidar/cloud`
- `CameraCloud` auf `/camera/realsense2_camera/depth/color/points`

Hotkeys im Terminal:

- `1/2/3` Schrittweite fein / mittel / grob
- `TAB` aktiven Sensor wechseln (`camera` / `lidar`)
- `q/a` x +/-
- `w/s` y +/-
- `e/d` z +/-
- `r/f` roll +/-
- `t/g` pitch +/-
- `y/h` yaw +/-
- `p` speichern
- `x` beenden
- `?` Hilfe erneut anzeigen

Initialwerte:

- Kamera: neuester Lauf aus `artifacts/calibration/camera_mount/*/best_extrinsics.env`
- LiDAR: bestehende Werte aus `config/mapping_test_extrinsics.env`
- Falls nichts gefunden wird, startet der Helfer mit `0 0 0` und loggt das klar.

Gespeicherte Dateien:

- `artifacts/manual_calibration/<timestamp>/manual_sensor_extrinsics.env`
- `artifacts/manual_calibration/<timestamp>/camera_manual_extrinsics.env`
- `artifacts/manual_calibration/<timestamp>/lidar_manual_extrinsics.env`
- `artifacts/manual_calibration/<timestamp>/camera_best_extrinsics_compatible.env`
- `artifacts/manual_calibration/latest -> <timestamp>`

Wichtig:

- Die Dateien werden nur abgelegt. Sie werden nicht automatisch in produktive Launch-/URDF-/Runtime-Pfade übernommen.
- Die Übernahme in produktive Pfade bleibt bewusst ein manueller Schritt.
