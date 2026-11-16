# AI Mafia — Project Context and Implementation Blueprint

> **Audience:** OpenAI Codex and both student developers of the IEEE ML/AI Club AI Mafia project.  
> **Status:** Planning specification; not a description of features already implemented.  
> **Primary development setup:** VS Code + Codex + GitHub.  
> **Guiding priority:** Both teammates learn agentic AI and contribute substantially to the backend. Codex assists especially with frontend scaffolding, 3D presentation, and tests, but code must be understood and reviewed by the team.

---

## 0. Directions for Codex — read this first

1. **Treat this document as the product and architecture context, not as permission to build every feature in one pass.** Implement the milestone requested by the user, keep changes narrowly scoped, and report what was actually completed.
2. **Before making changes**, inspect the repository, existing files, current branch, dependencies, tests, and any other instructions such as `AGENTS.md`. Respect working code; do not blindly overwrite it to match the aspirational tree here.
3. **Separate responsibilities clearly:** Person 1 owns agent intelligence; Person 2 owns orchestration; both own integration, contracts, and frontend. Codex may assist any owner, but should not silently modify files owned by the other person without the task calling for it.
4. **Backend first, visual prototype in parallel.** The MVP is five autonomous agents playing a valid, fully replayable game, plus a simple 3D frontend that plays mock/recorded events. Expand to 8–10 agents after that works.
5. **Use deterministic rules and validated schemas.** LLMs propose actions and dialogue; they never directly mutate authoritative game state, decide role permissions, or execute game rules.
6. **Protect private information by construction.** Ordinary player observations must not contain other roles, Mafia chat, hidden detective results, or developer-only inspector metadata. Do not transmit hidden state through the public WebSocket stream.
7. **Make events replayable.** Stable, ordered event IDs, explicit game phase changes, and state snapshots are central because the 3D frontend and analytics rely on them.
8. **Do not require 3D assets for the backend to function.** A text-mode runner and mock-agent tests should work without the frontend, voices, GPU, or external assets.
9. **Avoid overengineering.** Prefer simple Python structures, Pydantic models, a custom game state machine, JSONL event logs, and one working model provider before adding frameworks, databases, or complex animation pipelines.
10. **Be candid about uncertainty.** Do not claim the 3D models, lip-sync, celebrity voices, analytics, or LLM integration work until implemented and verified. Distinguish proposed examples from real measured values.

## 1. Vision and purpose

Build a **multi-agent AI Mafia social deduction simulation** for a two-person IEEE ML/AI Club team. The game features approximately **7–10 autonomous agents in its eventual form**, each with distinct personalities, separate memories and beliefs, secret game roles, objectives, and access to role-appropriate tools. The initial working MVP should have **five agents**.

The point is not to script a comedy performance. The goal is to observe **emergent behavior** as agents accuse, defend, form alliances, deceive, argue, update suspicions, and cast votes. Different agent personalities should influence how they evaluate situations and choose actions, rather than only changing their dialogue style.

The project has two complementary presentation modes:

1. **Cinematic Spectator Mode:** a polished, desktop-first 3D Mafia table where animated characters speak, react, vote, and survive/eliminate rounds, with a narrator, subtitles, lighting effects, and camera motion.
2. **AI Intelligence Inspector:** a development/demo view that visualizes personality traits, memories, stated or structured beliefs, suspicion scores, relationships, evidence, planned actions, and how those data change across game rounds. Clearly separate *actual game truth* from *what an agent believes*.

The default initial experience is **autonomous spectator mode**, not a human player participating in the game. A human-player mode is a possible future extension, outside the MVP.

The narrator should guide the audience and announce phase transitions and results, but **should not decide what autonomous agents say or do**. Narration can be template-based initially, with optional LLM embellishment later, as long as it cannot change the game state.

### Character direction

Characters can draw inspiration from recognizable *archetypes* associated with celebrities or familiar fictional character types: a loud impulsive comedian, a confident leader, a meticulous detective, a confrontational critic, a quiet observer, a calculating strategist, and so on. **Create original character names, voices, models, and appearances** unless the team has the proper rights/permissions for an identifiable living person's voice or likeness. A warm, deep, cinematic original narrator voice is preferable to an unauthorized imitation of Morgan Freeman or any other real person.

The humor should emerge from strategy and personality collisions—for example, an impulsive character inadvertently contradicts previous statements and loses trust—rather than from rigidly scripted scenes.

## 2. Development environment and technology choices

| Area | Default choice | Rationale |
|---|---|---|
| IDE / coding assistant | **VS Code + Codex** | Full-stack local development; AI assistance with scoped tasks |
| Version control | **Git + GitHub**, one monorepo | Parallel work, branches, pull requests, review |
| Backend language | **Python** | Agent implementations, orchestration, simulation, evaluation |
| API and WebSockets | **FastAPI** | HTTP endpoints, frontend event streaming, inspector endpoints |
| Schema validation | **Pydantic** | Structured action and observation contracts |
| LLM inference | **A hosted LLM API initially** behind a provider abstraction | Avoid fine-tuning or self-hosting complexity at the start |
| Orchestration | **Custom state machine** | Explicit Mafia phases, private information, valid actions |
| Frontend | **React + TypeScript + Vite** | Component UI, predictable integration and tooling |
| 3D | **Three.js + React Three Fiber** | Browser-rendered scene, animated characters and cameras |
| UI styling / animation | Tailwind CSS (optional), GSAP or Framer Motion/Motion as appropriate | Polished UI and cinematic transitions |
| Analytics visualizations | Recharts and/or a suitable graph visualization library | Suspicion charts, directional relationship graph |
| Speech | Consented/licensed synthetic TTS | Distinct, expressive original character voices |
| Initial persistence | **JSONL events + JSON game snapshots** | Simple debugging and replay |
| Later persistence | SQLite if needed | Indexing and multiple-game analysis |
| Testing | pytest for Python; frontend unit/integration tests as needed | Reliability and regression protection |

**Google Colab is not the primary environment.** It can be used later for offline experiment notebooks or GPU-heavy tests, but the interactive web app, local development server, and cross-person development are better suited to VS Code. Google Antigravity is an optional alternative AI IDE, but do not split the project across IDE-specific workflows unnecessarily.

Codex is a coding assistant, not the runtime for the Mafia agents. The Mafia player agents will run through the **Python application** and its configured LLM provider. Using the same underlying model for multiple independent agents with different memory, context, personality, and private information is a good starting point. The project does not require training seven to ten distinct neural networks.

## 3. Ownership, effort, and responsibilities

The two developers both want substantial hands-on agentic AI experience. **No one is relegated to only frontend work.**

### Combined team allocation

- **35%** of total combined effort: Person 1 — Agent Intelligence.
- **35%** of total combined effort: Person 2 — Multi-Agent Orchestration.
- **30%** of total combined effort: Shared — frontend, integration, tests, demo, and polish (split across both teammates).

Equivalently, each person should spend roughly **70% of their own time on backend work and 30% on shared frontend/integration work**. These are planning targets, not tracked actuals.

### Person 1: Agent Intelligence Engineer

**Mission:** Build an autonomous, configurable, reusable Mafia agent that can make decisions based on its own personality, role, permitted observations, history, and beliefs.

Primary implementation ownership:

- `backend/app/agents/base_agent.py` — Define the `MafiaAgent` interface, runtime agent identity, lifecycle, and decision method.
- `backend/app/agents/llm_client.py` — Wrap the chosen model API; support structured output, model configuration, timeout and retry policies, response validation, and optional token/latency tracking. Keep provider-specific code here.
- `backend/app/agents/personality.py` — Create a personality configuration schema and behavior mapping. Traits may include talkativeness, impulsiveness, aggressiveness, analytical tendency, trust, confidence, and loyalty.
- `backend/app/agents/prompts.py` — Build prompts from persona, explicit permitted role knowledge, public observations, personal memory, current objectives, and allowed actions. Never inject unauthorized game truth.
- `backend/app/agents/memory.py` — Store short-term conversational history, significant episodic events, and relevant retrieval. Begin with lists/dicts or a bounded in-game event store, not a vector database.
- `backend/app/agents/beliefs.py` — Track directional suspicion and trust toward other agents, evidence supporting these beliefs, uncertainty, and updates across rounds.
- `backend/app/agents/decision_engine.py` — Assemble context, select or propose legal action candidates, ask the LLM for the next structured action, and return it to the orchestrator without mutating official game state.
- `backend/app/agents/agent_factory.py` — Instantiate multiple independent agent instances from configuration, each with isolated memory and belief state.
- `backend/tests/test_agents.py`, `backend/tests/test_memory.py` — Unit tests and behavioral smoke tests.
- `backend/data/personalities.json` — Agent persona defaults, in consultation with Person 2.

Specific research/learning deliverables:

1. Compare how different personality traits influence both language and decisions. Simply inserting numbers in prompts is not proof that traits affect behavior.
2. Test whether an agent recalls previous statements and identifies contradictions.
3. Measure whether new evidence causes belief estimates to update.
4. Study how agent beliefs diverge from game truth, and whether personality shapes voting behavior.
5. Implement a concrete role-specific **Detective behavior** end-to-end, including private investigation result interpretation, memory, and subsequent decisions. This gives Person 1 direct ownership of one advanced agentic workflow.
6. Expose structured, access-controlled agent state snapshots for the Inspector dashboard.

**Person 1 done means:** Given an authorized `AgentObservation`, a configured agent can reliably return a structured `AgentAction`, maintain its own isolated memory and beliefs, and demonstrate distinguishable personality-conditioned behavior without changing the authoritative game state.

### Person 2: Multi-Agent Orchestration Engineer

**Mission:** Coordinate all autonomous agents within a valid, reliable, privacy-preserving Mafia environment: turn scheduling, game phases, communication channels, tools, game state, event records, and failure recovery.

Primary implementation ownership:

- `backend/app/orchestration/orchestrator.py` — Run the overall game loop and call agents at appropriate phases.
- `backend/app/orchestration/game_engine.py` — Own the canonical game state and enforce deterministic rules.
- `backend/app/orchestration/turn_manager.py` — Schedule turns and bound discussion length; prevent one agent from monopolizing the conversation.
- `backend/app/orchestration/communication.py` — Deliver public broadcasts versus private Mafia/player information without leaks.
- `backend/app/orchestration/observation_builder.py` — Transform authoritative state into a least-privilege `AgentObservation` tailored to the recipient.
- `backend/app/orchestration/tool_registry.py` — Register tool/action schemas and check role, phase, player status, and target permissions.
- `backend/app/orchestration/tools/speak.py` — Public dialogue or accusations.
- `backend/app/orchestration/tools/vote.py` — Validated vote submissions.
- `backend/app/orchestration/tools/investigate.py` — Detective-only investigation requests and results.
- `backend/app/orchestration/tools/role_action.py` — Mafia action and optional other night role actions.
- `backend/app/orchestration/win_conditions.py` — Win conditions, end-of-round transitions, game termination.
- `backend/tests/test_game_engine.py`, `backend/tests/test_permissions.py`, `backend/tests/test_orchestration.py` — Deterministic and mock-agent tests.

Specific research/learning deliverables:

1. Make 5 mock agents complete an entire valid game before using a paid LLM API.
2. Create a private communication pattern among Mafia agents, including permitted planning and collective action. Person 2 should own this advanced **Mafia coordination workflow** end-to-end.
3. Implement explicit role and tool permissions; never trust agent text as authorization.
4. Handle invalid action JSON, illegal targets, unexpected actions, timeouts, API failures, and game continuation safely.
5. Generate structured, ordered event logs and game snapshots for visual playback and experimental evaluation.
6. Scale from five agents to eight to ten, applying concurrency only where agent decisions are truly independent and order of information access remains well defined.

**Person 2 done means:** A complete Mafia simulation can finish using deterministic mock agents without LLM API calls, every action is validated, private information remains private, and ordered events support reliable replay.

### Shared responsibilities

- Define and review Pydantic contracts (`AgentObservation`, `AgentAction`, `GameEvent`, `GameState`, event payloads) *before* independent work starts.
- Integrate Person 1's real LLM agents into Person 2's testable orchestrator.
- Design and implement the FastAPI endpoints, WebSocket streaming, access-controlled Inspector endpoints, event storage, replay, full-game tests, research metrics, and README.
- Co-own the frontend design; use Codex to help implement many React/Three.js components while personally reviewing architecture and runtime behavior.
- Review each other's pull requests and run end-to-end demos together.

**Frontend shared ownership by expertise:**

- Person 1 + Codex: `AgentInspector.tsx`, `SuspicionChart.tsx`, `RelationshipGraph.tsx`, visual interpretation of beliefs/memory/evidence.
- Person 2 + Codex: `AnimationController.ts`, `DialoguePanel.tsx`, `VotingPanel.tsx`, `voiceService.ts`, `useGameSocket.ts`, mapping orchestrator events to presentation.
- Both + Codex: `MafiaScene.tsx`, `Character3D.tsx`, main layout, camera/lighting behavior, `useGameState.ts`, system integration and testing.
- Code generated by Codex is still owned and reviewed by the responsible teammates. **Codex is not a third teammate** and should not be treated as such for project accountability.

### Pull request / collaboration rules

1. Work in **one GitHub repository**, on separate branches such as `feature/agent-memory`, `feature/orchestrator`, `feature/3d-scene`, and `feature/inspector`.
2. Do not independently rewrite shared schemas or mutually dependent interfaces. Contract changes require explicit joint review.
3. Run tests and use pull requests; the other teammate reviews each significant change.
4. Avoid simultaneous Codex edits to the same shared files; use branches or worktrees.
5. Hold at least two short integration sessions per week. Rebalance work after Week 2 if actual time differs from planned estimates.
6. Keep a small working slice on `main` throughout development instead of leaving separate unintegrated systems until the end.

## 4. Target repository tree

**Legend:** `P1` = Person 1; `P2` = Person 2; `Both` = shared; `+ Codex` = AI-assisted construction after human review. This is the **target architecture**, not a mandate to create every file immediately.

```text
ai-mafia/
│
├── backend/
│   ├── app/
│   │   ├── main.py                         # Both — FastAPI startup
│   │   │
│   │   ├── agents/                         # PERSON 1
│   │   │   ├── __init__.py
│   │   │   ├── base_agent.py
│   │   │   ├── llm_client.py
│   │   │   ├── personality.py
│   │   │   ├── prompts.py
│   │   │   ├── memory.py
│   │   │   ├── beliefs.py
│   │   │   ├── decision_engine.py
│   │   │   └── agent_factory.py
│   │   │
│   │   ├── orchestration/                  # PERSON 2
│   │   │   ├── __init__.py
│   │   │   ├── orchestrator.py
│   │   │   ├── game_engine.py
│   │   │   ├── turn_manager.py
│   │   │   ├── communication.py
│   │   │   ├── observation_builder.py
│   │   │   ├── tool_registry.py
│   │   │   ├── win_conditions.py
│   │   │   └── tools/
│   │   │       ├── __init__.py
│   │   │       ├── speak.py
│   │   │       ├── vote.py
│   │   │       ├── investigate.py
│   │   │       └── role_action.py
│   │   │
│   │   ├── schemas/                        # BOTH — shared contracts
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── game.py
│   │   │   └── events.py
│   │   │
│   │   ├── api/                            # BOTH
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── websocket.py
│   │   │   └── inspector.py
│   │   │
│   │   ├── services/                       # BOTH
│   │   │   ├── __init__.py
│   │   │   ├── event_bus.py
│   │   │   ├── event_store.py
│   │   │   └── replay.py
│   │   │
│   │   └── experiments/                    # BOTH
│   │       ├── __init__.py
│   │       ├── runner.py
│   │       ├── metrics.py
│   │       └── reports.py
│   │
│   ├── data/
│   │   ├── personalities.json
│   │   └── game_config.json
│   │
│   ├── tests/
│   │   ├── test_agents.py                 # P1
│   │   ├── test_memory.py                 # P1
│   │   ├── test_game_engine.py            # P2
│   │   ├── test_permissions.py            # P2
│   │   ├── test_orchestration.py          # P2
│   │   └── test_full_game.py              # Both
│   │
│   ├── pyproject.toml
│   └── .env.example
│
├── frontend/                               # BOTH + CODEX
│   ├── public/
│   │   ├── models/
│   │   │   ├── characters/                  # Licensed models, if used
│   │   │   └── environment/
│   │   └── audio/                           # Cleared audio assets only
│   │
│   ├── src/
│   │   ├── scene/
│   │   │   ├── MafiaScene.tsx              # Both + Codex
│   │   │   ├── MafiaTable.tsx              # Codex-assisted, reviewed
│   │   │   ├── Character3D.tsx             # Both + Codex
│   │   │   ├── CameraController.tsx        # Codex-assisted, reviewed
│   │   │   ├── Lighting.tsx                # Codex-assisted, reviewed
│   │   │   └── AnimationController.ts      # P2 + Codex
│   │   │
│   │   ├── components/
│   │   │   ├── DialoguePanel.tsx           # P2 + Codex
│   │   │   ├── GameHUD.tsx                 # Both
│   │   │   ├── VotingPanel.tsx             # P2 + Codex
│   │   │   ├── AgentInspector.tsx          # P1 + Codex
│   │   │   ├── SuspicionChart.tsx          # P1 + Codex
│   │   │   └── RelationshipGraph.tsx       # P1 + Codex
│   │   │
│   │   ├── hooks/
│   │   │   ├── useGameSocket.ts            # P2
│   │   │   └── useGameState.ts             # Both
│   │   │
│   │   ├── services/
│   │   │   ├── api.ts                       # Both
│   │   │   ├── eventDispatcher.ts          # P2
│   │   │   └── voiceService.ts             # P2 + Codex
│   │   │
│   │   ├── types/
│   │   │   └── generated.ts                # Generated from agreed schema
│   │   │
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── context.md                         # This document if stored here
│   ├── architecture.md
│   ├── agent-contract.md
│   ├── event-contract.md
│   ├── frontend-design.md
│   └── milestones.md
│
├── scripts/
│   ├── run_backend.sh
│   └── run_frontend.sh
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── AGENTS.md
├── .gitignore
└── README.md
```

*Placement:* This delivered file is named `context.md`. In the repository, store it at **`docs/context.md`** and optionally reference it from root `AGENTS.md` and `README.md`.

## 5. Core backend architecture

### 5.1 Separate intelligence, environment, and visualization

```text
                    ┌────────────────────────────────────────┐
                    │ React / React Three Fiber Frontend     │
                    │ 3D game | captions | inspector | replay│
                    └───────────────────┬────────────────────┘
                                        │ HTTP / WebSockets
                    ┌───────────────────▼────────────────────┐
                    │ FastAPI API and event subscriptions    │
                    │ Public state vs authorized inspector   │
                    └───────────────────┬────────────────────┘
                                        │
               ┌────────────────────────▼─────────────────────┐
               │               Orchestrator (P2)               │
               │ phases | turns | communications | tool access │
               └───────────────┬────────────────┬──────────────┘
                               │                │
          ┌────────────────────▼────┐  ┌────────▼────────────────────┐
          │ Agent Intelligence (P1) │  │ Game Engine (P2)           │
          │ personas, LLM, memory,  │  │ canonical state, rules,    │
          │ beliefs, action proposal│  │ validators, win conditions │
          └────────────────────┬────┘  └────────┬────────────────────┘
                               │                │
                ┌──────────────▼────────────────▼───────────────┐
                │ Event bus + persistent game/event snapshots  │
                │ Replays, experiment metrics, debugging       │
                └──────────────────────────────────────────────┘
```

**Important:** Agents are independent *stateful objects*, potentially backed by the same base LLM. They have different private histories, roles, personalities, and objectives. The game engine—not the LLM—holds canonical truth.

### 5.2 Mafia game flow

The initial game should have a clear, finite state machine:

1. `SETUP`: Load characters, assign hidden roles, initialize per-agent isolated state, announce game start.
2. `NIGHT`: Eligible role agents submit private actions. Mafia may privately coordinate according to the rules. Detective may investigate; doctor/protection is optional in later milestones.
3. `DAWN_ANNOUNCEMENT`: Apply validated night results, publish appropriate public consequences, check win conditions.
4. `DAY_DISCUSSION`: Alive agents speak/accuse/defend in bounded turns, using only authorized observations.
5. `VOTING`: Alive agents cast valid votes for eligible targets; ties follow a documented deterministic rule.
6. `VOTE_RESOLUTION`: Apply elimination, announce result, and check win conditions.
7. If neither faction has won, increment round and return to `NIGHT`; otherwise enter `GAME_ENDED`.

Role composition, tie behavior, night-action ordering, what is revealed on elimination, and whether daytime starts before the first night **must be explicit in `game_config.json`**. Do not leave ambiguous rules to agent prompting.

### 5.3 Agent personas affect decisions, not only speaking style

Illustrative persona config:

```json
{
  "agent_id": "comedian_01",
  "display_name": "The Comedian",
  "voice_preset": "original_high_energy",
  "personality": {
    "talkativeness": 0.95,
    "impulsiveness": 0.90,
    "aggressiveness": 0.75,
    "analytical": 0.25,
    "loyalty": 0.40
  }
}
```

The real effect of these traits must be tested empirically. Examples:

- High talkativeness: more/longer speaking attempts, within global turn/token limits.
- High impulsiveness: greater tendency to form early accusations or change stance on limited evidence.
- High analysis: stronger reliance on recorded voting history and contradictions.
- High loyalty: greater tendency to defend allied or trusted players (without overriding actual role objectives).

The trait system may influence prompt construction, decision policy, or candidate action scoring. **Never assume a numeric persona prompt automatically causes measurable behavior.** Run repeated controlled experiments.

### 5.4 Memory and beliefs

- **Short-term conversation memory:** recent dialogue and actions in the current round.
- **Episodic history:** important prior accusations, votes, claims, contradictions, investigations, eliminations.
- **Belief state:** agent-local trust and suspicion scores, supporting evidence, confidence or uncertainty, target identities, and last-update event IDs.

Agent-local memory is not the same as global event history. Agents receive a filtered view of the event stream. A private event should be unavailable to an unauthorized agent even through a supposedly innocuous memory tool.

At first, store memory in bounded lists/dictionaries and event references. Add summarization or retrieval optimization only if context length or performance actually requires it.

Directional relationships are important: A trusting B does **not** imply B trusts A.

Belief and suspicion estimates in the dashboard represent the agent's own declared/structured state, **not privileged access to the model's hidden chain of thought**. Do not imply that an LLM's internal reasoning is faithfully exposed.

### 5.5 Agent tools and validated action types

The UI form previously listed the following agent-level capabilities:

| Conceptual tool/action | Intended behavior | Permission principle |
|---|---|---|
| `speak(message, target?)` | Public statement, question, accusation, defense | Alive players during discussion |
| `cast_vote(target)` | Cast phase-appropriate vote | Alive players, one valid vote per voting opportunity |
| `investigate(target)` | Detective investigation request/result | Detective role during permitted night phase |
| `submit_night_action(target)` | Mafia or other role night action | Matching role and phase only |
| `get_public_history()` | Review visible prior game events | Anyone eligible, public data only |
| `get_memory()` | Retrieve agent-local recorded memories | Only the calling agent's state |

These may be implemented as **validated structured actions** instead of direct model tool calls. The abstraction matters more than the exact SDK mechanism. The tool registry enforces agent identity, role, phase, allowed target, and state transitions.

No LLM response may be trusted merely because it says that an action is authorized. The orchestrator must validate it against authoritative state.

### 5.6 Communication channels and privacy

| Channel | Audience | Typical content |
|---|---|---|
| Public discussion | All eligible players and public game view | Dialogue, accusations, announcements |
| Mafia private coordination | Mafia members only | Private negotiation and night strategy |
| Detective private result | The relevant detective | Investigation outcome |
| Game authority | Game engine/orchestrator | True roles, all private states, correct results |
| Developer inspector | Authorized developer/demo view only | Hidden truth, agent beliefs, internal logs |

Security boundaries to enforce:

- Construct recipient-specific `AgentObservation` objects; never send raw game state and merely ask the LLM to ignore restricted fields.
- Do not broadcast private roles, Mafia chat, or detective results over the public WebSocket.
- An inspector mode **must have explicit local developer authorization**. It can be built as a local dev-only feature initially; if deployed publicly, add real authentication/authorization rather than relying only on a hidden button.
- Keep model API keys server-side, in ignored environment files, not in frontend JavaScript or event logs.
- Do not expose private prompt data as unrestricted client state.

## 6. Shared contracts — decide before parallel coding

Use Pydantic for Python models; derive corresponding frontend TypeScript types from an API schema or maintain a carefully versioned definition. Avoid loosely related handwritten types on each side.

### 6.1 Input to an agent: `AgentObservation`

Representative outline (adjust as necessary in shared design review):

```python
from pydantic import BaseModel, Field

class AgentObservation(BaseModel):
    agent_id: str
    round_number: int
    phase: str
    own_role: str
    public_events: list[dict] = Field(default_factory=list)
    private_messages: list[dict] = Field(default_factory=list)
    alive_player_ids: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
```

The observation must be created by `observation_builder.py`. It contains only the recipient's authorized information. For example, a Mafia player may receive teammate identities privately while an ordinary citizen cannot. The `own_role` is private to the recipient. When specific private state is needed, model it explicitly rather than silently smuggling it through `public_events`.

### 6.2 Output from an agent: `AgentAction`

```python
from pydantic import BaseModel

class AgentAction(BaseModel):
    agent_id: str
    action_type: str
    message: str | None = None
    target_agent_id: str | None = None
    emotion: str | None = None
    intensity: float | None = None
```

This is a **proposed action**, not proof that the action is legal. Validate against role, phase, permissions, and alive targets. Clamp or validate `intensity` to a documented 0–1 range. As implementation matures, use discriminated unions or enums (`SpeakAction`, `VoteAction`, `InvestigateAction`, etc.) so each action has exactly the fields it requires.

### 6.3 Agent decision interface

```python
class MafiaAgent:
    async def decide(self, observation: AgentObservation) -> AgentAction:
        # Retrieve only this agent's memory and beliefs.
        # Generate a personality-conditioned next action.
        # Parse the model output into a validated action schema.
        # DO NOT mutate authoritative game state.
        ...
```

Person 1 implements this interface. Person 2 invokes it using test/mocked agents until the real implementation is available. Both own its schema changes.

### 6.4 Example agent decision payload

```json
{
  "agent_id": "detective_02",
  "action_type": "speak",
  "message": "Why did you change your vote?",
  "target_agent_id": "comedian_01",
  "emotion": "suspicious",
  "intensity": 0.7
}
```

Belief updates may be returned as a distinct structured field or generated within the agent intelligence subsystem and separately recorded as privileged inspector events. **Do not attach private belief updates to publicly broadcast speech payloads.**

## 7. Backend → frontend event architecture

The frontend needs **structured, timestamped, ordered game events**, not just transcript strings. Person 2 publishes events after authoritative validation. Person 1 provides agent state/belief snapshots through a controlled private channel.

### 7.1 Public event example

```json
{
  "event_id": 37,
  "game_id": "demo-game-001",
  "type": "AGENT_SPEECH",
  "round": 2,
  "phase": "discussion",
  "visibility": "public",
  "payload": {
    "agent_id": "comedian_01",
    "text": "Why are you accusing me?",
    "emotion": "angry",
    "intensity": 0.85,
    "target_agent_id": "detective_02"
  }
}
```

The event system should include stable `game_id`, monotonic per-game `event_id`, an unambiguous event type, phase/round identifiers, visibility/audience, and a typed payload. Include creation timing if needed, but use sequence IDs—not wall-clock timestamps—as the replay ordering authority.

### 7.2 Planned event types

| Event | Public/game UI reaction | Visibility |
|---|---|---|
| `GAME_STARTED` | Initialize characters, seat assignments, and UI | Public-safe data only |
| `PHASE_CHANGED` | Transition day/night lighting and HUD | Public-safe phase information |
| `AGENT_SPEECH` | Focus camera; speaking animation, captions, voice | Public if public dialogue |
| `AGENT_EMOTION` | Change facial expression/gesture | Depends on conversation visibility |
| `VOTE_CAST` | Display vote action when rules allow it | Public or hidden until reveal, per rules |
| `VOTING_COMPLETED` | Animate tally and result | Public |
| `PLAYER_ELIMINATED` | Change seat/player state | Public result; role revelation rule-dependent |
| `BELIEF_UPDATED` | Refresh private agent inspector | Inspector / authorized audience only |
| `RELATIONSHIP_UPDATED` | Update directed trust/suspicion graph | Inspector / authorized audience only |
| `GAME_ENDED` | Show winner and final result | Public |

**Important:** Public game animation must not reveal secret information via unintended effects. For example, private Mafia speech should not light up a character on the normal spectator view unless the scene is deliberately displaying a privileged perspective.

### 7.3 How a speech event drives the scene

```text
Agent decides to speak (P1)
        ↓
Orchestrator validates action and records event (P2)
        ↓
FastAPI WebSocket sends public AGENT_SPEECH event
        ↓
Frontend eventDispatcher / React state
        ├─ CameraController focuses current speaker
        ├─ Character3D begins gesture/speaking animation
        ├─ DialoguePanel shows caption
        └─ voiceService plays permitted original synthetic voice
```

The frontend should not perform game-rule calculations. It simply presents the server's validated events. For resilience, let the UI recover from a refreshed game snapshot when it reconnects.

### 7.4 Event stores and replay

Record canonical events to JSONL, and save occasional authoritative snapshots. Keep public and restricted events classified so a public replay cannot accidentally reveal inspector-only information.

Example event trace:

```text
001 GAME_STARTED
002 PHASE_CHANGED
003 AGENT_SPEECH
004 AGENT_SPEECH
005 BELIEF_UPDATED        [inspector only]
006 VOTE_CAST
007 VOTE_CAST
008 VOTING_COMPLETED
009 PLAYER_ELIMINATED
...
```

Replay is **not a luxury feature**. It allows:

- Frontend development without spending tokens on live LLM calls.
- Pause/resume/step-through analysis.
- Debugging inconsistent decisions and belief updates.
- Reproducing a club presentation if an API or network connection fails.
- Comparing experiments across configurations.

Start with mock event fixtures. A replay viewer can render the same recorded game multiple times, with playback speed controls added later.

## 8. Frontend specification

### 8.1 High-level design: hybrid 3D + 2D

Use **3D for the spectacle** and **2D UI for clarity**:

- **3D:** circular Mafia table, 5–10 seats, stylized expressive original characters, dark room/environment, dramatic lighting, camera focus, simple gestures, day/night transitions.
- **2D overlay:** subtitles, narrator announcements, vote status/tallies, alive/eliminated indicators, pause/replay, current phase/round.
- **2D Inspector:** belief charts, personality sliders/readouts, evidence list, episodic memory snippets, relationship graph, prior actions, and game truth (clearly labeled and restricted).

Design for a **desktop demo / projector**, with readable captions and a stable layout. Mobile responsiveness is optional initially.

### 8.2 Cinematic Spectator Mode

At any moment, audience should understand:

- What round and phase it is (day, discussion, vote, night, results).
- Which characters are still alive.
- Which character is speaking, whom they're addressing, and what they said.
- Current public voting progress/results where permitted.
- Major eliminations and winners.

Desired presentation behaviors:

1. Camera focuses on the current speaker, with smooth transitions.
2. Speaking character has an animation state such as `idle`, `speaking`, `accusing`, `defending`, `voting`, `eliminated`.
3. Emotion labels/intensity map into visible expressions or gestures only to the extent supported by character assets.
4. Dialogue appears with captions; optional TTS uses unique, original voices.
5. Night phases shift scene lighting; narrator announces events without dictating agent decisions.
6. Eliminated players visually change state while staying understandable to the audience.
7. Presenter can pause, resume, skip audio, and replay prior segments.

Character models do **not** need to be photorealistic. Start with stylized placeholder geometry or licensed rigged assets. Codex can generate scene graph code, geometry, animations, camera choreography, and event wiring; it should not be assumed to automatically produce polished, complex professional models with facial rigs. Sophisticated facial animation and lip-sync are later enhancements.

### 8.3 AI Intelligence Inspector

Use an explicit inspector mode separate from the normal cinematic game. It may reveal hidden roles and agent-private beliefs *only to authorized developers/presenters*.

For a selected agent, show:

1. **Identity/personality:** profile, traits, role (restricted), speaking style.
2. **Current belief state:** directional suspicion, trust, confidence, and evidence references.
3. **Memory:** significant remembered statements, voting patterns, contradictions, and investigation results permitted to that agent.
4. **Current objective or proposed next action:** structured agent-reported intent, not purported hidden reasoning.
5. **History over time:** how beliefs and relationships changed across rounds.
6. **Ground truth comparison:** actual roles clearly labeled as authoritative game state, not agent beliefs.

Do not misrepresent LLM self-reported explanations as full access to model internal reasoning. Store explicit summaries/evidence and action metadata for explainability.

### 8.4 Relationship graph

- Nodes: individual AI characters.
- Edges: **directed** trust, suspicion, alliance, or interaction data.
- Edge direction matters; two agents can disagree about each other.
- Offer a selected-agent view and optional round/time selection.
- Differentiate inferred/agent-reported relationships from factual role membership.
- Make it possible to compare earlier and later rounds to see alliance formation, betrayal, and deception effects.

### 8.5 Suggested React component responsibilities

| File | Purpose | Primary owner |
|---|---|---|
| `MafiaScene.tsx` | Composes full 3D scene | Both + Codex |
| `MafiaTable.tsx` | Table geometry, seats, static props | Codex-assisted / both review |
| `Character3D.tsx` | Renders and animates a character | Both + Codex |
| `CameraController.tsx` | Smooth camera focus/transitions | Codex-assisted / both review |
| `Lighting.tsx` | Phase-sensitive lighting | Codex-assisted / both review |
| `AnimationController.ts` | Maps game events to animation commands | P2 + Codex |
| `DialoguePanel.tsx` | Captions/current speaker | P2 + Codex |
| `GameHUD.tsx` | Phase, round, live count, playback status | Both |
| `VotingPanel.tsx` | Vote visualization | P2 + Codex |
| `AgentInspector.tsx` | Selected agent memory/beliefs/role | P1 + Codex |
| `SuspicionChart.tsx` | Suspicion estimates and trends | P1 + Codex |
| `RelationshipGraph.tsx` | Directed social graph | P1 + Codex |
| `useGameSocket.ts` | Public event WebSocket and reconnect | P2 |
| `useGameState.ts` | Derived client game presentation state | Both |
| `api.ts` | HTTP requests, snapshots, inspector access | Both |
| `eventDispatcher.ts` | Translates events to UI actions | P2 |
| `voiceService.ts` | Original TTS audio playback and coordination | P2 + Codex |

### 8.6 Voice architecture

Voice is a **presentation layer**, not the definition of personality intelligence. A character's decision-making and generated dialogue must work without audio. The voice service should receive approved dialogue and an original voice preset, generate or load audio, and report playback status to the visual layer. Handle delays, skipped audio, interruption, and subtitle-only fallback gracefully.

Avoid unauthorized voice cloning, impersonation, or models intended to mimic identifiable celebrities. Use unique synthetic voices with appropriate rights/consent.

## 9. Cross-team interface and integration ownership

### Contract 1: Orchestrator → Agent

`decide(observation: AgentObservation) -> AgentAction`

- **P2** builds a least-privilege observation and supplies permitted actions.
- **P1** returns a structured proposed action.
- **P2** validates/executes/rejects it and records canonical events.
- **P1** updates its own private memory and beliefs based on authorized observations and results.

### Contract 2: Backend → Frontend

`GameEvent` stream + snapshot API + restricted inspector API.

- **P2** owns authoritative event ordering, game phase transitions, and public streaming.
- **P1** owns structured agent-specific belief/memory data that the inspector can display.
- **Both** agree on schema, visibility boundaries, JSON examples, and type generation.

### Contract 3: Event → 3D scene

Each public event should have a deterministic visual reaction. For example:

| Event | Triggered visual response |
|---|---|
| `AGENT_SPEECH` | Focus speaker, gesture, caption, optional voice |
| `AGENT_EMOTION` | Expression/gesture change |
| `PHASE_CHANGED` | Lighting and HUD transition |
| `VOTE_CAST` | Character vote indicator |
| `VOTING_COMPLETED` | Tally animation |
| `PLAYER_ELIMINATED` | Eliminated character style |
| `GAME_ENDED` | Winners and game summary |

The scene must be able to consume fixtures/recorded events without any live LLM backend. This is the first major Codex 3D task.

## 10. Testing, reliability, and research

### 10.1 Unit tests — Person 1

- Valid agent creation from persona config.
- Agent memory isolation (no state shared between instances unless intentional).
- Correct handling of relevant older information.
- Belief update logic for new evidence.
- Agent output parsed into valid schema.
- Robust handling of invalid or missing LLM outputs.
- Behavior comparison across persona configurations (as an experiment, not a hard-coded expectation that prompts always obey scores).

### 10.2 Unit tests — Person 2

- Role assignment and initial state validity.
- Phase transitions and win conditions.
- Votes limited to alive/eligible targets.
- Correct handling of tie rules.
- Night actions restricted by role and phase.
- No public/private observation leakage.
- Mock agents can play a complete game.
- Invalid actions/timeouts cannot permanently stall simulation.
- Event IDs and replay order are stable.

### 10.3 Shared tests

- End-to-end five-agent simulation with real model provider configuration.
- Deterministic seeded mock-game replay.
- API response and TypeScript schema compatibility.
- Public WebSocket never leaks private inspector state.
- Frontend can render a complete fixture game without the backend running.
- Disconnect/reconnect and snapshot recovery.
- Scene animation and captions remain synchronized under delayed audio.

### 10.4 Experimental questions

After the MVP, run repeated trials to explore:

- Do high-impulsiveness agents receive more votes or get eliminated more often?
- Do quieter deceptive agents survive longer?
- Does persistent memory improve detection or logical consistency?
- Do analytical agents detect contradictions more accurately?
- Do alliances form between certain traits or roles?
- Do confident agents influence group voting more than less assertive agents?
- How often do belief states move closer to or farther from the actual Mafia roles?

Track win rates, false accusations, successful detections, voting accuracy, contradictions, latency, cost, and simulation failures. Use multiple runs and, where feasible, repeated seeds/configurations. **Do not manufacture quantitative results**; the example percentages displayed in UI mockups are illustrative only.

## 11. Four-week milestone plan

This is an **ambitious four-week student-team target**, not a guaranteed delivery timeline. Adjust based on actual time, API budget, and the complexity of rigged 3D models.

### Week 1 — Foundations

**Person 1**

- Implement base agent interface and basic LLM client.
- Define three starter personas.
- Implement memory as a simple local store.
- Test decision output against mock observations.

**Person 2**

- Build deterministic game engine and state machine.
- Implement setup, phases, public discussion, basic voting, and win conditions.
- Build observation filtering.
- Complete a game using deterministic mock agents.

**Both**

- Agree on Pydantic contracts and ownership.
- Set up GitHub repository, branches, tests, and working commands.
- Have Codex build an isolated 3D table with eight placeholder seats/characters and fake speech events.

**Acceptance:** mock five-player game completes; a 3D mock frontend can independently play fake speech events.

### Week 2 — Agentic game integration

**Person 1**

- Expand memory and belief state.
- Build personality-conditioned decision prompts/policies.
- Implement contradiction/history awareness.
- Implement Detective agent investigation behavior.

**Person 2**

- Connect real agents to the orchestrator.
- Implement private Mafia coordination and role tools.
- Add action validation, retry/failure handling, and event logging.
- Produce first canonical replay file.

**Both**

- Run a full five-agent LLM game.
- Test private communication boundaries.
- Connect replayed dialogue to 3D characters and captions.

**Acceptance:** a full, valid, replayable game runs using five LLM agents.

### Week 3 — Scale and visualize

**Person 1**

- Improve directional beliefs and relationships.
- Explore memory summarization if context requires it.
- Add private inspector state snapshots.
- Begin controlled personality experiments.

**Person 2**

- Expand to eight agents if stability permits.
- Add FastAPI WebSockets and event subscriptions.
- Measure latency; optimize safe asynchronous scheduling.
- Verify no secret state reaches public stream.

**Both**

- Integrate full 3D gameplay and event animation.
- Build Inspector, suspicion chart, and relationship graph.
- Add optional unique synthetic character voices.

**Acceptance:** coherent eight-agent game visualization and a working Inspector showing meaningful backend state; scaling may be deferred if reliability is not yet sufficient.

### Week 4 — Evaluation, polish, presentation

**Person 1**

- Run personality and memory comparisons.
- Report suspicion behavior and decisions.
- Document agent intelligence design and limitations.

**Person 2**

- Test full-game correctness, privacy, failures, and replay.
- Measure model latency and API usage.
- Document orchestration tradeoffs and architecture.

**Both**

- Improve camera movements, lighting, gestures, voice timing, and captions.
- Add presenter pause/skip/replay controls.
- Prepare a recorded backup game and a brief demo walkthrough.
- Present both the entertainment experience and the underlying agentic system.

**Acceptance:** repeatable club demo with a technically grounded explanation of multi-agent behavior and limits.

### Scope tiers

**Must-have MVP**

- Five distinct autonomous agents.
- Deterministic Mafia rules and valid role permissions.
- Separate memories and private observations.
- Speech, vote, and basic nighttime actions.
- Event log + replayable mock fixture.
- Basic 3D scene with speaking focus/captions.

**High-value next steps**

- Eight to ten agents.
- Directional beliefs and Inspector.
- Relationship graph.
- Distinct synthetic voices.
- Stronger personality differentiation.
- Cinematic voting and day/night transitions.

**Optional stretch goals**

- Fully rigged facial expressions and lip-sync.
- More complex 3D environment.
- Human audience player mode.
- Sophisticated agent frameworks or retrieval architecture.
- Public deployment and authenticated multiple viewers.

## 12. Starting task checklist

1. [ ] Agree on `AgentObservation`, `AgentAction`, and `GameEvent` schemas (**Both**).
2. [ ] Implement one configurable LLM Mafia agent (**P1**).
3. [ ] Implement basic per-agent memory (**P1**).
4. [ ] Create deterministic Mafia state machine (**P2**).
5. [ ] Create turn manager, voting, and private observation filtering (**P2**).
6. [ ] Complete a game with five mock agents (**Both**).
7. [ ] Complete a game with five LLM agents (**Both**).
8. [ ] Use Codex to create an eight-seat procedural 3D Mafia table with placeholder characters (**Both + Codex**).
9. [ ] Render a recorded mock event stream with camera focus, animation, and captions (**Both + Codex**).
10. [ ] Add restricted inspector snapshots, belief charts, and replay controls (**Both**).

The **first complete vertical slice** should be: one valid agent speech event produced by an agent, validated by the orchestrator, recorded in the event log, delivered to the frontend, and rendered with camera focus plus a caption. Once that works, repeat the pattern for vote, phase transition, elimination, and inspector state.

## 13. Documentation to maintain

- `docs/context.md` — This high-level product/architecture/ownership specification.
- `docs/architecture.md` — Actual implemented architecture, updated as code changes.
- `docs/agent-contract.md` — Exact agent observations/actions and role knowledge policies.
- `docs/event-contract.md` — Exact event formats, public/private visibility, and replay semantics.
- `docs/frontend-design.md` — 3D visual direction, component states, animations, accessibility, and captions.
- `docs/milestones.md` — Task ownership, acceptance criteria, and done/blocked status.
- `AGENTS.md` — Short, operational instructions for Codex: repo map, build/test commands, architecture boundaries, and reference to this document.
- `README.md` — Setup, environment variables, local run instructions, developer workflow, and demo guide.

At each milestone, update documentation to match reality. Do not leave the spec implying a planned module has been built.

## 14. Architectural principles and practical pitfalls

1. **Game rules are deterministic.** The LLM cannot invent win conditions, eliminated players, secret revelations, or outcomes.
2. **Every agent is independent.** Unique identity, role, observation, memory, and beliefs—even when sharing an LLM provider.
3. **No hidden-state leakage.** Enforce public versus private channels in code and tests.
4. **Agent intelligence is observable through structured data, not hidden thought traces.** Store stated evidence, beliefs, actions, and explanations as deliberate outputs.
5. **Use bounded dialogue.** Eight to ten agents speaking without limits will increase latency, token cost, and demo length.
6. **Concurrency is selective.** Simultaneous independent votes may be parallelized; turn-dependent public conversations must preserve information order.
7. **Audio should never block game logic indefinitely.** Provide text-first and muted fallback.
8. **Recorded games are a first-class test asset.** Keep sample fixtures for animations and debugging.
9. **Visual design should explain the backend.** Don't build visual effects requiring data the agents never produce.
10. **Avoid premature model fine-tuning, vector databases, and complex agent frameworks.** Build and validate the behavioral system first.
11. **Keep model/provider secrets in the backend.** Use `.env.example`; ignore `.env` files and generated private logs.
12. **Respect voice, model, and asset permissions.** Original character designs and consented/licensed audio are the default.
13. **Own the code despite AI assistance.** Both developers should be able to explain and modify their own modules.
14. **Keep UX readable.** Projector-friendly captions, clear status indicators, animation restraint, and controlled camera motion matter more than raw polygon count.
15. **Define completion in testable terms.** Every feature should have behavior/acceptance criteria, not only a screenshot.

## 15. Specific next Codex task to request

**Do not prompt Codex to build the entire platform at once.** Begin with one of these tasks, depending on what you want to start:

**Option A — Shared backend foundations**

> Read `docs/context.md`. Inspect the existing repo. Implement only the minimum Python project scaffolding and Pydantic contracts for `AgentObservation`, `AgentAction`, and `GameEvent`, plus a short `docs/agent-contract.md` describing role-specific visibility. Add schema tests and a README snippet showing how to run them. Do not implement LLM agents, full Mafia rules, or frontend yet. List assumptions and propose the next separate tasks for Person 1 and Person 2.

**Option B — Frontend visual proof of concept**

> Read `docs/context.md`. Create a minimal React + TypeScript + React Three Fiber frontend prototype showing a stylized Mafia table with eight placeholder original characters. Provide a mock event player that cycles through `AGENT_SPEECH`, `PHASE_CHANGED`, and `VOTE_CAST` events. Make the camera focus on the speaking character, display readable captions, and adjust lighting for day/night. No backend or model API integration yet. Keep the code modular and document how to run it.

**Recommended order:** First jointly agree on schemas, then let Person 1 and Person 2 proceed independently using mocks, while Codex helps prototype the 3D scene against the same event contract.

---

## 16. Definition of project success

The project succeeds when an IEEE audience can watch **unscripted, independent AI agents** complete a rules-correct Mafia game, understand how agent personalities and memories affect choices, and switch to an **Inspector** to analyze how beliefs, accusations, alliances, and decisions evolve—while both teammates can clearly explain the intelligence and orchestration components they personally built.

**Build an intelligent system first; make its intelligence visible and entertaining through the 3D presentation.**
