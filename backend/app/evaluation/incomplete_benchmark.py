"""Repeated Deterministic Masking Experiments for Incomplete Symptom Evaluation.

Evaluates Rough Set Recommender vs Baseline ML Models under missing symptom rates:
- 0% missing
- 10% missing
- 30% missing
- 50% missing
- 70% missing

Runs repeated deterministic masking iterations using fixed seeds.
Records prediction accuracy, F1, top-3 accuracy, and per-query latencies.
"""

from typing import Dict, List, Optional, Any
import time
import numpy as np
import pandas as pd

from app.rst.decision_table import DecisionTable
from app.rst.engine import RoughSetRecommender
from app.ml.baseline_models import MLBaselines
from app.evaluation.evaluator import ModelEvaluator
from app.core.config import settings


class IncompleteBenchmarkRunner:
    """Orchestrates reproducible benchmarking of incomplete symptom sets."""

    def __init__(
        self,
        recommender: RoughSetRecommender,
        ml_baselines: MLBaselines,
        test_df: pd.DataFrame,
    ):
        self.recommender = recommender
        self.ml_baselines = ml_baselines
        self.test_df = test_df.copy()
        if "Unnamed: 133" in self.test_df.columns:
            self.test_df = self.test_df.drop(columns=["Unnamed: 133"], errors="ignore")
        self.test_df = self.test_df.loc[:, ~self.test_df.columns.str.contains("^Unnamed")]

        self.condition_attrs = [c for c in self.test_df.columns if c != "prognosis"]
        self.num_attrs = len(self.condition_attrs)
        self.all_classes = recommender.table.decision_classes

    def run_benchmark(
        self,
        missing_rates: Optional[List[float]] = None,
        repetitions: int = settings.BENCHMARK_REPETITIONS,
        base_seed: int = settings.RANDOM_SEED,
    ) -> Dict[str, Any]:
        """Execute the benchmark suite across all missing symptom ratios."""
        if missing_rates is None:
            missing_rates = settings.BENCHMARK_MISSING_RATES

        benchmark_results: Dict[str, Any] = {
            "missing_rates": missing_rates,
            "repetitions_per_rate": repetitions,
            "base_seed": base_seed,
            "test_sample_count": len(self.test_df),
            "results_by_rate": {},
            "comparison_summary": [],
        }

        for rate in missing_rates:
            rate_key = f"{int(rate * 100)}%_missing"
            rate_summary = {
                "missing_rate": rate,
                "percentage_label": f"{int(rate * 100)}%",
                "repetitions": [],
                "rst_metrics_aggregated": {},
                "ml_metrics_aggregated": {},
            }

            rst_acc_list = []
            rst_top3_list = []
            rst_f1_list = []
            rst_latency_list = []

            ml_acc_dict: Dict[str, List[float]] = {
                model_name: [] for model_name in ["RandomForest", "MultinomialNB", "LogisticRegression", "DecisionTree"]
            }

            for rep in range(repetitions):
                seed = base_seed + rep * 1000 + int(rate * 100)
                rng = np.random.default_rng(seed)

                y_true: List[str] = []
                rst_preds: List[str] = []
                rst_top3_preds: List[List[str]] = []
                latencies_ms: List[float] = []

                ml_preds: Dict[str, List[str]] = {m: [] for m in ml_acc_dict.keys()}

                for _, row in self.test_df.iterrows():
                    true_disease = str(row["prognosis"])
                    y_true.append(true_disease)

                    # Build masked query
                    raw_symptoms = {c: int(row[c]) for c in self.condition_attrs}
                    masked_query = dict(raw_symptoms)

                    if rate > 0.0:
                        # Randomly select a fraction of attributes to mask to '?'
                        mask_count = int(round(rate * self.num_attrs))
                        masked_indices = rng.choice(self.num_attrs, size=mask_count, replace=False)
                        for idx in masked_indices:
                            attr_name = self.condition_attrs[idx]
                            masked_query[attr_name] = "?"

                    # Evaluate RST Recommender
                    t0 = time.time()
                    rec_result = self.recommender.recommend(masked_query, top_k=3)
                    lat_ms = (time.time() - t0) * 1000.0
                    latencies_ms.append(lat_ms)

                    primary = rec_result.get("primary_recommendation")
                    pred_disease = primary["disease"] if primary else "Unknown"
                    rst_preds.append(pred_disease)

                    candidates = [c["disease"] for c in rec_result.get("top_candidates", [])]
                    rst_top3_preds.append(candidates)

                    # Evaluate ML Baselines
                    ml_res = self.ml_baselines.predict_query(masked_query, top_k=3)
                    for m_name in ml_preds.keys():
                        ml_preds[m_name].append(ml_res[m_name]["predicted_disease"])

                # Calculate repetition metrics for RST
                rep_eval = ModelEvaluator.evaluate_predictions(
                    y_true=y_true,
                    y_pred=rst_preds,
                    top_k_preds=rst_top3_preds,
                    all_classes=self.all_classes,
                    latencies_ms=latencies_ms,
                )

                rst_acc_list.append(rep_eval["accuracy"])
                rst_top3_list.append(rep_eval["top3_accuracy"])
                rst_f1_list.append(rep_eval["f1_weighted"])
                rst_latency_list.append(rep_eval["latency"]["mean_ms"])

                # Calculate ML accuracies for this repetition
                for m_name in ml_preds.keys():
                    ml_eval = ModelEvaluator.evaluate_predictions(
                        y_true=y_true,
                        y_pred=ml_preds[m_name],
                        all_classes=self.all_classes,
                    )
                    ml_acc_dict[m_name].append(ml_eval["accuracy"])

                rate_summary["repetitions"].append({
                    "rep_index": rep,
                    "seed": seed,
                    "rst_accuracy": rep_eval["accuracy"],
                    "rst_top3_accuracy": rep_eval["top3_accuracy"],
                    "rst_f1": rep_eval["f1_weighted"],
                    "mean_latency_ms": rep_eval["latency"]["mean_ms"],
                })

            # Aggregated metrics for this missing rate
            rate_summary["rst_metrics_aggregated"] = {
                "mean_accuracy": round(float(np.mean(rst_acc_list)), 4),
                "std_accuracy": round(float(np.std(rst_acc_list)), 4),
                "mean_top3_accuracy": round(float(np.mean(rst_top3_list)), 4),
                "std_top3_accuracy": round(float(np.std(rst_top3_list)), 4),
                "mean_f1": round(float(np.mean(rst_f1_list)), 4),
                "std_f1": round(float(np.std(rst_f1_list)), 4),
                "mean_latency_ms": round(float(np.mean(rst_latency_list)), 3),
            }

            rate_summary["ml_metrics_aggregated"] = {
                m_name: {
                    "mean_accuracy": round(float(np.mean(accs)), 4),
                    "std_accuracy": round(float(np.std(accs)), 4),
                }
                for m_name, accs in ml_acc_dict.items()
            }

            benchmark_results["results_by_rate"][rate_key] = rate_summary

            # Add to comparison summary
            summary_row = {
                "missing_rate": rate,
                "percentage": f"{int(rate * 100)}%",
                "RST_accuracy": round(float(np.mean(rst_acc_list)), 4),
                "RST_top3_accuracy": round(float(np.mean(rst_top3_list)), 4),
                "RST_f1": round(float(np.mean(rst_f1_list)), 4),
            }
            for m_name, accs in ml_acc_dict.items():
                summary_row[f"{m_name}_accuracy"] = round(float(np.mean(accs)), 4)
            benchmark_results["comparison_summary"].append(summary_row)

        return benchmark_results
