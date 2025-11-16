"""
Comprehensive test suite for keys_verify() validation function.

This test suite validates:
- Valid keys with various alphabets and presets
- Invalid character detection
- Length validation (min_length, max_length, both)
- Prefix validation (valid and invalid)
- Suffix validation (valid and invalid)
- Combined prefix + suffix scenarios
- Edge cases (empty strings, None alphabet, special characters)
- Error handling and reason reporting
"""

import pytest
import string
from tinygenkey.main import (
    keys_verify,
    keys_gen,
    ALPHANUMERIC_LIST,
    HEX_LIST,
    BASE64_LIST,
    SAFE_LIST,
    LOWERCASE_LIST,
    UPPERCASE_LIST,
    NUMBERS_LIST,
    PRINTABLE_LIST,
    PRESETS,
)


class TestKeysVerifyBasicFunctionality:
    """Tests for basic keys_verify() functionality and return structure."""

    def test_keys_verify_returns_dict(self):
        """keys_verify() should return a dictionary."""
        result = keys_verify("test_key")
        assert isinstance(result, dict)

    def test_keys_verify_dict_has_required_keys(self):
        """Result dict should contain all required keys."""
        result = keys_verify("test_key")
        required_keys = {"valid", "expected_charset", "length", "min_length", "max_length", "reasons"}
        assert set(result.keys()) == required_keys

    def test_keys_verify_valid_is_boolean(self):
        """'valid' field should be a boolean."""
        result = keys_verify("test")
        assert isinstance(result["valid"], bool)

    def test_keys_verify_reasons_is_list(self):
        """'reasons' field should be a list of strings."""
        result = keys_verify("test")
        assert isinstance(result["reasons"], list)
        assert all(isinstance(r, str) for r in result["reasons"])

    def test_keys_verify_length_is_integer(self):
        """'length' field should be an integer."""
        result = keys_verify("test")
        assert isinstance(result["length"], int)

    def test_keys_verify_expected_charset_is_list_or_empty(self):
        """'expected_charset' should be a list."""
        result = keys_verify("test")
        assert isinstance(result["expected_charset"], list)


class TestKeysVerifyValidKeysNoAlphabet:
    """Tests for valid keys when no alphabet constraint is provided."""

    def test_keys_verify_valid_key_no_constraints(self):
        """Key with no alphabet specified should be valid."""
        result = keys_verify("test123")
        assert result["valid"] is True
        assert result["length"] == 7
        assert "No errors" in result["reasons"][0]

    def test_keys_verify_empty_string_no_constraints(self):
        """Empty string with no constraints should be valid."""
        result = keys_verify("")
        assert result["valid"] is True
        assert result["length"] == 0
        assert "No errors" in result["reasons"][0]

    def test_keys_verify_special_characters_no_constraints(self):
        """Special characters valid when no alphabet constraint."""
        result = keys_verify("!@#$%^&*()")
        assert result["valid"] is True
        assert "No errors" in result["reasons"][0]

    def test_keys_verify_unicode_no_constraints(self):
        """Unicode characters valid when no alphabet constraint."""
        result = keys_verify("αβγδ测试")
        assert result["valid"] is True


class TestKeysVerifyValidKeysWithPresets:
    """Tests for valid keys using preset alphabets."""

    def test_keys_verify_alphanumeric_preset_valid(self):
        """Valid alphanumeric key with preset."""
        key = keys_gen(preset="alphanumeric", length=20)
        result = keys_verify(key, alphabet="alphanumeric")
        assert result["valid"] is True
        assert "No errors" in result["reasons"][0]

    def test_keys_verify_hex_preset_valid(self):
        """Valid hex key with preset."""
        key = keys_gen(preset="hex", length=20)
        result = keys_verify(key, alphabet="hex")
        assert result["valid"] is True

    def test_keys_verify_base64_preset_valid(self):
        """Valid base64 key with preset."""
        key = keys_gen(preset="base64", length=20)
        result = keys_verify(key, alphabet="base64")
        assert result["valid"] is True

    def test_keys_verify_safe_preset_valid(self):
        """Valid safe key with preset."""
        key = keys_gen(preset="safe", length=20)
        result = keys_verify(key, alphabet="safe")
        assert result["valid"] is True

    def test_keys_verify_lowercase_preset_valid(self):
        """Valid lowercase key with preset."""
        key = keys_gen(preset="lowercase", length=20)
        result = keys_verify(key, alphabet="lowercase")
        assert result["valid"] is True

    def test_keys_verify_uppercase_preset_valid(self):
        """Valid uppercase key with preset."""
        key = keys_gen(preset="uppercase", length=20)
        result = keys_verify(key, alphabet="uppercase")
        assert result["valid"] is True

    def test_keys_verify_numbers_preset_valid(self):
        """Valid numbers key with preset."""
        key = keys_gen(preset="numbers", length=20)
        result = keys_verify(key, alphabet="numbers")
        assert result["valid"] is True

    def test_keys_verify_printable_preset_valid(self):
        """Valid printable key with preset."""
        key = keys_gen(preset="printable", length=20)
        result = keys_verify(key, alphabet="printable")
        assert result["valid"] is True


class TestKeysVerifyValidKeysWithCustomAlphabet:
    """Tests for valid keys using custom alphabets."""

    def test_keys_verify_custom_alphabet_valid(self):
        """Custom alphabet constraint should validate correctly."""
        key = keys_gen(alphabet=list("ABC"), length=10)
        result = keys_verify(key, alphabet=list("ABC"))
        assert result["valid"] is True

    def test_keys_verify_custom_alphabet_single_char(self):
        """Custom single-character alphabet."""
        result = keys_verify("XXXXX", alphabet=list("X"))
        assert result["valid"] is True
        assert result["length"] == 5

    def test_keys_verify_custom_alphabet_special_chars(self):
        """Custom alphabet with special characters."""
        custom_alpha = list("!@#$%")
        key = "!@#!@#!@"
        result = keys_verify(key, alphabet=custom_alpha)
        assert result["valid"] is True

    def test_keys_verify_expected_charset_matches_custom(self):
        """expected_charset should match provided custom alphabet."""
        custom_alpha = list("ABC")
        result = keys_verify("ABC", alphabet=custom_alpha)
        assert result["expected_charset"] == custom_alpha


class TestKeysVerifyInvalidCharacters:
    """Tests for invalid character detection."""

    def test_keys_verify_invalid_chars_with_preset(self):
        """Should detect invalid characters with preset."""
        result = keys_verify("ABC123xyz", alphabet="numbers")
        assert result["valid"] is False
        assert "Invalid characters" in result["reasons"][0]

    def test_keys_verify_invalid_chars_identified(self):
        """Should identify which characters are invalid."""
        result = keys_verify("A1B2C3", alphabet="numbers")
        assert result["valid"] is False
        # Invalid chars are A, B, C
        reasons_str = " ".join(result["reasons"])
        assert "A" in reasons_str or "B" in reasons_str or "C" in reasons_str

    def test_keys_verify_single_invalid_char(self):
        """Single invalid character should fail validation."""
        result = keys_verify("abc1def", alphabet="lowercase")
        assert result["valid"] is False
        assert "Invalid characters" in result["reasons"][0]

    def test_keys_verify_multiple_invalid_chars(self):
        """Multiple invalid characters should all be identified."""
        result = keys_verify("a1b2c3", alphabet="lowercase")
        assert result["valid"] is False
        # Should report invalid characters 1, 2, 3
        reasons_str = " ".join(result["reasons"])
        assert "Invalid characters" in reasons_str

    def test_keys_verify_invalid_char_custom_alphabet(self):
        """Invalid char detection with custom alphabet."""
        result = keys_verify("AXYZ", alphabet=list("ABC"))
        assert result["valid"] is False
        assert "Invalid characters" in result["reasons"][0]

    def test_keys_verify_hex_alphabet_rejects_non_hex(self):
        """Hex alphabet should reject non-hex characters."""
        result = keys_verify("ABCDEFGH", alphabet="hex")
        assert result["valid"] is False
        # G, H are not valid hex

    def test_keys_verify_empty_string_with_alphabet(self):
        """Empty string with alphabet should be valid."""
        result = keys_verify("", alphabet="alphanumeric")
        assert result["valid"] is True


class TestKeysVerifyMinLength:
    """Tests for minimum length validation."""

    def test_keys_verify_min_length_pass(self):
        """Key longer than min_length should pass."""
        result = keys_verify("hello", min_length=3)
        assert result["valid"] is True

    def test_keys_verify_min_length_exact(self):
        """Key exactly at min_length should pass."""
        result = keys_verify("hello", min_length=5)
        assert result["valid"] is True

    def test_keys_verify_min_length_fail(self):
        """Key shorter than min_length should fail."""
        result = keys_verify("hi", min_length=5)
        assert result["valid"] is False
        assert "Length smaller than minimum" in result["reasons"][0]

    def test_keys_verify_min_length_zero(self):
        """min_length=0 should allow empty strings."""
        result = keys_verify("", min_length=0)
        assert result["valid"] is True

    def test_keys_verify_min_length_empty_key_fails(self):
        """Empty key with min_length > 0 should fail."""
        result = keys_verify("", min_length=1)
        assert result["valid"] is False

    def test_keys_verify_min_length_large_key(self):
        """Large key with reasonable min_length should pass."""
        result = keys_verify("x" * 1000, min_length=100)
        assert result["valid"] is True

    def test_keys_verify_min_length_reason_message(self):
        """Reason message should include length info."""
        result = keys_verify("abc", min_length=10)
        assert result["valid"] is False
        # Should mention the actual length (3)
        reasons_str = " ".join(result["reasons"])
        assert "3" in reasons_str


class TestKeysVerifyMaxLength:
    """Tests for maximum length validation."""

    def test_keys_verify_max_length_pass(self):
        """Key shorter than max_length should pass."""
        result = keys_verify("hi", max_length=10)
        assert result["valid"] is True

    def test_keys_verify_max_length_exact(self):
        """Key exactly at max_length should pass."""
        result = keys_verify("hello", max_length=5)
        assert result["valid"] is True

    def test_keys_verify_max_length_fail(self):
        """Key longer than max_length should fail."""
        result = keys_verify("hello", max_length=3)
        assert result["valid"] is False
        assert "Length larger than maximum" in result["reasons"][0]

    def test_keys_verify_max_length_empty_string(self):
        """Empty string within max_length should pass."""
        result = keys_verify("", max_length=10)
        assert result["valid"] is True

    def test_keys_verify_max_length_zero(self):
        """max_length=0 should only allow empty strings."""
        result = keys_verify("", max_length=0)
        assert result["valid"] is True

    def test_keys_verify_max_length_zero_rejects_content(self):
        """max_length=0 should reject non-empty strings."""
        result = keys_verify("x", max_length=0)
        assert result["valid"] is False

    def test_keys_verify_max_length_reason_message(self):
        """Reason message should include length info."""
        result = keys_verify("verylongstring", max_length=5)
        assert result["valid"] is False
        reasons_str = " ".join(result["reasons"])
        # Should mention the actual length
        assert "14" in reasons_str


class TestKeysVerifyMinMaxLength:
    """Tests for combined min and max length validation."""

    def test_keys_verify_min_max_within_range(self):
        """Key within min and max range should pass."""
        result = keys_verify("hello", min_length=3, max_length=10)
        assert result["valid"] is True

    def test_keys_verify_min_max_exact_min(self):
        """Key at exact min_length should pass."""
        result = keys_verify("abc", min_length=3, max_length=10)
        assert result["valid"] is True

    def test_keys_verify_min_max_exact_max(self):
        """Key at exact max_length should pass."""
        result = keys_verify("hello", min_length=3, max_length=5)
        assert result["valid"] is True

    def test_keys_verify_min_max_below_min(self):
        """Key below min_length should fail."""
        result = keys_verify("ab", min_length=3, max_length=10)
        assert result["valid"] is False

    def test_keys_verify_min_max_above_max(self):
        """Key above max_length should fail."""
        result = keys_verify("abcdefghij", min_length=3, max_length=5)
        assert result["valid"] is False

    def test_keys_verify_min_greater_than_max(self):
        """When min > max, keys within actual range still follow logic."""
        # This tests the current behavior - min takes priority in the code
        result = keys_verify("abc", min_length=10, max_length=3)
        assert result["valid"] is False  # Fails min check


class TestKeysVerifyPrefixValidation:
    """Tests for prefix validation."""

    def test_keys_verify_prefix_valid(self):
        """Key with correct prefix should pass."""
        result = keys_verify("PREFIX_rest", prefix="PREFIX_")
        assert result["valid"] is True

    def test_keys_verify_prefix_invalid(self):
        """Key with incorrect prefix should fail."""
        result = keys_verify("WRONG_rest", prefix="PREFIX_")
        assert result["valid"] is False
        assert "Invalid prefix" in result["reasons"][0]

    def test_keys_verify_prefix_missing(self):
        """Key without prefix should fail."""
        result = keys_verify("rest", prefix="PREFIX_")
        assert result["valid"] is False

    def test_keys_verify_prefix_single_char(self):
        """Single character prefix should work."""
        result = keys_verify("Xrest", prefix="X")
        assert result["valid"] is True

    def test_keys_verify_prefix_special_chars(self):
        """Prefix with special characters should work."""
        result = keys_verify(">>key<<", prefix=">>")
        assert result["valid"] is True

    def test_keys_verify_prefix_none(self):
        """Prefix=None should not validate prefix."""
        result = keys_verify("anykey", prefix=None)
        # Should not have prefix-related failures
        reasons_str = " ".join(result["reasons"])
        assert "prefix" not in reasons_str.lower() or "No errors" in result["reasons"][0]

    def test_keys_verify_prefix_reason_shows_expected_found(self):
        """Prefix error should show expected vs found."""
        result = keys_verify("ABCtest", prefix="XYZ")
        assert result["valid"] is False
        reasons_str = result["reasons"][0]
        assert "XYZ" in reasons_str  # Expected
        assert "ABC" in reasons_str  # Found

    def test_keys_verify_prefix_case_sensitive(self):
        """Prefix validation should be case-sensitive."""
        result = keys_verify("PREFIXtest", prefix="prefix")
        assert result["valid"] is False

    def test_keys_verify_prefix_with_generated_key(self):
        """Verify generated key with matching prefix."""
        key = keys_gen(prefix="TOKEN_", length=20)
        result = keys_verify(key, prefix="TOKEN_")
        assert result["valid"] is True


class TestKeysVerifySuffixValidation:
    """Tests for suffix validation."""

    def test_keys_verify_suffix_valid(self):
        """Key with correct suffix should pass."""
        result = keys_verify("rest_SUFFIX", suffix="_SUFFIX")
        assert result["valid"] is True

    def test_keys_verify_suffix_invalid(self):
        """Key with incorrect suffix should fail."""
        result = keys_verify("rest_WRONG", suffix="_SUFFIX")
        assert result["valid"] is False
        assert "Invalid suffix" in result["reasons"][0]

    def test_keys_verify_suffix_missing(self):
        """Key without suffix should fail."""
        result = keys_verify("rest", suffix="_SUFFIX")
        assert result["valid"] is False

    def test_keys_verify_suffix_single_char(self):
        """Single character suffix should work."""
        result = keys_verify("restX", suffix="X")
        assert result["valid"] is True

    def test_keys_verify_suffix_special_chars(self):
        """Suffix with special characters should work."""
        result = keys_verify("key>>", suffix=">>")
        assert result["valid"] is True

    def test_keys_verify_suffix_none(self):
        """Suffix=None should not validate suffix."""
        result = keys_verify("anykey", suffix=None)
        reasons_str = " ".join(result["reasons"])
        assert "suffix" not in reasons_str.lower() or "No errors" in result["reasons"][0]

    def test_keys_verify_suffix_reason_shows_expected_found(self):
        """Suffix error should show expected vs found."""
        result = keys_verify("testXYZ", suffix="ABC")
        assert result["valid"] is False
        reasons_str = result["reasons"][0]
        assert "ABC" in reasons_str  # Expected
        assert "XYZ" in reasons_str  # Found

    def test_keys_verify_suffix_case_sensitive(self):
        """Suffix validation should be case-sensitive."""
        result = keys_verify("testSUFFIX", suffix="suffix")
        assert result["valid"] is False

    def test_keys_verify_suffix_with_generated_key(self):
        """Verify generated key with matching suffix."""
        key = keys_gen(suffix="_TOKEN", length=20)
        result = keys_verify(key, suffix="_TOKEN")
        assert result["valid"] is True


class TestKeysVerifyPrefixAndSuffix:
    """Tests for combined prefix and suffix validation."""

    def test_keys_verify_prefix_and_suffix_both_valid(self):
        """Key with both valid prefix and suffix should pass."""
        result = keys_verify("PRE_middle_SUF", prefix="PRE_", suffix="_SUF")
        assert result["valid"] is True

    def test_keys_verify_prefix_valid_suffix_invalid(self):
        """Key with valid prefix but invalid suffix should fail."""
        result = keys_verify("PRE_middle_WRONG", prefix="PRE_", suffix="_SUF")
        assert result["valid"] is False
        assert "Invalid suffix" in result["reasons"][0]

    def test_keys_verify_prefix_invalid_suffix_valid(self):
        """Key with invalid prefix but valid suffix should fail."""
        result = keys_verify("WRONG_middle_SUF", prefix="PRE_", suffix="_SUF")
        assert result["valid"] is False
        assert "Invalid prefix" in result["reasons"][0]

    def test_keys_verify_prefix_and_suffix_both_invalid(self):
        """Key with both invalid prefix and suffix should fail."""
        result = keys_verify("WRONG_middle_WRONG", prefix="PRE_", suffix="_SUF")
        assert result["valid"] is False
        # Should have both errors
        reasons_str = " ".join(result["reasons"])
        assert "prefix" in reasons_str.lower() and "suffix" in reasons_str.lower()

    def test_keys_verify_prefix_suffix_with_generated_key(self):
        """Verify generated key with both prefix and suffix."""
        key = keys_gen(prefix="START_", suffix="_END", length=15)
        result = keys_verify(key, prefix="START_", suffix="_END")
        assert result["valid"] is True

    def test_keys_verify_overlapping_prefix_suffix(self):
        """Test with prefix and suffix that could overlap."""
        result = keys_verify("ABCmiddleABC", prefix="ABC", suffix="ABC")
        assert result["valid"] is True

    def test_keys_verify_adjacent_prefix_suffix(self):
        """Test with no content between prefix and suffix."""
        # Note: This depends on implementation details
        result = keys_verify("PRESUF", prefix="PRE", suffix="SUF")
        assert result["valid"] is True


class TestKeysVerifyComplexScenarios:
    """Tests combining alphabet, length, and prefix/suffix constraints."""

    def test_keys_verify_all_constraints_valid(self):
        """Key passing all constraints should be valid."""
        key = keys_gen(preset="hex", prefix="HEX_", suffix="_END", length=10)
        result = keys_verify(
            key,
            alphabet="hex",
            min_length=8,
            max_length=15,
            prefix="HEX_",
            suffix="_END"
        )
        assert result["valid"] is True

    def test_keys_verify_alphabet_and_length(self):
        """Alphabet and length constraints together."""
        result = keys_verify("ABC123", alphabet=list("ABC123"), min_length=5, max_length=10)
        assert result["valid"] is True

    def test_keys_verify_alphabet_and_prefix(self):
        """Alphabet and prefix constraints together."""
        result = keys_verify("KEY_abc123", alphabet="lowercase", prefix="KEY_")
        assert result["valid"] is True

    def test_keys_verify_alphabet_and_suffix(self):
        """Alphabet and suffix constraints together."""
        result = keys_verify("abc123_END", alphabet="alphanumeric", suffix="_END")
        assert result["valid"] is True

    def test_keys_verify_length_and_prefix(self):
        """Length and prefix constraints together."""
        result = keys_verify("PRE_rest", min_length=5, max_length=10, prefix="PRE_")
        assert result["valid"] is True

    def test_keys_verify_length_and_suffix(self):
        """Length and suffix constraints together."""
        result = keys_verify("rest_SUF", min_length=5, max_length=10, suffix="_SUF")
        assert result["valid"] is True

    def test_keys_verify_multiple_constraints_fail_alphabet(self):
        """Multiple constraints with alphabet failure."""
        result = keys_verify(
            "KEY_xyz123",
            alphabet="numbers",
            prefix="KEY_",
            min_length=8
        )
        assert result["valid"] is False
        assert "Invalid characters" in result["reasons"][0]

    def test_keys_verify_multiple_constraints_fail_length(self):
        """Multiple constraints with length failure."""
        result = keys_verify(
            "KEY_x",
            alphabet="alphanumeric",
            prefix="KEY_",
            min_length=10
        )
        assert result["valid"] is False
        assert "Length smaller than minimum" in result["reasons"][0]

    def test_keys_verify_multiple_constraints_fail_prefix(self):
        """Multiple constraints with prefix failure."""
        result = keys_verify(
            "WRONG_abc123",
            alphabet="alphanumeric",
            prefix="KEY_",
            min_length=8
        )
        assert result["valid"] is False
        assert "Invalid prefix" in result["reasons"][0]


class TestKeysVerifyEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_keys_verify_very_long_key(self):
        """Very long key validation."""
        long_key = "x" * 10000
        result = keys_verify(long_key, alphabet=list("x"))
        assert result["valid"] is True
        assert result["length"] == 10000

    def test_keys_verify_unicode_key(self):
        """Unicode characters in key."""
        result = keys_verify("αβγδε", alphabet=list("αβγδε"))
        assert result["valid"] is True

    def test_keys_verify_key_with_spaces(self):
        """Key containing spaces."""
        result = keys_verify("hello world", alphabet=list("helo wrd"))
        assert result["valid"] is True

    def test_keys_verify_key_with_newlines(self):
        """Key containing newlines."""
        result = keys_verify("hello\nworld", alphabet=list("helow\n"))
        assert result["valid"] is True

    def test_keys_verify_single_char_key(self):
        """Single character key."""
        result = keys_verify("X", alphabet=list("X"))
        assert result["valid"] is True
        assert result["length"] == 1

    def test_keys_verify_prefix_equals_entire_key(self):
        """Prefix that is the entire key."""
        result = keys_verify("PREFIX", prefix="PREFIX")
        assert result["valid"] is True

    def test_keys_verify_suffix_equals_entire_key(self):
        """Suffix that is the entire key."""
        result = keys_verify("SUFFIX", suffix="SUFFIX")
        assert result["valid"] is True

    def test_keys_verify_prefix_suffix_equal_entire_key(self):
        """Prefix and suffix together equal entire key."""
        result = keys_verify("PRESUF", prefix="PRE", suffix="SUF")
        assert result["valid"] is True

    def test_keys_verify_alphabet_none_explicit(self):
        """Explicitly passing alphabet=None should allow any character."""
        result = keys_verify("any!@#$%", alphabet=None)
        assert result["valid"] is True


class TestKeysVerifyReasonMessages:
    """Tests for the quality and content of reason messages."""

    def test_keys_verify_no_errors_message(self):
        """Valid key should have 'No errors' message."""
        result = keys_verify("test", alphabet="alphanumeric")
        assert "No errors" in result["reasons"][0]

    def test_keys_verify_single_reason_on_valid(self):
        """Valid key should have exactly one reason message."""
        result = keys_verify("test")
        assert len(result["reasons"]) == 1

    def test_keys_verify_invalid_chars_reason_format(self):
        """Invalid chars reason should list the characters."""
        result = keys_verify("a1b2", alphabet="lowercase")
        reasons_str = " ".join(result["reasons"])
        assert "1" in reasons_str and "2" in reasons_str

    def test_keys_verify_multiple_reasons(self):
        """Invalid key can have multiple reason messages."""
        result = keys_verify(
            "WRONG_x",
            alphabet="numbers",
            min_length=10,
            prefix="KEY_"
        )
        assert result["valid"] is False
        assert len(result["reasons"]) > 1

    def test_keys_verify_length_min_reason_includes_value(self):
        """Min length error should show actual length."""
        result = keys_verify("abc", min_length=10)
        reasons_str = " ".join(result["reasons"])
        assert "3" in reasons_str

    def test_keys_verify_length_max_reason_includes_value(self):
        """Max length error should show actual length."""
        result = keys_verify("abcdefghij", max_length=5)
        reasons_str = " ".join(result["reasons"])
        assert "10" in reasons_str


class TestKeysVerifyPresetRecognition:
    """Tests to verify preset string names are recognized."""

    def test_keys_verify_recognizes_hex_preset(self):
        """String 'hex' should be recognized as preset."""
        result = keys_verify("abc123", alphabet="hex")
        assert result["expected_charset"] == HEX_LIST

    def test_keys_verify_recognizes_alphanumeric_preset(self):
        """String 'alphanumeric' should be recognized as preset."""
        result = keys_verify("ABC123", alphabet="alphanumeric")
        assert result["expected_charset"] == ALPHANUMERIC_LIST

    def test_keys_verify_recognizes_base64_preset(self):
        """String 'base64' should be recognized as preset."""
        result = keys_verify("ABC123+/", alphabet="base64")
        assert result["expected_charset"] == BASE64_LIST

    def test_keys_verify_recognizes_safe_preset(self):
        """String 'safe' should be recognized as preset."""
        result = keys_verify("ABC123-_", alphabet="safe")
        assert result["expected_charset"] == SAFE_LIST

    def test_keys_verify_recognizes_lowercase_preset(self):
        """String 'lowercase' should be recognized as preset."""
        result = keys_verify("abc", alphabet="lowercase")
        assert result["expected_charset"] == LOWERCASE_LIST

    def test_keys_verify_recognizes_uppercase_preset(self):
        """String 'uppercase' should be recognized as preset."""
        result = keys_verify("ABC", alphabet="uppercase")
        assert result["expected_charset"] == UPPERCASE_LIST

    def test_keys_verify_recognizes_numbers_preset(self):
        """String 'numbers' should be recognized as preset."""
        result = keys_verify("123", alphabet="numbers")
        assert result["expected_charset"] == NUMBERS_LIST

    def test_keys_verify_recognizes_printable_preset(self):
        """String 'printable' should be recognized as preset."""
        result = keys_verify("abc", alphabet="printable")
        assert result["expected_charset"] == PRINTABLE_LIST


class TestKeysVerifyLengthFieldAccuracy:
    """Tests to verify the length field reports correct values."""

    def test_keys_verify_length_reports_core_length(self):
        """Length should be of core string, excluding prefix/suffix."""
        result = keys_verify("PRE_middle_SUF", prefix="PRE_", suffix="_SUF")
        # Expected: length of "middle" = 6
        assert result["length"] == 6

    def test_keys_verify_length_without_prefix_suffix(self):
        """Length should equal string length when no prefix/suffix."""
        result = keys_verify("hello", prefix=None, suffix=None)
        assert result["length"] == 5

    def test_keys_verify_length_with_prefix_only(self):
        """Length should exclude prefix."""
        result = keys_verify("PREhello", prefix="PRE")
        assert result["length"] == 5

    def test_keys_verify_length_with_suffix_only(self):
        """Length should exclude suffix."""
        result = keys_verify("helloSUF", suffix="SUF")
        assert result["length"] == 5

    def test_keys_verify_min_max_length_fields(self):
        """min_length and max_length fields should be preserved."""
        result = keys_verify("test", min_length=2, max_length=10)
        assert result["min_length"] == 2
        assert result["max_length"] == 10

    def test_keys_verify_none_length_fields(self):
        """min_length and max_length should be None when not provided."""
        result = keys_verify("test")
        assert result["min_length"] is None
        assert result["max_length"] is None


class TestKeysVerifyIntegration:
    """Integration tests combining multiple features."""

    def test_keys_verify_generated_key_full_validation(self):
        """Generated key with all constraints should pass own verification."""
        key = keys_gen(
            preset="alphanumeric",
            length=30,
            prefix="APP_",
            suffix="_TOKEN"
        )
        result = keys_verify(
            key,
            alphabet="alphanumeric",
            min_length=25,
            max_length=35,
            prefix="APP_",
            suffix="_TOKEN"
        )
        assert result["valid"] is True

    def test_keys_verify_custom_alphabet_generated_key(self):
        """Generated key with custom alphabet should verify correctly."""
        custom = list("ABCXYZ")
        key = keys_gen(alphabet=custom, length=20)
        result = keys_verify(key, alphabet=custom)
        assert result["valid"] is True

    def test_keys_verify_batch_consistency(self):
        """Multiple generated keys should all verify successfully."""
        from tinygenkey.main import keys_seq
        keys = keys_seq(count=10, preset="hex", length=20)
        for key in keys:
            result = keys_verify(key, alphabet="hex")
            assert result["valid"] is True

    def test_keys_verify_stress_test_long_key(self):
        """Very long key with all constraints should validate."""
        long_key = keys_gen(length=5000, preset="safe")
        result = keys_verify(
            long_key,
            alphabet="safe",
            min_length=4000,
            max_length=6000
        )
        assert result["valid"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
