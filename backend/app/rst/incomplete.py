"""Incomplete Information Tolerance & Compatibility Strategies.

In incomplete information systems, objects have missing or unknown values ('?').
Requirement:
- Represent:
  1 = symptom present
  0 = symptom absent
  ? = unknown / not provided
- NEVER treat ? as 0.

Faculty Notice & Theoretical Labeling:
The BaselineQueryToleranceStrategy below is an academic baseline compatibility
relation where unknown query attributes are ignored during comparison with
complete reference objects. It is exposed behind the IncompleteToleranceStrategy
interface so it can be seamlessly upgraded or replaced by faculty-prescribed
generalized rough tolerance models (e.g., Kryszkiewicz, 1999; Stefanowski & Tsoukias, 2001).
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any
import numpy as np


class IncompleteToleranceStrategy(ABC):
    """Abstract interface for incomplete-information compatibility/tolerance relations."""

    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """Name of the tolerance strategy."""
        pass

    @property
    @abstractmethod
    def is_baseline_provisional(self) -> bool:
        """Whether this strategy is the provisional baseline awaiting faculty review."""
        pass

    @abstractmethod
    def evaluate_query_compatibility(
        self,
        query_symptoms: Dict[str, Any],
        reference_X: np.ndarray,
        condition_attributes: List[str],
    ) -> Dict[str, Any]:
        """Compute tolerance/compatibility between query q and reference dataset X.

        Args:
            query_symptoms: Dict mapping symptom attribute names to values (1, 0, or '?').
            reference_X: Complete condition matrix of shape (N, |C|), values in {0, 1}.
            condition_attributes: List of condition attribute names.

        Returns:
            Dictionary containing:
            - 'compatible_indices': Array of reference object indices in tolerance class [q]_T
            - 'similarity_scores': Array of similarity scores for each reference object in [0, 1]
            - 'known_attributes_count': Number of known attributes in query
            - 'unknown_attributes_count': Number of unknown ('?') attributes in query
            - 'is_exact_match': Boolean indicating whether exact compatibility was achieved
            - 'strategy_metadata': Documentation on the applied strategy
        """
        pass


class BaselineQueryToleranceStrategy(IncompleteToleranceStrategy):
    """Baseline Incomplete Information Query Compatibility Strategy.

    Rule:
    For query q and complete reference object x:
    Compare ONLY attributes for which q is known (q[a] ∈ {0, 1}).
    Attributes where q[a] == '?' are strictly ignored in comparison.
    NEVER treat '?' as 0.
    """

    @property
    def strategy_name(self) -> str:
        return "Baseline Query Compatibility (Known-Only Attributes Comparison)"

    @property
    def is_baseline_provisional(self) -> bool:
        return True

    def evaluate_query_compatibility(
        self,
        query_symptoms: Dict[str, Any],
        reference_X: np.ndarray,
        condition_attributes: List[str],
    ) -> Dict[str, Any]:
        attr_to_idx = {attr: idx for idx, attr in enumerate(condition_attributes)}
        n_objects = reference_X.shape[0]

        known_indices: List[int] = []
        known_values: List[int] = []
        unknown_attrs: List[str] = []
        known_attrs: List[str] = []

        for attr in condition_attributes:
            val = query_symptoms.get(attr, "?")

            # Handle various representations of unknown
            if val in ("?", "unknown", None, "", -1):
                unknown_attrs.append(attr)
                continue

            # Parse known binary value
            try:
                int_val = int(val)
                if int_val in (0, 1):
                    known_indices.append(attr_to_idx[attr])
                    known_values.append(int_val)
                    known_attrs.append(attr)
                else:
                    unknown_attrs.append(attr)
            except (ValueError, TypeError):
                unknown_attrs.append(attr)

        num_known = len(known_indices)
        num_unknown = len(unknown_attrs)

        # If zero attributes are known, all objects in U are mutually compatible
        if num_known == 0:
            all_indices = np.arange(n_objects, dtype=np.int32)
            return {
                "compatible_indices": all_indices,
                "similarity_scores": np.ones(n_objects, dtype=np.float32),
                "known_attributes_count": 0,
                "unknown_attributes_count": num_unknown,
                "is_exact_match": True,
                "known_attributes": [],
                "unknown_attributes": unknown_attrs,
                "strategy_metadata": {
                    "strategy": self.strategy_name,
                    "is_baseline_provisional": self.is_baseline_provisional,
                    "description": "Zero known symptoms provided; complete universe is indiscernible.",
                },
            }

        known_indices_arr = np.array(known_indices, dtype=np.int32)
        known_values_arr = np.array(known_values, dtype=np.int8)

        # Reference matrix sub-slice for known attributes
        ref_sub = reference_X[:, known_indices_arr]  # shape: (n_objects, num_known)

        # Vectorized comparison: ref_sub == known_values_arr
        matches_matrix = (ref_sub == known_values_arr[None, :])  # shape: (n_objects, num_known) bool

        # Exact tolerance class: objects where all known attributes match
        exact_match_mask = np.all(matches_matrix, axis=1)
        exact_indices = np.where(exact_match_mask)[0]

        # Calculate similarity score: fraction of matched known symptoms
        similarity_scores = np.mean(matches_matrix, axis=1)  # shape: (n_objects,)

        if len(exact_indices) > 0:
            final_compatible = exact_indices
            is_exact = True
            desc = (
                f"Exact tolerance neighborhood identified with {len(exact_indices)} matching reference objects "
                f"across all {num_known} known attributes. {num_unknown} unknown attributes ignored."
            )
        else:
            # Fallback: Maximal similarity tolerance neighborhood
            max_sim = float(np.max(similarity_scores))
            final_compatible = np.where(similarity_scores == max_sim)[0]
            is_exact = False
            desc = (
                f"No exact match in reference table. Relaxed maximal similarity neighborhood identified "
                f"with {len(final_compatible)} objects at similarity {max_sim:.3f} across {num_known} known attributes."
            )

        return {
            "compatible_indices": final_compatible,
            "similarity_scores": similarity_scores,
            "known_attributes_count": num_known,
            "unknown_attributes_count": num_unknown,
            "is_exact_match": is_exact,
            "known_attributes": known_attrs,
            "unknown_attributes": unknown_attrs,
            "strategy_metadata": {
                "strategy": self.strategy_name,
                "is_baseline_provisional": self.is_baseline_provisional,
                "description": desc,
            },
        }


def get_default_tolerance_strategy() -> IncompleteToleranceStrategy:
    """Factory returning the configured incomplete-information tolerance strategy."""
    return BaselineQueryToleranceStrategy()
