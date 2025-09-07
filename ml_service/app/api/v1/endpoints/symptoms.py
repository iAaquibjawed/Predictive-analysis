from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
from app.core.security import get_current_user, require_roles
from app.services.symptom_analyzer import SymptomAnalyzer
from app.services.clinical_nlp import ClinicalNLPService

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response
class SymptomData(BaseModel):
    symptoms: List[str]
    patient_age: Optional[int] = None
    patient_gender: Optional[str] = None
    medical_history: Optional[List[str]] = None
    current_medications: Optional[List[str]] = None
    vital_signs: Optional[Dict[str, float]] = None

class SymptomAnalysisResponse(BaseModel):
    analysis_id: str
    primary_diagnosis: str
    confidence_score: float
    differential_diagnoses: List[Dict[str, Any]]
    recommended_tests: List[str]
    urgency_level: str  # low, medium, high, critical
    treatment_suggestions: List[str]
    risk_factors: List[str]
    clinical_guidelines: List[Dict[str, Any]]

@router.post("/analyze_symptoms", response_model=SymptomAnalysisResponse)
async def analyze_symptoms(
    symptom_data: SymptomData,
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "admin"]))
):
    """
    Analyze patient symptoms using AI models and clinical knowledge
    """
    try:
        logger.info(f"Symptom analysis requested by user {current_user['user_id']}")

        # Initialize services
        symptom_analyzer = SymptomAnalyzer()
        nlp_service = ClinicalNLPService()

        # Perform symptom analysis
        analysis_result = await symptom_analyzer.analyze_symptoms(
            symptoms=symptom_data.symptoms,
            patient_age=symptom_data.patient_age,
            patient_gender=symptom_data.patient_gender,
            medical_history=symptom_data.medical_history,
            current_medications=symptom_data.current_medications,
            vital_signs=symptom_data.vital_signs
        )

        # Enhance with clinical NLP insights
        clinical_insights = await nlp_service.get_clinical_insights(
            symptoms=symptom_data.symptoms,
            diagnosis=analysis_result["primary_diagnosis"]
        )

        # Combine results
        response = SymptomAnalysisResponse(
            analysis_id=analysis_result["analysis_id"],
            primary_diagnosis=analysis_result["primary_diagnosis"],
            confidence_score=analysis_result["confidence_score"],
            differential_diagnoses=analysis_result["differential_diagnoses"],
            recommended_tests=analysis_result["recommended_tests"],
            urgency_level=analysis_result["urgency_level"],
            treatment_suggestions=analysis_result["treatment_suggestions"],
            risk_factors=analysis_result["risk_factors"],
            clinical_guidelines=clinical_insights["guidelines"]
        )

        logger.info(f"Symptom analysis completed successfully for user {current_user['user_id']}")
        return response

    except Exception as e:
        logger.error(f"Symptom analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symptom analysis failed: {str(e)}"
        )

@router.get("/symptoms/search")
async def search_symptoms(
    query: str,
    limit: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Search for symptoms using clinical terminology
    """
    try:
        nlp_service = ClinicalNLPService()
        results = await nlp_service.search_symptoms(query, limit)
        return {"symptoms": results}

    except Exception as e:
        logger.error(f"Symptom search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symptom search failed: {str(e)}"
        )

@router.get("/symptoms/autocomplete")
async def autocomplete_symptoms(
    prefix: str,
    limit: int = 5,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Autocomplete symptoms as user types
    """
    try:
        nlp_service = ClinicalNLPService()
        results = await nlp_service.autocomplete_symptoms(prefix, limit)
        return {"suggestions": results}

    except Exception as e:
        logger.error(f"Symptom autocomplete failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Symptom autocomplete failed: {str(e)}"
        )

