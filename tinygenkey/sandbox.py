from main import *

def keys_format(
        key: str,
        group_size: int = 4,
        sep: str = "-",
) -> str:
    """
    Format a key with separators for readability.

    Args:
        key: The key to format
        group_size: Characters per group (default 4)
        sep: What to put between groups (default "-")

    Returns:
        Formatted key string

    Examples:
        >>> keys_format("ABCD1234EFGH5678")
        "ABCD-1234-EFGH-5678"

        >>> keys_format("ABCD1234EFGH5678", group_size=8, separator=".")
        "ABCD1234.EFGH5678"
    """
    if key == '':
        return ''

    if len(key) < group_size:
        return key

    chunks = []
    for i in range(0, len(key), group_size):
        chunk = key[i : i + group_size]
        chunks.append(chunk)
    result = sep.join(chunks)
    return result

if __name__ == "__main__":
    inp = input("Enter a key to be formatted: ")
    grp = input("Enter the group size (will default to 4): ")
    sep = input("Enter a separator (will default to '-'): ")

    if not sep:
        sep = '-'

    if not grp:
        grp = 4

    try:
        int_grp = int(grp)
    except ValueError as e:
        print(f"Error: {e}")
        exit()

    res = keys_format(inp, int_grp, sep)
    print(res)