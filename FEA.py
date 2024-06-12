import random

# Define S-boxes (8 S-boxes, each mapping 16 bits to 8 bits)
S_BOXES = [
    [random.randint(0, 255) for _ in range(65536)] for _ in range(8)
]

# Predefined expansion permutation (example)
EXPANSION_PERMUTATION = [i for i in range(64)] * 2

# Predefined permutation (example)
PERMUTATION = [random.randint(0, 127) for _ in range(128)]

# Round constants (example)
ROUND_CONSTANTS = [random.randint(0, 0xFFFFFFFF) for _ in range(16)]

def rotate_left(word, bits):
    return ((word << bits) & 0xFFFFFFFF) | (word >> (32 - bits))

def subkey_generation(key):
    subkeys = []
    key_words = [int.from_bytes(key[i:i+4], byteorder='big') for i in range(0, len(key), 4)]
    for i in range(16):
        round_key = []
        for j in range(8):
            rotated_word = rotate_left(key_words[j], i)
            round_key.append(rotated_word ^ ROUND_CONSTANTS[i])
        # Combine the 8 subkey words into a single 256-bit integer
        subkey = 0
        for word in round_key:
            subkey = (subkey << 32) | word
        subkeys.append(subkey)
    return subkeys

def expand_block(block):
    expanded_block = 0
    for i in range(128):
        bit = (block >> i) & 1
        expanded_block |= (bit << EXPANSION_PERMUTATION[i])
    return expanded_block

def permute_block(block):
    permuted_block = 0
    for i in range(128):
        bit = (block >> i) & 1
        permuted_block |= (bit << PERMUTATION[i])
    return permuted_block

def s_box_substitution(block):
    substituted_block = 0
    for i in range(8):
        chunk = (block >> (i * 16)) & 0xFFFF
        substituted_block |= (S_BOXES[i][chunk] << (i * 8))
    return substituted_block

def round_function(right_half, subkey):
    expanded_half = expand_block(right_half)
    xor_result = expanded_half ^ subkey
    substituted_half = s_box_substitution(xor_result)
    permuted_half = permute_block(substituted_half)
    return permuted_half

def feistel_round(left_half, right_half, subkey):
    new_left_half = right_half
    new_right_half = left_half ^ round_function(right_half, subkey)
    return new_left_half, new_right_half

def encrypt_block(block, key):
    left_half = (block >> 64) & 0xFFFFFFFFFFFFFFFF
    right_half = block & 0xFFFFFFFFFFFFFFFF
    subkeys = subkey_generation(key)
    
    for i in range(16):
        left_half, right_half = feistel_round(left_half, right_half, subkeys[i])
    
    encrypted_block = (left_half << 64) | right_half
    return encrypted_block

def decrypt_block(block, key):
    left_half = (block >> 64) & 0xFFFFFFFFFFFFFFFF
    right_half = block & 0xFFFFFFFFFFFFFFFF
    subkeys = subkey_generation(key)
    
    for i in range(15, -1, -1):
        right_half, left_half = feistel_round(right_half, left_half, subkeys[i])
    
    decrypted_block = (left_half << 64) | right_half
    return decrypted_block

# part 3 of the question
key = b'\x00' * 32  # 256-bit key (32 bytes)
plaintext_block = int.from_bytes(b'\x00' * 16, byteorder='big')  # 128-bit block (16 bytes)

encrypted_block = encrypt_block(plaintext_block, key)
print(f"Encrypted Block: {encrypted_block:032x}")
print(key)
decrypted_block = decrypt_block(encrypted_block, key)
print(f"Decrypted Block: {decrypted_block:032x}")
