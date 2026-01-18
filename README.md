# Emergency Response System

A layered architecture emergency response system that coordinates between Control Room operators and Emergency Response Team (ERT) vehicles for efficient incident management and resolution.

## Table of Contents

1. [System Workflow](#system-workflow)
2. [Architecture](#architecture)
3. [API Endpoints](#api-endpoints)
4. [Progress Status](#progress-status)
5. [Setup Instructions](#setup-instructions)

---

## System Workflow

The system follows a seven-step sequence from incident reporting to resolution:

### 1. **Incident Reporting & Creation**
Field personnel provide incident coordinates `(x, y)` to the Control Room operator, who creates the incident in the system.

**API**: `POST /cr/incidents`

### 2. **Dispatch**
Control Room operator assigns the incident to specific ERT vehicles that are available and suitable for the emergency.

**API**: `POST /cr/incidents/<id>/dispatch`

### 3. **Acknowledgment**
ERT vehicles receive the incident notification and acknowledge the task, signaling that they are en route to the incident location.

**API**: `PATCH /ert/units/<unit_id>/acknowledge`

### 4. **Path Computation**
Each ERT vehicle computes its optimal path from its current location to the incident coordinates `(x, y)` using its own path-finding algorithm.

**Note**: This is handled internally by each vehicle's path computation service.

### 5. **Live Tracking**
ERT vehicles continuously stream their GPS coordinates `(x, y)` back to the Control Room for real-time monitoring and coordination.

**API**: `POST /ert/units/<unit_id>/location`

### 6. **Unit Resolution**
Once the emergency work is completed, the ERT vehicle sends a "Resolve" signal indicating its task is done.

**API**: `PATCH /ert/units/<unit_id>/resolve`

### 7. **System Resolution**
The system automatically checks all assigned units for the incident. When the last unit resolves, the incident is automatically marked as "Resolved" in the database, completing the workflow.

**Note**: This is handled automatically by the service layer.

---

## Architecture

The system follows a **layered architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                    API Layer                        │
│  (Flask Blueprints - HTTP Request/Response)        │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│                  Service Layer                      │
│         (Business Logic & Orchestration)            │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│               Repository Layer                      │
│           (Data Access & Persistence)               │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│                  Model Layer                        │
│              (Domain Entities)                      │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│            Communication Module                     │
│    (Abstracted Channel - WebSocket/Polling/SIM)    │
└─────────────────────────────────────────────────────┘
```

### Module Structure

#### **1. control-room/**
Controls incident management and dispatch operations.

- **api/**: HTTP endpoints (Flask blueprints) for incident CRUD and dispatch operations
- **service/**: Business logic for incident lifecycle, dispatch, and resolution checking
- **repository/**: Data access layer with interface pattern (allows multiple implementations)
- **model/**: Incident domain model with status enumeration

#### **2. ert/** (Emergency Response Team)
Manages ERT unit operations and tracking.

- **api/**: HTTP endpoints for unit acknowledgment, location updates, and resolution
- **service/**: Business logic for unit operations and path computation
- **repository/**: Data access for unit and location persistence
- **model/**: Unit, Location domain models

#### **3. communication/**
Abstracted communication layer for Control Room ↔ ERT messaging.

- **channel.py**: Abstract base class for communication channels
- **message.py**: Message models with types (dispatch, acknowledgment, location, resolution)
- **Purpose**: Allows switching between WebSocket, polling, or SIM without affecting other code

### Architecture Benefits

- **Separation of Concerns**: Each layer has a single responsibility
- **Testability**: Easy to mock dependencies at each layer
- **Flexibility**: Repository pattern allows switching storage backends (in-memory, SQL, MongoDB)
- **Maintainability**: Changes in one layer don't cascade to others
- **Scalability**: Communication abstraction enables future protocol changes

---

## API Endpoints

### Control Room Endpoints

Base URL: `/cr`

#### 1. Create Incident

Creates a new incident in the system with coordinates provided by field personnel.

**Endpoint**: `POST /cr/incidents`

**Input**:
```json
{
  "coordinates": [10.5, 20.3]
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "coordinates": [10.5, 20.3],
  "status": "created",
  "assigned_unit_ids": [],
  "created_at": "2024-01-15T10:30:00",
  "resolved_at": null
}
```

---

#### 2. Get All Incidents

Retrieves a list of all incidents in the system.

**Endpoint**: `GET /cr/incidents`

**Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "coordinates": [10.5, 20.3],
    "status": "created",
    "assigned_unit_ids": [],
    "created_at": "2024-01-15T10:30:00",
    "resolved_at": null
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "coordinates": [15.2, 25.8],
    "status": "dispatched",
    "assigned_unit_ids": ["unit-001", "unit-002"],
    "created_at": "2024-01-15T11:00:00",
    "resolved_at": null
  }
]
```

---

#### 3. Get Incident by ID

Retrieves a specific incident by its unique identifier.

**Endpoint**: `GET /cr/incidents/<incident_id>`

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "coordinates": [10.5, 20.3],
  "status": "dispatched",
  "assigned_unit_ids": ["unit-001"],
  "created_at": "2024-01-15T10:30:00",
  "resolved_at": null
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "Incident not found"
}
```

---

#### 4. Update Incident

Updates an existing incident's properties (coordinates, status, assigned units).

**Endpoint**: `PUT /cr/incidents/<incident_id>`

**Input**:
```json
{
  "status": "in_progress",
  "assigned_unit_ids": ["unit-001", "unit-002"]
}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "coordinates": [10.5, 20.3],
  "status": "in_progress",
  "assigned_unit_ids": ["unit-001", "unit-002"],
  "created_at": "2024-01-15T10:30:00",
  "resolved_at": null
}
```

---

#### 5. Delete Incident

Removes an incident from the system.

**Endpoint**: `DELETE /cr/incidents/<incident_id>`

**Response** (200 OK):
```json
{
  "message": "Incident deleted successfully"
}
```

**Error Response** (404 Not Found):
```json
{
  "error": "Incident not found"
}
```

---

#### 6. Dispatch Incident

Assigns an incident to specific ERT vehicles, sending notifications to each unit.

**Endpoint**: `POST /cr/incidents/<incident_id>/dispatch`

**Input**:
```json
{
  "unit_ids": ["unit-001", "unit-002", "unit-003"]
}
```

**Response** (200 OK):
```json
{
  "status": "Units dispatched"
}
```

**Error Response** (400 Bad Request):
```json
{
  "error": "No units selected"
}
```

---

### ERT Endpoints

Base URL: `/ert`

#### 1. Get Active Assignment

Retrieves the currently active incident assignment for a specific ERT unit.

**Endpoint**: `GET /ert/units/<unit_id>/active`

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "coordinates": [10.5, 20.3],
  "status": "dispatched",
  "assigned_unit_ids": ["unit-001"],
  "created_at": "2024-01-15T10:30:00",
  "resolved_at": null
}
```

**Response** (204 No Content): When no active assignments exist.

---

#### 2. Acknowledge Task

ERT unit acknowledges receiving the incident assignment and signals it is en route.

**Endpoint**: `PATCH /ert/units/<unit_id>/acknowledge`

**Input**:
```json
{
  "incident_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response** (200 OK):
```json
{
  "status": "Acknowledged"
}
```

---

#### 3. Update Location

ERT vehicle streams its current GPS coordinates for live tracking by the Control Room.

**Endpoint**: `POST /ert/units/<unit_id>/location`

**Input**:
```json
{
  "x": 12.5,
  "y": 22.8
}
```

**OR**:
```json
{
  "coordinates": [12.5, 22.8]
}
```

**Response** (200 OK):
```json
{
  "status": "Location updated"
}
```

---

#### 4. Resolve Task

ERT vehicle signals that its work on the incident is complete.

**Endpoint**: `PATCH /ert/units/<unit_id>/resolve`

**Input**:
```json
{
  "incident_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Response** (200 OK):
```json
{
  "status": "Resolved"
}
```

---

### Health Check

**Endpoint**: `GET /health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "emergency-response-system"
}
```

---

## Progress Status

### ✅ Completed

#### **control-room/**
- ✅ **api/incident_api.py**: All CRUD endpoints and dispatch endpoint implemented
- ✅ **model/incident.py**: Incident model with status enum and `to_dict()` serialization
- ✅ **repository/base_repository.py**: Abstract base repository interface (ABC pattern)
- ✅ **repository/in_memory_incident_repository.py**: Working in-memory implementation with all CRUD operations
- ✅ **service/incident_service.py**: Basic service structure with `create_incident()` implemented (dummy implementation)

#### **ert/**
- ✅ **api/unit_api.py**: All ERT endpoints defined (acknowledge, location, resolve, active)
- ✅ **model/unit.py**: Unit model with status enum and `to_dict()` serialization
- ✅ **model/location.py**: Location tracking model
- ✅ **service/unit_service.py**: Service structure defined
- ✅ **service/path_service.py**: Path computation service interface defined
- ✅ **repository/unit_repository.py**: Repository interface defined

#### **communication/**
- ✅ **channel.py**: Abstract base class with all required methods
- ✅ **message.py**: Message models with type enumeration
- ✅ **Placeholder implementation**: `CommunicationChannelImpl` in `main.py` (logging only)

#### **main.py**
- ✅ Application factory pattern (`create_app()`)
- ✅ Dependency injection setup
- ✅ Blueprint registration
- ✅ Health check endpoint

---

### 🚧 In Progress / Partially Implemented

#### **control-room/service/incident_service.py**
- ✅ `create_incident()`: Implemented (creates incident with repository)
- ⚠️ `dispatch_incident()`: Structure defined, needs communication channel integration
- ⚠️ `check_and_resolve_incident()`: Structure defined, needs implementation
- ⚠️ `update_incident_status()`: Structure defined, needs implementation

#### **ert/service/unit_service.py**
- ⚠️ All methods have structure but need full implementation
- ⚠️ Integration with communication channel needed
- ⚠️ Path computation integration needed

---

### 📋 TODO / Not Implemented

#### **Repository Layer**
- ❌ SQL database implementation (placeholder structure exists)
- ❌ MongoDB implementation
- ❌ Unit repository implementations (interfaces defined only)

#### **Service Layer**
- ❌ Full incident dispatch flow with communication
- ❌ Automatic resolution checking when last unit resolves
- ❌ Path computation service implementation
- ❌ Location streaming to Control Room

#### **Communication Module**
- ❌ WebSocket implementation
- ❌ HTTP polling implementation
- ❌ SIM-based communication implementation
- ❌ Message routing and delivery logic

#### **Testing**
- ❌ Unit tests
- ❌ Integration tests
- ❌ API endpoint tests

#### **Additional Features**
- ❌ Authentication/Authorization
- ❌ Input validation middleware
- ❌ Error handling middleware
- ❌ Database migrations (when SQL is implemented)
- ❌ Logging configuration file
- ❌ Configuration management (config files, environment variables)

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd stjaba-layered
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist or is empty, install Flask manually:

```bash
pip install flask
```

### Step 4: Verify Project Structure

Ensure your project structure matches:

```
stjaba-layered/
├── control_room/
│   ├── api/
│   │   └── incident_api.py
│   ├── model/
│   │   └── incident.py
│   ├── repository/
│   │   ├── base_repository.py
│   │   └── in_memory_incident_repository.py
│   └── service/
│       └── incident_service.py
├── ert/
│   ├── api/
│   │   └── unit_api.py
│   ├── model/
│   │   ├── unit.py
│   │   └── location.py
│   ├── repository/
│   │   └── unit_repository.py
│   └── service/
│       ├── unit_service.py
│       └── path_service.py
├── communication/
│   ├── channel.py
│   └── message.py
└── main.py
```

### Step 5: Run the Application

```bash
python main.py
```

The application will start on `http://127.0.0.1:5000`

### Step 6: Verify Installation

Test the health check endpoint:

```bash
curl http://127.0.0.1:5000/health
```

Expected response:
```json
{"status":"healthy","service":"emergency-response-system"}
```

### Step 7: Test Endpoints (Optional)

Create a test incident:

```bash
curl -X POST http://127.0.0.1:5000/cr/incidents \
  -H "Content-Type: application/json" \
  -d '{"coordinates": [10.5, 20.3]}'
```

---

## Development Notes

### Current Storage

The system currently uses **in-memory storage** (`InMemoryIncidentRepository`), meaning:
- ✅ No database setup required
- ✅ Fast for development/testing
- ⚠️ Data is lost on application restart
- ⚠️ Not suitable for production

### Switching to SQL Database

To switch to SQL storage in the future:

1. Implement `SQLIncidentRepository` class
2. Update `main.py` line 42:
   ```python
   # Change from:
   incident_repository = InMemoryIncidentRepository()
   
   # To:
   incident_repository = SQLIncidentRepository(db_connection=db_conn)
   ```

### Communication Channel

Currently using a placeholder implementation that only logs messages. To implement actual communication:

1. Create a concrete implementation (e.g., `WebSocketChannel`, `PollingChannel`)
2. Update `main.py` line 50 to use the new implementation

---

## License

[Add your license information here]

## Contributors

[Add contributor information here]
