from config import Config
from participant import Participant
from shamir import ShamirSecret


key = ".äforv.,sdf89ufg24fnklK.-,dfg-.,eg0942ieg,"
secret1=ShamirSecret(5, 3)
secret1.create_secret(key)
for participant_data in secret1.iterate_participants():
    print(participant_data)


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
