from typing import List
from pydantic import BaseModel, Field


class FlowRecord(BaseModel):
    """Single network flow record.

    IMPORTANT:
    - Field names must match the feature names used during training.
    - Types are numeric (int/float).
    - Extend this model to include all your actual features.
    """

    src_port: int = Field(..., description="Source TCP/UDP port of the flow.")
    dst_port: int = Field(..., description="Destination TCP/UDP port of the flow.")

    flow_duration: float = Field(
        ...,
        description="Duration of the flow (e.g. in microseconds or milliseconds).",
    )

    tot_fwd_pkts: float = Field(
        ...,
        description="Total number of packets sent in the forward direction.",
    )
    tot_bwd_pkts: float = Field(
        ...,
        description="Total number of packets sent in the backward direction.",
    )
    tot_fwd_bytes: float = Field(
        ...,
        description="Total number of bytes sent in the forward direction.",
    )
    tot_bwd_bytes: float = Field(
        ...,
        description="Total number of bytes sent in the backward direction.",
    )

    flow_pkts_per_sec: float = Field(
        ...,
        description="Packets per second over the flow duration.",
    )
    flow_bytes_per_sec: float = Field(
        ...,
        description="Bytes per second over the flow duration.",
    )


class PredictRequest(BaseModel):
    records: List[FlowRecord] = Field(
        ...,
        description="List of flow records to score.",
    )


class PredictResponse(BaseModel):
    probabilities: List[float] = Field(
        ...,
        description="Per-record probability that the flow is an Attack (class=1).",
    )
    labels: List[int] = Field(
        ...,
        description="Per-record predicted class labels (0 = Benign, 1 = Attack).",
    )
    model_version: str = Field(
        ...,
        description="Model version string loaded from artifacts.",
    )


class ModelInfoResponse(BaseModel):
    version: str = Field(..., description="Model version currently loaded.")
    target_column: str = Field(..., description="Name of the target column in training data.")
    benign_labels: List[str] = Field(
        ..., description="Raw label values treated as Benign in training."
    )
    feature_count: int = Field(..., description="Number of numeric features used by the model.")
    train_days: List[str] = Field(
        ..., description="Dataset days used for training (from metadata)."
    )
    test_days: List[str] = Field(
        ..., description="Dataset days used for testing (from metadata)."
    )
