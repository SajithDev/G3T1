import random
from math import gcd

# ===========================
# Helper Functions
# ===========================

def egcd(a, b):
    if a == 0:
        return b, 0, 1
    g, y, x = egcd(b % a, a)
    return g, x - (b // a) * y, y


def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("No modular inverse")
    return x % m


def is_prime(n, k=5):
    """Miller-Rabin primality test"""
    if n <= 1:
        return False
    if n <= 3:
        return True

    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for i in range(k):
        a = random.randint(2, n - 2)
        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for i in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(bits=512):
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1
        if is_prime(p):
            return p


# ===========================
# Universal Input Parser
# ===========================

def parse_input(data):
    """
    Accepts:
    - bytes → returns as-is
    - str → detects:
        • hex string (e.g. '48656c6c6f')
        • normal string (e.g. 'hello')
    """
    if isinstance(data, bytes):
        return data

    if isinstance(data, str):
        data = data.strip()

        # Detect hex
        if len(data) % 2 == 0 and all(c in "0123456789abcdefABCDEF" for c in data):
            try:
                return bytes.fromhex(data)
            except:
                pass

        # Otherwise treat as normal string
        return data.encode()

    raise TypeError("Unsupported input type")


# ===========================
# Key Generation
# ===========================

def generate_keys(bits=1024):
    p = generate_prime(bits // 2)
    q = generate_prime(bits // 2)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    while gcd(e, phi) != 1:
        e = random.randrange(2, phi)

    d = modinv(e, phi)

    return (e, n), (d, n)


# ===========================
# Core RSA Operations
# ===========================

def encrypt_int(m, public_key):
    e, n = public_key
    return pow(m, e, n)


def decrypt_int(c, private_key):
    d, n = private_key
    return pow(c, d, n)


def sign_int(m, private_key):
    d, n = private_key
    return pow(m, d, n)


def verify_int(s, public_key):
    e, n = public_key
    return pow(s, e, n)


# ===========================
# Byte Conversion Wrappers
# ===========================

def bytes_to_int(data: bytes):
    return int.from_bytes(data, 'big')


def int_to_bytes(value: int):
    return value.to_bytes((value.bit_length() + 7) // 8, 'big')


# ===========================
# Confidentiality
# ===========================

def encrypt_bytes(data, public_key):
    data = parse_input(data)

    m = bytes_to_int(data)
    e, n = public_key

    if m >= n:
        raise ValueError("Message too large for modulus")

    c = encrypt_int(m, public_key)
    return int_to_bytes(c)


def decrypt_bytes(cipher: bytes, private_key):
    c = bytes_to_int(cipher)
    m = decrypt_int(c, private_key)
    return int_to_bytes(m)


# ===========================
# Integrity/Authentication
# ===========================

def sign_bytes(data, private_key):
    data = parse_input(data)

    m = bytes_to_int(data)
    s = sign_int(m, private_key)
    return int_to_bytes(s)


def verify_bytes(signature: bytes, public_key):
    s = bytes_to_int(signature)
    m = verify_int(s, public_key)
    return int_to_bytes(m)


# ===========================
# Confidentiality + Integrity
# ===========================

def encrypt_and_sign(data, sender_private_key, receiver_public_key):
    data = parse_input(data)

    m = bytes_to_int(data)

    d_sender, n = sender_private_key
    e_receiver, n2 = receiver_public_key

    if n != n2:
        raise ValueError("This simplified version requires same modulus n")

    if m >= n:
        raise ValueError("Message too large")

    # Step 1: Sign
    signed = pow(m, d_sender, n)

    # Step 2: Encrypt
    cipher = pow(signed, e_receiver, n)

    return int_to_bytes(cipher)


def decrypt_and_verify(cipher: bytes, receiver_private_key, sender_public_key):
    c = bytes_to_int(cipher)

    d_receiver, n = receiver_private_key
    e_sender, n2 = sender_public_key

    if n != n2:
        raise ValueError("This simplified version requires same modulus n")

    # Step 1: Decrypt
    signed = pow(c, d_receiver, n)

    # Step 2: Verify
    m = pow(signed, e_sender, n)

    return int_to_bytes(m)


# ===========================
# Chunking (for large data)
# ===========================

def encrypt_large(data, public_key):
    data = parse_input(data)

    e, n = public_key
    chunk_size = (n.bit_length() // 8) - 1

    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        chunks.append(encrypt_bytes(chunk, public_key))

    return chunks


def decrypt_large(chunks, private_key):
    result = b""
    for chunk in chunks:
        result += decrypt_bytes(chunk, private_key)
    return result


# ===========================
# Example (Midterm)
# ===========================

if __name__ == "__main__":
    # Andy
    andy_public = (29, 323)
    andy_private = (149, 323)

    # Mia
    mia_public = (79, 323)
    mia_private = (175, 323)

    message_blocks = [6, 14, 14, 3] 

    print("\nOriginal input:", message_blocks)

    print("=== ENCRYPTION (Andy → Mia) ===")
    encrypted_blocks = []

    for m in message_blocks:
        # Step 1: sign with Andy's private key
        step1 = pow(m, andy_private[0], 323)

        # Step 2: encrypt with Mia's public key
        step2 = pow(step1, mia_public[0], 323)

        print(f"({m:02d}^{andy_private[0]} mod 323)^{mia_public[0]} mod 323 = {step2:03d}")
        encrypted_blocks.append(step2)

    print("Encrypted output:", encrypted_blocks)

    print("\n=== DECRYPTION (Mia → Verify Andy) ===")
    decrypted_blocks = []

    for c in encrypted_blocks:
        # Step 1: decrypt with Mia's private key
        step1 = pow(c, mia_private[0], 323)

        # Step 2: verify with Andy's public key
        step2 = pow(step1, andy_public[0], 323)

        print(f"({c:03d}^{mia_private[0]} mod 323)^{andy_public[0]} mod 323 = {step2:02d}")
        decrypted_blocks.append(step2)

    print("\nDecrypted output:", decrypted_blocks)
