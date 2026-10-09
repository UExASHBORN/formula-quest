import json
from pathlib import Path

class ProgressTracker:
    def __init__(self, progress_path=None):
        if progress_path is None:
            progress_path = Path(__file__).parent / "data" / "progress.json"
        self.progress_path = Path(progress_path)
        self.data = self._default_data()
        self.load()

    def _default_data(self):
        return {
            "total_attempted": 0,
            "correct_answers": 0,
            "incorrect_formulas": []
        }

    def load(self):
        if not self.progress_path.exists():
            self.data = self._default_data()
            self.save()
            return

        try:
            with open(self.progress_path, "r", encoding="utf-8") as f:
                content = json.load(f)
                self.data["total_attempted"] = content.get("total_attempted", 0)
                self.data["correct_answers"] = content.get("correct_answers", 0)
                self.data["incorrect_formulas"] = content.get("incorrect_formulas", [])
        except (json.JSONDecodeError, IOError):
            self.data = self._default_data()
            self.save()

    def save(self):
        try:
            self.progress_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.progress_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
        except IOError as e:
            print(f"Error saving progress: {e}")

    def record_attempt(self, formula_id, is_correct):
        self.data["total_attempted"] += 1
        if is_correct:
            self.data["correct_answers"] += 1
            if formula_id in self.data["incorrect_formulas"]:
                self.data["incorrect_formulas"].remove(formula_id)
        else:
            if formula_id not in self.data["incorrect_formulas"]:
                self.data["incorrect_formulas"].append(formula_id)
        self.save()

    def get_accuracy(self):
        total = self.data["total_attempted"]
        if total == 0:
            return 0.0
        return (self.data["correct_answers"] / total) * 100.0

    def get_stats(self):
        return {
            "total_attempted": self.data["total_attempted"],
            "correct_answers": self.data["correct_answers"],
            "accuracy": self.get_accuracy(),
            "incorrect_count": len(self.data["incorrect_formulas"])
        }

    def get_incorrect_formulas(self):
        return self.data["incorrect_formulas"]