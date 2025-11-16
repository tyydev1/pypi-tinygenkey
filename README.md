[![On PyPI](https://img.shields.io/pypi/v/tinygenkey.svg)](https://pypi.org/project/tinygenkey/)
![Downloads](https://pepy.tech/badge/tinygenkey)
![Total Downloads](https://pepy.tech/badge/tinygenkey/total)
![Python Version](https://img.shields.io/pypi/pyversions/tinygenkey.svg)
![License](https://img.shields.io/pypi/l/tinygenkey.svg)

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
key2 = tgk.gen_key(prefix="user_", suffix="_end", length=16)
print(key2)

# Use a custom alphabet
custom_alphabet = list("ABC123")
key3 = tgk.gen_key(alphabet=custom_alphabet, length=8)
print(key3)
```

---

## `keys_seq()`

This function returns a list of keys, determined with argument `count` and customized with `**kwargs`.

```py
api_key = tgk.keys_seq(5) # Generates 5 keys

new_tokens = tgk.keys_seq(5, prefix="new_", suffix=f"_{tgk.keys_gen(length=6)}", preset="hex")

# Align with keys_align()
print(tgk.keys_align(new_tokens))
```

## `keys_align()`

Separates a list of tokens with a passed separator argument (default is newline `\n`). Examples could be seen on `keys_seq()`

---

## Advanced Usage

### Recursive Key Generation

Create structured, hierarchical keys by cleanly nesting `keys_gen()` (or outdated `gen_key()`) calls:

```py
api_key = tgk.keys_gen(
    prefix=f"api_{tgk.gen_key(length=8)}_",
    length=32,
    suffix=f"_{tgk.gen_key(length=4)}"
)
# Result = api_<8 random chars>_<32 random>_<4 random>
# Organized and polished identifiers!
```

This composable design allows you to build complex key structures while maintaining cryptographic security at every level.

### Why This Is Better Than `secrets`

#### With Python's built-in `secrets` module:

```py
# pretend we imported secrets and have an alphanumeric
# list of characters

# awkward..
secrets_key = (
    f"api_"
    f"{''.join(secrets.choice(chars) for _ in range(8))}_"
    f"{''.join(secrets.choice(chars) for _ in range(32))}"
    f"_{''.join(secrets.choice(chars) for _ in range(8))}"
)
```

#### With `tinygenkey`

```py
import tinygenkey as tgk

# Much better
tgk_key = tgk.keys_gen(
    prefix=f"api_{tgk.gen_key(length=8)}_",
    length=32,
    suffix=f"_{tgk.gen_key(length=4)}"
)
```

Cleaner, more readable, easier to maintain.

---

## !!!! WARNING Syntax Migration !!!!

In version 0.2.0, the syntax for `gen_key()` will be replaced by a more powerful and consistent `keys_gen()`. You may still use `gen_key()` as usual, but it is **deprecated**.

On version stable 0.5.0, `gen_key()` will be deleted, but *optional deprecated-supported versions* will still be maintained as version `>0.5-dep` and is NOT preserved in minor updates.

By version 1.0.0, `gen_key()` **will be removed entirely** and deprecated-supported versions will stop being maintained.

### Save Your Program
If your program *cannot* be modified and is *very* important for others, you may ask for a **special version** that supports `gen_key()`.

---

## GitHub

This project is open-sourced at GitHub:
[tinygenkey on GitHub](https://github.com/tyydev1/pypi-tinygenkey)

You may further verify the security of the code yourself.

---

## License

This project is protected by the MIT License.
