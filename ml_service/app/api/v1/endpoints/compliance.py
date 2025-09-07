from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from app.core.security import get_current_user, require_roles
from app.services.compliance_service import ComplianceService
from app.services.iot_service import IoTService

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response
class ComplianceReportRequest(BaseModel):
    patient_id: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_iot_data: bool = True
    include_prescription_data: bool = True

class MedicationAdherence(BaseModel):
    medication_id: str
    medication_name: str
    prescribed_doses: int
    taken_doses: int
    adherence_rate: float
    missed_doses: int
    last_taken: Optional[datetime]
    next_dose: Optional[datetime]
    compliance_trend: str  # improving, declining, stable

class IoTReading(BaseModel):
    timestamp: datetime
    device_type: str  # smart_pillbox, wearable, sensor
    reading_type: str  # medication_taken, heart_rate, blood_pressure, etc.
    value: Any
    unit: Optional[str]
    confidence: float

class ComplianceReport(BaseModel):
    report_id: str
    patient_id: str
    report_period: Dict[str, datetime]
    overall_adherence: float
    medications: List[MedicationAdherence]
    iot_readings: List[IoTReading]
    risk_factors: List[str]
    recommendations: List[str]
    alerts: List[Dict[str, Any]]
    next_review_date: datetime

@router.get("/compliance/{patient_id}", response_model=ComplianceReport)
async def generate_compliance_report(
    patient_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_iot_data: bool = True,
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "pharmacist", "admin"]))
):
    """
    Generate comprehensive compliance report for a patient
    """
    try:
        logger.info(f"Compliance report requested for patient {patient_id} by user {current_user['user_id']}")

        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Initialize services
        compliance_service = ComplianceService()
        iot_service = IoTService()

        # Generate compliance report
        compliance_data = await compliance_service.generate_compliance_report(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date
        )

        # Get IoT data if requested
        iot_readings = []
        if include_iot_data:
            iot_readings = await iot_service.get_patient_readings(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date
            )

        # Calculate overall adherence
        overall_adherence = compliance_service.calculate_overall_adherence(
            compliance_data["medications"]
        )

        # Generate risk assessment and recommendations
        risk_assessment = await compliance_service.assess_compliance_risks(
            patient_id=patient_id,
            adherence_data=compliance_data,
            iot_data=iot_readings
        )

        # Create response
        response = ComplianceReport(
            report_id=compliance_data["report_id"],
            patient_id=patient_id,
            report_period={"start": start_date, "end": end_date},
            overall_adherence=overall_adherence,
            medications=compliance_data["medications"],
            iot_readings=iot_readings,
            risk_factors=risk_assessment["risk_factors"],
            recommendations=risk_assessment["recommendations"],
            alerts=risk_assessment["alerts"],
            next_review_date=datetime.now() + timedelta(days=7)
        )

        logger.info(f"Compliance report generated successfully for patient {patient_id}")
        return response

    except Exception as e:
        logger.error(f"Compliance report generation failed for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Compliance report generation failed: {str(e)}"
        )

@router.get("/compliance/{patient_id}/medication/{medication_id}")
async def get_medication_compliance(
    patient_id: str,
    medication_id: str,
    days: int = 30,
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "pharmacist", "admin"]))
):
    """
    Get detailed compliance data for a specific medication
    """
    try:
        compliance_service = ComplianceService()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        medication_compliance = await compliance_service.get_medication_compliance(
            patient_id=patient_id,
            medication_id=medication_id,
            start_date=start_date,
            end_date=end_date
        )

        return medication_compliance

    except Exception as e:
        logger.error(f"Failed to get medication compliance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get medication compliance: {str(e)}"
        )

@router.post("/compliance/{patient_id}/iot_reading")
async def record_iot_reading(
    patient_id: str,
    reading: IoTReading,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Record IoT reading from patient devices
    """
    try:
        iot_service = IoTService()

        # Validate and store IoT reading
        stored_reading = await iot_service.store_reading(
            patient_id=patient_id,
            reading=reading
        )

        # Check if reading triggers any alerts
        alerts = await iot_service.check_alerts(patient_id, reading)

        return {
            "reading_id": stored_reading["id"],
            "stored_at": stored_reading["timestamp"],
            "alerts": alerts
        }

    except Exception as e:
        logger.error(f"Failed to record IoT reading: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record IoT reading: {str(e)}"
        )

@router.get("/compliance/{patient_id}/trends")
async def get_compliance_trends(
    patient_id: str,
    days: int = 90,
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "pharmacist", "admin"]))
):
    """
    Get compliance trends over time
    """
    try:
        compliance_service = ComplianceService()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        trends = await compliance_service.get_compliance_trends(
            patient_id=patient_id,
            start_date=start_date,
            end_date=end_date
        )

        return trends

    except Exception as e:
        logger.error(f"Failed to get compliance trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get compliance trends: {str(e)}"
        )

@router.post("/compliance/{patient_id}/alerts")
async def configure_compliance_alerts(
    patient_id: str,
    alert_config: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_roles(["doctor", "admin"]))
):
    """
    Configure compliance alerts for a patient
    """
    try:
        compliance_service = ComplianceService()

        alert_settings = await compliance_service.configure_alerts(
            patient_id=patient_id,
            alert_config=alert_config,
            configured_by=current_user["user_id"]
        )

        return alert_settings

    except Exception as e:
        logger.error(f"Failed to configure compliance alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure compliance alerts: {str(e)}"
        )

