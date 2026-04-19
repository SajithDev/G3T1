def vigenere_encrypt(plaintext, key):
    result = []
    key = key.lower()
    key_index = 0

    for char in plaintext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('a')

            if char.islower():
                encrypted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
            else:
                encrypted_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))

            result.append(encrypted_char)
            key_index += 1
        else:
            result.append(char)

    return ''.join(result)


def vigenere_decrypt(ciphertext, key):
    result = []
    key = key.lower()
    key_index = 0

    for char in ciphertext:
        if char.isalpha():
            shift = ord(key[key_index % len(key)]) - ord('a')

            if char.islower():
                decrypted_char = chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
            else:
                decrypted_char = chr((ord(char) - ord('A') - shift) % 26 + ord('A'))

            result.append(decrypted_char)
            key_index += 1
        else:
            result.append(char)

    return ''.join(result)