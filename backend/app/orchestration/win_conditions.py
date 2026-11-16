from app.schemas.game import GameState, Role
def winner(state: GameState) -> str | None:
    living = [p for p in state.players if p.alive]
    mafia = sum(p.role == Role.MAFIA for p in living)
    if mafia == 0:
        return "town"
    if mafia >= len(living) - mafia:
        return "mafia"
    return None
