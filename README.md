# PacketQuest

### Interactive Stop-and-Wait ARQ Learning Lab

PacketQuest is an interactive educational project that explains reliable data delivery through a visual **Stop-and-Wait Automatic Repeat Request (ARQ)** simulation.

It combines:

- A responsive browser-based simulation interface
- A dark, professional learning experience
- A Python implementation of the ARQ protocol
- A Flask application and JSON API
- Automated tests for the simulation and web application

The project uses an Amazon order analogy to make networking concepts easier to understand: the customer sends an order, the server validates it, and an acknowledgment confirms successful delivery.

## Features

### Interactive simulation

- Visual sender-to-receiver data transmission
- Return ACK transmission path
- Packet and acknowledgment loss simulation
- Configurable packet loss probability
- Timeout and automatic retransmission
- 1-bit sequence number tracking
- Duplicate packet detection
- Live transmission stages:
  1. Send
  2. Receive
  3. Acknowledge
  4. Complete
- Transmission event log
- Delivery statistics and average delivery time
- Responsive layout for desktop, tablet, and mobile screens

### Python protocol utilities

The Python implementation in `arq_simulation.py` provides:

- Deterministic simulations using a seeded random source
- Observable transmission events
- Packet loss and ACK loss handling
- Duplicate detection
- Retry limits to prevent infinite simulations
- Input validation for protocol configuration

### Flask application

The Flask app:

- Serves the PacketQuest web interface
- Provides a health-check endpoint
- Exposes the ARQ simulation through a JSON API

## Project structure

```text
PacketQuest/
├── app.py                  # Flask application and API routes
├── arq_simulation.py       # Stop-and-Wait ARQ Python utilities
├── packet_quest_arq.html   # Main interactive browser simulation
├── test_app.py             # Flask application tests
├── test_arq_simulation.py  # ARQ protocol tests
├── requirements.txt        # Python dependencies
├── AmazonOrder.html        # Additional project demonstration page
├── StopAndWait.html        # Additional Stop-and-Wait reference page
├── PacketQuest_Report.pdf  # Project report
└── README.md               # Project documentation
```

## How Stop-and-Wait ARQ works

1. The sender transmits one frame with a sequence number.
2. The sender waits for an acknowledgment.
3. The receiver checks the sequence number.
4. If the frame is new, the receiver accepts it and sends an ACK.
5. If the frame or ACK is lost, the sender waits for a timeout.
6. The sender retransmits the same frame using the same sequence number.
7. The receiver identifies retransmissions as duplicates and does not process the order twice.
8. After a valid ACK arrives, the sender toggles the sequence number and sends the next frame.

## Requirements

- Python 3.9 or newer
- Flask 3.x
- A modern web browser

## Run locally

### 1. Clone the repository

```bash
git clone https://github.com/omvaghelaa/PacketQuest.git
cd PacketQuest
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Start the Flask server

```bash
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

## API reference

### Health check

```http
GET /api/health
```

Example response:

```json
{
  "service": "packetquest",
  "status": "ok"
}
```

### Run a simulation

```http
POST /api/simulate
Content-Type: application/json
```

Request body:

```json
{
  "order_number": 7,
  "sequence_number": 1,
  "loss_probability": 0.3,
  "max_attempts": 100,
  "seed": 42
}
```

Parameter details:

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `order_number` | Integer | `1` | Positive order identifier |
| `sequence_number` | Integer | `0` | Sequence number, either `0` or `1` |
| `loss_probability` | Number | `0.3` | Packet and ACK loss probability from `0` to `1` |
| `max_attempts` | Integer | `100` | Maximum number of transmission attempts |
| `seed` | Integer | Random | Optional seed for repeatable results |

Example response:

```json
{
  "order_number": 7,
  "sequence_number": 1,
  "attempts": 1,
  "delivered": true,
  "duplicate_count": 0,
  "events": [
    {
      "name": "send",
      "order_number": 7,
      "sequence_number": 1,
      "attempt": 1,
      "detail": "Sender transmitted the frame."
    },
    {
      "name": "ack_received",
      "order_number": 7,
      "sequence_number": 1,
      "attempt": 1,
      "detail": "Sender received the ACK."
    }
  ]
}
```

## Run tests

Run the complete test suite:

```bash
python -m unittest discover -v
```

Run only the ARQ protocol tests:

```bash
python -m unittest -v test_arq_simulation.py
```

Run only the Flask tests:

```bash
python -m unittest -v test_app.py
```

Compile-check the Python files:

```bash
python -m py_compile app.py arq_simulation.py test_app.py test_arq_simulation.py
```

## Educational objectives

After using PacketQuest, learners should be able to explain:

- Why acknowledgments are required for reliable delivery
- How timeouts trigger retransmission
- Why retransmissions can create duplicate frames
- How sequence numbers distinguish new frames from duplicates
- How packet and ACK loss affect delivery time
- Why Stop-and-Wait ARQ is reliable but can have low throughput

## Design notes

PacketQuest intentionally keeps the browser UI and Python protocol implementation separate:

- The HTML page focuses on visualization and interaction.
- The Python module provides reusable, testable protocol behavior.
- The Flask app connects the web experience to the Python simulation.
- The event-based result format makes the protocol behavior easy to inspect or adapt.

## License

This project is intended for educational and academic use.
