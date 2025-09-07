#!/usr/bin/env python3
"""
Basic test script to verify the FastAPI ML service can start and run
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

async def test_imports():
    """Test that all required modules can be imported"""
    try:
        print("Testing imports...")

        # Test core modules
        from app.core.config import settings
        print("✓ Config imported successfully")

        from app.core.security import verify_token, get_current_user
        print("✓ Security imported successfully")

        # Test service modules
        from app.services.symptom_analyzer import SymptomAnalyzer
        print("✓ SymptomAnalyzer imported successfully")

        from app.services.drug_interaction_service import DrugInteractionService
        print("✓ DrugInteractionService imported successfully")

        from app.services.compliance_service import ComplianceService
        print("✓ ComplianceService imported successfully")

        from app.services.forecasting_service import ForecastingService
        print("✓ ForecastingService imported successfully")

        from app.services.recommendation_service import RecommendationService
        print("✓ RecommendationService imported successfully")

        from app.services.iot_service import IoTService
        print("✓ IoTService imported successfully")

        from app.services.supply_chain_service import SupplyChainService
        print("✓ SupplyChainService imported successfully")

        from app.services.drugbank_service import DrugBankService
        print("✓ DrugBankService imported successfully")

        from app.services.clinical_nlp_service import ClinicalNLPService
        print("✓ ClinicalNLPService imported successfully")

        from app.services.clinical_guidelines_service import ClinicalGuidelinesService
        print("✓ ClinicalGuidelinesService imported successfully")

        from app.services.literature_service import LiteratureService
        print("✓ LiteratureService imported successfully")

        # Test API modules
        from app.api.v1.endpoints.symptoms import router as symptoms_router
        print("✓ Symptoms router imported successfully")

        from app.api.v1.endpoints.drug_interactions import router as drug_interactions_router
        print("✓ Drug interactions router imported successfully")

        from app.api.v1.endpoints.compliance import router as compliance_router
        print("✓ Compliance router imported successfully")

        from app.api.v1.endpoints.forecasting import router as forecasting_router
        print("✓ Forecasting router imported successfully")

        from app.api.v1.endpoints.recommendations import router as recommendations_router
        print("✓ Recommendations router imported successfully")

        print("\n✅ All imports successful!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_basic_functionality():
    """Test basic functionality of services"""
    try:
        print("\nTesting basic functionality...")

        # Test symptom analyzer
        symptom_analyzer = SymptomAnalyzer()
        symptoms = await symptom_analyzer.analyze_symptoms(["fever", "cough"])
        print("✓ Symptom analysis working")

        # Test drug interaction service
        drug_service = DrugInteractionService()
        interactions = await drug_service.check_interactions([1, 2], {})
        print("✓ Drug interaction checking working")

        # Test compliance service
        compliance_service = ComplianceService()
        report = await compliance_service.generate_compliance_report(1)
        print("✓ Compliance reporting working")

        # Test forecasting service
        forecasting_service = ForecastingService()
        forecast = await forecasting_service.forecast_drug_demand([{"drug_id": 1, "historical_data": []}])
        print("✓ Forecasting working")

        # Test recommendation service
        recommendation_service = RecommendationService()
        recommendations = await recommendation_service.generate_treatment_recommendations({})
        print("✓ Treatment recommendations working")

        print("\n✅ All basic functionality tests passed!")
        return True

    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

async def test_configuration():
    """Test configuration loading"""
    try:
        print("\nTesting configuration...")

        from app.core.config import settings

        # Check essential settings
        assert settings.app_name == "CDSS ML Service"
        assert settings.app_version == "1.0.0"
        assert settings.server_host == "0.0.0.0"
        assert settings.server_port == 8001

        print("✓ Configuration loaded successfully")
        print(f"  - App Name: {settings.app_name}")
        print(f"  - Version: {settings.app_version}")
        print(f"  - Server: {settings.server_host}:{settings.server_port}")
        print(f"  - Environment: {settings.environment}")

        return True

    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 CDSS ML Service - Basic Test Suite")
    print("=" * 50)

    # Run tests
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_configuration),
        ("Functionality Test", test_basic_functionality),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        result = await test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! The service is ready to run.")
        print("\nTo start the service:")
        print("  python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload")
        print("\nOr using Docker:")
        print("  docker-compose up -d")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Unexpected error: {e}")
        sys.exit(1)





