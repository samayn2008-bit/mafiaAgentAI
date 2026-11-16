from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.game import Phase, Role
class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
class SpeakAction(Contract):
    agent_id: str
    action_type: Literal["speak"] = "speak"
    message: str = Field(min_length=1, max_length=1000)
    target_agent_id: str | None = None
    emotion: str | None = None
    intensity: float = Field(default=0.5, ge=0, le=1)
class VoteAction(Contract):
    agent_id: str
    action_type: Literal["vote"] = "vote"
    target_agent_id: str
class InvestigateAction(Contract):
    agent_id: str
    action_type: Literal["investigate"] = "investigate"
    target_agent_id: str
class NightAction(Contract):
    agent_id: str
    action_type: Literal["night_action"] = "night_action"
    target_agent_id: str
AgentAction = Annotated[SpeakAction | VoteAction | InvestigateAction | NightAction, Field(discriminator="action_type")]
class AgentObservation(Contract):
    agent_id: str
    round_number: int
    phase: Phase
    own_role: Role
    alive_player_ids: list[str]
    allowed_actions: list[str]
    eligible_target_ids: list[str]
    public_events: list[dict] = Field(default_factory=list)
    private_messages: list[dict] = Field(default_factory=list)
