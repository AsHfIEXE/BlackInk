import os
import logging
import questionary
import time
from src.vault_manager import VaultManager
from src.exceptions import InvalidPasswordError
from src.entry_templates import TEMPLATES

STYLE = questionary.Style([
    ('question', 'fg:#673ab7 bold'),
    ('pointer', 'fg:#cc5454 bold'),
    ('highlighted', 'fg:#cc5454 bold'),
    ('selected', 'fg:#cc5454'),
    ('separator', 'fg:#cc5454'),
    ('instruction', 'fg:#cc5454'),
    ('text', 'fg:#ffffff'),
    ('answer', 'fg:#f44336 bold'),
])

def create_vault_ui():
    """Handles the UI for creating a new vault."""
    vault_path = questionary.text("Vault name:", style=STYLE).ask()
    manager = VaultManager(vault_path)
    primary_password = questionary.password("Set primary password:", style=STYLE).ask()
    decoy_password = questionary.password("Set decoy password (optional):", style=STYLE).ask()
    log_attempts = questionary.confirm("Log incorrect password attempts?", style=STYLE).ask()

    if decoy_password:
        manager.create_vault(primary_password, log_attempts, decoy_password)
        print("Your thoughts are safe here. Vault with decoy initialized and encrypted.")
    else:
        manager.create_vault(primary_password, log_attempts)
        print("Your thoughts are safe here. Vault initialized and encrypted.")

def unlock_vault_ui():
    """Handles the UI for unlocking an existing vault."""
    vault_path = questionary.text("Vault name:", style=STYLE).ask()
    manager = VaultManager(vault_path)
    password = questionary.password("Enter passphrase:", style=STYLE).ask()
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
        return vault, manager, password
    except InvalidPasswordError as e:
        logging.error(f"Failed to load vault: {e}")
        print("Incorrect passphrase.")
        return None, None, None
    except FileNotFoundError:
        logging.error("Vault not found.")
        print("Vault not found. Use --create to create a new vault.")
        return None, None, None

def add_note_ui(vault, manager, password):
    """Handles the UI for adding a note."""
    use_template = questionary.confirm("Use an entry template?", style=STYLE).ask()
    if use_template:
        template_name = questionary.select(
            "Choose a template:",
            choices=list(TEMPLATES.keys()),
            style=STYLE
        ).ask()
        template = TEMPLATES[template_name]
        note_name = questionary.text("Enter note name:", default=template['name'], style=STYLE).ask()
        content = questionary.text(template['prompt'], default=template['content'], multiline=True, style=STYLE).ask()
    else:
        note_name = questionary.text("Enter note name:", style=STYLE).ask()
        content = questionary.text("Enter content (press Enter twice to finish):", multiline=True, style=STYLE).ask()

    fade_time_str = questionary.text("Enter fade time in seconds (optional):", style=STYLE).ask()
    fade_time = int(fade_time_str) if fade_time_str else None

    vault.add_note(note_name, content, fade_time)
    manager.save_vault(vault, password)
    print("Note saved.")

def read_note_ui(vault):
    """Handles the UI for reading a note."""
    note_name = questionary.text("Enter note name:", style=STYLE).ask()
    content = vault.get_note(note_name)
    if content:
        print("\n--- Note Content ---")
        print(content)
        print("--------------------")
    else:
        print("Note not found.")

def list_notes_ui(vault):
    """Handles the UI for listing notes."""
    show_hidden = questionary.confirm("Show hidden notes?", style=STYLE).ask()

    start_date_str = questionary.text("Filter by start date (YYYY-MM-DD, optional):", style=STYLE).ask()
    end_date_str = questionary.text("Filter by end date (YYYY-MM-DD, optional):", style=STYLE).ask()

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

def search_notes_ui(vault):
    """Handles the UI for searching notes."""
    query = questionary.text("Enter search query:", style=STYLE).ask()
    tag_filter = questionary.text("Filter by tag (optional):", style=STYLE).ask()

    results = vault.search_notes(query)

    if tag_filter:
        filtered_results = []
        for note_name in results:
            content = vault.get_note(note_name)
            if content and tag_filter in content:
                filtered_results.append(note_name)
        results = filtered_results

    if results:
        print("\n--- Search Results ---")
        for note in results:
            print(f"- {note}")
        print("--------------------")
    else:
        print("No results found.")

def purge_note_ui(vault, manager, password):
    """Handles the UI for purging a note."""
    note_name = questionary.text("Enter note name to purge:", style=STYLE).ask()
    confirm = questionary.confirm(f"Are you sure you want to permanently delete '{note_name}'?", style=STYLE).ask()
    if confirm:
        vault.purge_note(note_name)

        fake_log = questionary.confirm("Create a plausible fake deletion log?", style=STYLE).ask()
        if fake_log:
            log_name = f"log_{time.strftime('%Y-%m-%d_%H-%M-%S')}"
            log_content = f"Deleted shopping list on {time.strftime('%Y-%m-%d')}."
            vault.add_note(log_name, log_content)

        manager.save_vault(vault, password)
        print(f"Note '{note_name}' has been securely purged.")

def reflect_ui(vault, manager, password):
    """Handles the UI for the reflect command."""
    print("How did today feel?")
    q1 = questionary.text("", style=STYLE).ask()
    print("What drained you? What sparked you?")
    q2 = questionary.text("", style=STYLE).ask()
    print("What did you avoid saying?")
    q3 = questionary.text("", style=STYLE).ask()

    entry = f"How did today feel?\n{q1}\n\nWhat drained you? What sparked you?\n{q2}\n\nWhat did you avoid saying?\n{q3}"

    note_name = f"reflection_{time.strftime('%Y-%m-%d')}"
    vault.add_note(note_name, entry)
    manager.save_vault(vault, password)
    print("Your reflection has been saved securely. No one else sees this.")

def main_menu(vault, manager, password):
    """Shows the main menu after the vault is unlocked."""
    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=["Add/Update Note", "Read Note", "List Notes", "Search Notes", "Purge Note", "Reflect", "Exit"],
            style=STYLE
        ).ask()

        if choice == 'Add/Update Note':
            add_note_ui(vault, manager, password)
        elif choice == 'Read Note':
            read_note_ui(vault)
        elif choice == 'List Notes':
            list_notes_ui(vault)
        elif choice == 'Search Notes':
            search_notes_ui(vault)
        elif choice == 'Purge Note':
            purge_note_ui(vault, manager, password)
        elif choice == 'Reflect':
            reflect_ui(vault, manager, password)
        elif choice == 'Exit':
            break
        else:
            print("Invalid choice.")

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    command = questionary.select(
        "What would you like to do?",
        choices=["create-vault", "unlock-vault"],
        style=STYLE
    ).ask()

    if command == "create-vault":
        create_vault_ui()
    elif command == "unlock-vault":
        vault, manager, password = unlock_vault_ui()
        if vault:
            main_menu(vault, manager, password)

if __name__ == "__main__":
    main()
