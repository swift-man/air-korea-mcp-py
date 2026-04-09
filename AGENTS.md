# AGENTS.md

This repository hosts a Python MCP server for the Air Korea public API.

## Product Scope

- Support Streamable HTTP MCP only.
- Do not reintroduce `stdio`, `sse`, or transport-selection features unless explicitly requested.
- Keep the public MCP surface focused on Air Korea data retrieval tools and the reference resource.

## Architecture

Follow SOLID boundaries when making changes.

- `src/air_korea_mcp/server.py`
  - MCP registration and process startup only.
  - Keep tool handlers thin.
  - No request building, validation, or response parsing here.

- `src/air_korea_mcp/bootstrap.py`
  - Composition root only.
  - Build settings, gateway, and service objects.

- `src/air_korea_mcp/service.py`
  - Application/use-case layer.
  - Validate inputs, normalize arguments, and delegate to the gateway.
  - Depend on abstractions such as `AirKoreaGateway`, not concrete transport details.
  - If a tool needs smarter user-input handling, delegate that logic to a focused helper module instead of growing this file indiscriminately.

- `src/air_korea_mcp/gateway.py`
  - External API boundary.
  - Own HTTP calls, response decoding, and API payload normalization.

- `src/air_korea_mcp/settings.py`
  - Environment/config loading only.

- `src/air_korea_mcp/runtime.py`
  - Streamable HTTP runtime config only.

- `src/air_korea_mcp/validation.py`
  - Shared validation helpers only.

- `src/air_korea_mcp/reference.py`
  - Static/reference payload construction only.

- `src/air_korea_mcp/location_resolution.py`
  - Resolve user-facing region aliases and lower-level administrative names into Air Korea `sidoName` values.
  - Keep ambiguity handling and normalization here, not in `service.py` or `server.py`.

- `src/air_korea_mcp/location_index_data.py`
  - Generated snapshot data only.
  - Do not hand-edit business rules here.
  - If the administrative dataset changes, regenerate the snapshot instead of mixing manual fixes into the generated file.

## Change Rules

- Prefer extending the service and gateway layers over adding logic to MCP tool functions.
- If a new feature needs different infrastructure concerns, introduce a new module instead of overloading an existing one.
- Keep error messages user-facing and actionable.
- Preserve backward-compatible imports when practical, especially around `client.py`.
- Avoid framework-heavy abstractions. Use small, explicit interfaces and dataclasses.
- Keep SOLID boundaries explicit:
  - SRP: one module, one kind of responsibility.
  - OCP: prefer adding a new helper or adapter over stacking conditionals into existing layers.
  - DIP: high-level workflows should depend on protocols or simple interfaces where practical.

## Runtime Rules

- `scripts/run_http.sh` is the supported launch path for local and deployed usage.
- `deploy/systemd/air-korea-mcp.service.example` should remain aligned with `scripts/run_http.sh`.
- `.env.example` must reflect the actually supported runtime variables.
- A change to `AGENTS.md` does not require restarting the MCP server by itself.
- If `AGENTS.md` changes, restart the coding-agent session or client so the new instructions are picked up.

## Restart Guidance

- If runtime code, service code, environment-variable handling, or dependency wiring changes, surface the restart commands in the response.
- For deployed Linux/systemd usage, prefer showing this sequence:

```bash
cd /home/jiniopening/air-korea-mcp-py
git pull
source .venv/bin/activate
pip install -e .
sudo systemctl restart air-korea-mcp
sudo systemctl status air-korea-mcp
journalctl -u air-korea-mcp -n 50 --no-pager
```

- If only `AGENTS.md` changed, do not tell the user to restart the MCP server.
- If only `AGENTS.md` changed, tell the user to restart the coding-agent session or client instead.

## Testing

Run these after meaningful changes:

```bash
bash -n scripts/run_http.sh
python3 -m compileall src tests
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Docs

- Update `README.md` when changing runtime behavior, environment variables, or deployment steps.
- Keep examples aligned with Streamable HTTP at `http://127.0.0.1:8000/mcp` unless the default changes.
