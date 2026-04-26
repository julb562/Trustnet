import configparser
from participant import Participants
from keystore import KeyStore
from shamir import ShamirSecret

CONFIG_FILE_NAME = "default_config.ini"

class Data:

    def __init__(self):
        self.participants = Participants()
        self.key_store = KeyStore()
        self.config = configparser.ConfigParser()

    def load_all(self):
        self.config.sections()
        self.config.read(CONFIG_FILE_NAME)

        self.participants.load_all(
            self.config["local_settings"]["participant_file"]
        )

        self.key_store.load_all(
            self.config["local_settings"]["key_store_file"]
        )

    def save_all(self):
        self.participants.save_all(
            self.config["local_settings"]["participant_file"]
        )
        self.key_store.save_all(
            self.config["local_settings"]["key_store_file"]
        )
        with open(CONFIG_FILE_NAME, 'w', encoding="utf8") as configfile:
            self.config.write(configfile)

    def create_secret(self, secret: str, shares: int, treshold: int) -> list:
        participant_data: list = []
        with ShamirSecret("Tester", "localhost", shares, treshold) as secret1:
            secret1.create_secret(secret)
            for single_participant_data in secret1.iterate_participants():
                participant_data.append(single_participant_data)
        return participant_data


    def decrypt_secret(self, participant_data: list, shares: int, treshold: int) -> str:
        with ShamirSecret("Tester", "localhost", shares, treshold) as secret2:
            # pylint: disable=bare-except;
            for single_data in participant_data:
                secret2.populate_decoder(single_data)
            try:
                result = secret2.decode()
            except:
                return ""
        return result
