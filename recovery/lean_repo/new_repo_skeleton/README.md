# Lean MatGraph Extraction Skeleton

This scaffold defines target package boundaries for the new clean repository focused on importing and matching runtime paths.

## Target boundaries

- `src/api/importing`: API layer for ingestion/extraction endpoints.
- `src/api/matching`: API layer for workflow extraction endpoint.
- `src/domain/process`: Process lifecycle models and status transitions.
- `src/domain/graph_ingest`: Ingestion/extraction business logic.
- `src/infra/tasks`: Background task orchestration and callback delivery.
- `src/infra/neo4j`: Graph persistence/query adapters.
- `src/optional/reporting`: Optional HTML/report persistence features.

## Migration order

1. Port process/status enums and callback contract from current `tasks` app.
2. Port importing endpoint contracts and task dispatch orchestration.
3. Port matching endpoint contracts and matcher orchestration.
4. Port graph ingestion pipelines (label -> attribute -> node -> graph -> import).
5. Add end-to-end parity tests with golden fixtures.
6. Move reporting to optional package and disable by default.

## Source of truth

Use the module inventory and checks in:
- `recovery/lean_repo/module_manifest.yaml`
- `recovery/lean_repo/check_manifest_paths.py`

## Current guardrails in this repository

- API contract tests:
  - `importing/tests.py`
  - `matching/tests.py`
- Task/callback contract tests:
  - `tasks/tests.py`
