# src/core/hash_functions.py
def fnv1a(string: str, hash_val: int, iv: int, mask: int) -> int:
    for c in string.encode('utf-8'):
        hash_val ^= c
        hash_val = (hash_val * iv) & 0xFFFFFFFFFFFFFFFF
    return hash_val & mask


def fnv1a_bo3(string: str) -> int:
    h = fnv1a(string.lower(), 0x4B9ACE2F, 0x1000193, 0xFFFFFFFF)
    h = (h * 0x1000193) & 0xFFFFFFFFFFFFFFFF
    return h & 0xFFFFFFFF


def black_ops_3_scr(string: str) -> int:
    return fnv1a_bo3(string)