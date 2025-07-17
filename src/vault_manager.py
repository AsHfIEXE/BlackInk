import os
from Crypto.Random import get_random_bytes
from src.vault import Vault
from src.exceptions import InvalidPasswordError
import json
from src.decoy_templates import get_random_template

class VaultManager:
    def __init__(self, vault_path, log_attempts=False):
        self.vault_path = vault_path
        self.log_attempts = log_attempts

    def create_vault(self, password, decoy_password=None):
        # Create the main vault
        self._create_vault_file(self.vault_path, password)

        # Create the decoy vault if a decoy password is provided
        if decoy_password:
            decoy_vault_path = self.vault_path + ".decoy"
            self._create_vault_file(decoy_vault_path, decoy_password, is_decoy=True)

    def _create_vault_file(self, path, password, is_decoy=False):
        salt = get_random_bytes(16)
        vault = Vault.create(password, salt)
        if is_decoy:
            template = get_random_template()
            for note_name, content in template['notes']:
                vault.add_note(note_name, content)
            # We are not using tags yet, but we can store them for later
            vault.add_note("tags", ", ".join(template['tags']))
        else:
            vault.add_note("welcome_note", "Welcome to your new BlackInk vault.")

        encrypted_data = vault.encrypt(vault.to_json())

        vault_content = {
            'salt': salt.hex(),
            'data': encrypted_data
        }

        with open(path, 'w') as f:
            json.dump(vault_content, f)

    def load_vault(self, password):
        try:
            vault = self._load_vault_file(self.vault_path, password)
            return vault, False
        except InvalidPasswordError:
            if self.log_attempts:
                logging.warning("Incorrect password attempt on main vault.")

            decoy_vault_path = self.vault_path + ".decoy"
            if os.path.exists(decoy_vault_path):
                try:
                    vault = self._load_vault_file(decoy_vault_path, password)
                    return vault, True
                except InvalidPasswordError:
                    # If the decoy vault also fails, load a dummy decoy vault
                    return self._load_dummy_decoy_vault(password)
            else:
                raise InvalidPasswordError("Incorrect password or corrupted vault.")

    def _load_dummy_decoy_vault(self, password):
        salt = get_random_bytes(16)
        vault = Vault.create(password, salt)
        template = get_random_template()
        for note_name, content in template['notes']:
            vault.add_note(note_name, content)
        vault.add_note("tags", ", ".join(template['tags']))
        return vault, True

    def _load_vault_file(self, path, password):
        with open(path, 'r') as f:
            vault_content = json.load(f)

        salt = bytes.fromhex(vault_content['salt'])
        encrypted_data = vault_content['data']

        key = Vault.create(password, salt).key
        vault = Vault(key)
        decrypted_data = vault.decrypt(encrypted_data)
        return Vault.from_json(key, decrypted_data)

    def save_vault(self, vault, password):
        # Determine if we are saving the main or decoy vault
        try:
            self._load_vault_file(self.vault_path, password)
            path = self.vault_path
            with open(path, 'r') as f:
                salt = bytes.fromhex(json.load(f)['salt'])
        except InvalidPasswordError:
            path = self.vault_path + ".decoy"
            with open(path, 'r') as f:
                salt = bytes.fromhex(json.load(f)['salt'])

        vault.key = Vault.create(password, salt).key # Re-key the vault
        encrypted_data = vault.encrypt(vault.to_json())

        vault_content = {
            'salt': salt.hex(),
            'data': encrypted_data
        }

        with open(path, 'w') as f:
            json.dump(vault_content, f)
