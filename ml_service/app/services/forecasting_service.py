import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from prophet import Prophet
import torch
from pytorch_forecasting import TimeSeriesDataSet, TemporalFusionTransformer

logger = logging.getLogger(__name__)

class ForecastingService:
    """
    Service for drug demand forecasting using time series models
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self._load_models()

    def _load_models(self):
        """Load pre-trained forecasting models"""
        try:
            # In production, this would load from MLflow or model registry
            self.logger.info("Forecasting models loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load forecasting models: {e}")

    async def forecast_drug_demand(
        self,
        drug_ids: List[str],
        horizon: int = 30,
        include_seasonality: bool = True,
        include_external_factors: bool = True,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """
        Forecast drug demand using time series models
        """
        try:
            forecast_id = str(uuid.uuid4())
            self.logger.info(f"Starting drug demand forecast {forecast_id} for {len(drug_ids)} drugs")

            drug_forecasts = []

            for drug_id in drug_ids:
                forecast = await self._forecast_single_drug(
                    drug_id, horizon, include_seasonality, include_external_factors, confidence_level
                )
                drug_forecasts.append(forecast)

            result = {
                "forecast_id": forecast_id,
                "drug_forecasts": drug_forecasts,
                "forecast_horizon": horizon,
                "generated_at": datetime.now().isoformat()
            }

            self.logger.info(f"Drug demand forecast {forecast_id} completed successfully")
            return result

        except Exception as e:
            self.logger.error(f"Drug demand forecast failed: {e}")
            raise

    async def _forecast_single_drug(
        self,
        drug_id: str,
        horizon: int,
        include_seasonality: bool,
        include_external_factors: bool,
        confidence_level: float
    ) -> Dict[str, Any]:
        """Forecast demand for a single drug"""

        # Get historical data
        historical_data = await self._get_historical_demand(drug_id)

        if not historical_data or len(historical_data) < 30:  # Need at least 30 days of data
            return self._create_default_forecast(drug_id, horizon)

        # Create time series dataframe
        df = pd.DataFrame(historical_data)
        df['ds'] = pd.to_datetime(df['date'])
        df['y'] = df['demand']

        # Initialize and fit Prophet model
        model = Prophet(
            yearly_seasonality=include_seasonality,
            weekly_seasonality=include_seasonality,
            daily_seasonality=False,
            interval_width=confidence_level
        )

        # Add external factors if requested
        if include_external_factors:
            model.add_regressor('epidemic_indicator')
            model.add_regressor('seasonal_factor')

        # Fit the model
        model.fit(df)

        # Make future predictions
        future_dates = model.make_future_dataframe(periods=horizon)

        # Add external factors for future dates
        if include_external_factors:
            future_dates['epidemic_indicator'] = 0  # Default value
            future_dates['seasonal_factor'] = self._calculate_seasonal_factor(future_dates['ds'])

        # Generate forecast
        forecast = model.predict(future_dates)

        # Extract forecast data
        forecast_data = forecast.tail(horizon)

        # Calculate trend
        trend = self._calculate_trend(forecast_data['yhat'].values)

        # Calculate seasonality factor
        seasonality_factor = None
        if include_seasonality:
            seasonality_factor = self._calculate_seasonality_factor(forecast_data)

        # Get external factors impact
        external_factors = []
        if include_external_factors:
            external_factors = await self._get_external_factors_impact(drug_id, horizon)

        return {
            "drug_id": drug_id,
            "drug_name": self._get_drug_name(drug_id),
            "forecast_date": datetime.now(),
            "predicted_demand": float(forecast_data['yhat'].mean()),
            "lower_bound": float(forecast_data['yhat_lower'].mean()),
            "upper_bound": float(forecast_data['yhat_upper'].mean()),
            "confidence_interval": confidence_level,
            "trend": trend,
            "seasonality_factor": seasonality_factor,
            "external_factors": external_factors
        }

    async def _get_historical_demand(self, drug_id: str) -> List[Dict[str, Any]]:
        """Get historical demand data for a drug"""

        # Mock historical data - in production, this would query the database
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)  # 1 year of data

        historical_data = []
        current_date = start_date

        # Generate realistic demand patterns with seasonality and trends
        base_demand = 100
        trend_factor = 1.02  # 2% monthly growth
        seasonal_factor = 1.0

        while current_date <= end_date:
            # Add trend
            months_since_start = (current_date.year - start_date.year) * 12 + current_date.month - start_date.month
            trend_multiplier = trend_factor ** months_since_start

            # Add seasonality (higher in winter months)
            month = current_date.month
            if month in [12, 1, 2]:  # Winter
                seasonal_factor = 1.3
            elif month in [6, 7, 8]:  # Summer
                seasonal_factor = 0.8
            else:
                seasonal_factor = 1.0

            # Add some randomness
            noise = np.random.normal(0, 0.1)

            demand = int(base_demand * trend_multiplier * seasonal_factor * (1 + noise))

            historical_data.append({
                "date": current_date.date(),
                "demand": max(0, demand),
                "epidemic_indicator": 0,  # No epidemic in historical data
                "seasonal_factor": seasonal_factor
            })

            current_date += timedelta(days=1)

        return historical_data

    def _create_default_forecast(self, drug_id: str, horizon: int) -> Dict[str, Any]:
        """Create default forecast when insufficient data is available"""
        return {
            "drug_id": drug_id,
            "drug_name": self._get_drug_name(drug_id),
            "forecast_date": datetime.now(),
            "predicted_demand": 100.0,  # Default value
            "lower_bound": 80.0,
            "upper_bound": 120.0,
            "confidence_interval": 0.95,
            "trend": "stable",
            "seasonality_factor": None,
            "external_factors": []
        }

    def _get_drug_name(self, drug_id: str) -> str:
        """Get drug name from ID"""
        drug_names = {
            "drug_001": "Metformin",
            "drug_002": "Lisinopril",
            "drug_003": "Atorvastatin",
            "drug_004": "Amlodipine"
        }
        return drug_names.get(drug_id, "Unknown Drug")

    def _calculate_trend(self, values: np.ndarray) -> str:
        """Calculate trend direction from forecast values"""
        if len(values) < 2:
            return "stable"

        # Simple linear trend calculation
        slope = np.polyfit(range(len(values)), values, 1)[0]

        if slope > np.std(values) * 0.1:
            return "increasing"
        elif slope < -np.std(values) * 0.1:
            return "decreasing"
        else:
            return "stable"

    def _calculate_seasonality_factor(self, forecast_data: pd.DataFrame) -> float:
        """Calculate seasonality factor from forecast data"""
        if len(forecast_data) < 30:
            return 1.0

        # Calculate seasonal component
        seasonal_component = forecast_data['yearly'].mean() if 'yearly' in forecast_data.columns else 1.0
        return float(seasonal_component)

    def _calculate_seasonal_factor(self, dates: pd.Series) -> np.ndarray:
        """Calculate seasonal factors for future dates"""
        seasonal_factors = []

        for date in dates:
            month = date.month
            if month in [12, 1, 2]:  # Winter
                seasonal_factors.append(1.3)
            elif month in [6, 7, 8]:  # Summer
                seasonal_factors.append(0.8)
            else:
                seasonal_factors.append(1.0)

        return np.array(seasonal_factors)

    async def _get_external_factors_impact(
        self,
        drug_id: str,
        horizon: int
    ) -> List[Dict[str, Any]]:
        """Get impact of external factors on drug demand"""

        external_factors = []

        # Check for ongoing epidemics
        epidemic_impact = await self._check_epidemic_impact(drug_id)
        if epidemic_impact:
            external_factors.append(epidemic_impact)

        # Check for seasonal factors
        seasonal_impact = await self._check_seasonal_impact(drug_id, horizon)
        if seasonal_impact:
            external_factors.append(seasonal_impact)

        # Check for economic factors
        economic_impact = await self._check_economic_impact(drug_id)
        if economic_impact:
            external_factors.append(economic_impact)

        return external_factors

    async def _check_epidemic_impact(self, drug_id: str) -> Optional[Dict[str, Any]]:
        """Check if there's an ongoing epidemic affecting drug demand"""

        # Mock epidemic data - in production, this would query health databases
        epidemic_data = {
            "drug_001": {"type": "diabetes", "impact": "increased", "magnitude": 0.2},
            "drug_002": {"type": "hypertension", "impact": "increased", "magnitude": 0.15}
        }

        if drug_id in epidemic_data:
            return {
                "factor": "epidemic",
                "type": epidemic_data[drug_id]["type"],
                "impact": epidemic_data[drug_id]["impact"],
                "magnitude": epidemic_data[drug_id]["magnitude"],
                "description": f"Ongoing {epidemic_data[drug_id]['type']} epidemic affecting demand"
            }

        return None

    async def _check_seasonal_impact(self, drug_id: str, horizon: int) -> Optional[Dict[str, Any]]:
        """Check seasonal impact on drug demand"""

        current_month = datetime.now().month

        # Define seasonal patterns for different drug types
        seasonal_patterns = {
            "drug_001": {"winter": 1.2, "summer": 0.9},  # Diabetes meds - higher in winter
            "drug_002": {"winter": 1.1, "summer": 0.95},  # Hypertension meds - slight winter increase
            "drug_003": {"winter": 1.15, "summer": 0.85},  # Statins - higher in winter
            "drug_004": {"winter": 1.05, "summer": 0.98}   # Calcium channel blockers - minimal seasonal effect
        }

        if drug_id in seasonal_patterns:
            pattern = seasonal_patterns[drug_id]

            # Determine if forecast period includes seasonal changes
            forecast_months = [(datetime.now() + timedelta(days=i)).month for i in range(horizon)]

            winter_months = [m for m in forecast_months if m in [12, 1, 2]]
            summer_months = [m for m in forecast_months if m in [6, 7, 8]]

            if winter_months or summer_months:
                return {
                    "factor": "seasonal",
                    "winter_impact": pattern["winter"] if winter_months else 1.0,
                    "summer_impact": pattern["summer"] if summer_months else 1.0,
                    "description": "Seasonal variations in demand expected"
                }

        return None

    async def _check_economic_impact(self, drug_id: str) -> Optional[Dict[str, Any]]:
        """Check economic factors affecting drug demand"""

        # Mock economic data - in production, this would query economic databases
        economic_indicators = {
            "unemployment_rate": 0.05,  # 5%
            "inflation_rate": 0.03,     # 3%
            "gdp_growth": 0.02         # 2%
        }

        # Determine economic impact
        if economic_indicators["unemployment_rate"] > 0.08:
            return {
                "factor": "economic",
                "type": "unemployment",
                "impact": "decreased",
                "magnitude": 0.1,
                "description": "High unemployment may reduce drug affordability"
            }

        if economic_indicators["inflation_rate"] > 0.05:
            return {
                "factor": "economic",
                "type": "inflation",
                "impact": "decreased",
                "magnitude": 0.05,
                "description": "High inflation may affect drug purchasing power"
            }

        return None

    async def get_drug_forecast(self, drug_id: str, horizon: int) -> Dict[str, Any]:
        """Get demand forecast for a specific drug"""

        forecast_result = await self.forecast_drug_demand(
            drug_ids=[drug_id],
            horizon=horizon
        )

        if forecast_result["drug_forecasts"]:
            return forecast_result["drug_forecasts"][0]

        return self._create_default_forecast(drug_id, horizon)

    async def analyze_seasonality(self, drug_id: str, years: int = 3) -> Dict[str, Any]:
        """Analyze seasonal patterns for drug demand"""

        # Get historical data for multiple years
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years)

        historical_data = await self._get_historical_demand(drug_id)

        if not historical_data:
            return {"error": "Insufficient data for seasonality analysis"}

        # Convert to DataFrame for analysis
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year

        # Calculate monthly averages
        monthly_averages = df.groupby('month')['demand'].mean()

        # Identify peak and trough months
        peak_month = monthly_averages.idxmax()
        trough_month = monthly_averages.idxmin()
        peak_demand = monthly_averages.max()
        trough_demand = monthly_averages.min()

        # Calculate seasonality strength
        overall_mean = df['demand'].mean()
        seasonality_strength = (peak_demand - trough_demand) / overall_mean

        return {
            "drug_id": drug_id,
            "analysis_period": f"{years} years",
            "monthly_patterns": monthly_averages.to_dict(),
            "peak_month": peak_month,
            "trough_month": trough_month,
            "peak_demand": float(peak_demand),
            "trough_demand": float(trough_demand),
            "seasonality_strength": float(seasonality_strength),
            "overall_mean": float(overall_mean)
        }

    async def get_market_insights(self, drug_ids: List[str]) -> List[Dict[str, Any]]:
        """Get market insights for drugs"""

        insights = []

        for drug_id in drug_ids:
            # Get market data
            market_data = await self._get_market_data(drug_id)

            # Get competitive landscape
            competitive_landscape = await self._get_competitive_landscape(drug_id)

            # Get regulatory updates
            regulatory_updates = await self._get_regulatory_updates(drug_id)

            insights.append({
                "drug_id": drug_id,
                "drug_name": self._get_drug_name(drug_id),
                "market_data": market_data,
                "competitive_landscape": competitive_landscape,
                "regulatory_updates": regulatory_updates
            })

        return insights

    async def _get_market_data(self, drug_id: str) -> Dict[str, Any]:
        """Get market data for a drug"""

        # Mock market data - in production, this would query market databases
        market_data = {
            "market_size": np.random.randint(1000000, 10000000),
            "growth_rate": np.random.uniform(0.05, 0.15),
            "market_share": np.random.uniform(0.1, 0.4),
            "price_trend": "stable"
        }

        return market_data

    async def _get_competitive_landscape(self, drug_id: str) -> Dict[str, Any]:
        """Get competitive landscape for a drug"""

        # Mock competitive data
        competitors = [
            {"name": "Generic Alternative 1", "market_share": 0.25, "price": "lower"},
            {"name": "Brand Alternative 2", "market_share": 0.15, "price": "higher"},
            {"name": "Generic Alternative 3", "market_share": 0.20, "price": "lower"}
        ]

        return {
            "competitor_count": len(competitors),
            "competitors": competitors,
            "competitive_intensity": "high" if len(competitors) > 3 else "medium"
        }

    async def _get_regulatory_updates(self, drug_id: str) -> List[Dict[str, Any]]:
        """Get regulatory updates for a drug"""

        # Mock regulatory data
        updates = [
            {
                "type": "patent_expiry",
                "date": "2024-06-15",
                "impact": "decreased",
                "description": "Patent expiry may lead to generic competition"
            }
        ]

        return updates

    async def assess_forecast_risks(
        self,
        forecasts: Dict[str, Any],
        market_insights: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess risks in forecasting"""

        risks = []

        # Check forecast confidence
        for forecast in forecasts.get("drug_forecasts", []):
            if forecast.get("upper_bound", 0) - forecast.get("lower_bound", 0) > forecast.get("predicted_demand", 1) * 0.5:
                risks.append({
                    "type": "high_uncertainty",
                    "drug_id": forecast["drug_id"],
                    "severity": "medium",
                    "description": "High forecast uncertainty"
                })

        # Check market risks
        for insight in market_insights:
            if insight.get("market_data", {}).get("growth_rate", 0) < 0.05:
                risks.append({
                    "type": "market_decline",
                    "drug_id": insight["drug_id"],
                    "severity": "high",
                    "description": "Market showing decline"
                })

        return {
            "risk_count": len(risks),
            "risks": risks,
            "overall_risk_level": "high" if len([r for r in risks if r["severity"] == "high"]) > 2 else "medium"
        }

    async def retrain_models(self, drug_ids: List[str]) -> Dict[str, Any]:
        """Retrain forecasting models with latest data"""

        retrain_results = []

        for drug_id in drug_ids:
            try:
                # Get latest data
                latest_data = await self._get_historical_demand(drug_id)

                if len(latest_data) >= 100:  # Need sufficient data
                    # Retrain model
                    model = Prophet()
                    df = pd.DataFrame(latest_data)
                    df['ds'] = pd.to_datetime(df['date'])
                    df['y'] = df['demand']

                    model.fit(df)

                    # Save updated model
                    # In production, this would save to MLflow or model registry

                    retrain_results.append({
                        "drug_id": drug_id,
                        "status": "success",
                        "data_points": len(latest_data),
                        "retrained_at": datetime.now().isoformat()
                    })
                else:
                    retrain_results.append({
                        "drug_id": drug_id,
                        "status": "insufficient_data",
                        "data_points": len(latest_data),
                        "required": 100
                    })

            except Exception as e:
                retrain_results.append({
                    "drug_id": drug_id,
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "retrain_results": retrain_results,
            "success_count": len([r for r in retrain_results if r["status"] == "success"]),
            "failed_count": len([r for r in retrain_results if r["status"] == "failed"])
        }

    async def get_forecast_accuracy(self, drug_id: str, days: int = 30) -> Dict[str, Any]:
        """Get accuracy metrics for previous forecasts"""

        # Get historical forecasts and actual data
        historical_forecasts = await self._get_historical_forecasts(drug_id, days)
        actual_data = await self._get_historical_demand(drug_id)

        if not historical_forecasts or not actual_data:
            return {"error": "Insufficient data for accuracy assessment"}

        # Calculate accuracy metrics
        mae = self._calculate_mae(historical_forecasts, actual_data)
        mape = self._calculate_mape(historical_forecasts, actual_data)
        rmse = self._calculate_rmse(historical_forecasts, actual_data)

        return {
            "drug_id": drug_id,
            "assessment_period": f"{days} days",
            "mae": mae,
            "mape": mape,
            "rmse": rmse,
            "accuracy_level": self._get_accuracy_level(mape)
        }

    async def _get_historical_forecasts(self, drug_id: str, days: int) -> List[Dict[str, Any]]:
        """Get historical forecasts for accuracy assessment"""

        # Mock historical forecasts - in production, this would query forecast history
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        forecasts = []
        current_date = start_date

        while current_date <= end_date:
            forecasts.append({
                "date": current_date.date(),
                "forecasted_demand": np.random.randint(80, 120),
                "confidence_interval": 0.95
            })
            current_date += timedelta(days=1)

        return forecasts

    def _calculate_mae(self, forecasts: List[Dict[str, Any]], actuals: List[Dict[str, Any]]) -> float:
        """Calculate Mean Absolute Error"""
        if len(forecasts) != len(actuals):
            return 0.0

        errors = []
        for f, a in zip(forecasts, actuals):
            if f["date"] == a["date"]:
                errors.append(abs(f["forecasted_demand"] - a["demand"]))

        return float(np.mean(errors)) if errors else 0.0

    def _calculate_mape(self, forecasts: List[Dict[str, Any]], actuals: List[Dict[str, Any]]) -> float:
        """Calculate Mean Absolute Percentage Error"""
        if len(forecasts) != len(actuals):
            return 0.0

        errors = []
        for f, a in zip(forecasts, actuals):
            if f["date"] == a["date"] and a["demand"] > 0:
                errors.append(abs(f["forecasted_demand"] - a["demand"]) / a["demand"])

        return float(np.mean(errors) * 100) if errors else 0.0

    def _calculate_rmse(self, forecasts: List[Dict[str, Any]], actuals: List[Dict[str, Any]]) -> float:
        """Calculate Root Mean Square Error"""
        if len(forecasts) != len(actuals):
            return 0.0

        errors = []
        for f, a in zip(forecasts, actuals):
            if f["date"] == a["date"]:
                errors.append((f["forecasted_demand"] - a["demand"]) ** 2)

        return float(np.sqrt(np.mean(errors))) if errors else 0.0

    def _get_accuracy_level(self, mape: float) -> str:
        """Get accuracy level based on MAPE"""
        if mape < 10:
            return "excellent"
        elif mape < 20:
            return "good"
        elif mape < 30:
            return "fair"
        else:
            return "poor"





