def speaking_order(state):
    """Stable, bounded ordering; future personality affects choices within these limits."""
    return sorted(p.agent_id for p in state.players if p.alive)
