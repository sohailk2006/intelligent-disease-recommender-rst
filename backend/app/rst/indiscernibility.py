"""Pawlak Rough Set Theory - Indiscernibility Relation & Equivalence Classes.

Definition (Pawlak, 1982):
Let S = (U, A) be an information system, and let B ⊆ A be a non-empty subset of attributes.
The indiscernibility relation IND(B) is an equivalence relation defined as:
    IND(B) = { (x, y) ∈ U × U | ∀a ∈ B, a(x) = a(y) }

The equivalence class of an object x with respect to B is denoted [x]_B:
    [x]_B = { y ∈ U | (x, y) ∈ IND(B) }

The family of all equivalence classes induced by B is denoted U / IND(B).
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from app.rst.decision_table import DecisionTable


class IndiscernibilityRelation:
    """Computes and manages the indiscernibility relation IND(B) and equivalence classes U / IND(B)."""

    def __init__(self, table: DecisionTable):
        self.table = table

    def compute_equivalence_classes(
        self,
        attribute_names: Optional[List[str]] = None,
        attribute_indices: Optional[List[int]] = None,
    ) -> Tuple[List[np.ndarray], np.ndarray]:
        """Compute the equivalence classes U / IND(B).

        Args:
            attribute_names: Optional list of attribute names subset B ⊆ C.
            attribute_indices: Optional list of column indices. If neither provided, uses all condition attributes C.

        Returns:
            Tuple of:
            - List of numpy arrays, where each array contains the universe object indices in that equivalence class.
            - Array of equivalence class IDs for each object in U (shape: (universe_size,)).
        """
        if attribute_indices is None:
            if attribute_names is not None:
                attribute_indices = self.table.get_attribute_indices(attribute_names)
            else:
                attribute_indices = list(range(self.table.num_condition_attributes))

        if len(attribute_indices) == 0:
            # If B is empty, all objects in U are mutually indiscernible: single equivalence class U
            all_indices = np.arange(self.table.universe_size, dtype=np.int32)
            return [all_indices], np.zeros(self.table.universe_size, dtype=np.int32)

        # Slice sub-matrix for attribute subset B
        sub_X = self.table.X[:, attribute_indices]

        # Use np.unique along rows to partition U into equivalence classes
        _, inverse_indices = np.unique(sub_X, axis=0, return_inverse=True)
        num_classes = np.max(inverse_indices) + 1

        # Group universe object indices by their equivalence class ID
        classes: List[np.ndarray] = [[] for _ in range(num_classes)]
        for obj_idx, cls_id in enumerate(inverse_indices):
            classes[cls_id].append(obj_idx)

        classes_arrays = [np.array(c, dtype=np.int32) for c in classes]
        return classes_arrays, inverse_indices

    def are_indiscernible(self, obj_i: int, obj_j: int, attribute_names: List[str]) -> bool:
        """Check whether two objects obj_i, obj_j are indiscernible under B ⊆ C."""
        indices = self.table.get_attribute_indices(attribute_names)
        return bool(np.all(self.table.X[obj_i, indices] == self.table.X[obj_j, indices]))
