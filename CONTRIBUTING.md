# Contributing to Secure Encryptor

Thank you for helping improve Secure Encryptor.

## Guidelines

- Keep encryption and decryption behavior backward compatible unless a version migration is documented.
- Do not commit generated files, logs, local databases, encrypted outputs, decrypted outputs, or key files.
- Run import checks before opening a pull request.
- Keep UI changes consistent with the dark cybersecurity theme.
- Add focused tests or manual verification notes for security-sensitive changes.

## Local Setup

```powershell
setup.bat
```

## Pull Request Checklist

- The app starts with `python app.py`.
- Encryption works for a sample file.
- Decryption works with the generated `.key` file.
- No sensitive files are included in Git.
- Documentation is updated when behavior changes.
