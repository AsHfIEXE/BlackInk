import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import json

class Vault:
    def __init__(self, vault_path, password):
        self.vault_path = vault_path
        self.password = password
        self.key = None
        self.salt = None

        if not os.path.exists(self.vault_path):
            self._create_vault()
        else:
            self._load_vault()

    def _create_vault(self):
        self.salt = get_random_bytes(16)
        self.key = self._derive_key(self.password, self.salt)
        with open(self.vault_path, 'wb') as f:
            f.write(self.salt)

    def _load_vault(self):
        with open(self.vault_path, 'rb') as f:
            self.salt = f.read(16)
        self.key = self._derive_key(self.password, self.salt)

    def _derive_key(self, password, salt):
        return PBKDF2(password, salt, dkLen=32, count=1000000)

    def encrypt_note(self, note_name, content):
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(content.encode('utf-8'))

        vault_data = self._read_vault_data()
        vault_data[note_name] = {
            'nonce': cipher.nonce.hex(),
            'tag': tag.hex(),
            'ciphertext': ciphertext.hex()
        }
        self._write_vault_data(vault_data)

    def decrypt_note(self, note_name):
        vault_data = self._read_vault_data()
        note_data = vault_data.get(note_name)
        if not note_data:
            return "Decryption failed. Incorrect password or corrupted data."

        nonce = bytes.fromhex(note_data['nonce'])
        tag = bytes.fromhex(note_data['tag'])
        ciphertext = bytes.fromhex(note_data['ciphertext'])

        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        try:
            decrypted_content = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted_content.decode('utf-8')
        except (ValueError, KeyError):
            return "Decryption failed. Incorrect password or corrupted data."

    def _read_vault_data(self):
        with open(self.vault_path, 'rb') as f:
            f.seek(16)  # Skip the salt
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()

        if not ciphertext:
            return {}

        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        try:
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
            return json.loads(decrypted_data.decode('utf-8'))
        except (ValueError, KeyError, json.JSONDecodeError):
            # If the vault is empty or corrupted, return an empty dict
            return {}

    def _write_vault_data(self, data):
        json_data = json.dumps(data).encode('utf-8')
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(json_data)

        with open(self.vault_path, 'wb') as f:
            f.write(self.salt)
            f.write(cipher.nonce)
            f.write(tag)
            f.write(ciphertext)
