import secrets
from math import ceil
import base64
import datetime
from uuid import uuid4

# 12th Mersenne prime — larger than any 8-byte (64-bit) secret integer
PRIME = 2**127 - 1


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


class ShamirSecret:
    """
    Class for one secret encoding & decoding

    Original secret_raw can be a string of any format for it's tarnsformed:
    """

    def __init__(
        self,
        name: str,
        owner: str,
        shares: int = 5,
        treshold: int = 3,
    ):
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
        self.ready_to_decode = False
        self.treshold = treshold
        self.shares = shares
        self.name = name
        self.owner = owner
        self.uuid = str(uuid4())
        self.secret_matrix: list = []
        self.creation_date = datetime.datetime(1800, 1, 1)
        self.decoding_participants_keys: list = []
        self.bytes_per_integer: int = 8 # Growing this may brake decoding

    def create_secret(self, secret_raw: str)->None:
        plain_text_codes: list = string_to_integers(
            secret_raw,
            self.bytes_per_integer
        )
        self.creation_date = str(datetime.datetime.now())
        for plaintext_integer in plain_text_codes:
            self.secret_matrix.append(
                self.generate_shares(
                    self.shares,
                    self.treshold,
                    plaintext_integer))
        self.ready_to_decode = True

    def iterate_participants(self) -> dict:
        """
        Iterator that returns participants' datas as a dict
        after a secret has been created.
        """

        # Create the key data per participant
        participant_data = []
        for secret_ind, secret in enumerate(self.secret_matrix[0]):
            single_participant_data: list = []
            for participant_ind, secret_list in enumerate(self.secret_matrix):
                single_participant_data.append(
                    self.secret_matrix[participant_ind][secret_ind]
                )
            participant_data.append(single_participant_data)

        # Iterate over the created data
        index = -1
        while index + 1 < len(participant_data):
            index += 1
            yield {
                "keys": participant_data[index],
                "creation_date": self.creation_date,
                "owner": self.owner,
                "name": self.name,
                "uuid": self.uuid,
                "treshold": self.treshold,
                "shares": self.shares
            }

    def populate_decoder(self, participant_data: dict) -> int:
        """
        Takes a participant data dict as input.

        If secret_matrix has values, tests other data to match
        the given essentials and fail if it doesn't

        if secret_matrix empty, populates all settings from 
        given participant data
        
        last tries to add key data to secret_matrix -list if it
        differs from existing data.

        Returns negative integer of participants key required 
        after this operation to decode the secret in all cases
        """
        failed = False
        if self.decoding_participants_keys:
            # Some data in secret_matrix. Check the newly given
            # matches that
            if self.creation_date != participant_data["creation_date"]:
                failed = True
            if self.uuid != participant_data["uuid"]:
                failed = True
            if self.name != participant_data["name"]:
                failed = True
            if self.shares != participant_data["shares"]:
                failed = True
            if self.treshold != participant_data["treshold"]:
                failed = True

        if participant_data["keys"] in self.decoding_participants_keys:
            failed = True

        if failed:
            return 0 - self.treshold + len(self.decoding_participants_keys)

        self.decoding_participants_keys.append(participant_data["keys"])
        self.creation_date = participant_data["creation_date"]
        self.owner = participant_data["owner"]
        self.name = participant_data["name"]
        self.uuid = participant_data["uuid"]
        self.treshold = participant_data["treshold"]
        self.shares = participant_data["shares"]
        shares_needed = (
            0 - self.treshold + len(self.decoding_participants_keys)
        )
        if shares_needed >= 0:
            self.ready_to_decode = True
        return shares_needed

    def decode(self) -> str:
        if not self.ready_to_decode:
            return ""
        decrypted_ints: list = []
        for key_ind, temp in enumerate(self.decoding_participants_keys[0]):
            this_parts_encrypted_ints: list = []
            for line in self.decoding_participants_keys:
                this_parts_encrypted_ints.append(line[key_ind])
            decrypted_ints.append(self.reconstruct_secret(this_parts_encrypted_ints))
        return integer_list_to_string(decrypted_ints, self.bytes_per_integer)

    def reconstruct_secret(self, shares: list) -> int:
        """
        Combines individual shares (points on graph)
        using Lagrange interpolation in GF(PRIME).

        `shares` is a list of points (x, y) belonging to a
        polynomial with a constant of our key.
        """
        sums = 0
        for j, share_j in enumerate(shares):
            xj, yj = share_j
            num = 1
            den = 1
            for i, share_i in enumerate(shares):
                xi, _ = share_i
                if i != j:
                    num = (num * (-xi)) % PRIME
                    den = (den * (xj - xi)) % PRIME
            lagrange = (num * pow(den, -1, PRIME)) % PRIME
            sums = (sums + yj * lagrange) % PRIME
        return sums


    def polynom(self, x, coefficients):
        """
        This generates a single point on the graph of given polynomial
        in `x`. The polynomial is given by the list of `coefficients`.
        All arithmetic is done in GF(PRIME).
        """
        point = 0
        for coefficient_index, coefficient_value in enumerate(
            coefficients[::-1]
        ):
            point = (point + pow(x, coefficient_index, PRIME) * coefficient_value) % PRIME
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
        coeff = [secrets.randbelow(PRIME) for _ in range(treshold - 1)]
        coeff.append(secret)
        return coeff


    def generate_shares(self, n_shares, m, secret) -> list:
        """
        Split given `secret` into `n_shares` shares with minimum threshold
        of `m` shares to recover this `secret`, using SSS algorithm.
        """
        coefficients = self.coeff(m, secret)
        shares = []
        x_values: set = set()

        while len(shares) < n_shares:
            x = secrets.randbelow(PRIME - 1) + 1  # x in [1, PRIME-1]
            if x in x_values:
                continue
            x_values.add(x)
            shares.append((x, self.polynom(x, coefficients)))

        return shares

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.secret_matrix: list = []
        self.decoding_participants_keys: list = []
        self.__init__("","")

    def __enter__(self):
        return self
