from backend.abstract_classes import IntentRecognition
from hassil import Intents, Recognize
from pathlib import Path

class HassilService(IntentRecognition):
    def __init__(self):
        """
        Load supported intents. hassil has multiple different options, ie. from_files, from_yaml, from_dict. from_yaml is used for simplicity for starter. In that case all intents are defined in the same YAML file.
        """
        
        filepath = Path("/backend/hassil/src/intent/fi.yaml")
        with open(filepath, 'r', encoding='utf-8') as f:
            self.intents = Intents.from_yaml(f)
        


    def recognize_intent(self, text: str, _lang: str) -> dict:
        """
        Uses recognize() to return first match. recognize() has a bunch of optional params which could be used to fine tune the process.
        
        Discards most contents of a RecognizeResult and returns only the essential information.
        
        text: Text to recognize.
        """
        
        result = Recognize.recognize(text, self.intents)

        return {"intent": result.intent, "data": result.intent_data}
  