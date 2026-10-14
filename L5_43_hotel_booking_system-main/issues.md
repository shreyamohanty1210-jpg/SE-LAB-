# Static Code Analysis — Issues Found

| Issue | Type | Line(s) | Description | Fix Approach |
|---|---|---:|---|---|
| Unsafe `eval()` | Security — Medium | 42 | Evaluating input as Python code can allow unintended code execution. | Replace with a safe alternative. |
| Weak MD5 hash | Security — High | 47 | MD5 is unsuitable for security-sensitive hashing. | Use a suitable secure hashing method. |
| Shell command execution | Security — High | 58 | `os.system()` may expose the program to command injection. | Replace with a safer Python operation. |
| Hardcoded token | Security — Low | 62 | A secret token is stored in source code. | Read it from an environment variable. |
| Broad exception handling | Code quality | 26 | A `try/except/pass` block may silently hide errors. | Handle expected exceptions explicitly. |
| Unused import | Style | 6 | The `math` module is imported but unused. | Remove the import. |
| Unused variables | Style | 31, 41 | Variables are assigned but never used. | Remove or use them appropriately. |
| Missing final newline | Style | 73 | The source file lacks a final newline. | Add a final newline. |
