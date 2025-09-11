import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

class SupplyChainService:
    """
    Service for supply chain optimization and inventory management
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.inventory_database = {}  # In production, this would be a database
        self.supplier_database = {}   # In production, this would be a database

    async def optimize_inventory(
        self,
        drug_ids: List[str],
        forecasts: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Optimize inventory levels based on demand forecasts
        """
        try:
            optimizations = []

            for drug_id in drug_ids:
                # Get current inventory
                current_inventory = await self._get_current_inventory(drug_id)

                # Get demand forecast
                drug_forecast = next(
                    (f for f in forecasts.get("drug_forecasts", []) if f["drug_id"] == drug_id),
                    None
                )

                if drug_forecast and current_inventory:
                    optimization = await self._optimize_single_drug(
                        drug_id, current_inventory, drug_forecast
                    )
                    optimizations.append(optimization)

            return optimizations

        except Exception as e:
            self.logger.error(f"Inventory optimization failed: {e}")
            raise

    async def _get_current_inventory(self, drug_id: str) -> Optional[Dict[str, Any]]:
        """Get current inventory for a drug"""

        # Mock inventory data - in production, this would query the database
        mock_inventory = {
            "drug_001": {
                "current_stock": 150,
                "unit_cost": 2.50,
                "reorder_point": 50,
                "lead_time_days": 7,
                "safety_stock": 25,
                "max_stock": 300
            },
            "drug_002": {
                "current_stock": 80,
                "unit_cost": 5.75,
                "reorder_point": 30,
                "lead_time_days": 5,
                "safety_stock": 15,
                "max_stock": 200
            }
        }

        return mock_inventory.get(drug_id)

    async def _optimize_single_drug(
        self,
        drug_id: str,
        current_inventory: Dict[str, Any],
        forecast: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize inventory for a single drug"""

        # Extract forecast data
        predicted_demand = forecast.get("predicted_demand", 100)
        forecast_horizon = forecast.get("forecast_horizon", 30)

        # Calculate daily demand
        daily_demand = predicted_demand / forecast_horizon

        # Calculate lead time demand
        lead_time = current_inventory["lead_time_days"]
        lead_time_demand = daily_demand * lead_time

        # Calculate safety stock
        safety_stock = current_inventory["safety_stock"]

        # Calculate reorder point
        reorder_point = lead_time_demand + safety_stock

        # Calculate optimal order quantity
        optimal_order_quantity = self._calculate_economic_order_quantity(
            daily_demand * 30,  # Monthly demand
            current_inventory["unit_cost"],
            self._get_ordering_cost(drug_id),
            self._get_holding_cost_rate(drug_id)
        )

        # Ensure order quantity doesn't exceed max stock
        max_order_quantity = current_inventory["max_stock"] - current_inventory["current_stock"]
        optimal_order_quantity = min(optimal_order_quantity, max_order_quantity)

        # Calculate total cost
        total_cost = self._calculate_total_cost(
            current_inventory["current_stock"],
            optimal_order_quantity,
            current_inventory["unit_cost"],
            daily_demand
        )

        # Generate recommendations
        recommendations = self._generate_inventory_recommendations(
            current_inventory, reorder_point, optimal_order_quantity
        )

        return {
            "optimization_id": str(uuid.uuid4()),
            "drug_id": drug_id,
            "current_stock": current_inventory["current_stock"],
            "reorder_point": float(reorder_point),
            "optimal_order_quantity": float(optimal_order_quantity),
            "lead_time": current_inventory["lead_time_days"],
            "safety_stock": current_inventory["safety_stock"],
            "total_cost": float(total_cost),
            "cost_breakdown": self._breakdown_costs(
                current_inventory["current_stock"],
                optimal_order_quantity,
                current_inventory["unit_cost"],
                daily_demand
            ),
            "recommendations": recommendations
        }

    def _calculate_economic_order_quantity(
        self,
        annual_demand: float,
        unit_cost: float,
        ordering_cost: float,
        holding_cost_rate: float
    ) -> float:
        """Calculate Economic Order Quantity (EOQ)"""

        if holding_cost_rate <= 0:
            return annual_demand / 12  # Default to monthly ordering

        eoq = np.sqrt((2 * annual_demand * ordering_cost) / (unit_cost * holding_cost_rate))
        return eoq

    def _get_ordering_cost(self, drug_id: str) -> float:
        """Get ordering cost for a drug"""

        # Mock ordering costs - in production, this would query supplier data
        ordering_costs = {
            "drug_001": 25.0,  # $25 per order
            "drug_002": 30.0   # $30 per order
        }

        return ordering_costs.get(drug_id, 25.0)

    def _get_holding_cost_rate(self, drug_id: str) -> float:
        """Get holding cost rate for a drug"""

        # Mock holding cost rates - in production, this would be based on drug characteristics
        holding_rates = {
            "drug_001": 0.20,  # 20% of unit cost per year
            "drug_002": 0.25   # 25% of unit cost per year
        }

        return holding_rates.get(drug_id, 0.20)

    def _calculate_total_cost(
        self,
        current_stock: float,
        order_quantity: float,
        unit_cost: float,
        daily_demand: float
    ) -> float:
        """Calculate total inventory cost"""

        # Holding cost
        average_inventory = (current_stock + order_quantity) / 2
        holding_cost = average_inventory * unit_cost * 0.20 / 365 * 30  # Monthly

        # Ordering cost
        monthly_demand = daily_demand * 30
        orders_per_month = monthly_demand / order_quantity if order_quantity > 0 else 0
        ordering_cost = orders_per_month * 25  # Assume $25 per order

        # Purchase cost
        purchase_cost = order_quantity * unit_cost

        return holding_cost + ordering_cost + purchase_cost

    def _breakdown_costs(
        self,
        current_stock: float,
        order_quantity: float,
        unit_cost: float,
        daily_demand: float
    ) -> Dict[str, float]:
        """Break down inventory costs"""

        # Holding cost
        average_inventory = (current_stock + order_quantity) / 2
        holding_cost = average_inventory * unit_cost * 0.20 / 365 * 30  # Monthly

        # Ordering cost
        monthly_demand = daily_demand * 30
        orders_per_month = monthly_demand / order_quantity if order_quantity > 0 else 0
        ordering_cost = orders_per_month * 25  # Assume $25 per order

        # Purchase cost
        purchase_cost = order_quantity * unit_cost

        return {
            "holding_cost": float(holding_cost),
            "ordering_cost": float(ordering_cost),
            "purchase_cost": float(purchase_cost),
            "total_cost": float(holding_cost + ordering_cost + purchase_cost)
        }

    def _generate_inventory_recommendations(
        self,
        current_inventory: Dict[str, Any],
        reorder_point: float,
        optimal_order_quantity: float
    ) -> List[str]:
        """Generate inventory recommendations"""

        recommendations = []

        # Check if reorder point needs adjustment
        if current_inventory["reorder_point"] != reorder_point:
            recommendations.append(f"Adjust reorder point from {current_inventory['reorder_point']} to {reorder_point:.0f}")

        # Check if current stock is low
        if current_inventory["current_stock"] <= reorder_point:
            recommendations.append("Place order immediately - stock below reorder point")

        # Check if order quantity is optimal
        if optimal_order_quantity > 0:
            recommendations.append(f"Order {optimal_order_quantity:.0f} units to optimize inventory")

        # Check safety stock levels
        if current_inventory["current_stock"] <= current_inventory["safety_stock"]:
            recommendations.append("Stock critically low - expedite order if possible")

        return recommendations

    async def optimize_supply_chain(
        self,
        optimization_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize supply chain for multiple drugs
        """
        try:
            drug_ids = optimization_request.get("drug_ids", [])
            constraints = optimization_request.get("constraints", {})

            # Get current supply chain data
            supply_chain_data = await self._get_supply_chain_data(drug_ids)

            # Apply constraints
            constrained_data = self._apply_supply_chain_constraints(
                supply_chain_data, constraints
            )

            # Optimize routes and suppliers
            optimized_routes = await self._optimize_supply_routes(constrained_data)

            # Calculate cost savings
            cost_savings = self._calculate_supply_chain_savings(
                supply_chain_data, optimized_routes
            )

            return {
                "optimization_id": str(uuid.uuid4()),
                "drug_ids": drug_ids,
                "optimized_routes": optimized_routes,
                "cost_savings": cost_savings,
                "constraints_applied": constraints,
                "recommendations": self._generate_supply_chain_recommendations(
                    optimized_routes, cost_savings
                )
            }

        except Exception as e:
            self.logger.error(f"Supply chain optimization failed: {e}")
            raise

    async def _get_supply_chain_data(self, drug_ids: List[str]) -> Dict[str, Any]:
        """Get supply chain data for drugs"""

        # Mock supply chain data - in production, this would query multiple databases
        supply_chain_data = {}

        for drug_id in drug_ids:
            supply_chain_data[drug_id] = {
                "suppliers": [
                    {
                        "supplier_id": "supplier_001",
                        "name": "Primary Pharma Supplier",
                        "lead_time_days": 7,
                        "unit_cost": 2.50,
                        "reliability": 0.95,
                        "capacity": 1000
                    },
                    {
                        "supplier_id": "supplier_002",
                        "name": "Secondary Pharma Supplier",
                        "lead_time_days": 10,
                        "unit_cost": 2.25,
                        "reliability": 0.90,
                        "capacity": 800
                    }
                ],
                "warehouses": [
                    {
                        "warehouse_id": "warehouse_001",
                        "name": "Main Distribution Center",
                        "location": "London",
                        "capacity": 5000,
                        "handling_cost": 0.10
                    }
                ],
                "transport_routes": [
                    {
                        "route_id": "route_001",
                        "from": "supplier_001",
                        "to": "warehouse_001",
                        "transport_cost": 0.05,
                        "transit_time_days": 2
                    }
                ]
            }

        return supply_chain_data

    def _apply_supply_chain_constraints(
        self,
        supply_chain_data: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply constraints to supply chain optimization"""

        constrained_data = supply_chain_data.copy()

        # Apply budget constraints
        if "max_budget" in constraints:
            for drug_id, data in constrained_data.items():
                for supplier in data["suppliers"]:
                    if supplier["unit_cost"] * supplier["capacity"] > constraints["max_budget"]:
                        supplier["capacity"] = constraints["max_budget"] / supplier["unit_cost"]

        # Apply lead time constraints
        if "max_lead_time" in constraints:
            for drug_id, data in constrained_data.items():
                data["suppliers"] = [
                    s for s in data["suppliers"]
                    if s["lead_time_days"] <= constraints["max_lead_time"]
                ]

        # Apply reliability constraints
        if "min_reliability" in constraints:
            for drug_id, data in constrained_data.items():
                data["suppliers"] = [
                    s for s in data["suppliers"]
                    if s["reliability"] >= constraints["min_reliability"]
                ]

        return constrained_data

    async def _optimize_supply_routes(
        self,
        constrained_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Optimize supply routes based on constraints"""

        optimized_routes = []

        for drug_id, data in constrained_data.items():
            if not data["suppliers"]:
                continue

            # Find best supplier based on cost and reliability
            best_supplier = min(
                data["suppliers"],
                key=lambda s: s["unit_cost"] / s["reliability"]
            )

            # Find best warehouse
            best_warehouse = min(
                data["warehouses"],
                key=lambda w: w["handling_cost"]
            )

            # Find best transport route
            best_route = None
            for route in data["transport_routes"]:
                if (route["from"] == best_supplier["supplier_id"] and
                    route["to"] == best_warehouse["warehouse_id"]):
                    best_route = route
                    break

            if best_route:
                optimized_routes.append({
                    "drug_id": drug_id,
                    "supplier": best_supplier,
                    "warehouse": best_warehouse,
                    "transport_route": best_route,
                    "total_cost": (
                        best_supplier["unit_cost"] +
                        best_warehouse["handling_cost"] +
                        best_route["transport_cost"]
                    ),
                    "total_lead_time": (
                        best_supplier["lead_time_days"] +
                        best_route["transit_time_days"]
                    )
                })

        return optimized_routes

    def _calculate_supply_chain_savings(
        self,
        original_data: Dict[str, Any],
        optimized_routes: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate cost savings from supply chain optimization"""

        # Mock original costs - in production, this would compare with actual costs
        original_total_cost = 0
        optimized_total_cost = 0

        for route in optimized_routes:
            # Assume original cost is 20% higher
            original_cost = route["total_cost"] * 1.2
            original_total_cost += original_cost
            optimized_total_cost += route["total_cost"]

        savings = original_total_cost - optimized_total_cost
        savings_percentage = (savings / original_total_cost * 100) if original_total_cost > 0 else 0

        return {
            "original_cost": float(original_total_cost),
            "optimized_cost": float(optimized_total_cost),
            "savings": float(savings),
            "savings_percentage": float(savings_percentage)
        }

    def _generate_supply_chain_recommendations(
        self,
        optimized_routes: List[Dict[str, Any]],
        cost_savings: Dict[str, Any]
    ) -> List[str]:
        """Generate supply chain recommendations"""

        recommendations = []

        # Cost savings recommendations
        if cost_savings["savings_percentage"] > 10:
            recommendations.append("Significant cost savings achieved - implement immediately")
        elif cost_savings["savings_percentage"] > 5:
            recommendations.append("Moderate cost savings - consider implementation")

        # Route optimization recommendations
        for route in optimized_routes:
            if route["total_lead_time"] > 14:
                recommendations.append(f"Consider alternative suppliers for {route['drug_id']} to reduce lead time")

            if route["supplier"]["reliability"] < 0.95:
                recommendations.append(f"Monitor reliability of {route['supplier']['name']} for {route['drug_id']}")

        # Capacity recommendations
        for route in optimized_routes:
            if route["supplier"]["capacity"] < 500:
                recommendations.append(f"Consider capacity expansion for {route['supplier']['name']}")

        return recommendations

    async def get_supplier_performance(
        self,
        supplier_id: str,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a specific supplier
        """
        try:
            # Mock supplier performance data - in production, this would query historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Generate mock performance metrics
            performance_data = {
                "supplier_id": supplier_id,
                "period_days": days,
                "on_time_deliveries": np.random.randint(80, 98),
                "quality_issues": np.random.randint(0, 5),
                "cost_variance": np.random.uniform(-0.05, 0.05),
                "lead_time_variance": np.random.uniform(-1, 2),
                "overall_score": np.random.uniform(0.85, 0.98)
            }

            # Calculate performance trends
            performance_data["trend"] = self._calculate_performance_trend(performance_data)

            # Generate recommendations
            performance_data["recommendations"] = self._generate_supplier_recommendations(
                performance_data
            )

            return performance_data

        except Exception as e:
            self.logger.error(f"Failed to get supplier performance: {e}")
            raise

    def _calculate_performance_trend(self, performance_data: Dict[str, Any]) -> str:
        """Calculate performance trend"""

        overall_score = performance_data["overall_score"]

        if overall_score > 0.95:
            return "excellent"
        elif overall_score > 0.90:
            return "good"
        elif overall_score > 0.80:
            return "fair"
        else:
            return "poor"

    def _generate_supplier_recommendations(
        self,
        performance_data: Dict[str, Any]
    ) -> List[str]:
        """Generate supplier recommendations based on performance"""

        recommendations = []

        # On-time delivery recommendations
        if performance_data["on_time_deliveries"] < 90:
            recommendations.append("Improve delivery reliability - consider penalties for late deliveries")

        # Quality recommendations
        if performance_data["quality_issues"] > 3:
            recommendations.append("Address quality issues - implement stricter quality control")

        # Cost recommendations
        if performance_data["cost_variance"] > 0.03:
            recommendations.append("Monitor cost increases - negotiate better pricing")

        # Lead time recommendations
        if performance_data["lead_time_variance"] > 1.5:
            recommendations.append("Improve lead time consistency - optimize logistics processes")

        # Overall performance recommendations
        if performance_data["overall_score"] < 0.85:
            recommendations.append("Overall performance below target - develop improvement plan")
        elif performance_data["overall_score"] > 0.95:
            recommendations.append("Excellent performance - consider expanding relationship")

        return recommendations

    async def get_inventory_alerts(self) -> List[Dict[str, Any]]:
        """
        Get inventory alerts for all drugs
        """
        try:
            alerts = []

            # Get all inventory items
            for drug_id in ["drug_001", "drug_002"]:
                inventory = await self._get_current_inventory(drug_id)

                if inventory:
                    # Check for low stock
                    if inventory["current_stock"] <= inventory["reorder_point"]:
                        alerts.append({
                            "alert_id": str(uuid.uuid4()),
                            "drug_id": drug_id,
                            "alert_type": "low_stock",
                            "severity": "medium",
                            "message": f"Stock for {drug_id} is below reorder point ({inventory['current_stock']} units)",
                            "recommendation": "Place order immediately"
                        })

                    # Check for critical stock
                    if inventory["current_stock"] <= inventory["safety_stock"]:
                        alerts.append({
                            "alert_id": str(uuid.uuid4()),
                            "drug_id": drug_id,
                            "alert_type": "critical_stock",
                            "severity": "high",
                            "message": f"Stock for {drug_id} is critically low ({inventory['current_stock']} units)",
                            "recommendation": "Expedite order and consider emergency supply"
                        })

                    # Check for overstock
                    if inventory["current_stock"] > inventory["max_stock"] * 0.9:
                        alerts.append({
                            "alert_id": str(uuid.uuid4()),
                            "drug_id": drug_id,
                            "alert_type": "overstock",
                            "severity": "low",
                            "message": f"Stock for {drug_id} is approaching maximum ({inventory['current_stock']} units)",
                            "recommendation": "Reduce order quantities or delay next order"
                        })

            return alerts

        except Exception as e:
            self.logger.error(f"Failed to get inventory alerts: {e}")
            raise

    async def get_supply_chain_analytics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get supply chain analytics and insights
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Mock analytics data - in production, this would aggregate historical data
            analytics = {
                "period_days": days,
                "total_orders": np.random.randint(50, 200),
                "average_lead_time": np.random.uniform(5, 12),
                "on_time_delivery_rate": np.random.uniform(0.85, 0.98),
                "cost_trend": np.random.uniform(-0.05, 0.05),
                "supplier_performance": {
                    "excellent": np.random.randint(3, 8),
                    "good": np.random.randint(5, 12),
                    "fair": np.random.randint(2, 6),
                    "poor": np.random.randint(0, 3)
                },
                "top_suppliers": [
                    {"name": "Primary Pharma Supplier", "performance": 0.96},
                    {"name": "Secondary Pharma Supplier", "performance": 0.92},
                    {"name": "Tertiary Pharma Supplier", "performance": 0.88}
                ],
                "cost_breakdown": {
                    "purchase_costs": np.random.uniform(0.60, 0.75),
                    "transport_costs": np.random.uniform(0.10, 0.20),
                    "handling_costs": np.random.uniform(0.05, 0.15),
                    "other_costs": np.random.uniform(0.05, 0.10)
                }
            }

            # Calculate insights
            analytics["insights"] = self._generate_supply_chain_insights(analytics)

            # Generate recommendations
            analytics["recommendations"] = self._generate_analytics_recommendations(analytics)

            return analytics

        except Exception as e:
            self.logger.error(f"Failed to get supply chain analytics: {e}")
            raise

    def _generate_supply_chain_insights(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate insights from supply chain analytics"""

        insights = []

        # Lead time insights
        if analytics["average_lead_time"] > 10:
            insights.append("Average lead time is above target - consider supplier optimization")
        elif analytics["average_lead_time"] < 6:
            insights.append("Excellent lead time performance - maintain current supplier relationships")

        # Delivery performance insights
        if analytics["on_time_delivery_rate"] < 0.90:
            insights.append("Delivery performance below target - address supplier reliability issues")
        elif analytics["on_time_delivery_rate"] > 0.95:
            insights.append("Outstanding delivery performance - leverage for cost negotiations")

        # Cost trend insights
        if analytics["cost_trend"] > 0.02:
            insights.append("Costs are increasing - investigate and implement cost controls")
        elif analytics["cost_trend"] < -0.02:
            insights.append("Costs are decreasing - maintain current strategies")

        # Supplier performance insights
        poor_suppliers = analytics["supplier_performance"]["poor"]
        if poor_suppliers > 0:
            insights.append(f"{poor_suppliers} suppliers performing poorly - develop improvement plans")

        return insights

    def _generate_analytics_recommendations(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analytics"""

        recommendations = []

        # Performance-based recommendations
        if analytics["on_time_delivery_rate"] < 0.90:
            recommendations.append("Implement supplier performance improvement programs")
            recommendations.append("Consider alternative suppliers for underperforming partners")

        if analytics["average_lead_time"] > 10:
            recommendations.append("Optimize supplier selection for faster delivery")
            recommendations.append("Implement just-in-time inventory strategies")

        # Cost-based recommendations
        if analytics["cost_trend"] > 0.02:
            recommendations.append("Negotiate better pricing with suppliers")
            recommendations.append("Optimize transport routes to reduce costs")

        # Supplier-based recommendations
        if analytics["supplier_performance"]["poor"] > 0:
            recommendations.append("Develop supplier improvement plans")
            recommendations.append("Consider supplier consolidation for better control")

        # General recommendations
        recommendations.append("Implement regular supplier performance reviews")
        recommendations.append("Develop contingency plans for critical suppliers")

        return recommendations







