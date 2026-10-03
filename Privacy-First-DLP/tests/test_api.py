import unittest

from fastapi import HTTPException
from pydantic import ValidationError

from api.main import ScanRequest, health_check, scan


class ApiTests(unittest.TestCase):
    def test_health_endpoint(self):
        self.assertEqual(health_check(), {"status": "ok"})

    def test_scan_returns_typed_result_fields(self):
        result = scan(ScanRequest(text="Password: sample-secret"))

        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(result["decision"], "BLOCK")
        self.assertEqual(result["scanned_characters"], len("Password: sample-secret"))
        self.assertNotIn("sample-secret", result["redacted_text"])

    def test_scan_rejects_whitespace_only_text(self):
        with self.assertRaises(HTTPException) as context:
            scan(ScanRequest(text="   "))

        self.assertEqual(context.exception.status_code, 422)

    def test_request_rejects_oversized_text_and_extra_fields(self):
        with self.assertRaises(ValidationError):
            ScanRequest(text="x" * 200_001)
        with self.assertRaises(ValidationError):
            ScanRequest(text="valid", unexpected="field")


if __name__ == "__main__":
    unittest.main()
