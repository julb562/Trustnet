from config import Config
from participant import Participants
from keystore import KeyStore
from shamir import ShamirSecret
import configparser
import click

CONFIG_FILE_NAME = "default_config.ini"


def load_all():
    config = configparser.ConfigParser()
    config.sections()
    config.read(CONFIG_FILE_NAME)

    participants = Participants()
    participants.load_all(
        config["local_settings"]["participant_file"]
    )

    key_store = KeyStore()
    key_store.load_all(
        config["local_settings"]["key_store_file"]
    )

def save_all():
    participants.save_all(config["local_settings"]["participant_file"])
    key_store.save_all(config["local_settings"]["key_store_file"])
    with open(CONFIG_FILE_NAME, 'w', encoding="utf8") as configfile:
        config.write(configfile)


def create_secret(secret: str) -> None:
    participant_data: list = []
    # TODO: Get shares and treshold from real life
    shares = 6
    treshold = 3
    with ShamirSecret("Tester", "localhost", shares, treshold) as secret1:
        secret1.create_secret(secret)
        for single_participant_data in secret1.iterate_participants():
            participant_data.append(single_participant_data)
    # TODO: Spread the keys to participants

def decrypt_secret(name_of_secret: str) -> str:
    # TODO: Get participant keys from network
    participant_data = [ 12, 12, 12, 12]
    # TODO: Get shares and treshold from real life    
    shares = 6
    treshold = 3
    with ShamirSecret("Tester", "localhost", shares, treshold) as secret2:
        secret2.populate_decoder(participant_data[1])
        secret2.populate_decoder(participant_data[4])
        secret2.populate_decoder(participant_data[0])
        try:
            result = secret2.decode()
        except:
            return ""
    return result

def request_secret(name: str) -> str:
    return ""


