# TinyGenKey

A *tiny*, *secure*, and *easy-to-use* key generator in Python.
Generate cryptographically strong keys for your needs.

---

## Features

- Cryptographically secure keys using `os.urandom`
- Customizable alphabet, length, prefix, and suffix
- Lightweight and dependency-free
- Type-hinted for modern Python

---

## Installation

```bash
pip install tinygenkey
```

---

## Usage

```py
import tinygenkey as tgk


# Generate a default 42-character key
key = tgk.gen_key()
print(key)

# Generate a key with a prefix and suffix
key2 = tgk.gen_key(key_prefix="user_", key_suffix="_end", length=16)
print(key2)

# Use a custom alphabet
custom_alphabet = list("ABC123")
key3 = tgk.gen_key(alphabet=custom_alphabet, length=8)
print(key3)
```
