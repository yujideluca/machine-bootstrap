import unittest

from mb.scan import find_secrets


class ScanTest(unittest.TestCase):
    # REQ MB-3
    def test_flags_private_keys_and_tokens(self):
        bad = [
            "-----BEGIN OPENSSH PRIVATE KEY-----\nabc\n",
            "-----BEGIN PGP PRIVATE KEY BLOCK-----",
            "export GH=ghp_" + "a" * 36,
            "key = sk-ant-api03-" + "x" * 30,
            "AKIA" + "A" * 16,
            "bot 1234567890:" + "A" * 35,
            'password = "hunter2hunter2"',
            "API_KEY=abcdef123456",
        ]
        for text in bad:
            self.assertTrue(find_secrets(text), text)

    # REQ MB-3
    def test_ordinary_config_is_clean(self):
        clean = [
            "[user]\nname = yujideluca\nemail = a@b.c\n",
            "export PATH=\"$HOME/.local/bin:$PATH\"",
            "token = $TOKEN_FROM_ENV",
            "# password is asked at runtime",
            "Signed-By: /usr/share/keyrings/google-chrome.gpg",
            "qpdf --password=secret123 --decrypt encrypted.pdf decrypted.pdf",   # example in a manual
            "let TOKEN = tokenInfo.value;",
            "        TOKEN = generateToken();",
            'token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")',
        ]
        for text in clean:
            self.assertEqual(find_secrets(text), [], text)

    # REQ MB-3
    def test_report_names_the_kind_not_the_value(self):
        hits = find_secrets("export GH=ghp_" + "b" * 36)
        self.assertEqual(len(hits), 1)
        self.assertNotIn("bbbb", hits[0])


if __name__ == "__main__":
    unittest.main()
