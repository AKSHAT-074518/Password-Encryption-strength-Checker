import re
from cryptography.fernet import Fernet
from datetime import datetime
from fpdf import FPDF
from colorama import Fore, Style, init
import csv
import sys
import os

init(autoreset=True)

# Generate encryption key
key = Fernet.generate_key()
cipher = Fernet(key)

# Platform check
WINDOWS = os.name == 'nt'

# Password input function with * masking (Windows only)
def masked_password(prompt="Enter your password: "):
    if WINDOWS:
        import msvcrt
        print(Fore.LIGHTBLUE_EX + prompt, end='', flush=True)
        password = ''
        while True:
            ch = msvcrt.getch()
            if ch in {b'\r', b'\n'}:
                print()
                break
            elif ch == b'\x08':  # Backspace
                if len(password) > 0:
                    password = password[:-1]
                    print('\b \b', end='', flush=True)
            elif ch in {b'\x03', b'\x1a'}:  # Ctrl+C or Ctrl+Z
                raise KeyboardInterrupt
            else:
                try:
                    ch_decoded = ch.decode()
                    password += ch_decoded
                    print('*', end='', flush=True)
                except:
                    pass
        return password
    else:
        import getpass
        return getpass.getpass(Fore.LIGHTBLUE_EX + prompt)

# Check password strength
def check_password_strength(password):
    strength = "Weak"
    if len(password) >= 8:
        if (re.search(r"[A-Z]", password) and
            re.search(r"[a-z]", password) and
            re.search(r"\d", password) and
            re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
            strength = "Strong"
        elif ((re.search(r"[A-Z]", password) or re.search(r"[a-z]", password)) and
              re.search(r"\d", password)):
            strength = "Medium"
    return strength

# Encrypt password
def encrypt_password(password):
    encrypted = cipher.encrypt(password.encode())
    return encrypted.decode()

# Save to PDF (with unique name)
def save_to_pdf(username, password, strength, encrypted_password):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"password_report_{timestamp}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Password Check Report", ln=True, align='C')
    pdf.ln(8)

    pdf.set_font("Arial", '', 12)

    col1_width = 45
    col2_width = 140
    row_height = 10

    data = [
        ("Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("User Name", username),
        ("Password", "*" * len(password)),
        ("Strength", strength),
        ("Encrypted", encrypted_password)
    ]

    for label, value in data:
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(col1_width, row_height, label, border=1)
        pdf.set_font("Arial", '', 12)

        if label == "Encrypted" and len(value) > 80:
            pdf.multi_cell(col2_width, row_height, value, border=1)
        else:
            pdf.cell(col2_width, row_height, value, border=1, ln=True)

    pdf.output(filename)
    print(Fore.GREEN + f"\n[✔] Report saved as '{filename}' successfully!")

# Save to CSV with original password
def save_to_csv(username, password, strength, encrypted_password):
    file_exists = os.path.exists("password_data.csv")
    with open("password_data.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Name", "Password", "Strength", "Encrypted", "Time", "Original Password"])
        writer.writerow([username, "*" * len(password), strength, encrypted_password,
                         datetime.now().strftime("%Y-%m-%d %H:%M:%S"), password])
    print(Fore.GREEN + "[✔] Data also saved to 'password_data.csv'!")

# Main logic
try:
    print(Fore.CYAN + Style.BRIGHT + "\n🔐 Password Encryption & Strength Checker\n" + "-"*40)

    username = input(Fore.LIGHTBLUE_EX + "Enter your name: ")
    password = masked_password("Enter your password (will be hidden with *): ")

    show = input(Fore.LIGHTMAGENTA_EX + "Do you want to show your password? (yes/no): ").strip().lower()
    if show == "yes":
        print(Fore.YELLOW + f"\nHi {username}, your password is: {password}")

    strength = check_password_strength(password)

    if strength == "Strong":
        print(Fore.GREEN + f"\nPassword Strength: {strength}")
    elif strength == "Medium":
        print(Fore.YELLOW + f"\nPassword Strength: {strength}")
    else:
        print(Fore.RED + f"\nPassword Strength: {strength}")

    save = input(Fore.LIGHTMAGENTA_EX + "\nDo you want to save the result in PDF and CSV? (yes/no): ").strip().lower()
    if save == "yes":
        encrypted = encrypt_password(password)
        save_to_pdf(username, password, strength, encrypted)
        save_to_csv(username, password, strength, encrypted)
    else:
        print(Fore.RED + "\n[✘] Data not saved.")

except KeyboardInterrupt:
    print(Fore.RED + "\n\n[!] Process interrupted by user.")
except Exception as e:
    print(Fore.RED + f"\n[!] Error occurred: {str(e)}")
