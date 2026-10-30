# Restoring original large research artifacts

All original bytes are preserved in this version’s .large-files directory. From the repository root, run python scripts/restore_large_files.py. The manifest publication/large_files.json records original paths, sizes and SHA-256 checksums. The Pages workflow restores them automatically before building. Restored originals are ignored by Git to keep the publication snapshot pushable.
