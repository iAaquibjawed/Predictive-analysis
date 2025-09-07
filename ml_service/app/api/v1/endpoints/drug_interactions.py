from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from app.core.security import get_current_user, require_roles
from app.services.drug_interaction_service import DrugInteractionService
from app.services.drugbank_service import DrugBankService

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response
class DrugInteractionRequest(BaseModel):
    drug_ids: List[str]
    patient_age: Optional[int] = None
    patient_weight: Optional[float] = None
    patient_conditions: Optional[List[str]] = None
    include_over_the_counter: bool = True
    include_herbal_supplements: bool = True

class DrugInteraction(BaseModel):
    drug1_id: str
    drug1_name: str
    drug2_id: str
    drug2_name: str
    interaction_type: str  # contraindicated, major, moderate, minor, none
    severity: str  # high, medium, low
    description: str
    clinical_significance: str
    management: str
    evidence_level: str  # A, B, C, D, X
    references: List[str]

class DrugInteractionResponse(BaseModel):
    analysis_id: str
    interactions: List[DrugInteraction]
    risk_score: float  # 0.0 to 1.0
    overall_risk: str  # low, medium, high, critical
    recommendations: List[str]
    alternative_drugs: List[Dict[str, Any]]
    monitoring_required: bool
    monitoring_parameters: List[str]

@router.post("/drug_interactions", response_model=DrugInteractionResponse)
async def check_drug_interactions(
    request: DrugInteractionRequest,
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "pharmacist", "admin"]))
):
    """
    Check for drug interactions between multiple medications
    """
    try:
        logger.info(f"Drug interaction check requested by user {current_user['user_id']} for {len(request.drug_ids)} drugs")

        # Initialize services
        interaction_service = DrugInteractionService()
        drugbank_service = DrugBankService()

        # Get drug information from DrugBank
        drug_info = await drugbank_service.get_drugs_info(request.drug_ids)

        # Check for interactions
        interactions_result = await interaction_service.check_interactions(
            drug_ids=request.drug_ids,
            drug_info=drug_info,
            patient_age=request.patient_age,
            patient_weight=request.patient_weight,
            patient_conditions=request.patient_conditions,
            include_over_the_counter=request.include_over_the_counter,
            include_herbal_supplements=request.include_herbal_supplements
        )

        # Calculate overall risk score
        risk_score = interaction_service.calculate_risk_score(interactions_result["interactions"])

        # Generate recommendations
        recommendations = interaction_service.generate_recommendations(
            interactions_result["interactions"],
            risk_score
        )

        # Find alternative drugs if needed
        alternative_drugs = []
        if risk_score > 0.7:  # High risk threshold
            alternative_drugs = await interaction_service.find_alternative_drugs(
                request.drug_ids,
                patient_conditions=request.patient_conditions
            )

        response = DrugInteractionResponse(
            analysis_id=interactions_result["analysis_id"],
            interactions=interactions_result["interactions"],
            risk_score=risk_score,
            overall_risk=interactions_result["overall_risk"],
            recommendations=recommendations,
            alternative_drugs=alternative_drugs,
            monitoring_required=interactions_result["monitoring_required"],
            monitoring_parameters=interactions_result["monitoring_parameters"]
        )

        logger.info(f"Drug interaction check completed successfully for user {current_user['user_id']}")
        return response

    except Exception as e:
        logger.error(f"Drug interaction check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Drug interaction check failed: {str(e)}"
        )

@router.get("/drug_interactions/{drug_id}")
async def get_drug_interactions(
    drug_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get all known interactions for a specific drug
    """
    try:
        interaction_service = DrugInteractionService()
        drugbank_service = DrugBankService()

        # Get drug information
        drug_info = await drugbank_service.get_drug_info(drug_id)

        # Get all interactions for this drug
        interactions = await interaction_service.get_drug_interactions(drug_id)

        return {
            "drug": drug_info,
            "interactions": interactions
        }

    except Exception as e:
        logger.error(f"Failed to get drug interactions for {drug_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get drug interactions: {str(e)}"
        )

@router.post("/drug_interactions/batch")
async def batch_drug_interaction_check(
    requests: List[DrugInteractionRequest],
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "pharmacist", "admin"]))
):
    """
    Batch check multiple drug interaction scenarios
    """
    try:
        logger.info(f"Batch drug interaction check requested by user {current_user['user_id']} for {len(requests)} scenarios")

        interaction_service = DrugInteractionService()
        results = []

        for request in requests:
            try:
                result = await check_drug_interactions(request, current_user)
                results.append(result)
            except Exception as e:
                results.append({
                    "error": str(e),
                    "request": request.dict()
                })

        return {"results": results}

    except Exception as e:
        logger.error(f"Batch drug interaction check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch drug interaction check failed: {str(e)}"
        )

@router.get("/drug_interactions/contraindications/{condition}")
async def get_contraindicated_drugs(
    condition: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get drugs that are contraindicated for a specific medical condition
    """
    try:
        interaction_service = DrugInteractionService()
        contraindicated_drugs = await interaction_service.get_contraindicated_drugs(condition)

        return {
            "condition": condition,
            "contraindicated_drugs": contraindicated_drugs
        }

    except Exception as e:
        logger.error(f"Failed to get contraindicated drugs for {condition}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get contraindicated drugs: {str(e)}"
        )

