"""
Grade Prediction Model for EduPredict
Uses Random Forest Regressor to predict student grades
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from loguru import logger
from typing import Dict, List

class GradePredictor:
    """Machine Learning model for predicting student grades"""
    
    def __init__(self, model_path: str = "app/ml/models/grade_model.joblib"):
        self.model_path = model_path
        self.model = None
        self.feature_columns = [
            'previous_gpa', 'attendance_rate', 'assignment_avg', 'quiz_avg',
            'midterm_score', 'participation_score', 'course_difficulty'
        ]
        
    def prepare_features(self, student_data: Dict, course_data: Dict) -> np.ndarray:
        """
        Prepare feature vector from student and course data
        
        Args:
            student_data: Dictionary containing student information
            course_data: Dictionary containing course information
            
        Returns:
            Feature vector for prediction
        """
        try:
            features = {
                'previous_gpa': student_data.get('gpa', 0.0),
                'attendance_rate': student_data.get('attendance_rate', 0.0),
                'assignment_avg': course_data.get('assignment_avg', 0.0),
                'quiz_avg': course_data.get('quiz_avg', 0.0),
                'midterm_score': course_data.get('midterm_score', 0.0),
                'participation_score': course_data.get('participation_score', 0.0),
                'course_difficulty': course_data.get('difficulty_rating', 3.0)
            }
            
            feature_vector = np.array([features[col] for col in self.feature_columns]).reshape(1, -1)
            return feature_vector
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return np.zeros((1, len(self.feature_columns)))
    
    def train_model(self, training_data: pd.DataFrame) -> Dict:
        """
        Train the grade prediction model
        
        Args:
            training_data: DataFrame with student and course data
            
        Returns:
            Training results and metrics
        """
        try:
            # Prepare features and target
            X = training_data[self.feature_columns]
            y = training_data['final_grade_points']
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                random_state=42,
                min_samples_split=5,
                min_samples_leaf=2
            )
            
            self.model.fit(X_train, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test)
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            # Save model
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            
            logger.info(f"Grade model trained - MAE: {mae:.3f}, RMSE: {rmse:.3f}, R²: {r2:.3f}")
            
            return {
                'mae': mae,
                'rmse': rmse,
                'r2_score': r2,
                'feature_importance': dict(zip(self.feature_columns, self.model.feature_importances_))
            }
            
        except Exception as e:
            logger.error(f"Error training grade model: {e}")
            raise
    
    def load_model(self) -> bool:
        """Load trained model from file"""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info("Grade prediction model loaded successfully")
                return True
            else:
                logger.warning("No trained grade model found")
                return False
        except Exception as e:
            logger.error(f"Error loading grade model: {e}")
            return False
    
    def predict_grade(self, student_data: Dict, course_data: Dict) -> Dict:
        """
        Predict final grade for a student in a course
        
        Args:
            student_data: Student information
            course_data: Course information and current performance
            
        Returns:
            Grade prediction with confidence
        """
        try:
            # Load model if not already loaded
            if self.model is None:
                if not self.load_model():
                    return self._default_grade_prediction(student_data, course_data)
            
            # Prepare features
            features = self.prepare_features(student_data, course_data)
            
            # Make prediction
            predicted_gpa = self.model.predict(features)[0]
            
            # Convert to letter grade
            letter_grade = self._gpa_to_letter(predicted_gpa)
            
            # Calculate confidence (simplified)
            confidence = min(95, max(60, 85 - abs(predicted_gpa - student_data.get('gpa', 3.0)) * 10))
            
            return {
                'student_id': student_data.get('student_id', 'unknown'),
                'course_id': course_data.get('course_id', 'unknown'),
                'predicted_grade_points': float(predicted_gpa),
                'predicted_letter_grade': letter_grade,
                'confidence': float(confidence),
                'current_performance': course_data.get('current_grade', 'N/A'),
                'factors': self._identify_grade_factors(student_data, course_data)
            }
            
        except Exception as e:
            logger.error(f"Error predicting grade: {e}")
            return self._default_grade_prediction(student_data, course_data)
    
    def _default_grade_prediction(self, student_data: Dict, course_data: Dict) -> Dict:
        """Default prediction when model is not available"""
        current_gpa = student_data.get('gpa', 3.0)
        attendance = student_data.get('attendance_rate', 0.85)
        
        # Simple rule-based prediction
        predicted_gpa = current_gpa * (0.7 + 0.3 * attendance)
        predicted_gpa = max(0.0, min(4.0, predicted_gpa))
        
        return {
            'student_id': student_data.get('student_id', 'unknown'),
            'course_id': course_data.get('course_id', 'unknown'),
            'predicted_grade_points': predicted_gpa,
            'predicted_letter_grade': self._gpa_to_letter(predicted_gpa),
            'confidence': 75.0,
            'current_performance': course_data.get('current_grade', 'N/A'),
            'factors': ['Based on current GPA and attendance']
        }
    
    def _gpa_to_letter(self, gpa: float) -> str:
        """Convert GPA to letter grade"""
        if gpa >= 3.7:
            return "A"
        elif gpa >= 3.3:
            return "A-"
        elif gpa >= 3.0:
            return "B+"
        elif gpa >= 2.7:
            return "B"
        elif gpa >= 2.3:
            return "B-"
        elif gpa >= 2.0:
            return "C+"
        elif gpa >= 1.7:
            return "C"
        elif gpa >= 1.3:
            return "C-"
        elif gpa >= 1.0:
            return "D"
        else:
            return "F"
    
    def _identify_grade_factors(self, student_data: Dict, course_data: Dict) -> List[str]:
        """Identify factors affecting grade prediction"""
        factors = []
        
        gpa = student_data.get('gpa', 0.0)
        attendance = student_data.get('attendance_rate', 0.0)
        
        if gpa > 3.5:
            factors.append("Strong academic history")
        elif gpa < 2.5:
            factors.append("Academic performance concerns")
            
        if attendance > 0.9:
            factors.append("Excellent attendance")
        elif attendance < 0.75:
            factors.append("Attendance issues")
            
        return factors

# Global instance
grade_predictor = GradePredictor()