import unittest

from app import app


class FlaskAppTests(unittest.TestCase):
    def setUp(self) -> None:
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_serves_packetquest(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PacketQuest", response.data)
        response.close()

    def test_health_endpoint(self) -> None:
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "ok")

    def test_simulation_endpoint_returns_events(self) -> None:
        response = self.client.post(
            "/api/simulate",
            json={
                "order_number": 7,
                "sequence_number": 1,
                "loss_probability": 0,
                "seed": 42,
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["delivered"])
        self.assertEqual(body["order_number"], 7)
        self.assertEqual(body["events"][-1]["name"], "ack_received")

    def test_simulation_endpoint_rejects_invalid_input(self) -> None:
        response = self.client.post(
            "/api/simulate",
            json={"loss_probability": 2},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
