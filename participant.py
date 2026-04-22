import json

class Participants:
    def __init__(self):
        self.participant_dict: dict = {}

    def load_all(self, file_name: str) -> None:
        self.participant_dict: dict = {}
        with open(file_name, "r") as save_file:
            self.participant_dict = json.load(save_file)

    def save_all(self, file_name: str) -> None:    
        with open(file_name, "w") as save_file:
            #save_file.write(json.dumps(participant_dict, indent=2))
            save_dict: dict = {}
            for participant in self.participant_dict:
                save_dict[participant] = self.participant_dict[participant]
            save_file.write(json.dumps(save_dict, indent=2))
        save_file.close()





    