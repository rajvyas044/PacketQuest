import unittest
from random import Random

from arq_simulation import iter_event_names, simulate_order


class SequenceRandom:
    def __init__(self, values: list[float]) -> None:
        self._values = iter(values)

    def random(self) -> float:
        return next(self._values)


class StopAndWaitArqTests(unittest.TestCase):
    def test_clean_channel_delivers_on_first_attempt(self) -> None:
        result = simulate_order(loss_probability=0, rng=Random(1))

        self.assertTrue(result.delivered)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.duplicate_count, 0)
        self.assertEqual(
            list(iter_event_names(result)),
            ["send", "receive", "accepted", "ack_send", "ack_received"],
        )

    def test_lost_ack_creates_duplicate_on_retry(self) -> None:
        result = simulate_order(
            loss_probability=0.5,
            rng=SequenceRandom([0.9, 0.1, 0.9, 0.9]),
            max_attempts=3,
        )

        self.assertTrue(result.delivered)
        self.assertEqual(result.attempts, 2)
        self.assertEqual(result.duplicate_count, 1)
        self.assertIn("ack_lost", list(iter_event_names(result)))
        self.assertIn("duplicate", list(iter_event_names(result)))

    def test_invalid_configuration_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            simulate_order(loss_probability=1.1)
        with self.assertRaises(ValueError):
            simulate_order(sequence_number=2)
        with self.assertRaises(ValueError):
            simulate_order(max_attempts=0)

    def test_max_attempts_prevents_infinite_retry(self) -> None:
        with self.assertRaises(RuntimeError):
            simulate_order(loss_probability=1, max_attempts=2)


if __name__ == "__main__":
    unittest.main()
