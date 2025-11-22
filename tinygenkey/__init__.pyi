from typing import Any, Generator, List, Literal, TypedDict, Optional

# ---------------------------------------------------------
# Presets
# ---------------------------------------------------------

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

ALPHANUMERIC_LIST: list[str]
HEX_LIST: list[str]
BASE64_LIST: list[str]
SAFE_LIST: list[str]
LOWERCASE_LIST: list[str]
UPPERCASE_LIST: list[str]
NUMBERS_LIST: list[str]
PRINTABLE_LIST: list[str]

PRESETS: dict[str, list[str]]


# ---------------------------------------------------------
# Errors
# ---------------------------------------------------------

class NoneError(Exception): ...
class KeyPresetError(Exception): ...


# ---------------------------------------------------------
# Typed reports
# ---------------------------------------------------------

class KeyVerifyReport(TypedDict, total=False):
    valid: bool
    expected_charset: Optional[list[str]]
    length: int
    min_length: Optional[int]
    max_length: Optional[int]
    reasons: list[str]
    hints: list[str]
    key_number: str


# ---------------------------------------------------------
# Functions
# ---------------------------------------------------------

def secure_choice(seq: List[str]) -> str: ...

def gen_key(
    alphabet: list[str] = ...,
    length: int = ...,
    prefix: str = ...,
    suffix: str = ...,
) -> str: ...

def base_handle_verify(
    key: str,
    alphabet_or_preset: Optional[list[str] | KEYS_PRESETS] = ...,
    min_length: Optional[int] = ...,
    max_length: Optional[int] = ...,
    prefix: Optional[str] = ...,
    suffix: Optional[str] = ...,
) -> KeyVerifyReport: ...

def ext_verify_handle_list(
    keys: list[str],
    **kwargs: Any,
) -> Generator[KeyVerifyReport, None, None]: ...

def rand_key(
    key_prefix: str,
    list_of_chars: list[str] = ...,
    length_of_string: int = ...,
) -> Generator[str, None, None]: ...


# ---------------------------------------------------------
# Classes
# ---------------------------------------------------------

class BaseKey:
    @staticmethod
    def gen(
        length: int = ...,
        alphabet: Optional[list[str]] = ...,
        prefix: str = ...,
        suffix: str = ...,
        preset: KEYS_PRESETS = ...,
    ) -> str: ...

    def verify(self, value: str, **kwargs: Any) -> KeyVerifyReport: ...


class Key(BaseKey):
    value: str

    def __init__(self, value: str = ...) -> None: ...
    def verify(self, **kwargs: Any) -> KeyVerifyReport: ...
    def is_valid(self, **kwargs: Any) -> bool: ...

    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...


class Keys(BaseKey):
    values: list[str]

    def __init__(self, values: list[str]) -> None: ...

    @classmethod
    def create(cls, count: int = ..., **kwargs: Any) -> "Keys": ...
    def gen(self, count: int = ..., **kwargs: Any) -> list[str]: ...
    def verify(self, **kwargs: Any) -> list[KeyVerifyReport]: ...
    def is_valid(self, **kwargs: Any) -> list[bool]: ...

    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...


# ---------------------------------------------------------
# Package metadata
# ---------------------------------------------------------

__all__: list[str]
__version__: str
__author__: str
__license__: str
