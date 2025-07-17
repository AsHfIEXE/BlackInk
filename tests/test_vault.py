import unittest
import os
from src.vault import Vault

class TestVault(unittest.TestCase):

    def setUp(self):
        self.vault_path = "test_vault.bin"
        self.password = "test_password"
        self.vault = Vault(self.vault_path, self.password)

    def tearDown(self):
        if os.path.exists(self.vault_path):
            os.remove(self.vault_path)

    def test_create_and_load_vault(self):
        self.assertTrue(os.path.exists(self.vault_path))
        self.assertIsNotNone(self.vault.key)
        self.assertIsNotNone(self.vault.salt)

        # Test loading an existing vault
        new_vault = Vault(self.vault_path, self.password)
        self.assertEqual(self.vault.key, new_vault.key)
        self.assertEqual(self.vault.salt, new_vault.salt)

    def test_encrypt_and_decrypt_note(self):
        note_name = "my_secret_note"
        content = "This is a secret message."
        self.vault.encrypt_note(note_name, content)

        decrypted_content = self.vault.decrypt_note(note_name)
        self.assertEqual(content, decrypted_content)

    def test_decrypt_nonexistent_note(self):
        decrypted_content = self.vault.decrypt_note("nonexistent_note")
        self.assertIn("Decryption failed", decrypted_content)

    def test_decrypt_with_wrong_password(self):
        note_name = "my_secret_note"
        content = "This is a secret message."
        self.vault.encrypt_note(note_name, content)

        wrong_password_vault = Vault(self.vault_path, "wrong_password")
        decrypted_content = wrong_password_vault.decrypt_note(note_name)
        self.assertIn("Decryption failed", decrypted_content)

if __name__ == '__main__':
    unittest.main()
