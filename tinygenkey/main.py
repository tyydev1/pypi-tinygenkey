# tinygenkey/main.py

import os
import string
from typing import Generator, List

CHARS_LIST = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)


def rand_key(
    key_prefix: str, list_of_chars: list[str] = CHARS_LIST, length_of_string: int = 42
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
    length: int = 42,
    prefix: str = "",
    alphabet: list[str] = CHARS_LIST,
    suffix: str = "",
) -> str:
    """Generates a secure key with optional prefix and suffix."""
    return prefix + "".join(crypt(alphabet) for _ in range(length)) + suffix


def test_gen() -> None:
    """Test generation of safe key"""
    key = gen_key("testKey__", key_suffix="__")
    print(key)
