# TurbinControl

A wind turbine monitoring and control system built as a Python prototype. Exposes a REST API and is structured around Domain-Driven Design (DDD) principles.

---

## Setup

**Prerequisites:** Python 3.11+

```bash
# Clone / navigate to the project
cd TurbinControl

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The API is available at `http://localhost:8000`.  
Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

---

## Architecture & Design

### Domain-Driven Design

The system is split into two bounded contexts. Each context owns its domain model independently — they share only a thin **shared kernel** (`TurbineId`).

```
┌─────────────────────────────────────────────────────────────┐
│                        REST API Layer                        │
│          /monitoring/*             /control/*               │
└────────────────┬───────────────────────┬────────────────────┘
                 │                       │
   ┌─────────────▼──────────┐  ┌────────▼───────────────┐
   │   Monitoring Context   │  │    Control Context      │
   │                        │  │                         │
   │  TurbineReading        │  │  Turbine (aggregate)    │
   │  Alert                 │  │  ControlCommand         │
   │  AlertRule             │  │  TurbineState           │
   │  MonitoringService     │  │  ControlService         │
   └─────────────┬──────────┘  └────────┬────────────────┘
                 │                       │
                 └──────────┬────────────┘
                            │
                   ┌────────▼────────┐
                   │  Shared Kernel  │
                   │   TurbineId     │
                   └─────────────────┘
```

### Layer structure (per context)

```
<context>/
├── domain/
│   ├── value_objects.py   # Immutable types with invariant validation
│   ├── entities.py        # Entities and aggregate roots
│   ├── events.py          # Domain events
│   └── repositories.py    # Abstract repository interfaces
├── application/
│   └── services.py        # Use-case orchestration
└── infrastructure/
    └── repositories.py    # In-memory repository implementations
```

### Monitoring bounded context

Responsible for ingesting sensor readings and triggering alerts.

**Key types:**

| Type | Kind | Description |
|---|---|---|
| `TurbineReading` | Entity | A timestamped snapshot of sensor data for a turbine |
| `Measurements` | Value object | Wind speed, power output, rotor RPM, nacelle temperature, vibration level |
| `WindSpeed`, `PowerOutput`, etc. | Value objects | Single-metric wrappers that validate their own constraints |
| `AlertRule` | Entity | A configurable min/max threshold for a specific metric |
| `Alert` | Entity | Fired when a reading violates an alert rule |
| `MonitoringService` | App service | Records readings, evaluates rules, manages alerts |

**Flow — recording a reading:**

```
POST /monitoring/readings
        │
        ▼
MonitoringService.record_reading()
        │
        ├─► TurbineReading.create()  →  ReadingRepository.save()
        │
        └─► _evaluate_rules()
                │
                └─► for each AlertRule: compare measurement value
                        │
                        └─► Alert.create()  →  AlertRepository.save()
```

### Control bounded context

Responsible for managing turbine state and issuing control commands.

**Key types:**

| Type | Kind | Description |
|---|---|---|
| `Turbine` | Aggregate root | Owns state and enforces valid transitions |
| `TurbineState` | Value object (enum) | `stopped`, `starting`, `running`, `stopping`, `fault`, `maintenance` |
| `ControlCommand` | Entity | Audit record of every issued command, with `executed` or `rejected` status |
| `PitchAngle` | Value object | Blade pitch — validated to −5°…90° |
| `YawAngle` | Value object | Nacelle yaw — validated to 0°…360° |
| `PowerSetpoint` | Value object | Target power output in kW |
| `ControlService` | App service | Issues commands and delegates state changes to the aggregate |

**Turbine state machine:**

```
              ┌─────────┐
    start()   │         │  stop() / emergency_stop()
  ┌──────────►│ RUNNING │──────────────────────────┐
  │           │         │                           │
  │           └─────────┘                           │
  │                                                 ▼
┌─────────┐                                    ┌─────────┐
│ STOPPED │◄── exit_maintenance() ─────────────│  FAULT  │
└─────────┘                                    └─────────┘
  │                                                 ▲
  │  enter_maintenance()                            │ emergency_stop()
  ▼                                                 │
┌─────────────┐                                     │
│ MAINTENANCE │─────────────────────────────────────┘
└─────────────┘
```

**Command pattern:** Every control action (start, stop, set pitch, etc.) creates a `ControlCommand` record before touching the aggregate. If the aggregate rejects the action (e.g. starting a faulted turbine), the command is persisted with `status: rejected` and the reason. This gives a full audit trail.

---

## API Reference

### Monitoring

| Method | Path | Description |
|---|---|---|
| `POST` | `/monitoring/readings` | Record sensor readings for a turbine |
| `GET` | `/monitoring/turbines/{id}/readings/latest` | Get the latest reading |
| `GET` | `/monitoring/turbines/{id}/readings` | Get reading history (`?limit=100`) |
| `POST` | `/monitoring/rules` | Create an alert rule |
| `GET` | `/monitoring/turbines/{id}/rules` | List alert rules for a turbine |
| `DELETE` | `/monitoring/rules/{rule_id}` | Delete an alert rule |
| `GET` | `/monitoring/turbines/{id}/alerts` | List alerts (`?active_only=true`) |
| `POST` | `/monitoring/alerts/{alert_id}/acknowledge` | Acknowledge an alert |

### Control

| Method | Path | Description |
|---|---|---|
| `POST` | `/control/turbines` | Register a new turbine |
| `GET` | `/control/turbines` | List all turbines |
| `GET` | `/control/turbines/{id}` | Get a turbine |
| `POST` | `/control/turbines/{id}/start` | Start the turbine |
| `POST` | `/control/turbines/{id}/stop` | Stop the turbine |
| `POST` | `/control/turbines/{id}/emergency-stop` | Emergency stop (sets fault state) |
| `POST` | `/control/turbines/{id}/pitch` | Set blade pitch angle (°) |
| `POST` | `/control/turbines/{id}/yaw` | Set nacelle yaw angle (°) |
| `POST` | `/control/turbines/{id}/power-setpoint` | Set power setpoint (kW) |
| `POST` | `/control/turbines/{id}/maintenance` | Enter or exit maintenance mode |
| `GET` | `/control/turbines/{id}/commands` | Get command history |

---

## Quick-start walkthrough

```bash
BASE=http://localhost:8000

# 1. Register a turbine
curl -s -X POST $BASE/control/turbines \
  -H "Content-Type: application/json" \
  -d '{"name": "Turbine-1"}' | python -m json.tool

# Copy the returned "id" into TURBINE_ID below
TURBINE_ID=<id>

# 2. Start the turbine
curl -s -X POST $BASE/control/turbines/$TURBINE_ID/start | python -m json.tool

# 3. Add an alert rule — warn if wind speed exceeds 25 m/s
curl -s -X POST $BASE/monitoring/rules \
  -H "Content-Type: application/json" \
  -d "{
    \"turbine_id\": \"$TURBINE_ID\",
    \"metric\": \"wind_speed\",
    \"threshold_max\": 25.0,
    \"severity\": \"warning\"
  }" | python -m json.tool

# 4. Record a reading (wind speed deliberately over threshold)
curl -s -X POST $BASE/monitoring/readings \
  -H "Content-Type: application/json" \
  -d "{
    \"turbine_id\": \"$TURBINE_ID\",
    \"measurements\": {
      \"wind_speed\": 28.5,
      \"power_output\": 2100.0,
      \"rotor_rpm\": 14.2,
      \"nacelle_temperature\": 42.0,
      \"vibration_level\": 0.3
    }
  }" | python -m json.tool

# 5. Check active alerts
curl -s $BASE/monitoring/turbines/$TURBINE_ID/alerts | python -m json.tool

# 6. Set blade pitch
curl -s -X POST $BASE/control/turbines/$TURBINE_ID/pitch \
  -H "Content-Type: application/json" \
  -d '{"degrees": 15.0}' | python -m json.tool
```

---

## CI/CD & Deployment (Azure)

### Overview

```
┌─────────────┐   push to main   ┌──────────────────────────────────────────┐
│   GitHub    │─────────────────►│          GitHub Actions Pipeline          │
│  (source)   │                  │                                           │
└─────────────┘                  │  1. Lint (ruff)                           │
                                 │  2. Test (pytest)  ─── fail: stop here    │
                                 │  3. docker build                           │
                                 │  4. docker push ──► Azure Container       │
                                 │                      Registry (ACR)        │
                                 │  5. az containerapp update                │
                                 │         │                                 │
                                 └─────────┼─────────────────────────────────┘
                                           ▼
                                  ┌─────────────────┐
                                  │ Azure Container │
                                  │      Apps       │  ◄── HTTPS public URL
                                  │  (scale 0–3)    │
                                  └─────────────────┘
```

Pull requests trigger **lint + test only** — no deploy. Merging to `main` triggers the full pipeline including deploy.

---

### Prerequisites

- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) installed locally
- Logged in: `az login`
- [Docker](https://www.docker.com/products/docker-desktop) installed locally
- Your code pushed to a GitHub repository

---

### Step 1 — Provision Azure infrastructure (one-time)

```powershell
# From the project root (PowerShell)
.\infra\setup.ps1
```

This script:
1. Creates a resource group
2. Deploys `infra/main.bicep` which provisions:
   - **Azure Container Registry** (Basic SKU) — stores Docker images
   - **Azure Container Apps Environment** — the serverless container runtime
   - **Azure Container App** — runs the API, scales to zero when idle
3. Creates a **service principal** for GitHub Actions and prints all the values you need for the next step

> **Cost:** Azure Container Apps with `minReplicas: 0` costs nothing when idle. The Basic ACR tier costs ~$0.17/day. Well within student credit limits.

---

### Step 2 — Add GitHub secrets

Go to your GitHub repo → **Settings → Secrets and variables → Actions** and add these secrets (the setup script prints all values):

| Secret | Description |
|---|---|
| `AZURE_CREDENTIALS` | Full JSON block from `az ad sp create-for-rbac` |
| `AZURE_RESOURCE_GROUP` | e.g. `turbincontrol-rg` |
| `ACR_NAME` | e.g. `turbincontrolacr` |
| `ACR_LOGIN_SERVER` | e.g. `turbincontrolacr.azurecr.io` |
| `CONTAINER_APP_NAME` | e.g. `turbincontrol` |

---

### Step 3 — Push to main

```bash
git add .
git commit -m "initial commit"
git push origin main
```

GitHub Actions runs automatically. Watch it at **Actions** tab in your repo. On success, the deploy step prints the live HTTPS URL.

---

### Pipeline file

`.github/workflows/ci-cd.yml` defines two jobs:

| Job | Trigger | Steps |
|---|---|---|
| `test` | every push / PR | ruff lint → pytest |
| `deploy` | push to `main` only, after `test` passes | Azure login → ACR login → docker build + push → containerapp update |

---

### Running tests locally

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

### Linting locally

```bash
ruff check .
```

---

### Deploying manually (without CI)

```powershell
# Build image
docker build -t turbincontrolacr.azurecr.io/turbincontrol:latest .

# Push to ACR
az acr login --name turbincontrolacr
docker push turbincontrolacr.azurecr.io/turbincontrol:latest

# Update the container app
az containerapp update `
  --name turbincontrol `
  --resource-group turbincontrol-rg `
  --image turbincontrolacr.azurecr.io/turbincontrol:latest
```

---

## Extending the prototype

| Concern | Suggestion |
|---|---|
| Persistence | Replace `InMemory*Repository` classes with SQLAlchemy or MongoDB adapters — the domain is fully decoupled from infrastructure |
| Real-time push | Add a WebSocket endpoint or SSE stream on top of the existing alert model |
| Authentication | Add OAuth2 / API-key middleware at the FastAPI layer |
| Domain events | Wire the existing event dataclasses to an event bus (e.g. Redis Pub/Sub) for cross-context integration |
| Multiple turbines | The design already supports it — `TurbineId` is the key throughout |
