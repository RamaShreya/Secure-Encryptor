# Secure Encryptor Security Notes

Secure Encryptor uses AES-256-GCM with a unique random 256-bit key per encrypted file. The key is saved as a separate `.key` file and is never stored in the SQLite database.

## Key Handling

- Store `.key` files in a private location.
- Back up `.key` files separately from encrypted files.
- Do not upload key files to public repositories.

## Runtime Data

The following folders are ignored by Git because they may contain local or sensitive data:

- `keys/`
- `logs/`
- `database/`
- `encrypted_files/`
- `decrypted_files/`
- `temp/`
