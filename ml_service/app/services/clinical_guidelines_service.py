import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

class ClinicalGuidelinesService:
    """
    Service for accessing clinical guidelines and best practices
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.base_url = "https://api.nice.org.uk"  # NICE Guidelines API
        self.api_key = None  # In production, this would be loaded from environment
        self.cache = {}  # Simple cache for demo purposes

        # Initialize guidelines database
        self._init_guidelines_database()

    def _init_guidelines_database(self):
        """Initialize the clinical guidelines database"""

        self.guidelines_database = {
            "diabetes": {
                "type_2_diabetes": {
                    "title": "Type 2 diabetes in adults: management",
                    "guideline_id": "NG28",
                    "version": "2023",
                    "source": "NICE",
                    "evidence_level": "A",
                    "summary": "Management of type 2 diabetes in adults including lifestyle, pharmacological and surgical interventions",
                    "key_recommendations": [
                        "Start metformin as first-line therapy",
                        "Target HbA1c of 6.5% (48 mmol/mol)",
                        "Monitor blood glucose regularly",
                        "Lifestyle modifications should be initiated at diagnosis",
                        "Consider cardiovascular risk factors"
                    ],
                    "pharmacological_treatments": [
                        {
                            "drug": "Metformin",
                            "dose": "500mg twice daily, titrate to 2g daily",
                            "evidence": "Level A",
                            "notes": "First-line therapy, monitor renal function"
                        },
                        {
                            "drug": "Sulfonylurea",
                            "dose": "Variable based on agent",
                            "evidence": "Level A",
                            "notes": "Second-line if metformin contraindicated"
                        },
                        {
                            "drug": "DPP-4 inhibitor",
                            "dose": "Variable based on agent",
                            "evidence": "Level B",
                            "notes": "Consider if metformin not tolerated"
                        }
                    ],
                    "monitoring": [
                        "HbA1c every 3-6 months",
                        "Blood glucose monitoring",
                        "Annual renal function",
                        "Annual eye examination",
                        "Annual foot examination"
                    ],
                    "complications_screening": [
                        "Retinopathy screening",
                        "Nephropathy screening",
                        "Neuropathy screening",
                        "Cardiovascular risk assessment"
                    ]
                },
                "diabetes_prevention": {
                    "title": "Preventing type 2 diabetes",
                    "guideline_id": "NG38",
                    "version": "2022",
                    "source": "NICE",
                    "evidence_level": "A",
                    "summary": "Risk identification and prevention of type 2 diabetes",
                    "key_recommendations": [
                        "Identify high-risk individuals",
                        "Lifestyle interventions for prevention",
                        "Regular monitoring of high-risk patients",
                        "Consider metformin for very high-risk patients"
                    ]
                }
            },
            "hypertension": {
                "hypertension_management": {
                    "title": "Hypertension in adults: diagnosis and management",
                    "guideline_id": "NG136",
                    "version": "2023",
                    "source": "NICE",
                    "evidence_level": "A",
                    "summary": "Diagnosis and management of hypertension in adults",
                    "key_recommendations": [
                        "Lifestyle modifications first",
                        "ACE inhibitors or calcium channel blockers as first-line",
                        "Target BP <140/90 mmHg",
                        "Regular monitoring",
                        "Consider combination therapy if needed"
                    ],
                    "pharmacological_treatments": [
                        {
                            "drug": "ACE inhibitor",
                            "dose": "Variable based on agent",
                            "evidence": "Level A",
                            "notes": "First-line therapy, monitor renal function"
                        },
                        {
                            "drug": "Calcium channel blocker",
                            "dose": "Variable based on agent",
                            "evidence": "Level A",
                            "notes": "Alternative first-line therapy"
                        },
                        {
                            "drug": "Thiazide diuretic",
                            "dose": "Variable based on agent",
                            "evidence": "Level B",
                            "notes": "Second-line or combination therapy"
                        }
                    ],
                    "monitoring": [
                        "Blood pressure monitoring",
                        "Renal function monitoring",
                        "Electrolyte monitoring",
                        "Regular cardiovascular assessment"
                    ]
                }
            },
            "hyperlipidemia": {
                "cardiovascular_risk": {
                    "title": "Cardiovascular disease: risk assessment and reduction",
                    "guideline_id": "NG181",
                    "version": "2023",
                    "source": "NICE",
                    "evidence_level": "A",
                    "summary": "Assessment and reduction of cardiovascular risk",
                    "key_recommendations": [
                        "Statins for primary prevention",
                        "Target LDL-C reduction of 40%",
                        "Regular lipid monitoring",
                        "Lifestyle modifications",
                        "Risk stratification using QRISK2"
                    ],
                    "pharmacological_treatments": [
                        {
                            "drug": "Atorvastatin",
                            "dose": "20mg daily",
                            "evidence": "Level A",
                            "notes": "First-line therapy for primary prevention"
                        },
                        {
                            "drug": "Simvastatin",
                            "dose": "40mg daily",
                            "evidence": "Level B",
                            "notes": "Alternative first-line therapy"
                        }
                    ],
                    "monitoring": [
                        "Lipid profile monitoring",
                        "Liver function monitoring",
                        "Muscle symptoms monitoring",
                        "Regular cardiovascular assessment"
                    ]
                }
            },
            "asthma": {
                "asthma_management": {
                    "title": "Asthma: diagnosis, monitoring and chronic asthma management",
                    "guideline_id": "NG80",
                    "version": "2023",
                    "source": "NICE",
                    "evidence_level": "A",
                    "summary": "Diagnosis and management of chronic asthma",
                    "key_recommendations": [
                        "Inhaled corticosteroids as first-line",
                        "Add long-acting beta agonists if needed",
                        "Regular monitoring of symptoms",
                        "Personal asthma action plan",
                        "Avoid triggers"
                    ],
                    "pharmacological_treatments": [
                        {
                            "drug": "Inhaled corticosteroid",
                            "dose": "Variable based on severity",
                            "evidence": "Level A",
                            "notes": "First-line controller therapy"
                        },
                        {
                            "drug": "Long-acting beta agonist",
                            "dose": "Variable based on agent",
                            "evidence": "Level A",
                            "notes": "Add-on therapy if ICS insufficient"
                        }
                    ]
                }
            },
            "copd": {
                "copd_management": {
                    "title": "Chronic obstructive pulmonary disease in over 16s: diagnosis and management",
                    "guideline_id": "NG115",
                    "version": "2023",
                    "source": "NICE",
                    "evidence_level": "A",
                    "summary": "Diagnosis and management of COPD",
                    "key_recommendations": [
                        "Smoking cessation support",
                        "Inhaled bronchodilators",
                        "Pulmonary rehabilitation",
                        "Regular monitoring",
                        "Vaccination"
                    ]
                }
            }
        }

    async def get_guidelines(
        self,
        condition: str,
        guideline_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get clinical guidelines for a specific condition
        """
        try:
            condition_lower = condition.lower()

            if condition_lower not in self.guidelines_database:
                return []

            condition_guidelines = self.guidelines_database[condition_lower]

            if guideline_type:
                # Return specific guideline type
                if guideline_type in condition_guidelines:
                    return [condition_guidelines[guideline_type]]
                else:
                    return []
            else:
                # Return all guidelines for the condition
                return list(condition_guidelines.values())

        except Exception as e:
            self.logger.error(f"Failed to get guidelines for {condition}: {e}")
            raise

    async def search_guidelines(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search clinical guidelines by query
        """
        try:
            results = []
            query_lower = query.lower()

            for condition, guidelines in self.guidelines_database.items():
                for guideline_type, guideline_data in guidelines.items():
                    # Search in title, summary, and key recommendations
                    searchable_text = (
                        guideline_data.get("title", "") +
                        " " + guideline_data.get("summary", "") +
                        " " + " ".join(guideline_data.get("key_recommendations", []))
                    ).lower()

                    if query_lower in searchable_text:
                        results.append({
                            "condition": condition,
                            "guideline_type": guideline_type,
                            **guideline_data
                        })

                        if len(results) >= limit:
                            break

                if len(results) >= limit:
                    break

            return results

        except Exception as e:
            self.logger.error(f"Guideline search failed: {e}")
            raise

    async def get_treatment_recommendations(
        self,
        condition: str,
        guideline_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get treatment recommendations from clinical guidelines
        """
        try:
            guidelines = await self.get_guidelines(condition, guideline_type)

            treatments = []
            for guideline in guidelines:
                if "pharmacological_treatments" in guideline:
                    treatments.extend(guideline["pharmacological_treatments"])

            return treatments

        except Exception as e:
            self.logger.error(f"Failed to get treatment recommendations: {e}")
            raise

    async def get_monitoring_recommendations(
        self,
        condition: str,
        guideline_type: Optional[str] = None
    ) -> List[str]:
        """
        Get monitoring recommendations from clinical guidelines
        """
        try:
            guidelines = await self.get_guidelines(condition, guideline_type)

            monitoring = []
            for guideline in guidelines:
                if "monitoring" in guideline:
                    monitoring.extend(guideline["monitoring"])

            return monitoring

        except Exception as e:
            self.logger.error(f"Failed to get monitoring recommendations: {e}")
            raise

    async def get_evidence_levels(
        self,
        condition: str,
        guideline_type: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Get evidence levels for clinical guidelines
        """
        try:
            guidelines = await self.get_guidelines(condition, guideline_type)

            evidence_levels = {}
            for guideline in guidelines:
                evidence_levels[guideline.get("title", "Unknown")] = guideline.get("evidence_level", "Unknown")

            return evidence_levels

        except Exception as e:
            self.logger.error(f"Failed to get evidence levels: {e}")
            raise

    async def get_guideline_updates(
        self,
        since_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recently updated clinical guidelines
        """
        try:
            updates = []

            for condition, guidelines in self.guidelines_database.items():
                for guideline_type, guideline_data in guidelines.items():
                    # Mock update date - in production, this would be real
                    update_date = datetime(2023, 1, 1)  # Mock date

                    if since_date is None or update_date >= since_date:
                        updates.append({
                            "condition": condition,
                            "guideline_type": guideline_type,
                            "title": guideline_data.get("title"),
                            "update_date": update_date,
                            "version": guideline_data.get("version")
                        })

            # Sort by update date (newest first)
            updates.sort(key=lambda x: x["update_date"], reverse=True)

            return updates

        except Exception as e:
            self.logger.error(f"Failed to get guideline updates: {e}")
            raise

    async def validate_treatment_plan(
        self,
        condition: str,
        treatments: List[str],
        patient_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a treatment plan against clinical guidelines
        """
        try:
            validation_result = {
                "is_valid": True,
                "warnings": [],
                "recommendations": [],
                "evidence_level": "Unknown",
                "guideline_compliance": 0.0
            }

            # Get relevant guidelines
            guidelines = await self.get_guidelines(condition)

            if not guidelines:
                validation_result["is_valid"] = False
                validation_result["warnings"].append("No clinical guidelines found for this condition")
                return validation_result

            # Check treatment compliance
            recommended_treatments = []
            for guideline in guidelines:
                if "pharmacological_treatments" in guideline:
                    recommended_treatments.extend([
                        treatment["drug"].lower()
                        for treatment in guideline["pharmacological_treatments"]
                    ])

            # Calculate compliance
            if recommended_treatments:
                treatment_lower = [t.lower() for t in treatments]
                matches = sum(1 for t in treatment_lower if any(rt in t for rt in recommended_treatments))
                validation_result["guideline_compliance"] = matches / len(treatments) if treatments else 0.0

            # Check for warnings
            if validation_result["guideline_compliance"] < 0.5:
                validation_result["warnings"].append("Treatment plan has low compliance with clinical guidelines")

            # Get evidence level
            if guidelines:
                validation_result["evidence_level"] = guidelines[0].get("evidence_level", "Unknown")

            # Generate recommendations
            if validation_result["guideline_compliance"] < 1.0:
                validation_result["recommendations"].append("Consider reviewing treatment plan against clinical guidelines")

            return validation_result

        except Exception as e:
            self.logger.error(f"Treatment plan validation failed: {e}")
            raise

    async def get_condition_specific_guidelines(
        self,
        condition: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive guidelines for a specific condition
        """
        try:
            condition_lower = condition.lower()

            if condition_lower not in self.guidelines_database:
                return {}

            condition_guidelines = self.guidelines_database[condition_lower]

            # Compile comprehensive information
            comprehensive_guidelines = {
                "condition": condition,
                "guidelines": condition_guidelines,
                "summary": {
                    "total_guidelines": len(condition_guidelines),
                    "evidence_levels": list(set(
                        g.get("evidence_level", "Unknown")
                        for g in condition_guidelines.values()
                    )),
                    "sources": list(set(
                        g.get("source", "Unknown")
                        for g in condition_guidelines.values()
                    ))
                }
            }

            return comprehensive_guidelines

        except Exception as e:
            self.logger.error(f"Failed to get comprehensive guidelines: {e}")
            raise

    async def get_guideline_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about available clinical guidelines
        """
        try:
            metadata = {
                "total_conditions": len(self.guidelines_database),
                "total_guidelines": sum(
                    len(guidelines) for guidelines in self.guidelines_database.values()
                ),
                "conditions": list(self.guidelines_database.keys()),
                "sources": ["NICE", "ADA", "ESC"],  # Mock sources
                "last_updated": datetime.now().isoformat(),
                "coverage": {
                    "diabetes": "Comprehensive",
                    "hypertension": "Comprehensive",
                    "hyperlipidemia": "Comprehensive",
                    "asthma": "Moderate",
                    "copd": "Basic"
                }
            }

            return metadata

        except Exception as e:
            self.logger.error(f"Failed to get guideline metadata: {e}")
            raise

    async def compare_guidelines(
        self,
        condition: str,
        guideline_types: List[str]
    ) -> Dict[str, Any]:
        """
        Compare multiple guidelines for the same condition
        """
        try:
            comparison = {
                "condition": condition,
                "guidelines": {},
                "differences": [],
                "similarities": [],
                "recommendations": []
            }

            # Get guidelines for comparison
            for guideline_type in guideline_types:
                guidelines = await self.get_guidelines(condition, guideline_type)
                if guidelines:
                    comparison["guidelines"][guideline_type] = guidelines[0]

            if len(comparison["guidelines"]) < 2:
                comparison["recommendations"].append("Need at least 2 guidelines for comparison")
                return comparison

            # Find differences and similarities
            guideline_list = list(comparison["guidelines"].values())

            # Compare key recommendations
            all_recommendations = set()
            for guideline in guideline_list:
                if "key_recommendations" in guideline:
                    all_recommendations.update(guideline["key_recommendations"])

            # Find common recommendations
            common_recommendations = set()
            for guideline in guideline_list:
                if "key_recommendations" in guideline:
                    if not common_recommendations:
                        common_recommendations = set(guideline["key_recommendations"])
                    else:
                        common_recommendations &= set(guideline["key_recommendations"])

            comparison["similarities"] = list(common_recommendations)
            comparison["differences"] = list(all_recommendations - common_recommendations)

            # Generate recommendations
            if comparison["similarities"]:
                comparison["recommendations"].append("Strong consensus on common recommendations")

            if comparison["differences"]:
                comparison["recommendations"].append("Consider differences when making clinical decisions")

            return comparison

        except Exception as e:
            self.logger.error(f"Guideline comparison failed: {e}")
            raise







