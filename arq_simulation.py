"""Stop-and-Wait ARQ utilities for PacketQuest.

The browser page is the interactive presentation layer. This module keeps the
protocol rules independently testable and can be reused by scripts or a future
Python backend.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterator, Protocol


class RandomSource(Protocol):
    def random(self) -> float:
        """Return a pseudo-random float in the interval [0.0, 1.0)."""


@dataclass(frozen=True)
class TransmissionEvent:
    """A single observable step in one order transmission."""

    name: str
    order_number: int
    sequence_number: int
    attempt: int
    detail: str


@dataclass(frozen=True)
class TransmissionResult:
    """Final outcome and event history for one order."""

    order_number: int
    sequence_number: int
    attempts: int
    delivered: bool
    duplicate_count: int
    events: tuple[TransmissionEvent, ...]


def _validate_loss_probability(loss_probability: float) -> None:
    if not 0 <= loss_probability <= 1:
        raise ValueError("loss_probability must be between 0 and 1")


def simulate_order(
    order_number: int = 1,
    sequence_number: int = 0,
    loss_probability: float = 0.3,
    *,
    rng: RandomSource | None = None,
    max_attempts: int = 100,
) -> TransmissionResult:
    """Simulate one Stop-and-Wait ARQ order.

    Packet and ACK delivery each use ``loss_probability`` independently. When
    an ACK is lost, the receiver sees the retransmission as a duplicate and
    sends another ACK without accepting the order twice.
    """

    if order_number < 1:
        raise ValueError("order_number must be positive")
    if sequence_number not in (0, 1):
        raise ValueError("sequence_number must be 0 or 1")
    if max_attempts < 1:
        raise ValueError("max_attempts must be positive")
    _validate_loss_probability(loss_probability)

    random = rng or Random()
    expected_sequence = sequence_number
    events: list[TransmissionEvent] = []
    duplicate_count = 0

    for attempt in range(1, max_attempts + 1):
        events.append(
            TransmissionEvent(
                "send",
                order_number,
                sequence_number,
                attempt,
                "Sender transmitted the frame.",
            )
        )

        if random.random() < loss_probability:
            events.append(
                TransmissionEvent(
                    "packet_lost",
                    order_number,
                    sequence_number,
                    attempt,
                    "Frame was lost before reaching the receiver.",
                )
            )
            continue

        events.append(
            TransmissionEvent(
                "receive",
                order_number,
                sequence_number,
                attempt,
                "Receiver received the frame.",
            )
        )

        if sequence_number != expected_sequence:
            duplicate_count += 1
            events.append(
                TransmissionEvent(
                    "duplicate",
                    order_number,
                    sequence_number,
                    attempt,
                    "Receiver discarded a duplicate frame.",
                )
            )
        else:
            events.append(
                TransmissionEvent(
                    "accepted",
                    order_number,
                    sequence_number,
                    attempt,
                    "Receiver accepted the new frame.",
                )
            )
            expected_sequence = 1 - expected_sequence

        events.append(
            TransmissionEvent(
                "ack_send",
                order_number,
                sequence_number,
                attempt,
                "Receiver sent an ACK.",
            )
        )

        if random.random() < loss_probability:
            events.append(
                TransmissionEvent(
                    "ack_lost",
                    order_number,
                    sequence_number,
                    attempt,
                    "ACK was lost before reaching the sender.",
                )
            )
            continue

        events.append(
            TransmissionEvent(
                "ack_received",
                order_number,
                sequence_number,
                attempt,
                "Sender received the ACK.",
            )
        )
        return TransmissionResult(
            order_number,
            sequence_number,
            attempt,
            True,
            duplicate_count,
            tuple(events),
        )

    raise RuntimeError(
        f"transmission did not complete within {max_attempts} attempts"
    )


def iter_event_names(result: TransmissionResult) -> Iterator[str]:
    """Yield event names for simple console output or adapters."""

    yield from (event.name for event in result.events)
