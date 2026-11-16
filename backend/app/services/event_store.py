from pathlib import Path
from app.schemas.events import GameEvent
def save_events(path: Path, events: list[GameEvent]):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(e.model_dump_json()+"\n" for e in events))
