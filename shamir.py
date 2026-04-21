import random
from math import ceil
from decimal import Decimal
import base64
import datetime

FIELD_SIZE = 10**5


def string_to_integers(input_raw: str, bytes_per_integer: int) -> list:
    """
    Converts any string to a list of (large) integers. This process
    can be inverted by integer_list_to_string() -function
    """
    raw_bytes = input_raw.encode('utf-8')
    byte_length = len(raw_bytes)
    result = [byte_length]
    for i in range(0, byte_length, bytes_per_integer):
        chunk = raw_bytes[i:i + bytes_per_integer]
        chunk = chunk.ljust(bytes_per_integer, b'\x00')  # pad last chunk if needed
        result.append(int.from_bytes(chunk, byteorder='big'))
    return result

def integer_list_to_string(input_list: list, bytes_per_integer: int) -> str:
    """
    Inverts a list of integers created with string_to_integers() back
    to a single string
    """
    byte_length = input_list[0]
    all_bytes = bytearray()
    for integer in input_list[1:]:
        all_bytes.extend(integer.to_bytes(bytes_per_integer, byteorder='big'))
    return bytes(all_bytes[:byte_length]).decode('utf-8')

#class ParticipantData:
#    def __init__(self) -> None:
#        self.data: list = []
#        self.index: int = 0
#
#    def __iter__(self) -> dict:
#        if self.data:
#            self.index = 0
#            return self.data[0]
#        raise StopIteration
#
#    def __next__(self) -> list:
#        if self.index + 1 < len(self.data):
#            self.index += 1
#            return self.data[self.index]
#        raise StopIteration()
#
#    def add_participant(self, data: dict) -> None:
#        self.data.append(data)
#
#    def clear_data(self) -> None:
#        self.data = []


class ShamirSecret:
    """
    Class for one secret encoding & decoding

    Original secret_raw can be a string of any format for it's tarnsformed:
    """

    def __init__(self, shares: int = 5, treshold: int = 3):
        """
            Holds exactly one passphrase
            create_secret:
             1. Breaks the passphrase to large integers in plain_text_codes:
                    [byte_length, int1, int2, int3, ...]
             2. Plain_text_codes[1:] are then encrypted by create_shares 
                in secret_matrix:
                   [
                    [int_P_1_1, int_P_2_1, int_P_3_1, ...]  # secrets set 1
                    [int_P_1_2, int_P_2_2, int_P_3,2, ...]  # secrets set 2
                    [int_P_1_3, int_P_2_3, int_P_3_3, ...]  # secrets set 3
                    ....
                #   particip1,  particip2, particip3, ---
                   ] 
             3. Each secret holder should now be handed all keys in vertical
                axis of this matrix
        """
        self.treshold = treshold
        self.shares = shares
        self.plain_text_codes: list = []
        self.secret_matrix: list = []
        self.byte_length: int = 0
        self.creation_date = datetime.datetime(1800, 1, 1)
        self.participant_data = []
        

        #self._decode_bits_secret()
        #self.integer_list = string_to_integers(secret_raw, 10)
        #print(self.integer_list)
        #temp_returned_string = int in plain_text_codeseger_list_to_string(self.integer_list, 10)
        #print(temp_returned_string)
        #exit()Plain_text_codes is

    def create_secret(self, secret_raw: str)->None:
        print(secret_raw)
        self.plain_text_codes = string_to_integers(secret_raw, 18)
        self.byte_length = self.plain_text_codes[0]
        self.creation_date = datetime.datetime.now()
        self.participant_data = []
        for plaintext_integer in self.plain_text_codes[1:]:
            self.secret_matrix.append(
                self.generate_shares(
                    self.shares,
                    self.treshold,
                    plaintext_integer))
        #    print(self.secret_matrix[-1])
        # print()

        self.secret_matrix=[
            [101, 201, 301, 401],
            [102, 202, 302, 402],
            [103, 203, 303, 403],
            [104, 204, 304, 404],
            [105, 205, 305, 405],
        ]

        for line in self.secret_matrix:
            print(line)

        for secret_ind, secret in enumerate(self.secret_matrix[0]):
            single_participant_data: dict = {
                "byte_length": self.byte_length,
                "creation_date": self.creation_date,
                "keys": [],
            }
            for participant_ind, secret_list in enumerate(self.secret_matrix):
                single_participant_data["keys"].append(
                    self.secret_matrix[participant_ind][secret_ind]
                )
            print(single_participant_data["keys"])

    def iterate_participants(self) -> dict:
        """
        Iterator that returns participants' datas after 
        a secret has been created.
        """
        index = -1
        while index + 1 < len(self.participant_data):
            index += 1
            yield self.participant_data[index]

    def reconstruct_secret(self, shares: list) -> int:
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
        for coefficient_index, coefficient_value in enumerate(
            coefficients[::-1]
        ):
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


    def generate_shares(self, n_shares, m, secret) -> list:
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

