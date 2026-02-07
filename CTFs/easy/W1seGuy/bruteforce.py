import string

chars = string.ascii_uppercase + string.ascii_lowercase + string.digits

def bruteforce():
    encrypted = input("encrypted hex: ")
    decrypted = input("decrypted text: ")
    for i, d in enumerate(decrypted):
        for k in chars:
            if d == chr(int(encrypted[2*i:2*i+2], 16) ^ ord(k)):
                print(k, i)

bruteforce()
