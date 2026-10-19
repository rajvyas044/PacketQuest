"""Flask application for the PacketQuest ARQ learning project."""

from __future__ import annotations

from pathlib import Path
from random import Random
from typing import Any

from flask import Flask, jsonify, request, send_file

from arq_simulation import simulate_order


PROJECT_DIR = Path(__file__).resolve().parent
HTML_FILE = PROJECT_DIR / "packet_quest_arq.html"

app = Flask(__name__)


@app.get("/")
def home() -> Any:
    """Serve the PacketQuest browser interface."""

    return send_file(HTML_FILE)


@app.get("/api/health")
def health() -> Any:
    """Return a simple service status for local development checks."""

    return jsonify({"status": "ok", "service": "packetquest"})


@app.post("/api/simulate")
def simulate() -> Any:
    """Run one ARQ order and return its event history as JSON."""

    payload = request.get_json(silent=True) or {}

    try:
        order_number = int(payload.get("order_number", 1))
        sequence_number = int(payload.get("sequence_number", 0))
        loss_probability = float(payload.get("loss_probability", 0.3))
        max_attempts = int(payload.get("max_attempts", 100))
        seed = payload.get("seed")
        rng = Random(int(seed)) if seed is not None else Random()

        result = simulate_order(
            order_number=order_number,
            sequence_number=sequence_number,
            loss_probability=loss_probability,
            rng=rng,
            max_attempts=max_attempts,
        )
    except (TypeError, ValueError, RuntimeError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(
        {
            "order_number": result.order_number,
            "sequence_number": result.sequence_number,
            "attempts": result.attempts,
            "delivered": result.delivered,
            "duplicate_count": result.duplicate_count,
            "events": [
                {
                    "name": event.name,
                    "order_number": event.order_number,
                    "sequence_number": event.sequence_number,
                    "attempt": event.attempt,
                    "detail": event.detail,
                }
                for event in result.events
            ],
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
