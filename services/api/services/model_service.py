"""MLflow model loading and inference service.

Loads the Staging XGBoost model from the MLflow Model Registry at
application startup (via lifespan) and keeps it in memory for the
lifetime of the process.

Model versioning
----------------
The active model version is read from the ``MODEL_VERSION`` environment
variable (defaults to ``Staging``).  Upgrading to a new version requires
restarting the API container — no hot-swap is implemented in Phase 6.

Thread safety
-------------
XGBoost inference is CPU-bound and thread-safe.  Concurrent FastAPI
requests run in the same event loop and call ``predict_proba`` via
``asyncio.to_thread``, so the model is shared but never mutated after
loading.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass

import numpy as np

log = logging.getLogger(__name__)

_DEFAULT_MODEL_NAME = "hereditary-risk-xgboost"
_DEFAULT_MODEL_STAGE = "Staging"


@dataclass
class ModelInfo:
    """Metadata about the loaded model version.

    Attributes:
        model_name: Registered model name in MLflow.
        version: Model version string.
        run_id: MLflow run ID that produced this model.
        feature_names: Ordered feature column names used during training.
    """

    model_name: str
    version: str
    run_id: str
    feature_names: list[str]


class ModelService:
    """Holds the loaded model and provides inference + SHAP methods.

    Attributes:
        info: Loaded model metadata.
    """

    def __init__(self) -> None:
        self._xgb_model: object | None = None  # xgboost.XGBClassifier
        self.info: ModelInfo | None = None

    def load(
        self,
        tracking_uri: str,
        model_name: str = _DEFAULT_MODEL_NAME,
        stage: str = _DEFAULT_MODEL_STAGE,
    ) -> None:
        """Load the model from the MLflow Model Registry.

        Args:
            tracking_uri: MLflow tracking server URI.
            model_name: Registered model name.
            stage: Model stage to load (``Staging``, ``Production``, etc.).

        Raises:
            RuntimeError: If no model is registered at the given stage.
        """
        import mlflow
        import mlflow.xgboost

        mlflow.set_tracking_uri(tracking_uri)
        model_uri = f"models:/{model_name}/{stage}"
        log.info("Loading model from %s", model_uri)

        try:
            self._xgb_model = mlflow.xgboost.load_model(model_uri)
        except Exception as exc:
            raise RuntimeError(
                f"Failed to load model '{model_name}' stage='{stage}' from {tracking_uri}: {exc}"
            ) from exc

        # Retrieve model metadata for the response
        client = mlflow.tracking.MlflowClient()
        versions = client.get_latest_versions(model_name, stages=[stage])
        if not versions:
            raise RuntimeError(f"No model version found for {model_name}/{stage}")

        mv = versions[0]
        run_data = client.get_run(mv.run_id).data

        # Feature names are stored as a tag by train_xgboost.py (or derived from booster)
        try:
            feat_names = list(self._xgb_model.feature_names_in_)  # type: ignore[union-attr]
        except AttributeError:
            # Fall back to the registry's feature_columns if available
            feat_names = run_data.tags.get("feature_columns", "").split(",") or []

        self.info = ModelInfo(
            model_name=model_name,
            version=mv.version,
            run_id=mv.run_id,
            feature_names=feat_names,
        )
        log.info(
            "Model loaded: %s v%s  (run_id=%s, features=%d)",
            model_name, mv.version, mv.run_id, len(feat_names),
        )

    def _build_input(self, features: dict[str, object]) -> np.ndarray:
        """Build an ordered numpy row from a feature dict.

        Unknown features default to 0.  None values default to 0
        (median imputation should have been applied upstream).

        Args:
            features: Feature name → value dict.

        Returns:
            Float32 array of shape (1, n_features).
        """
        if self.info is None:
            raise RuntimeError("Model is not loaded")
        row = [float(features.get(name) or 0.0) for name in self.info.feature_names]
        return np.array([row], dtype=np.float32)

    def predict_proba_sync(self, features: dict[str, object]) -> float:
        """Return the calibrated positive-class probability synchronously.

        Args:
            features: Feature dict.

        Returns:
            Probability in [0, 1].

        Raises:
            RuntimeError: If the model is not loaded.
        """
        if self._xgb_model is None:
            raise RuntimeError("Model is not loaded — call load() at startup")
        X = self._build_input(features)
        proba: np.ndarray = self._xgb_model.predict_proba(X)  # type: ignore[union-attr]
        return float(proba[0, 1])

    async def predict_proba(self, features: dict[str, object]) -> float:
        """Async wrapper around ``predict_proba_sync``.

        Args:
            features: Feature dict.

        Returns:
            Probability in [0, 1].
        """
        return await asyncio.to_thread(self.predict_proba_sync, features)

    def shap_values_sync(
        self,
        features: dict[str, object],
        top_n: int = 5,
    ) -> list[dict[str, object]]:
        """Compute top-N SHAP contributions synchronously.

        Args:
            features: Feature dict (same keys as training features).
            top_n: Number of contributors to return.

        Returns:
            List of dicts with keys ``feature``, ``raw_value``,
            ``shap_value``, ``direction``.

        Raises:
            ImportError: If the ``shap`` package is not installed.
        """
        if self._xgb_model is None or self.info is None:
            raise RuntimeError("Model is not loaded")
        try:
            import shap
        except ImportError as exc:
            raise ImportError("Install 'shap' for explanation support") from exc

        X = self._build_input(features)
        explainer = shap.TreeExplainer(self._xgb_model)
        sv = explainer.shap_values(X)[0]  # shape: (n_features,)

        pairs = sorted(
            zip(self.info.feature_names, sv.tolist()),
            key=lambda x: abs(x[1]),
            reverse=True,
        )[:top_n]

        return [
            {
                "feature": name,
                "raw_value": float(features.get(name) or 0.0),
                "shap_value": float(val),
                "direction": "increases_risk" if val > 0 else "decreases_risk",
            }
            for name, val in pairs
        ]

    async def shap_values(
        self,
        features: dict[str, object],
        top_n: int = 5,
    ) -> list[dict[str, object]]:
        """Async wrapper around ``shap_values_sync``.

        Args:
            features: Feature dict.
            top_n: Number of top contributors.

        Returns:
            List of SHAP contribution dicts.
        """
        return await asyncio.to_thread(self.shap_values_sync, features, top_n)

    @property
    def is_loaded(self) -> bool:
        """True if the model has been successfully loaded."""
        return self._xgb_model is not None
