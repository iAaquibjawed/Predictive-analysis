import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class ClinicalNLPService:
    """
    Service for clinical NLP and medical literature analysis
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.ncbi.nlm.nih.gov"
        self.api_key = None  # In production, this would be loaded from environment
        self.cache = {}  # Simple cache for demo purposes

    async def search_symptoms(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for symptoms using clinical terminology
        """
        try:
            # Mock symptom search - in production, this would use clinical NLP models
            symptoms_database = {
                "fever": {
                    "symptom": "Fever",
                    "icd10_code": "R50.9",
                    "synonyms": ["Pyrexia", "Elevated temperature", "Hyperthermia"],
                    "severity": "variable",
                    "common_causes": ["Infection", "Inflammation", "Medication side effect"]
                },
                "cough": {
                    "symptom": "Cough",
                    "icd10_code": "R05.9",
                    "synonyms": ["Tussis", "Hacking", "Dry cough", "Wet cough"],
                    "severity": "variable",
                    "common_causes": ["Respiratory infection", "Allergy", "Asthma", "GERD"]
                },
                "headache": {
                    "symptom": "Headache",
                    "icd10_code": "R51.9",
                    "synonyms": ["Cephalalgia", "Head pain", "Migraine"],
                    "severity": "variable",
                    "common_causes": ["Tension", "Migraine", "Sinusitis", "Dehydration"]
                },
                "fatigue": {
                    "symptom": "Fatigue",
                    "icd10_code": "R53.83",
                    "synonyms": ["Tiredness", "Exhaustion", "Lethargy", "Weakness"],
                    "severity": "variable",
                    "common_causes": ["Sleep deprivation", "Stress", "Anemia", "Chronic illness"]
                },
                "nausea": {
                    "symptom": "Nausea",
                    "icd10_code": "R11.0",
                    "synonyms": ["Sick feeling", "Queasiness", "Stomach upset"],
                    "severity": "variable",
                    "common_causes": ["Gastroenteritis", "Migraine", "Medication side effect", "Pregnancy"]
                },
                "chest_pain": {
                    "symptom": "Chest Pain",
                    "icd10_code": "R07.9",
                    "synonyms": ["Thoracic pain", "Chest discomfort", "Angina"],
                    "severity": "high",
                    "common_causes": ["Cardiac", "Respiratory", "Gastrointestinal", "Musculoskeletal"]
                },
                "shortness_of_breath": {
                    "symptom": "Shortness of Breath",
                    "icd10_code": "R06.02",
                    "synonyms": ["Dyspnea", "Breathlessness", "Difficulty breathing"],
                    "severity": "high",
                    "common_causes": ["Asthma", "COPD", "Heart failure", "Anxiety"]
                }
            }

            search_results = []
            query_lower = query.lower()

            for symptom_key, symptom_data in symptoms_database.items():
                if (query_lower in symptom_key.lower() or
                    any(query_lower in synonym.lower() for synonym in symptom_data["synonyms"])):

                    search_results.append({
                        "symptom": symptom_data["symptom"],
                        "icd10_code": symptom_data["icd10_code"],
                        "synonyms": symptom_data["synonyms"],
                        "severity": symptom_data["severity"],
                        "common_causes": symptom_data["common_causes"]
                    })

                    if len(search_results) >= limit:
                        break

            return search_results

        except Exception as e:
            self.logger.error(f"Symptom search failed: {e}")
            raise

    async def autocomplete_symptoms(self, prefix: str, limit: int = 5) -> List[str]:
        """
        Autocomplete symptoms as user types
        """
        try:
            # Mock symptom autocomplete
            all_symptoms = [
                "fever", "cough", "headache", "fatigue", "nausea",
                "chest pain", "shortness of breath", "dizziness",
                "abdominal pain", "back pain", "joint pain",
                "swelling", "rash", "itching", "bleeding"
            ]

            suggestions = []
            prefix_lower = prefix.lower()

            for symptom in all_symptoms:
                if symptom.lower().startswith(prefix_lower):
                    suggestions.append(symptom)

                    if len(suggestions) >= limit:
                        break

            return suggestions

        except Exception as e:
            self.logger.error(f"Symptom autocomplete failed: {e}")
            raise

    async def get_clinical_insights(
        self,
        symptoms: List[str],
        diagnosis: str
    ) -> Dict[str, Any]:
        """
        Get clinical insights and guidelines based on symptoms and diagnosis
        """
        try:
            insights = {
                "guidelines": [],
                "evidence_level": "B",
                "recommendations": [],
                "risk_factors": [],
                "differential_diagnoses": []
            }

            # Get clinical guidelines
            guidelines = await self._get_clinical_guidelines(diagnosis, symptoms)
            insights["guidelines"] = guidelines

            # Get evidence-based recommendations
            recommendations = await self._get_evidence_based_recommendations(diagnosis)
            insights["recommendations"] = recommendations

            # Get risk factors
            risk_factors = await self._get_risk_factors(diagnosis, symptoms)
            insights["risk_factors"] = risk_factors

            # Get differential diagnoses
            differentials = await self._get_differential_diagnoses(symptoms)
            insights["differential_diagnoses"] = differentials

            return insights

        except Exception as e:
            self.logger.error(f"Clinical insights failed: {e}")
            raise

    async def _get_clinical_guidelines(
        self,
        diagnosis: str,
        symptoms: List[str]
    ) -> List[Dict[str, Any]]:
        """Get clinical guidelines for diagnosis"""

        # Mock clinical guidelines database
        guidelines_database = {
            "diabetes": [
                {
                    "source": "NICE Guidelines",
                    "title": "Type 2 diabetes in adults: management",
                    "recommendations": [
                        "Start metformin as first-line therapy",
                        "Target HbA1c of 6.5% (48 mmol/mol)",
                        "Monitor blood glucose regularly"
                    ],
                    "evidence_level": "A",
                    "last_updated": "2023"
                },
                {
                    "source": "ADA Standards of Care",
                    "title": "Standards of Medical Care in Diabetes",
                    "recommendations": [
                        "Individualize glycemic targets",
                        "Consider cardiovascular risk factors",
                        "Regular screening for complications"
                    ],
                    "evidence_level": "A",
                    "last_updated": "2024"
                }
            ],
            "hypertension": [
                {
                    "source": "NICE Guidelines",
                    "title": "Hypertension in adults: diagnosis and management",
                    "recommendations": [
                        "Lifestyle modifications first",
                        "ACE inhibitors or calcium channel blockers as first-line",
                        "Target BP <140/90 mmHg"
                    ],
                    "evidence_level": "A",
                    "last_updated": "2023"
                }
            ],
            "hyperlipidemia": [
                {
                    "source": "NICE Guidelines",
                    "title": "Cardiovascular disease: risk assessment and reduction",
                    "recommendations": [
                        "Statins for primary prevention",
                        "Target LDL-C reduction of 40%",
                        "Regular lipid monitoring"
                    ],
                    "evidence_level": "A",
                    "last_updated": "2023"
                }
            ]
        }

        return guidelines_database.get(diagnosis.lower(), [])

    async def _get_evidence_based_recommendations(self, diagnosis: str) -> List[str]:
        """Get evidence-based recommendations for diagnosis"""

        # Mock recommendations database
        recommendations_database = {
            "diabetes": [
                "Metformin is the first-line therapy for type 2 diabetes (Level A evidence)",
                "Lifestyle modification should be initiated at diagnosis (Level A evidence)",
                "Regular monitoring of HbA1c every 3-6 months (Level B evidence)"
            ],
            "hypertension": [
                "Lifestyle modifications should be initiated for all patients (Level A evidence)",
                "ACE inhibitors or calcium channel blockers are preferred first-line agents (Level A evidence)",
                "Target blood pressure should be <140/90 mmHg (Level A evidence)"
            ],
            "hyperlipidemia": [
                "Statins are first-line therapy for cardiovascular risk reduction (Level A evidence)",
                "High-intensity statins for high-risk patients (Level A evidence)",
                "Regular monitoring of liver function and muscle symptoms (Level B evidence)"
            ]
        }

        return recommendations_database.get(diagnosis.lower(), [
            "Consult clinical guidelines for evidence-based recommendations"
        ])

    async def _get_risk_factors(
        self,
        diagnosis: str,
        symptoms: List[str]
    ) -> List[Dict[str, Any]]:
        """Get risk factors for diagnosis"""

        # Mock risk factors database
        risk_factors_database = {
            "diabetes": [
                {"factor": "Age >45 years", "modifiable": False, "evidence_level": "A"},
                {"factor": "Obesity (BMI >30)", "modifiable": True, "evidence_level": "A"},
                {"factor": "Family history", "modifiable": False, "evidence_level": "A"},
                {"factor": "Physical inactivity", "modifiable": True, "evidence_level": "A"},
                {"factor": "Previous gestational diabetes", "modifiable": False, "evidence_level": "B"}
            ],
            "hypertension": [
                {"factor": "Age >50 years", "modifiable": False, "evidence_level": "A"},
                {"factor": "High salt intake", "modifiable": True, "evidence_level": "A"},
                {"factor": "Obesity", "modifiable": True, "evidence_level": "A"},
                {"factor": "Physical inactivity", "modifiable": True, "evidence_level": "A"},
                {"factor": "Excessive alcohol consumption", "modifiable": True, "evidence_level": "A"}
            ],
            "hyperlipidemia": [
                {"factor": "Age >40 years", "modifiable": False, "evidence_level": "A"},
                {"factor": "High saturated fat diet", "modifiable": True, "evidence_level": "A"},
                {"factor": "Obesity", "modifiable": True, "evidence_level": "A"},
                {"factor": "Physical inactivity", "modifiable": True, "evidence_level": "A"},
                {"factor": "Family history", "modifiable": False, "evidence_level": "A"}
            ]
        }

        return risk_factors_database.get(diagnosis.lower(), [])

    async def _get_differential_diagnoses(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """Get differential diagnoses based on symptoms"""

        # Mock differential diagnosis database
        differential_database = {
            "fever": [
                {"diagnosis": "Viral infection", "probability": 0.4, "evidence_level": "B"},
                {"diagnosis": "Bacterial infection", "probability": 0.3, "evidence_level": "B"},
                {"diagnosis": "Inflammatory condition", "probability": 0.2, "evidence_level": "C"},
                {"diagnosis": "Malignancy", "probability": 0.1, "evidence_level": "C"}
            ],
            "cough": [
                {"diagnosis": "Upper respiratory infection", "probability": 0.5, "evidence_level": "B"},
                {"diagnosis": "Allergy", "probability": 0.2, "evidence_level": "B"},
                {"diagnosis": "Asthma", "probability": 0.15, "evidence_level": "B"},
                {"diagnosis": "GERD", "probability": 0.1, "evidence_level": "C"},
                {"diagnosis": "Pneumonia", "probability": 0.05, "evidence_level": "B"}
            ],
            "headache": [
                {"diagnosis": "Tension headache", "probability": 0.6, "evidence_level": "B"},
                {"diagnosis": "Migraine", "probability": 0.25, "evidence_level": "B"},
                {"diagnosis": "Sinusitis", "probability": 0.1, "evidence_level": "C"},
                {"diagnosis": "Cluster headache", "probability": 0.05, "evidence_level": "C"}
            ]
        }

        differentials = []
        for symptom in symptoms:
            if symptom.lower() in differential_database:
                differentials.extend(differential_database[symptom.lower()])

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

    async def analyze_clinical_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze clinical text for medical entities and insights
        """
        try:
            analysis = {
                "entities": [],
                "symptoms": [],
                "medications": [],
                "conditions": [],
                "procedures": [],
                "confidence_score": 0.0
            }

            # Extract medical entities (mock implementation)
            entities = await self._extract_medical_entities(text)
            analysis["entities"] = entities

            # Extract symptoms
            symptoms = await self._extract_symptoms(text)
            analysis["symptoms"] = symptoms

            # Extract medications
            medications = await self._extract_medications(text)
            analysis["medications"] = medications

            # Extract conditions
            conditions = await self._extract_conditions(text)
            analysis["conditions"] = conditions

            # Extract procedures
            procedures = await self._extract_procedures(text)
            analysis["procedures"] = procedures

            # Calculate confidence score
            analysis["confidence_score"] = self._calculate_confidence_score(analysis)

            return analysis

        except Exception as e:
            self.logger.error(f"Clinical text analysis failed: {e}")
            raise

    async def _extract_medical_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract medical entities from text"""

        # Mock entity extraction - in production, this would use NER models
        entities = []

        # Simple keyword-based extraction
        medical_keywords = {
            "fever": "SYMPTOM",
            "cough": "SYMPTOM",
            "headache": "SYMPTOM",
            "metformin": "MEDICATION",
            "lisinopril": "MEDICATION",
            "diabetes": "CONDITION",
            "hypertension": "CONDITION",
            "blood test": "PROCEDURE",
            "x-ray": "PROCEDURE"
        }

        text_lower = text.lower()
        for keyword, entity_type in medical_keywords.items():
            if keyword in text_lower:
                entities.append({
                    "text": keyword,
                    "type": entity_type,
                    "start_pos": text_lower.find(keyword),
                    "end_pos": text_lower.find(keyword) + len(keyword),
                    "confidence": 0.8
                })

        return entities

    async def _extract_symptoms(self, text: str) -> List[str]:
        """Extract symptoms from text"""

        symptoms = []
        text_lower = text.lower()

        symptom_keywords = [
            "fever", "cough", "headache", "fatigue", "nausea",
            "chest pain", "shortness of breath", "dizziness",
            "abdominal pain", "back pain", "joint pain"
        ]

        for symptom in symptom_keywords:
            if symptom in text_lower:
                symptoms.append(symptom)

        return symptoms

    async def _extract_medications(self, text: str) -> List[str]:
        """Extract medications from text"""

        medications = []
        text_lower = text.lower()

        medication_keywords = [
            "metformin", "lisinopril", "atorvastatin", "amlodipine",
            "aspirin", "ibuprofen", "acetaminophen", "warfarin"
        ]

        for medication in medication_keywords:
            if medication in text_lower:
                medications.append(medication)

        return medications

    async def _extract_conditions(self, text: str) -> List[str]:
        """Extract medical conditions from text"""

        conditions = []
        text_lower = text.lower()

        condition_keywords = [
            "diabetes", "hypertension", "hyperlipidemia", "asthma",
            "copd", "heart disease", "kidney disease", "liver disease"
        ]

        for condition in condition_keywords:
            if condition in text_lower:
                conditions.append(condition)

        return conditions

    async def _extract_procedures(self, text: str) -> List[str]:
        """Extract medical procedures from text"""

        procedures = []
        text_lower = text.lower()

        procedure_keywords = [
            "blood test", "x-ray", "ct scan", "mri", "ultrasound",
            "biopsy", "surgery", "endoscopy", "colonoscopy"
        ]

        for procedure in procedure_keywords:
            if procedure in text_lower:
                procedures.append(procedure)

        return procedures

    def _calculate_confidence_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for analysis"""

        # Simple confidence calculation based on entity count and types
        base_confidence = 0.5

        # Entity count factor
        total_entities = len(analysis["entities"])
        entity_factor = min(total_entities * 0.1, 0.3)

        # Entity type diversity factor
        entity_types = set(entity["type"] for entity in analysis["entities"])
        diversity_factor = min(len(entity_types) * 0.05, 0.2)

        confidence = base_confidence + entity_factor + diversity_factor

        return min(1.0, confidence)

    async def get_medical_literature(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search medical literature for clinical evidence
        """
        try:
            # Mock medical literature search - in production, this would use PubMed API
            literature_database = {
                "diabetes": [
                    {
                        "title": "Metformin for Type 2 Diabetes: A Systematic Review",
                        "authors": ["Smith J", "Johnson A", "Brown K"],
                        "journal": "Diabetes Care",
                        "year": 2023,
                        "abstract": "Systematic review of metformin efficacy in type 2 diabetes management...",
                        "evidence_level": "A",
                        "doi": "10.1000/diabetes.2023.001"
                    },
                    {
                        "title": "Lifestyle Interventions in Diabetes Prevention",
                        "authors": ["Davis M", "Wilson P", "Taylor R"],
                        "journal": "New England Journal of Medicine",
                        "year": 2022,
                        "abstract": "Randomized controlled trial of lifestyle interventions...",
                        "evidence_level": "A",
                        "doi": "10.1000/nejm.2022.001"
                    }
                ],
                "hypertension": [
                    {
                        "title": "ACE Inhibitors in Hypertension Management",
                        "authors": ["Anderson L", "Miller S", "Clark J"],
                        "journal": "Hypertension",
                        "year": 2023,
                        "abstract": "Meta-analysis of ACE inhibitor efficacy...",
                        "evidence_level": "A",
                        "doi": "10.1000/hypertension.2023.001"
                    }
                ]
            }

            # Search in literature database
            results = []
            query_lower = query.lower()

            for condition, publications in literature_database.items():
                if query_lower in condition.lower():
                    results.extend(publications)

                    if len(results) >= limit:
                        break

            return results[:limit]

        except Exception as e:
            self.logger.error(f"Medical literature search failed: {e}")
            raise

    async def get_clinical_decision_support(
        self,
        patient_data: Dict[str, Any],
        symptoms: List[str]
    ) -> Dict[str, Any]:
        """
        Get clinical decision support based on patient data and symptoms
        """
        try:
            decision_support = {
                "recommendations": [],
                "alerts": [],
                "guidelines": [],
                "evidence_summary": "",
                "confidence_level": "medium"
            }

            # Generate recommendations based on symptoms
            recommendations = await self._generate_symptom_recommendations(symptoms)
            decision_support["recommendations"] = recommendations

            # Generate alerts for concerning symptoms
            alerts = await self._generate_clinical_alerts(symptoms, patient_data)
            decision_support["alerts"] = alerts

            # Get relevant guidelines
            guidelines = await self._get_relevant_guidelines(symptoms)
            decision_support["guidelines"] = guidelines

            # Generate evidence summary
            evidence_summary = await self._generate_evidence_summary(symptoms)
            decision_support["evidence_summary"] = evidence_summary

            # Calculate confidence level
            decision_support["confidence_level"] = self._calculate_decision_confidence(
                symptoms, recommendations, guidelines
            )

            return decision_support

        except Exception as e:
            self.logger.error(f"Clinical decision support failed: {e}")
            raise

    async def _generate_symptom_recommendations(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """Generate recommendations based on symptoms"""

        recommendations = []

        for symptom in symptoms:
            symptom_lower = symptom.lower()

            if "fever" in symptom_lower:
                recommendations.append({
                    "symptom": symptom,
                    "recommendation": "Monitor temperature and seek care if >39°C or persistent >3 days",
                    "urgency": "medium",
                    "evidence_level": "B"
                })

            if "chest pain" in symptom_lower:
                recommendations.append({
                    "symptom": symptom,
                    "recommendation": "Seek immediate medical attention - rule out cardiac causes",
                    "urgency": "high",
                    "evidence_level": "A"
                })

            if "shortness of breath" in symptom_lower:
                recommendations.append({
                    "symptom": symptom,
                    "recommendation": "Seek medical attention - assess for respiratory or cardiac causes",
                    "urgency": "high",
                    "evidence_level": "A"
                })

            if "headache" in symptom_lower:
                recommendations.append({
                    "symptom": symptom,
                    "recommendation": "Monitor for red flag symptoms, consider pain management",
                    "urgency": "low",
                    "evidence_level": "B"
                })

        return recommendations

    async def _generate_clinical_alerts(
        self,
        symptoms: List[str],
        patient_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate clinical alerts for concerning symptoms"""

        alerts = []

        # Check for high-urgency symptoms
        high_urgency_symptoms = ["chest pain", "shortness of breath", "severe bleeding"]

        for symptom in symptoms:
            symptom_lower = symptom.lower()

            if any(urgent in symptom_lower for urgent in high_urgency_symptoms):
                alerts.append({
                    "type": "high_urgency",
                    "symptom": symptom,
                    "message": f"High-urgency symptom: {symptom}",
                    "action": "Seek immediate medical attention",
                    "severity": "high"
                })

        # Check for age-related alerts
        age = patient_data.get("age", 0)
        if age > 65:
            for symptom in symptoms:
                if "fever" in symptom.lower():
                    alerts.append({
                        "type": "age_related",
                        "symptom": symptom,
                        "message": "Fever in elderly patient",
                        "action": "Monitor closely, consider lower threshold for intervention",
                        "severity": "medium"
                    })

        return alerts

    async def _get_relevant_guidelines(self, symptoms: List[str]) -> List[Dict[str, Any]]:
        """Get relevant clinical guidelines for symptoms"""

        guidelines = []

        # Mock guidelines mapping
        guidelines_mapping = {
            "fever": "Fever management guidelines",
            "cough": "Respiratory infection guidelines",
            "chest pain": "Chest pain evaluation guidelines",
            "headache": "Headache management guidelines"
        }

        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for key, guideline in guidelines_mapping.items():
                if key in symptom_lower:
                    guidelines.append({
                        "symptom": symptom,
                        "guideline": guideline,
                        "source": "NICE Guidelines",
                        "evidence_level": "A"
                    })

        return guidelines

    async def _generate_evidence_summary(self, symptoms: List[str]) -> str:
        """Generate evidence summary for symptoms"""

        if not symptoms:
            return "No symptoms provided for analysis"

        summary = f"Evidence-based analysis for {len(symptoms)} symptom(s): "

        symptom_summaries = []
        for symptom in symptoms:
            symptom_lower = symptom.lower()

            if "fever" in symptom_lower:
                symptom_summaries.append("Fever: Evidence supports monitoring and antipyretics for comfort")
            elif "cough" in symptom_lower:
                symptom_summaries.append("Cough: Evidence supports symptomatic treatment and monitoring")
            elif "chest pain" in symptom_lower:
                symptom_summaries.append("Chest pain: Evidence supports immediate evaluation for cardiac causes")
            elif "headache" in symptom_lower:
                symptom_summaries.append("Headache: Evidence supports pain management and monitoring for red flags")
            else:
                symptom_summaries.append(f"{symptom}: Standard clinical evaluation recommended")

        summary += "; ".join(symptom_summaries)
        summary += ". Consult clinical guidelines for specific recommendations."

        return summary

    def _calculate_decision_confidence(
        self,
        symptoms: List[str],
        recommendations: List[Dict[str, Any]],
        guidelines: List[Dict[str, Any]]
    ) -> str:
        """Calculate confidence level for clinical decisions"""

        # Simple confidence calculation
        if len(symptoms) >= 3 and len(recommendations) >= 2 and len(guidelines) >= 1:
            return "high"
        elif len(symptoms) >= 2 and len(recommendations) >= 1:
            return "medium"
        else:
            return "low"





