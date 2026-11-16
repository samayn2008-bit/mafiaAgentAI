# AI Mafia working instructions
Read docs/context.md and docs/architecture.md before implementation. The context is a plan, not implemented status.
User is Person 2. P1 owns backend/app/agents; P2 owns backend/app/orchestration. Schemas, API, services, frontend and docs are shared. Changes to contracts require teammate review.
Agents propose actions; only deterministic engine/orchestrator code mutates canonical state. Never expose raw GameState to clients or agents. Public streams/replays must filter restricted events. Inspector is unimplemented; do not expose it without authorization controls.
Commands: create root .venv; install backend editable with dev extras. From backend run ../.venv/bin/python -m pytest and ../.venv/bin/python -m app.experiments.runner. Frontend: npm install, npm run build.
Keep scope narrow, preserve working code, and clearly identify placeholders. Do not add LLM providers, assets, or frameworks without a task requiring them.
