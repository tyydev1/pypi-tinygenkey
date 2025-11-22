"""
TinyGenKey - A small secure key generator and validator library.
"""

from .main import (
    # Core classes
    BaseKey,
    Key,
    Keys,

    # Generation helpers
    secure_choice,
    gen_key,

    # Verification API
    base_handle_verify,
    ext_verify_handle_list,

    # Presets and preset aliases
    PRESETS,
    KEYS_PRESETS,

    # Character sets
    ALPHANUMERIC_LIST,
    HEX_LIST,
    BASE64_LIST,
    SAFE_LIST,
    LOWERCASE_LIST,
    UPPERCASE_LIST,
    NUMBERS_LIST,
    PRINTABLE_LIST,

    # Errors
    NoneError,
    KeyPresetError,

    # Typed report
    KeyVerifyReport,
)

__all__ = [
    # Classes
    "BaseKey",
    "Key",
    "Keys",

    # Generation
    "secure_choice",
    "gen_key",

    # Verification
    "base_handle_verify",
    "ext_verify_handle_list",

    # Presets
    "PRESETS",
    "KEYS_PRESETS",

    # Charsets
    "ALPHANUMERIC_LIST",
    "HEX_LIST",
    "BASE64_LIST",
    "SAFE_LIST",
    "LOWERCASE_LIST",
    "UPPERCASE_LIST",
    "NUMBERS_LIST",
    "PRINTABLE_LIST",

    # Errors
    "NoneError",
    "KeyPresetError",

    # Report
    "KeyVerifyReport",
]

__version__ = "0.4.0-dev"
__author__ = "Razka Rizaldi"
__email__ = "razka.rizaldis@gmail.com"
__license__ = "MIT"

