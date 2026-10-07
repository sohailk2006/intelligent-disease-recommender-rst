"""Skowron Rough Set Theory - Discernibility Matrix & Discernibility Function.

Definitions (Skowron & Rauszer, 1992):
Let DT = (U, C ∪ {d}, V, f) be a decision table.
The discernibility matrix M = (c_ij)_{n × n} is defined by:
    c_ij = { a ∈ C | a(x_i) ≠ a(x_j) }   if d(x_i) ≠ d(x_j)
    c_ij = ∅                              otherwise

The discernibility function f_M is a Boolean function of m Boolean variables
corresponding to attributes in C, defined as:
    f_M(c_1, ..., c_m) = ⋀ { ⋁ c_ij | 1 ≤ j < i ≤ n, c_ij ≠ ∅ }

The Core is defined as the set of all singleton entries in the discernibility matrix:
    CORE(C) = { a ∈ C | ∃ i, j such that c_ij = {a} }
"""

from typing import Dict, List, Set, Tuple, Any
import numpy as np
from app.rst.decision_table import DecisionTable


class DiscernibilityMatrix:
    """Computes Skowron's discernibility matrix and discernibility clauses."""

    def __init__(self, table: DecisionTable):
        self.table = table
        self._computed = False
        self.clauses: List[np.ndarray] = []  # Array of boolean masks of length |C|
        self.pair_count: int = 0
        self.min_clause_size: int = 0
        self.avg_clause_size: float = 0.0
        self.core_indices: List[int] = []

    def compute(self) -> "DiscernibilityMatrix":
        """Compute discernibility matrix over unique equivalence patterns."""
        if self._computed:
            return self

        # Extract unique condition vectors with their decision
        unique_patterns, unique_indices = np.unique(self.table.X, axis=0, return_index=True)
        unique_y = self.table.y[unique_indices]
        n_unique = len(unique_indices)

        # Pairs of objects with different decisions
        diff_decisions = unique_y[:, None] != unique_y[None, :]
        i_idx, j_idx = np.triu_indices(n_unique, k=1)
        valid_pairs_mask = diff_decisions[i_idx, j_idx]

        pair_i = i_idx[valid_pairs_mask]
        pair_j = j_idx[valid_pairs_mask]
        self.pair_count = len(pair_i)

        if self.pair_count == 0:
            self._computed = True
            return self

        # Boolean diffs: shape (pair_count, num_attributes)
        # diff_matrix[k, a] is True if attribute a discerns pair k
        diff_matrix = unique_patterns[pair_i] != unique_patterns[pair_j]

        # Filter out duplicates among clauses for efficiency
        unique_clauses = np.unique(diff_matrix, axis=0)
        self.clauses = [unique_clauses[idx] for idx in range(len(unique_clauses))]

        clause_sizes = unique_clauses.sum(axis=1)
        self.min_clause_size = int(clause_sizes.min()) if len(clause_sizes) > 0 else 0
        self.avg_clause_size = float(clause_sizes.mean()) if len(clause_sizes) > 0 else 0.0

        # Core attributes: any attribute appearing alone in a clause of size 1
        core_set = set()
        singleton_mask = clause_sizes == 1
        if np.any(singleton_mask):
            singleton_clauses = unique_clauses[singleton_mask]
            for s_clause in singleton_clauses:
                attr_idx = int(np.where(s_clause)[0][0])
                core_set.add(attr_idx)

        self.core_indices = sorted(list(core_set))
        self._diff_matrix = unique_clauses  # shape: (num_distinct_clauses, |C|)
        self._computed = True
        return self

    def get_core_attributes(self) -> List[str]:
        """Return the names of attributes in CORE(C)."""
        self.compute()
        return [self.table.idx_to_attr[idx] for idx in self.core_indices]

    def get_statistics(self) -> Dict[str, Any]:
        """Return discernibility matrix statistics."""
        self.compute()
        return {
            "total_discerning_pairs": self.pair_count,
            "unique_discernibility_clauses": len(self.clauses),
            "min_clause_size": self.min_clause_size,
            "avg_clause_size": round(self.avg_clause_size, 3),
            "core_size": len(self.core_indices),
            "core_attributes": self.get_core_attributes(),
        }
