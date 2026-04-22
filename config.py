from pathlib import Path

class Config:
    def __init__(self, path: str="./", filename: str="config.ini"):
        self.config_file = "./my_config.ini"
        self.values: dict = {}

    def load_config(self)->(bool, str):
        """
        Loads all configurations. Path & file must be defined before calling
        this.

        Returns:    (True, "Ok") if loading succeeded
                    (False, error_text) if any error in loading the file
        """
        print(f"Opening config file {self.config_file}")
        with open(self.config_file, "r", encoding="utf-8") as config_file:
            self.values = config_file.read()
            config_file.close()
        return (True, "Ok")

    def save_config(self)->(bool, str):
        """
        Saves all current configurations. Path & file must be defined before 
        calling this.

        Returns:    (True, "Ok") if saving succeeded
                    (False, error_text) if any error in saving the file
        """
        with open(self.config_file, "w", encoding="utf-8") as config_file:
            config_file.write(self.values)
            config_file.close()
        return (True, "Ok")
