\# KPMG CTF Writeup — Golden Hour



\*\*Category:\*\* OSINT / Git Forensics / Steganography  

\*\*Challenge:\*\* Golden Hour  

\*\*Points:\*\* 30  

\*\*Objective:\*\* Recover the hidden flag by investigating the challenge author's online footprint, unlocking a browser-based vault, and analyzing the downloaded image.



\## 1. Challenge Description



The challenge provides the following description:



> I never delete, I just stop pointing. Everything I walked away from is still out there, and the one thing worth keeping, I locked. The key's already yours.



The challenge website directs the user to a personal portfolio and journal, with a vault containing a locked item.



\*\*Challenge URL:\*\*  

https://kicyber-a0d9510e941b-goldenhour-0-0.chals.io/#journal



The wording suggests investigating abandoned content, deleted references, and historical versions of online resources rather than relying solely on the current website.



\## 2. Initial Reconnaissance



The website belonged to a fictional creator named Nova Keller, who described making small games and photographing golden-hour coastal scenery.



The journal contained two useful clues:



\- The creator had changed their name while keeping their work publicly available.

\- Selected photographs were kept in a vault rather than posted publicly.



The website linked to the creator's GitHub profile:



https://github.com/nova-drifts



Several repositories were available, including `driftlog` and `config-archive`.



The challenge description's reference to things that are no longer pointed to suggested examining old commits, deleted files, and archived content.



\## 3. Investigating the GitHub Repositories



The `config-archive` repository contained an `old.env` file with the following flag:



`KPMG\_CTF{n0va\_dr1fted\_h0m3}`



Initially, this looked like a potential solution. However, the surrounding text explicitly explained that the flag had been planted to catch scrapers and was not the actual solution.



This was an intentional decoy.



\*\*Lesson:\*\* A flag-shaped string is not necessarily the correct flag. Always examine its context and verify it against the challenge.



The investigation then continued through the creator's online footprint and historical content associated with the `driftlog` repository.



\## 4. Recovering the Vault Passphrase



A deleted LinkedIn post was recovered through the investigation of historical content.



The post's comments contained encoded strings, including:



\*\*Base64 string 1\*\*



`eTB1IDRyMyA0bG0wNTcgN2gzcjM=`



Decoding it from Base64 produced:



`y0u 4r3 4lm057 7h3r3`



Interpreting the leetspeak gave:



\*\*"you are almost there"\*\*



\*\*Base64 string 2\*\*



`bjA3IDdoNDcgMzQ1eXl5`



This produced another leetspeak message:



`n07 7h47 345yyy`



The comments also contained two Base32-encoded strings:



\- `MRZGSZTUO5XW6ZA=` → `driftwood`

\- `O5ZG63THNZXXIZI=` → `wrongnote`



The accompanying comment suggested that the author sometimes left notes in their own comments.



The word \*\*`driftwood`\*\* was the correct vault passphrase.



Entering it into the vault unlocked the next stage.



\## 5. Downloading the Image



After the passphrase was accepted, the vault provided a full-resolution JPEG image named:



`golden-hour.jpg`



The image showed Peggy's Point Lighthouse, also known as Peggy's Cove Lighthouse, in Peggy's Cove, Nova Scotia, Canada.



At this point, identifying the location was useful contextual information, but the downloaded file still needed to be investigated for additional clues.



Since the image was available locally, the next step was to inspect its metadata.



\## 6. Analyzing the JPEG Metadata



The initial attempt to use ExifTool failed because it was not installed or available in the Windows PATH.



Instead of installing another utility, Python and Pillow were used to inspect the image.



First, Pillow was installed if necessary:



```powershell

python -m pip install Pillow

```



The following command displayed the image dimensions, EXIF metadata, and embedded information:



```powershell

python -c "from PIL import Image; im=Image.open('golden-hour.jpg'); print('Dimensions:',im.size); print('EXIF:',im.getexif()); print('Metadata:',im.info)"

```



The command reported:



```text

Dimensions: (1280, 640)
EXIF: {296: 2, 282: 72.0, 531: 1, 34665: 90, 283: 72.0}
Metadata: {'exif': b'Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x05\x01\x1a\x00\x05\x00\x00\x00\x01\x00\x00\x00J\x01\x1b\x00\x05\x00\x00\x00\x01\x00\x00\x00R\x01(\x00\x03\x00\x00\x00\x01\x00\x02\x00\x00\x02\x13\x00\x03\x00\x00\x00\x01\x00\x01\x00\x00\x87i\x00\x04\x00\x00\x00\x01\x00\x00\x00Z\x00\x00\x00\x00\x00\x00\x00H\x00\x00\x00\x01\x00\x00\x00H\x00\x00\x00\x01\x00\x05\x90\x00\x00\x07\x00\x00\x00\x040232\x91\x01\x00\x07\x00\x00\x00\x04\x01\x02\x03\x00\x92\x86\x00\x07\x00\x00\x00#\x00\x00\x00\x9c\xa0\x00\x00\x07\x00\x00\x00\x040100\xa0\x01\x00\x03\x00\x00\x00\x01\xff\xff\x00\x00\x00\x00\x00\x00ASCII\x00\x00\x00KPMG_CTF{n0va_dr1ft3d_h0m3}\x00', 'dpi': (72.0, 72.0)}

```



The EXIF output contained several numeric metadata fields. More importantly, the embedded EXIF data included an ASCII string containing:



`KPMG\_CTF{n0va\_dr1ft3d\_h0m3}`



This was the actual flag recovered from the JPEG metadata.



\### Why the decoy was easy to miss



The flag embedded in the image was visually similar to the decoy found in `old.env`, but the strings differed:



\*\*Decoy — `old.env`\*\*



`KPMG\_CTF{n0va\_dr1fted\_h0m3}`



\*\*Actual flag — JPEG EXIF\*\*



`KPMG\_CTF{n0va\_dr1ft3d\_h0m3}`



The critical difference is in `drifted`:



\- Decoy: `dr1fted`

\- Actual flag: `dr1ft3d`



The actual flag uses the digit \*\*`3`\*\* in place of the letter \*\*`e`\*\* in the final part of the word.



This small difference is why copying the first flag without checking the later evidence would have resulted in an incorrect submission.



\## 7. Final Flag



The flag recovered from the image's EXIF metadata was:



`KPMG\_CTF{n0va\_dr1ft3d\_h0m3}`



\## 8. Key Takeaways



This challenge combined several investigation techniques:



1\. \*\*OSINT:\*\* Examining the creator's website, GitHub repositories, and historical online content.

2\. \*\*Git forensics:\*\* Following clues about abandoned or deleted content rather than relying only on current repository files.

3\. \*\*Encoding analysis:\*\* Decoding Base64 and Base32 strings and interpreting leetspeak.

4\. \*\*Passphrase recovery:\*\* Using the decoded word `driftwood` to unlock the vault.

5\. \*\*File forensics:\*\* Inspecting a downloaded JPEG's EXIF metadata with Python and Pillow.

6\. \*\*Decoy recognition:\*\* Comparing similar flag strings character by character instead of assuming the first discovered flag was correct.



\## Conclusion



The Golden Hour challenge rewarded following the evidence across multiple sources. The initial GitHub flag was deliberately misleading, while encoded LinkedIn comments revealed the passphrase needed to unlock the vault. The downloaded JPEG then contained the actual flag in its EXIF metadata.



The decisive step was examining the original image file rather than relying only on what it displayed.



\*\*Final flag:\*\* `KPMG\_CTF{n0va\_dr1ft3d\_h0m3}`

