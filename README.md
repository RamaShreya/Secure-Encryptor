# Secure Encryptor

**Designed by Shreya**

Secure Encryptor is a modern Python desktop application for protecting files with AES-256-GCM encryption. It provides a clean CustomTkinter interface for encrypting files, generating separate key files, decrypting `.enc` files, and reviewing local activity history.

This project is organized for GitHub portfolio use, resume project sections, and internship/project showcase submissions.

## Features

- AES-256-GCM authenticated file encryption.
- Separate `.key` file generation for every encrypted file.
- Secure decryption with matching key-file validation.
- SHA-256 integrity checking after decryption.
- Modern dark-mode GUI built with CustomTkinter.
- Optional drag-and-drop support through TkinterDnD2.
- SQLite activity history for encryption and decryption events.
- Safe output naming to avoid overwriting existing files.
- Runtime folders for encrypted files, decrypted files, keys, logs, database files, screenshots, and temporary files.

## Technologies Used

- Python 3
- CustomTkinter
- TkinterDnD2
- Cryptography
- SQLite
- Tkinter

## Installation

Follow these steps from a terminal in Visual Studio Code.

```powershell
git clone https://github.com/RamaShreya/Secure-Encryptor.git
cd Secure-Encryptor
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Beginner note: the virtual environment keeps this project's Python packages separate from the rest of your computer.

## Usage

Start the application:

```powershell
python app.py
```

Or run the Windows helper script:

```powershell
.\run.bat
```

Encrypt a file:

1. Open Secure Encryptor.
2. Go to **Encrypt File**.
3. Select one or more files.
4. Choose the encrypted output folder.
5. Choose where the `.key` file should be saved.
6. Click **Encrypt File**.

Decrypt a file:

1. Go to **Decrypt File**.
2. Select one or more `.enc` files.
3. Select the matching `.key` file.
4. Choose the decrypted output folder.
5. Click **Decrypt File**.

Important: keep `.key` files private and backed up. Without the matching key file, encrypted files cannot be recovered.

## Project Structure

```text
Secure-Encryptor/
|-- app.py
|-- main.py
|-- requirements.txt
|-- README.md
|-- LICENSE
|-- CONTRIBUTING.md
|-- CHANGELOG.md
|-- setup.bat
|-- run.bat
|-- assets/
|   |-- icons/
|   |-- images/
|   |-- themes/
|-- crypto/
|-- database/
|-- docs/
|-- gui/
|-- screenshots/
|-- encrypted_files/
|-- decrypted_files/
|-- keys/
|-- logs/
|-- temp/
```

Recommended organization:

- Keep encryption logic inside `crypto/`.
- Keep GUI screens and reusable UI components inside `gui/`.
- Keep database code inside `database/`.
- Keep screenshots for GitHub inside `screenshots/`.
- Keep generated encrypted files, decrypted files, key files, logs, database files, and temporary files out of Git.

## Screenshots

Add project screenshots here before publishing the repository:

```text
screenshots/
|-- dashboard.png
|-- encrypt-page.png
|-- decrypt-page.png
```

Example Markdown format:

```markdown
![Secure Encryptor Dashboard](screenshots/dashboard.png)
```

## Git And GitHub Setup

This project already has Git configured with:

```text
Remote: https://github.com/RamaShreya/Secure-Encryptor.git
Branch: main
```

Useful Git commands:

```powershell
# Initialize Git if the project is not already a repository
git init

# Check changed files
git status

# Add project files
git add .

# Create a commit
git commit -m "Prepare Secure Encryptor for GitHub"

# Connect to GitHub if the remote is not already set
git remote add origin https://github.com/RamaShreya/Secure-Encryptor.git

# Push to GitHub
git branch -M main
git push -u origin main
```

If `origin` already exists, update it with:

```powershell
git remote set-url origin https://github.com/RamaShreya/Secure-Encryptor.git
```

## Security Notes

- The app stores activity metadata, not raw AES keys, in the SQLite database.
- Key files are saved separately from encrypted files.
- Existing output files are not overwritten; Secure Encryptor creates unique file names.
- Runtime folders are ignored by Git except for `.gitkeep` placeholder files.

## Future Enhancements

- Add password-based key protection for `.key` files.
- Add folder encryption and batch folder restore.
- Add exportable encrypted activity reports.
- Add automatic screenshot assets for GitHub documentation.
- Add automated tests for encryption, decryption, and database behavior.
- Add packaged desktop builds using PyInstaller.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).

## Author

**Designed by Shreya**
