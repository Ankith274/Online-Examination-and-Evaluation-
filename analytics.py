import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from models import Result, ProctoringLog, User

class PerformancePredictor:
    def __init__(self):
        # We start with basic feature weights, but this can be trained on past data.
        self.model = RandomForestClassifier(n_estimators=100)

    def predict_risk(self, result_id):
        """
        Predicts if a student is "At Risk" based on current exam performance 
        and proctoring violations.
        Returns prediction (True/False) and confidence (%)
        """
        # Fetching data for the current result
        result = Result.query.get(result_id)
        if not result:
            return False, 0.0
            
        logs = ProctoringLog.query.filter_by(result_id=result.id).all()
        violation_count = len(logs)
        score_perc = (result.score / result.total_marks) if result.total_marks > 0 else 0
        
        # Heuristic/ML model prediction
        # A simple model could use [score_perc, violation_count] as features.
        # For now, we use a weighted risk score logic.
        risk_score = (1.0 - score_perc) * 0.7 + (violation_count * 0.1)
        
        is_at_risk = True if risk_score > 0.5 else False
        confidence = min(1.0, risk_score) * 100
        
        return is_at_risk, confidence

# Example usage (standalone test)
if __name__ == "__main__":
    # This would normally be used inside the web app context.
    pass
