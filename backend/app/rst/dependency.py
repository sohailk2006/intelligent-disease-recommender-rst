"""Pawlak Rough Set Theory - Degree of Dependency & Attribute Significance.

Definitions (Pawlak, 1982):
Let DT = (U, C ∪ {d}, V, f) be a decision table, and B ⊆ C.
1. Degree of dependency of decision attribute d on condition attributes B:
       γ_B(d) = |POS_B(d)| / |U|
   where:
   - γ_B(d) = 1.0 means d is completely dependent on B (consistent subsystem)
   - 0.0 < γ_B(d) < 1.0 means d partially depends on B
   - γ_B(d) = 0.0 means d is independent of B

2. Significance of an attribute a ∈ B with respect to decision d:
       σ_B(a, d) = γ_B(d) - γ_{B \\ {a}}(d)
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
from app.rst.decision_table import DecisionTable


class DependencyDegree:
    """Fast, mathematically rigorous dependency and attribute significance calculator."""

    def __init__(self, table: DecisionTable):
        self.table = table
        self.total_u = table.universe_size

    def compute_gamma(
        self,
        attribute_names: Optional[List[str]] = None,
        attribute_indices: Optional[List[int]] = None,
    ) -> float:
        """Compute the degree of dependency γ_B(d) = |POS_B(d)| / |U|.

        Vectorized using numpy inverse indices for maximum computational efficiency.
        """
        if attribute_indices is None:
            if attribute_names is not None:
                attribute_indices = self.table.get_attribute_indices(attribute_names)
            else:
                attribute_indices = list(range(self.table.num_condition_attributes))

        if len(attribute_indices) == 0:
            return 0.0

        sub_X = self.table.X[:, attribute_indices]
        _, inv = np.unique(sub_X, axis=0, return_inverse=True)
        num_classes = np.max(inv) + 1

        min_y = np.full(num_classes, 999999, dtype=np.int32)
        max_y = np.full(num_classes, -1, dtype=np.int32)
        np.minimum.at(min_y, inv, self.table.y)
        np.maximum.at(max_y, inv, self.table.y)

        # Consistent equivalence classes have min(y) == max(y)
        consistent_classes = min_y == max_y
        counts = np.bincount(inv, minlength=num_classes)
        pos_count = int(np.sum(counts[consistent_classes]))

        return float(pos_count / self.total_u)

    def compute_attribute_significance(
        self,
        base_attributes: List[str],
        attribute_to_test: str,
    ) -> float:
        """Compute σ_B(a, d) = γ_B(d) - γ_{B \\ {a}}(d)."""
        gamma_full = self.compute_gamma(attribute_names=base_attributes)
        reduced_attributes = [a for a in base_attributes if a != attribute_to_test]
        gamma_reduced = self.compute_gamma(attribute_names=reduced_attributes)
        return float(gamma_full - gamma_reduced)

    def rank_individual_attributes(self, top_k: int = 20) -> List[Dict[str, float]]:
        """Compute γ_{{a}}(d) for each condition attribute individually and rank them."""
        results = []
        for a_idx, a_name in enumerate(self.table.condition_attributes):
            g = self.compute_gamma(attribute_indices=[a_idx])
            results.append({"attribute": a_name, "dependency": g})
        results.sort(key=lambda x: x["dependency"], reverse=True)
        return results[:top_k]
