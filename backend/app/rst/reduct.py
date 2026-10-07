"""Pawlak Rough Set Theory - Reduct Candidate Generation & Core Analysis.

Definitions (Pawlak, 1982):
A subset of condition attributes R ⊆ C is a reduct of C with respect to d if:
1. γ_R(d) = γ_C(d) (same degree of dependency as the full attribute set)
2. ∀a ∈ R, γ_{R \\ {a}}(d) < γ_R(d) (minimality: no attribute in R is redundant)

The Core of C is the intersection of all reducts:
    CORE(C) = ⋂ RED(C)
"""

from typing import Dict, List, Optional, Set, Tuple, Any
import numpy as np
from app.rst.decision_table import DecisionTable
from app.rst.dependency import DependencyDegree
from app.rst.discernibility import DiscernibilityMatrix


class ReductGenerator:
    """Generates minimal attribute reduct candidates using QuickReduct and Johnson's algorithm."""

    def __init__(self, table: DecisionTable):
        self.table = table
        self.dependency = DependencyDegree(table)
        self.discernibility = DiscernibilityMatrix(table)
        self.full_gamma = self.dependency.compute_gamma()

    def generate_johnson_reduct(self) -> List[str]:
        """Compute a minimal reduct using Johnson's greedy discernibility algorithm."""
        self.discernibility.compute()
        diff_matrix = self.discernibility._diff_matrix  # (n_clauses, |C|) bool
        n_clauses, n_attrs = diff_matrix.shape

        uncovered = np.ones(n_clauses, dtype=bool)
        selected_indices: List[int] = []

        # Core attributes must be included first
        for core_idx in self.discernibility.core_indices:
            selected_indices.append(core_idx)
            uncovered = uncovered & (~diff_matrix[:, core_idx])

        while np.any(uncovered):
            # Find attribute that covers the largest number of remaining uncovered clauses
            coverage_counts = np.sum(diff_matrix[uncovered, :], axis=0)
            # Mask out already selected
            for s in selected_indices:
                coverage_counts[s] = -1

            best_idx = int(np.argmax(coverage_counts))
            if coverage_counts[best_idx] <= 0:
                break
            selected_indices.append(best_idx)
            uncovered = uncovered & (~diff_matrix[:, best_idx])

        # Minimality check (backward elimination)
        final_indices = list(selected_indices)
        for attr_idx in list(selected_indices):
            remaining = [x for x in final_indices if x != attr_idx]
            if len(remaining) == 0:
                continue
            # Check if remaining attributes cover all clauses
            covered_all = np.all(np.any(diff_matrix[:, remaining], axis=1))
            if covered_all:
                final_indices.remove(attr_idx)

        return [self.table.idx_to_attr[i] for i in final_indices]

    def generate_quickreduct(self) -> List[str]:
        """Compute a minimal reduct using the QuickReduct dependency heuristic.

        Uses exact weighted equivalence patterns from U/IND(C) for mathematically identical
        gamma calculation with sub-5-second execution.
        """
        unique_patterns, unique_indices, unique_counts = np.unique(
            self.table.X, axis=0, return_index=True, return_counts=True
        )
        unique_y = self.table.y[unique_indices]
        n_total = float(self.table.universe_size)

        def calc_gamma_weighted(indices: List[int]) -> float:
            if not indices:
                return 0.0
            _, inv = np.unique(unique_patterns[:, indices], axis=0, return_inverse=True)
            k = int(inv.max()) + 1
            min_y = np.full(k, 999999, dtype=np.int32)
            max_y = np.full(k, -1, dtype=np.int32)
            np.minimum.at(min_y, inv, unique_y)
            np.maximum.at(max_y, inv, unique_y)
            consistent = (min_y == max_y)
            weights = np.bincount(inv, weights=unique_counts, minlength=k)
            return float(np.sum(weights[consistent]) / n_total)

        R_indices: List[int] = list(self.discernibility.core_indices)
        candidates: List[int] = [i for i in range(self.table.num_condition_attributes) if i not in R_indices]

        cur_gamma = calc_gamma_weighted(R_indices)

        while cur_gamma < self.full_gamma - 1e-9 and candidates:
            best_idx = None
            best_g = cur_gamma

            for cand in candidates:
                test_g = calc_gamma_weighted(R_indices + [cand])
                if test_g > best_g:
                    best_g = test_g
                    best_idx = cand
                    if best_g >= self.full_gamma - 1e-9:
                        break

            if best_idx is None:
                cand_gammas = [calc_gamma_weighted([c]) for c in candidates]
                best_idx = candidates[int(np.argmax(cand_gammas))]
                best_g = calc_gamma_weighted(R_indices + [best_idx])

            R_indices.append(best_idx)
            candidates.remove(best_idx)
            cur_gamma = best_g

        # Backward elimination for minimality
        final_r = list(R_indices)
        for idx in list(R_indices):
            test_subset = [x for x in final_r if x != idx]
            if len(test_subset) > 0:
                g = calc_gamma_weighted(test_subset)
                if g >= self.full_gamma - 1e-9:
                    final_r.remove(idx)

        return [self.table.idx_to_attr[i] for i in final_r]

    def generate_multiple_reducts(self, count: int = 3) -> List[Dict[str, Any]]:
        """Generate multiple distinct reduct candidates."""
        reducts: List[Dict[str, Any]] = []

        # Reduct 1: Johnson's algorithm (discernibility hitting set)
        johnson_r = self.generate_johnson_reduct()
        g_johnson = self.dependency.compute_gamma(attribute_names=johnson_r)
        reducts.append({
            "id": "reduct_johnson",
            "name": "Johnson Greedy Discernibility Reduct",
            "size": len(johnson_r),
            "attributes": sorted(johnson_r),
            "dependency_degree": g_johnson,
            "is_minimal": True,
        })

        # Reduct 2: QuickReduct algorithm (dependency-driven)
        quick_r = self.generate_quickreduct()
        g_quick = self.dependency.compute_gamma(attribute_names=quick_r)
        reducts.append({
            "id": "reduct_quickreduct",
            "name": "QuickReduct Dependency-Driven Reduct",
            "size": len(quick_r),
            "attributes": sorted(quick_r),
            "dependency_degree": g_quick,
            "is_minimal": True,
        })

        # Reduct 3: Weighted frequency reduct
        # Reverse order candidate exploration
        self.discernibility.compute()
        diff_matrix = self.discernibility._diff_matrix
        rev_indices = list(range(self.table.num_condition_attributes - 1, -1, -1))
        uncovered = np.ones(diff_matrix.shape[0], dtype=bool)
        alt_indices: List[int] = []

        for idx in rev_indices:
            if np.any(diff_matrix[uncovered, idx]):
                alt_indices.append(idx)
                uncovered = uncovered & (~diff_matrix[:, idx])
            if not np.any(uncovered):
                break

        # Prune alt_indices
        for idx in list(alt_indices):
            rem = [x for x in alt_indices if x != idx]
            if rem and np.all(np.any(diff_matrix[:, rem], axis=1)):
                alt_indices.remove(idx)

        alt_attrs = [self.table.idx_to_attr[i] for i in alt_indices]
        g_alt = self.dependency.compute_gamma(attribute_names=alt_attrs)
        reducts.append({
            "id": "reduct_frequency",
            "name": "Alternative Minimal Covering Reduct",
            "size": len(alt_attrs),
            "attributes": sorted(alt_attrs),
            "dependency_degree": g_alt,
            "is_minimal": True,
        })

        return reducts
