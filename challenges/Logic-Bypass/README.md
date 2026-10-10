# Logic Bypass

**CTF:** KPMG CTF 2026  
**Category:** Reverse Engineering  
**Points:** 10  
**Status:** Solved  
**Target:** `challenge` — 64-bit Linux ELF executable

## Challenge

The challenge asks us to analyze the program's logic and recover the flag. The prompt references following the mountain elf's instructions to reach the hilltop and secure the flag.

The useful route is static analysis: the executable contains an XOR-obfuscated flag and the key needed to decode it.

> **Flag:** `KPMG_CTF{pcoJI0Oaqg1oyNglEm0sTI7tt06H6y5NzsgdrM1WK3ia}`

## 1. Identify the executable

```bash
file challenge
```

The target is a 64-bit x86-64 Linux ELF executable. It is **not stripped**, so useful function and symbol names remain available.

## 2. Search for useful strings

```bash
strings challenge
```

Interesting strings include:

```text
LOGIC BYPASS // AUTH
A secret is protected by a local check.
Your goal is to make the binary approve access.
Enter access key:
[ACCESS DENIED]
[ACCESS GRANTED]
Flag: %s
```

Useful symbols include `transform_password`, `fnv1a32`, `weird_mix`, `looks_reasonable`, `secondary_decoy`, `validate_password`, `decode_flag`, `FLAG_KEY`, `ENC_FLAG`, and `analysis_noise`.

These suggest two paths: password validation and flag decoding. The decoder is the more direct route to the flag.

## 3. Inspect symbols and disassembly

```bash
nm -n challenge
objdump -d -M intel challenge > disasm.txt
```

The `validate_password` function checks the input format, transforms the password, computes a hash, and compares results with embedded constants. A decoy function also updates `analysis_noise`, but that value does not determine the final acceptance comparison.

Recovering the accepted password is unnecessary because the flag can be decoded directly from data stored in the executable.

## 4. Locate the key and ciphertext

```bash
objdump -s -j .rodata challenge
```

Relevant symbols:

| Symbol | Address | Purpose |
|---|---:|---|
| `FLAG_KEY` | `0x402020` | XOR key |
| `ENC_FLAG` | `0x402040` | Encrypted flag |
| `table.1` | `0x4021c0` | Transformation lookup table |
| `expected.0` | `0x4021d0` | Expected transformed password |

The key bytes are:

```text
5a 17 c0 de 13 37 42 69
```

```python
key = bytes.fromhex("5a17c0de13374269")
```

## 5. Understand the decoder

The `decode_flag` function applies repeating-key XOR to 54 bytes:

```c
for (i = 0; i < 54; i++) {
    output[i] = ENC_FLAG[i] ^ FLAG_KEY[i & 7];
}
output[54] = '\0';
```

`i & 7` selects an index from `0` to `7`, making the eight-byte key repeat. XORing the ciphertext with the same key bytes recovers the plaintext:

`plaintext[i] = ciphertext[i] XOR key[i % len(key)]`

## 6. Decode the flag

The included [`solve.py`](solve.py) script reproduces the decoder with Python 3:

```bash
python3 solve.py
```

Expected output:

```text
KPMG_CTF{pcoJI0Oaqg1oyNglEm0sTI7tt06H6y5NzsgdrM1WK3ia}
```

## 7. Result

The flag was recovered through static analysis by identifying `decode_flag`, extracting the XOR key and ciphertext, and reproducing the decoding operation in Python. There was no need to bypass the password check at runtime.

## Tools used

- `file` — identify the executable format
- `strings` — locate readable strings
- `nm` — list symbols
- `objdump` — inspect disassembly and `.rodata`
- Python 3 — reproduce the decoder

## Takeaways

- Identify the binary format before choosing analysis tools.
- Preserved symbols can make reverse engineering easier.
- Verify what each validation function actually controls; decoy logic can distract from the real path.
- Inspect read-only data for embedded constants and encoded values.
- Repeating-key XOR is obfuscation, not strong encryption, when the key is stored alongside the ciphertext.
