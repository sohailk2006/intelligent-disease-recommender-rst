"""Baseline Machine Learning Models for Comparative Evaluation.

Trains standard supervised ML algorithms strictly on Training.csv:
1. Random Forest Classifier
2. Multinomial Naive Bayes
3. Logistic Regression (L2 regularized)
4. Decision Tree Classifier (CART)

These serve as empirical comparison baselines alongside Rough Set Theory.
"""

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier

from app.rst.decision_table import DecisionTable
from app.core.config import settings


class MLBaselines:
    """Manages baseline machine learning models."""

    def __init__(self, table: DecisionTable):
        self.table = table
        self.models: Dict[str, Any] = {}
        self.is_trained = False

    def train_models(self) -> Dict[str, Any]:
        """Train baseline ML models deterministically on Training.csv."""
        X_train = self.table.X
        y_train = self.table.y

        # Initialize classifiers with fixed deterministic random seed
        self.models = {
            "RandomForest": RandomForestClassifier(
                n_estimators=100,
                random_state=settings.RANDOM_SEED,
                max_depth=15,
                n_jobs=-1,
            ),
            "MultinomialNB": MultinomialNB(),
            "LogisticRegression": LogisticRegression(
                max_iter=1000,
                random_state=settings.RANDOM_SEED,
            ),
            "DecisionTree": DecisionTreeClassifier(
                random_state=settings.RANDOM_SEED,
            ),
        }

        train_times = {}
        for name, clf in self.models.items():
            import time
            t0 = time.time()
            clf.fit(X_train, y_train)
            train_times[name] = round(time.time() - t0, 4)

        self.is_trained = True
        return train_times

    def predict_query(
        self,
        query_symptoms: Dict[str, Any],
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """Predict disease using trained ML baselines for comparison with RST.

        Imputes unknown ('?') symptoms as 0 (standard ML assumption of absence).
        """
        if not self.is_trained:
            self.train_models()

        # Build feature vector (defaulting unknown ? or missing to 0 for ML input)
        x_vec = np.zeros(self.table.num_condition_attributes, dtype=np.int8)
        for attr, idx in self.table.attr_to_idx.items():
            val = query_symptoms.get(attr, 0)
            if str(val) == "1":
                x_vec[idx] = 1

        results = {}
        for name, clf in self.models.items():
            probs = clf.predict_proba(x_vec.reshape(1, -1))[0]
            top_indices = np.argsort(probs)[::-1][:top_k]
            top_preds = [
                {
                    "disease": self.table.idx_to_class[idx],
                    "probability": round(float(probs[idx]), 4),
                }
                for idx in top_indices
                if probs[idx] > 0.001
            ]
            primary_idx = top_indices[0]
            results[name] = {
                "predicted_disease": self.table.idx_to_class[primary_idx],
                "confidence": round(float(probs[primary_idx]), 4),
                "top_candidates": top_preds,
            }

        return results
