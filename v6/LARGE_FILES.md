# Restoring V6 standalone dashboards

From repository root run `python scripts/restore_large_files.py`. Version-local `.large-files/` chunks preserve both original standalone HTML files exactly. Their SHA-256 checksums are in `publication/large_files.json`. The Pages build restores them automatically. Original working research files and history are unchanged.
