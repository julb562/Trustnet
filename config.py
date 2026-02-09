class Config:
    def __init__(self, path: str="", filename: str="config.ini"):
        self.path = path
        self.filename = filename
        parameter = {}

    def load_config(self)->(bool, str):
        """
        Loads all configurations. Path & file must be defined before calling
        this.

        Returns:    (True, "Ok") if loading succeeded
                    (False, error_text) if any error in loading the file
        """
        Return (True, "Ok")

    def save_config(self)->(bool, str):
        """
        Saves all current configurations. Path & file must be defined before 
        calling this.

        Returns:    (True, "Ok") if saving succeeded
                    (False, error_text) if any error in saving the file
        """
        Return (True, "Ok")
