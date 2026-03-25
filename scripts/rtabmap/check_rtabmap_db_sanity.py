#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check that an RTAB-Map SQLite database exists and contains saved nodes."
    )
    parser.add_argument("--db", required=True, help="Path to rtabmap.db")
    parser.add_argument("--context", default="rtabmap replay", help="Short label for error messages")
    parser.add_argument(
        "--artifact-dir",
        help="Optional artifact directory to mention in failure messages",
    )
    parser.add_argument(
        "--log-path",
        action="append",
        default=[],
        help="Optional log path to mention in failure messages (can be repeated)",
    )
    return parser.parse_args()


def count_rows(cursor: sqlite3.Cursor, table_name: str) -> int | None:
    tables = {row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if table_name not in tables:
        return None
    return int(cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0])


def main() -> int:
    args = parse_args()
    db_path = Path(args.db).resolve()

    if not db_path.exists():
        print(f"[check_rtabmap_db_sanity] ERROR: {args.context}: DB file does not exist: {db_path}")
        return 2
    if not db_path.is_file():
        print(f"[check_rtabmap_db_sanity] ERROR: {args.context}: DB path is not a file: {db_path}")
        return 2

    size_bytes = db_path.stat().st_size
    if size_bytes <= 0:
        print(f"[check_rtabmap_db_sanity] ERROR: {args.context}: DB file is empty on disk: {db_path}")
        return 2

    try:
        connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.Error as exc:
        print(f"[check_rtabmap_db_sanity] ERROR: {args.context}: failed to open SQLite DB {db_path}: {exc}")
        return 2

    try:
        cursor = connection.cursor()
        data_count = count_rows(cursor, "Data")
        node_count = count_rows(cursor, "Node")
        admin_count = count_rows(cursor, "Admin")
    except sqlite3.Error as exc:
        print(f"[check_rtabmap_db_sanity] ERROR: {args.context}: failed to inspect DB {db_path}: {exc}")
        return 2
    finally:
        connection.close()

    print(f"[check_rtabmap_db_sanity] context={args.context}")
    print(f"[check_rtabmap_db_sanity] db_path={db_path}")
    print(f"[check_rtabmap_db_sanity] size_bytes={size_bytes}")
    print(f"[check_rtabmap_db_sanity] data_rows={data_count}")
    print(f"[check_rtabmap_db_sanity] node_rows={node_count}")
    print(f"[check_rtabmap_db_sanity] admin_rows={admin_count}")

    data_rows = int(data_count or 0)
    node_rows = int(node_count or 0)
    semantic_nonempty = data_rows > 0 or node_rows > 0
    print(f"[check_rtabmap_db_sanity] semantic_nonempty={'true' if semantic_nonempty else 'false'}")

    if semantic_nonempty:
        return 0

    print(
        f"[check_rtabmap_db_sanity] ERROR: {args.context}: RTAB-Map DB exists but has no saved nodes "
        f"(Data={data_rows}, Node={node_rows}): {db_path}"
    )
    if args.artifact_dir:
        print(f"[check_rtabmap_db_sanity] artifact_dir={Path(args.artifact_dir).resolve()}")
    for log_path in args.log_path:
        print(f"[check_rtabmap_db_sanity] log_path={Path(log_path).resolve()}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
