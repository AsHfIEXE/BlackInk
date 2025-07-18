import os
import git
import gnupg
from pathlib import Path

class SyncManager:
    def __init__(self, vault_path, gpg_home=None):
        self.vault_path = Path(vault_path).parent
        self.gpg = gnupg.GPG(gnupghome=gpg_home)
        self.repo = self._get_or_init_repo()

    def _get_or_init_repo(self):
        if (self.vault_path / ".git").exists():
            return git.Repo(self.vault_path)
        else:
            return git.Repo.init(self.vault_path)

    def set_remote(self, remote_url):
        if 'origin' in self.repo.remotes:
            self.repo.delete_remote('origin')
        self.repo.create_remote('origin', remote_url)

    def sync(self, recipients):
        self._encrypt_files(recipients)
        self._commit_and_push()

    def _encrypt_files(self, recipients):
        for file_path in self.vault_path.glob('*.bin*'):
            with open(file_path, 'rb') as f:
                self.gpg.encrypt_file(
                    f,
                    recipients=recipients,
                    output=str(file_path) + ".gpg",
                    always_trust=True
                )
            os.remove(file_path)

    def decrypt_files(self):
        for file_path in self.vault_path.glob('*.gpg'):
            with open(file_path, 'rb') as f:
                self.gpg.decrypt_file(
                    f,
                    output=str(file_path).replace(".gpg", "")
                )
            os.remove(file_path)

    def _commit_and_push(self):
        self.repo.git.add(A=True)
        if self.repo.is_dirty(untracked_files=True):
            self.repo.index.commit("BlackInk Sync")
            self.repo.remotes.origin.push()
