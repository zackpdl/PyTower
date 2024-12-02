import json
import os

class SaveManager:
    SAVE_FILE = "save_data.json"
    
    @staticmethod
    def save_game(qi_pills, spirit_stones):
        data = {
            "qi_pills": qi_pills,
            "spirit_stones": spirit_stones
        }
        with open(SaveManager.SAVE_FILE, "w") as f:
            json.dump(data, f)
    
    @staticmethod
    def load_game():
        if not os.path.exists(SaveManager.SAVE_FILE):
            return {"qi_pills": 500, "spirit_stones": 0}
        try:
            with open(SaveManager.SAVE_FILE, "r") as f:
                return json.load(f)
        except:
            return {"qi_pills": 500, "spirit_stones": 0}
