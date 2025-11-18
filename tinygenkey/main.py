# tinygenkey/main.py

import os
import string
from typing import Any, Generator, List, Literal, TypedDict

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


class NoneError(Exception):
    """Call this if the error has something to do with None"""
    pass


class KeyVerifyReport(TypedDict, total=False):
    valid: bool
    expected_charset: list[str] | None
    length: int
    min_length: int | None
    max_length: int | None
    reasons: list[str]
    hints: list[str]
    key_number: str

class BaseKey:
    def gen(
        obj,
        length: int = 42,
        alphabet: list[str] | None = None,
        prefix: str = "",
        suffix: str = "",
        preset: KEYS_PRESETS = "alphanumeric",
    ) -> str:

        if preset not in PRESETS:
            raise ValueError(f"Invalid preset: {preset}")

        chars = alphabet if alphabet else PRESETS[preset]
        return prefix + "".join(secure_choice(chars) for _ in range(length)) + suffix

    def verify(obj, value: str, **kwargs) -> KeyVerifyReport:
        """Base single-value verification."""
        return base_handle_verify(value, **kwargs)

class Key(BaseKey):
    def __init__(obj, value: str):
        obj.value = value

    def verify(obj, **kwargs) -> KeyVerifyReport:
        return super(Key, obj).verify(obj.value, **kwargs)

    def is_valid(obj, **kwargs) -> bool:
        return obj.verify(**kwargs)["valid"]

    def __str__(obj):
        return obj.value

    def __repr__(obj):
        return f"Key({obj.value!r})"

class Keys(BaseKey):
    def __init__(obj, values: list[str]):
        obj.values = values

    @classmethod
    def create(cls, count: int = 1, **kwargs) -> "Keys":
        """Generate multiple keys and return a Keys object."""
        values = [super(Keys, cls).gen(**kwargs) for _ in range(count)]
        return cls(values)

    def gen(
        obj,
        count: int = 1,
        **kwargs
    ) -> list[str]:
        """Generate multiple keys using BaseKey.gen()."""
        return [super(Keys, obj).gen(**kwargs) for _ in range(count)]

    def verify(obj, **kwargs) -> list[KeyVerifyReport]:
        return [super(Keys, obj).verify(v, **kwargs) for v in obj.values]

    def is_valid(obj, **kwargs) -> list[bool]:
        return [r["valid"] for r in obj.verify(**kwargs)]

    def __str__(obj):
        return "\n".join(obj.values)

    def __repr__(obj):
        return f"Keys(values={obj.values!r})"


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


def secure_choice(seq: List[str]) -> str:
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
    return Key.gen(
        Key(),
        length=length,
        alphabet=alphabet,
        prefix=prefix,
        suffix=suffix,
        preset="alphanumeric",
    )


def base_handle_verify(
    key: str,
    alphabet: list[str] | KEYS_PRESETS | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
    prefix: str | None = None,
    suffix: str | None = None,
) -> dict[str, bool | list[str] | list[Any] | None | int]:
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
    if alphabet is None and not (prefix or suffix or min_length or max_length):
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


def ext_verify_handle_list(
    key: list[str],
    **kwargs,
) -> Generator[KeyVerifyReport, None, None]:
    for i, k in enumerate(key):
        res = base_handle_verify(k, **kwargs)
        res["key_number"] = f"{i + 1} out of {len(key)}"
        yield res


def test_gen() -> None:
    """Test generation of safe key"""
    key = gen_key(prefix="testKey__", suffix="__")
    print(key)


class UsingThis:
    def __init__(this) -> None:  # type: ignore
        this.name = "Jeff"
