import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class IoTService:
    """
    Service for handling IoT data from patient monitoring devices
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.device_database = {}  # In production, this would be a database
        self.alert_rules = self._load_alert_rules()

    def _load_alert_rules(self) -> Dict[str, Any]:
        """Load alert rules for IoT devices"""
        return {
            "medication_taken": {
                "missed_dose": {"threshold": 1, "severity": "medium"},
                "multiple_missed_doses": {"threshold": 3, "severity": "high"}
            },
            "heart_rate": {
                "bradycardia": {"threshold": 50, "severity": "high", "condition": "below"},
                "tachycardia": {"threshold": 100, "severity": "high", "condition": "above"}
            },
            "blood_pressure": {
                "hypertension": {"threshold": 140, "severity": "medium", "condition": "above"},
                "hypotension": {"threshold": 90, "severity": "high", "condition": "below"}
            },
            "blood_glucose": {
                "hypoglycemia": {"threshold": 70, "severity": "critical", "condition": "below"},
                "hyperglycemia": {"threshold": 200, "severity": "medium", "condition": "above"}
            }
        }

    async def store_reading(
        self,
        patient_id: str,
        reading: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store IoT reading from patient devices
        """
        try:
            reading_id = str(uuid.uuid4())
            timestamp = datetime.now()

            # Validate reading data
            validated_reading = self._validate_reading(reading)

            # Store reading with metadata
            stored_reading = {
                "id": reading_id,
                "patient_id": patient_id,
                "timestamp": timestamp,
                "device_type": validated_reading.get("device_type", "unknown"),
                "reading_type": validated_reading.get("reading_type", "unknown"),
                "value": validated_reading.get("value"),
                "unit": validated_reading.get("unit"),
                "confidence": validated_reading.get("confidence", 1.0),
                "raw_data": reading
            }

            # Store in database (mock for now)
            self.device_database[reading_id] = stored_reading

            self.logger.info(f"Stored IoT reading {reading_id} for patient {patient_id}")
            return stored_reading

        except Exception as e:
            self.logger.error(f"Failed to store IoT reading: {e}")
            raise

    def _validate_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """Validate IoT reading data"""

        validated = {}

        # Required fields
        required_fields = ["device_type", "reading_type", "value"]
        for field in required_fields:
            if field in reading:
                validated[field] = reading[field]
            else:
                raise ValueError(f"Missing required field: {field}")

        # Optional fields
        optional_fields = ["unit", "confidence"]
        for field in optional_fields:
            if field in reading:
                validated[field] = reading[field]

        # Validate confidence range
        if "confidence" in validated:
            confidence = validated["confidence"]
            if not (0.0 <= confidence <= 1.0):
                validated["confidence"] = 1.0

        # Validate device type
        valid_device_types = ["smart_pillbox", "wearable", "sensor", "monitor"]
        if validated["device_type"] not in valid_device_types:
            validated["device_type"] = "unknown"

        return validated

    async def get_patient_readings(
        self,
        patient_id: str,
        start_date: datetime,
        end_date: datetime,
        device_type: Optional[str] = None,
        reading_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get IoT readings for a patient within a date range
        """
        try:
            # Filter readings by patient and date range
            readings = []

            for reading_id, reading in self.device_database.items():
                if reading["patient_id"] == patient_id:
                    reading_timestamp = reading["timestamp"]

                    if start_date <= reading_timestamp <= end_date:
                        # Apply additional filters
                        if device_type and reading["device_type"] != device_type:
                            continue
                        if reading_type and reading["reading_type"] != reading_type:
                            continue

                        readings.append(reading)

            # Sort by timestamp
            readings.sort(key=lambda x: x["timestamp"])

            return readings

        except Exception as e:
            self.logger.error(f"Failed to get patient readings: {e}")
            raise

    async def check_alerts(
        self,
        patient_id: str,
        reading: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Check if IoT reading triggers any alerts
        """
        try:
            alerts = []
            reading_type = reading.get("reading_type")
            value = reading.get("value")

            if reading_type in self.alert_rules and value is not None:
                rules = self.alert_rules[reading_type]

                for alert_name, rule in rules.items():
                    threshold = rule["threshold"]
                    severity = rule["severity"]
                    condition = rule.get("condition", "above")

                    # Check if alert should be triggered
                    should_alert = False

                    if condition == "above" and value > threshold:
                        should_alert = True
                    elif condition == "below" and value < threshold:
                        should_alert = True
                    elif condition == "equals" and value == threshold:
                        should_alert = True

                    if should_alert:
                        alert = {
                            "alert_id": str(uuid.uuid4()),
                            "patient_id": patient_id,
                            "alert_type": alert_name,
                            "severity": severity,
                            "reading_type": reading_type,
                            "value": value,
                            "threshold": threshold,
                            "timestamp": datetime.now(),
                            "message": self._generate_alert_message(alert_name, reading_type, value, threshold)
                        }
                        alerts.append(alert)

            return alerts

        except Exception as e:
            self.logger.error(f"Failed to check alerts: {e}")
            raise

    def _generate_alert_message(
        self,
        alert_name: str,
        reading_type: str,
        value: Any,
        threshold: Any
    ) -> str:
        """Generate human-readable alert message"""

        if alert_name == "missed_dose":
            return f"Patient missed medication dose. Value: {value}, Threshold: {threshold}"
        elif alert_name == "multiple_missed_doses":
            return f"Patient has missed multiple medication doses. Value: {value}, Threshold: {threshold}"
        elif alert_name == "bradycardia":
            return f"Patient heart rate is below normal range. Value: {value} bpm, Threshold: {threshold} bpm"
        elif alert_name == "tachycardia":
            return f"Patient heart rate is above normal range. Value: {value} bpm, Threshold: {threshold} bpm"
        elif alert_name == "hypertension":
            return f"Patient blood pressure is elevated. Value: {value} mmHg, Threshold: {threshold} mmHg"
        elif alert_name == "hypotension":
            return f"Patient blood pressure is below normal. Value: {value} mmHg, Threshold: {threshold} mmHg"
        elif alert_name == "hypoglycemia":
            return f"Patient blood glucose is critically low. Value: {value} mg/dL, Threshold: {threshold} mg/dL"
        elif alert_name == "hyperglycemia":
            return f"Patient blood glucose is elevated. Value: {value} mg/dL, Threshold: {threshold} mg/dL"
        else:
            return f"Alert triggered for {reading_type}. Value: {value}, Threshold: {threshold}"

    async def get_device_status(self, patient_id: str) -> Dict[str, Any]:
        """
        Get status of all IoT devices for a patient
        """
        try:
            # Get recent readings for each device type
            device_status = {}

            device_types = ["smart_pillbox", "wearable", "sensor", "monitor"]

            for device_type in device_types:
                recent_readings = await self.get_patient_readings(
                    patient_id=patient_id,
                    start_date=datetime.now() - timedelta(hours=24),
                    end_date=datetime.now(),
                    device_type=device_type
                )

                if recent_readings:
                    latest_reading = max(recent_readings, key=lambda x: x["timestamp"])
                    device_status[device_type] = {
                        "status": "active",
                        "last_reading": latest_reading["timestamp"],
                        "last_value": latest_reading["value"],
                        "reading_count_24h": len(recent_readings)
                    }
                else:
                    device_status[device_type] = {
                        "status": "inactive",
                        "last_reading": None,
                        "last_value": None,
                        "reading_count_24h": 0
                    }

            return {
                "patient_id": patient_id,
                "device_status": device_status,
                "overall_status": "active" if any(d["status"] == "active" for d in device_status.values()) else "inactive"
            }

        except Exception as e:
            self.logger.error(f"Failed to get device status: {e}")
            raise

    async def get_medication_adherence_from_iot(
        self,
        patient_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Calculate medication adherence from IoT pillbox data
        """
        try:
            # Get pillbox readings
            pillbox_readings = await self.get_patient_readings(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                device_type="smart_pillbox",
                reading_type="medication_taken"
            )

            if not pillbox_readings:
                return {
                    "adherence_rate": 0.0,
                    "total_doses": 0,
                    "taken_doses": 0,
                    "missed_doses": 0,
                    "data_quality": "poor"
                }

            # Calculate adherence metrics
            total_doses = len(pillbox_readings)
            taken_doses = sum(1 for reading in pillbox_readings if reading["value"] == 1)
            missed_doses = total_doses - taken_doses

            adherence_rate = taken_doses / total_doses if total_doses > 0 else 0.0

            # Assess data quality
            data_quality = self._assess_data_quality(pillbox_readings)

            return {
                "adherence_rate": adherence_rate,
                "total_doses": total_doses,
                "taken_doses": taken_doses,
                "missed_doses": missed_doses,
                "data_quality": data_quality,
                "readings": pillbox_readings
            }

        except Exception as e:
            self.logger.error(f"Failed to get medication adherence from IoT: {e}")
            raise

    def _assess_data_quality(self, readings: List[Dict[str, Any]]) -> str:
        """Assess quality of IoT data"""

        if not readings:
            return "poor"

        # Check for missing data
        total_expected = len(readings)
        actual_readings = len([r for r in readings if r["value"] is not None])

        completeness = actual_readings / total_expected

        # Check for data consistency
        values = [r["value"] for r in readings if r["value"] is not None]
        if values:
            std_dev = np.std(values)
            mean_val = np.mean(values)
            consistency = 1.0 - (std_dev / mean_val) if mean_val > 0 else 0.0
        else:
            consistency = 0.0

        # Determine overall quality
        if completeness > 0.9 and consistency > 0.8:
            return "excellent"
        elif completeness > 0.7 and consistency > 0.6:
            return "good"
        elif completeness > 0.5 and consistency > 0.4:
            return "fair"
        else:
            return "poor"

    async def get_vital_signs_trends(
        self,
        patient_id: str,
        vital_sign: str,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get trends for specific vital signs from IoT data
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Get vital signs readings
            vital_readings = await self.get_patient_readings(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                reading_type=vital_sign
            )

            if not vital_readings:
                return {
                    "vital_sign": vital_sign,
                    "trend": "insufficient_data",
                    "readings": [],
                    "statistics": {}
                }

            # Calculate trends
            values = [r["value"] for r in vital_readings if r["value"] is not None]

            if len(values) < 2:
                return {
                    "vital_sign": vital_sign,
                    "trend": "insufficient_data",
                    "readings": vital_readings,
                    "statistics": {"count": len(values)}
                }

            # Calculate basic statistics
            mean_val = np.mean(values)
            std_val = np.std(values)
            min_val = min(values)
            max_val = max(values)

            # Calculate trend
            if len(values) >= 3:
                # Simple linear trend
                x = np.arange(len(values))
                slope = np.polyfit(x, values, 1)[0]

                if slope > std_val * 0.1:
                    trend = "increasing"
                elif slope < -std_val * 0.1:
                    trend = "decreasing"
                else:
                    trend = "stable"
            else:
                trend = "insufficient_data"

            return {
                "vital_sign": vital_sign,
                "trend": trend,
                "readings": vital_readings,
                "statistics": {
                    "count": len(values),
                    "mean": float(mean_val),
                    "std": float(std_val),
                    "min": float(min_val),
                    "max": float(max_val),
                    "range": float(max_val - min_val)
                }
            }

        except Exception as e:
            self.logger.error(f"Failed to get vital signs trends: {e}")
            raise

    async def configure_device_alerts(
        self,
        patient_id: str,
        device_type: str,
        alert_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Configure alerts for specific IoT devices
        """
        try:
            config_id = str(uuid.uuid4())

            # Validate alert configuration
            validated_config = self._validate_alert_config(alert_config)

            # Store configuration
            device_config = {
                "config_id": config_id,
                "patient_id": patient_id,
                "device_type": device_type,
                "alert_config": validated_config,
                "created_at": datetime.now(),
                "active": True
            }

            # In production, this would save to database
            self.device_database[f"config_{config_id}"] = device_config

            return {
                "config_id": config_id,
                "status": "configured",
                "device_type": device_type,
                "alerts": validated_config
            }

        except Exception as e:
            self.logger.error(f"Failed to configure device alerts: {e}")
            raise

    def _validate_alert_config(self, alert_config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate alert configuration"""

        validated = {}

        # Required fields
        required_fields = ["threshold", "severity"]
        for field in required_fields:
            if field not in alert_config:
                raise ValueError(f"Missing required field: {field}")
            validated[field] = alert_config[field]

        # Optional fields
        optional_fields = ["condition", "notification_method", "escalation_rules"]
        for field in optional_fields:
            if field in alert_config:
                validated[field] = alert_config[field]

        # Validate severity
        valid_severities = ["low", "medium", "high", "critical"]
        if validated["severity"] not in valid_severities:
            validated["severity"] = "medium"

        # Validate condition
        valid_conditions = ["above", "below", "equals"]
        if "condition" in validated and validated["condition"] not in valid_conditions:
            validated["condition"] = "above"

        return validated

    async def get_device_analytics(
        self,
        patient_id: str,
        device_type: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get analytics for specific IoT devices
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Get device readings
            readings = await self.get_patient_readings(
                patient_id=patient_id,
                start_date=start_date,
                end_date=end_date,
                device_type=device_type
            )

            if not readings:
                return {
                    "device_type": device_type,
                    "data_availability": 0.0,
                    "usage_patterns": {},
                    "anomalies": [],
                    "recommendations": []
                }

            # Calculate data availability
            total_hours = days * 24
            expected_readings = total_hours  # Assuming hourly readings
            actual_readings = len(readings)
            data_availability = actual_readings / expected_readings if expected_readings > 0 else 0.0

            # Analyze usage patterns
            usage_patterns = self._analyze_usage_patterns(readings)

            # Detect anomalies
            anomalies = self._detect_anomalies(readings)

            # Generate recommendations
            recommendations = self._generate_device_recommendations(
                device_type, data_availability, usage_patterns, anomalies
            )

            return {
                "device_type": device_type,
                "data_availability": data_availability,
                "usage_patterns": usage_patterns,
                "anomalies": anomalies,
                "recommendations": recommendations,
                "total_readings": actual_readings,
                "period_days": days
            }

        except Exception as e:
            self.logger.error(f"Failed to get device analytics: {e}")
            raise

    def _analyze_usage_patterns(self, readings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze usage patterns from IoT readings"""

        if not readings:
            return {}

        # Group readings by hour of day
        hourly_patterns = {}
        for reading in readings:
            hour = reading["timestamp"].hour
            if hour not in hourly_patterns:
                hourly_patterns[hour] = []
            hourly_patterns[hour].append(reading["value"])

        # Calculate hourly averages
        hourly_averages = {}
        for hour, values in hourly_patterns.items():
            if values:
                hourly_averages[hour] = float(np.mean(values))

        # Find peak usage hours
        if hourly_averages:
            peak_hour = max(hourly_averages, key=hourly_averages.get)
            peak_value = hourly_averages[peak_hour]
        else:
            peak_hour = None
            peak_value = None

        return {
            "hourly_patterns": hourly_averages,
            "peak_usage_hour": peak_hour,
            "peak_usage_value": peak_value,
            "total_readings": len(readings)
        }

    def _detect_anomalies(self, readings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies in IoT readings"""

        anomalies = []

        if len(readings) < 3:
            return anomalies

        values = [r["value"] for r in readings if r["value"] is not None]

        if len(values) < 3:
            return anomalies

        # Calculate statistical measures
        mean_val = np.mean(values)
        std_val = np.std(values)

        # Detect outliers (values beyond 2 standard deviations)
        for reading in readings:
            if reading["value"] is not None:
                z_score = abs(reading["value"] - mean_val) / std_val if std_val > 0 else 0

                if z_score > 2:
                    anomalies.append({
                        "timestamp": reading["timestamp"],
                        "value": reading["value"],
                        "expected_range": f"{mean_val - 2*std_val:.2f} to {mean_val + 2*std_val:.2f}",
                        "z_score": float(z_score),
                        "severity": "high" if z_score > 3 else "medium"
                    })

        return anomalies

    def _generate_device_recommendations(
        self,
        device_type: str,
        data_availability: float,
        usage_patterns: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on device analytics"""

        recommendations = []

        # Data availability recommendations
        if data_availability < 0.8:
            recommendations.append("Consider device maintenance or replacement")
            recommendations.append("Check device connectivity and battery status")

        # Usage pattern recommendations
        if usage_patterns.get("peak_usage_hour") is not None:
            peak_hour = usage_patterns["peak_usage_hour"]
            if peak_hour in [22, 23, 0, 1, 2, 3, 4, 5]:  # Late night/early morning
                recommendations.append("Consider adjusting device schedule for better daytime monitoring")

        # Anomaly recommendations
        if anomalies:
            high_severity_anomalies = [a for a in anomalies if a["severity"] == "high"]
            if high_severity_anomalies:
                recommendations.append("Investigate high-severity anomalies immediately")
                recommendations.append("Consider device calibration or sensor replacement")

        # Device-specific recommendations
        if device_type == "smart_pillbox":
            if data_availability < 0.9:
                recommendations.append("Ensure pillbox is properly connected to network")
                recommendations.append("Check pillbox battery and charging status")

        elif device_type == "wearable":
            if data_availability < 0.7:
                recommendations.append("Ensure wearable device is being worn consistently")
                recommendations.append("Check device charging and syncing")

        return recommendations







