from config import Config
from participant import Participant
from shamir import Shamir_secret

from binascii import hexlify
#from Crypto.Cipher import AES
#from Crypto.Random import get_random_bytes
#from Cryptodome.Protocol.SecretSharing import Shamir
#key = "😊   '    j3j"
key = ".,forv1)"
secret1=Shamir_secret(5, 3, key)

#key = get_random_bytes(16)

#shares = Shamir.split(2, 5, key)
#for piece in shares:
#    print(piece)
#for idx, share in shares:
#    print "Index #%d: %s" % (idx, hexlify(share))

#with open("clear.txt", "rb") as fi, open("enc.txt", "wb") as fo:
#    cipher = AES.new(key, AES.MODE_EAX)
#    ct, tag = cipher.encrypt(fi.read()), cipher.digest()
#    fo.write(cipher.nonce + tag + ct)
