import random
from app.schemas.game import GameConfig, GameState, Phase, Player
from app.schemas.events import GameEvent
from app.orchestration.win_conditions import winner
class GameEngine:
    """Minimal mock-game engine. Advanced rule configuration is not implemented."""
    def __init__(self, game_id: str, config: GameConfig | None = None):
        self.config = config or GameConfig()
        if len(self.config.roles) != 5 or sorted(self.config.roles) != ["citizen", "citizen", "citizen", "detective", "mafia"]:
            raise ValueError("Starter engine supports exactly 1 Mafia, 1 Detective, 3 Citizens")
        if (self.config.first_phase != "night" or self.config.tie_rule != "lowest_agent_id"
                or self.config.night_action_order != ["investigate", "mafia_kill"]):
            raise ValueError("Unsupported starter rules")
        roles = list(self.config.roles)
        random.Random(self.config.seed).shuffle(roles)
        self.state = GameState(game_id=game_id, players=[Player(agent_id=f"player_{i+1}", role=r) for i,r in enumerate(roles)])
        self.events: list[GameEvent] = []
        self.emit("GAME_STARTED", {"player_ids": [p.agent_id for p in self.state.players]})
    def emit(self, kind, payload, visibility="public", audience=None):
        event = GameEvent(event_id=len(self.events)+1, game_id=self.state.game_id, type=kind,
            round_number=self.state.round_number, phase=self.state.phase, visibility=visibility,
            audience=audience or [], payload=payload)
        self.events.append(event)
        return event
    def transition(self, phase):
        self.state.phase = phase
        self.emit("PHASE_CHANGED", {"phase": phase.value})
    def eliminate(self, target, reason):
        player = next(p for p in self.state.players if p.agent_id == target)
        if not player.alive: raise ValueError("Player already eliminated")
        player.alive = False
        payload = {"agent_id": target, "reason": reason}
        if self.config.reveal_role_on_elimination: payload["role"] = player.role.value
        self.emit("PLAYER_ELIMINATED", payload)
    def check_winner(self):
        self.state.winner = winner(self.state)
        if self.state.winner:
            self.transition(Phase.ENDED)
            self.emit("GAME_ENDED", {"winner": self.state.winner})
        return self.state.winner
