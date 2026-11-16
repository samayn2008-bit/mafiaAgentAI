from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.schemas.game import Phase
class GameEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    schema_version: int = 1
    event_id: int = Field(ge=1)
    game_id: str
    type: str
    round_number: int
    phase: Phase
    visibility: Literal["public", "private", "inspector"] = "public"
    audience: list[str] = Field(default_factory=list)
    payload: dict = Field(default_factory=dict)
    @model_validator(mode="after")
    def validate_audience(self):
        if self.visibility == "public" and self.audience:
            raise ValueError("Public events cannot specify a restricted audience")
        if self.visibility == "private" and not self.audience:
            raise ValueError("Private events require recipients")
        return self
