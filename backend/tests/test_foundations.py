import asyncio
import pytest
from app.schemas.agent import InvestigateAction
from app.schemas.game import Phase, Role
from app.orchestration.game_engine import GameEngine
from app.orchestration.orchestrator import Orchestrator, MockAgent
from app.orchestration.observation_builder import build_observation
from app.orchestration.communication import visible_events
from app.orchestration.tool_registry import validate_action
from app.services.event_store import save_events
from app.services.replay import load_events

def play(agents=None):
    e = GameEngine("test")
    asyncio.run(Orchestrator(e, agents or {p.agent_id: MockAgent() for p in e.state.players}).run())
    return e

def test_complete_deterministic_game_and_replay(tmp_path):
    a,b = play(),play()
    assert a.state.winner in {"town", "mafia"}
    assert a.events == b.events
    assert [e.event_id for e in a.events] == list(range(1,len(a.events)+1))
    path = tmp_path/"public.jsonl"
    save_events(path, visible_events(a.events))
    assert load_events(path) == visible_events(a.events)
    assert all(e.visibility == "public" for e in load_events(path))

def test_private_result_is_recipient_only():
    e = GameEngine("privacy")
    detective = next(p for p in e.state.players if p.role == Role.DETECTIVE)
    citizen = next(p for p in e.state.players if p.role == Role.CITIZEN)
    e.emit("INVESTIGATION_RESULT", {"secret": "result"}, "private", [detective.agent_id])
    assert build_observation(e.state,e.events,detective.agent_id).private_messages
    assert not build_observation(e.state,e.events,citizen.agent_id).private_messages
    assert not any(ev.type == "INVESTIGATION_RESULT" for ev in visible_events(e.events))
    assert "role" not in e.events[0].payload

def test_role_and_actor_permissions():
    e = GameEngine("permissions")
    e.transition(Phase.NIGHT)
    citizen = next(p for p in e.state.players if p.role == Role.CITIZEN)
    with pytest.raises(ValueError):
        validate_action(e.state,citizen.agent_id,InvestigateAction(agent_id=citizen.agent_id,target_agent_id="player_1"))

class BrokenAgent:
    async def decide(self, observation):
        return {"malformed": True}

def test_invalid_agents_do_not_stall():
    e = play({f"player_{i}": BrokenAgent() for i in range(1,6)})
    assert e.state.winner
    assert any(ev.type == "ACTION_FAILED" for ev in e.events)
