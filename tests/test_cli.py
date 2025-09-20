import unittest
from unittest.mock import patch, MagicMock
from src import cli
from src.vault import Vault

class TestCli(unittest.TestCase):

    @patch('src.cli.questionary')
    @patch('src.cli.VaultManager')
    def test_create_vault_ui(self, mock_vault_manager, mock_questionary):
        # Arrange
        mock_questionary.text.return_value.ask.return_value = "test_vault"
        mock_questionary.confirm.return_value.ask.return_value = True
        mock_questionary.password.return_value.ask.side_effect = ["password123", "decoypassword"]

        mock_manager_instance = MagicMock()
        mock_vault_manager.return_value = mock_manager_instance

        # Act
        cli.create_vault_ui()

        # Assert
        mock_vault_manager.assert_called_with("test_vault")
        mock_manager_instance.create_vault.assert_called_with("password123", True, "decoypassword")

    @patch('src.cli.questionary')
    @patch('src.cli.VaultManager')
    def test_unlock_vault_ui_success(self, mock_vault_manager, mock_questionary):
        # Arrange
        mock_questionary.text.return_value.ask.return_value = "test_vault"
        mock_questionary.password.return_value.ask.return_value = "password123"

        mock_manager_instance = MagicMock()
        mock_vault_manager.return_value = mock_manager_instance
        mock_vault = Vault("some_key")
        mock_manager_instance.load_vault.return_value = (mock_vault, False)

        # Act
        vault, manager, password = cli.unlock_vault_ui()

        # Assert
        self.assertIsNotNone(vault)
        self.assertIsNotNone(manager)
        self.assertEqual(password, "password123")
        mock_manager_instance.load_vault.assert_called_with("password123")

    @patch('src.cli.questionary')
    def test_add_note_ui(self, mock_questionary):
        # Arrange
        mock_vault = MagicMock()
        mock_manager = MagicMock()
        password = "password123"

        mock_questionary.confirm.return_value.ask.return_value = False  # Don't use a template
        mock_questionary.text.side_effect = [
            MagicMock(ask=MagicMock(return_value="test_note")),
            MagicMock(ask=MagicMock(return_value="test_content")),
            MagicMock(ask=MagicMock(return_value="3600"))
        ]

        # Act
        cli.add_note_ui(mock_vault, mock_manager, password)

        # Assert
        mock_vault.add_note.assert_called_with("test_note", "test_content", 3600)
        mock_manager.save_vault.assert_called_with(mock_vault, password)

    @patch('src.cli.questionary')
    def test_list_notes_ui(self, mock_questionary):
        # Arrange
        mock_vault = MagicMock()
        mock_vault.list_notes.return_value = ["note1", "note2"]
        mock_questionary.confirm.return_value.ask.return_value = True # Show hidden notes
        mock_questionary.text.return_value.ask.side_effect = ["", ""] # No date filters

        # Act
        cli.list_notes_ui(mock_vault)

        # Assert
        mock_vault.list_notes.assert_called_once()


if __name__ == '__main__':
    unittest.main()
