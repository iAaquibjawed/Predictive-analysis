from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from app.core.security import get_current_user, require_roles
from app.services.recommendation_service import RecommendationService
from app.services.clinical_guidelines_service import ClinicalGuidelinesService
from app.services.literature_service import LiteratureService
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response
class PatientData(BaseModel):
    patient_id: str
    age: int
    gender: str
    weight: Optional[float] = None
    height: Optional[float] = None
    symptoms: List[str]
    medical_history: List[str]
    current_medications: List[str]
    allergies: List[str]
    vital_signs: Optional[Dict[str, float]] = None
    lab_results: Optional[Dict[str, Any]] = None
    imaging_results: Optional[Dict[str, Any]] = None

class TreatmentRecommendation(BaseModel):
    recommendation_id: str
    condition: str
    confidence_score: float
    treatment_options: List[Dict[str, Any]]
    recommended_treatment: Dict[str, Any]
    alternative_treatments: List[Dict[str, Any]]
    contraindications: List[str]
    monitoring_requirements: List[str]
    follow_up_schedule: Dict[str, Any]
    evidence_level: str  # A, B, C, D, X
    supporting_evidence: List[Dict[str, Any]]

class ClinicalDecision(BaseModel):
    decision_id: str
    patient_id: str
    decision_type: str  # diagnosis, treatment, monitoring, referral
    primary_recommendation: str
    confidence_score: float
    reasoning: str
    alternatives: List[str]
    risks: List[str]
    benefits: List[str]
    clinical_guidelines: List[Dict[str, Any]]
    literature_references: List[Dict[str, Any]]

class RecommendationsResponse(BaseModel):
    patient_id: str
    generated_at: datetime
    primary_diagnosis: str
    treatment_recommendations: List[TreatmentRecommendation]
    clinical_decisions: List[ClinicalDecision]
    risk_assessment: Dict[str, Any]
    monitoring_plan: Dict[str, Any]
    follow_up_recommendations: List[str]

@router.post("/recommendations", response_model=RecommendationsResponse)
async def get_treatment_recommendations(
    patient_data: PatientData,
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "admin"]))
):
    """
    Generate AI-powered treatment recommendations based on patient data
    """
    try:
        logger.info(f"Treatment recommendations requested for patient {patient_data.patient_id} by user {current_user['user_id']}")

        # Initialize services
        recommendation_service = RecommendationService()
        guidelines_service = ClinicalGuidelinesService()
        literature_service = LiteratureService()

        # Generate primary diagnosis
        diagnosis_result = await recommendation_service.generate_diagnosis(
            patient_data=patient_data
        )

        # Get treatment recommendations
        treatment_recommendations = await recommendation_service.get_treatment_recommendations(
            patient_data=patient_data,
            diagnosis=diagnosis_result["primary_diagnosis"]
        )

        # Get clinical guidelines
        clinical_guidelines = await guidelines_service.get_relevant_guidelines(
            diagnosis=diagnosis_result["primary_diagnosis"],
            patient_characteristics=patient_data
        )

        # Get supporting literature
        literature_references = await literature_service.search_clinical_evidence(
            diagnosis=diagnosis_result["primary_diagnosis"],
            treatments=treatment_recommendations
        )

        # Generate clinical decisions
        clinical_decisions = await recommendation_service.generate_clinical_decisions(
            patient_data=patient_data,
            diagnosis=diagnosis_result,
            treatments=treatment_recommendations,
            guidelines=clinical_guidelines
        )

        # Assess patient risks
        risk_assessment = await recommendation_service.assess_patient_risks(
            patient_data=patient_data,
            treatments=treatment_recommendations
        )

        # Create monitoring plan
        monitoring_plan = await recommendation_service.create_monitoring_plan(
            patient_data=patient_data,
            treatments=treatment_recommendations,
            risks=risk_assessment
        )

        response = RecommendationsResponse(
            patient_id=patient_data.patient_id,
            generated_at=datetime.now(),
            primary_diagnosis=diagnosis_result["primary_diagnosis"],
            treatment_recommendations=treatment_recommendations,
            clinical_decisions=clinical_decisions,
            risk_assessment=risk_assessment,
            monitoring_plan=monitoring_plan,
            follow_up_recommendations=monitoring_plan["follow_up_recommendations"]
        )

        logger.info(f"Treatment recommendations generated successfully for patient {patient_data.patient_id}")
        return response

    except Exception as e:
        logger.error(f"Treatment recommendations generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Treatment recommendations generation failed: {str(e)}"
        )

@router.get("/recommendations/{patient_id}/history")
async def get_recommendation_history(
    patient_id: str,
    limit: int = 10,
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "admin"]))
):
    """
    Get history of recommendations for a patient
    """
    try:
        recommendation_service = RecommendationService()

        history = await recommendation_service.get_recommendation_history(
            patient_id=patient_id,
            limit=limit
        )

        return history

    except Exception as e:
        logger.error(f"Failed to get recommendation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendation history: {str(e)}"
        )

@router.post("/recommendations/{patient_id}/feedback")
async def provide_recommendation_feedback(
    patient_id: str,
    feedback: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "admin"]))
):
    """
    Provide feedback on recommendations to improve the system
    """
    try:
        recommendation_service = RecommendationService()

        feedback_result = await recommendation_service.record_feedback(
            patient_id=patient_id,
            feedback=feedback,
            provided_by=current_user["user_id"]
        )

        return feedback_result

    except Exception as e:
        logger.error(f"Failed to record feedback: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record feedback: {str(e)}"
        )

@router.get("/recommendations/guidelines/{condition}")
async def get_clinical_guidelines(
    condition: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get clinical guidelines for a specific condition
    """
    try:
        guidelines_service = ClinicalGuidelinesService()

        guidelines = await guidelines_service.get_guidelines_for_condition(condition)

        return guidelines

    except Exception as e:
        logger.error(f"Failed to get clinical guidelines: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get clinical guidelines: {str(e)}"
        )

@router.post("/recommendations/validate")
async def validate_treatment_plan(
    treatment_plan: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "admin"]))
):
    """
    Validate a treatment plan against clinical guidelines and best practices
    """
    try:
        recommendation_service = RecommendationService()

        validation_result = await recommendation_service.validate_treatment_plan(
            treatment_plan=treatment_plan
        )

        return validation_result

    except Exception as e:
        logger.error(f"Treatment plan validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Treatment plan validation failed: {str(e)}"
        )

@router.get("/recommendations/evidence/{treatment}")
async def get_treatment_evidence(
    treatment: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get clinical evidence supporting a specific treatment
    """
    try:
        literature_service = LiteratureService()

        evidence = await literature_service.get_treatment_evidence(treatment)

        return evidence

    except Exception as e:
        logger.error(f"Failed to get treatment evidence: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get treatment evidence: {str(e)}"
        )

@router.post("/recommendations/compare")
async def compare_treatments(
    treatments: List[str],
    patient_context: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "admin"]))
):
    """
    Compare multiple treatment options for a patient
    """
    try:
        recommendation_service = RecommendationService()

        comparison = await recommendation_service.compare_treatments(
            treatments=treatments,
            patient_context=patient_context
        )

        return comparison

    except Exception as e:
        logger.error(f"Treatment comparison failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Treatment comparison failed: {str(e)}"
        )







