BLOCK_SIZE = 16
Nr = 10 # Number of rounds for AES-128

class AES128:
    S_BOX = [
        0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
        0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
        0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
        0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
        0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
        0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
        0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
        0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
        0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
        0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
        0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
        0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
        0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
        0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
        0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
        0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16,
    ]

    INV_S_BOX = [0] * 256
    for i, v in enumerate(S_BOX):
        INV_S_BOX[v] = i

    RCON = [0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]

    def __init__(self, key):
        if not isinstance(key, (bytes, bytearray)):
            raise TypeError("Key must be bytes")

        if len(key) != 16:
            raise ValueError("AES-128 key must be 16 bytes")
        
        # Precompute round keys
        self.round_keys = self._expand_key(key)

    # ----------- STATE CONVERSIONS -----------
    # Converts 16-byte block → 4x4 column-major matrix
    def _block_to_state(self, block):
        state = []
        for c in range(4):
            column = []
            for r in range(4):
                column.append(block[r + 4 * c])
            state.append(column)
        return state

    # Converts state matrix back → bytes
    def _state_to_block(self, state):
        output = []
        for c in range(4):
            for r in range(4):
                output.append(state[c][r])
        return bytes(output)

    # ----------- HELPERS -----------

    def _xor_bytes(self, a, b):
        return bytes(x ^ y for x, y in zip(a, b))

    # Multiply by 2 in GF(2^8)
    def _xtime(self, value):
        value <<= 1
        if value & 0x100:  # overflow past 8 bits
            value ^= 0x1B
        return value & 0xFF

    # Split data into 16-byte blocks
    def _split_blocks(self, data):
        return [data[i:i+BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]

    # ----------- AES TRANSFORMS -----------
    def SubBytes(self, s):
        for c in range(4):
            for r in range(4):
                s[c][r] = self.S_BOX[s[c][r]]

    def InvSubBytes(self, s):
        for c in range(4):
            for r in range(4):
                s[c][r] = self.INV_S_BOX[s[c][r]]

    def ShiftRows(self, s):
        # Rotate each row left by row index
        for r in range(4):
            row = [s[c][r] for c in range(4)]
            row = row[r:] + row[:r]
            for c in range(4):
                s[c][r] = row[c]

    def InvShiftRows(self, s):
        for r in range(4):
            row = [s[c][r] for c in range(4)]
            row = row[-r:] + row[:-r]
            for c in range(4):
                s[c][r] = row[c]

    def AddRoundKey(self, s, k):
        # XOR state with round key
        for c in range(4):
            for r in range(4):
                s[c][r] ^= k[c][r]

    def MixColumns(self, s):
        for c in range(4):
            a = s[c]
            t = a[0] ^ a[1] ^ a[2] ^ a[3]
            u = a[0]
            s[c][0] ^= t ^ self._xtime(a[0] ^ a[1])
            s[c][1] ^= t ^ self._xtime(a[1] ^ a[2])
            s[c][2] ^= t ^ self._xtime(a[2] ^ a[3])
            s[c][3] ^= t ^ self._xtime(a[3] ^ u)

    def InvMixColumns(self, s):
        for c in range(4):
            a = s[c]
            u = self._xtime(self._xtime(a[0] ^ a[2]))
            v = self._xtime(self._xtime(a[1] ^ a[3]))
            s[c][0] ^= u
            s[c][1] ^= v
            s[c][2] ^= u
            s[c][3] ^= v
        self.MixColumns(s)

    # ----------- KEY EXPANSION -----------
    def _expand_key(self, key):
        columns = self._block_to_state(key)
        i = 1

        while len(columns) < 44: # AES-128 needs 44 words
            word = list(columns[-1])

            if len(columns) % 4 == 0:
                word = word[1:] + word[:1]
                word = [self.S_BOX[b] for b in word]
                word[0] ^= self.RCON[i]
                i += 1

            word = self._xor_bytes(word, columns[-4])
            columns.append(list(word))

        return [columns[4*i:4*(i+1)] for i in range(Nr + 1)]

    # ----------- BLOCK CIPHER -----------
    def _encrypt_block(self, block):
        state = self._block_to_state(block)

        self.AddRoundKey(state, self.round_keys[0])

        for rnd in range(1, Nr):
            self.SubBytes(state)
            self.ShiftRows(state)
            self.MixColumns(state)
            self.AddRoundKey(state, self.round_keys[rnd])

        self.SubBytes(state)
        self.ShiftRows(state)
        self.AddRoundKey(state, self.round_keys[Nr])

        return self._state_to_block(state)

    def _decrypt_block(self, block):
        state = self._block_to_state(block)

        self.AddRoundKey(state, self.round_keys[Nr])

        for rnd in range(Nr - 1, 0, -1):
            self.InvShiftRows(state)
            self.InvSubBytes(state)
            self.AddRoundKey(state, self.round_keys[rnd])
            self.InvMixColumns(state)

        self.InvShiftRows(state)
        self.InvSubBytes(state)
        self.AddRoundKey(state, self.round_keys[0])

        return self._state_to_block(state)

    # ----------- PADDING -----------
    def _pad(self, data):
        pad_len = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
        return data + bytes([pad_len] * pad_len)

    def _unpad(self, data):
        if not data or len(data) % BLOCK_SIZE != 0:
            raise ValueError("Invalid padded data length")

        pad_len = data[-1]
        if pad_len < 1 or pad_len > BLOCK_SIZE:
            raise ValueError("Invalid padding")

        if data[-pad_len:] != bytes([pad_len] * pad_len):
            raise ValueError("Invalid padding")

        return data[:-pad_len]

    # ----------- API wrapper for GUI -----------
    def encrypt(self, plaintext: bytes) -> bytes:
        if not isinstance(plaintext, (bytes, bytearray)):
            raise TypeError("Plaintext must be bytes")

        if len(plaintext) == 0:
          return b""

        padded = self._pad(plaintext)
        ciphertext = b''.join(
            self._encrypt_block(b) for b in self._split_blocks(padded)
        )
        return ciphertext


    def decrypt(self, ciphertext: bytes) -> bytes:
        if not isinstance(ciphertext, (bytes, bytearray)):
            raise TypeError("Ciphertext must be bytes")

        if len(ciphertext) == 0:
            return b""

        if len(ciphertext) % BLOCK_SIZE != 0:
            raise ValueError("Invalid ciphertext length")

        plaintext = b''.join(
            self._decrypt_block(b) for b in self._split_blocks(ciphertext)
        )
        return self._unpad(plaintext)
