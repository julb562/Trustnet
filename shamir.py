import random
from math import ceil
from decimal import Decimal
import base64

FIELD_SIZE = 10**5

#HEX_CHARS=[
#    "\x00","\x01","\x02","\x03","\x04",
#    "\x05","\x06","\x07","\x08","\x09","A","B","C","D","E","F"]
HEX_CHARS=[
    "0", "1", "2", "3", "4", 
    "5", "6", "7", "8", "9", 
    "A", "B", "C", "D", "E", "F"]
HEX_CHAR_CODES={
    '30': 0, "31": 1, "32": 2,  "33": 3,  "34": 4,  "35": 5,  "36": 6,  "37": 7, 
    "38": 8, "39": 9, "41": 10, "42": 11, "43": 12, "44": 13, "45": 14, "46": 15
}


def string_to_integers(input_raw: str, bytes_per_integer: int )->list:
    return_list=[]

    print(f"{input_raw} len {len(input_raw)}")
    input_encoded = input_raw.encode('utf-8')
    #print(input_encoded)
    input_base16 = base64.b16encode(input_encoded)
    print(input_base16)

    multiplier=1
    byte=0
    value=0
    for hex in input_base16:
        value += HEX_CHARS.index(chr(hex)) * 16 ** byte
        print(f" -{HEX_CHARS.index(chr(hex))}-", end="")
        byte += 1
        print(f"\n{value}", end="")
        if byte >=bytes_per_integer:
            return_list.append(value)
            byte = 0
            value = 0
            multiplier = 1
    if value != 0:
        return_list.append(value)
        print(f"\n{value}")
    print()


    #print("\n")
    output_list=return_list

    output_base16=""
    for value in output_list:
        for byte in range(0, bytes_per_integer):
            print(f"\n{value}", end="")
            print(f" -{value % 16}-", end="")
            output_base16 += HEX_CHARS[value % 16]
            value -= value % 16
            value = int(value / 16)
    print(f"\n{output_base16}")


    output_un_base16d = base64.b16decode(output_base16)
    #print(output_un_base16d)
    output_decoded=output_un_base16d.decode('utf-8')
    while output_decoded[-1]=="\x00":
        output_decoded = output_decoded[0:-1]
    print(f"\n{output_decoded} len {len(output_decoded)}")
    
    for integers in return_list:
        print(integers)

    exit()

    return return_list

class Shamir_secret:
    """
    Class for one secret encoding & decoding

    Original secret_raw can be a string of any format for it's tarnsformed:
    """

    def __init__(self, shares: int = 5, treshold: int = 3, secret_raw: str = ""):
        # (3,5) sharing scheme
        self.treshold = treshold
        self.shares = shares
        self.secret_raw=secret_raw
        #self.secret_raw="Aaäa"

        self._encode_raw_secret()
        self._decode_bits_secret()
        secret = 123491872398792638776152387
        print(f'Original Secret: {secret}')
    
        # Phase I: Generation of shares
        shares = self.generate_shares(self.shares, self.treshold, secret)
        print(f'Shares: {", ".join(str(share) for share in shares)}')
    
        # Phase II: Secret Reconstruction
        # Picking self.treshold shares randomly for
        # reconstruction
        pool = random.sample(shares, self.treshold)
        print(f'Combining shares: {", ".join(str(share) for share in pool)}')
        print(f'Reconstructed secret: {self.reconstruct_secret(pool)}')

    def _encode_raw_secret(self)->bool:
        """
        1. base16 encoded => secret_base16
        2. Split into parts of X bytes
        xxxxxxxxx
        10^25
        """

        self.secret=string_to_integers(self.secret_raw, 16)
        print("\n\n")

    def _decode_bits_secret(self)->bool:
        """
        """
        #print(integer_list_to_hex_byte_string(self.secret[0:1], 20))
#        self.raw_secret=""
#        print("\nDecoding:")
#        for part in self.secret:
#            print(f"Base16: '{part}'")
#            part_byte_array=base64.b16decode(part)
#            print(f"Byte_array: '{part_byte_array}'")
#            part_clear=bytes(part_byte_array).decode("utf-8")
#            print(f"Clear: '{part_clear}'")
#            self.raw_secret+=part_clear
#        print(f"Final clear text: '{self.secret_raw}'")
#        print("\n\n")

    def reconstruct_secret(self, shares):
        """
        Combines individual shares (points on graph)
        using Lagranges interpolation.

        `shares` is a list of points (x, y) belonging to a
        polynomial with a constant of our key.
        """
        sums = 0
        prod_arr = []

        for j, share_j in enumerate(shares):
            xj, yj = share_j
            prod = Decimal(1)

            for i, share_i in enumerate(shares):
                xi, _ = share_i
                if i != j:
                    prod *= Decimal(Decimal(xi)/(xi-xj))

            prod *= yj
            sums += Decimal(prod)

        return int(round(Decimal(sums), 0))


    def polynom(self, x, coefficients):
        """
        This generates a single point on the graph of given polynomial
        in `x`. The polynomial is given by the list of `coefficients`.
        """
        point = 0
        # Loop through reversed list, so that indices from enumerate match the
        # actual coefficient indices
        for coefficient_index, coefficient_value in enumerate(coefficients[::-1]):
            point += x ** coefficient_index * coefficient_value
        return point


    def coeff(self, treshold, secret):
        """
        Randomly generate a list of coefficients for a polynomial with
        degree of `treshold` - 1, whose constant is `secret`.

        For example with a 3rd degree coefficient like this:
            3x^3 + 4x^2 + 18x + 554

            554 is the secret, and the polynomial degree + 1 is 
            how many points are needed to recover this secret. 
            (in this case it's 4 points).
        """
        coeff = [random.randrange(0, FIELD_SIZE) for _ in range(treshold - 1)]
        coeff.append(secret)
        return coeff


    def generate_shares(self, n_shares, m, secret):
        """
        Split given `secret` into `n_shares` shares with minimum threshold
        of `m` shares to recover this `secret`, using SSS algorithm.
        """
        coefficients = self.coeff(m, secret)
        shares = []

        for i in range(1, n_shares+1):
            x = random.randrange(1, FIELD_SIZE)
            shares.append((x, self.polynom(x, coefficients)))

        return shares

