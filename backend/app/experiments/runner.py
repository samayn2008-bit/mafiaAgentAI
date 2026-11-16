import asyncio
from pathlib import Path
from app.orchestration.game_engine import GameEngine
from app.orchestration.orchestrator import Orchestrator, MockAgent
from app.orchestration.communication import visible_events
from app.services.event_store import save_events
async def main():
    engine = GameEngine("mock-demo-001")
    await Orchestrator(engine, {p.agent_id: MockAgent() for p in engine.state.players}).run()
    save_events(Path("data/replays/mock-demo.public.jsonl"), visible_events(engine.events))
    print(f"Winner: {engine.state.winner}; canonical events: {len(engine.events)}")
    print("Saved public replay; private events and authoritative state were not exported.")
if __name__ == "__main__": asyncio.run(main())
