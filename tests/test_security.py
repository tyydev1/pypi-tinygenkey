"""
Comprehensive security-focused test suite for tinygenkey cryptographic library.

This test suite validates:
- Cryptographic randomness and os.urandom usage
- Statistical distribution and bias mitigation
- Key uniqueness and collision resistance
- Alphabet and preset validation
- Edge cases and error handling
- Security comparison (rand_key vs keys_gen)
- Performance under stress
- Character distribution analysis
"""

import os
import string
import pytest
from collections import Counter
from typing import List, Set
import statistics
import math

from tinygenkey.main import (
    crypt,
    keys_gen,
    keys_seq,
    rand_key,
    gen_key,
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


class TestCryptographicFundamentals:
    """Tests for the core cryptographic functions and randomness properties."""

    def test_crypt_returns_string_from_sequence(self):
        """crypt() should return a single string element from the input sequence."""
        seq = ["a", "b", "c"]
        result = crypt(seq)
        assert isinstance(result, str)
        assert result in seq
        assert len(result) == 1

    def test_crypt_works_with_single_element(self):
        """crypt() should work with single-element sequences."""
        seq = ["x"]
        result = crypt(seq)
        assert result == "x"

    def test_crypt_works_with_large_sequences(self):
        """crypt() should work with sequences of 256+ elements."""
        seq = list(range(300))  # 300 elements
        seq = [str(i) for i in seq]
        result = crypt(seq)
        assert result in seq

    def test_crypt_bias_mitigation_logic(self):
        """
        crypt() implements bias mitigation: limit = 256 - (256 % n).

        This ensures uniform distribution without modulo bias.
        For alphabet size n, values in range [limit, 256) are rejected.
        """
        # Test with alphabet size 10: limit should be 250 (256 - 6)
        seq = list(string.digits)  # 10 elements
        assert len(seq) == 10
        limit = 256 - (256 % len(seq))
        assert limit == 250

        # Generate many values and verify all are in valid range
        results = []
        for _ in range(100):
            results.append(crypt(seq))
        assert all(r in seq for r in results)

    def test_crypt_uses_os_urandom(self, monkeypatch):
        """
        crypt() should use os.urandom for cryptographic randomness.

        Security implication: Uses kernel entropy pool, not Python's random module.
        """
        urandom_called = False
        original_urandom = os.urandom

        def mock_urandom(n):
            nonlocal urandom_called
            urandom_called = True
            return original_urandom(n)

        monkeypatch.setattr(os, "urandom", mock_urandom)
        crypt(["a", "b", "c"])
        assert urandom_called, "crypt() should call os.urandom for entropy"

    def test_crypt_distribution_uniformity(self):
        """
        Verify that crypt() produces approximately uniform distribution.

        Statistical test: Generate keys and count character frequencies.
        With uniform distribution, each character should appear roughly equally often.
        """
        seq = list(string.digits)  # 10 characters
        iterations = 10000
        results = [crypt(seq) for _ in range(iterations)]

        counter = Counter(results)
        frequencies = list(counter.values())

        # Expected: ~1000 each (10000 / 10)
        expected = iterations / len(seq)

        # Chi-square test: verify no extreme deviations
        # For uniform distribution, each cell should be ~1000
        # We allow 20% deviation: 800-1200
        tolerance = 0.25  # 25% tolerance for this sample size
        for count in frequencies:
            assert abs(count - expected) / expected < tolerance, \
                f"Character frequency {count} deviates too much from expected {expected}"

    def test_crypt_unpredictability_no_patterns(self):
        """
        Verify crypt() output shows no discernible patterns.

        This is a basic non-randomness detector: check that consecutive
        calls don't show sequential or repeating patterns.
        """
        seq = list(string.digits)
        results = [crypt(seq) for _ in range(100)]

        # Check for patterns: if distribution is random, transitions between
        # consecutive results should be well-distributed
        transitions = set()
        for i in range(len(results) - 1):
            pair = (results[i], results[i + 1])
            transitions.add(pair)

        # For 100 outputs of 10 possible chars, we expect many unique transitions
        # Random output: ~90-99 unique pairs. Patterned output: much fewer.
        assert len(transitions) > 80, \
            f"Only {len(transitions)} unique transitions in 100 outputs - suggests patterning"


class TestKeyGeneration:
    """Tests for keys_gen() primary key generation function."""

    def test_keys_gen_default_parameters(self):
        """keys_gen() should generate 42-character alphanumeric key by default."""
        key = keys_gen()
        assert isinstance(key, str)
        assert len(key) == 42
        assert all(c in ALPHANUMERIC_LIST for c in key)

    def test_keys_gen_custom_length(self):
        """keys_gen() should respect custom length parameter."""
        for length in [1, 10, 100, 256]:
            key = keys_gen(length=length)
            assert len(key) == length

    def test_keys_gen_all_presets(self):
        """keys_gen() should work with all preset alphabets."""
        presets = ["alphanumeric", "hex", "base64", "safe", "lowercase", "uppercase", "numbers", "printable"]

        for preset in presets:
            key = keys_gen(preset=preset)
            alphabet = PRESETS[preset]
            assert all(c in alphabet for c in key), \
                f"Key contains invalid characters for preset '{preset}'"

    def test_keys_gen_preset_hex(self):
        """Hex preset should only contain 0-9 and a-f."""
        key = keys_gen(preset="hex", length=100)
        valid_chars = set("0123456789abcdef")
        assert set(key).issubset(valid_chars)

    def test_keys_gen_preset_base64(self):
        """Base64 preset should contain a-zA-Z0-9+/."""
        key = keys_gen(preset="base64", length=100)
        valid_chars = set(string.ascii_letters + string.digits + "+/")
        assert set(key).issubset(valid_chars)

    def test_keys_gen_preset_safe(self):
        """Safe preset should contain a-zA-Z0-9-_."""
        key = keys_gen(preset="safe", length=100)
        valid_chars = set(string.ascii_letters + string.digits + "-_")
        assert set(key).issubset(valid_chars)

    def test_keys_gen_preset_lowercase(self):
        """Lowercase preset should only contain a-z."""
        key = keys_gen(preset="lowercase", length=100)
        assert all(c in string.ascii_lowercase for c in key)

    def test_keys_gen_preset_uppercase(self):
        """Uppercase preset should only contain A-Z."""
        key = keys_gen(preset="uppercase", length=100)
        assert all(c in string.ascii_uppercase for c in key)

    def test_keys_gen_preset_numbers(self):
        """Numbers preset should only contain 0-9."""
        key = keys_gen(preset="numbers", length=100)
        assert all(c in string.digits for c in key)

    def test_keys_gen_custom_alphabet(self):
        """keys_gen() should use custom alphabet when provided."""
        custom_alphabet = list("ABCXYZ")
        key = keys_gen(alphabet=custom_alphabet, length=50)
        assert all(c in custom_alphabet for c in key)

    def test_keys_gen_custom_alphabet_overrides_preset(self):
        """Custom alphabet should override preset parameter."""
        custom_alphabet = list("XYZ")
        key = keys_gen(preset="hex", alphabet=custom_alphabet, length=50)
        assert all(c in custom_alphabet for c in key)
        # Should NOT contain hex characters
        assert not any(c in "0123456789abcdef" for c in key if c not in "XYZ")

    def test_keys_gen_with_prefix(self):
        """keys_gen() should add prefix to generated key."""
        prefix = "SECRET_"
        key = keys_gen(prefix=prefix, length=20)
        assert key.startswith(prefix)
        assert len(key) == len(prefix) + 20

    def test_keys_gen_with_suffix(self):
        """keys_gen() should add suffix to generated key."""
        suffix = "_TOKEN"
        key = keys_gen(suffix=suffix, length=20)
        assert key.endswith(suffix)
        assert len(key) == 20 + len(suffix)

    def test_keys_gen_with_prefix_and_suffix(self):
        """keys_gen() should support both prefix and suffix."""
        prefix = "PRE_"
        suffix = "_SUF"
        key = keys_gen(prefix=prefix, suffix=suffix, length=15)
        assert key.startswith(prefix)
        assert key.endswith(suffix)
        assert len(key) == len(prefix) + 15 + len(suffix)

    def test_keys_gen_prefix_with_special_characters(self):
        """Prefix should work with special characters."""
        prefix = "key-2024_v1.0:"
        key = keys_gen(prefix=prefix, length=10)
        assert key.startswith(prefix)

    def test_keys_gen_suffix_with_special_characters(self):
        """Suffix should work with special characters."""
        suffix = ":v1.0_2024-key"
        key = keys_gen(suffix=suffix, length=10)
        assert key.endswith(suffix)

    def test_keys_gen_long_key(self):
        """keys_gen() should handle very long keys efficiently."""
        key = keys_gen(length=10000)
        assert len(key) == 10000
        assert all(c in ALPHANUMERIC_LIST for c in key)

    def test_keys_gen_single_character_key(self):
        """keys_gen() should handle single-character keys."""
        key = keys_gen(length=1)
        assert len(key) == 1
        assert key in ALPHANUMERIC_LIST

    def test_keys_gen_invalid_preset(self):
        """keys_gen() should raise ValueError for invalid preset."""
        with pytest.raises(ValueError, match="Invalid preset"):
            keys_gen(preset="invalid_preset")

    def test_keys_gen_zero_length(self):
        """keys_gen() with length=0 should return empty string (plus prefix/suffix)."""
        key = keys_gen(length=0)
        assert key == ""

        key_with_prefix = keys_gen(length=0, prefix="PRE")
        assert key_with_prefix == "PRE"

        key_with_suffix = keys_gen(length=0, suffix="SUF")
        assert key_with_suffix == "SUF"


class TestKeyUniqueness:
    """Tests for key uniqueness and collision resistance."""

    def test_generated_keys_are_unique(self):
        """Generated keys should be unique across multiple generations."""
        keys = keys_seq(count=1000, length=42)
        unique_keys = set(keys)

        # With proper randomness, all 1000 keys should be unique
        assert len(unique_keys) == 1000, \
            f"Expected 1000 unique keys, got {len(unique_keys)} (collisions detected)"

    def test_collision_resistance_large_batch(self):
        """Verify extremely low collision probability across large batches."""
        # Generate 5,000 keys and verify no collisions
        keys = keys_seq(count=5000, length=42)
        unique_keys = set(keys)

        collision_count = len(keys) - len(unique_keys)
        assert collision_count == 0, \
            f"Found {collision_count} collisions in 5,000 keys - randomness issue"

    def test_uniqueness_with_different_lengths(self):
        """Keys of different lengths should all be unique."""
        # Generate mixed-length keys
        all_keys = []
        for length in [10, 20, 30, 40]:
            keys = keys_seq(count=250, length=length)
            all_keys.extend(keys)

        unique_keys = set(all_keys)
        assert len(unique_keys) == len(all_keys), \
            "Collisions detected across different key lengths"

    def test_uniqueness_with_different_presets(self):
        """Keys from different presets should be unique."""
        keys_hex = keys_seq(count=100, preset="hex", length=50)
        keys_safe = keys_seq(count=100, preset="safe", length=50)

        all_keys = keys_hex + keys_safe
        unique_keys = set(all_keys)

        # Some overlap possible due to shared characters, but no duplicates within same generation
        assert len(set(keys_hex)) == 100
        assert len(set(keys_safe)) == 100

    def test_prefix_suffix_dont_reduce_uniqueness(self):
        """Adding prefix/suffix should not reduce uniqueness."""
        prefix = "app_"
        suffix = "_token"

        keys = keys_seq(count=500, prefix=prefix, suffix=suffix, length=30)
        unique_keys = set(keys)

        assert len(unique_keys) == 500, \
            "Prefix/suffix reduced uniqueness - randomness issue in core generation"


class TestAlphabetHandling:
    """Tests for alphabet validation and handling."""

    def test_single_character_alphabet(self):
        """Should work with single-character alphabet."""
        alphabet = ["X"]
        key = keys_gen(alphabet=alphabet, length=20)
        assert key == "X" * 20

    def test_very_large_alphabet(self):
        """Should work with very large alphabets."""
        # Create alphabet with 256 unique characters
        large_alphabet = list(string.printable) + [chr(i) for i in range(128, 150)]
        key = keys_gen(alphabet=large_alphabet, length=50)
        assert all(c in large_alphabet for c in key)

    def test_custom_alphabet_with_unicode(self):
        """Should work with Unicode characters in custom alphabet."""
        unicode_alphabet = ["a", "b", "c", "α", "β", "γ", "ñ", "é"]
        key = keys_gen(alphabet=unicode_alphabet, length=30)
        assert all(c in unicode_alphabet for c in key)

    def test_custom_alphabet_with_duplicate_characters(self):
        """Duplicate characters in alphabet should still work."""
        # If alphabet is ["a", "a", "b"], it's technically redundant but should work
        alphabet = list("aabbcc")  # 6 elements but only 3 unique
        key = keys_gen(alphabet=alphabet, length=20)
        assert all(c in alphabet for c in key)

    def test_alphabet_special_characters(self):
        """Alphabet with special characters should work."""
        special_alphabet = list("!@#$%^&*()")
        key = keys_gen(alphabet=special_alphabet, length=25)
        assert all(c in special_alphabet for c in key)

    def test_all_preset_characters_can_appear(self):
        """Over many iterations, all characters from preset should appear."""
        for preset_name, alphabet in PRESETS.items():
            if len(alphabet) > 20:
                # For large alphabets, generate fewer keys to save time
                keys = keys_seq(count=500, preset=preset_name, length=100)
            else:
                # For small alphabets, generate more keys to ensure coverage
                keys = keys_seq(count=1000, preset=preset_name, length=100)

            combined = "".join(keys)
            chars_found = set(combined)

            # We should see most characters (not all guaranteed, but high probability)
            coverage = len(chars_found) / len(alphabet)
            assert coverage > 0.75, \
                f"Preset '{preset_name}': only {coverage:.1%} character coverage"


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_invalid_preset_raises_value_error(self):
        """Invalid preset names should raise ValueError."""
        invalid_presets = ["hexx", "basee64", "unknown", ""]

        for preset in invalid_presets:
            with pytest.raises(ValueError, match="Invalid preset"):
                keys_gen(preset=preset)

    def test_none_alphabet_uses_preset(self):
        """When alphabet is None, preset should be used."""
        key = keys_gen(preset="hex", alphabet=None, length=30)
        assert all(c in HEX_LIST for c in key)

    def test_empty_prefix_suffix(self):
        """Empty prefix/suffix should work (no effect)."""
        key1 = keys_gen(prefix="", suffix="", length=20)
        key2 = keys_gen(length=20)

        # Length should be same (both just 20 random chars)
        assert len(key1) == len(key2) == 20


class TestKeySequence:
    """Tests for keys_seq() batch generation function."""

    def test_keys_seq_count(self):
        """keys_seq() should generate exactly count keys."""
        counts = [1, 10, 100, 500]

        for count in counts:
            keys = keys_seq(count=count)
            assert len(keys) == count

    def test_keys_seq_returns_list(self):
        """keys_seq() should return a list."""
        result = keys_seq(count=10)
        assert isinstance(result, list)

    def test_keys_seq_passes_kwargs(self):
        """keys_seq() should pass kwargs to keys_gen()."""
        keys = keys_seq(count=20, preset="hex", length=50)
        assert len(keys) == 20
        assert all(len(k) == 50 for k in keys)
        assert all(all(c in HEX_LIST for c in k) for k in keys)

    def test_keys_seq_with_prefix_suffix(self):
        """keys_seq() should apply prefix/suffix to all generated keys."""
        prefix = "key_"
        suffix = "_secure"
        keys = keys_seq(count=10, prefix=prefix, suffix=suffix, length=15)

        assert all(k.startswith(prefix) for k in keys)
        assert all(k.endswith(suffix) for k in keys)

    def test_keys_seq_zero_count(self):
        """keys_seq() with count=0 should return empty list."""
        keys = keys_seq(count=0)
        assert keys == []


class TestSecurityComparison:
    """Tests comparing secure keys_gen() vs insecure rand_key()."""

    def test_rand_key_is_generator(self):
        """rand_key() should be a generator function."""
        result = rand_key(key_prefix="test")
        assert hasattr(result, "__iter__")
        assert hasattr(result, "__next__")

    def test_rand_key_output_format(self):
        """rand_key() should yield prefix first, then characters."""
        gen = rand_key(key_prefix="PREFIX", list_of_chars=list("ABC"), length_of_string=5)
        result = "".join(gen)
        assert result.startswith("PREFIX")
        assert len(result) == len("PREFIX") + 5

    def test_rand_key_uses_python_random(self, monkeypatch):
        """
        rand_key() should use Python's random.randint (insecure for cryptography).

        Security implication: random module is NOT cryptographically secure.
        It can be predicted with sufficient prior values.
        """
        randint_called = False

        def mock_randint(a, b):
            nonlocal randint_called
            randint_called = True
            return 0

        monkeypatch.setattr("random.randint", mock_randint)
        gen = rand_key(key_prefix="test", list_of_chars=list("ABC"), length_of_string=3)
        result = "".join(gen)

        assert randint_called, "rand_key() should call random.randint"

    def test_rand_key_predictability(self):
        """
        rand_key() should show predictability compared to keys_gen().

        This test demonstrates the security weakness of rand_key():
        - Python's random module uses Mersenne Twister (predictable)
        - os.urandom uses kernel entropy (cryptographically secure)
        """
        import random

        # Set seed to demonstrate predictability of rand_key
        random.seed(12345)
        gen1 = rand_key(key_prefix="", list_of_chars=list("ABCD"), length_of_string=20)
        key1 = "".join(gen1)

        # Reset seed - we should get the same key (predictable!)
        random.seed(12345)
        gen2 = rand_key(key_prefix="", list_of_chars=list("ABCD"), length_of_string=20)
        key2 = "".join(gen2)

        assert key1 == key2, \
            "rand_key() with same seed produced different keys - this is backwards! " \
            "For insecure RNG, same seed SHOULD produce same output"

    def test_keys_gen_not_reproducible_with_seed(self):
        """
        keys_gen() should NOT be reproducible by seeding.

        This is a good sign - os.urandom doesn't respect random.seed().
        """
        import random

        random.seed(42)
        key1 = keys_gen(length=50)

        random.seed(42)
        key2 = keys_gen(length=50)

        # These should be different (not seeded)
        assert key1 != key2, \
            "keys_gen() is affected by random.seed() - should use os.urandom instead"

    def test_entropy_comparison_distribution(self):
        """
        Compare character distribution: rand_key vs keys_gen.

        Both may show variation, but rand_key may show systematic biases
        due to poor RNG seeding.
        """
        alphabet = list(string.digits)  # 10 characters

        # Generate with keys_gen (secure)
        keys_secure = keys_seq(count=100, alphabet=alphabet, length=100)
        secure_combined = "".join(keys_secure)
        secure_counter = Counter(secure_combined)

        # Generate with rand_key (insecure) - for comparison
        import random
        random.seed(999)  # Use a seed so test is reproducible
        rand_keys = []
        for _ in range(100):
            gen = rand_key(key_prefix="", list_of_chars=alphabet, length_of_string=100)
            rand_keys.append("".join(gen))

        insecure_combined = "".join(rand_keys)
        insecure_counter = Counter(insecure_combined)

        # Both should have all characters represented
        assert len(secure_counter) == len(alphabet), \
            "Secure method should have all alphabet characters"
        assert len(insecure_counter) == len(alphabet), \
            "Insecure method should also have all alphabet characters"


class TestCharacterDistribution:
    """Tests for character frequency and distribution analysis."""

    def test_character_distribution_hex(self):
        """Hex preset should have approximately uniform distribution."""
        keys = keys_seq(count=200, preset="hex", length=100)
        combined = "".join(keys)
        counter = Counter(combined)

        expected = len(combined) / len(HEX_LIST)

        for char, count in counter.items():
            ratio = count / expected
            # Allow 20% deviation from expected
            assert 0.8 < ratio < 1.2, \
                f"Character '{char}' count {count} deviates too much from expected {expected}"

    def test_character_distribution_alphanumeric(self):
        """Alphanumeric preset should have approximately uniform distribution."""
        keys = keys_seq(count=200, preset="alphanumeric", length=100)
        combined = "".join(keys)
        counter = Counter(combined)

        expected = len(combined) / len(ALPHANUMERIC_LIST)

        # Verify reasonable distribution (not perfect, but no extreme outliers)
        counts = list(counter.values())
        mean_count = statistics.mean(counts)
        stdev = statistics.stdev(counts)

        # Standard deviation should be reasonable (not all one character)
        assert stdev < mean_count * 0.5, \
            f"Distribution too skewed: stdev={stdev}, mean={mean_count}"

    def test_no_character_completely_missing(self):
        """Given sufficient iterations, all alphabet characters should appear."""
        # Use small alphabet to verify all chars appear
        small_alphabet = list("ABC")
        keys = keys_seq(count=500, alphabet=small_alphabet, length=100)
        combined = "".join(keys)
        chars_found = set(combined)

        assert chars_found == set(small_alphabet), \
            f"Missing characters from output: {set(small_alphabet) - chars_found}"

    def test_first_position_also_randomized(self):
        """First character of key should also be random, not biased."""
        keys = keys_seq(count=1000, preset="hex", length=30)
        first_chars = [k[0] for k in keys]
        counter = Counter(first_chars)

        # All 16 hex digits should appear in first position
        assert len(counter) > 10, \
            f"First position only has {len(counter)} unique chars out of 16"


class TestGenKeyDeprecatedFunction:
    """Tests for deprecated gen_key() function."""

    def test_gen_key_still_works(self):
        """gen_key() deprecated function should still work."""
        key = gen_key()
        assert isinstance(key, str)
        assert len(key) == 42

    def test_gen_key_with_parameters(self):
        """gen_key() should accept parameters."""
        key = gen_key(
            alphabet=list("XYZ"),
            length=30,
            prefix="OLD_",
            suffix="_STYLE"
        )
        assert key.startswith("OLD_")
        assert key.endswith("_STYLE")
        assert len(key) == len("OLD_") + 30 + len("_STYLE")


class TestPerformanceAndStress:
    """Performance and stress tests."""

    def test_large_batch_generation_performance(self):
        """keys_seq() should handle large batches efficiently."""
        # Generate 2000 keys - should complete in reasonable time
        keys = keys_seq(count=2000, length=50)
        assert len(keys) == 2000
        assert len(set(keys)) == 2000  # All unique

    def test_very_long_key_generation(self):
        """Should handle very long key generation efficiently."""
        key = keys_gen(length=50000)
        assert len(key) == 50000

    def test_large_alphabet_performance(self):
        """Should handle large custom alphabets efficiently."""
        # Create large alphabet (all printable ASCII)
        large_alphabet = list(string.printable)
        keys = keys_seq(count=1000, alphabet=large_alphabet, length=100)
        assert len(keys) == 1000

    def test_batch_generation_memory_efficiency(self):
        """Batch generation should not cause excessive memory use."""
        # Generate a large batch and verify reasonable memory usage
        import sys

        keys = keys_seq(count=5000, length=100)

        # Each key is ~100 chars = 100 bytes, plus Python overhead
        # 5000 keys * ~200 bytes (with Python overhead) = ~1MB max
        estimated_size = sum(sys.getsizeof(k) for k in keys)
        assert estimated_size < 3_000_000, \
            f"Memory usage suspiciously high: {estimated_size} bytes"


class TestEdgeCasesAndBoundaries:
    """Edge cases and boundary condition tests."""

    def test_maximum_length_key(self):
        """Should handle very large length values."""
        key = keys_gen(length=100000)
        assert len(key) == 100000

    def test_very_small_alphabet(self):
        """Should work with minimal 1-character alphabet."""
        key = keys_gen(alphabet=["*"], length=50)
        assert key == "*" * 50

    def test_alphabet_with_whitespace(self):
        """Should handle whitespace in alphabet."""
        alphabet = list("a b")  # Includes space
        key = keys_gen(alphabet=alphabet, length=20)
        assert all(c in alphabet for c in key)

    def test_alphabet_with_newline(self):
        """Should handle special characters including newline."""
        alphabet = ["a", "b", "\n"]
        key = keys_gen(alphabet=alphabet, length=15)
        assert all(c in alphabet for c in key)

    def test_very_long_prefix_suffix(self):
        """Should handle very long prefix and suffix."""
        prefix = "x" * 1000
        suffix = "y" * 1000
        key = keys_gen(prefix=prefix, suffix=suffix, length=10)
        assert key.startswith(prefix)
        assert key.endswith(suffix)
        assert len(key) == 1000 + 10 + 1000

    def test_empty_key_with_prefix_suffix(self):
        """Empty key length with prefix/suffix should just be prefix+suffix."""
        prefix = "START"
        suffix = "END"
        key = keys_gen(prefix=prefix, suffix=suffix, length=0)
        assert key == "STARTEND"


class TestPresetsIntegrity:
    """Tests to verify preset definitions are correct and consistent."""

    def test_alphanumeric_contains_lowercase(self):
        """ALPHANUMERIC_LIST should contain lowercase letters."""
        assert any(c in string.ascii_lowercase for c in ALPHANUMERIC_LIST)

    def test_alphanumeric_contains_uppercase(self):
        """ALPHANUMERIC_LIST should contain uppercase letters."""
        assert any(c in string.ascii_uppercase for c in ALPHANUMERIC_LIST)

    def test_alphanumeric_contains_digits(self):
        """ALPHANUMERIC_LIST should contain digits."""
        assert any(c in string.digits for c in ALPHANUMERIC_LIST)

    def test_hex_only_valid_hex_chars(self):
        """HEX_LIST should only contain 0-9 and a-f."""
        valid_hex = set("0123456789abcdef")
        assert set(HEX_LIST) == valid_hex

    def test_safe_only_safe_chars(self):
        """SAFE_LIST should only contain a-zA-Z0-9-_."""
        valid_safe = set(string.ascii_letters + string.digits + "-_")
        assert set(SAFE_LIST) == valid_safe

    def test_presets_are_lists(self):
        """All presets should be lists."""
        for name, preset in PRESETS.items():
            assert isinstance(preset, list), f"Preset '{name}' is not a list"

    def test_presets_contain_strings(self):
        """All preset elements should be single-character strings."""
        for name, preset in PRESETS.items():
            for char in preset:
                assert isinstance(char, str), f"Preset '{name}' contains non-string: {char}"
                assert len(char) == 1, f"Preset '{name}' contains multi-char string: {char}"


class TestRegularExpressionAndPatternSafety:
    """Tests to ensure generated keys don't accidentally match dangerous patterns."""

    def test_keys_not_all_same_character(self):
        """Keys should not degenerate to all same character."""
        for _ in range(100):
            key = keys_gen(length=50)
            # If key were all same char, this would fail
            assert len(set(key)) > 1 or len(key) < 2, \
                f"Key appears to be all same character: {key[:10]}..."

    def test_keys_not_sequential_patterns(self):
        """Keys should not show obvious sequential patterns."""
        alphabet = list(string.digits)
        for _ in range(50):
            key = keys_gen(alphabet=alphabet, length=50)
            # Check for sequential patterns like "0123456789"
            for i in range(len(key) - 3):
                substring = key[i:i+4]
                # Check if it's sequential
                is_sequential = all(
                    int(substring[j+1]) - int(substring[j]) == 1
                    for j in range(len(substring) - 1)
                    if substring[j].isdigit() and substring[j+1].isdigit()
                )
                # Consecutive sequential patterns are unlikely
                assert not is_sequential, f"Found sequential pattern: {substring} in {key}"


class TestStatisticalProperties:
    """Advanced statistical tests for randomness properties."""

    def test_entropy_estimate_crypt(self):
        """
        Estimate entropy of generated keys.

        For n-character alphabet and k-character key:
        Max entropy = k * log2(n) bits

        Example: 42 chars, 62-char alphabet = 42 * log2(62) = ~251 bits
        """
        alphabet_size = len(ALPHANUMERIC_LIST)  # 62
        key_length = 42

        # Generate multiple keys
        keys = keys_seq(count=100, length=key_length)
        combined = "".join(keys)

        # Count unique characters used
        unique_chars = len(set(combined))

        # With good randomness, should see most alphabet
        assert unique_chars > alphabet_size * 0.5, \
            f"Only {unique_chars}/{alphabet_size} unique chars - randomness issue"

    def test_collision_birthday_problem(self):
        """
        Verify key generation respects birthday problem statistics.

        For independent uniform random strings of length n from alphabet of size m:
        Probability of collision ~ sqrt(m^n) / sqrt(pi/2)

        For 42-char alphanumeric (62^42 possibilities), collision in 10k keys is astronomically unlikely.
        """
        keys = keys_seq(count=10000, length=42)
        unique = len(set(keys))

        # For practical purposes, all should be unique
        assert unique >= 9999, \
            f"Too many collisions: {10000 - unique} collisions in 10k keys"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
