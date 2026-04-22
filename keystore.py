import json

class KeyStore:
    def __init__(self):
        self.secret_list: list = []

    def load_all(self, file_name: str) -> None:
        self.secret_list: list = []
        with open(file_name, "r") as save_file:
            self.secret_list = json.load(save_file)

    def save_all(self, file_name: str) -> None:    
        save_dump = json.dumps(self.secret_list)
        with open(file_name, "w") as save_file:
            save_file.write(save_dump)
        save_file.close()
