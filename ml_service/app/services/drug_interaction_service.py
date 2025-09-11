import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class DrugInteractionService:
    """
    Service for checking drug interactions and providing recommendations
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.interaction_database = self._load_interaction_database()

    def _load_interaction_database(self) -> Dict[str, Any]:
        """Load drug interaction database (simplified for demo)"""
        # In production, this would load from DrugBank, SIDER, or other sources
        return {
            "warfarin": {
                "interactions": {
                    "aspirin": {"type": "major", "severity": "high", "description": "Increased bleeding risk"},
                    "ibuprofen": {"type": "moderate", "severity": "medium", "description": "Increased bleeding risk"},
                    "vitamin_k": {"type": "moderate", "severity": "medium", "description": "Reduced anticoagulant effect"}
                }
            },
            "digoxin": {
                "interactions": {
                    "furosemide": {"type": "moderate", "severity": "medium", "description": "Increased digoxin toxicity risk"},
                    "amiodarone": {"type": "major", "severity": "high", "description": "Increased digoxin levels"}
                }
            },
            "metformin": {
                "interactions": {
                    "alcohol": {"type": "moderate", "severity": "medium", "description": "Increased lactic acidosis risk"},
                    "furosemide": {"type": "minor", "severity": "low", "description": "Reduced metformin effectiveness"}
                }
            }
        }

    async def check_interactions(
        self,
        drug_ids: List[str],
        drug_info: Dict[str, Any],
        patient_age: Optional[int] = None,
        patient_weight: Optional[float] = None,
        patient_conditions: Optional[List[str]] = None,
        include_over_the_counter: bool = True,
        include_herbal_supplements: bool = True
    ) -> Dict[str, Any]:
        """
        Check for drug interactions between multiple medications
        """
        try:
            analysis_id = str(uuid.uuid4())
            self.logger.info(f"Starting drug interaction analysis {analysis_id} for {len(drug_ids)} drugs")

            interactions = []
            monitoring_required = False
            monitoring_parameters = []

            # Check pairwise interactions
            for i, drug1_id in enumerate(drug_ids):
                for j, drug2_id in enumerate(drug_ids):
                    if i < j:  # Avoid duplicate checks
                        interaction = await self._check_pairwise_interaction(
                            drug1_id, drug2_id, drug_info
                        )
                        if interaction:
                            interactions.append(interaction)

                            # Check if monitoring is required
                            if interaction["severity"] in ["high", "critical"]:
                                monitoring_required = True
                                monitoring_parameters.extend(
                                    self._get_monitoring_parameters(interaction)
                                )

            # Check for contraindications based on patient conditions
            contraindications = await self._check_contraindications(
                drug_ids, patient_conditions
            )

            # Calculate overall risk
            overall_risk = self._calculate_overall_risk(interactions)

            # Generate recommendations
            recommendations = self._generate_recommendations(interactions, overall_risk)

            result = {
                "analysis_id": analysis_id,
                "interactions": interactions,
                "contraindications": contraindications,
                "overall_risk": overall_risk,
                "monitoring_required": monitoring_required,
                "monitoring_parameters": list(set(monitoring_parameters)),  # Remove duplicates
                "analysis_timestamp": datetime.now().isoformat()
            }

            self.logger.info(f"Drug interaction analysis {analysis_id} completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Drug interaction analysis failed: {e}")
            raise

    async def _check_pairwise_interaction(
        self,
        drug1_id: str,
        drug2_id: str,
        drug_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Check for interaction between two specific drugs"""

        # Get drug names from drug_info
        drug1_name = drug_info.get(drug1_id, {}).get("name", drug1_id)
        drug2_name = drug_info.get(drug2_id, {}).get("name", drug2_id)

        # Check interaction database
        interaction = None

        # Check if drug1 has interactions with drug2
        if drug1_id in self.interaction_database:
            if drug2_id in self.interaction_database[drug1_id]["interactions"]:
                interaction_data = self.interaction_database[drug1_id]["interactions"][drug2_id]
                interaction = {
                    "drug1_id": drug1_id,
                    "drug1_name": drug1_name,
                    "drug2_id": drug2_id,
                    "drug2_name": drug2_name,
                    "interaction_type": interaction_data["type"],
                    "severity": interaction_data["severity"],
                    "description": interaction_data["description"],
                    "clinical_significance": self._get_clinical_significance(interaction_data["type"]),
                    "management": self._get_management_strategy(interaction_data["type"], interaction_data["severity"]),
                    "evidence_level": self._get_evidence_level(interaction_data["type"]),
                    "references": ["DrugBank", "SIDER Database"]
                }

        # Check if drug2 has interactions with drug1 (reverse check)
        elif drug2_id in self.interaction_database:
            if drug1_id in self.interaction_database[drug2_id]["interactions"]:
                interaction_data = self.interaction_database[drug2_id]["interactions"][drug1_id]
                interaction = {
                    "drug1_id": drug1_id,
                    "drug1_name": drug1_name,
                    "drug2_id": drug2_id,
                    "drug2_name": drug2_name,
                    "interaction_type": interaction_data["type"],
                    "severity": interaction_data["severity"],
                    "description": interaction_data["description"],
                    "clinical_significance": self._get_clinical_significance(interaction_data["type"]),
                    "management": self._get_management_strategy(interaction_data["type"], interaction_data["severity"]),
                    "evidence_level": self._get_evidence_level(interaction_data["type"]),
                    "references": ["DrugBank", "SIDER Database"]
                }

        return interaction

    async def _check_contraindications(
        self,
        drug_ids: List[str],
        patient_conditions: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """Check for contraindications based on patient conditions"""

        contraindications = []

        if not patient_conditions:
            return contraindications

        # Simplified contraindication rules
        contraindication_rules = {
            "warfarin": ["bleeding_disorders", "peptic_ulcer", "recent_surgery"],
            "metformin": ["kidney_disease", "liver_disease", "heart_failure"],
            "digoxin": ["heart_block", "kidney_disease"],
            "furosemide": ["dehydration", "electrolyte_imbalance"]
        }

        for drug_id in drug_ids:
            if drug_id in contraindication_rules:
                for condition in patient_conditions:
                    if condition in contraindication_rules[drug_id]:
                        contraindications.append({
                            "drug_id": drug_id,
                            "condition": condition,
                            "severity": "high",
                            "recommendation": f"Consider alternative to {drug_id} due to {condition}"
                        })

        return contraindications

    def _get_clinical_significance(self, interaction_type: str) -> str:
        """Get clinical significance description for interaction type"""
        significance_map = {
            "contraindicated": "Drugs should not be used together",
            "major": "Significant clinical impact, requires close monitoring",
            "moderate": "Moderate clinical impact, monitor for adverse effects",
            "minor": "Minimal clinical impact, routine monitoring sufficient",
            "none": "No known interaction"
        }
        return significance_map.get(interaction_type, "Unknown significance")

    def _get_management_strategy(self, interaction_type: str, severity: str) -> str:
        """Get management strategy for drug interaction"""
        if interaction_type == "contraindicated":
            return "Avoid combination, use alternative therapy"
        elif severity == "high":
            return "Close monitoring required, consider dose adjustment"
        elif severity == "medium":
            return "Monitor for adverse effects, adjust if necessary"
        elif severity == "low":
            return "Routine monitoring sufficient"
        else:
            return "No special monitoring required"

    def _get_evidence_level(self, interaction_type: str) -> str:
        """Get evidence level for interaction"""
        evidence_map = {
            "contraindicated": "A",
            "major": "B",
            "moderate": "C",
            "minor": "D",
            "none": "X"
        }
        return evidence_map.get(interaction_type, "D")

    def _get_monitoring_parameters(self, interaction: Dict[str, Any]) -> List[str]:
        """Get monitoring parameters for drug interaction"""
        monitoring_params = []

        # Add general monitoring parameters
        monitoring_params.append("Adverse effects monitoring")
        monitoring_params.append("Efficacy monitoring")

        # Add specific monitoring based on interaction type
        if "bleeding" in interaction["description"].lower():
            monitoring_params.extend([
                "Complete blood count (CBC)",
                "International normalized ratio (INR)",
                "Bleeding time"
            ])

        if "cardiac" in interaction["description"].lower():
            monitoring_params.extend([
                "Electrocardiogram (ECG)",
                "Heart rate monitoring",
                "Blood pressure monitoring"
            ])

        if "kidney" in interaction["description"].lower():
            monitoring_params.extend([
                "Serum creatinine",
                "Blood urea nitrogen (BUN)",
                "Electrolyte levels"
            ])

        return monitoring_params

    def _calculate_overall_risk(self, interactions: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level based on interactions"""
        if not interactions:
            return "low"

        risk_scores = {
            "critical": 4,
            "high": 3,
            "medium": 2,
            "low": 1,
            "none": 0
        }

        total_score = sum(risk_scores.get(interaction["severity"], 0) for interaction in interactions)
        avg_score = total_score / len(interactions)

        if avg_score >= 3.5:
            return "critical"
        elif avg_score >= 2.5:
            return "high"
        elif avg_score >= 1.5:
            return "medium"
        else:
            return "low"

    def calculate_risk_score(self, interactions: List[Dict[str, Any]]) -> float:
        """Calculate numerical risk score (0.0 to 1.0)"""
        if not interactions:
            return 0.0

        risk_scores = {
            "critical": 1.0,
            "high": 0.8,
            "medium": 0.5,
            "low": 0.2,
            "none": 0.0
        }

        total_score = sum(risk_scores.get(interaction["severity"], 0) for interaction in interactions)
        avg_score = total_score / len(interactions)

        return min(1.0, avg_score)

    def generate_recommendations(
        self,
        interactions: List[Dict[str, Any]],
        overall_risk: str
    ) -> List[str]:
        """Generate recommendations based on interactions and risk level"""

        recommendations = []

        # General recommendations
        if interactions:
            recommendations.append("Review all medications for potential interactions")
            recommendations.append("Consider alternative medications if high-risk interactions exist")

        # Risk-specific recommendations
        if overall_risk == "critical":
            recommendations.extend([
                "Immediate medical review required",
                "Consider discontinuing one or more medications",
                "Implement intensive monitoring protocols"
            ])
        elif overall_risk == "high":
            recommendations.extend([
                "Close monitoring required",
                "Consider dose adjustments",
                "Monitor for adverse effects"
            ])
        elif overall_risk == "medium":
            recommendations.extend([
                "Regular monitoring recommended",
                "Be aware of potential adverse effects",
                "Consider alternative timing of medications"
            ])

        # Interaction-specific recommendations
        for interaction in interactions:
            if interaction["severity"] in ["high", "critical"]:
                recommendations.append(
                    f"Monitor for {interaction['description']} between {interaction['drug1_name']} and {interaction['drug2_name']}"
                )

        return recommendations

    async def find_alternative_drugs(
        self,
        drug_ids: List[str],
        patient_conditions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Find alternative drugs with fewer interactions"""

        # Simplified alternative drug suggestions
        alternatives = {
            "warfarin": ["dabigatran", "rivaroxaban", "apixaban"],
            "digoxin": ["beta_blockers", "calcium_channel_blockers"],
            "metformin": ["sulfonylureas", "dpp4_inhibitors", "glp1_agonists"]
        }

        alternative_suggestions = []

        for drug_id in drug_ids:
            if drug_id in alternatives:
                for alt_drug in alternatives[drug_id]:
                    alternative_suggestions.append({
                        "original_drug": drug_id,
                        "alternative_drug": alt_drug,
                        "rationale": f"Lower interaction profile than {drug_id}",
                        "considerations": "Consult with healthcare provider before switching"
                    })

        return alternative_suggestions

    async def get_drug_interactions(self, drug_id: str) -> List[Dict[str, Any]]:
        """Get all known interactions for a specific drug"""

        if drug_id not in self.interaction_database:
            return []

        interactions = []
        drug_interactions = self.interaction_database[drug_id]["interactions"]

        for other_drug, interaction_data in drug_interactions.items():
            interactions.append({
                "drug1_id": drug_id,
                "drug2_id": other_drug,
                "interaction_type": interaction_data["type"],
                "severity": interaction_data["severity"],
                "description": interaction_data["description"]
            })

        return interactions

    async def get_contraindicated_drugs(self, condition: str) -> List[Dict[str, Any]]:
        """Get drugs that are contraindicated for a specific condition"""

        contraindicated_drugs = []

        # Simplified contraindication database
        contraindication_db = {
            "bleeding_disorders": ["warfarin", "aspirin", "clopidogrel"],
            "kidney_disease": ["metformin", "furosemide", "digoxin"],
            "liver_disease": ["metformin", "statins", "acetaminophen"],
            "heart_disease": ["decongestants", "stimulants"]
        }

        if condition in contraindication_db:
            for drug in contraindication_db[condition]:
                contraindicated_drugs.append({
                    "drug_id": drug,
                    "condition": condition,
                    "severity": "high",
                    "rationale": f"Contraindicated in patients with {condition}"
                })

        return contraindicated_drugs







