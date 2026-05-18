# OpenEyes CLI JSON Protocol (v1)

All commands run with `--json` return this envelope:

```json
{
  "ok": true,
  "cli_schema_version": "1",
  "data": {},
  "error": null
}
```

## Envelope fields
- `ok` (bool): success indicator.
- `cli_schema_version` (string): current protocol version (`"1"`).
- `data` (object): command-specific payload.
- `error` (object|null): structured error payload with fields `code`, `message` when `ok=false`.

## ask command payload (data)
Typical fields include:
- `answer`
- `answer_class`
- `confidence`
- `domain`
- `routed_domain`
- `routing_confidence`

## Backward compatibility
- Schema version is pinned to `1` currently.
- New fields may be added to `data` without changing version.
- Field removals or semantic changes require a schema version bump.
