"""Pawlak Rough Set Theory - Set Approximations & Boundary Regions.

Definitions (Pawlak, 1982):
Let S = (U, A) be an information system, B ⊆ A, and X ⊆ U.
- B-lower approximation of X:
    B_*(X) = { x ∈ U | [x]_B ⊆ X } = ⋃ { [x]_B | [x]_B ⊆ X }
- B-upper approximation of X:
    B^*(X) = { x ∈ U | [x]_B ∩ X ≠ ∅ } = ⋃ { [x]_B | [x]_B ∩ X ≠ ∅ }
- B-boundary region of X:
    BN_B(X) = B^*(X) \\ B_*(X)
- B-negative region of X:
    NEG_B(X) = U \\ B^*(X)
- Accuracy of approximation of X:
    α_B(X) = |B_*(X)| / |B^*(X)| (if |B^*(X)| > 0 else 1.0)
- B-positive region of decision partition U/IND(d):
    POS_B(d) = ⋃_{X_i ∈ U/IND(d)} B_*(X_i)
"""

from typing import Dict, List, Optional, Set, Tuple, Any
import numpy as np
from app.rst.decision_table import DecisionTable
from app.rst.indiscernibility import IndiscernibilityRelation


class RoughApproximations:
    """Calculates lower/upper approximations, boundary regions, and positive regions."""

    def __init__(self, table: DecisionTable):
        self.table = table
        self.indiscernibility = IndiscernibilityRelation(table)

    def compute_approximations_for_set(
        self,
        target_object_indices: np.ndarray,
        attribute_names: Optional[List[str]] = None,
        attribute_indices: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """Compute B_*(X), B^*(X), BN_B(X), and α_B(X) for an arbitrary subset X ⊆ U."""
        target_set = set(target_object_indices.tolist())
        equiv_classes, _ = self.indiscernibility.compute_equivalence_classes(
            attribute_names=attribute_names, attribute_indices=attribute_indices
        )

        lower_approx_members: List[int] = []
        upper_approx_members: List[int] = []

        for eq_class in equiv_classes:
            eq_set = set(eq_class.tolist())
            intersection = eq_set.intersection(target_set)

            if len(intersection) > 0:
                upper_approx_members.extend(eq_class.tolist())
                if eq_set.issubset(target_set):
                    lower_approx_members.extend(eq_class.tolist())

        lower_arr = np.array(lower_approx_members, dtype=np.int32)
        upper_arr = np.array(upper_approx_members, dtype=np.int32)
        boundary_arr = np.setdiff1d(upper_arr, lower_arr)

        accuracy = float(len(lower_arr) / len(upper_arr)) if len(upper_arr) > 0 else 1.0

        return {
            "lower_approximation": lower_arr,
            "upper_approximation": upper_arr,
            "boundary_region": boundary_arr,
            "accuracy_of_approximation": accuracy,
            "num_lower": len(lower_arr),
            "num_upper": len(upper_arr),
            "num_boundary": len(boundary_arr),
        }

    def compute_positive_region(
        self,
        attribute_names: Optional[List[str]] = None,
        attribute_indices: Optional[List[int]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Dict[str, Any]]]:
        """Compute POS_B(d) = ⋃_{X_i ∈ U/IND(d)} B_*(X_i) across all decision classes.

        Returns:
            - Array of all universe object indices belonging to POS_B(d)
            - Dictionary of per-disease approximation details
        """
        decision_partition = self.table.get_decision_partition()
        equiv_classes, _ = self.indiscernibility.compute_equivalence_classes(
            attribute_names=attribute_names, attribute_indices=attribute_indices
        )

        # Precompute mapping from object index to decision class
        y_vec = self.table.y

        positive_region_indices: List[int] = []
        per_disease_info: Dict[str, Dict[str, Any]] = {}

        # Initialize disease lower/upper sets
        disease_lower: Dict[int, List[int]] = {cls_idx: [] for cls_idx in range(self.table.num_decision_classes)}
        disease_upper: Dict[int, List[int]] = {cls_idx: [] for cls_idx in range(self.table.num_decision_classes)}

        for eq_class in equiv_classes:
            class_decisions = y_vec[eq_class]
            unique_decisions = np.unique(class_decisions)

            # Each disease present in this equivalence class gets these objects in its upper approximation
            for d in unique_decisions:
                disease_upper[int(d)].extend(eq_class.tolist())

            # If all objects in this equivalence class share the EXACT same decision:
            # this equivalence class belongs to the lower approximation of that decision class!
            if len(unique_decisions) == 1:
                single_dec = int(unique_decisions[0])
                disease_lower[single_dec].extend(eq_class.tolist())
                positive_region_indices.extend(eq_class.tolist())

        pos_arr = np.array(positive_region_indices, dtype=np.int32)

        for cls_name, cls_idx in self.table.class_to_idx.items():
            low = np.array(disease_lower[cls_idx], dtype=np.int32)
            upp = np.array(disease_upper[cls_idx], dtype=np.int32)
            bnd = np.setdiff1d(upp, low)
            acc = float(len(low) / len(upp)) if len(upp) > 0 else 1.0
            per_disease_info[cls_name] = {
                "num_lower": len(low),
                "num_upper": len(upp),
                "num_boundary": len(bnd),
                "accuracy": acc,
            }

        return pos_arr, per_disease_info
