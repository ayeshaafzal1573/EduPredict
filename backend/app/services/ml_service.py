"""
Machine Learning service for EduPredict
"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime, timedelta
from app.core.database import get_database
from app.services.student_service import StudentService
import logging
import random

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self):
        self.db = get_database()
        self.student_service = StudentService()

    async def predict_dropout_risk(self, student_id: str) -> Dict[str, Any]:
        """Predict dropout risk for a student using ML model"""
        try:
            # Get student data
            student = await self.student_service.get_student_by_id(student_id)
            if not student:
                raise ValueError("Student not found")

            # Get historical data for prediction
            features = await self._extract_features(student_id)
            
            # Simulate ML model prediction (in real implementation, this would call actual ML model)
            risk_score = await self._calculate_risk_score(features)
            risk_level = self._determine_risk_level(risk_score)
            
            # Get risk factors
            risk_factors = await self._analyze_risk_factors(features)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_level, risk_factors)

            return {
                "student_id": student_id,
                "risk_score": round(risk_score, 3),
                "risk_level": risk_level,
                "confidence": 0.89,  # Model confidence
                "factors": risk_factors,
                "recommendations": recommendations,
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error predicting dropout risk for student {student_id}: {str(e)}")
            raise

    async def predict_grades(self, student_id: str) -> Dict[str, Any]:
        """Predict grades for a student's current courses"""
        try:
            # Get student's current courses
            courses_collection = self.db.get_collection("courses")
            current_courses = await courses_collection.find(
                {"students": {"$in": [student_id]}, "is_active": True}
            ).to_list(None)

            predictions = []
            for course in current_courses:
                # Get historical performance in this course
                course_features = await self._extract_course_features(student_id, str(course["_id"]))
                
                # Predict grade (simulate ML model)
                predicted_grade = await self._predict_course_grade(course_features)
                confidence = self._calculate_prediction_confidence(course_features)
                
                predictions.append({
                    "course_id": str(course["_id"]),
                    "course_name": course.get("name", "Unknown Course"),
                    "current_grade": course_features.get("current_grade", "N/A"),
                    "predicted_grade": predicted_grade,
                    "confidence": round(confidence, 2),
                    "improvement_potential": self._calculate_improvement_potential(course_features)
                })

            return {
                "student_id": student_id,
                "predictions": predictions,
                "overall_predicted_gpa": self._calculate_predicted_gpa(predictions),
                "semester_outlook": self._generate_semester_outlook(predictions),
                "last_updated": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error predicting grades for student {student_id}: {str(e)}")
            raise

    async def _extract_features(self, student_id: str) -> Dict[str, Any]:
        """Extract features for ML model"""
        try:
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")
            
            # Get recent grades
            recent_grades = await grades_collection.find(
                {"student_id": student_id}
            ).sort("created_at", -1).limit(20).to_list(20)

            # Calculate GPA trend
            if len(recent_grades) >= 2:
                recent_gpa = np.mean([grade.get("grade_points", 0) for grade in recent_grades[:10]])
                older_gpa = np.mean([grade.get("grade_points", 0) for grade in recent_grades[10:]])
                gpa_trend = recent_gpa - older_gpa
            else:
                gpa_trend = 0
                recent_gpa = np.mean([grade.get("grade_points", 0) for grade in recent_grades]) if recent_grades else 0

            # Get attendance data
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_attendance = await attendance_collection.find({
                "student_id": student_id,
                "date": {"$gte": thirty_days_ago}
            }).to_list(None)

            attendance_rate = 0
            if recent_attendance:
                attended = sum(1 for record in recent_attendance if record.get("status") == "present")
                attendance_rate = attended / len(recent_attendance)

            # Calculate engagement score (simplified)
            engagement_score = min(1.0, (recent_gpa / 4.0) * 0.7 + attendance_rate * 0.3)

            return {
                "gpa": recent_gpa,
                "gpa_trend": gpa_trend,
                "attendance_rate": attendance_rate,
                "engagement_score": engagement_score,
                "total_courses": len(set(grade.get("course_id") for grade in recent_grades)),
                "grade_consistency": np.std([grade.get("grade_points", 0) for grade in recent_grades]) if recent_grades else 0
            }
        except Exception as e:
            logger.error(f"Error extracting features for student {student_id}: {str(e)}")
            raise

    async def _calculate_risk_score(self, features: Dict[str, Any]) -> float:
        """Calculate dropout risk score using features"""
        try:
            # Simplified risk calculation (in real implementation, this would use trained ML model)
            gpa_factor = max(0, (4.0 - features.get("gpa", 0)) / 4.0)  # Higher risk for lower GPA
            attendance_factor = max(0, (1.0 - features.get("attendance_rate", 0)))  # Higher risk for lower attendance
            trend_factor = max(0, -features.get("gpa_trend", 0))  # Higher risk for declining GPA
            engagement_factor = max(0, (1.0 - features.get("engagement_score", 0)))

            # Weighted combination
            risk_score = (
                gpa_factor * 0.4 +
                attendance_factor * 0.3 +
                trend_factor * 0.2 +
                engagement_factor * 0.1
            )

            return min(1.0, risk_score)
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 0.5  # Default moderate risk

    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score"""
        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.6:
            return "medium"
        else:
            return "high"

    async def _analyze_risk_factors(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze individual risk factors"""
        factors = []

        # Academic Performance
        gpa = features.get("gpa", 0)
        if gpa >= 3.5:
            factors.append({
                "name": "Academic Performance",
                "impact": "positive",
                "score": min(1.0, gpa / 4.0),
                "description": "Strong academic performance"
            })
        elif gpa >= 2.5:
            factors.append({
                "name": "Academic Performance",
                "impact": "neutral",
                "score": gpa / 4.0,
                "description": "Average academic performance"
            })
        else:
            factors.append({
                "name": "Academic Performance",
                "impact": "negative",
                "score": gpa / 4.0,
                "description": "Below average academic performance"
            })

        # Attendance Rate
        attendance = features.get("attendance_rate", 0)
        if attendance >= 0.9:
            factors.append({
                "name": "Attendance Rate",
                "impact": "positive",
                "score": attendance,
                "description": "Excellent attendance record"
            })
        elif attendance >= 0.75:
            factors.append({
                "name": "Attendance Rate",
                "impact": "neutral",
                "score": attendance,
                "description": "Good attendance record"
            })
        else:
            factors.append({
                "name": "Attendance Rate",
                "impact": "negative",
                "score": attendance,
                "description": "Poor attendance record"
            })

        # Engagement Level
        engagement = features.get("engagement_score", 0)
        if engagement >= 0.8:
            impact = "positive"
            description = "High engagement level"
        elif engagement >= 0.6:
            impact = "neutral"
            description = "Moderate engagement level"
        else:
            impact = "negative"
            description = "Low engagement level"

        factors.append({
            "name": "Engagement Level",
            "impact": impact,
            "score": engagement,
            "description": description
        })

        return factors

    def _generate_recommendations(self, risk_level: str, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on risk level and factors"""
        recommendations = []

        if risk_level == "low":
            recommendations.extend([
                "Keep up the excellent work! 🎉",
                "Continue attending classes regularly",
                "Maintain your current study habits",
                "Consider helping peers who might be struggling"
            ])
        elif risk_level == "medium":
            recommendations.extend([
                "Focus on improving attendance if needed",
                "Schedule study sessions with classmates",
                "Meet with your academic advisor",
                "Consider joining study groups"
            ])
        else:  # high risk
            recommendations.extend([
                "Immediate intervention recommended",
                "Schedule meeting with academic counselor",
                "Consider tutoring services",
                "Review course load and time management"
            ])

        # Add specific recommendations based on risk factors
        for factor in risk_factors:
            if factor["impact"] == "negative":
                if factor["name"] == "Academic Performance":
                    recommendations.append("Seek additional academic support")
                elif factor["name"] == "Attendance Rate":
                    recommendations.append("Improve class attendance immediately")
                elif factor["name"] == "Engagement Level":
                    recommendations.append("Increase participation in class activities")

        return recommendations[:6]  # Limit to 6 recommendations

    async def _extract_course_features(self, student_id: str, course_id: str) -> Dict[str, Any]:
        """Extract features for course-specific prediction"""
        try:
            grades_collection = self.db.get_collection("grades")
            attendance_collection = self.db.get_collection("attendance")

            # Get course grades
            course_grades = await grades_collection.find({
                "student_id": student_id,
                "course_id": course_id
            }).sort("created_at", -1).to_list(10)

            current_grade = "N/A"
            grade_trend = 0
            if course_grades:
                current_grade = course_grades[0].get("letter_grade", "N/A")
                if len(course_grades) >= 2:
                    recent_avg = np.mean([g.get("grade_points", 0) for g in course_grades[:3]])
                    older_avg = np.mean([g.get("grade_points", 0) for g in course_grades[3:6]])
                    grade_trend = recent_avg - older_avg

            # Get course attendance
            course_attendance = await attendance_collection.find({
                "student_id": student_id,
                "course_id": course_id
            }).to_list(None)

            attendance_rate = 0
            if course_attendance:
                attended = sum(1 for record in course_attendance if record.get("status") == "present")
                attendance_rate = attended / len(course_attendance)

            return {
                "current_grade": current_grade,
                "grade_trend": grade_trend,
                "attendance_rate": attendance_rate,
                "total_assignments": len(course_grades),
                "consistency": np.std([g.get("grade_points", 0) for g in course_grades]) if course_grades else 0
            }
        except Exception as e:
            logger.error(f"Error extracting course features: {str(e)}")
            return {}

    async def _predict_course_grade(self, features: Dict[str, Any]) -> str:
        """Predict grade for a specific course"""
        try:
            # Simplified prediction logic (in real implementation, use trained model)
            base_score = 2.5  # Base C+ grade
            
            # Adjust based on attendance
            attendance_bonus = features.get("attendance_rate", 0.8) * 1.5
            
            # Adjust based on trend
            trend_bonus = max(-0.5, min(0.5, features.get("grade_trend", 0)))
            
            # Calculate predicted GPA
            predicted_gpa = base_score + attendance_bonus + trend_bonus
            predicted_gpa = max(0.0, min(4.0, predicted_gpa))

            # Convert to letter grade
            if predicted_gpa >= 3.7:
                return "A-"
            elif predicted_gpa >= 3.3:
                return "B+"
            elif predicted_gpa >= 3.0:
                return "B"
            elif predicted_gpa >= 2.7:
                return "B-"
            elif predicted_gpa >= 2.3:
                return "C+"
            elif predicted_gpa >= 2.0:
                return "C"
            else:
                return "C-"
        except Exception as e:
            logger.error(f"Error predicting course grade: {str(e)}")
            return "B"  # Default prediction

    def _calculate_prediction_confidence(self, features: Dict[str, Any]) -> float:
        """Calculate confidence in grade prediction"""
        try:
            # Base confidence
            confidence = 0.7
            
            # Increase confidence with more data
            if features.get("total_assignments", 0) > 5:
                confidence += 0.1
            
            # Increase confidence with consistent performance
            consistency = features.get("consistency", 1.0)
            if consistency < 0.5:  # Low standard deviation means consistent performance
                confidence += 0.15
            
            # Increase confidence with good attendance
            if features.get("attendance_rate", 0) > 0.9:
                confidence += 0.05

            return min(0.99, confidence)
        except Exception as e:
            logger.error(f"Error calculating prediction confidence: {str(e)}")
            return 0.75

    def _calculate_improvement_potential(self, features: Dict[str, Any]) -> str:
        """Calculate improvement potential for a course"""
        attendance = features.get("attendance_rate", 0)
        trend = features.get("grade_trend", 0)
        
        if attendance < 0.8 and trend < 0:
            return "high"
        elif attendance < 0.9 or trend < 0:
            return "medium"
        else:
            return "low"

    def _calculate_predicted_gpa(self, predictions: List[Dict[str, Any]]) -> float:
        """Calculate overall predicted GPA from course predictions"""
        try:
            grade_points = {
                "A": 4.0, "A-": 3.7, "B+": 3.3, "B": 3.0, "B-": 2.7,
                "C+": 2.3, "C": 2.0, "C-": 1.7, "D+": 1.3, "D": 1.0, "F": 0.0
            }
            
            total_points = 0
            total_courses = 0
            
            for pred in predictions:
                grade = pred.get("predicted_grade", "B")
                points = grade_points.get(grade, 3.0)
                total_points += points
                total_courses += 1
            
            return round(total_points / total_courses, 2) if total_courses > 0 else 0.0
        except Exception as e:
            logger.error(f"Error calculating predicted GPA: {str(e)}")
            return 0.0

    def _generate_semester_outlook(self, predictions: List[Dict[str, Any]]) -> str:
        """Generate semester outlook based on predictions"""
        try:
            avg_confidence = np.mean([pred.get("confidence", 0.75) for pred in predictions])
            predicted_gpa = self._calculate_predicted_gpa(predictions)
            
            if predicted_gpa >= 3.5 and avg_confidence >= 0.8:
                return "excellent"
            elif predicted_gpa >= 3.0 and avg_confidence >= 0.7:
                return "good"
            elif predicted_gpa >= 2.5:
                return "fair"
            else:
                return "needs_improvement"
        except Exception as e:
            logger.error(f"Error generating semester outlook: {str(e)}")
            return "fair"
