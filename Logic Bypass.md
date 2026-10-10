\# KPMG CTF 2026 — Logic Bypass Write-up



Solved · 10 points



We solved the challenge by reverse-engineering the ELF binary and decoding the flag directly, rather than guessing a password or exploiting a memory corruption bug.



\## 1. Challenge overview



\- Challenge: Logic Bypass

\- Category: Reverse engineering / binary analysis

\- Goal: Obtain the flag in `KPMG\_CTF{...}` format.

\- File: `challenge` — a 64-bit Linux ELF executable.



\## 2. What we did



Step 1 — Identified the binary



We ran:



bash

```

file challenge

```



The output confirmed it was a dynamically linked, 64-bit ELF executable for Linux. It was also not stripped, meaning its internal function names were preserved.



Step 2 — Examined the strings



bash

```

strings challenge

```



This revealed useful symbols and clues, including:



\- `validate\_password`

\- `transform\_password`

\- `decode\_flag`

\- `FLAG\_KEY`

\- `ENC\_FLAG`



These names suggested that the executable contained its own password validation and flag-decoding logic.



Step 3 — Disassembled the program



We used:



bash

```

objdump -d -M intel challenge

nm -n challenge

```



The disassembly showed that `validate\_password` checked a transformed password against an expected 16-byte value and also performed a hash-based comparison.



We also found that `decode\_flag` used a repeating XOR key to decrypt the embedded flag.



Step 4 — Extracted the embedded data



We ran:



bash

```

objdump -s -j .rodata challenge

```



This exposed the relevant data in the read-only data section:



\- `FLAG\_KEY` at `0x402020`

\- `ENC\_FLAG` at `0x402040`



The key was:



text

```

5a 17 c0 de 13 37 42 69

```



Step 5 — Decoded the flag



The decryption routine XORed each ciphertext byte with a repeating key byte:



$$

P\_i=C\_i\\oplus K\_{i\\bmod 8}

$$



Here, $P\_i$ is the plaintext byte, $C\_i$ is the encrypted byte, and $K$ is the eight-byte key.



We applied this operation to the 54 encrypted bytes and recovered the flag.



Step 6 — Submitted the flag



We submitted the decoded string to the CTF platform, and the submission was accepted.



\## 3. Final flag



Accepted answer



KPMG\\\_CTF{pcoJI0Oaqg1oyNglEm0sTI7tt06H6y5NzsgdrM1WK3ia}



&#x20;Copy flag



\## 4. What we learned



| Technique | What it taught us |

| --- | --- |

| `file` | Identify executable formats and architecture. |

| `strings` | Find useful text and function names inside binaries. |

| `nm` | Locate functions and symbols. |

| `objdump -d` | Understand program control flow and validation logic. |

| `objdump -s -j .rodata` | Extract embedded constants and encrypted data. |

| XOR decryption | Recover plaintext using a repeating key. |



The key lesson: Don't assume a CTF challenge must be solved through its intended input field. Sometimes the executable itself reveals a simpler route. In this case, rather than reverse-engineering the full password transformation to generate a valid key, we found the embedded flag and reversed its XOR encryption directly.



One final security note: repeating-key XOR is reversible obfuscation, not strong encryption. Embedding both the ciphertext and the key in the same executable makes the flag recoverable through static analysis.

