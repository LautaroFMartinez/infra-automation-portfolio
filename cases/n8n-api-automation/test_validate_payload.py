import unittest

from validate_payload import validate


class PayloadValidationTests(unittest.TestCase):
    def test_valid_payload_has_no_errors(self):
        payload = {
            "event": "service_request.created",
            "source": "sanitized-form",
            "customer": {"name": "Example customer", "email": "customer@example.test"},
            "requested_service": "backup verification",
            "requires_human_review": True,
        }

        self.assertEqual(validate(payload), [])

    def test_missing_and_malformed_fields_are_reported(self):
        errors = validate(
            {
                "event": "",
                "customer": {"name": "", "email": "not-empty"},
                "requires_human_review": "yes",
            }
        )

        self.assertIn("missing field: source", errors)
        self.assertIn("missing field: requested_service", errors)
        self.assertIn("event must be a non-empty string", errors)
        self.assertIn("customer.name must be a non-empty string", errors)
        self.assertIn("requires_human_review must be boolean", errors)

    def test_non_object_payload_is_rejected(self):
        self.assertEqual(validate(["not", "an", "object"]), ["payload must be a JSON object"])


if __name__ == "__main__":
    unittest.main()
