from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
class Role(StrEnum):
    MAFIA = "mafia"
    DETECTIVE = "detective"
    CITIZEN = "citizen"
class Phase(StrEnum):
    SETUP = "setup"
    NIGHT = "night"
    DAWN = "dawn_announcement"
    DISCUSSION = "day_discussion"
    VOTING = "voting"
    RESOLUTION = "vote_resolution"
    ENDED = "game_ended"
class Player(BaseModel):
    model_config = ConfigDict(extra="forbid")
    agent_id: str
    role: Role
    alive: bool = True
class GameState(BaseModel):
    """Authoritative server-only state. Never serialize into public responses."""
    model_config = ConfigDict(extra="forbid")
    game_id: str
    round_number: int = 1
    phase: Phase = Phase.SETUP
    players: list[Player]
    winner: str | None = None
class GameConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seed: int = 7
    roles: list[Role] = Field(default_factory=lambda: [Role.MAFIA, Role.DETECTIVE, Role.CITIZEN, Role.CITIZEN, Role.CITIZEN])
    first_phase: str = "night"
    tie_rule: str = "lowest_agent_id"
    reveal_role_on_elimination: bool = False
    discussion_turns_per_player: int = Field(default=1, ge=1, le=5)
    night_action_order: list[str] = Field(default_factory=lambda: ["investigate", "mafia_kill"])
