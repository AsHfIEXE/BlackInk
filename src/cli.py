import argparse
from src.vault_manager import VaultManager
from src.exceptions import InvalidPasswordError
import os

def main():
    parser = argparse.ArgumentParser(description="BlackInk - A secure writing tool.")
    parser.add_argument("vault_path", help="Path to the vault file.")
    parser.add_argument("--create", action="store_true", help="Create a new vault.")
    parser.add_argument("--decoy-password", help="Set a decoy password for the vault.")
    parser.add_argument("--fade", type=int, help="Set a fade time in seconds for a new note.")

    args = parser.parse_args()

    manager = VaultManager(args.vault_path)

    if args.create:
        password = input("Enter new password: ")
        if args.decoy_password:
            decoy_password = input("Enter decoy password: ")
            manager.create_vault(password, decoy_password)
            print("Vault with decoy created.")
        else:
            manager.create_vault(password)
            print("Vault created.")
        return

    password = input("Enter password: ")
    try:
        vault = manager.load_vault(password)
    except InvalidPasswordError as e:
        print(e)
        return
    except FileNotFoundError:
        print("Vault not found. Use --create to create a new vault.")
        return

    while True:
        print("\n1. Add/Update Note")
        print("2. Read Note")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == '1':
            note_name = input("Enter note name: ")
            print("Enter content (end with 'EOF' on a new line):")
            content = []
            while True:
                line = input()
                if line == 'EOF':
                    break
                content.append(line)
            vault.add_note(note_name, "\n".join(content), args.fade)
            manager.save_vault(vault, password)
            print("Note saved.")
        elif choice == '2':
            note_name = input("Enter note name: ")
            content = vault.get_note(note_name)
            if content:
                print("\n--- Note Content ---")
                print(content)
                print("--------------------")
            else:
                print("Note not found.")
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
