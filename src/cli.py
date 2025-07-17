import os
import logging
import questionary
import time
from src.vault_manager import VaultManager
from src.exceptions import InvalidPasswordError
from src.entry_templates import TEMPLATES

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    style = questionary.Style([
        ('question', 'fg:#673ab7 bold'),
        ('pointer', 'fg:#cc5454 bold'),
        ('highlighted', 'fg:#cc5454 bold'),
        ('selected', 'fg:#cc5454'),
        ('separator', 'fg:#cc5454'),
        ('instruction', 'fg:#cc5454'),
        ('text', 'fg:#ffffff'),
        ('answer', 'fg:#f44336 bold'),
    ])

    command = questionary.select(
        "What would you like to do?",
        choices=["create-vault", "unlock-vault", "reflect"],
        style=style
    ).ask()

    if command == "create-vault":
        vault_path = questionary.text("Vault name:", style=style).ask()
        log_attempts = questionary.confirm("Log incorrect password attempts?", style=style).ask()
        manager = VaultManager(vault_path, log_attempts=log_attempts)
        primary_password = questionary.password("Set primary password:", style=style).ask()
        decoy_password = questionary.password("Set decoy password (optional):", style=style).ask()

        if decoy_password:
            manager.create_vault(primary_password, decoy_password)
            print("Your thoughts are safe here. Vault with decoy initialized and encrypted.")
        else:
            manager.create_vault(primary_password)
            print("Your thoughts are safe here. Vault initialized and encrypted.")
        return

    if command == "reflect":
        vault_path = questionary.text("Vault name:", style=style).ask()
        password = questionary.password("Enter passphrase:", style=style).ask()
        try:
            vault, _ = manager.load_vault(password)
        except (InvalidPasswordError, FileNotFoundError):
            print("Could not unlock vault.")
            return

        print("How did today feel?")
        q1 = questionary.text("", style=style).ask()
        print("What drained you? What sparked you?")
        q2 = questionary.text("", style=style).ask()
        print("What did you avoid saying?")
        q3 = questionary.text("", style=style).ask()

        entry = f"How did today feel?\n{q1}\n\nWhat drained you? What sparked you?\n{q2}\n\nWhat did you avoid saying?\n{q3}"

        note_name = f"reflection_{time.strftime('%Y-%m-%d')}"
        vault.add_note(note_name, entry)
        manager.save_vault(vault, password)
        print("Your reflection has been saved securely. No one else sees this.")
        return

    vault_path = questionary.text("Vault name:", style=style).ask()
    log_attempts = questionary.confirm("Log incorrect password attempts?", style=style).ask()
    manager = VaultManager(vault_path, log_attempts=log_attempts)
    password = questionary.password("Enter passphrase:", style=style).ask()
    try:
        vault, is_decoy = manager.load_vault(password)
        print("🔒 Unlocking your vault...")
        time.sleep(1)
        print("💭 Loading your last whispers...")
        time.sleep(1)
        if is_decoy:
            logging.info("Decoy vault loaded.")
            print("➤ Vault loaded: Decoy Mode")
        else:
            logging.info("Main vault loaded.")
            print("➤ Vault loaded: Specter")
    except InvalidPasswordError as e:
        logging.error(f"Failed to load vault: {e}")
        print("Incorrect passphrase.")
        return
    except FileNotFoundError:
        logging.error("Vault not found.")
        print("Vault not found. Use --create to create a new vault.")
        return

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=["Add/Update Note", "Read Note", "List Notes", "Search Notes", "Purge Note", "Exit"],
            style=style
        ).ask()

        if choice == 'Add/Update Note':
            use_template = questionary.confirm("Use an entry template?", style=style).ask()
            if use_template:
                template_name = questionary.select(
                    "Choose a template:",
                    choices=list(TEMPLATES.keys()),
                    style=style
                ).ask()
                template = TEMPLATES[template_name]
                note_name = questionary.text("Enter note name:", default=template['name'], style=style).ask()
                content = questionary.text(template['prompt'], default=template['content'], multiline=True, style=style).ask()
            else:
                note_name = questionary.text("Enter note name:", style=style).ask()
                content = questionary.text("Enter content (press Enter twice to finish):", multiline=True, style=style).ask()

            fade_time_str = questionary.text("Enter fade time in seconds (optional):", style=style).ask()
            fade_time = int(fade_time_str) if fade_time_str else None

            vault.add_note(note_name, content, fade_time)
            manager.save_vault(vault, password)
            print("Note saved.")
        elif choice == 'Read Note':
            note_name = questionary.text("Enter note name:", style=style).ask()
            content = vault.get_note(note_name)
            if content:
                print("\n--- Note Content ---")
                print(content)
                print("--------------------")
            else:
                print("Note not found.")
        elif choice == 'List Notes':
            show_hidden = questionary.confirm("Show hidden notes?", style=style).ask()

            start_date_str = questionary.text("Filter by start date (YYYY-MM-DD, optional):", style=style).ask()
            end_date_str = questionary.text("Filter by end date (YYYY-MM-DD, optional):", style=style).ask()

            notes = vault.list_notes()

            if not show_hidden:
                notes = [note for note in notes if not note.startswith('.')]

            if start_date_str:
                notes = [note for note in notes if note >= start_date_str]

            if end_date_str:
                notes = [note for note in notes if note <= end_date_str]

            if notes:
                print("\n--- Your Notes ---")
                for note in notes:
                    print(f"- {note}")
                print("------------------")
            else:
                print("No notes found.")
        elif choice == 'Search Notes':
            query = questionary.text("Enter search query:", style=style).ask()
            tag_filter = questionary.text("Filter by tag (optional):", style=style).ask()

            results = vault.search_notes(query)

            if tag_filter:
                filtered_results = []
                for note_name in results:
                    content = vault.get_note(note_name)
                    if tag_filter in content:
                        filtered_results.append(note_name)
                results = filtered_results

            if results:
                print("\n--- Search Results ---")
                for note in results:
                    print(f"- {note}")
                print("--------------------")
            else:
                print("No results found.")
        elif choice == 'Purge Note':
            note_name = questionary.text("Enter note name to purge:", style=style).ask()
            confirm = questionary.confirm(f"Are you sure you want to permanently delete '{note_name}'?", style=style).ask()
            if confirm:
                vault.purge_note(note_name)

                fake_log = questionary.confirm("Create a plausible fake deletion log?", style=style).ask()
                if fake_log:
                    log_name = f"log_{time.strftime('%Y-%m-%d_%H-%M-%S')}"
                    log_content = f"Deleted shopping list on {time.strftime('%Y-%m-%d')}."
                    vault.add_note(log_name, log_content)

                manager.save_vault(vault, password)
                print(f"Note '{note_name}' has been securely purged.")
        elif choice == 'Exit':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
