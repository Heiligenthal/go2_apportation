# ASSUMPTIONS_PROPOSED.md

Phase 1 haelt neue fachliche Defaults bewusst minimal.

Benutzerentscheidungen D1-D5 (bereits entschieden, daher keine neuen Annahmen):
- BT als Framework-Default (nur Skeleton/Stub)
- Runtime-Topics/Frames bleiben Platzhalter
- eigenes Msg-Paket `go2_apportation_msgs`
- Contracts + Orchestrator-Skeleton + Spezifikationsartefakte + Appendix-Templates
- Python fuer erste Nodes/Stubs

Neu vorgeschlagene Defaults (klar unverbindlich, Best-Effort):
- A001: `go2_apportation_msgs/msg/ObjectState.msg` wird in Phase 1 als minimaler Stub mit
  `std_msgs/Header`, `geometry_msgs/PoseWithCovariance`, `geometry_msgs/TwistWithCovariance`
  angelegt (weil Dokument 002 nur "Pose, Velocity, Covariance" nennt, aber keine exakte Msg-Definition liefert).
  Status: unverbindlich, durch Dokument/Entscheidung nachzuziehen.

Nicht vorgeschlagen / bewusst offen gelassen:
- konkrete Runtime-Topic-Werte
- Action-Definitionen (Pick/Release etc.)
- harte cmd_vel-Ownership-Enforcement-Logik

Neu vorgeschlagene lokale Implementierungsdefaults (nicht Shared Surface):
- A002: `go2_person_perception` darf private lokale Eingänge `~/input/person_pose_map` und `~/input/person_visible`
  verwenden, solange nach außen ausschließlich die gefreezten Person-Topics publiziert werden.
  Status: rein implementierungslokal, nicht dokumentierter Shared Surface.
