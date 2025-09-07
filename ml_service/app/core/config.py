from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "CDSS ML Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React frontend
        "http://localhost:3001",  # Rails backend
        "http://localhost:3002",  # Other services
    ]

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/cdss_ml")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # ML Models
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")
    DRUG_INTERACTION_MODEL: str = os.getenv("DRUG_INTERACTION_MODEL", "drug_interaction_model.pkl")
    SYMPTOM_ANALYSIS_MODEL: str = os.getenv("SYMPTOM_ANALYSIS_MODEL", "symptom_analysis_model.pkl")
    FORECASTING_MODEL: str = os.getenv("FORECASTING_MODEL", "forecasting_model.pkl")

    # External APIs
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    PUBMED_API_KEY: Optional[str] = os.getenv("PUBMED_API_KEY")
    DRUGBANK_USERNAME: Optional[str] = os.getenv("DRUGBANK_USERNAME")
    DRUGBANK_PASSWORD: Optional[str] = os.getenv("DRUGBANK_PASSWORD")

    # MLflow
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    MLFLOW_EXPERIMENT_NAME: str = "cdss_clinical_models"

    # Monitoring
    PROMETHEUS_PORT: int = 8002
    LOG_LEVEL: str = "INFO"

    # NHS Integration
    NHS_API_KEY: Optional[str] = os.getenv("NHS_API_KEY")
    NHS_API_BASE_URL: str = os.getenv("NHS_API_BASE_URL", "https://api.nhs.uk")

    # Drug Data Sources
    DRUGBANK_URL: str = "https://go.drugbank.com"
    SIDER_URL: str = "http://sideeffects.embl.de"
    RX_NORM_URL: str = "https://www.nlm.nih.gov/research/umls/rxnorm"

    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

