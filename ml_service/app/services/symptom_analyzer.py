import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModel
import torch

logger = logging.getLogger(__name__)

class SymptomAnalyzer:
    """
    AI-powered symptom analysis service using clinical NLP models
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.symptom_classifier = None
        self.symptom_encoder = None
        self._load_models()

    def _load_models(self):
        """Load pre-trained symptom analysis models"""
        try:
            # Load symptom classification model
            self.symptom_classifier = pipeline(
                "text-classification",
                model="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract",
                return_all_scores=True
            )

            # Load symptom encoding model for similarity
            self.symptom_encoder = pipeline(
                "feature-extraction",
                model="microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract"
            )

            self.logger.info("Symptom analysis models loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load symptom analysis models: {e}")
            # Fallback to rule-based analysis
            self.symptom_classifier = None
            self.symptom_encoder = None

    async def analyze_symptoms(
        self,
        symptoms: List[str],
        patient_age: Optional[int] = None,
        patient_gender: Optional[str] = None,
        medical_history: Optional[List[str]] = None,
        current_medications: Optional[List[str]] = None,
        vital_signs: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Analyze patient symptoms using AI models and clinical knowledge
        """
        try:
            analysis_id = str(uuid.uuid4())
            self.logger.info(f"Starting symptom analysis {analysis_id} for {len(symptoms)} symptoms")

            # Combine symptoms into text for analysis
            symptoms_text = " ".join(symptoms)

            # Get AI-based diagnosis if models are available
            if self.symptom_classifier:
                ai_diagnosis = await self._get_ai_diagnosis(symptoms_text)
            else:
                ai_diagnosis = await self._get_rule_based_diagnosis(symptoms, patient_age, patient_gender)

            # Get differential diagnoses
            differential_diagnoses = await self._get_differential_diagnoses(
                symptoms, ai_diagnosis, patient_age, patient_gender
            )

            # Assess urgency level
            urgency_level = self._assess_urgency(symptoms, vital_signs, patient_age)

            # Generate treatment suggestions
            treatment_suggestions = await self._generate_treatment_suggestions(
                ai_diagnosis, symptoms, patient_age, patient_gender
            )

            # Identify risk factors
            risk_factors = self._identify_risk_factors(
                symptoms, patient_age, patient_gender, medical_history, current_medications
            )

            # Recommend tests
            recommended_tests = self._recommend_tests(ai_diagnosis, symptoms, patient_age)

            # Calculate confidence score
            confidence_score = self._calculate_confidence(
                symptoms, ai_diagnosis, differential_diagnoses
            )

            analysis_result = {
                "analysis_id": analysis_id,
                "primary_diagnosis": ai_diagnosis,
                "confidence_score": confidence_score,
                "differential_diagnoses": differential_diagnoses,
                "recommended_tests": recommended_tests,
                "urgency_level": urgency_level,
                "treatment_suggestions": treatment_suggestions,
                "risk_factors": risk_factors,
                "analysis_timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Symptom analysis {analysis_id} completed successfully")
            return analysis_result

        except Exception as e:
            self.logger.error(f"Symptom analysis failed: {e}")
            raise

    async def _get_ai_diagnosis(self, symptoms_text: str) -> str:
        """Get AI-based diagnosis using pre-trained models"""
        try:
            # Use the symptom classifier to get diagnosis probabilities
            results = self.symptom_classifier(symptoms_text)

            # Get the most likely diagnosis
            if results and len(results) > 0:
                top_result = max(results[0], key=lambda x: x['score'])
                return top_result['label']
            else:
                return "General symptoms"

        except Exception as e:
            self.logger.warning(f"AI diagnosis failed, falling back to rule-based: {e}")
            return "General symptoms"

    async def _get_rule_based_diagnosis(
        self,
        symptoms: List[str],
        patient_age: Optional[int],
        patient_gender: Optional[str]
    ) -> str:
        """Fallback rule-based diagnosis system"""

        # Define symptom-diagnosis mappings
        symptom_patterns = {
            "fever": ["viral infection", "bacterial infection", "inflammatory condition"],
            "cough": ["respiratory infection", "allergy", "asthma"],
            "headache": ["tension headache", "migraine", "sinusitis"],
            "fatigue": ["viral infection", "anemia", "depression"],
            "nausea": ["gastroenteritis", "migraine", "medication side effect"],
            "chest_pain": ["musculoskeletal", "gastroesophageal reflux", "anxiety"],
            "shortness_of_breath": ["asthma", "anxiety", "respiratory infection"]
        }

        # Match symptoms to patterns
        matched_diagnoses = []
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for pattern, diagnoses in symptom_patterns.items():
                if pattern in symptom_lower:
                    matched_diagnoses.extend(diagnoses)

        # Return most common diagnosis or default
        if matched_diagnoses:
            from collections import Counter
            diagnosis_counts = Counter(matched_diagnoses)
            return diagnosis_counts.most_common(1)[0][0]

        return "General symptoms"

    async def _get_differential_diagnoses(
        self,
        symptoms: List[str],
        primary_diagnosis: str,
        patient_age: Optional[int],
        patient_gender: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get differential diagnoses based on symptoms and patient characteristics"""

        differentials = []

        # Age and gender-specific differentials
        if patient_age and patient_age > 65:
            differentials.extend([
                {"diagnosis": "Cardiovascular disease", "probability": 0.3},
                {"diagnosis": "Diabetes complications", "probability": 0.2},
                {"diagnosis": "Medication interactions", "probability": 0.25}
            ])

        if patient_gender == "female":
            differentials.extend([
                {"diagnosis": "Autoimmune conditions", "probability": 0.2},
                {"diagnosis": "Hormonal imbalances", "probability": 0.15}
            ])

        # Symptom-specific differentials
        for symptom in symptoms:
            symptom_lower = symptom.lower()
            if "fever" in symptom_lower:
                differentials.append({"diagnosis": "Infectious disease", "probability": 0.4})
            elif "cough" in symptom_lower:
                differentials.append({"diagnosis": "Respiratory condition", "probability": 0.35})
            elif "fatigue" in symptom_lower:
                differentials.append({"diagnosis": "Chronic condition", "probability": 0.3})

        # Remove duplicates and sort by probability
        unique_differentials = {}
        for diff in differentials:
            if diff["diagnosis"] not in unique_differentials:
                unique_differentials[diff["diagnosis"]] = diff["probability"]
            else:
                unique_differentials[diff["diagnosis"]] = max(
                    unique_differentials[diff["diagnosis"]], diff["probability"]
                )

        return [
            {"diagnosis": diagnosis, "probability": prob}
            for diagnosis, prob in sorted(
                unique_differentials.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def _assess_urgency(
        self,
        symptoms: List[str],
        vital_signs: Optional[Dict[str, float]],
        patient_age: Optional[int]
    ) -> str:
        """Assess urgency level based on symptoms and vital signs"""

        urgency_score = 0

        # High urgency symptoms
        high_urgency_symptoms = [
            "chest pain", "shortness of breath", "severe bleeding",
            "unconsciousness", "seizure", "paralysis"
        ]

        # Medium urgency symptoms
        medium_urgency_symptoms = [
            "fever", "moderate pain", "dizziness", "nausea", "vomiting"
        ]

        for symptom in symptoms:
            symptom_lower = symptom.lower()
            if any(high in symptom_lower for high in high_urgency_symptoms):
                urgency_score += 3
            elif any(medium in symptom_lower for medium in medium_urgency_symptoms):
                urgency_score += 1

        # Vital signs assessment
        if vital_signs:
            if vital_signs.get("heart_rate", 0) > 120 or vital_signs.get("heart_rate", 0) < 50:
                urgency_score += 2
            if vital_signs.get("blood_pressure_systolic", 0) > 180 or vital_signs.get("blood_pressure_systolic", 0) < 90:
                urgency_score += 2
            if vital_signs.get("temperature", 0) > 39.0:
                urgency_score += 1

        # Age factor
        if patient_age and patient_age > 65:
            urgency_score += 1

        # Determine urgency level
        if urgency_score >= 5:
            return "critical"
        elif urgency_score >= 3:
            return "high"
        elif urgency_score >= 1:
            return "medium"
        else:
            return "low"

    async def _generate_treatment_suggestions(
        self,
        diagnosis: str,
        symptoms: List[str],
        patient_age: Optional[int],
        patient_gender: Optional[str]
    ) -> List[str]:
        """Generate treatment suggestions based on diagnosis and patient characteristics"""

        treatment_suggestions = []

        # General treatment suggestions
        if "infection" in diagnosis.lower():
            treatment_suggestions.extend([
                "Rest and hydration",
                "Over-the-counter pain relievers if needed",
                "Monitor for worsening symptoms"
            ])

        if "pain" in diagnosis.lower():
            treatment_suggestions.extend([
                "Pain management with appropriate medications",
                "Rest and elevation if applicable",
                "Consider physical therapy for chronic pain"
            ])

        # Age-specific suggestions
        if patient_age and patient_age > 65:
            treatment_suggestions.append("Monitor for medication interactions")
            treatment_suggestions.append("Consider lower medication dosages")

        # Gender-specific suggestions
        if patient_gender == "female":
            treatment_suggestions.append("Consider hormonal factors in treatment")

        return treatment_suggestions

    def _identify_risk_factors(
        self,
        symptoms: List[str],
        patient_age: Optional[int],
        patient_gender: Optional[str],
        medical_history: Optional[List[str]],
        current_medications: Optional[List[str]]
    ) -> List[str]:
        """Identify risk factors based on symptoms and patient characteristics"""

        risk_factors = []

        # Age-related risks
        if patient_age and patient_age > 65:
            risk_factors.extend([
                "Age-related decline in organ function",
                "Increased risk of medication interactions",
                "Higher risk of complications"
            ])

        # Gender-related risks
        if patient_gender == "female":
            risk_factors.append("Pregnancy considerations if applicable")

        # Medical history risks
        if medical_history:
            for condition in medical_history:
                if "diabetes" in condition.lower():
                    risk_factors.append("Diabetes complications")
                elif "heart" in condition.lower():
                    risk_factors.append("Cardiovascular complications")
                elif "lung" in condition.lower():
                    risk_factors.append("Respiratory complications")

        # Medication risks
        if current_medications:
            risk_factors.append("Potential medication interactions")

        return risk_factors

    def _recommend_tests(
        self,
        diagnosis: str,
        symptoms: List[str],
        patient_age: Optional[int]
    ) -> List[str]:
        """Recommend diagnostic tests based on diagnosis and symptoms"""

        recommended_tests = []

        # General tests
        recommended_tests.append("Complete blood count (CBC)")
        recommended_tests.append("Basic metabolic panel")

        # Diagnosis-specific tests
        if "infection" in diagnosis.lower():
            recommended_tests.extend([
                "C-reactive protein (CRP)",
                "Erythrocyte sedimentation rate (ESR)"
            ])

        if "cardiac" in diagnosis.lower() or "chest pain" in " ".join(symptoms).lower():
            recommended_tests.extend([
                "Electrocardiogram (ECG)",
                "Troponin levels",
                "Chest X-ray"
            ])

        # Age-specific tests
        if patient_age and patient_age > 65:
            recommended_tests.append("Thyroid function tests")

        return recommended_tests

    def _calculate_confidence(
        self,
        symptoms: List[str],
        primary_diagnosis: str,
        differential_diagnoses: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence score for the analysis"""

        # Base confidence
        base_confidence = 0.6

        # Symptom count factor (more symptoms = higher confidence)
        symptom_factor = min(len(symptoms) * 0.1, 0.2)

        # Differential diagnosis factor (fewer differentials = higher confidence)
        differential_factor = max(0.2 - (len(differential_diagnoses) * 0.02), 0.0)

        # Diagnosis specificity factor
        specificity_factor = 0.1 if len(primary_diagnosis.split()) > 2 else 0.0

        confidence = base_confidence + symptom_factor + differential_factor + specificity_factor

        # Ensure confidence is between 0.0 and 1.0
        return max(0.0, min(1.0, confidence))







