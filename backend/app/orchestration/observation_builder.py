from app.schemas.agent import AgentObservation
from app.schemas.game import GameState, Role
from app.orchestration.communication import visible_events
from app.orchestration.tool_registry import allowed_actions, targets
def build_observation(state: GameState, events, agent_id: str) -> AgentObservation:
    player = next(p for p in state.players if p.agent_id == agent_id)
    visible = visible_events(events, agent_id)
    private = [e.payload.copy() for e in visible if e.visibility == "private"]
    if player.role == Role.MAFIA:
        private.append({"type": "mafia_team", "agent_ids": [p.agent_id for p in state.players if p.role == Role.MAFIA]})
    return AgentObservation(agent_id=agent_id, round_number=state.round_number, phase=state.phase,
        own_role=player.role, alive_player_ids=[p.agent_id for p in state.players if p.alive],
        allowed_actions=allowed_actions(state, agent_id), eligible_target_ids=targets(state, agent_id),
        public_events=[e.model_dump(mode="json") for e in visible if e.visibility == "public"], private_messages=private)
