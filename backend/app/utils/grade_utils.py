from enum import Enum

class GradeTrend(str, Enum):
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"

def calculate_percentage(points_earned: float, points_possible: float) -> float:
    if points_possible <= 0:
        return 0.0
    return round((points_earned / points_possible) * 100, 2)

def calculate_letter_grade(percentage: float) -> str:
    if percentage >= 97: return "A+"
    elif percentage >= 93: return "A"
    elif percentage >= 90: return "A-"
    elif percentage >= 87: return "B+"
    elif percentage >= 83: return "B"
    elif percentage >= 80: return "B-"
    elif percentage >= 77: return "C+"
    elif percentage >= 73: return "C"
    elif percentage >= 70: return "C-"
    elif percentage >= 67: return "D+"
    elif percentage >= 63: return "D"
    elif percentage >= 60: return "D-"
    return "F"

def calculate_grade_points(letter_grade: str) -> float:
    mapping = {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "D-": 0.7,
        "F": 0.0
    }
    return mapping.get(letter_grade, 0.0)
