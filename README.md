# Cyber IDS - Intrusion Detection System API

A production-ready Django Ninja API for network intrusion detection using machine learning. This system classifies network flows as **Attack** or **Benign** using a trained model on the CSE-CIC-IDS2018 dataset.

## Features

- **Binary Classification**: Detects attack vs. benign network flows
- **REST API**: Django Ninja-powered endpoints for predictions and model info
- **Artifact Management**: Automatic loading and caching of ML model artifacts
- **Production Ready**: Configurable thresholds, versioned models, and sanitized inputs

## Requirements

- Python 3.11+
- Django 5.x
- Django Ninja
- scikit-learn
- pandas
- numpy
- joblib

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/antgonto/cyberids.git
cd cyberids
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install django django-ninja pandas numpy scikit-learn joblib
```

### 4. Apply Database Migrations

```bash
python manage.py migrate
```

### 5. Verify Model Artifacts

Ensure the following artifact files exist in the `cyber_ids/artifacts/` directory (inside the `cyber_ids` app folder):

```
cyber_ids/
└── artifacts/
    ├── meta/
    │   ├── cyber_ids_features_<version>.json
    │   ├── cyber_ids_metadata_<version>.json
    │   └── cyber_ids_sanitizer_<version>.joblib
    └── models/
        └── cyber_ids_champion_<version>.joblib
```

These artifacts are generated from the training notebook and are required for the API to function.

## Running the Server

### Development Server

```bash
python manage.py runserver 8000
```

The API will be available at: `http://127.0.0.1:8000/api/`

### Check Configuration

```bash
python manage.py check
```

## API Endpoints

Base URL: `http://127.0.0.1:8000/api/`

### Interactive API Documentation

Visit `http://127.0.0.1:8000/api/docs` for the Swagger UI documentation.

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cyber-ids/ml/predict` | Predict attack/benign for network flows |
| GET | `/api/cyber-ids/ml/model_info` | Get current model version and metadata |

### Example: Predict Request

```bash
curl -X POST http://127.0.0.1:8000/api/cyber-ids/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "records": [
      {
        "src_port": 443,
        "dst_port": 52431,
        "flow_duration": 1000000,
        "tot_fwd_pkts": 10,
        "tot_bwd_pkts": 8,
        "tot_fwd_bytes": 1500,
        "tot_bwd_bytes": 2000,
        "flow_pkts_per_sec": 18.0,
        "flow_bytes_per_sec": 3500.0
      }
    ]
  }'
```

### Example: Response

```json
{
  "probabilities": [0.12],
  "labels": [0],
  "model_version": "20251204-040056"
}
```

- `probabilities`: Attack probability (0.0 - 1.0)
- `labels`: 0 = Benign, 1 = Attack
- `model_version`: Version of the loaded model

### Example: Model Info Request

```bash
curl http://127.0.0.1:8000/api/cyber-ids/ml/model_info
```

## Project Structure

```
cyberids/
├── manage.py                 # Django management script
├── config/                   # Django project configuration
│   ├── settings.py
│   ├── urls.py               # Main URL configuration with Ninja API
│   ├── wsgi.py
│   └── asgi.py
├── cyber_ids/                # Main application
│   ├── api.py                # Django Ninja router and endpoints
│   ├── schemas.py            # Pydantic request/response models
│   ├── services.py           # ML inference and artifact loading
│   ├── artifacts_config.py   # Artifact paths configuration
│   └── artifacts/            # ML model artifacts
│       ├── meta/             # Feature lists, metadata, sanitizers
│       └── models/           # Trained model files
└── README.md
```

## Configuration

### Environment Variables (Optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings` | Django settings module |
| `DEBUG` | `True` | Enable debug mode (set to `False` in production) |

### Decision Threshold

The default decision threshold is `0.5`. To adjust:

1. Edit `cyber_ids/artifacts_config.py`
2. Modify `DEFAULT_DECISION_THRESHOLD`

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

### Production Checklist

- [ ] Set `DEBUG = False` in settings
- [ ] Configure `ALLOWED_HOSTS`
- [ ] Set a secure `SECRET_KEY` via environment variable
- [ ] Use HTTPS in production
- [ ] Configure proper logging

## License

See [LICENSE](LICENSE) for details.

## Author

Antonio González-Torres - NYU Tandon School of Engineering

