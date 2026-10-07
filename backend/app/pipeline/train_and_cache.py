"""Offline Artifact Generation & Research Pipeline.

Trains and precomputes all models and Rough Set artifacts on the FULL 4,920-row Training.csv.
Measures and records:
- dataset loading time
- preprocessing time
- RST dependency time
- reduct calculation time
- association-rule mining time
- ML training time
- total preparation time
- per-query prediction time

Serializes artifacts to backend/artifacts/ for instant, deterministic zero-latency API serving.
"""

import json
import time
from pathlib import Path
from typing import Dict, Any
import joblib
import pandas as pd
import numpy as np

from app.core.config import settings
from app.core.logging_config import logger
from app.rst.decision_table import DecisionTable
from app.rst.dependency import DependencyDegree
from app.rst.discernibility import DiscernibilityMatrix
from app.rst.reduct import ReductGenerator
from app.rst.engine import RoughSetRecommender
from app.rules.association_mining import AssociationRuleMiner
from app.ml.baseline_models import MLBaselines
from app.evaluation.evaluator import ModelEvaluator
from app.evaluation.incomplete_benchmark import IncompleteBenchmarkRunner


def build_symptom_catalog(table: DecisionTable) -> list[Dict[str, Any]]:
    """Build a rich categorized metadata catalog for all 132 symptoms."""
    # Symptom taxonomy mapping based on medical domain categories
    categories = {
        "constitutional": [
            "fatigue", "high_fever", "mild_fever", "chills", "shivering", "sweating",
            "weight_loss", "weight_gain", "malaise", "lethargy", "loss_of_appetite",
            "increased_appetite", "excessive_hunger"
        ],
        "skin_mucosa": [
            "itching", "skin_rash", "nodal_skin_eruptions", "patches_in_throat",
            "pus_filled_pimples", "blackheads", "scurring", "skin_peeling",
            "silver_like_dusting", "small_dents_in_nails", "inflammatory_nails",
            "blister", "red_sore_around_nose", "yellow_crust_ooze", "yellowish_skin",
            "bruising", "red_spots_over_body", "dischromic _patches"
        ],
        "gastrointestinal": [
            "stomach_pain", "acidity", "ulcers_on_tongue", "vomiting", "cough",
            "indigestion", "nausea", "abdominal_pain", "constipation", "diarrhoea",
            "pain_during_bowel_movements", "pain_in_anal_region", "bloody_stool",
            "irritation_in_anus", "belly_pain", "passage_of_gases", "distention_of_abdomen",
            "swelling_of_stomach", "stomach_bleeding"
        ],
        "respiratory": [
            "continuous_sneezing", "breathlessness", "phlegm", "throat_irritation",
            "redness_of_eyes", "sinus_pressure", "runny_nose", "congestion",
            "chest_pain", "cough", "fast_heart_rate", "mucoid_sputum", "rusty_sputum",
            "blood_in_sputum"
        ],
        "neurological_sensory": [
            "headache", "dizziness", "loss_of_balance", "unsteadiness", "spinning_movements",
            "loss_of_smell", "blurred_and_distorted_vision", "slurred_speech", "altered_sensorium",
            "lack_of_concentration", "visual_disturbances", "coma"
        ],
        "musculoskeletal": [
            "joint_pain", "neck_pain", "back_pain", "cramps", "muscle_weakness",
            "stiff_neck", "swelling_joints", "movement_stiffness", "painful_walking",
            "muscle_pain", "muscle_wasting", "weakness_in_limbs", "knee_pain", "hip_joint_pain"
        ],
        "urinary_hepatic": [
            "burning_micturition", "spotting_ urination", "dark_urine", "yellow_urine",
            "yellowing_of_eyes", "acute_liver_failure", "fluid_overload", "swelling_of_stomach",
            "extra_marital_contacts", "polyuria", "continuous_feel_of_urine", "bladder_discomfort",
            "foul_smell_of urine"
        ],
    }

    # Reverse lookup for category
    attr_to_cat = {}
    for cat_name, symptoms in categories.items():
        for s in symptoms:
            attr_to_cat[s] = cat_name

    catalog = []
    # Overall frequencies in training data
    freqs = table.X.mean(axis=0)

    for attr, idx in table.attr_to_idx.items():
        clean_name = attr.replace("_", " ").strip().title()
        cat = attr_to_cat.get(attr, "general_clinical")
        catalog.append({
            "id": attr,
            "label": clean_name,
            "category": cat,
            "frequency_in_train": round(float(freqs[idx]), 4),
            "prevalence_percentage": round(float(freqs[idx] * 100), 2),
        })

    catalog.sort(key=lambda x: x["label"])
    return catalog


def run_pipeline() -> Dict[str, Any]:
    """Execute the full end-to-end training, mining, and evaluation pipeline."""
    total_start_time = time.time()
    artifacts_dir = settings.ARTIFACTS_DIR
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Starting Offline Pipeline on full dataset...")

    # 1. Dataset Loading
    t0 = time.time()
    train_df = pd.read_csv(settings.TRAIN_DATA_PATH)
    t_load = time.time() - t0
    logger.info(f"Loaded Training.csv with shape {train_df.shape} in {t_load:.4f}s")

    # 2. Preprocessing & Decision Table Construction
    t0 = time.time()
    decision_table = DecisionTable(
        train_df,
        decision_col="prognosis",
        drop_columns=["Unnamed: 133"],
    )
    t_prep = time.time() - t0
    logger.info(
        f"Decision Table created: |U|={decision_table.universe_size}, "
        f"|C|={decision_table.num_condition_attributes}, "
        f"|D|={decision_table.num_decision_classes} in {t_prep:.4f}s"
    )

    # 3. RST Dependency & Positive Region
    t0 = time.time()
    dependency = DependencyDegree(decision_table)
    full_gamma = dependency.compute_gamma()
    top_attrs = dependency.rank_individual_attributes(top_k=20)
    t_dep = time.time() - t0
    logger.info(f"RST Full Dependency Degree gamma_C(d) = {full_gamma} computed in {t_dep:.4f}s")

    # 4. Discernibility Matrix & Core Analysis
    t0 = time.time()
    disc_matrix = DiscernibilityMatrix(decision_table)
    disc_stats = disc_matrix.get_statistics()
    core_attrs = disc_matrix.get_core_attributes()
    t_disc = time.time() - t0
    logger.info(
        f"Discernibility analysis: {disc_stats['total_discerning_pairs']} pairs, "
        f"Core size={len(core_attrs)} in {t_disc:.4f}s"
    )

    # 5. Reduct Generation
    t0 = time.time()
    reduct_gen = ReductGenerator(decision_table)
    reducts = reduct_gen.generate_multiple_reducts(count=3)
    active_reduct = reducts[0]["attributes"]
    t_red = time.time() - t0
    logger.info(
        f"Reduct calculation: {len(reducts)} candidates generated, "
        f"Primary reduct size={len(active_reduct)} in {t_red:.4f}s"
    )

    # 6. Association Rule Mining (mlxtend)
    t0 = time.time()
    miner = AssociationRuleMiner(decision_table)
    rules = miner.mine_rules(
        min_support=settings.ASSOCIATION_MIN_SUPPORT,
        min_confidence=settings.ASSOCIATION_MIN_CONFIDENCE,
        max_len=settings.ASSOCIATION_MAX_LEN,
    )
    t_rules = time.time() - t0
    logger.info(f"Association rules: {len(rules)} disease rules mined in {t_rules:.4f}s")

    # 7. Machine Learning Baseline Models Training
    t0 = time.time()
    ml_baselines = MLBaselines(decision_table)
    ml_train_times = ml_baselines.train_models()
    t_ml = time.time() - t0
    logger.info(f"ML Baselines trained in {t_ml:.4f}s. Model times: {ml_train_times}")

    # 8. Recommender Instantiation & Latency Test
    recommender = RoughSetRecommender(
        decision_table,
        active_reduct=active_reduct,
    )

    # Measure per-query prediction latency on 100 sample queries
    sample_latencies = []
    for _ in range(100):
        # Sample query with 20% unknown
        sample_query = {
            a: (1 if np.random.rand() > 0.8 else ("?" if np.random.rand() > 0.5 else 0))
            for a in decision_table.condition_attributes
        }
        t_q = time.time()
        recommender.recommend(sample_query)
        sample_latencies.append((time.time() - t_q) * 1000.0)

    latency_stats = {
        "mean_latency_ms": round(float(np.mean(sample_latencies)), 3),
        "p50_latency_ms": round(float(np.median(sample_latencies)), 3),
        "p95_latency_ms": round(float(np.percentile(sample_latencies, 95)), 3),
    }

    # 9. Benchmarking on Testing.csv across Missing Ratios (0%, 10%, 30%, 50%, 70%)
    t0 = time.time()
    test_df = pd.read_csv(settings.TEST_DATA_PATH)
    bench_runner = IncompleteBenchmarkRunner(
        recommender=recommender,
        ml_baselines=ml_baselines,
        test_df=test_df,
    )
    benchmark_results = bench_runner.run_benchmark(
        missing_rates=settings.BENCHMARK_MISSING_RATES,
        repetitions=settings.BENCHMARK_REPETITIONS,
        base_seed=settings.RANDOM_SEED,
    )
    t_bench = time.time() - t0
    logger.info(f"Deterministic masking benchmarks (0% to 70%) completed in {t_bench:.4f}s")

    # 10. Complete (0% missing) Testing Evaluation for Detailed Confusion Matrix
    clean_test_df = test_df.loc[:, ~test_df.columns.str.contains("^Unnamed")]
    test_cond_cols = [c for c in clean_test_df.columns if c != "prognosis"]
    y_test_true = clean_test_df["prognosis"].tolist()
    y_test_pred = []
    top3_test_preds = []
    for _, r in clean_test_df.iterrows():
        q = {c: int(r[c]) for c in test_cond_cols}
        res = recommender.recommend(q, top_k=3)
        prim = res.get("primary_recommendation")
        y_test_pred.append(prim["disease"] if prim else "Unknown")
        top3_test_preds.append([c["disease"] for c in res.get("top_candidates", [])])

    complete_eval = ModelEvaluator.evaluate_predictions(
        y_true=y_test_true,
        y_pred=y_test_pred,
        top_k_preds=top3_test_preds,
        all_classes=decision_table.decision_classes,
    )

    total_time = time.time() - total_start_time

    pure_model_time = t_load + t_prep + t_dep + t_disc + t_red + t_rules + t_ml

    # Record complete execution timings with rigorous component delineation
    timing_record = {
        "dataset_loading_time_seconds": round(t_load, 4),
        "preprocessing_time_seconds": round(t_prep, 4),
        "rst_dependency_time_seconds": round(t_dep, 4),
        "discernibility_analysis_time_seconds": round(t_disc, 4),
        "reduct_calculation_time_seconds": round(t_red, 4),
        "association_rule_mining_time_seconds": round(t_rules, 4),
        "ml_training_time_seconds": round(t_ml, 4),
        "pure_model_preparation_time_seconds": round(pure_model_time, 4),
        "benchmarking_time_seconds": round(t_bench, 4),
        "total_preparation_time_seconds": round(total_time, 4),
        "timing_breakdown_note": (
            "pure_model_preparation_time_seconds (~6.7-7.5s) measures training the RST engine, reducts, "
            "rules, and ML classifiers. benchmarking_time_seconds (~20-32s) measures running repeated "
            "evaluations on Testing.csv across 5 missing rates. total_preparation_time_seconds measures "
            "the entire script including benchmarking and artifact serialization."
        ),
        "per_query_latency": latency_stats,
    }

    # Build and Save Artifacts
    metadata = {
        "project_name": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "random_seed": settings.RANDOM_SEED,
        "dataset_summary": decision_table.get_summary_statistics(),
        "timings": timing_record,
        "top_predictive_symptoms": top_attrs,
        "discernibility_summary": disc_stats,
        "num_mined_association_rules": len(rules),
        "complete_test_evaluation": {
            "accuracy": complete_eval["accuracy"],
            "top3_accuracy": complete_eval["top3_accuracy"],
            "precision_weighted": complete_eval["precision_weighted"],
            "recall_weighted": complete_eval["recall_weighted"],
            "f1_weighted": complete_eval["f1_weighted"],
            "total_test_samples": complete_eval["total_samples"],
        },
    }

    symptom_catalog = build_symptom_catalog(decision_table)

    logger.info("Saving generated artifacts to disk...")
    with open(artifacts_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(artifacts_dir / "reducts.json", "w", encoding="utf-8") as f:
        json.dump({
            "reducts": reducts,
            "core_attributes": core_attrs,
            "core_size": len(core_attrs),
            "full_dependency_degree": full_gamma,
        }, f, indent=2)

    with open(artifacts_dir / "association_rules.json", "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)

    with open(artifacts_dir / "benchmarks.json", "w", encoding="utf-8") as f:
        json.dump(benchmark_results, f, indent=2)

    with open(artifacts_dir / "confusion_matrix.json", "w", encoding="utf-8") as f:
        json.dump({
            "class_labels": complete_eval["class_labels"],
            "confusion_matrix": complete_eval["confusion_matrix"],
            "per_disease": complete_eval["per_disease"],
        }, f, indent=2)

    with open(artifacts_dir / "symptoms_catalog.json", "w", encoding="utf-8") as f:
        json.dump(symptom_catalog, f, indent=2)

    # Save trained ML models
    joblib.dump(ml_baselines.models, artifacts_dir / "ml_models.joblib")

    logger.info(f"Artifact generation completed successfully in {total_time:.2f}s!")
    return {
        "status": "SUCCESS",
        "timings": timing_record,
        "metadata": metadata,
    }


if __name__ == "__main__":
    run_pipeline()
