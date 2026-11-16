from typing import Protocol
from app.schemas.agent import AgentAction, AgentObservation
class MafiaAgent(Protocol):
    async def decide(self, observation: AgentObservation) -> AgentAction: ...
