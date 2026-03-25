# Mapping / Calibration / Replay Runbook

Der unterstützte Pfad für eine brauchbare Referenzkarte ist:

1. Referenz-Bag aufnehmen
2. Kalibrierung trocken prüfen
3. Kalibrierung laufen lassen
4. Finale Replay-Referenzkarte aus dem besten Extrinsics-Ergebnis erzeugen
5. Artefakte prüfen

## Host-Startpfade

Alles über den Host-Wrapper:

```bash
./scripts/rtabmap/run_camera_mount_workflow_in_container.sh record
./scripts/rtabmap/run_camera_mount_workflow_in_container.sh dry-run
./scripts/rtabmap/run_camera_mount_workflow_in_container.sh calibrate
./scripts/rtabmap/run_camera_mount_workflow_in_container.sh reference-map
```

Optional mit `/scan` beim Recording oder Replay:

```bash
./scripts/rtabmap/run_camera_mount_workflow_in_container.sh record --with-scan
./scripts/rtabmap/run_camera_mount_workflow_in_container.sh reference-map --with-scan
```

## Ergebnisorte

- Bags:
  - `artifacts/bags/calibration_YYYYmmdd_HHMMSS`
- Kalibrierläufe:
  - `artifacts/calibration/camera_mount/<timestamp>`
  - `artifacts/calibration/camera_mount/latest`
- Finale Replay-Referenzläufe:
  - `artifacts/reference_mapping/<timestamp>`
  - `artifacts/reference_mapping/latest`
- Referenzkarten:
  - `artifacts/maps/<timestamp>`

## Was ein guter Referenz-Bag enthalten muss

Pflicht:

- `/camera/realsense2_camera/color/image_raw`
- `/camera/realsense2_camera/aligned_depth_to_color/image_raw`
- `/camera/realsense2_camera/color/camera_info`
- `/utlidar/robot_odom`
- `/tf`
- `/tf_static`

Optional:

- `/scan`

Praktisch hilfreich:

- Die ersten ca. 10 Sekunden sollten Boden und mindestens eine Wand sauber zeigen.
- Keine harten Sync-/TF-Warnungen während der Aufnahme.
- Möglichst keine Aussetzer in RGB, aligned depth oder Odom.

## Wie man erkennt, ob die Karte brauchbar ist

Wichtige Artefakte:

- `artifacts/maps/<timestamp>/rtabmap.db`
- `artifacts/maps/<timestamp>/map.pgm`
- `artifacts/maps/<timestamp>/map.yaml`
- `artifacts/reference_mapping/<timestamp>/evaluation.txt`

Gute Zeichen:

- `map.pgm` und `map.yaml` existieren
- Wände wirken gerade statt doppelt oder ausgefranst
- `evaluation.txt` zeigt keine starke Häufung von TF-/Timing-Warnungen

Typische Fehlerbilder:

- Fast alles belegt / „überall Hindernisse“:
  - oft Extrinsics-, Depth- oder Sync-Problem
- Doppelte Wände / Ghosting:
  - oft falsche Mount-Extrinsics oder Timing-/TF-Drift
- Fehlende Karte oder fast leere Karte:
  - Bag unvollständig, Topics fehlen oder Replay-Mapping konnte keine brauchbare DB aufbauen
- `Input database doesn't have any nodes saved in it.`:
  - der Replay-Lauf hat zwar eine SQLite-Datei erzeugt, aber fachlich keine RTAB-Map-Knoten gespeichert
  - zuerst `db_sanity.log`, `04_mapping.err.log` und `05_bag_play.err.log` im jeweiligen Replay-/Candidate-Ordner prüfen
- `Replay TF/clock mismatch`:
  - der Replaypfad hat TF-/Clock-Daten aus gemischten Zeitbasen gesehen
  - zuerst `01_odom_tf.err.log`, `04_mapping.err.log`, `05_bag_play.err.log` und `db_sanity.log` prüfen

## Unterstützte Produktivkette

- Live-Aufnahme über `camera_mount_workflow.sh record`
- Offline-Kalibrierung über `camera_mount_workflow.sh dry-run` und `calibrate`
- Finaler Replay-Mappinglauf über `camera_mount_workflow.sh reference-map`
- Kartenbewertung über das bereits vorhandene `evaluate_map_artifacts.py`
