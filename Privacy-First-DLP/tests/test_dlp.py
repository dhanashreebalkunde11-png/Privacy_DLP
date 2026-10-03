import unittest

from modules.dlp_service import scan_document


class ScanDocumentTests(unittest.TestCase):
    def test_finds_and_redacts_supported_sensitive_values(self):
        text = (
            "Contact alice@example.com or +1 (555) 123-4567. "
            "Password: hunter2 API_Key: sk-live-123456789"
        )

        result = scan_document(text)

        self.assertEqual(result["finding_count"], 4)
        self.assertEqual(
            {finding["type"] for finding in result["findings"]},
            {"Email", "Phone-like number", "Password", "API key"},
        )
        self.assertEqual(result["decision"], "BLOCK")
        for secret in ("alice@example.com", "123-4567", "hunter2", "sk-live-123456789"):
            self.assertNotIn(secret, result["redacted_text"])

    def test_credential_mask_wins_when_value_looks_like_email(self):
        result = scan_document("API_Key: alice@example.com")

        self.assertEqual([item["type"] for item in result["findings"]], ["API key"])
        self.assertNotIn("alice@example.com", result["redacted_text"])
        self.assertNotIn("@example.com", result["redacted_text"])

    def test_numeric_email_is_not_counted_twice_as_a_phone(self):
        result = scan_document("123456789@example.com")

        self.assertEqual([item["type"] for item in result["findings"]], ["Email"])
        self.assertEqual(result["decision"], "MASK")

    def test_text_without_supported_patterns_is_allowed_with_caveat(self):
        result = scan_document("A harmless sentence.")

        self.assertEqual(result["finding_count"], 0)
        self.assertEqual(result["risk_score"], 0)
        self.assertEqual(result["decision"], "ALLOW")
        self.assertIn("does not guarantee", result["reason"])


if __name__ == "__main__":
    unittest.main()
