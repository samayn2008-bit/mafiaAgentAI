# Event contract — initial proposal for joint review
GameEvent has schema_version, game_id, event_id, type, round_number, phase, visibility, audience and payload. Per-game event IDs are monotonic and authoritative for replay order. Public projection retains IDs, so gaps are expected.
public is available to all; private requires explicit player recipients; inspector is excluded from public and player views. GameState must never be sent as a public snapshot. Never export raw canonical events as public replay.
Payloads are dictionaries in the scaffold; typed payload variants, timestamps, snapshot cursors, WebSocket delivery and reconnect semantics must be agreed before frontend integration. Public consumers must not assume contiguous IDs.
