# TryHackMe - W1seGuy

![W1seGuy Logo](https://tryhackme-images.s3.amazonaws.com/room-icons/9a13d8dcbd8940d14352ba2edbf66735.png)

## Room Info
- **Difficulty:** Easy
- **Category:** Cryptography
- **Link:** [https://tryhackme.com/room/w1seguy](https://tryhackme.com/room/w1seguy)

## Challenge Overview

This challenge involves decrypting a simple XOR cipher using a known-plaintext-attack brute-force method.

## Task 1 - Source Code Analysis

```python
def setup(server, key):
    flag = 'THM{thisisafakeflag}'  # Known plaintext
    xored = ""
    for i in range(0,len(flag)):
        xored += chr(ord(flag[i]) ^ ord(key[i%len(key)]))
    return xored.encode().hex()

def start(server):
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    hex_encoded = setup(server, key)
    send_message(server, f"This XOR encoded text has flag 1: {hex_encoded}\n")
```

### Analysis
- It choses a **5** digit key from **alphanumeric characters**
- It encrypts and returns a flag(the flag on the attack machine will be different) using an **XOR operation**

## Task 2 - Attack

We connect to port 1337 of the attack machine using netcat. We are given a 40-byte XOR encoded text string and asked for the key.
Since the plain text is known, all possibilities for the key are tried, byte by byte, and the key digits corresponding to the known bytes are identified.

Because the XOR operation is reversible, if the ciphertext is XORed again with the same key, the plaintext will be revealed. In other words:

`C = P ⊕ K`

`P = C ⊕ K`

This can be solved using CyberChef (From Hex + XOR Brute Force).

For this, I wrote a simple Python script that takes a hex input, XORs it, and finds the key that produces the desired result.

```python
chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

def bruteforce():
    encrypted = input("encrypted hex: ")
    decrypted = input("decrypted text: ")
    for i, d in enumerate(decrypted):
        for k in chars:
            if d == chr(int(encrypted[2*i:2*i+2], 16) ^ ord(k)):
                print(k, i)
```

*I used brute force because the key length is short and performance isn't critical, but the key can be calculated at the bit level if necessary.*

With the help of this script, the first flag is obtained, and the second flag is obtained by sending the key.
