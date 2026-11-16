from pathlib import Path
from app.schemas.events import GameEvent
def load_events(path: Path) -> list[GameEvent]:
    events = [GameEvent.model_validate_json(line) for line in path.read_text().splitlines() if line.strip()]
    ids = [e.event_id for e in events]
    if ids != sorted(set(ids)) or len({e.game_id for e in events}) > 1:
        raise ValueError("Invalid replay sequence")
    return events
