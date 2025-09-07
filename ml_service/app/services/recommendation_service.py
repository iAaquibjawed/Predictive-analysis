import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class RecommendationService:
    """
    Service for generating AI-powered treatment recommendations and clinical decisions
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.clinical_knowledge_base = self._load_clinical_knowledge()

    def _load_clinical_knowledge(self) -> Dict[str, Any]:
        """Load clinical knowledge base for recommendations"""
        # In production, this would load from clinical databases and guidelines
        return {
            "diabetes": {
                "first_line": ["metformin"],
                "second_line": ["sulfonylureas", "dpp4_inhibitors", "glp1_agonists"],
                "monitoring": ["hba1c", "blood_glucose", "kidney_function"],
                "contraindications": ["kidney_disease", "liver_disease"]
            },
            "hypertension": {
                "first_line": ["ace_inhibitors", "calcium_channel_blockers", "thiazide_diuretics"],
                "second_line": ["beta_blockers", "alpha_blockers"],
                "monitoring": ["blood_pressure", "kidney_function", "electrolytes"],
                "contraindications": ["pregnancy", "angioedema"]
            },
            "hyperlipidemia": {
                "first_line": ["statins"],
                "second_line": ["ezetimibe", "pcsk9_inhibitors"],
                "monitoring": ["lipid_panel", "liver_function", "muscle_symptoms"],
                "contraindications": ["liver_disease", "pregnancy"]
            }
        }

    async def generate_diagnosis(
        self,
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate primary diagnosis based on patient symptoms and data
        """
        try:
            symptoms = patient_data.get("symptoms", [])
            age = patient_data.get("age", 0)
            gender = patient_data.get("gender", "")
            medical_history = patient_data.get("medical_history", [])

            # Simple symptom-based diagnosis logic
            # In production, this would use more sophisticated AI models
            diagnosis = self._analyze_symptoms_for_diagnosis(symptoms, age, gender, medical_history)

            # Calculate confidence based on symptom specificity and patient data
            confidence = self._calculate_diagnosis_confidence(symptoms, diagnosis, medical_history)

            return {
                "primary_diagnosis": diagnosis,
                "confidence_score": confidence,
                "differential_diagnoses": self._get_differential_diagnoses(diagnosis, symptoms),
                "supporting_factors": self._get_supporting_factors(symptoms, diagnosis)
            }

        except Exception as e:
            self.logger.error(f"Diagnosis generation failed: {e}")
            raise

    def _analyze_symptoms_for_diagnosis(
        self,
        symptoms: List[str],
        age: int,
        gender: str,
        medical_history: List[str]
    ) -> str:
        """Analyze symptoms to determine primary diagnosis"""

        # Convert symptoms to lowercase for matching
        symptoms_lower = [s.lower() for s in symptoms]

        # Define symptom-diagnosis mappings
        symptom_patterns = {
            "diabetes": ["frequent urination", "excessive thirst", "fatigue", "blurred vision", "slow healing"],
            "hypertension": ["headache", "dizziness", "chest pain", "shortness of breath", "vision problems"],
            "hyperlipidemia": ["chest pain", "shortness of breath", "fatigue", "yellow deposits on skin"],
            "heart_disease": ["chest pain", "shortness of breath", "fatigue", "swelling in legs", "irregular heartbeat"],
            "respiratory_infection": ["cough", "fever", "shortness of breath", "chest congestion", "fatigue"]
        }

        # Score each diagnosis based on symptom matches
        diagnosis_scores = {}
        for diagnosis, pattern_symptoms in symptom_patterns.items():
            score = 0
            for symptom in symptoms_lower:
                if any(pattern in symptom for pattern in pattern_symptoms):
                    score += 1

            # Adjust score based on age and medical history
            if diagnosis == "diabetes" and age > 45:
                score += 1
            if diagnosis == "hypertension" and age > 50:
                score += 1
            if diagnosis in medical_history:
                score += 2

            diagnosis_scores[diagnosis] = score

        # Return diagnosis with highest score
        if diagnosis_scores:
            best_diagnosis = max(diagnosis_scores, key=diagnosis_scores.get)
            if diagnosis_scores[best_diagnosis] > 0:
                return best_diagnosis

        return "general_symptoms"

    def _calculate_diagnosis_confidence(
        self,
        symptoms: List[str],
        diagnosis: str,
        medical_history: List[str]
    ) -> float:
        """Calculate confidence score for diagnosis"""

        base_confidence = 0.5

        # Symptom count factor
        symptom_factor = min(len(symptoms) * 0.1, 0.3)

        # Medical history factor
        history_factor = 0.2 if diagnosis in medical_history else 0.0

        # Symptom specificity factor
        specificity_factor = 0.1 if len(symptoms) >= 3 else 0.0

        confidence = base_confidence + symptom_factor + history_factor + specificity_factor

        return min(1.0, confidence)

    def _get_differential_diagnoses(
        self,
        primary_diagnosis: str,
        symptoms: List[str]
    ) -> List[Dict[str, Any]]:
        """Get differential diagnoses"""

        differentials = []

        # Define differential diagnoses for common conditions
        differential_mappings = {
            "diabetes": [
                {"diagnosis": "prediabetes", "probability": 0.3},
                {"diagnosis": "gestational_diabetes", "probability": 0.1},
                {"diagnosis": "secondary_diabetes", "probability": 0.05}
            ],
            "hypertension": [
                {"diagnosis": "white_coat_hypertension", "probability": 0.2},
                {"diagnosis": "secondary_hypertension", "probability": 0.15},
                {"diagnosis": "masked_hypertension", "probability": 0.1}
            ],
            "hyperlipidemia": [
                {"diagnosis": "familial_hypercholesterolemia", "probability": 0.1},
                {"diagnosis": "secondary_hyperlipidemia", "probability": 0.2}
            ]
        }

        if primary_diagnosis in differential_mappings:
            differentials = differential_mappings[primary_diagnosis]

        return differentials

    def _get_supporting_factors(
        self,
        symptoms: List[str],
        diagnosis: str
    ) -> List[str]:
        """Get factors that support the diagnosis"""

        supporting_factors = []

        # Add symptoms as supporting factors
        supporting_factors.extend(symptoms)

        # Add diagnosis-specific factors
        if diagnosis == "diabetes":
            supporting_factors.append("Age-related risk factors")
            supporting_factors.append("Family history considerations")
        elif diagnosis == "hypertension":
            supporting_factors.append("Lifestyle factors")
            supporting_factors.append("Salt sensitivity")

        return supporting_factors

    async def get_treatment_recommendations(
        self,
        patient_data: Dict[str, Any],
        diagnosis: str
    ) -> List[Dict[str, Any]]:
        """
        Get treatment recommendations based on diagnosis and patient characteristics
        """
        try:
            recommendations = []

            if diagnosis in self.clinical_knowledge_base:
                knowledge = self.clinical_knowledge_base[diagnosis]

                # First-line treatments
                for treatment in knowledge["first_line"]:
                    recommendations.append({
                        "treatment": treatment,
                        "line": "first",
                        "rationale": f"First-line treatment for {diagnosis}",
                        "evidence_level": "A",
                        "monitoring": knowledge["monitoring"]
                    })

                # Second-line treatments
                for treatment in knowledge["second_line"]:
                    recommendations.append({
                        "treatment": treatment,
                        "line": "second",
                        "rationale": f"Second-line treatment for {diagnosis}",
                        "evidence_level": "B",
                        "monitoring": knowledge["monitoring"]
                    })

            # Add patient-specific considerations
            recommendations = self._add_patient_specific_considerations(
                recommendations, patient_data
            )

            return recommendations

        except Exception as e:
            self.logger.error(f"Treatment recommendations failed: {e}")
            raise

    def _add_patient_specific_considerations(
        self,
        recommendations: List[Dict[str, Any]],
        patient_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Add patient-specific considerations to recommendations"""

        age = patient_data.get("age", 0)
        gender = patient_data.get("gender", "")
        medical_history = patient_data.get("medical_history", [])
        current_medications = patient_data.get("current_medications", [])

        for rec in recommendations:
            # Age considerations
            if age > 65:
                rec["considerations"] = rec.get("considerations", [])
                rec["considerations"].append("Consider lower starting dose in elderly patients")
                rec["considerations"].append("Monitor for increased side effects")

            # Gender considerations
            if gender == "female":
                rec["considerations"] = rec.get("considerations", [])
                rec["considerations"].append("Consider pregnancy status and contraception")

            # Medical history considerations
            for condition in medical_history:
                if condition in ["kidney_disease", "liver_disease"]:
                    rec["considerations"] = rec.get("considerations", [])
                    rec["considerations"].append(f"Adjust dose for {condition}")

            # Medication interaction considerations
            if current_medications:
                rec["considerations"] = rec.get("considerations", [])
                rec["considerations"].append("Check for drug interactions with current medications")

        return recommendations

    async def generate_clinical_decisions(
        self,
        patient_data: Dict[str, Any],
        diagnosis: Dict[str, Any],
        treatments: List[Dict[str, Any]],
        guidelines: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate clinical decisions based on diagnosis and treatments
        """
        try:
            decisions = []

            # Diagnosis decision
            decisions.append({
                "decision_id": str(uuid.uuid4()),
                "patient_id": patient_data.get("patient_id", "unknown"),
                "decision_type": "diagnosis",
                "primary_recommendation": f"Confirm {diagnosis['primary_diagnosis']} diagnosis",
                "confidence_score": diagnosis.get("confidence_score", 0.0),
                "reasoning": self._generate_diagnosis_reasoning(diagnosis, patient_data),
                "alternatives": [d["diagnosis"] for d in diagnosis.get("differential_diagnoses", [])],
                "risks": self._assess_diagnosis_risks(diagnosis, patient_data),
                "benefits": self._assess_diagnosis_benefits(diagnosis),
                "clinical_guidelines": guidelines,
                "literature_references": []
            })

            # Treatment decision
            if treatments:
                primary_treatment = next((t for t in treatments if t["line"] == "first"), treatments[0])
                decisions.append({
                    "decision_id": str(uuid.uuid4()),
                    "patient_id": patient_data.get("patient_id", "unknown"),
                    "decision_type": "treatment",
                    "primary_recommendation": f"Start {primary_treatment['treatment']}",
                    "confidence_score": 0.8,  # High confidence for evidence-based treatments
                    "reasoning": self._generate_treatment_reasoning(primary_treatment, diagnosis),
                    "alternatives": [t["treatment"] for t in treatments if t["line"] == "second"],
                    "risks": self._assess_treatment_risks(primary_treatment, patient_data),
                    "benefits": self._assess_treatment_benefits(primary_treatment, diagnosis),
                    "clinical_guidelines": guidelines,
                    "literature_references": []
                })

            # Monitoring decision
            monitoring_decision = self._generate_monitoring_decision(treatments, patient_data)
            if monitoring_decision:
                decisions.append(monitoring_decision)

            return decisions

        except Exception as e:
            self.logger.error(f"Clinical decision generation failed: {e}")
            raise

    def _generate_diagnosis_reasoning(
        self,
        diagnosis: Dict[str, Any],
        patient_data: Dict[str, Any]
    ) -> str:
        """Generate reasoning for diagnosis decision"""

        symptoms = patient_data.get("symptoms", [])
        age = patient_data.get("age", 0)

        reasoning = f"Diagnosis of {diagnosis['primary_diagnosis']} is supported by "

        if symptoms:
            reasoning += f"the presence of {', '.join(symptoms[:3])}"
            if len(symptoms) > 3:
                reasoning += f" and {len(symptoms) - 3} additional symptoms"

        if age > 50:
            reasoning += f", age-related risk factors ({age} years old)"

        confidence = diagnosis.get("confidence_score", 0.0)
        if confidence > 0.8:
            reasoning += ". High confidence in this diagnosis."
        elif confidence > 0.6:
            reasoning += ". Moderate confidence in this diagnosis."
        else:
            reasoning += ". Low confidence - consider additional testing."

        return reasoning

    def _generate_treatment_reasoning(
        self,
        treatment: Dict[str, Any],
        diagnosis: Dict[str, Any]
    ) -> str:
        """Generate reasoning for treatment decision"""

        reasoning = f"Recommendation to start {treatment['treatment']} is based on "

        if treatment["line"] == "first":
            reasoning += "its status as a first-line treatment for "
        else:
            reasoning += "its effectiveness as a second-line treatment for "

        reasoning += f"{diagnosis['primary_diagnosis']}. "

        if treatment.get("evidence_level"):
            reasoning += f"Evidence level: {treatment['evidence_level']}. "

        if treatment.get("monitoring"):
            reasoning += f"Monitoring required: {', '.join(treatment['monitoring'])}."

        return reasoning

    def _assess_diagnosis_risks(
        self,
        diagnosis: Dict[str, Any],
        patient_data: Dict[str, Any]
    ) -> List[str]:
        """Assess risks associated with diagnosis"""

        risks = []
        age = patient_data.get("age", 0)

        if diagnosis["primary_diagnosis"] == "diabetes":
            risks.extend([
                "Long-term complications if untreated",
                "Cardiovascular disease risk",
                "Kidney disease progression"
            ])
            if age > 65:
                risks.append("Increased risk of complications in elderly")

        elif diagnosis["primary_diagnosis"] == "hypertension":
            risks.extend([
                "Stroke risk",
                "Heart disease progression",
                "Kidney damage"
            ])

        return risks

    def _assess_diagnosis_benefits(self, diagnosis: Dict[str, Any]) -> List[str]:
        """Assess benefits of making the diagnosis"""

        benefits = [
            "Early intervention possible",
            "Prevention of complications",
            "Improved quality of life",
            "Better long-term outcomes"
        ]

        return benefits

    def _assess_treatment_risks(
        self,
        treatment: Dict[str, Any],
        patient_data: Dict[str, Any]
    ) -> List[str]:
        """Assess risks associated with treatment"""

        risks = []
        age = patient_data.get("age", 0)

        # General treatment risks
        risks.append("Potential side effects")
        risks.append("Drug interactions")

        # Age-specific risks
        if age > 65:
            risks.append("Increased sensitivity to medications")
            risks.append("Higher risk of adverse effects")

        # Treatment-specific risks
        if "metformin" in treatment["treatment"].lower():
            risks.append("Gastrointestinal side effects")
            risks.append("Lactic acidosis risk in kidney disease")

        return risks

    def _assess_treatment_benefits(
        self,
        treatment: Dict[str, Any],
        diagnosis: Dict[str, Any]
    ) -> List[str]:
        """Assess benefits of treatment"""

        benefits = [
            "Symptom improvement",
            "Disease progression prevention",
            "Complication reduction",
            "Evidence-based approach"
        ]

        return benefits

    def _generate_monitoring_decision(
        self,
        treatments: List[Dict[str, Any]],
        patient_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate monitoring decision"""

        if not treatments:
            return None

        # Collect all monitoring requirements
        monitoring_parameters = set()
        for treatment in treatments:
            if treatment.get("monitoring"):
                monitoring_parameters.update(treatment["monitoring"])

        if not monitoring_parameters:
            return None

        # Determine monitoring frequency
        monitoring_frequency = "monthly"  # Default
        if any("kidney" in param.lower() for param in monitoring_parameters):
            monitoring_frequency = "weekly"

        return {
            "decision_id": str(uuid.uuid4()),
            "patient_id": patient_data.get("patient_id", "unknown"),
            "decision_type": "monitoring",
            "primary_recommendation": f"Implement {monitoring_frequency} monitoring",
            "confidence_score": 0.9,
            "reasoning": f"Regular monitoring required for {', '.join(monitoring_parameters)}",
            "alternatives": ["Bi-weekly monitoring", "Quarterly monitoring"],
            "risks": ["Missed complications", "Delayed intervention"],
            "benefits": ["Early detection", "Timely intervention", "Better outcomes"],
            "clinical_guidelines": [],
            "literature_references": []
        }

    async def assess_patient_risks(
        self,
        patient_data: Dict[str, Any],
        treatments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assess patient risks based on data and proposed treatments
        """
        try:
            risks = []
            risk_level = "low"

            age = patient_data.get("age", 0)
            medical_history = patient_data.get("medical_history", [])
            current_medications = patient_data.get("current_medications", [])

            # Age-related risks
            if age > 75:
                risks.append({
                    "category": "age",
                    "description": "Advanced age increases risk of complications",
                    "severity": "medium"
                })
                risk_level = "medium"

            # Medical history risks
            for condition in medical_history:
                if condition in ["kidney_disease", "liver_disease", "heart_disease"]:
                    risks.append({
                        "category": "medical_history",
                        "description": f"Pre-existing {condition} increases treatment risks",
                        "severity": "high"
                    })
                    risk_level = "high"

            # Medication interaction risks
            if len(current_medications) > 3:
                risks.append({
                    "category": "polypharmacy",
                    "description": "Multiple medications increase interaction risk",
                    "severity": "medium"
                })
                if risk_level == "low":
                    risk_level = "medium"

            # Treatment-specific risks
            for treatment in treatments:
                if "kidney" in treatment.get("monitoring", []):
                    risks.append({
                        "category": "treatment",
                        "description": f"{treatment['treatment']} requires kidney function monitoring",
                        "severity": "medium"
                    })

            return {
                "risk_level": risk_level,
                "risks": risks,
                "recommendations": self._generate_risk_recommendations(risks)
            }

        except Exception as e:
            self.logger.error(f"Patient risk assessment failed: {e}")
            raise

    def _generate_risk_recommendations(self, risks: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on identified risks"""

        recommendations = []

        for risk in risks:
            if risk["category"] == "age":
                recommendations.append("Implement more frequent monitoring")
                recommendations.append("Consider lower starting doses")
            elif risk["category"] == "medical_history":
                recommendations.append("Consult with specialists if needed")
                recommendations.append("Implement intensive monitoring protocols")
            elif risk["category"] == "polypharmacy":
                recommendations.append("Review all medications for interactions")
                recommendations.append("Consider medication reconciliation")
            elif risk["category"] == "treatment":
                recommendations.append("Implement specific monitoring protocols")
                recommendations.append("Educate patient about warning signs")

        return recommendations

    async def create_monitoring_plan(
        self,
        patient_data: Dict[str, Any],
        treatments: List[Dict[str, Any]],
        risks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create comprehensive monitoring plan for patient
        """
        try:
            monitoring_plan = {
                "parameters": [],
                "frequency": "monthly",
                "duration": "ongoing",
                "escalation_criteria": [],
                "follow_up_recommendations": []
            }

            # Collect monitoring parameters from treatments
            for treatment in treatments:
                if treatment.get("monitoring"):
                    monitoring_plan["parameters"].extend(treatment["monitoring"])

            # Add risk-based monitoring
            if risks.get("risk_level") == "high":
                monitoring_plan["frequency"] = "weekly"
                monitoring_plan["parameters"].append("vital_signs")
                monitoring_plan["parameters"].append("symptom_assessment")

            # Determine follow-up schedule
            if risks.get("risk_level") == "high":
                monitoring_plan["follow_up_recommendations"].append("Weekly follow-up for first month")
                monitoring_plan["follow_up_recommendations"].append("Monthly follow-up thereafter")
            else:
                monitoring_plan["follow_up_recommendations"].append("Monthly follow-up")
                monitoring_plan["follow_up_recommendations"].append("Quarterly review")

            # Add escalation criteria
            monitoring_plan["escalation_criteria"] = [
                "Worsening symptoms",
                "Abnormal test results",
                "Medication side effects",
                "Non-compliance"
            ]

            return monitoring_plan

        except Exception as e:
            self.logger.error(f"Monitoring plan creation failed: {e}")
            raise

    async def get_recommendation_history(
        self,
        patient_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get history of recommendations for a patient
        """
        try:
            # Mock recommendation history - in production, this would query the database
            history = [
                {
                    "date": "2024-01-15",
                    "diagnosis": "diabetes",
                    "treatment": "metformin",
                    "outcome": "improved"
                },
                {
                    "date": "2024-02-15",
                    "diagnosis": "hypertension",
                    "treatment": "lisinopril",
                    "outcome": "stable"
                }
            ]

            return history[:limit]

        except Exception as e:
            self.logger.error(f"Failed to get recommendation history: {e}")
            raise

    async def record_feedback(
        self,
        patient_id: str,
        feedback: Dict[str, Any],
        provided_by: str
    ) -> Dict[str, Any]:
        """
        Record feedback on recommendations to improve the system
        """
        try:
            feedback_id = str(uuid.uuid4())

            # Store feedback - in production, this would save to database
            stored_feedback = {
                "feedback_id": feedback_id,
                "patient_id": patient_id,
                "provided_by": provided_by,
                "timestamp": datetime.now().isoformat(),
                "feedback": feedback
            }

            return {
                "feedback_id": feedback_id,
                "status": "recorded",
                "message": "Feedback recorded successfully"
            }

        except Exception as e:
            self.logger.error(f"Failed to record feedback: {e}")
            raise

    async def validate_treatment_plan(
        self,
        treatment_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate treatment plan against clinical guidelines and best practices
        """
        try:
            validation_result = {
                "is_valid": True,
                "warnings": [],
                "errors": [],
                "recommendations": []
            }

            # Check for required components
            required_fields = ["diagnosis", "treatments", "monitoring"]
            for field in required_fields:
                if field not in treatment_plan:
                    validation_result["is_valid"] = False
                    validation_result["errors"].append(f"Missing required field: {field}")

            # Check treatment appropriateness
            if "treatments" in treatment_plan:
                for treatment in treatment_plan["treatments"]:
                    if treatment.get("line") == "first" and not treatment.get("evidence_level"):
                        validation_result["warnings"].append(f"First-line treatment {treatment['treatment']} missing evidence level")

            # Check monitoring plan
            if "monitoring" in treatment_plan:
                monitoring = treatment_plan["monitoring"]
                if not monitoring.get("parameters"):
                    validation_result["warnings"].append("Monitoring plan missing specific parameters")

            return validation_result

        except Exception as e:
            self.logger.error(f"Treatment plan validation failed: {e}")
            raise

    async def compare_treatments(
        self,
        treatments: List[str],
        patient_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare multiple treatment options for a patient
        """
        try:
            comparison = {
                "treatments": [],
                "summary": {}
            }

            for treatment in treatments:
                treatment_analysis = {
                    "treatment": treatment,
                    "efficacy": self._assess_treatment_efficacy(treatment),
                    "safety": self._assess_treatment_safety(treatment, patient_context),
                    "cost": self._assess_treatment_cost(treatment),
                    "convenience": self._assess_treatment_convenience(treatment),
                    "recommendation": self._generate_treatment_recommendation(treatment, patient_context)
                }

                comparison["treatments"].append(treatment_analysis)

            # Generate summary
            comparison["summary"] = self._generate_comparison_summary(comparison["treatments"])

            return comparison

        except Exception as e:
            self.logger.error(f"Treatment comparison failed: {e}")
            raise

    def _assess_treatment_efficacy(self, treatment: str) -> Dict[str, Any]:
        """Assess treatment efficacy"""

        # Mock efficacy data - in production, this would query clinical databases
        efficacy_data = {
            "metformin": {"score": 0.85, "evidence": "strong", "description": "Highly effective for diabetes"},
            "lisinopril": {"score": 0.80, "evidence": "strong", "description": "Effective for hypertension"},
            "atorvastatin": {"score": 0.90, "evidence": "strong", "description": "Highly effective for cholesterol"}
        }

        return efficacy_data.get(treatment.lower(), {
            "score": 0.5,
            "evidence": "limited",
            "description": "Limited evidence available"
        })

    def _assess_treatment_safety(
        self,
        treatment: str,
        patient_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess treatment safety for specific patient"""

        # Mock safety assessment
        safety_data = {
            "metformin": {"score": 0.9, "risks": ["GI side effects"], "contraindications": ["kidney_disease"]},
            "lisinopril": {"score": 0.85, "risks": ["cough", "angioedema"], "contraindications": ["pregnancy"]},
            "atorvastatin": {"score": 0.8, "risks": ["muscle pain", "liver issues"], "contraindications": ["liver_disease"]}
        }

        safety = safety_data.get(treatment.lower(), {
            "score": 0.7,
            "risks": ["unknown"],
            "contraindications": []
        })

        # Adjust for patient context
        if patient_context.get("kidney_disease") and "kidney_disease" in safety["contraindications"]:
            safety["score"] *= 0.5
            safety["risks"].append("contraindicated for this patient")

        return safety

    def _assess_treatment_cost(self, treatment: str) -> Dict[str, Any]:
        """Assess treatment cost"""

        # Mock cost data
        cost_data = {
            "metformin": {"cost": "low", "insurance_coverage": "high", "generic_available": True},
            "lisinopril": {"cost": "low", "insurance_coverage": "high", "generic_available": True},
            "atorvastatin": {"cost": "medium", "insurance_coverage": "high", "generic_available": True}
        }

        return cost_data.get(treatment.lower(), {
            "cost": "unknown",
            "insurance_coverage": "unknown",
            "generic_available": False
        })

    def _assess_treatment_convenience(self, treatment: str) -> Dict[str, Any]:
        """Assess treatment convenience"""

        # Mock convenience data
        convenience_data = {
            "metformin": {"dosing": "twice_daily", "administration": "oral", "storage": "room_temperature"},
            "lisinopril": {"dosing": "once_daily", "administration": "oral", "storage": "room_temperature"},
            "atorvastatin": {"dosing": "once_daily", "administration": "oral", "storage": "room_temperature"}
        }

        return convenience_data.get(treatment.lower(), {
            "dosing": "unknown",
            "administration": "unknown",
            "storage": "unknown"
        })

    def _generate_treatment_recommendation(
        self,
        treatment: str,
        patient_context: Dict[str, Any]
    ) -> str:
        """Generate treatment recommendation"""

        # Simple recommendation logic
        if "metformin" in treatment.lower():
            return "Recommended for diabetes management"
        elif "lisinopril" in treatment.lower():
            return "Recommended for hypertension control"
        elif "atorvastatin" in treatment.lower():
            return "Recommended for cholesterol management"
        else:
            return "Consider based on individual patient factors"

    def _generate_comparison_summary(self, treatments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of treatment comparison"""

        if not treatments:
            return {}

        # Find best treatment in each category
        best_efficacy = max(treatments, key=lambda x: x["efficacy"]["score"])
        best_safety = max(treatments, key=lambda x: x["safety"]["score"])
        best_cost = min(treatments, key=lambda x: x["cost"]["cost"] if x["cost"]["cost"] != "unknown" else "high")

        return {
            "best_efficacy": best_efficacy["treatment"],
            "best_safety": best_safety["treatment"],
            "best_cost": best_cost["treatment"],
            "overall_recommendation": best_efficacy["treatment"] if best_efficacy["efficacy"]["score"] > 0.8 else "Consider alternatives"
        }





