import unittest
import os
import json
from src.vault_manager import VaultManager
from src.exceptions import InvalidPasswordError

class TestVaultManager(unittest.TestCase):

    def setUp(self):
        self.vault_path = "test_vault.bin"
        self.manager = VaultManager(self.vault_path)

    def tearDown(self):
        if os.path.exists(self.vault_path):
            os.remove(self.vault_path)
        if os.path.exists(self.vault_path + ".decoy"):
            os.remove(self.vault_path + ".decoy")

    def test_create_and_load_vault(self):
        password = "test_password"
        self.manager.create_vault(password)
        self.assertTrue(os.path.exists(self.vault_path))

        vault, is_decoy = self.manager.load_vault(password)
        self.assertIsNotNone(vault)
        self.assertFalse(is_decoy)
        self.assertEqual("Welcome to your new BlackInk vault.", vault.get_note("welcome_note"))

    def test_create_and_load_decoy_vault(self):
        main_password = "main_password"
        decoy_password = "decoy_password"
        self.manager.create_vault(main_password, decoy_password)
        self.assertTrue(os.path.exists(self.vault_path))
        self.assertTrue(os.path.exists(self.vault_path + ".decoy"))

        # Load main vault
        main_vault, is_decoy = self.manager.load_vault(main_password)
        self.assertIsNotNone(main_vault)
        self.assertFalse(is_decoy)
        self.assertEqual("Welcome to your new BlackInk vault.", main_vault.get_note("welcome_note"))

        # Load decoy vault
        decoy_vault, is_decoy = self.manager.load_vault(decoy_password)
        self.assertIsNotNone(decoy_vault)
        self.assertTrue(is_decoy)
        # Check for one of the notes from the templates
        notes = ["meeting_notes", "todo_list", "brainstorming", "daily_reflection", "gratitude_journal", "favorite_quote", "poem_idea", "doodle_description", "story_prompt"]
        self.assertTrue(any(note in decoy_vault.notes for note in notes))

    def test_wrong_password(self):
        password = "test_password"
        self.manager.create_vault(password)
        with self.assertRaises(InvalidPasswordError):
            self.manager.load_vault("wrong_password")

    def test_save_and_load_note(self):
        password = "test_password"
        self.manager.create_vault(password)
        vault, _ = self.manager.load_vault(password)

        note_name = "my_note"
        content = "This is a test note."
        vault.add_note(note_name, content)
        self.manager.save_vault(vault, password)

        new_vault, _ = self.manager.load_vault(password)
        self.assertEqual(content, new_vault.get_note(note_name))

    def test_hmac_mismatch(self):
        password = "test_password"
        self.manager.create_vault(password)

        # Tamper with the vault data
        with open(self.vault_path, 'r+') as f:
            vault_content = json.load(f)
            vault_content['data']['ciphertext'] = '0' * len(vault_content['data']['ciphertext'])
            f.seek(0)
            json.dump(vault_content, f)
            f.truncate()

        with self.assertRaises(InvalidPasswordError):
            self.manager.load_vault(password)

    def test_wrong_key_correct_length(self):
        password = "test_password"
        wrong_password = "wrong_password" # Same length
        self.manager.create_vault(password)
        with self.assertRaises(InvalidPasswordError):
            self.manager.load_vault(wrong_password)

if __name__ == '__main__':
    unittest.main()
