
# TABLES

# Initial Permutation Table

IP = [58, 50, 42, 34, 26, 18, 10, 2,
      60, 52, 44, 36, 28, 20, 12, 4,
      62, 54, 46, 38, 30, 22, 14, 6,
      64, 56, 48, 40, 32, 24, 16, 8,
      57, 49, 41, 33, 25, 17,  9, 1,
      59, 51, 43, 35, 27, 19, 11, 3,
      61, 53, 45, 37, 29, 21, 13, 5,
      63, 55, 47, 39, 31, 23, 15, 7]

# Final Permutation Table
FP = [40, 8, 48, 16, 56, 24, 64, 32,
      39, 7, 47, 15, 55, 23, 63, 31,
      38, 6, 46, 14, 54, 22, 62, 30,
      37, 5, 45, 13, 53, 21, 61, 29,
      36, 4, 44, 12, 52, 20, 60, 28,
      35, 3, 43, 11, 51, 19, 59, 27,
      34, 2, 42, 10, 50, 18, 58, 26,
      33, 1, 41,  9, 49, 17, 57, 25]

# Expansion Permutation Table
E = [32,  1,  2,  3,  4,  5,
      4,  5,  6,  7,  8,  9,
      8,  9, 10, 11, 12, 13,
     12, 13, 14, 15, 16, 17,
     16, 17, 18, 19, 20, 21,
     20, 21, 22, 23, 24, 25,
     24, 25, 26, 27, 28, 29,
     28, 29, 30, 31, 32,  1]

# Permutation Function Table
P = [16,  7, 20, 21, 29, 12, 28, 17,
      1, 15, 23, 26,  5, 18, 31, 10,
      2,  8, 24, 14, 32, 27,  3,  9,
     19, 13, 30,  6, 22, 11,  4, 25]

# Key Permutation Tables
PC1 = [57, 49, 41, 33, 25, 17, 9,
        1, 58, 50, 42, 34, 26, 18,
       10,  2, 59, 51, 43, 35, 27,
       19, 11,  3, 60, 52, 44, 36,
       63, 55, 47, 39, 31, 23, 15,
        7, 62, 54, 46, 38, 30, 22,
       14,  6, 61, 53, 45, 37, 29,
       21, 13,  5, 28, 20, 12,  4]

PC2 = [14, 17, 11, 24,  1,  5,
        3, 28, 15,  6, 21, 10,
       23, 19, 12,  4, 26,  8,
       16,  7, 27, 20, 13,  2,
       41, 52, 31, 37, 47, 55,
       30, 40, 51, 45, 33, 48,
       44, 49, 39, 56, 34, 53,
       46, 42, 50, 36, 29, 32]

LEFT_SHIFTS = [1, 1, 2, 2, 2, 2, 2, 2,
               1, 2, 2, 2, 2, 2, 2, 1]

# S-Boxes
S_BOX = [
    # S1
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],

    # S2
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],

    # S3
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],

    # S4
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],

    # S5
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],

    # S6
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],

    # S7
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],

    # S8
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
]


# --- Utility Functions ---

def permute(block, table, size):
    """Apply a permutation table to a block of bits."""
    result = 0
    for i, pos in enumerate(table):
        if block & (1 << (size - pos)):
            result |= (1 << (len(table) - 1 - i))
    return result


def left_rotate(val, shifts, bits):
    """Circular left shift of a value within a fixed bit width."""
    return ((val << shifts) & ((1 << bits) - 1)) | (val >> (bits - shifts))


def pad(data: bytes) -> bytes:
    """Apply PKCS#5 padding to make data a multiple of 8 bytes."""
    pad_len = 8 - (len(data) % 8)
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes) -> bytes:
    if not data:
        raise ValueError("Invalid padding")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 8:
        raise ValueError("Invalid padding")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Invalid padding")
    return data[:-pad_len]


# --- DES Class ---

class DES:
    def __init__(self, key: bytes):
        if len(key) != 8:
            raise ValueError("DES key must be 8 bytes")
        self.round_keys = self._generate_keys(int.from_bytes(key, 'big'))

    def _generate_keys(self, key):
        key = permute(key, PC1, 64)
        C = (key >> 28) & ((1 << 28) - 1)
        D = key & ((1 << 28) - 1)

        keys = []
        for shift in LEFT_SHIFTS:
            C = left_rotate(C, shift, 28)
            D = left_rotate(D, shift, 28)
            combined = (C << 28) | D
            keys.append(permute(combined, PC2, 56))
        return keys

    def _f(self, R, K):
        """The Feistel (f) function: expansion, key mixing, S-box substitution, permutation."""
        R_expanded = permute(R, E, 32)
        x = R_expanded ^ K

        output = 0
        for i in range(8):
            # Extract each 6-bit block from the 48-bit XOR result
            block = (x >> (42 - 6 * i)) & 0x3F
            # Row is formed by the outer bits (bits 1 and 6)
            row = ((block & 0x20) >> 4) | (block & 0x01)
            # Column is formed by the inner 4 bits (bits 2-5)
            col = (block >> 1) & 0x0F
            val = S_BOX[i][row][col]
            output = (output << 4) | val

        return permute(output, P, 32)

    def process_block(self, block, encrypt=True):
        """Encrypt or decrypt a single 64-bit block."""
        block = permute(block, IP, 64)
        L = (block >> 32) & 0xFFFFFFFF
        R = block & 0xFFFFFFFF

        # Use round keys forward for encryption, reversed for decryption
        keys = self.round_keys if encrypt else list(reversed(self.round_keys))

        for K in keys:
            L, R = R, L ^ self._f(R, K)

        # Note: final swap — combine as R||L (swapped)
        combined = (R << 32) | L
        return permute(combined, FP, 64)


# --- Triple DES Class ---

class TripleDES:
    def __init__(self, key1: bytes, key2: bytes, key3: bytes):
        if not (len(key1) == len(key2) == len(key3) == 8):
            raise ValueError("Each key must be 8 bytes")

        self.des1 = DES(key1)
        self.des2 = DES(key2)
        self.des3 = DES(key3)

    def _encrypt_block(self, block):
        block = self.des1.process_block(block, True)
        block = self.des2.process_block(block, False)
        block = self.des3.process_block(block, True)
        return block

    def _decrypt_block(self, block):
        block = self.des3.process_block(block, False)
        block = self.des2.process_block(block, True)
        block = self.des1.process_block(block, False)
        return block

    def encrypt(self, data: bytes) -> bytes:
        if not isinstance(data, (bytes, bytearray)):
            raise TypeError("Data must be bytes")
        
        data = pad(data)
        result = b''

        for i in range(0, len(data), 8):
            block = int.from_bytes(data[i:i+8], 'big')
            encrypted = self._encrypt_block(block)
            result += encrypted.to_bytes(8, 'big')

        return result

    def decrypt(self, data: bytes) -> bytes:
        if len(data) % 8 != 0:
            raise ValueError("Ciphertext must be multiple of 8 bytes")

        result = b''

        for i in range(0, len(data), 8):
            block = int.from_bytes(data[i:i+8], 'big')
            decrypted = self._decrypt_block(block)
            result += decrypted.to_bytes(8, 'big')

        return unpad(result)


# --- API wrapper for GUI ---

def encrypt_3des(data: bytes, key1: bytes, key2: bytes, key3: bytes) -> bytes:
    return TripleDES(key1, key2, key3).encrypt(data)


def decrypt_3des(data: bytes, key1: bytes, key2: bytes, key3: bytes) -> bytes:
    return TripleDES(key1, key2, key3).decrypt(data)

