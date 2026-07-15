## Commands
```bash
python main.py                          # run FastAPI + GraphQL app (mounted at /gql)
pytest                                   # tests, dir set by pytest.ini
bash .alembic.sh "message"               # autogenerate + apply migration
alembic upgrade head                     # apply migrations only
```
requirements.txt = source of truth. Pipfile/Pipfile.lock removed from repo (git status shows deletion) — do not regenerate them, do not use pipenv despite README claim.

## Environment
DB mode picked via `MODE` env var (`development` / `testing` / `production`), see `app/database/database.py`. Each mode reads separate DB/user/password vars (`DEV_*`, `TEST_*`, `PROD_*`). `.env` loaded via `python-dotenv`. Never commit real `.env` values.

## Sensitive Areas
- `app/graphql/schema.py` — GraphQL schema. Any field/type/arg/mutation change breaks bot's queries (separate repo). Always write diff + plain description of change alongside edit. Never skip, even small change.
- `alembic/` migrations — never edit existing migration files; always generate new one.

## Conventions Not Enforced by Tooling
- Custom scalars `Snowflake` (ID as int/str) and `JSON` defined in `app/graphql/schema.py` — reuse these, don't redefine.
- Resolvers live in `app/graphql/resolvers/resolver.py`, imported as `resolve` — schema types call into this, not inline DB queries.

## Architecture Decisions
- Strawberry GraphQL library (not graphene/ariadne) — schema built with `strawberry.type`/`strawberry.mutation` decorators, not SDL-first.
- SQLAlchemy models under `app/database/models/`; `BaseModel.metadata.create_all(engine)` runs at import of `main.py` — no separate init-db step needed for dev.
- Recent commits removed `last_act_server` from `MemberShard` — check current `member_shard.py` before assuming old field names still exist.

## Workflow Rules
- Never implement/refactor unless user explicit ask. Question in, answer only, for schema/query analysis tasks.
- No refactor of working schema/resolver code without asking first, even if better structure obvious.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
