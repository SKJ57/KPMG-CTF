#!/usr/bin/env python3
"""Decode the flag for the KPMG CTF 2026 'Logic Bypass' challenge."""

KEY = bytes.fromhex("5a17c0de13374269")
CIPHERTEXT = bytes.fromhex(
    "11478d994c74162f"
    "2167a3b1597e7226"
    "3b66a7ef7c4e0c0e"
    "3652adee60630b5e"
    "2e63f0e85b013b5c"
    "146db3b977450f58"
    "0d5cf3b7724a"
)


def decode_flag(ciphertext: bytes, key: bytes) -> str:
    """Decode bytes encrypted with repeating-key XOR."""
    if not key:
        raise ValueError("Key must not be empty")
    plaintext = bytes(byte ^ key[i % len(key)] for i, byte in enumerate(ciphertext))
    return plaintext.decode("utf-8")


if __name__ == "__main__":
    print(decode_flag(CIPHERTEXT, KEY))
