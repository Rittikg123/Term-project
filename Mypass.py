import re
import random
import string
import time
import threading
import pyperclip


# Singleton Pattern
class SessionManagement:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionManagement, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.current_user = None
        self.last_time = time.time()  # Initializing last activity time

    def login(self, user):
        self.current_user = user
        self.last_time = time.time()  # Updating activity time
        print(f"User {user} logged in.")

    def logout(self):
        print(f"User {self.current_user} logged out.")
        self.current_user = None

    def update_activity(self):
        self.last_time = time.time()  # Update activity time during the time action is performed


# Observer Pattern for letting the user know about weak password
class Observable:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notifying_observers(self, message):
        for observer in self.observers:
            observer.update(message)


class Observer:
    def update(self, message):
        pass


class EmailNotifier(Observer):
    def update(self, message):
        print(f"Email Notification: {message}")


# Mediator Pattern 
class Mediator:
    def __init__(self):
        self.components = {}

    def register(self, name, component):
        self.components[name] = component

    def notify(self, sender, event):
        if event == "login":
            print(f"{sender} logged in.")
        elif event == "logout":
            print(f"{sender} logged out.")


# Builder Pattern 
class PasswordBuilder:
    def __init__(self):
        self._length = 12 
        self.include_uppercase = True
        self.include_number = True
        self.include_characters = True

    def length(self, length):
        self._length = length
        return self

    def include_uppercases(self, include):
        self.include_uppercase = include
        return self

    def include_number(self, include):
        self.include_number = include
        return self

    def include_characters(self, include):
        self.include_characters = include
        return self

    def build(self):
        characters = string.ascii_lowercase
        if self.include_uppercase:
            characters += string.ascii_uppercase
        if self.include_number:
            characters += string.digits
        if self.include_characters:
            characters += string.punctuation
        return ''.join(random.choice(characters) for _ in range(self._length))


# Proxy Pattern for Masking/Unmasking
class MaskingOrUnmasking:
    def __init__(self, data):
        self.data = data
        self.is_masked = True

    def get_data(self):
        if self.is_masked:
            return {k: ("****" if k != "type" else v) for k, v in self.data.items()}
        return self.data

    def mask(self):
        self.is_masked = not self.is_masked


# Chain of Responsibility Pattern for Password Recovery
class Handler:
    def __init__(self, next_handler=None):
        self.next_handler = next_handler

    def handle_request(self, request):
        if self.next_handler:
            return self.next_handler.handle_request(request)
        return False


class SecurityQuestionHandler(Handler):
    def __init__(self, question, expected_answer, next_handler=None):
        super().__init__(next_handler)
        self.question = question
        self.expected_answer = expected_answer

    def handle_request(self, request):
        print(f"Security Check: {self.question}")
        answer = input("Your Answer: ").strip()
        if answer == self.expected_answer:
            if self.next_handler:
                return self.next_handler.handle_request(request)
            return True
        print("Incorrect answer.")
        return False


class PasswordRecovery:
    def __init__(self, security_questions):
        self.chain = None
        for question, answer in reversed(security_questions):
            self.chain = SecurityQuestionHandler(question, answer, self.chain)

    def recover_password(self):
        if self.chain.handle_request(None):
            print("You may now reset your master password.")
        else:
            print("Failed security checks.")


# Main Application Class
class MyPass(Observable):
    def __init__(self):
        super().__init__()
        self.session = SessionManagement()
        self.vault = []
        self.auto_lock_time = 300  # Auto-lock after 5 minutes
        self.clipboard_clear_time = 60  # Clear clipboard after 60 seconds
        threading.Thread(target=self.auto_lock, daemon=True).start()

    def auto_lock(self):
        """Automatically locks the vault after inactivity."""
        while self.running:  # Check if the thread should keep running
            if self.session.current_user and time.time() - self.session.last_activity_time > self.auto_lock_time:
                self.session.logout()
                print("\nVault auto-locked due to inactivity.")
            time.sleep(1)

    def is_weak_password(self, password):
        """Checks if the password is weak."""
        if len(password) < 8:
            return True
        if not any(char.isdigit() for char in password):
            return True
        if not any(char.isupper() for char in password):
            return True
        if not any(char.islower() for char in password):
            return True
        if not any(char in string.punctuation for char in password):
            return True
        return False

    def register_account(self):
        email = input("Enter your email: ").strip()
        if not self.is_valid_email(email):
            print("Invalid email format.")
            return

        while True:
            password = input("Enter your master password: ").strip()
            if self.is_weak_password(password):
                print(
                    "Warning: Your password is weak"
                )
                suggest = input("Would you want a strong password? (yes/no): ").strip().lower()
                if suggest == "yes":
                    password_builder = PasswordBuilder()
                    suggested_password = password_builder.length(16).build()
                    print(f"Suggested Strong Password: {suggested_password}")
                    use_suggestion = input("Do you want to use this password? (yes/no): ").strip().lower()
                    if use_suggestion == "yes":
                        password = suggested_password
                        break
                    else:
                        print("Please enter a password again.")
                else:
                    choice = input("Do you want to use this password? (yes/no): ").strip().lower()
                    if choice == "yes":
                        break
            else:
                print("Your password is good")
                break

        security_questions = []
        for i in range(3):
            question = input(f"Enter Security Question {i + 1}: ").strip()
            answer = input("Answer: ").strip()
            security_questions.append((question, answer))

        # Store the user details
        self.session.login(email)
        print("Account registered successfully!")

    def add_vault_item(self, item_type, data):
        
        self.session.update_activity()
        proxy = MaskingOrUnmasking(data)
        self.vault.append(proxy)
        print(f"{item_type} added to the vault.")

    def view_vault(self):
        self.session.update_activity()
        print("\nVault Items:")
        for idx, proxy in enumerate(self.vault):
            print(f"{idx}: {proxy.get_data()}")

    def unmask_item(self, index):
        self.session.update_activity()
        if 0 <= index < len(self.vault):
            proxy = self.vault[index]
            proxy.mask()
            print(f"Item {index} unmasked: {proxy.get_data()}")
        else:
            print("Invalid index.")

    def delete_vault_item(self, index):
        """Deletes an item from the vault."""
        if not self.session.current_user:
            print("You must be registered and logged in to delete items.")
            return

        if 0 <= index < len(self.vault):
            deleted_item = self.vault.pop(index)  # Retrieve the deleted item
            print(f"Item of type '{deleted_item.data.get('type', 'Unknown')}' deleted successfully.")
        else:
            print("Invalid index.")

    def copy_to_clipboard(self, index, field):
        self.session.update_activity()
        if 0 <= index < len(self.vault):
            proxy = self.vault[index]
            data = proxy.get_data()
            if field in data:
                pyperclip.copy(data[field])
                print(f"{field.capitalize()} copied to clipboard.")
                threading.Timer(self.clipboard_clear_time, self.clear_clipboard).start()
            else:
                print(f"Field '{field}' not found.")
        else:
            print("Invalid index.")

    def clear_clipboard(self):
        pyperclip.copy("")
        print("Clipboard cleared.")

    def auto_lock(self):
        while True:
            if self.session.current_user and time.time() - self.session.last_time > self.auto_lock_time:
                self.session.logout()
                print("\nVault auto-locked due to inactivity.")
            time.sleep(1)

    def is_valid_email(self, email):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(email_regex, email) is not None


if __name__ == "__main__":
    mypass = MyPass()

    while True:
        print("\n 1. Register 2. Add 3. View Vault 4. Unmask 5. Copy 6. Delete 7. Exit")
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            mypass.register_account()
        elif choice == "2":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            item_type = input("Enter item type: ").strip()
            data = {}
            while True:
                key = input("Enter field name (or 'finish' to finish): ").strip()
                if key.lower() == "finish":
                    break
                value = input(f"Enter value for {key}: ").strip()
                data[key] = value
            mypass.add_vault_item(item_type, data)
        elif choice == "3":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            mypass.view_vault()
        elif choice == "4":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            index = input("Enter the index of the item to unmask: ").strip()
            if index.isdigit():
                mypass.unmask_item(int(index))
            else:
                print("Invalid input. Please enter a valid index.")
        elif choice == "5":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            index = input("Enter the index of the item: ").strip()
            field = input("Enter the field to copy: ").strip()
            if index.isdigit():
                mypass.copy_to_clipboard(int(index), field)
            else:
                print("Invalid input. Please enter a valid index.")
        elif choice == "6":
            if not mypass.session.current_user:
                print("You must be registered and logged in to use this feature.")
                continue
            index = input("Enter the index of the item to delete: ").strip()
            if index.isdigit():
                mypass.delete_vault_item(int(index))
            else:
                print("Invalid input. Please enter a valid index.")
        elif choice == "7":
            print("Exiting")
            mypass.running = False  # Stops the auto-lock thread
            break
        else:
            print("Invalid choice.")
