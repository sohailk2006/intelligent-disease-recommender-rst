"""Academic Evaluation Suite for Disease Prediction Models.

Calculates:
- Overall Accuracy
- Top-3 Accuracy
- Macro & Weighted Precision, Recall, and F1-score
- Multi-class Confusion Matrix
- Per-Disease Classification Report
- Prediction Latency (mean, p50, p95 in milliseconds)
"""

from typing import Dict, List, Optional, Tuple, Any
import time
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)


class ModelEvaluator:
    """Evaluates classification performance across multiple metrics."""

    @staticmethod
    def evaluate_predictions(
        y_true: List[str],
        y_pred: List[str],
        top_k_preds: Optional[List[List[str]]] = None,
        all_classes: Optional[List[str]] = None,
        latencies_ms: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Compute full suite of classification metrics.

        Args:
            y_true: Ground truth disease labels.
            y_pred: Predicted primary disease labels.
            top_k_preds: List of top-k candidate lists per sample.
            all_classes: Complete list of disease class names.
            latencies_ms: List of per-query latency measurements in ms.

        Returns:
            Dictionary containing comprehensive metrics.
        """
        if all_classes is None:
            all_classes = sorted(list(set(y_true + y_pred)))

        acc = float(accuracy_score(y_true, y_pred))

        # Precision, Recall, F1 (macro and weighted)
        p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=all_classes, average="macro", zero_division=0
        )
        p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(
            y_true, y_pred, labels=all_classes, average="weighted", zero_division=0
        )

        # Top-3 Accuracy
        top3_acc = None
        if top_k_preds is not None and len(top_k_preds) == len(y_true):
            top3_correct = sum(
                1 for true_lbl, candidates in zip(y_true, top_k_preds)
                if true_lbl in candidates[:3]
            )
            top3_acc = float(top3_correct / len(y_true))

        # Confusion Matrix
        cm = confusion_matrix(y_true, y_pred, labels=all_classes)

        # Per-class metrics
        per_p, per_r, per_f1, per_sup = precision_recall_fscore_support(
            y_true, y_pred, labels=all_classes, average=None, zero_division=0
        )
        per_disease = {}
        for idx, cls_name in enumerate(all_classes):
            per_disease[cls_name] = {
                "precision": round(float(per_p[idx]), 4),
                "recall": round(float(per_r[idx]), 4),
                "f1_score": round(float(per_f1[idx]), 4),
                "support": int(per_sup[idx]),
            }

        # Latency statistics
        latency_stats = {}
        if latencies_ms and len(latencies_ms) > 0:
            arr_lat = np.array(latencies_ms)
            latency_stats = {
                "mean_ms": round(float(np.mean(arr_lat)), 3),
                "p50_ms": round(float(np.median(arr_lat)), 3),
                "p95_ms": round(float(np.percentile(arr_lat, 95)), 3),
                "min_ms": round(float(np.min(arr_lat)), 3),
                "max_ms": round(float(np.max(arr_lat)), 3),
            }

        return {
            "accuracy": round(acc, 4),
            "top3_accuracy": round(top3_acc, 4) if top3_acc is not None else None,
            "precision_macro": round(float(p_macro), 4),
            "recall_macro": round(float(r_macro), 4),
            "f1_macro": round(float(f1_macro), 4),
            "precision_weighted": round(float(p_weighted), 4),
            "recall_weighted": round(float(r_weighted), 4),
            "f1_weighted": round(float(f1_weighted), 4),
            "confusion_matrix": cm.tolist(),
            "class_labels": all_classes,
            "per_disease": per_disease,
            "latency": latency_stats,
            "total_samples": len(y_true),
        }
