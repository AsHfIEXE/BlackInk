import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Hash import HMAC, SHA256
import json
import time
from src.exceptions import InvalidPasswordError

class Vault:
    def __init__(self, key):
        self.key = key
        self.notes = {}
        self.links = {}

    @staticmethod
    def create(password, salt):
        key = PBKDF2(password, salt, dkLen=32, count=1000000)
        return Vault(key)

    def encrypt(self, data):
        # Use a new nonce for each encryption
        cipher = AES.new(self.key, AES.MODE_GCM)
        ciphertext, tag = cipher.encrypt_and_digest(data)

        # Create an HMAC of the ciphertext
        hmac = HMAC.new(self.key, digestmod=SHA256)
        hmac.update(ciphertext)

        return {
            'nonce': cipher.nonce.hex(),
            'tag': tag.hex(),
            'ciphertext': ciphertext.hex(),
            'hmac': hmac.hexdigest()
        }

    def decrypt(self, encrypted_data):
        nonce = bytes.fromhex(encrypted_data['nonce'])
        tag = bytes.fromhex(encrypted_data['tag'])
        ciphertext = bytes.fromhex(encrypted_data['ciphertext'])
        hmac = encrypted_data['hmac']

        # Verify the HMAC
        h = HMAC.new(self.key, digestmod=SHA256)
        h.update(ciphertext)
        try:
            h.hexverify(hmac)
        except ValueError:
            raise InvalidPasswordError("HMAC verification failed. The data may have been tampered with.")

        cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
        try:
            return cipher.decrypt_and_verify(ciphertext, tag)
        except (ValueError, KeyError):
            raise InvalidPasswordError("Decryption failed. Incorrect password or corrupted data.")

    def add_note(self, note_name, content, fade_time=None):
        delete_at = None
        if fade_time:
            delete_at = time.time() + fade_time

        self.notes[note_name] = {
            'content': content,
            'delete_at': delete_at
        }

    def get_note(self, note_name):
        note = self.notes.get(note_name)
        if not note:
            return None

        if note.get('delete_at') and time.time() > note.get('delete_at'):
            del self.notes[note_name]
            return "This note has faded."

        return note['content']

    def list_notes(self):
        return self.notes.keys()

    def search_notes(self, query):
        results = []
        for note_name, note_data in self.notes.items():
            if query in note_data['content']:
                results.append(note_name)
        return results

    def purge_note(self, note_name):
        if note_name in self.notes:
            # Overwrite with random data
            self.notes[note_name]['content'] = os.urandom(len(self.notes[note_name]['content'])).hex()
            del self.notes[note_name]

    def link_notes(self, note1_name, note2_name):
        if note1_name in self.notes and note2_name in self.notes:
            if note1_name not in self.links:
                self.links[note1_name] = []
            if note2_name not in self.links:
                self.links[note2_name] = []

            self.links[note1_name].append(note2_name)
            self.links[note2_name].append(note1_name)

    def to_json(self):
        return json.dumps({'notes': self.notes, 'links': self.links}).encode('utf-8')

    @classmethod
    def from_json(cls, key, json_data):
        data = json.loads(json_data)
        vault = cls(key)
        vault.notes = data.get('notes', {})
        vault.links = data.get('links', {})
        return vault
