"""Rough Set Reasoning & Recommender Engine for Disease Prediction.

Primary deterministic reasoning engine using Rough Set Theory.
Computes:
- Incomplete query tolerance class [q]_T
- Rough membership degrees μ_d(q)
- Lower, boundary, and upper approximation membership for each disease
- Reduct attribute alignment
- Explainable recommendation evidence
- Disambiguation suggestion for unknown symptoms
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from app.rst.decision_table import DecisionTable
from app.rst.incomplete import IncompleteToleranceStrategy, get_default_tolerance_strategy


class RoughSetRecommender:
    """Primary explainable recommender engine grounded in Rough Set Theory."""

    def __init__(
        self,
        table: DecisionTable,
        tolerance_strategy: Optional[IncompleteToleranceStrategy] = None,
        active_reduct: Optional[List[str]] = None,
    ):
        self.table = table
        self.strategy = tolerance_strategy or get_default_tolerance_strategy()
        self.active_reduct: Optional[List[str]] = active_reduct

    def recommend(
        self,
        query_symptoms: Dict[str, Any],
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """Generate explainable disease recommendation from complete or incomplete symptoms.

        Args:
            query_symptoms: Dict mapping symptom names to 1, 0, or '?'.
            top_k: Number of candidate recommendations to return.

        Returns:
            Structured recommendation with RST approximations, confidence, and evidence.
        """
        # Step 1: Incomplete Information Tolerance Evaluation
        compat_result = self.strategy.evaluate_query_compatibility(
            query_symptoms=query_symptoms,
            reference_X=self.table.X,
            condition_attributes=self.table.condition_attributes,
        )

        compatible_indices = compat_result["compatible_indices"]
        num_compatible = len(compatible_indices)
        known_attrs = compat_result["known_attributes"]
        unknown_attrs = compat_result["unknown_attributes"]

        if num_compatible == 0:
            return {
                "status": "NO_MATCH",
                "message": "No compatible disease found in the decision table.",
                "candidates": [],
                "primary_recommendation": None,
                "rough_set_reasoning": {},
            }

        # Step 2: Distribution of decisions within tolerance class [q]_T
        matching_y = self.table.y[compatible_indices]
        class_counts = pd.Series(matching_y).value_counts()

        # Step 3: Compute Rough Approximations & Membership for candidate diseases
        candidates: List[Dict[str, Any]] = []

        for cls_idx, count in class_counts.items():
            cls_name = self.table.idx_to_class[int(cls_idx)]
            membership_degree = float(count / num_compatible)

            # Lower approximation condition: [q]_T ⊆ X_d
            in_lower = (count == num_compatible)
            in_upper = True  # because count > 0
            in_boundary = (not in_lower) and in_upper

            if in_lower:
                approx_status = "LOWER_APPROXIMATION (Certain)"
                approx_code = "LOWER"
            elif in_boundary:
                approx_status = "BOUNDARY_REGION (Uncertain / Incomplete)"
                approx_code = "BOUNDARY"
            else:
                approx_status = "UPPER_APPROXIMATION (Possible)"
                approx_code = "UPPER"

            # Profile of this disease in training data for evidence extraction
            disease_mask = (self.table.y == cls_idx)
            disease_profiles = self.table.X[disease_mask]
            # Symptom prevalence within this disease
            symptom_prevalence = disease_profiles.mean(axis=0)

            # Identify which known positive query symptoms align with this disease
            present_query_symptoms = [
                a for a in known_attrs if str(query_symptoms.get(a)) == "1"
            ]
            absent_query_symptoms = [
                a for a in known_attrs if str(query_symptoms.get(a)) == "0"
            ]

            aligned_present = [
                a for a in present_query_symptoms
                if symptom_prevalence[self.table.attr_to_idx[a]] > 0.5
            ]
            conflicting_symptoms = [
                a for a in present_query_symptoms
                if symptom_prevalence[self.table.attr_to_idx[a]] == 0.0
            ]

            candidates.append({
                "disease": cls_name,
                "membership_degree": round(membership_degree, 4),
                "confidence_percentage": round(membership_degree * 100, 2),
                "support_count": int(count),
                "approximation_status": approx_status,
                "approximation_code": approx_code,
                "aligned_symptoms": aligned_present,
                "conflicting_symptoms": conflicting_symptoms,
            })

        # Rank candidates by membership degree and support
        candidates.sort(key=lambda x: (x["membership_degree"], x["support_count"]), reverse=True)
        primary = candidates[0] if candidates else None

        # Step 4: Reduct attribute alignment
        reduct_alignment = {}
        if self.active_reduct:
            known_reduct_attrs = [a for a in self.active_reduct if a in known_attrs]
            reduct_alignment = {
                "active_reduct_size": len(self.active_reduct),
                "known_reduct_attributes_count": len(known_reduct_attrs),
                "known_reduct_attributes": known_reduct_attrs,
                "coverage_ratio": round(len(known_reduct_attrs) / len(self.active_reduct), 3),
            }

        # Step 5: Suggested disambiguating symptoms (if boundary region is non-empty)
        # Note: 'discriminative_power' is our project's custom variance-based heuristic (NOT a standard RST metric).
        # Formula: Var(p(a)) = (1/K) * sum((p_k(a) - mean(p(a)))^2) across top K candidate diseases (K <= 3).
        # Higher variance indicates greater distinguishing utility between the candidate disease profiles.
        disambiguation_suggestions: List[Dict[str, Any]] = []
        if len(candidates) > 1 and len(unknown_attrs) > 0:
            top_candidate_indices = [
                self.table.class_to_idx[c["disease"]] for c in candidates[:3]
            ]
            top_profiles = self.table.X[np.isin(self.table.y, top_candidate_indices)]
            top_y = self.table.y[np.isin(self.table.y, top_candidate_indices)]

            for unk_attr in unknown_attrs[:25]:
                col_idx = self.table.attr_to_idx[unk_attr]
                # Compare prevalence across top diseases
                rates = []
                for cid in top_candidate_indices:
                    sub = self.table.X[self.table.y == cid, col_idx]
                    rates.append(float(sub.mean()))
                variance = float(np.var(rates))
                if variance > 0.05:  # Attribute discerns between the top diseases
                    disambiguation_suggestions.append({
                        "symptom": unk_attr,
                        "discriminative_power": round(variance, 3),
                        "rates_per_disease": {
                            self.table.idx_to_class[cid]: round(rates[i], 2)
                            for i, cid in enumerate(top_candidate_indices)
                        },
                    })
            disambiguation_suggestions.sort(key=lambda x: x["discriminative_power"], reverse=True)

        return {
            "status": "SUCCESS",
            "primary_recommendation": primary,
            "top_candidates": candidates[:top_k],
            "rough_set_reasoning": {
                "tolerance_class_size": num_compatible,
                "is_exact_match": compat_result["is_exact_match"],
                "known_symptoms_count": compat_result["known_attributes_count"],
                "unknown_symptoms_count": compat_result["unknown_attributes_count"],
                "strategy": compat_result["strategy_metadata"],
                "reduct_alignment": reduct_alignment,
                "boundary_uncertainty": len(candidates) > 1,
                "suggested_disambiguation_symptoms": disambiguation_suggestions[:5],
            },
        }
