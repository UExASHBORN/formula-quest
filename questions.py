import json
from pathlib import Path
import random

class QuestionBank:
    def __init__(self, json_path=None):
        if json_path is None:
            json_path = Path(__file__).parent / "data" / "formulas.json"
        self.json_path = Path(json_path)
        self.formulas = []
        self.load_data()

    def load_data(self):
        if not self.json_path.exists():
            raise FileNotFoundError(f"Formula data file not found at {self.json_path}")
        
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.formulas = data.get("formulas", [])
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in {self.json_path}: {e}")
        
        self._validate_formulas()

    def _validate_formulas(self):
        required_keys = [
            "id", "topic", "name", "notation", "explanation",
            "example_question", "correct_answer", "worked_solution",
            "mcq_options", "hint", "accepted_answers"
        ]
        for idx, formula in enumerate(self.formulas):
            for key in required_keys:
                if key not in formula:
                    raise ValueError(f"Formula at index {idx} missing required key: '{key}'")
            if "weight" not in formula:
                # Assign higher weights automatically to high-yield competitive exam items (squares, cubes, factorials)
                topic = formula.get("topic", "")
                if "Squares" in topic or "Cubes" in topic or "Factorials" in topic:
                    formula["weight"] = 3
                else:
                    formula["weight"] = 1

    def get_all_formulas(self):
        return self.formulas

    def get_topics(self):
        """Returns a unique list of topics and their starting indices for table-of-contents navigation."""
        topics = {}
        for idx, f in enumerate(self.formulas):
            t = f["topic"]
            if t not in topics:
                topics[t] = idx
        return topics

    def get_randomized_practice_questions(self, count=50):
        """Generates a randomized stream using the weight matrix so high-yield items appear more often."""
        weights = [f.get("weight", 1) for f in self.formulas]
        return random.choices(self.formulas, weights=weights, k=min(count, len(self.formulas) * 3))

    def get_practice_questions(self):
        return self.get_randomized_practice_questions()

    def get_recall_questions(self):
        return self.get_randomized_practice_questions()