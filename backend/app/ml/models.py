"""
Machine Learning models for student performance prediction
"""

# Optional imports for ML functionality
try:
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, mean_squared_error, classification_report
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    pd = None
    np = None

import os
from typing import Dict, List, Tuple, Any

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

from app.core.config import settings


class DropoutPredictor:
    """Machine learning model for predicting student dropout risk"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
    
    def prepare_features(self, data) -> any:
        """Prepare features for training/prediction"""
        if not ML_AVAILABLE:
            raise ImportError("Machine learning packages not available")
        # Define feature columns
        feature_cols = [
            'gpa', 'attendance_rate', 'total_credits', 'current_semester',
            'current_year', 'age', 'gender', 'department', 'program'
        ]
        
        # Create a copy of the data
        df = data.copy()
        
        # Handle missing values
        df['gpa'] = df['gpa'].fillna(df['gpa'].mean())
        df['attendance_rate'] = df['attendance_rate'].fillna(df['attendance_rate'].mean())
        
        # Calculate age if date_of_birth is available
        if 'date_of_birth' in df.columns:
            df['age'] = (pd.Timestamp.now() - pd.to_datetime(df['date_of_birth'])).dt.days / 365.25
        else:
            df['age'] = 20  # Default age
        
        # Encode categorical variables
        categorical_cols = ['gender', 'department', 'program']
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    # Handle unseen categories
                    df[col] = df[col].astype(str)
                    known_categories = set(self.label_encoders[col].classes_)
                    df[col] = df[col].apply(lambda x: x if x in known_categories else 'unknown')
                    df[col] = self.label_encoders[col].transform(df[col])
        
        # Select and return feature columns
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_columns = available_cols
        
        return df[available_cols]
    
    def train(self, training_data, target_column: str = 'dropped_out') -> Dict[str, Any]:
        """Train the dropout prediction model"""
        try:
            # Prepare features
            X = self.prepare_features(training_data)
            y = training_data[target_column]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Get feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.model.feature_importances_
            ))
            
            self.is_trained = True
            
            # Save model
            self.save_model()
            
            logger.info(f"Dropout model trained with accuracy: {accuracy:.4f}")
            
            return {
                'accuracy': accuracy,
                'feature_importance': feature_importance,
                'classification_report': classification_report(y_test, y_pred, output_dict=True)
            }
            
        except Exception as e:
            logger.error(f"Failed to train dropout model: {e}")
            raise
    
    def predict(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict dropout risk for a student"""
        try:
            if not self.is_trained:
                self.load_model()
            
            # Convert to DataFrame
            df = pd.DataFrame([student_data])
            
            # Prepare features
            X = self.prepare_features(df)
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Make prediction
            dropout_probability = self.model.predict_proba(X_scaled)[0][1]  # Probability of dropout
            dropout_prediction = self.model.predict(X_scaled)[0]
            
            # Get risk factors based on feature importance
            risk_factors = self._identify_risk_factors(student_data)
            
            return {
                'dropout_risk_score': float(dropout_probability),
                'dropout_prediction': bool(dropout_prediction),
                'risk_level': self._get_risk_level(dropout_probability),
                'risk_factors': risk_factors
            }
            
        except Exception as e:
            logger.error(f"Failed to predict dropout risk: {e}")
            return {
                'dropout_risk_score': 0.5,
                'dropout_prediction': False,
                'risk_level': 'medium',
                'risk_factors': []
            }
    
    def _identify_risk_factors(self, student_data: Dict[str, Any]) -> List[str]:
        """Identify risk factors for a student"""
        risk_factors = []
        
        # GPA-based risk factors
        gpa = student_data.get('gpa', 3.0)
        if gpa < 2.0:
            risk_factors.append('Very low GPA')
        elif gpa < 2.5:
            risk_factors.append('Low GPA')
        
        # Attendance-based risk factors
        attendance = student_data.get('attendance_rate', 0.8)
        if attendance < 0.6:
            risk_factors.append('Very low attendance')
        elif attendance < 0.75:
            risk_factors.append('Low attendance')
        
        # Credit-based risk factors
        current_semester = student_data.get('current_semester', 1)
        total_credits = student_data.get('total_credits', 0)
        expected_credits = current_semester * 15  # Assuming 15 credits per semester
        
        if total_credits < expected_credits * 0.7:
            risk_factors.append('Behind in credit completion')
        
        return risk_factors
    
    def _get_risk_level(self, probability: float) -> str:
        """Convert probability to risk level"""
        if probability < 0.3:
            return 'low'
        elif probability < 0.7:
            return 'medium'
        else:
            return 'high'
    
    def save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(settings.DROPOUT_MODEL_PATH), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained
            }
            
            joblib.dump(model_data, settings.DROPOUT_MODEL_PATH)
            logger.info("Dropout model saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save dropout model: {e}")
    
    def load_model(self):
        """Load a trained model"""
        try:
            if os.path.exists(settings.DROPOUT_MODEL_PATH):
                model_data = joblib.load(settings.DROPOUT_MODEL_PATH)
                
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                self.feature_columns = model_data['feature_columns']
                self.is_trained = model_data['is_trained']
                
                logger.info("Dropout model loaded successfully")
            else:
                logger.warning("No trained dropout model found")
                
        except Exception as e:
            logger.error(f"Failed to load dropout model: {e}")


class GradePredictor:
    """Machine learning model for predicting student grades"""
    
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
    
    def prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for training/prediction"""
        # Similar to DropoutPredictor but for grade prediction
        feature_cols = [
            'previous_gpa', 'attendance_rate', 'total_credits', 'current_semester',
            'study_hours', 'assignment_scores', 'quiz_scores', 'department', 'course_difficulty'
        ]
        
        df = data.copy()
        
        # Handle missing values
        numeric_cols = ['previous_gpa', 'attendance_rate', 'study_hours', 'assignment_scores', 'quiz_scores']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = df[col].fillna(df[col].mean())
        
        # Encode categorical variables
        categorical_cols = ['department', 'course_difficulty']
        for col in categorical_cols:
            if col in df.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col].astype(str))
                else:
                    df[col] = df[col].astype(str)
                    known_categories = set(self.label_encoders[col].classes_)
                    df[col] = df[col].apply(lambda x: x if x in known_categories else 'unknown')
                    df[col] = self.label_encoders[col].transform(df[col])
        
        available_cols = [col for col in feature_cols if col in df.columns]
        self.feature_columns = available_cols
        
        return df[available_cols]
    
    def predict(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict grade for a student"""
        try:
            if not self.is_trained:
                self.load_model()
            
            df = pd.DataFrame([student_data])
            X = self.prepare_features(df)
            X_scaled = self.scaler.transform(X)
            
            predicted_grade = self.model.predict(X_scaled)[0]
            
            return {
                'predicted_grade': float(predicted_grade),
                'grade_letter': self._convert_to_letter_grade(predicted_grade),
                'confidence': 0.85  # Placeholder confidence score
            }
            
        except Exception as e:
            logger.error(f"Failed to predict grade: {e}")
            return {
                'predicted_grade': 3.0,
                'grade_letter': 'B',
                'confidence': 0.5
            }
    
    def _convert_to_letter_grade(self, numeric_grade: float) -> str:
        """Convert numeric grade to letter grade"""
        if numeric_grade >= 3.7:
            return 'A'
        elif numeric_grade >= 3.3:
            return 'A-'
        elif numeric_grade >= 3.0:
            return 'B+'
        elif numeric_grade >= 2.7:
            return 'B'
        elif numeric_grade >= 2.3:
            return 'B-'
        elif numeric_grade >= 2.0:
            return 'C+'
        elif numeric_grade >= 1.7:
            return 'C'
        elif numeric_grade >= 1.3:
            return 'C-'
        elif numeric_grade >= 1.0:
            return 'D'
        else:
            return 'F'
    
    def save_model(self):
        """Save the trained model"""
        try:
            os.makedirs(os.path.dirname(settings.GRADE_MODEL_PATH), exist_ok=True)
            
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'label_encoders': self.label_encoders,
                'feature_columns': self.feature_columns,
                'is_trained': self.is_trained
            }
            
            joblib.dump(model_data, settings.GRADE_MODEL_PATH)
            logger.info("Grade model saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save grade model: {e}")
    
    def load_model(self):
        """Load a trained model"""
        try:
            if os.path.exists(settings.GRADE_MODEL_PATH):
                model_data = joblib.load(settings.GRADE_MODEL_PATH)
                
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.label_encoders = model_data['label_encoders']
                self.feature_columns = model_data['feature_columns']
                self.is_trained = model_data['is_trained']
                
                logger.info("Grade model loaded successfully")
            else:
                logger.warning("No trained grade model found")
                
        except Exception as e:
            logger.error(f"Failed to load grade model: {e}")
