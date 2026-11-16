from app.schemas.events import GameEvent
def visible_events(events: list[GameEvent], agent_id: str | None = None) -> list[GameEvent]:
    return [e for e in events if e.visibility == "public" or
            (agent_id is not None and e.visibility == "private" and agent_id in e.audience)]
