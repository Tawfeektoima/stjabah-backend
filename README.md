# S.T. Jabah - Emergency Response System

A comprehensive emergency response coordination system that manages real-time communication between Control Room operators and Emergency Response Team (ERT) vehicles. Built with a layered architecture using Python, Flask, WebSockets, and async programming patterns.

---

## System Overview

S.T. Jabah is a distributed emergency response system with clear client-server separation:

**Server (Central Emergency Operations Center)**
- Control Room module with operator UI for incident management
- WebSocket Hub Server for real-time message routing
- Incident and unit data persistence
- Dispatch and monitoring capabilities

**Client (Raspberry Pi on ERT Vehicles)**
- ERT module with vehicle UI displaying incident assignments
- GPS location tracking and streaming
- Incident resolution and acknowledgment
- Local path planning and routing

**Key Features:**
- Real-time incident dispatch and acknowledgment
- Live GPS tracking of all deployed units
- Automatic incident resolution when all units complete tasks
- Graceful disconnection handling
- Multi-unit incident coordination

---

## System Workflow

The system follows a comprehensive workflow from incident creation to resolution:

1. **Incident Reporting & Creation**: Control Room operator creates an incident with coordinates `(x, y)`
2. **Dispatch**: Control Room assigns the incident to available ERT vehicles
3. **Acknowledgment**: ERT vehicles receive and acknowledge incident assignment via WebSocket
4. **Live Tracking**: ERT vehicles continuously stream GPS coordinates `(x, y)` back to Control Room
5. **Path Computation**: Each ERT vehicle computes optimal paths using its path-finding algorithm (internal)
6. **Unit Resolution**: When ERT completes its task, it sends a resolution signal via REST API
7. **Automatic Incident Resolution**: System checks all assigned units; when **all** are resolved, incident status updates to "RESOLVED"
8. **Graceful Disconnection**: System automatically removes units from assignments if they disconnect unexpectedly
---

## Architecture

The system follows a **distributed client-server architecture** with clear separation between the central server and field units:

```
                    ┌──────────────────────────────────┐
                    │   CENTRAL SERVER                 │
                    │ (Emergency Operations Center)    │
                    └──────────────────────────────────┘
                              │
          ┌───────────────────┼──────────────────┐
          │                   │                  │
    ┌─────▼──────┐   ┌────────▼───────┐   ┌──────▼────┐
    │  Control   │   │  WebSocket Hub │   │ Incident  │
    │  Room UI   │   │  Server        │   │ Database  │
    │ (Port 5001)│   │  (Port 8765)   │   │ (In-Mem)  │
    └─────┬──────┘   └────────┬───────┘   └──────┬────┘
          │                   │                  │
          └───────────────────┼──────────────────┘
                    WebSocket │
                  Hub Routing │
         ┌──────────────────────────────────┐
         │   COMMUNICATION MODULE (SERVER)  │
         │   - Hub subscriptions            │
         │   - Message routing              │
         └──────────────────────────────────┘
                    │
        ┌───────────┴───────────────────────────────────┐
        │   Connections to ERT Units (Raspberry Pi)     │
        └────────────┬────────────────────────────────┬─┘
                     │                                │
        ┌────────────▼─────────────┐     ┌────────────▼─────────────┐
        │  ERT UNIT #1             │     │  ERT UNIT #N             │
        │  (Raspberry Pi)          │     │  (Raspberry Pi)          │
        │                          │     │                          │
        │ ┌──────────────────────┐ │     │ ┌──────────────────────┐ │
        │ │ ERT UI (Local)       │ │     │ │ ERT UI (Local)       │ │
        │ │ - Incident Display   │ │     │ │ - Incident Display   │ │
        │ │ - GPS Coordinates    │ │     │ │ - GPS Coordinates    │ │
        │ │ - Resolution Button  │ │     │ │ - Resolution Button  │ │
        │ └──────────┬───────────┘ │     │ └──────────┬───────────┘ │
        │            │             │     │            │             │
        │ ┌──────────▼───────────┐ │     │ ┌──────────▼───────────┐ │
        │ │ ERT SERVICE          │ │     │ │ ERT SERVICE          │ │
        │ │ - Unit Logic         │ │     │ │ - Unit Logic         │ │
        │ │ - Incident Handler   │ │     │ │ - Incident Handler   │ │
        │ │ - GPS Simulator      │ │     │ │ - GPS Simulator      │ │
        │ └──────────┬───────────┘ │     │ └──────────┬───────────┘ │
        │            │             │     │            │             │
        │ ┌──────────▼───────────┐ │     │ ┌──────────▼───────────┐ │
        │ │ COMMUNICATION CLIENT │ │     │ │ COMMUNICATION CLIENT │ │
        │ │ (WebSocket)          │ │     │ │ (WebSocket)          │ │
        │ │ - Connect to hub     │ │     │ │ - Connect to hub     │ │
        │ │ - Publish messages   │ │     │ │ - Publish messages   │ │
        │ │ - Subscribe to topics│ │     │ │ - Subscribe to topics│ │
        │ └──────────────────────┘ │     │ └──────────────────────┘ │
        └──────────────────────────┘     └──────────────────────────┘
```

### Deployment Model

**Server-side (Centralized)**
- Runs on a dedicated server/machine
- Hosts Control Room web UI (operator dashboard)
- Runs WebSocket hub server for message routing
- Manages incident database and state
- Port 5001: Control Room API & UI
- Port 8765: WebSocket hub for client connections

**Client-side (Distributed on Raspberry Pi)**
- Runs on each ERT vehicle (Raspberry Pi)
- Hosts ERT local UI showing assigned incidents
- Maintains WebSocket connection to central hub
- Streams GPS location data
- Publishes acknowledgments and resolutions
- Port 5002: ERT local API & UI (local network only)

### Architecture Benefits

- **Separation of Concerns**: Server handles dispatch, clients handle execution
- **Scalability**: Multiple ERT units can connect independently to the hub
- **Resilience**: Unit can continue operating if disconnected (offline mode)
- **Real-time Coordination**: WebSocket hub enables instant message delivery
- **Distributed Computing**: Each unit has its own UI and can function autonomously
- **Flexibility**: Easy to add new ERT units without changing server code
- **Local Processing**: Each Raspberry Pi runs its own service layer for path planning

---

## Project Structure
## Project Structure

```
S.T.Jabah/
├── control_room/                      # Control Room application
│   ├── __init__.py
│   ├── cr_main.py                     # Entry point for Control Room
│   ├── hub_server.py                  # WebSocket hub server
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── incident_api.py            # Incident REST endpoints (Flask blueprint)
│   │
│   ├── model/
│   │   ├── __init__.py
│   │   ├── incident.py                # Incident entity with status enum
│   │   └── unit.py                    # Unit entity with status enum (ACTIVE/RESOLVED/UNAVAILABLE)
│   │
│   ├── repository/
│   │   ├── __init__.py
│   │   ├── incident_repository.py     # Abstract incident repository interface
│   │   ├── in_memory_incident_repository.py  # In-memory implementation
│   │   ├── unit_repository.py         # Abstract unit repository interface
│   │   └── in_memory_unit_repository.py      # In-memory implementation
│   │
│   └── service/
│       ├── __init__.py
│       ├── incident_service.py        # Incident business logic
│       └── unit_service.py            # Unit business logic & resolution
│
├── ert/                               # Emergency Response Team application
│   ├── __init__.py
│   ├── ert_main.py                    # Entry point for ERT unit
│   ├── unit_info.json                 # Local ERT state (id, location, assignment, status)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── unit_api.py                # ERT unit REST endpoints (Flask blueprint)
│   │
│   ├── model/
│   │   └── unit.py                    # ERT unit entity
│   │
│   ├── repository/
│   │   └── unit_repository.py         # ERT unit repository
│   │
│   └── service/
│       ├── __init__.py
│       ├── unit_service.py            # ERT unit business logic & resolution publishing
│       └── path_service.py            # Path-finding algorithm
│
├── communication/                     # Shared communication module
│   ├── __init__.py
│   ├── websocket_communication.py     # WebSocket client abstraction
│   └── websocket_handlers.py          # Message handlers for incoming WebSocket events
│
├── pyproject.toml                     # Project configuration & dependencies
└── README.md                          # This file
```

### Key Components

#### Control Room (`control_room/`)
- **Hub Server**: Central WebSocket server that manages all client connections and message routing
- **Services**: Business logic for incident and unit management
- **API**: REST endpoints for creating/updating incidents and managing dispatch
- **Repository**: Data persistence layer (in-memory for now, SQLite planned)

#### ERT Unit (`ert/`)
- **Main Loop**: Connects to hub, receives incidents, streams location updates
- **API**: REST endpoints for retrieving unit location and resolving incidents
- **Service**: Handles incident acknowledgment and resolution with hub notification
- **unit_info.json**: Local state file storing unit id, coordinates, assigned incident, and status

#### Communication (`communication/`)
- **WebSocketCommunication**: Unified client for connecting to the hub (used by both Control Room and ERT)
- **WebSocketHandlers**: Processes incoming messages at the server (location, acknowledgment, resolution, disconnection)
- **Topics**: `incident`, `acknowledgment`, `location`, `resolution`

---

## Deployment Architecture

### Server Deployment (Central Emergency Operations Center)
- Single server machine running Control Room + Hub Server
- Hosts the operator dashboard (Control Room UI)
- Manages all incident state and unit assignments
- Maintains WebSocket connections from all ERT units

### Client Deployment (Raspberry Pi on ERT Vehicles)
- One Raspberry Pi per emergency vehicle
- Runs ERT module with local UI
- Maintains persistent WebSocket connection to central hub
- Can operate independently (offline mode) if hub connection drops
- Streams GPS and status data to hub

### Network Communication
- Server → Hub: Local or internal network
- Hub ↔ ERT Units: WebSocket connections (can be over WAN/internet)
- Server ↔ ERT: One-way via hub (no direct connection)

---

## Running the System

### Prerequisites
- Python 3.8+
- `uv` package manager

### Server Setup (Single machine)

```bash
# Clone the repository on the server
git clone https://github.com/Shaker-10/S.T.Jabah.git
cd S.T.Jabah

# Install uv if not already installed
pip install uv

# (Optional) Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows
```

### Server Startup

Start the Control Room and Hub Server on the central server:

```bash
uv run python control_room/cr_main.py
```

**Output should show:**
```
Control Room API running on http://127.0.0.1:5001
WebSocket Hub running on ws://127.0.0.1:8765
Control Room UI: http://127.0.0.1:5001
```

### ERT Unit Setup (Raspberry Pi)

On each ERT vehicle (Raspberry Pi):

```bash
# Clone the repository on the Raspberry Pi
git clone https://github.com/Shaker-10/S.T.Jabah.git
cd S.T.Jabah

# Install uv
pip install uv

# (Optional) Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Update the hub server address in ert/ert_main.py if needed
# Change: ws://127.0.0.1:8765 → ws://<SERVER_IP>:8765

# Run the ERT unit
uv run python ert/ert_main.py
```

**Output should show:**
```
ERT-001 starting...
🔗 Connected to hub server
ERT API running on http://127.0.0.1:5002
ERT UI: http://127.0.0.1:5002/ert (local vehicle only)
```

---

## Quick Start Guide

### Minimal Local Testing (All on one machine)

```bash
# Terminal 1: Start the server
uv run python control_room/cr_main.py
# Wait for: "Hub Server running on ws://127.0.0.1:8765"

# Terminal 2: Start ERT Unit #1
uv run python ert/ert_main.py
# Should see: "Connected to hub server"

# Terminal 3: Test the system
# Create incident
curl -X POST http://127.0.0.1:5001/incidents \
  -H "Content-Type: application/json" \
  -d '{"x": 45.5, "y": 67.8}'

# Dispatch to unit
curl -X PUT http://127.0.0.1:5001/incidents/{incident_id}/dispatch \
  -H "Content-Type: application/json" \
  -d '{"ert_id": "ert-001"}'

# Resolve incident
curl -X PUT http://127.0.0.1:5002/ert/incident/resolve
```

### Multi-Unit Deployment

```bash
# On Server
uv run python control_room/cr_main.py

# On Raspberry Pi #1
# Edit ert/ert_main.py to set: hub_server = "ws://<SERVER_IP>:8765"
uv run python ert/ert_main.py

# On Raspberry Pi #2 (different unit)
# Edit ert/unit_info.json to change unit ID
# Edit ert/ert_main.py to set: hub_server = "ws://<SERVER_IP>:8765"
uv run python ert/ert_main.py
# Both units will now connect to the same hub
```

---

## API Endpoints

### Control Room Incident Endpoints

#### Create Incident
```
POST /incidents
Content-Type: application/json

{
  "x": 45.5,
  "y": 67.8
}

Response (201):
{
  "id": "incident_abc123",
  "x": 45.5,
  "y": 67.8,
  "status": "created",
  "assigned_units": []
}
```

#### Get All Incidents
```
GET /incidents

Response (200):
[
  {
    "id": "incident_abc123",
    "x": 45.5,
    "y": 67.8,
    "status": "in_progress",
    "assigned_units": ["ert-001", "ert-002"]
  }
]
```

#### Get Incident by ID
```
GET /incidents/<incident_id>

Response (200):
{
  "id": "incident_abc123",
  "x": 45.5,
  "y": 67.8,
  "status": "in_progress",
  "assigned_units": ["ert-001"]
}
```

#### Update Incident Coordinates
```
PUT /incidents/<incident_id>
Content-Type: application/json

{
  "x": 50.0,
  "y": 75.5
}

Response (200):
{
  "id": "incident_abc123",
  "x": 50.0,
  "y": 75.5,
  "status": "in_progress",
  "assigned_units": ["ert-001"]
}
```

#### Delete Incident
```
DELETE /incidents/<incident_id>

Response (200):
{
  "message": "Incident deleted successfully"
}
```

#### Dispatch Incident to Unit
```
PUT /incidents/<incident_id>/dispatch
Content-Type: application/json

{
  "ert_id": "ert-001"
}

Response (200):
{
  "message": "Incident dispatched successfully",
  "incident_id": "incident_abc123",
  "ert_id": "ert-001"
}
```

### ERT Unit Endpoints

#### Get Unit Location
```
GET /ert/unit/location

Response (200):
{
  "x": 23.45,
  "y": 56.78
}
```

#### Get Assigned Incident Location
```
GET /ert/assigned_incident/location

Response (200):
{
  "x": 45.5,
  "y": 67.8
}
```

#### Resolve Incident
```
PUT /ert/incident/resolve

Response (200):
{
  "message": "Incident resolved successfully"
}
```

#### Health Check
```
GET /ert/health

Response (200):
{
  "status": "healthy",
  "service": "emergency-response-system",
  "component": "ert-001"
}
```

### WebSocket Messages (Hub Server)

#### Incident Dispatch (Control Room → Hub → ERT)
```json
Topic: "incident"
{
  "id": "incident_abc123",
  "x": 45.5,
  "y": 67.8,
  "status": "dispatched"
}
```

#### Acknowledgment (ERT → Hub → Control Room)
```json
Topic: "acknowledgment"
{
  "ert_id": "ert-001",
  "incident_id": "incident_abc123",
  "x": 23.45,
  "y": 56.78,
  "message": "Incident received successfully. ERT unit dispatched.",
  "status": "acknowledged"
}
```

#### Location Update (ERT → Hub → Control Room)
```json
Topic: "location"
{
  "ert_id": "ert-001",
  "x": 30.0,
  "y": 60.0
}
```

#### Resolution (ERT → Hub → Control Room)
```json
Topic: "resolution"
{
  "ert_id": "ert-001",
  "incident_id": "incident_abc123",
  "message": "Incident resolved successfully"
}
```

---

## Message Flow Examples

### Example 1: Full Incident Resolution

1. **Create Incident** (Control Room operator)
   ```
   POST /incidents → {id: "inc-1", x: 10, y: 20}
   ```

2. **Dispatch Incident** (Control Room operator)
   ```
   PUT /incidents/inc-1/dispatch → {ert_id: "ert-001"}
   Hub broadcasts via "incident" topic
   ```

3. **ERT Unit Acknowledges** (Automatic)
   ```
   ERT receives incident, sends acknowledgment via "acknowledgment" topic
   Control Room receives and adds "ert-001" to incident.assigned_units
   ```

4. **ERT Streams Location** (Continuous)
   ```
   ERT publishes via "location" topic every N seconds
   Control Room receives and updates unit location
   ```

5. **ERT Resolves Incident** (When task complete)
   ```
   PUT /ert/incident/resolve
   ERT publishes via "resolution" topic
   Control Room checks all assigned units:
     - If ALL resolved → incident.status = RESOLVED
     - Otherwise → incident.status stays IN_PROGRESS
   ```

### Example 2: Multi-Unit Dispatch

1. Dispatch same incident to 2 units: `{ert_id: "ert-001"}` and `{ert_id: "ert-002"}`
2. Both units acknowledge → `incident.assigned_units = ["ert-001", "ert-002"]`
3. First unit resolves:
   ```
   ert-001 → PUT /ert/incident/resolve
   Control Room checks: ert-001=RESOLVED, but ert-002=ACTIVE
   Result: incident.status stays IN_PROGRESS
   ```
4. Second unit resolves:
   ```
   ert-002 → PUT /ert/incident/resolve
   Control Room checks: ert-001=RESOLVED, ert-002=RESOLVED
   Result: incident.status = RESOLVED ✅
   ```

### Example 3: Unexpected Disconnection

1. ERT unit loses connection (network failure, power loss, etc.)
2. Hub detects disconnection event
3. Control Room removes unit from incident:
   ```
   incident.assigned_units.remove("ert-001")
   ```
4. Incident status logic adjusts:
   - If it was the only unit → incident may transition to IN_PROGRESS or PENDING
   - If other units exist → continues with remaining units
---

## Status Enums

### Incident Status
```python
CREATED = "created"           # Just created, not dispatched
DISPATCHED = "dispatched"     # Assigned to at least one ERT unit
ACKNOWLEDGED = "acknowledged" # At least one ERT unit has acknowledged
IN_PROGRESS = "in_progress"   # Active units working on incident
RESOLVED = "resolved"         # All assigned units have resolved
PENDING = "pending"           # Waiting for assignment
```

### Unit Status
```python
ACTIVE = "active"             # Unit available and ready
RESOLVED = "resolved"         # Unit completed its assigned task
UNAVAILABLE = "unavailable"   # Unit offline/disconnected
```

---

## Configuration

### Control Room
- **HTTP Port**: 5001 (configurable in `control_room/cr_main.py`)
- **Hub Server Port**: 8765 (configured in `control_room/hub_server.py`)
- **Repository**: In-memory (default), SQLite (future)

### ERT Unit
- **HTTP Port**: 5002 (configurable in `ert/ert_main.py`)
- **Hub Server**: Connects to `ws://127.0.0.1:8765`
- **State File**: `ert/unit_info.json` (local persistence)
- **GPS Simulation**: Random coordinates updated periodically

### Environment Variables
Currently not used, but can be added for:
- `CONTROL_ROOM_PORT`
- `ERT_PORT`
- `HUB_SERVER_URL`
- `DATABASE_URL`
- `LOG_LEVEL`

---

## Data Persistence

### Current Implementation (In-Memory)
- All incident and unit data stored in Python dictionaries
- Data lost on application restart
- Suitable for development and testing

### Planned (Task 2)
- SQLite database integration
- Persistent incident history
- Unit performance metrics
- Message persistence for late-joining ERT units

---

## Known Issues & Limitations

1. **Race Conditions**: File-based `unit_info.json` not thread-safe; candidates for database
2. **No Authentication**: System currently has no auth/authorization layer
3. **Single Hub Instance**: Hub server not horizontally scalable (no clustering)
4. **No Message Persistence**: Late-joining units don't see incident history
5. **Basic Path Planning**: ERT path service not fully implemented
6. **No Backup/Failover**: No redundancy for Control Room or Hub
7. **Import Path Issues**: Some modules may fail when run as scripts vs imports

---

## Future Improvements (Spring Roadmap)

### Task 1: ✅ Disconnect Handling
- [x] Detect ERT unit disconnection at hub
- [x] Automatically remove disconnected units from incident assignments
- [x] Update incident status if needed

### Task 2: SQLite Persistence
- [ ] Add SQLite integration with SQLAlchemy ORM
- [ ] Migrate in-memory repositories to database repositories
- [ ] Add incident history and audit logs
- [ ] Store message history for late joiners

### Task 3: Map Endpoints
- [ ] `/map/unit-locations` - Get all active unit locations
- [ ] `/map/incident-location` - Get specific incident location with assigned units
- [ ] WebSocket feed for real-time map updates

### Task 4: Message Persistence
- [ ] Store incident messages in database
- [ ] Allow late-joining ERT units to receive past messages
- [ ] Implement TTL-based message cleanup

### Task 5: Report Generation
- [ ] `/reports/incident/<incident_id>` - Generate incident report
- [ ] `/reports/unit/<unit_id>` - Unit performance report
- [ ] PDF export functionality
- [ ] Time-range filtered reports

### Additional Improvements
- [ ] Docker & Docker Compose for local development
- [ ] Unit tests for all services and handlers
- [ ] Integration tests for full message flows
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Performance benchmarking and optimization
- [ ] Horizontal scaling with load balancer
- [ ] Authentication and authorization (JWT/OAuth)
- [ ] Configuration management (environment files)
- [ ] Structured logging with correlation IDs
- [ ] Health checks and monitoring endpoints

---

## Development

### Project Tools
- **Language**: Python 3.8+
- **Package Manager**: `uv` (fast, modern Python package manager)
- **Framework**: Flask (REST API), websockets (WebSocket)
- **Async**: asyncio (async/await patterns)
- **Code Style**: (To be configured) Black, Flake8, MyPy

### Common Commands

```bash
# Run all components in order
Terminal 1: uv run python control_room/cr_main.py
Terminal 2: uv run python ert/ert_main.py

# Create an incident
curl -X POST http://127.0.0.1:5001/incidents \
  -H "Content-Type: application/json" \
  -d '{"x": 45.5, "y": 67.8}'

# Dispatch to unit
curl -X PUT http://127.0.0.1:5001/incidents/incident_abc123/dispatch \
  -H "Content-Type: application/json" \
  -d '{"ert_id": "ert-001"}'

# Resolve incident
curl -X PUT http://127.0.0.1:5002/ert/incident/resolve

# Check ERT health
curl http://127.0.0.1:5002/ert/health
```

---

## Troubleshooting

### Port Already in Use
```bash
# Kill process on specific port (macOS/Linux)
lsof -ti:5001 | xargs kill -9  # Control Room
lsof -ti:5002 | xargs kill -9  # ERT
lsof -ti:8765 | xargs kill -9  # Hub Server
```

### WebSocket Connection Refused
- Ensure hub server is running on port 8765
- Check firewall settings
- Verify both CR and ERT are connecting to the same hub URL

### Unit Not Receiving Incidents
- Check that unit is connected (should see "Connected to hub" log message)
- Verify incident is being dispatched via Control Room API
- Check that acknowledgment is being published (look for "✅ Acknowledgment" in logs)

### Resolution Not Working
- Ensure `communication_channel` is passed to ERT unit service
- Check that unit_info.json has valid incident assignment
- Verify Control Room has unit_service initialized with resolve_unit method

---

## License

[Add your license here]

---

## Contact & Support

For questions or issues:
- Create a GitHub issue
- Contact the development team

---

## Changelog

### v0.1.0 (Current)
- WebSocket hub server and routing
- Control Room REST API for incidents
- ERT REST API with unit location and resolution endpoints
- Real-time incident dispatch and acknowledgment
- Automatic incident resolution when all units resolve
- Graceful disconnection handling
- Basic status enum system

### v0.0.1 (Initial)
- Project scaffolding
- Basic layered architecture
- In-memory repositories