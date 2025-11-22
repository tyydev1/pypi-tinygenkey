# tinygenkey/main.py

import os
import string
from typing import Any, Generator, List, Literal, TypedDict

# ---------------------------------------------------------
# Character presets
# ---------------------------------------------------------

ALPHANUMERIC_LIST = list(
    string.ascii_lowercase + string.ascii_uppercase + string.digits
)
HEX_LIST = list(string.digits + "abcdef")
BASE64_LIST = list(string.ascii_letters + string.digits + "+/")
SAFE_LIST = list(string.ascii_letters + string.digits + "-_")
LOWERCASE_LIST = list(string.ascii_lowercase)
UPPERCASE_LIST = list(string.ascii_uppercase)
NUMBERS_LIST = list(string.digits)
PRINTABLE_LIST = list(string.printable[:-5])  # remove whitespace

KEYS_PRESETS = Literal[
    "alphanumeric",
    "hex",
    "base64",
    "safe",
    "lowercase",
    "uppercase",
    "numbers",
    "printable",
]

PRESETS = {
    "alphanumeric": ALPHANUMERIC_LIST,
    "hex": HEX_LIST,
    "base64": BASE64_LIST,
    "safe": SAFE_LIST,
    "lowercase": LOWERCASE_LIST,
    "uppercase": UPPERCASE_LIST,
    "numbers": NUMBERS_LIST,
    "printable": PRINTABLE_LIST,
}


# ---------------------------------------------------------
# Custom errors
# ---------------------------------------------------------

class NoneError(Exception):
    """Call this if the error has something to do with None"""
    pass


class KeyPresetError(Exception):
    """Call this if the error has something to do with a preset"""
    pass


# ---------------------------------------------------------
# Verification Report
# ---------------------------------------------------------

class KeyVerifyReport(TypedDict, total=False):
    valid: bool
    expected_charset: list[str] | None
    length: int
    min_length: int | None
    max_length: int | None
    reasons: list[str]
    hints: list[str]
    key_number: str


# ---------------------------------------------------------
# Core random selection
# ---------------------------------------------------------

def secure_choice(seq: List[str]) -> str:
    """Returns a single cryptographically secure string element from seq."""
    n = len(seq)
    limit = 256 - (256 % n)

    while True:
        b = os.urandom(1)[0]
        if b < limit:
            return seq[b % n]


# ---------------------------------------------------------
# Main key generation / verification helpers
# ---------------------------------------------------------

def base_handle_verify(
    key: str,
    alphabet_or_preset: list[str] | KEYS_PRESETS | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
) -> KeyVerifyReport:

    # Extract core characters (removing affixes)
    if prefix and suffix:
        core_chars = key[len(prefix): -len(suffix)]
    elif prefix:
        core_chars = key[len(prefix):]
    elif suffix:
        core_chars = key[:-len(suffix)]
    else:
        core_chars = key

    allowed_chars: list[str] | None = None
    reasons: list[str] = []
    hints: list[str] = []
    valid = True
    length = len(core_chars)

    # Determine allowed characters
    if alphabet_or_preset is not None:
        if isinstance(alphabet_or_preset, list):
            allowed_chars = alphabet_or_preset
        elif isinstance(alphabet_or_preset, str) and alphabet_or_preset in PRESETS:
            allowed_chars = PRESETS[alphabet_or_preset]
        else:
            raise ValueError(f"Invalid preset or alphabet: {alphabet_or_preset}")

        # Identify invalid chars
        invalid_chars = set(core_chars) - set(allowed_chars)
        if invalid_chars:
            valid = False
            reasons.append("Invalid characters: " + ", ".join(sorted(invalid_chars)))
            if "_" in invalid_chars:
                hints.append(
                    "Found '_' among invalid characters. Did you intend it as a prefix/suffix separator?"
                )
    else:
        invalid_chars = []

    # Length checks
    failed_length = None
    if min_length is not None and length < min_length:
        valid = False
        failed_length = "min"
        reasons.append(f"Too small (length of key): {length}")
    elif max_length is not None and length > max_length:
        valid = False
        failed_length = "max"
        reasons.append(f"Too large (length of key): {length}")

    if failed_length == "min" and min_length is not None and len(key) > min_length:
        hints.append("'min_length' failure: did you mean to include affixes in the check?")
    if failed_length == "max" and max_length is not None and len(key) < max_length:
        hints.append("'max_length' failure: did you mean to include affixes in the check?")

    # Prefix/suffix validation
    if prefix and not key.startswith(prefix):
        valid = False
        reasons.append(f"Invalid prefix: expected '{prefix}', found '{key[:len(prefix)]}'")

    if suffix and not key.endswith(suffix):
        valid = False
        reasons.append(f"Invalid suffix: expected '{suffix}', found '{key[-len(suffix):]}'")

    # Hints for no alphabet provided
    if alphabet_or_preset is None and not any([prefix, suffix, min_length, max_length]):
        hints.append(
            "No 'alphabet' or preset was provided. All characters are considered valid. "
            "Did you mean to provide an empty list instead?"
        )

    if valid:
        reasons.append("No errors.")

    return KeyVerifyReport(
        valid=valid,
        expected_charset=allowed_chars,
        length=length,
        min_length=min_length,
        max_length=max_length,
        reasons=reasons,
        hints=hints,
    )


def ext_verify_handle_list(
    keys: list[str],
    **kwargs,
) -> Generator[KeyVerifyReport, None, None]:
    """Verify a list of keys, yielding numbered reports."""
    for i, k in enumerate(keys):
        report = base_handle_verify(k, **kwargs)
        report["key_number"] = f"{i + 1} out of {len(keys)}"
        yield report


# ---------------------------------------------------------
# BaseKey class and derived Key / Keys classes
# ---------------------------------------------------------

class BaseKey:
    """
    Base class shared by key generators.
    gen() is static because it does not need a self-reference.
    """

    @staticmethod
    def gen(
        length: int = 42,
        alphabet: list[str] | None = None,
        prefix: str = "",
        suffix: str = "",
        preset: KEYS_PRESETS = "alphanumeric",
    ) -> str:

        if preset not in PRESETS:
            raise KeyPresetError(f"Invalid preset: {preset}")

        chars = alphabet if alphabet else PRESETS[preset]
        return prefix + "".join(secure_choice(chars) for _ in range(length)) + suffix

    def verify(self, value: str, **kwargs) -> KeyVerifyReport:
        """Base single-value verification."""
        return base_handle_verify(value, **kwargs)


class Key(BaseKey):
    def __init__(self, value: str = ""):
        self.value = value

    def verify(self, **kwargs) -> KeyVerifyReport:
        if self.value is None:
            raise NoneError("No key to verify. Set .value or pass it to constructor.")
        report = super().verify(self.value, **kwargs)
        report["key_number"] = "1 of 1"
        return report

    def is_valid(self, **kwargs) -> bool:
        return self.verify(**kwargs)["valid"]

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"Key({self.value!r})"


class Keys(BaseKey):
    def __init__(self, values: list[str]):
        self.values = values

    @classmethod
    def create(cls, count: int = 1, **kwargs) -> "Keys":
        values = [BaseKey.gen(**kwargs) for _ in range(count)]
        return cls(values)

    def gen(self, count: int = 1, **kwargs) -> list[str]:
        return [BaseKey.gen(**kwargs) for _ in range(count)]

    def verify(self, **kwargs) -> list[KeyVerifyReport]:
        return list(ext_verify_handle_list(self.values, **kwargs))

    def is_valid(self, **kwargs) -> list[bool]:
        return [r["valid"] for r in self.verify(**kwargs)]

    def __str__(self):
        return "\n".join(self.values)

    def __repr__(self):
        return f"Keys(values={self.values!r})"


# ---------------------------------------------------------
# Legacy and utility methods
# ---------------------------------------------------------

def rand_key(
    key_prefix: str,
    list_of_chars: list[str] = ALPHANUMERIC_LIST,
    length_of_string: int = 42,
) -> Generator[str, None, None]:
    """Insecure random generator using randint. Generates characters one-by-one."""
    yield key_prefix
    from random import randint
    for _ in range(length_of_string):
        yield list_of_chars[randint(0, len(list_of_chars) - 1)]


def gen_key(
    alphabet: list[str] = ALPHANUMERIC_LIST,
    length: int = 42,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Deprecated: use BaseKey.gen() instead."""
    return BaseKey.gen(
        length=length,
        alphabet=alphabet,
        prefix=prefix,
        suffix=suffix,
        preset="alphanumeric",
    )


# ---------------------------------------------------------
# Simple REPL interface
# ---------------------------------------------------------

def test_gen() -> None:
    key = gen_key(prefix="testKey__", suffix="__")
    print(key)


def repl() -> None:
    import readline
    print("Welcome to TinyGenKey!")
    print("This is the interactive REPL tool. tinygenkey-cli v0.1.0\n")
    print("Input 'generate' to generate a key, and 'verify' to verify.\n")

    while True:
        try:
            usercmd = input(">>> ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting REPL.")
            break

        if usercmd in ("exit", "quit"):
            print("Goodbye!")
            break

        elif usercmd == "help":
            print("""
Available commands:
    generate    Generate a new key with custom parameters
    verify      Verify an existing key against rules
    quick       Generate with defaults (quick mode)
    presets     List available presets
    exit/quit   Exit the REPL
""")

        elif usercmd == "generate":
            preset = input("Enter a preset: ")
            length = input("Enter the length: ")
            prefix = input("Enter a prefix (if any): ")
            suffix = input("Enter a suffix (if any): ")

            try:
                length = int(length)
                custkey = BaseKey.gen(length=length, preset=preset, prefix=prefix, suffix=suffix)
                print(f"\nHere's your password: {custkey}\n")
            except (KeyPresetError, ValueError) as e:
                print(f"Error: {e}")

        elif usercmd == "verify":
            import pprint
            key_to_verify = input("Enter key to verify: ")
            preset = input("Enter a preset or leave blank: ")
            min_length = input("Enter a minimum length (if any): ")
            max_length = input("Enter a maximum length (if any): ")
            prefix = input("Enter a prefix (if any): ")
            suffix = input("Enter a suffix (if any): ")

            preset_val = preset if preset else None

            try:
                min_length = int(min_length) if min_length else None
                max_length = int(max_length) if max_length else None

                report = base_handle_verify(
                    key_to_verify,
                    alphabet_or_preset=preset_val,
                    min_length=min_length,
                    max_length=max_length,
                    prefix=prefix or None,
                    suffix=suffix or None,
                )
                pprint.pprint(report)
                print()

            except (ValueError, KeyPresetError) as e:
                print(f"Error: {e}")
                continue

        elif usercmd == "quick":
            print(f"Here's your quick key: {BaseKey.gen()}\n")

        elif usercmd == "presets":
            print("Available presets:")
            for name in PRESETS:
                print(f" - {name}")
            print()

        else:
            print(f"Unknown command: {usercmd}")


if __name__ == "__main__":
    repl()
