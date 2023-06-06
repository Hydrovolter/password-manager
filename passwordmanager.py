import getpass
import os
from cryptography.fernet import Fernet
import json


class PasswordManager:
    def __init__(self):
        self.users_folder = "users"
        self.key_file = "key.key"
        self.users_file = "users.json"
        self.current_user = None
        self.current_data_folder = None
        self.current_data_file = None
        self.key = None

    def run(self):
        self.create_folders()
        while True:
            self.display_menu()
            choice = input("Enter your choice: ")

            if choice == "1":
                self.login()
            elif choice == "2":
                self.sign_up()
            elif choice == "3":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please try again.")

    def display_menu(self):
        print("\n=== Password Manager Login Menu ===")
        print("1. Login")
        print("2. Sign Up")
        print("3. Quit")

    def create_folders(self):
        if not os.path.exists(self.users_folder):
            os.makedirs(self.users_folder)

    def login(self):
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")
        users = self.load_users()

        if username not in users or users[username] != password:
            print("No username/password match.")
            return

        self.current_user = username
        self.current_data_folder = os.path.join(self.users_folder, self.current_user)
        self.current_data_file = os.path.join(self.current_data_folder, f"{self.current_user}_passwords.db")
        self.load_key()

        print(f"Logged in as {self.current_user}.\n")
        self.password_manager_menu()

    def sign_up(self):
        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")
        users = self.load_users()

        if username in users:
            print("Username already exists.")
            return

        users[username] = password
        self.save_users(users)

        self.current_user = username
        self.current_data_folder = os.path.join(self.users_folder, self.current_user)
        self.current_data_file = os.path.join(self.current_data_folder, f"{self.current_user}_passwords.db")
        self.load_key()

        print(f"Account created. Logged in as {self.current_user}.\n")
        self.password_manager_menu()

    def password_manager_menu(self):
        while True:
            self.display_password_manager_menu()
            choice = input("Enter your choice: ")

            if choice == "1":
                self.view_passwords()
            elif choice == "2":
                self.add_password()
            elif choice == "3":
                self.remove_password()
            elif choice == "4":
                print("Logging out...\n")
                self.current_user = None
                self.current_data_folder = None
                self.current_data_file = None
                break
            else:
                print("Invalid choice. Please try again.")

    def display_password_manager_menu(self):
        print("\n=== Password Manager User Menu ===")
        print("1. View Passwords")
        print("2. Add Password")
        print("3. Remove Password")
        print("4. Logout")

    def load_key(self):
        key_file = os.path.join(self.current_data_folder, self.key_file)
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            if not os.path.exists(self.current_data_folder):
                os.makedirs(self.current_data_folder)
            with open(key_file, "wb") as f:
                f.write(self.key)


    def encrypt_password(self, password):
        cipher_suite = Fernet(self.key)
        cipher_text = cipher_suite.encrypt(password.encode())
        return cipher_text.decode()

    def decrypt_password(self, cipher_text):
        cipher_suite = Fernet(self.key)
        plain_text = cipher_suite.decrypt(cipher_text.encode())
        return plain_text.decode()

    def load_passwords(self):
        if not os.path.exists(self.current_data_file):
            return {}

        with open(self.current_data_file, "r") as f:
            encrypted_data = f.read()

        if encrypted_data:
            decrypted_data = self.decrypt_password(encrypted_data)
            return json.loads(decrypted_data)

        return {}

    def save_passwords(self, passwords):
        encrypted_data = self.encrypt_password(json.dumps(passwords))
        with open(self.current_data_file, "w") as f:
            f.write(encrypted_data)

    def view_passwords(self):
        passwords = self.load_passwords()
        if not passwords:
            print("No data found.")
            return

        print("\n=== Passwords ===")
        for website, password in passwords.items():
            decrypted_password = self.decrypt_password(password)
            print(f"Website: {website}, Password: {decrypted_password}")

    def add_password(self):
        website = input("Enter website name: ")
        password = getpass.getpass("Enter password: ")
        passwords = self.load_passwords()
        encrypted_password = self.encrypt_password(password)
        passwords[website] = encrypted_password
        self.save_passwords(passwords)
        print("Password added successfully.")

    def remove_password(self):
        website = input("Enter website name to remove password: ")
        passwords = self.load_passwords()
        if website in passwords:
            del passwords[website]
            self.save_passwords(passwords)
            print("Password removed successfully.")
        else:
            print("No matching website found.")

    def load_users(self):
        if not os.path.exists(self.users_file):
            return {}

        with open(self.users_file, "r") as f:
            users_data = f.read()

        if users_data:
            return json.loads(users_data)

        return {}

    def save_users(self, users):
        with open(self.users_file, "w") as f:
            f.write(json.dumps(users))


if __name__ == "__main__":
    manager = PasswordManager()
    manager.run()


# Made by Hydrovolter