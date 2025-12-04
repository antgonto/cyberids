from ninja import Router
import pandas as pd

from .schemas import PredictRequest, PredictResponse, ModelInfoResponse
from .services import load_artifacts, predict_from_dataframe

router = Router(tags=["cyber-ids"])


@router.post("/ml/predict", response=PredictResponse)
def predict(request, payload: PredictRequest):
    records = [r.dict() for r in payload.records]
    df = pd.DataFrame.from_records(records)

    proba, labels, artifacts = predict_from_dataframe(df, name="X_api_request")

    return PredictResponse(
        probabilities=proba.tolist(),
        labels=labels.tolist(),
        model_version=artifacts.version,
    )


@router.get("/ml/model_info", response=ModelInfoResponse)
def model_info(request):
    artifacts = load_artifacts()
    meta = artifacts.metadata

    target_column = meta.get("target_column", "Label")
    benign_labels = meta.get("benign_labels", ["Benign"])
    train_days = meta.get("train_days", [])
    test_days = meta.get("test_days", [])

    return ModelInfoResponse(
        version=artifacts.version,
        target_column=target_column,
        benign_labels=benign_labels,
        feature_count=len(artifacts.feature_names),
        train_days=train_days,
        test_days=test_days,
    )
