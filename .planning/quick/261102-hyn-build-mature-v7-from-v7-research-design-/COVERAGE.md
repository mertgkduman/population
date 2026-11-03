# Integration coverage decision

No external API integration: V7 is an offline, local Python/JavaScript research workflow over versioned JSON, CSV, gzip, and NPZ artifacts; it uses no vendor API, SDK, remote service, credential, secret, network request, or public deployment.

No database integration: model state and evidence are immutable local files with schema validation and hashes, so database schema migration/push coverage is not applicable.
