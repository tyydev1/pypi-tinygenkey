# Testing Guide for `keys_verify()` Function

## Quick Start

### Install Dependencies
```bash
pip install pytest
```

### Run All Tests
```bash
pytest tests/test_keys_verify.py -v
```

## Test Suite Overview

The `test_keys_verify.py` file contains **116 comprehensive tests** organized into 17 test classes, covering:

1. **Return Value Structure** - Validates dict format and required fields
2. **Valid Keys** - Tests with presets and custom alphabets
3. **Invalid Characters** - Detection and reporting
4. **Length Validation** - min_length, max_length, and combinations
5. **Prefix Validation** - Valid, invalid, and edge cases
6. **Suffix Validation** - Valid, invalid, and edge cases
7. **Combined Constraints** - Multiple validations at once
8. **Edge Cases** - Very long keys, unicode, special characters
9. **Error Messages** - Quality and informativeness
10. **Integration** - Real-world usage scenarios

## Test Categories

### Basic Tests (6 tests)
```bash
pytest tests/test_keys_verify.py::TestKeysVerifyBasicFunctionality -v
```
Tests the return dictionary structure and data types.

### Alphabet Tests (19 tests)
```bash
pytest tests/test_keys_verify.py::TestKeysVerifyValidKeysWithPresets -v
```
Tests all 8 preset alphabets (alphanumeric, hex, base64, safe, lowercase, uppercase, numbers, printable).

### Length Tests (21 tests)
```bash
pytest tests/test_keys_verify.py::TestKeysVerifyMinLength -v
pytest tests/test_keys_verify.py::TestKeysVerifyMaxLength -v
pytest tests/test_keys_verify.py::TestKeysVerifyMinMaxLength -v
```
Tests minimum length, maximum length, and combined constraints.

### Prefix Tests (9 tests)
```bash
pytest tests/test_keys_verify.py::TestKeysVerifyPrefixValidation -v
```
Tests prefix validation with valid/invalid cases.

### Suffix Tests (9 tests)
```bash
pytest tests/test_keys_verify.py::TestKeysVerifySuffixValidation -v
```
Tests suffix validation with valid/invalid cases.

### Complex Scenarios (9 tests)
```bash
pytest tests/test_keys_verify.py::TestKeysVerifyComplexScenarios -v
```
Tests combining alphabet, length, and prefix/suffix constraints.

### Edge Cases (10 tests)
```bash
pytest tests/test_keys_verify.py::TestKeysVerifyEdgeCases -v
```
Tests boundary conditions like very long keys, unicode, whitespace.

## Running Specific Tests

### Run single test class:
```bash
pytest tests/test_keys_verify.py::TestKeysVerifyMinLength -v
```

### Run single test:
```bash
pytest tests/test_keys_verify.py::TestKeysVerifyMinLength::test_keys_verify_min_length_pass -v
```

### Run tests matching pattern:
```bash
pytest tests/test_keys_verify.py -k "prefix" -v
```

### Show print output:
```bash
pytest tests/test_keys_verify.py -v -s
```

### Run with detailed traceback:
```bash
pytest tests/test_keys_verify.py -v --tb=long
```

## Expected Output

The test suite currently has **51 failing tests** which reveal bugs in the implementation:

1. **Incorrect prefix/suffix core extraction logic** - Slicing indices are wrong
2. **Type checking issue** - Can't use list as dict key when checking presets
3. **Empty alphabet handling** - Should allow any char when alphabet=None
4. **Debug print statements** - Should be removed from production code

## Test Examples

### Example: Valid Key with Preset
```python
def test_keys_verify_hex_preset_valid(self):
    """Valid hex key with preset."""
    key = keys_gen(preset="hex", length=20)
    result = keys_verify(key, alphabet="hex")
    assert result["valid"] is True
```

### Example: Invalid Characters
```python
def test_keys_verify_invalid_chars_with_preset(self):
    """Should detect invalid characters with preset."""
    result = keys_verify("ABC123xyz", alphabet="numbers")
    assert result["valid"] is False
    assert "Invalid characters" in result["reasons"][0]
```

### Example: Length Validation
```python
def test_keys_verify_min_length_fail(self):
    """Key shorter than min_length should fail."""
    result = keys_verify("hi", min_length=5)
    assert result["valid"] is False
    assert "Length smaller than minimum" in result["reasons"][0]
```

### Example: Prefix + Suffix
```python
def test_keys_verify_prefix_and_suffix_both_valid(self):
    """Key with both valid prefix and suffix should pass."""
    result = keys_verify("PRE_middle_SUF", prefix="PRE_", suffix="_SUF")
    assert result["valid"] is True
```

## Understanding Test Failures

When a test fails, look at the captured output to understand what went wrong:

```
tests/test_keys_verify.py::TestKeysVerifyMinLength::test_keys_verify_min_length_pass FAILED

Captured stdout call:
hello
5
```

The print statements show:
1. The core_chars extracted (should be "hello", may be wrong due to slicing bug)
2. The length calculated (should be 5)

## Test Design Principles

1. **Independent** - Each test doesn't depend on others
2. **Repeatable** - Same result on multiple runs
3. **Self-checking** - Clear assertions, not visual inspection
4. **Thorough** - Covers both happy path and error cases
5. **Clear** - Descriptive names explain what's being tested
6. **Isolated** - No test affects another's state

## Contributing Additional Tests

To add more tests, follow the pattern:

```python
def test_descriptive_name_of_what_is_tested(self):
    """Clear docstring explaining the test."""
    # Arrange: Set up test data
    key = "test_key"

    # Act: Call the function
    result = keys_verify(key, alphabet="alphanumeric")

    # Assert: Verify the results
    assert result["valid"] is True
```

## Key Test Statistics

- **Total Tests:** 116
- **Passing:** 65 (56%)
- **Failing:** 51 (44% - revealing bugs)
- **Execution Time:** ~2 seconds
- **Test Organization:** 17 test classes
- **Test Patterns:** Happy path + Error cases + Edge cases

## Debugging Failed Tests

### See what the function returned:
```bash
pytest tests/test_keys_verify.py::TestName::test_name -v -s
```

### See the full difference:
```bash
pytest tests/test_keys_verify.py --tb=long -v
```

### Run only tests that are currently passing:
```bash
pytest tests/test_keys_verify.py --lf -v  # Last Failed
pytest tests/test_keys_verify.py --ff -v  # Failed First
```

## References

- Test file: `/home/razkar/Workspace/GitHub/tyydev1/tinygenkey/tests/test_keys_verify.py`
- Function under test: `/home/razkar/Workspace/GitHub/tyydev1/tinygenkey/tinygenkey/main.py:119-194`
- Full report: `/home/razkar/Workspace/GitHub/tyydev1/tinygenkey/TESTING_REPORT.md`
