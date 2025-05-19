import re

def fnv1a(string, hash_val, iv, mask):
    for c in string.encode('utf-8'):
        hash_val ^= c
        hash_val = (hash_val * iv) & 0xFFFFFFFFFFFFFFFF
    return hash_val & mask

def fnv1a_bo3(string, hash_val, iv, mask):
    hash_val = fnv1a(string, hash_val, iv, mask)
    hash_val = (hash_val * iv) & 0xFFFFFFFFFFFFFFFF
    return hash_val & mask

def fnv1a_sec(string, sec_string, hash_val, iv, mask):
    if len(string) < 1:
        return fnv1a(string, hash_val, iv, mask)
    modified_string = string[0] + sec_string + string[1:]
    return fnv1a(modified_string, hash_val, iv, mask)

def fnv1a_sec_suffix(string, sec_string, hash_val, iv, mask):
    modified_string = string + sec_string
    return fnv1a(modified_string, hash_val, iv, mask)

def hash_bo4cw_scr(string):
    hash_val = 0x4B9ACE2F
    for c in string.encode('utf-8'):
        temp = (c + hash_val) ^ ((c + hash_val) << 10)
        hash_val = temp + (temp >> 6)
    return (0x8001 * ((9 * hash_val) ^ ((9 * hash_val) >> 11))) & 0xFFFFFFFF

# Wrapper functions per game variant
def base_fnv1a_63(string):
    return fnv1a(string.lower(), 0xCBF29CE484222325, 0x100000001B3, 0x7FFFFFFFFFFFFFFF)

def base_fnv1a_64(string):
    return fnv1a(string.lower(), 0xCBF29CE484222325, 0x100000001B3, 0xFFFFFFFFFFFFFFFF)

def base_fnv1a_32(string):
    return fnv1a(string.lower(), 0x811C9DC5, 0x1000193, 0xFFFFFFFF)

def iw_resources(string):
    return fnv1a(string.lower(), 0x47F5817A5EF961BA, 0x100000001B3, 0x7FFFFFFFFFFFFFFF)

def mwii_iii_scr(string):
    return fnv1a(string.lower(), 0x79D6530B0BB9B5D1, 0x10000000233, 0x7FFFFFFFFFFFFFFF)

def black_ops_3_scr(string):
    return fnv1a_bo3(string.lower(), 0x4B9ACE2F, 0x1000193, 0xFFFFFFFF)

def iw_dvars(string):
    return fnv1a_sec(string.lower(), "q6n-+7=tyytg94_*", 0xD86A3B09566EBAAC, 0x10000000233, 0xFFFFFFFFFFFFFFFF)

def black_ops_6_scr(string):
    return fnv1a_sec(string.lower(), "zt@f3yp(d[kkd=_@", 0x1C2F2E3C8A257D07, 0x10000000233, 0xFFFFFFFFFFFFFFFF)

def black_ops_6_omnvars(string):
    return fnv1a_sec(string.lower(), "gvbs9*vpm@mh@krh", 0xCBF28CE593123345, 0x100000002C1, 0xFFFFFFFFFFFFFFFF)

def black_ops_6_sp_scr(string):
    return fnv1a_sec_suffix(string.lower(), "zt@f3yp(d[kkd=_@", 0x1C2F2E3C8A257D07, 0x10000000233, 0xFFFFFFFFFFFFFFFF)
