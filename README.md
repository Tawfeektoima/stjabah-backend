# Emergency Response System

A layered architecture emergency response system that coordinates between Control Room operators and Emergency Response Team (ERT) vehicles for efficient incident management and resolution.

---
## System Workflow

The system follows a seven-step sequence from incident reporting to resolution:

1. **Incident Reporting & Creation**: Field personnel provide incident coordinates `(x, y)` to the Control Room operator, who creates the incident in the system.
2. **Dispatch**: Control Room operator assigns the incident to specific ERT vehicles that are available and suitable for the emergency.
3. **Acknowledgment**: ERT vehicles receive the incident notification and acknowledge the task, signaling that they are en route to the incident location.
4. **Path Computation**: Each ERT vehicle computes its optimal path from its current location to the incident coordinates `(x, y)` using its own path-finding algorithm.
  - **Note**: This is handled internally by each vehicle's path computation service.
5. **Live Tracking**: ERT vehicles continuously stream their GPS coordinates `(x, y)` back to the Control Room for real-time monitoring and coordination.
6. **Unit Resolution**: Once the emergency work is completed, the ERT vehicle sends a "Resolve" signal indicating its task is done.
7. **System Resolution**: The system automatically checks all assigned units for the incident. When the last unit resolves, the incident is automatically marked as "Resolved" in the database, completing the workflow.
---
## Architecture

The system follows a **layered architecture** pattern with clear separation of concerns:

```
┌─────────────────────────────────────────────────────┐
│                    API Layer                        │
│   (Flask Blueprints - HTTP Request/Response)        │
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
│    (Abstracted Channel - WebSocket/Polling/SIM)     │
└─────────────────────────────────────────────────────┘
```

### Architecture Benefits

- **Separation of Concerns**: Each layer has a single responsibility
- **Testability**: Easy to mock dependencies at each layer
- **Flexibility**: Repository pattern allows switching storage backends (in-memory, SQL, MongoDB)
- **Maintainability**: Changes in one layer don't cascade to others
- **Scalability**: Communication abstraction enables future protocol changes
### Project Structures
```
stjaba-layered/
├── control_room/
│   ├── api/
│   │   └── incident_api.py
│   ├── model/
│   │   └── incident.py
│   ├── repository/
│   │   ├── incident_repository.py
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

----
## Endpoints

### 1. Get Incident by ID

**HTTP Method and URL:**

```
GET /incidents/<incident_id>
```

**Purpose:** Retrieve detailed information about a specific incident using its unique identifier.

**Payload Format:** No payload required.

**Response Format:**

_Success (200):_

```json
{
  "id": "incident_123",
  "x": 45.5,
  "y": 67.8,
  "status": "active",
  "created_at": "2026-01-29T10:30:00Z"
}
```

_Error - Not Found (404):_

```json
{
  "error": "Incident not found",
  "incident_id": "incident_123"
}
```

_Error - Internal Server Error (500):_

```json
{
  "error": "Internal server error"
}
```

---

### 2. List All Incidents

**HTTP Method and URL:**

```
GET /incidents
```

**Purpose:** Retrieve a list of all incidents in the system.

**Payload Format:** No payload required.

**Response Format:**

_Success (200):_

```json
[
  {
    "id": "incident_123",
    "x": 45.5,
    "y": 67.8,
    "status": "active",
    "created_at": "2026-01-29T10:30:00Z"
  },
  {
    "id": "incident_456",
    "x": 12.3,
    "y": 34.5,
    "status": "resolved",
    "created_at": "2026-01-29T09:15:00Z"
  }
]
```

---

### 3. Create Incident

**HTTP Method and URL:**

```
POST /incidents
```

**Purpose:** Create a new incident with specified coordinates.

**Payload Format:**

```json
{
  "x": 45.5,
  "y": 67.8
}
```

**Required Fields:**

- `x` (number): X coordinate of the incident location
- `y` (number): Y coordinate of the incident location

**Response Format:**

_Success (201):_

```json
{
  "id": "incident_789",
  "x": 45.5,
  "y": 67.8,
  "status": "active",
  "created_at": "2026-01-29T11:00:00Z"
}
```

_Error - Invalid JSON (400):_

```json
{
  "error": "Invalid JSON payload"
}
```

_Error - Missing x coordinate (400):_

```json
{
  "error": "Missing x coordinate"
}
```

_Error - Invalid x coordinate (400):_

```json
{
  "error": "Invalid x coordinate"
}
```

_Error - Missing y coordinate (400):_

```json
{
  "error": "Missing y coordinate"
}
```

_Error - Invalid y coordinate (400):_

```json
{
  "error": "Invalid y coordinate"
}
```

_Error - Internal Server Error (500):_

```json
{
  "error": "Internal server error"
}
```

---

### 4. Update Incident

**HTTP Method and URL:**

```
PUT /incidents/<incident_id>
```

**Purpose:** Update the coordinates of an existing incident.

**Payload Format:**

```json
{
  "x": 50.0,
  "y": 75.5
}
```

**Required Fields:**

- `x` (number): New X coordinate of the incident location
- `y` (number): New Y coordinate of the incident location

**Response Format:**

_Success (200):_

```json
{
  "id": "incident_123",
  "x": 50.0,
  "y": 75.5,
  "status": "active",
  "created_at": "2026-01-29T10:30:00Z",
  "updated_at": "2026-01-29T11:30:00Z"
}
```

_Error - Invalid JSON (400):_

```json
{
  "error": "Invalid JSON payload"
}
```

_Error - Missing x coordinate (400):_

```json
{
  "error": "Missing x coordinate"
}
```

_Error - Invalid x coordinate (400):_

```json
{
  "error": "Invalid x coordinate"
}
```

_Error - Missing y coordinate (400):_

```json
{
  "error": "Missing y coordinate"
}
```

_Error - Invalid y coordinate (400):_

```json
{
  "error": "Invalid y coordinate"
}
```

_Error - Internal Server Error (500):_

```json
{
  "error": "Internal server error"
}
```

---

### 5. Delete Incident

**HTTP Method and URL:**

```
DELETE /incidents/<incident_id>
```

**Purpose:** Delete an incident from the system using its unique identifier.

**Payload Format:** No payload required.

**Response Format:**

_Success (200):_

```json
{
  "message": "Incident deleted successfully"
}
```

_Error - Not Found (404):_

```json
{
  "error": "Incident not found"
}
```
---
## Setup Instructions
Clone the repository and navigate to project directory
  ```bash
  git clone git@github.com:Shaker-10/S.T.Jabah.git
  ```
Install uv package manager
  ```bash
  pip install uv
  ```
If not sure if you have it
  ```bash
  uv --version
  ```
Run application
  ```bash
  uv run python main.py
  ```
