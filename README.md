# AI Mafia
Two-person autonomous Mafia project. Person 1 owns agent intelligence; Person 2 owns orchestration. See [architecture](docs/architecture.md), [project context](docs/context.md), and [milestones](docs/milestones.md).

## Backend
From repository root:
```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e './backend[dev]'
cd backend
../.venv/bin/python -m pytest
../.venv/bin/python -m app.experiments.runner
```
The runner requires no API key, outputs a winner and saves a public replay under backend/data/replays. It uses deterministic mock decisions, not LLM intelligence. Canonical/private logs are not persisted by default. To launch the health API from root: `bash scripts/run_backend.sh`; visit http://127.0.0.1:8000/health.

## Frontend
```sh
cd frontend
npm install
npm run dev
```
`npm run build` checks TypeScript and builds the status shell. Named components are placeholders; no 3D or live game UI is implemented yet.

## Working together
Review the proposed contracts together before integration. Use separate feature branches and peer-reviewed PRs. Keep keys in backend/.env (ignored); .env.example documents optional provider fields. No provider is integrated yet. Never commit restricted game logs. See AGENTS.md for operational boundaries.
