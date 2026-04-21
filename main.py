from config import Config
from participant import Participant
from shamir import ShamirSecret


bad_strings = open("../big-list-of-naughty-strings/blns.txt", "r")
line: int = 0

for key in bad_strings:
    line += 1

    participant_data = []

    with ShamirSecret("Tester", "localhost", 6, 3) as secret1:
        secret1.create_secret(key)
        for single_participant_data in secret1.iterate_participants():
            #print(single_participant_data)
            participant_data.append(single_participant_data)

    with ShamirSecret("Tester", "localhost", 6, 3) as secret2:
        secret2.populate_decoder(participant_data[1])
        secret2.populate_decoder(participant_data[2])
        secret2.populate_decoder(participant_data[2])
        secret2.populate_decoder(participant_data[2])
        secret2.populate_decoder(participant_data[0])
        result = secret2.decode()

    if result != key:
        print(f"\n Line {line} failed")
    else: print(".", end="")
print(f"\n{line} lines went ok")
    

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
