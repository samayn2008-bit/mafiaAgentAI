import asyncio
from collections import Counter
from pydantic import TypeAdapter
from app.schemas.agent import AgentAction, SpeakAction, VoteAction, InvestigateAction, NightAction
from app.schemas.game import Phase, Role
from app.orchestration.observation_builder import build_observation
from app.orchestration.tool_registry import validate_action
from app.orchestration.turn_manager import speaking_order
class MockAgent:
    async def decide(self, observation):
        kind = observation.allowed_actions[0]
        if kind == "speak": return SpeakAction(agent_id=observation.agent_id, message="Let us compare the public evidence.")
        cls = {"vote": VoteAction, "investigate": InvestigateAction, "night_action": NightAction}[kind]
        return cls(agent_id=observation.agent_id, target_agent_id=observation.eligible_target_ids[0])
class Orchestrator:
    def __init__(self, engine, agents, timeout=5):
        self.engine, self.agents, self.timeout = engine, agents, timeout
    async def request(self, agent_id):
        e = self.engine
        observation = build_observation(e.state, e.events, agent_id)
        try:
            action = await asyncio.wait_for(self.agents[agent_id].decide(observation), self.timeout)
            action = TypeAdapter(AgentAction).validate_python(action)
            validate_action(e.state, agent_id, action)
            return action
        except (Exception,) as exc:
            e.emit("ACTION_FAILED", {"agent_id": agent_id, "error_type": type(exc).__name__}, "inspector")
            # Deterministic, bounded fallback avoids a permanently stalled game.
            action = await MockAgent().decide(observation)
            validate_action(e.state, agent_id, action)
            return action
    async def run(self):
        e = self.engine
        while not e.state.winner:
            e.transition(Phase.NIGHT)
            kill = None
            for role in [Role.DETECTIVE, Role.MAFIA]:
                for p in e.state.players:
                    if p.alive and p.role == role:
                        action = await self.request(p.agent_id)
                        if role == Role.DETECTIVE:
                            target = next(t for t in e.state.players if t.agent_id == action.target_agent_id)
                            e.emit("INVESTIGATION_RESULT", {"target_agent_id": target.agent_id, "is_mafia": target.role == Role.MAFIA}, "private", [p.agent_id])
                        else: kill = action.target_agent_id
            e.transition(Phase.DAWN)
            if kill: e.eliminate(kill, "night")
            if e.check_winner(): break
            e.transition(Phase.DISCUSSION)
            for _ in range(e.config.discussion_turns_per_player):
                for agent_id in speaking_order(e.state):
                    action = await self.request(agent_id)
                    e.emit("AGENT_SPEECH", {"agent_id": agent_id, "text": action.message, "emotion": action.emotion, "intensity": action.intensity})
            e.transition(Phase.VOTING)
            votes = []
            # Sequential collection keeps the MVP information order explicit.
            for agent_id in speaking_order(e.state):
                action = await self.request(agent_id)
                votes.append(action.target_agent_id)
                e.emit("VOTE_CAST", {"agent_id": agent_id, "target_agent_id": action.target_agent_id})
            e.transition(Phase.RESOLUTION)
            tally = Counter(votes)
            target = min(tally, key=lambda t: (-tally[t], t))
            e.emit("VOTING_COMPLETED", {"tally": dict(tally), "eliminated_agent_id": target})
            e.eliminate(target, "vote")
            if not e.check_winner(): e.state.round_number += 1
        return e
