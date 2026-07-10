# CodeAtlas

CodeAtlas is a repository-intelligence platform. This repository currently contains
Milestone 1 only: the API foundation, database wiring, and frontend shell.

## Run locally

1. Start PostgreSQL with a `codeatlas` database. Development defaults are in
   `.env.example`; copy it to `.env` to override them.
2. In `backend`, install Python 3.12 dependencies with `pip install -e ".[dev]"`,
   then run `uvicorn app.main:app --reload`.
3. In `frontend`, run `npm install` and `npm run dev`.

Open `http://localhost:8000/docs`, `http://localhost:8000/api/v1/health`, and
`http://localhost:5173`.

## Verification

Run `pytest` from `backend` and `npm run test`, `npm run lint`, and `npm run build`
from `frontend`.
