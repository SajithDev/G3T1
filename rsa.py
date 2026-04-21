# ===========================
# Internal helpers
# ===========================

def _bytes_to_int(data: bytes) -> int:
    return int.from_bytes(data, "big")


def _int_to_bytes(value: int, length=None) -> bytes:
    if length is None:
        if value == 0:
            return b"\x00"
        length = (value.bit_length() + 7) // 8
    return value.to_bytes(length, "big")


# ===========================
# Core single-block RSA
# ===========================

def _encrypt_block(block: bytes, e: int, n: int) -> bytes:
    m = _bytes_to_int(block)
    if m >= n:
        raise ValueError("Block too large for modulus")
    c = pow(m, e, n)

    # ciphertext is always full size of modulus
    k = (n.bit_length() + 7) // 8
    return _int_to_bytes(c, k)


def _decrypt_block(block: bytes, d: int, n: int) -> bytes:
    c = _bytes_to_int(block)
    m = pow(c, d, n)
    return _int_to_bytes(m)


# ===========================
# Public API (chunked)
# ===========================

def rsa_encrypt(data: bytes, e: int, n: int) -> bytes:
    """
    Encrypt arbitrary bytes using chunking.
    Returns a single bytes object.
    """

    if n < 256:
        raise ValueError(f"Invalid RSA modulus: n must be at least 256, got {n}. Use a larger n.")

    k = (n.bit_length() + 7) // 8      # modulus size in bytes
    chunk_size = k - 1                 # must be < n

    output = bytearray()

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]

        # store original chunk length (2 bytes)
        output += len(chunk).to_bytes(2, "big")

        encrypted = _encrypt_block(chunk, e, n)
        output += encrypted

    return bytes(output)


def rsa_decrypt(cipher: bytes, d: int, n: int) -> bytes:
    """
    Decrypt chunked ciphertext back into original bytes.
    """

    if n < 256:
        raise ValueError(f"Invalid RSA modulus: n must be at least 256, got {n}. Use a larger n.")
    
    k = (n.bit_length() + 7) // 8

    i = 0
    output = bytearray()

    while i < len(cipher):
        # read original length
        chunk_len = int.from_bytes(cipher[i:i+2], "big")
        i += 2

        block = cipher[i:i+k]
        i += k

        decrypted = _decrypt_block(block, d, n)

        # trim back to original size
        output += decrypted[-chunk_len:]

    return bytes(output)