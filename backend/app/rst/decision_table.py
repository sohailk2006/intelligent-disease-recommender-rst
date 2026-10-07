"""Pawlak Rough Set Theory - Decision Table Representation.

In Rough Set Theory (Pawlak, 1982), an information system is a pair S = (U, A),
where U is a non-empty finite set of objects (the Universe) and A is a non-empty
finite set of attributes. A decision table is an information system of the form:
DT = (U, C ∪ {d}, V, f)
where:
- U: Universe of discourse (|U| = 4,920 in Training.csv)
- C: Set of condition attributes (132 binary symptom attributes)
- {d}: Decision attribute ("prognosis", 41 distinct disease categories)
- V = ⋃_{a ∈ C ∪ {d}} V_a: Domain of attribute values (V_a = {0, 1} for a ∈ C)
- f: U × (C ∪ {d}) → V: Information mapping function
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd


class DecisionTable:
    """Rigorous mathematical representation of a Rough Set Decision Table."""

    def __init__(
        self,
        df: pd.DataFrame,
        decision_col: str = "prognosis",
        drop_columns: Optional[List[str]] = None,
    ):
        """Initialize and sanitize the decision table from DataFrame.

        Args:
            df: Raw or preprocessed DataFrame.
            decision_col: Name of the decision (prognosis) attribute.
            drop_columns: List of columns to drop (e.g. ['Unnamed: 133']).
        """
        clean_df = df.copy()

        # Remove any unwanted columns such as 'Unnamed: 133'
        if drop_columns:
            clean_df = clean_df.drop(columns=drop_columns, errors="ignore")
        clean_df = clean_df.loc[:, ~clean_df.columns.str.contains("^Unnamed")]

        if decision_col not in clean_df.columns:
            raise ValueError(f"Decision attribute '{decision_col}' not found in dataframe columns.")

        self.decision_col: str = decision_col
        self.condition_attributes: List[str] = [c for c in clean_df.columns if c != decision_col]
        self.all_attributes: List[str] = self.condition_attributes + [decision_col]

        # Attribute name to index lookup
        self.attr_to_idx: Dict[str, int] = {attr: idx for idx, attr in enumerate(self.condition_attributes)}
        self.idx_to_attr: Dict[int, str] = {idx: attr for idx, attr in enumerate(self.condition_attributes)}

        # Universe objects
        self.universe_size: int = len(clean_df)
        self.object_ids: List[int] = list(range(self.universe_size))

        # Internal matrix representations
        # Condition matrix X: shape (N, |C|), binary {0, 1}
        self.X: np.ndarray = clean_df[self.condition_attributes].to_numpy(dtype=np.int8)

        # Decision values: array of categorical strings
        self.decisions_raw: np.ndarray = clean_df[decision_col].to_numpy()

        # Decision encoding
        self.decision_classes: List[str] = sorted(list(set(self.decisions_raw)))
        self.class_to_idx: Dict[str, int] = {c: i for i, c in enumerate(self.decision_classes)}
        self.idx_to_class: Dict[int, str] = {i: c for i, c in enumerate(self.decision_classes)}
        self.y: np.ndarray = np.array([self.class_to_idx[d] for d in self.decisions_raw], dtype=np.int32)

        # Keep dataframe reference
        self.df: pd.DataFrame = clean_df

    @property
    def num_condition_attributes(self) -> int:
        return len(self.condition_attributes)

    @property
    def num_decision_classes(self) -> int:
        return len(self.decision_classes)

    def get_attribute_indices(self, attributes: List[str]) -> List[int]:
        """Convert a list of attribute names to matrix column indices."""
        return [self.attr_to_idx[a] for a in attributes if a in self.attr_to_idx]

    def get_decision_partition(self) -> Dict[str, np.ndarray]:
        """Compute the partition of Universe U by decision attribute d: U / IND({d}).

        Returns:
            Dictionary mapping each disease class to the array of universe object indices.
        """
        partition = {}
        for cls_name, cls_idx in self.class_to_idx.items():
            partition[cls_name] = np.where(self.y == cls_idx)[0]
        return partition

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Return research summary metrics of the decision table."""
        decision_counts = pd.Series(self.decisions_raw).value_counts().to_dict()
        return {
            "universe_size": self.universe_size,
            "num_condition_attributes": self.num_condition_attributes,
            "num_decision_classes": self.num_decision_classes,
            "condition_attributes": self.condition_attributes,
            "decision_classes": self.decision_classes,
            "decision_distribution": decision_counts,
            "is_balanced": len(set(decision_counts.values())) == 1,
            "sample_per_class": next(iter(decision_counts.values())),
        }
