import unittest
import os
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

        vault = self.manager.load_vault(password)
        self.assertIsNotNone(vault)
        self.assertEqual("Welcome to your new BlackInk vault.", vault.get_note("welcome_note"))

    def test_create_and_load_decoy_vault(self):
        main_password = "main_password"
        decoy_password = "decoy_password"
        self.manager.create_vault(main_password, decoy_password)
        self.assertTrue(os.path.exists(self.vault_path))
        self.assertTrue(os.path.exists(self.vault_path + ".decoy"))

        # Load main vault
        main_vault = self.manager.load_vault(main_password)
        self.assertIsNotNone(main_vault)
        self.assertEqual("Welcome to your new BlackInk vault.", main_vault.get_note("welcome_note"))

        # Load decoy vault
        decoy_vault = self.manager.load_vault(decoy_password)
        self.assertIsNotNone(decoy_vault)
        self.assertEqual("This is a decoy note.", decoy_vault.get_note("decoy_note"))

    def test_wrong_password(self):
        password = "test_password"
        self.manager.create_vault(password)
        with self.assertRaises(InvalidPasswordError):
            self.manager.load_vault("wrong_password")

    def test_save_and_load_note(self):
        password = "test_password"
        self.manager.create_vault(password)
        vault = self.manager.load_vault(password)

        note_name = "my_note"
        content = "This is a test note."
        vault.add_note(note_name, content)
        self.manager.save_vault(vault, password)

        new_vault = self.manager.load_vault(password)
        self.assertEqual(content, new_vault.get_note(note_name))

if __name__ == '__main__':
    unittest.main()
