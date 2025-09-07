import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class ComplianceService:
    """
    Service for tracking patient medication compliance and generating reports
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.compliance_database = {}  # In production, this would be a database

    async def generate_compliance_report(
        self,
        patient_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate comprehensive compliance report for a patient
        """
        try:
            report_id = str(uuid.uuid4())
            self.logger.info(f"Generating compliance report {report_id} for patient {patient_id}")

            # Get patient's medication data
            medication_data = await self._get_patient_medications(patient_id, start_date, end_date)

            # Calculate adherence for each medication
            medications = []
            for med in medication_data:
                adherence = await self._calculate_medication_adherence(
                    patient_id, med["medication_id"], start_date, end_date
                )
                medications.append(adherence)

            # Calculate overall adherence
            overall_adherence = self.calculate_overall_adherence(medications)

            # Generate risk assessment
            risk_assessment = await self.assess_compliance_risks(
                patient_id, {"medications": medications}, []
            )

            result = {
                "report_id": report_id,
                "medications": medications,
                "overall_adherence": overall_adherence,
                "risk_assessment": risk_assessment
            }

            self.logger.info(f"Compliance report {report_id} generated successfully")
            return result

        except Exception as e:
            self.logger.error(f"Failed to generate compliance report: {e}")
            raise

    async def _get_patient_medications(
        self,
        patient_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get patient's medications for the specified period"""

        # Mock data - in production, this would query the database
        mock_medications = [
            {
                "medication_id": "med_001",
                "medication_name": "Metformin",
                "dosage": "500mg",
                "frequency": "twice daily",
                "prescribed_date": start_date - timedelta(days=30),
                "end_date": end_date + timedelta(days=30)
            },
            {
                "medication_id": "med_002",
                "medication_name": "Lisinopril",
                "dosage": "10mg",
                "frequency": "once daily",
                "prescribed_date": start_date - timedelta(days=45),
                "end_date": end_date + timedelta(days=45)
            }
        ]

        return mock_medications

    async def _calculate_medication_adherence(
        self,
        patient_id: str,
        medication_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Calculate adherence for a specific medication"""

        # Mock adherence data - in production, this would query IoT devices and prescription records
        mock_adherence_data = {
            "med_001": {
                "prescribed_doses": 60,  # 30 days * 2 doses per day
                "taken_doses": 52,
                "last_taken": end_date - timedelta(days=1),
                "next_dose": end_date + timedelta(hours=12)
            },
            "med_002": {
                "prescribed_doses": 30,  # 30 days * 1 dose per day
                "taken_doses": 28,
                "last_taken": end_date - timedelta(days=2),
                "next_dose": end_date + timedelta(hours=24)
            }
        }

        if medication_id not in mock_adherence_data:
            return self._create_empty_adherence(medication_id)

        data = mock_adherence_data[medication_id]
        adherence_rate = data["taken_doses"] / data["prescribed_doses"]
        missed_doses = data["prescribed_doses"] - data["taken_doses"]

        # Determine compliance trend
        compliance_trend = self._determine_compliance_trend(adherence_rate)

        return {
            "medication_id": medication_id,
            "medication_name": self._get_medication_name(medication_id),
            "prescribed_doses": data["prescribed_doses"],
            "taken_doses": data["taken_doses"],
            "adherence_rate": adherence_rate,
            "missed_doses": missed_doses,
            "last_taken": data["last_taken"],
            "next_dose": data["next_dose"],
            "compliance_trend": compliance_trend
        }

    def _create_empty_adherence(self, medication_id: str) -> Dict[str, Any]:
        """Create empty adherence data for medications without data"""
        return {
            "medication_id": medication_id,
            "medication_name": self._get_medication_name(medication_id),
            "prescribed_doses": 0,
            "taken_doses": 0,
            "adherence_rate": 0.0,
            "missed_doses": 0,
            "last_taken": None,
            "next_dose": None,
            "compliance_trend": "unknown"
        }

    def _get_medication_name(self, medication_id: str) -> str:
        """Get medication name from ID"""
        medication_names = {
            "med_001": "Metformin",
            "med_002": "Lisinopril"
        }
        return medication_names.get(medication_id, "Unknown Medication")

    def _determine_compliance_trend(self, adherence_rate: float) -> str:
        """Determine if compliance is improving, declining, or stable"""
        if adherence_rate >= 0.9:
            return "stable"
        elif adherence_rate >= 0.7:
            return "improving"
        else:
            return "declining"

    def calculate_overall_adherence(self, medications: List[Dict[str, Any]]) -> float:
        """Calculate overall adherence across all medications"""
        if not medications:
            return 0.0

        total_adherence = sum(med["adherence_rate"] for med in medications)
        return total_adherence / len(medications)

    async def assess_compliance_risks(
        self,
        patient_id: str,
        adherence_data: Dict[str, Any],
        iot_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess compliance risks and generate recommendations"""

        risk_factors = []
        recommendations = []
        alerts = []

        medications = adherence_data.get("medications", [])

        # Assess medication-specific risks
        for med in medications:
            if med["adherence_rate"] < 0.8:
                risk_factors.append(f"Low adherence to {med['medication_name']} ({med['adherence_rate']:.1%})")
                recommendations.append(f"Increase monitoring for {med['medication_name']}")

                if med["adherence_rate"] < 0.6:
                    alerts.append({
                        "type": "high_risk",
                        "medication": med["medication_name"],
                        "message": f"Critical: {med['medication_name']} adherence below 60%",
                        "severity": "high"
                    })

        # Assess overall compliance risks
        overall_adherence = self.calculate_overall_adherence(medications)

        if overall_adherence < 0.7:
            risk_factors.append("Overall medication adherence below 70%")
            recommendations.append("Implement comprehensive compliance intervention")
            alerts.append({
                "type": "compliance_intervention",
                "message": "Patient requires compliance support program",
                "severity": "medium"
            })

        # Assess timing risks
        for med in medications:
            if med["last_taken"] and med["next_dose"]:
                time_since_last = datetime.now() - med["last_taken"]
                if time_since_last > timedelta(days=3):
                    risk_factors.append(f"Missed doses of {med['medication_name']} for {time_since_last.days} days")
                    recommendations.append(f"Contact patient regarding {med['medication_name']}")

        return {
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "alerts": alerts
        }

    async def get_medication_compliance(
        self,
        patient_id: str,
        medication_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get detailed compliance data for a specific medication"""

        adherence = await self._calculate_medication_adherence(
            patient_id, medication_id, start_date, end_date
        )

        # Add daily breakdown
        daily_breakdown = await self._get_daily_compliance_breakdown(
            patient_id, medication_id, start_date, end_date
        )

        return {
            "medication": adherence,
            "daily_breakdown": daily_breakdown,
            "compliance_analysis": self._analyze_compliance_patterns(daily_breakdown)
        }

    async def _get_daily_compliance_breakdown(
        self,
        patient_id: str,
        medication_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get daily compliance breakdown for a medication"""

        daily_data = []
        current_date = start_date

        while current_date <= end_date:
            # Mock daily data - in production, this would query IoT devices
            daily_data.append({
                "date": current_date.date(),
                "prescribed_doses": 2 if medication_id == "med_001" else 1,
                "taken_doses": np.random.randint(0, 3) if medication_id == "med_001" else np.random.randint(0, 2),
                "adherence_rate": np.random.uniform(0.5, 1.0)
            })
            current_date += timedelta(days=1)

        return daily_data

    def _analyze_compliance_patterns(self, daily_breakdown: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze compliance patterns from daily data"""

        if not daily_breakdown:
            return {}

        adherence_rates = [day["adherence_rate"] for day in daily_breakdown]

        # Calculate statistics
        mean_adherence = np.mean(adherence_rates)
        std_adherence = np.std(adherence_rates)

        # Identify patterns
        patterns = []
        if std_adherence < 0.1:
            patterns.append("Consistent compliance")
        elif std_adherence > 0.3:
            patterns.append("Variable compliance")

        # Check for weekend effect
        weekend_days = [day for day in daily_breakdown if day["date"].weekday() >= 5]
        weekday_days = [day for day in daily_breakdown if day["date"].weekday() < 5]

        if weekend_days and weekday_days:
            weekend_adherence = np.mean([day["adherence_rate"] for day in weekend_days])
            weekday_adherence = np.mean([day["adherence_rate"] for day in weekday_days])

            if abs(weekend_adherence - weekday_adherence) > 0.2:
                patterns.append("Weekend compliance variation")

        return {
            "mean_adherence": mean_adherence,
            "std_adherence": std_adherence,
            "patterns": patterns,
            "total_days": len(daily_breakdown)
        }

    async def get_compliance_trends(
        self,
        patient_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get compliance trends over time"""

        # Get compliance data for multiple time periods
        periods = [
            (start_date, start_date + timedelta(days=30)),
            (start_date + timedelta(days=31), start_date + timedelta(days=60)),
            (start_date + timedelta(days=61), end_date)
        ]

        trends = []
        for period_start, period_end in periods:
            if period_end <= end_date:
                period_data = await self._get_patient_medications(patient_id, period_start, period_end)
                period_adherence = []

                for med in period_data:
                    adherence = await self._calculate_medication_adherence(
                        patient_id, med["medication_id"], period_start, period_end
                    )
                    period_adherence.append(adherence["adherence_rate"])

                if period_adherence:
                    trends.append({
                        "period": f"{period_start.date()} to {period_end.date()}",
                        "average_adherence": np.mean(period_adherence),
                        "medication_count": len(period_adherence)
                    })

        return {
            "trends": trends,
            "overall_trend": self._calculate_trend_direction(trends)
        }

    def _calculate_trend_direction(self, trends: List[Dict[str, Any]]) -> str:
        """Calculate if compliance is trending up, down, or stable"""
        if len(trends) < 2:
            return "insufficient_data"

        adherence_values = [trend["average_adherence"] for trend in trends]

        # Simple linear trend calculation
        if len(adherence_values) >= 2:
            slope = adherence_values[-1] - adherence_values[0]
            if slope > 0.05:
                return "improving"
            elif slope < -0.05:
                return "declining"
            else:
                return "stable"

        return "stable"

    async def configure_alerts(
        self,
        patient_id: str,
        alert_config: Dict[str, Any],
        configured_by: str
    ) -> Dict[str, Any]:
        """Configure compliance alerts for a patient"""

        # Validate alert configuration
        required_fields = ["threshold", "notification_method", "escalation_rules"]
        for field in required_fields:
            if field not in alert_config:
                raise ValueError(f"Missing required field: {field}")

        # Store alert configuration
        alert_id = str(uuid.uuid4())
        alert_config["id"] = alert_id
        alert_config["patient_id"] = patient_id
        alert_config["configured_by"] = configured_by
        alert_config["configured_at"] = datetime.now().isoformat()
        alert_config["active"] = True

        # In production, this would be stored in a database
        self.compliance_database[alert_id] = alert_config

        return {
            "alert_id": alert_id,
            "status": "configured",
            "configuration": alert_config
        }





