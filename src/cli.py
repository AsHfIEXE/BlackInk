import os
from src.vault import Vault

def main():
    print("Welcome to BlackInk")
    vault_path = input("Enter vault path: ")
    password = input("Enter password: ")

    vault = Vault(vault_path, password)

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
            vault.encrypt_note(note_name, "\n".join(content))
            print("Note saved.")
        elif choice == '2':
            note_name = input("Enter note name: ")
            content = vault.decrypt_note(note_name)
            if content:
                print("\n--- Note Content ---")
                print(content)
                print("--------------------")
            else:
                print("Note not found or decryption failed.")
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
