from app.schemas.agent import AgentAction
from app.schemas.game import GameState, Phase, Role
def allowed_actions(state: GameState, agent_id: str) -> list[str]:
    p = next(p for p in state.players if p.agent_id == agent_id)
    if not p.alive: return []
    if state.phase == Phase.DISCUSSION: return ["speak"]
    if state.phase == Phase.VOTING: return ["vote"]
    if state.phase == Phase.NIGHT:
        return {Role.MAFIA: ["night_action"], Role.DETECTIVE: ["investigate"]}.get(p.role, [])
    return []
def targets(state: GameState, agent_id: str) -> list[str]:
    actor = next(p for p in state.players if p.agent_id == agent_id)
    return sorted(p.agent_id for p in state.players if p.alive and p.agent_id != agent_id
                  and not (state.phase == Phase.NIGHT and actor.role == Role.MAFIA and p.role == Role.MAFIA))
def validate_action(state: GameState, expected_id: str, action: AgentAction) -> None:
    if action.agent_id != expected_id: raise ValueError("Actor identity mismatch")
    if action.action_type not in allowed_actions(state, expected_id): raise ValueError("Action forbidden")
    target = getattr(action, "target_agent_id", None)
    if action.action_type != "speak" and target not in targets(state, expected_id):
        raise ValueError("Illegal target")
    if action.action_type == "speak" and target is not None and target not in targets(state, expected_id):
        raise ValueError("Illegal speech target")
