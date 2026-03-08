"""
ML Model Runner — loads the trained AMR prediction model and runs inference.

The model is loaded once at module import time (singleton pattern) so that
it stays in memory across requests, avoiding repeated disk I/O.
"""

import os

import joblib
import numpy as np

from app.config import MODEL_PATH

# ─── Antibiotic mapping ──────────────────────────────────────────────────────
# The model predicts a class for each of these antibiotics (in order).

ANTIBIOTICS: list[str] = ["ciprofloxacin", "ampicillin", "tetracycline"]

# Class labels produced by the model
RESISTANCE_LABELS: dict[int, str] = {
    0: "Susceptible",
    1: "Intermediate",
    2: "Resistant",
}

# ─── Model loading (singleton) ───────────────────────────────────────────────

_model = None


def _load_model():
    """Load the model from disk once and cache it in a module-level variable."""
    global _model
    if _model is not None:
        return _model

    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(
            f"Model file not found at '{MODEL_PATH}'. "
            "Please place a trained model.pkl in the project root."
        )

    _model = joblib.load(MODEL_PATH)
    return _model


def predict_resistance(genes: list[int]) -> dict[str, str]:
    """
    Predict antibiotic resistance from a gene presence vector.

    Args:
        genes: Binary list (e.g. [1, 0, 1, 0, 0]) from the gene scanner.

    Returns:
        Dictionary mapping antibiotic names to predicted resistance status.
        Example: {"ciprofloxacin": "Resistant", "ampicillin": "Susceptible", ...}

    Raises:
        FileNotFoundError: If model.pkl is missing.
        RuntimeError: If prediction fails for any reason.
    """
    model = _load_model()

    try:
        # Reshape to (1, n_features) for a single sample
        input_array = np.array(genes).reshape(1, -1)
        raw_predictions = model.predict(input_array)
    except Exception as e:
        raise RuntimeError(f"Model prediction failed: {e}") from e

    # Map numeric predictions to human-readable labels
    predictions: dict[str, str] = {}
    for i, antibiotic in enumerate(ANTIBIOTICS):
        class_id = int(raw_predictions[0][i])
        predictions[antibiotic] = RESISTANCE_LABELS.get(class_id, "Unknown")

    return predictions
