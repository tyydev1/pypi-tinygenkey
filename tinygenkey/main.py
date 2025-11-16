# tinygenkey/main.py

import os
import string
from typing import Generator, List, Literal

ALPHANUMERIC_LIST = list(
    string.ascii_lowercase + string.ascii_uppercase + string.digits
)
HEX_LIST = list(string.digits + "abcdef")
BASE64_LIST = list(string.ascii_letters + string.digits + "+/")
SAFE_LIST = list(string.ascii_letters + string.digits + "-_")
LOWERCASE_LIST = list(string.ascii_lowercase)
UPPERCASE_LIST = list(string.ascii_uppercase)
NUMBERS_LIST = list(string.digits)
PRINTABLE_LIST = list(string.printable[:-5])  # To remove whitespace characters

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


def rand_key(
    key_prefix: str,
    list_of_chars: list[str] = ALPHANUMERIC_LIST,
    length_of_string: int = 42,
) -> Generator[str, None, None]:
    """Insecure random generator using randint."""
    yield key_prefix
    for _ in range(length_of_string):
        from random import randint

        random_index = randint(0, len(list_of_chars) - 1)
        yield list_of_chars[random_index]


def crypt(seq: List[str]) -> str:
    """Returns a single cryptographically secure string element from seq."""
    n = len(seq)
    limit = 256 - (256 % n)

    while True:
        b = os.urandom(1)[0]
        if b < limit:
            return seq[b % n]


def gen_key(
    alphabet: list[str] = ALPHANUMERIC_LIST,
    length: int = 42,
    prefix: str = "",
    suffix: str = "",
) -> str:
    """Generates a secure key with optional prefix and suffix.

    .. deprecated:: 0.2.0
        Use :func:`keys_gen` instead.
    """
    return keys_gen(
        length=length,
        alphabet=alphabet,
        prefix=prefix,
        suffix=suffix,
        preset="alphanumeric",
    )


def keys_gen(
    length: int = 42,
    alphabet: list[str] | None = None,
    prefix: str = "",
    suffix: str = "",
    preset: KEYS_PRESETS = "alphanumeric",
) -> str:
    """Generates a secure key with added arguments.

    Added args:
        preset: Alphabet preset to use
        alphabet: Overrides preset
    """

    if preset not in PRESETS:
        raise ValueError(f"Invalid preset: {preset}")

    chars = alphabet if alphabet else PRESETS[preset]
    return prefix + "".join(crypt(chars) for _ in range(length)) + suffix


def keys_seq(
    count: int,
    **kwargs,
) -> list[str]:
    """Generates a 'count' amount of keys"""
    return [keys_gen(**kwargs) for _ in range(count)]


def keys_align(keys: list[str], sep: str = "\n") -> str:
    """Align a list of keys into an organized string"""
    return sep.join(keys)


def keys_verify(
    key: str,
    alphabet: list[str] | KEYS_PRESETS | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
) -> dict:
    """Checks if a key is valid based on passed parameters."""

    core_chars = key
    if prefix and suffix:
        core_chars = key[len(prefix) : -len(suffix)]
    elif prefix:
        core_chars = key[len(prefix) :]
    elif suffix:
        core_chars = key[: -len(suffix)]

    allowed_chars = []
    is_valid = True
    invalid_chars = []
    length = len(core_chars)
    reasons = []

    if alphabet is not None:
        if isinstance(alphabet, list):
            allowed_chars = alphabet
        elif isinstance(alphabet, str) and alphabet in PRESETS:
            allowed_chars = PRESETS[alphabet]
        else:
            raise ValueError(f"Invalid preset: {alphabet}")

    if alphabet is not None:
        invalid_chars = set(core_chars) - set(allowed_chars)
        if invalid_chars:
            is_valid = False
            invalid_chars = list(invalid_chars)
            reasons.append(f"Invalid characters: {', '.join(invalid_chars)}")
    else:
        invalid_chars = []

    failed_length = ""
    if min_length and (length < min_length):
        is_valid = False
        reasons.append(f"Too small (length of key): {length}")
        failed_length = "min"
    elif max_length and (length > max_length):
        is_valid = False
        reasons.append(f"Too large (length of key): {length}")
        failed_length = "max"

    if prefix and (not key.startswith(prefix)):
        is_valid = False
        reasons.append(
            f"Invalid prefix: expected '{prefix}', found '{key[: len(prefix)]}'"
        )
    if suffix and (not key.endswith(suffix)):
        is_valid = False
        reasons.append(
            f"Invalid suffix: expected '{suffix}', found '{key[-len(suffix) :]}'"
        )

    hints = []
    if "_" in invalid_chars:
        hints.append(
            "Found '_' in the core char. Did you mean it as an affix separator?"
        )
    if failed_length == "min" and (min_length and len(key) > min_length):
        hints.append(
            "'min' length failure. Did you consider min_length to include affix?"
        )
    if failed_length == "max" and (max_length and len(key) < max_length):
        hints.append(
            "'max' length failure. Did you consider max_length to include affix?"
        )
    if alphabet is None and not (prefix or suffix or min_length or max_length)
        hints.append(
            "No arguments passed to alphabet will result to no invalid characters. Did you mean to put an empty list?"
        )

    if is_valid:
        reasons.append("No errors.")

    report = {
        "valid": is_valid,
        "expected_charset": allowed_chars if alphabet else None,
        "length": length,
        "min_length": min_length,
        "max_length": max_length,
        "reasons": reasons,
        "hints": hints,
    }
    return report


def test_gen() -> None:
    """Test generation of safe key"""
    key = gen_key(prefix="testKey__", suffix="__")
    print(key)
