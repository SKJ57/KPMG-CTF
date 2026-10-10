KPMG CTF 2026 — Logic Bypass Write-up

Category: Reverse Engineering
Challenge: Logic Bypass
Points: 10
Status: Solved ✅

1. Challenge Overview

The challenge provided an executable named challenge, along with the following description:

A secret is protected by a local check. Your goal is to make the binary approve access.

The objective was to understand the binary's validation logic and obtain the flag.

Instead of guessing passwords or attempting a memory corruption exploit, I analyzed the executable and discovered that the flag was embedded in the binary in an XOR-obfuscated form.

2. Identifying the Binary

First, I checked the file type:

file challenge


Output:

ELF 64-bit LSB executable, x86-64,
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
not stripped


This confirmed that the file was a 64-bit Linux ELF executable.

The binary was not stripped, meaning that many internal function and variable names were preserved. This made static analysis easier.

Note: If you're using Windows Git Bash, the file and objdump commands may work through an installed GNU toolchain, but the Linux executable itself may need WSL or a Linux environment to run.
3. Extracting Strings

Next, I searched for readable strings inside the binary:

strings challenge


Some interesting results were:

LOGIC BYPASS // AUTH
A secret is protected by a local check.
Your goal is to make the binary approve access.
Enter access key:
[ACCESS DENIED]
[ACCESS GRANTED]
Flag: %s


The binary also contained these internal symbols:

transform_password
fnv1a32
weird_mix
looks_reasonable
secondary_decoy
validate_password
decode_flag
FLAG_KEY
ENC_FLAG
analysis_noise


These names provided useful clues about the program's implementation.

In particular, validate_password appeared to handle access validation, while decode_flag, FLAG_KEY, and ENC_FLAG suggested that the flag could be decoded locally.

4. Examining the Symbols and Disassembly

I listed the binary's symbols:

nm -n challenge


Then I generated an Intel-syntax disassembly:

objdump -d -M intel challenge > disasm.txt


This allowed me to inspect the internal functions and follow the program's control flow.

Password validation

The validate_password function performed several checks:

It called looks_reasonable to check the input's length and character types.
It passed the input to transform_password.
It calculated a hash using fnv1a32 and passed the result through weird_mix.
It compared the transformed password with an expected 16-byte value.
It checked the hash-related result against 0x46b31fef.

The function secondary_decoy also affected an analysis_noise variable, but its result was not directly used in the final acceptance comparison.

This was consistent with the challenge's hint that the decision was based on logic rather than a memory corruption bug.

However, I did not need to recover the valid password because the binary contained another route to the flag.

5. Inspecting the Read-Only Data Section

I dumped the .rodata section:

objdump -s -j .rodata challenge


This section contained the data associated with the embedded flag.

The important addresses were:

Symbol	Address	Purpose
FLAG_KEY	0x402020	XOR key
ENC_FLAG	0x402040	Encrypted flag
table.1	0x4021c0	Transformation lookup table
expected.0	0x4021d0	Expected transformed password

The XOR key was stored as eight bytes:

5a 17 c0 de 13 37 42 69


In hexadecimal notation, the corresponding key bytes were:

key = bytes.fromhex("5a17c0de13374269")


The encrypted flag began at address 0x402040.

6. Understanding the Flag Decoder

The disassembly of decode_flag revealed the following operation:

for (i = 0; i < 54; i++) {
    output[i] = ENC_FLAG[i] ^ FLAG_KEY[i & 7];
}
output[54] = '\0';


The expression:

i & 7


selects one of the eight key bytes, repeating the key every eight bytes.

Because the XOR operation is reversible, applying the same key to the encrypted bytes recovers the original plaintext.

Mathematically:

𝑃
𝑖
=
𝐶
𝑖
⊕
𝐾
𝑖
 
mod
 
8

Where:

𝑃
𝑖
 is the plaintext byte.
𝐶
𝑖
 is the ciphertext byte.
𝐾
𝑖
 is the key byte.
⊕
 represents bitwise XOR.

The binary contained both the ciphertext and the key, so I could reproduce this operation without satisfying the password validation checks.

7. Decoding the Flag with Python

I recreated the decoder in Python:

key = bytes.fromhex("5a17c0de13374269")

ciphertext = bytes.fromhex(
    "11478d994c74162f"
    "2167a3b1597e7226"
    "3b66a7ef7c4e0c0e"
    "3652adee60630b5e"
    "2e63f0e85b013b5c"
    "146db3b977450f58"
    "0d5cf3b7724a"
)

flag = bytes(
    byte ^ key[i % len(key)]
    for i, byte in enumerate(ciphertext)
)

print(flag.decode())


Output:

KPMG_CTF{pcoJI0Oaqg1oyNglEm0sTI7tt06H6y5NzsgdrM1WK3ia}

8. Final Flag

Flag:

KPMG_CTF{pcoJI0Oaqg1oyNglEm0sTI7tt06H6y5NzsgdrM1WK3ia}


I submitted the decoded flag to the CTF platform, and it was accepted.

9. Key Takeaways

This challenge provided useful practice in static binary analysis and reverse engineering.

Techniques used:

file — identifying the executable format.
strings — finding useful text and symbol names.
nm — listing functions and symbols.
objdump -d — inspecting assembly and control flow.
objdump -s -j .rodata — extracting embedded constants.
Python — reproducing the XOR decoder.
Lessons learned
Always identify the binary format before analyzing it.
Preserved symbols can reveal the purpose of internal functions.
Follow the actual validation logic instead of relying on function names alone.
Inspect read-only data sections for embedded constants and encoded information.
Repeating-key XOR is reversible obfuscation, not secure encryption, especially when the key is stored in the same executable.
Conclusion

The challenge was solved through static analysis of the ELF binary. By identifying the flag decoder, extracting the XOR key and encrypted bytes, and reproducing the decoding algorithm in Python, I recovered the flag without needing to discover a valid access key.

Tools used: GNU file, strings, nm, objdump, and Python 3.