# CDSS ML Service

AI-Driven Clinical Decision Support System - Machine Learning Service

## Overview

The CDSS ML Service is a FastAPI-based microservice that provides AI-powered clinical decision support, including:

- **Symptom Analysis**: AI-powered symptom analysis using clinical NLP models
- **Drug Interaction Checking**: Comprehensive drug interaction analysis and risk assessment
- **Patient Compliance Monitoring**: IoT-based medication adherence tracking and reporting
- **Demand Forecasting**: Time-series forecasting for drug demand and supply chain optimization
- **Treatment Recommendations**: AI-generated treatment recommendations based on clinical guidelines and literature

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Rails App     │    │   FastAPI ML    │    │   External      │
│   (Frontend)    │◄──►│   Service       │◄──►│   APIs          │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   ML Models     │
                       │   & Services    │
                       └─────────────────┘
```

## Features

### 🧠 AI-Powered Clinical Intelligence
- **Clinical NLP**: BioGPT, PubMedBERT integration for medical text analysis
- **Drug Interactions**: Knowledge graph-based drug interaction analysis
- **Treatment Recommendations**: Evidence-based treatment suggestions
- **Risk Assessment**: Patient-specific risk factor analysis

### 📊 Data Analytics & Forecasting
- **Demand Forecasting**: Prophet-based time-series forecasting
- **Supply Chain Optimization**: Inventory optimization algorithms
- **Compliance Analytics**: Patient adherence pattern analysis
- **Performance Metrics**: ML model performance monitoring

### 🔒 Security & Compliance
- **JWT Authentication**: Secure API access with role-based permissions
- **Audit Logging**: Comprehensive audit trail for compliance
- **Data Encryption**: End-to-end data protection
- **GDPR Compliance**: Patient data privacy controls

## Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + Redis
- **ML Libraries**: PyTorch, Transformers, Scikit-learn, Prophet
- **Monitoring**: Prometheus, Grafana, MLflow
- **Containerization**: Docker + Docker Compose
- **Testing**: Pytest, Coverage

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ml_service

# Copy environment file
cp env.example .env

# Edit environment variables
nano .env
```

### 2. Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f ml-service

# Stop services
docker-compose down
```

### 3. Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export $(cat .env | xargs)

# Run the service
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## API Endpoints

### Authentication
All endpoints require JWT authentication except `/health` and `/docs`.

### Core Endpoints

#### Symptoms Analysis
```http
POST /api/v1/symptoms/analyze_symptoms
GET  /api/v1/symptoms/search
GET  /api/v1/symptoms/autocomplete
```

#### Drug Interactions
```http
POST /api/v1/drug_interactions
GET  /api/v1/drug_interactions/{drug_id}
POST /api/v1/drug_interactions/batch
```

#### Patient Compliance
```http
GET  /api/v1/compliance/{patient_id}
GET  /api/v1/compliance/{patient_id}/medication/{medication_id}
POST /api/v1/compliance/iot_reading
```

#### Demand Forecasting
```http
POST /api/v1/forecast/demand
GET  /api/v1/forecast/{drug_id}
POST /api/v1/forecast/supply_chain
```

#### Treatment Recommendations
```http
POST /api/v1/recommendations
GET  /api/v1/recommendations/history/{patient_id}
POST /api/v1/recommendations/feedback
```

## Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# API Configuration
ML_API_TOKEN=your_token_here
JWT_SECRET_KEY=your_secret_key

# External APIs
OPENAI_API_KEY=your_openai_key
PUBMED_API_KEY=your_pubmed_key
DRUGBANK_API_KEY=your_drugbank_key

# Database
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
```

### Service Configuration

The service can be configured through:

1. **Environment Variables**: Set in `.env` file
2. **Configuration Files**: `app/core/config.py`
3. **Docker Environment**: In `docker-compose.yml`

## Development

### Project Structure

```
ml_service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/          # API endpoint definitions
│   ├── core/                       # Core configuration & security
│   ├── models/                     # ML model definitions
│   └── services/                   # Business logic services
├── tests/                          # Test suite
├── models/                         # Trained ML models
├── logs/                           # Application logs
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── docker-compose.yml             # Service orchestration
└── README.md                      # This file
```

### Adding New Endpoints

1. **Create Service**: Add business logic in `app/services/`
2. **Define Models**: Create Pydantic models in the endpoint file
3. **Add Endpoint**: Implement in `app/api/v1/endpoints/`
4. **Update Router**: Include in the appropriate router
5. **Add Tests**: Create tests in `tests/`

Example:

```python
# app/api/v1/endpoints/new_feature.py
from fastapi import APIRouter, Depends
from app.core.security import require_role

router = APIRouter()

@router.post("/new_feature")
@require_role(["doctor", "admin"])
async def new_feature(data: NewFeatureRequest):
    # Implementation here
    pass
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_symptoms.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black app/ tests/

# Lint code
flake8 app/ tests/

# Type checking
mypy app/
```

## Monitoring & Observability

### Health Checks

```bash
# Service health
curl http://localhost:8001/health

# Detailed health
curl http://localhost:8001/health/detailed
```

### Metrics

- **Prometheus**: Available at `http://localhost:9090`
- **Grafana**: Available at `http://localhost:3000` (admin/admin)
- **MLflow**: Available at `http://localhost:5000`

### Logging

Logs are available in:
- **Console**: During development
- **Files**: In `./logs/` directory
- **Docker**: `docker-compose logs ml-service`

## Deployment

### Production Considerations

1. **Environment**: Set `ENVIRONMENT=production`
2. **Security**: Use strong JWT secrets and API keys
3. **Scaling**: Configure multiple workers in Docker
4. **Monitoring**: Enable all monitoring services
5. **Backup**: Regular database and model backups

### Docker Production

```bash
# Build production image
docker build -t cdss-ml-service:prod .

# Run with production settings
docker run -d \
  -p 8001:8001 \
  -e ENVIRONMENT=production \
  -e DEBUG=false \
  cdss-ml-service:prod
```

### Kubernetes Deployment

See `k8s/` directory for Kubernetes manifests.

## Integration with Rails App

The ML service integrates with the Rails backend through the `MlApiService`:

```ruby
# In Rails app
class MlApiService
  base_uri ENV.fetch('ML_API_URL', 'http://localhost:8001')

  def analyze_symptoms(symptoms_data)
    post('/api/v1/analyze_symptoms', symptoms_data)
  end
end
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Ensure ports 8001, 5432, 6379 are available
2. **Database Connection**: Check PostgreSQL is running and accessible
3. **Redis Connection**: Verify Redis service is running
4. **Permission Issues**: Check file permissions for logs and models directories

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG=true
# or in .env file
DEBUG=true
```

### Log Analysis

```bash
# View real-time logs
tail -f logs/app.log

# Search for errors
grep "ERROR" logs/app.log

# View Docker logs
docker-compose logs -f ml-service
```

## Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Add** tests for new functionality
5. **Ensure** all tests pass
6. **Submit** a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- **Issues**: GitHub Issues
- **Documentation**: API docs at `/docs` when service is running
- **Email**: support@cdss.com

## Roadmap

- [ ] Real ML model integration
- [ ] Advanced NLP capabilities
- [ ] Real-time streaming analytics
- [ ] Advanced forecasting models
- [ ] Integration with more external APIs
- [ ] Advanced security features
- [ ] Performance optimization
- [ ] Additional clinical specialties







