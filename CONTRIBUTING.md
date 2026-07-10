# Contributing to CodeAtlas

Keep changes within the active milestone and preserve the documents in `docs/`.

## Development

- Backend: `cd backend`, `pip install -e ".[dev]"`, then `uvicorn app.main:app --reload`.
- Frontend: `cd frontend`, `npm install`, then `npm run dev`.
- Quality checks: run `black .`, `ruff check .`, and `isort .` in `backend`; run
  `npm run lint`, `npm run test`, and `npm run build` in `frontend`.

Install the hooks with `pre-commit install` after installing pre-commit.
