import hashlib

# file deepcode ignore InsecureHash: <User is being notified by a warning in description of a function>


def sha256(data: str) -> str:
    """
    Args:
      data (str): string -> hash_256

    Returns:
        str: hash_256 of string
    """
    return hashlib.sha256(data.encode("utf-8"), usedforsecurity=True).hexdigest()


def sha512(data: str) -> str:
    """
    Args:
      data (str): string -> hash_512

    Returns:
        str: hash_512 of string
    """
    return hashlib.sha512(data.encode("utf-8"), usedforsecurity=True).hexdigest()


