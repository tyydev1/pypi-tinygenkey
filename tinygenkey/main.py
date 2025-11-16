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
):
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


def test_gen() -> None:
    """Test generation of safe key"""
    key = gen_key(prefix="testKey__", suffix="__")
    print(key)
