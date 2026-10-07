"""Association Rule Mining using mlxtend.

Mines association rules connecting symptom patterns to diseases:
Antecedent (symptoms) → Consequent (disease prognosis)
Provides confidence, support, lift, and match filtering for queries.
"""

from typing import Dict, List, Optional, Any
import numpy as np
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from app.rst.decision_table import DecisionTable
from app.core.config import settings


class AssociationRuleMiner:
    """Mines and queries symptom-disease association rules."""

    def __init__(self, table: DecisionTable):
        self.table = table
        self.rules_df: Optional[pd.DataFrame] = None
        self.disease_rules: List[Dict[str, Any]] = []

    def mine_rules(
        self,
        min_support: float = settings.ASSOCIATION_MIN_SUPPORT,
        min_confidence: float = settings.ASSOCIATION_MIN_CONFIDENCE,
        max_len: int = settings.ASSOCIATION_MAX_LEN,
    ) -> List[Dict[str, Any]]:
        """Mine association rules using Apriori and return structured rule items."""
        # Convert decision attribute to one-hot encoded columns
        one_hot_df = pd.get_dummies(self.table.df, columns=[self.table.decision_col], prefix="DISEASE", dtype=bool)
        bool_df = one_hot_df.select_dtypes(include=["bool", "int64", "int8"]).astype(bool)

        frequent_itemsets = apriori(
            bool_df,
            min_support=min_support,
            use_colnames=True,
            max_len=max_len,
        )

        if len(frequent_itemsets) == 0:
            return []

        rules = association_rules(
            frequent_itemsets,
            metric="confidence",
            min_threshold=min_confidence,
        )

        # Filter rules where consequent contains exactly one disease
        disease_prefix = "DISEASE_"
        disease_rule_rows = []

        for _, row in rules.iterrows():
            consequents = list(row["consequents"])
            # Consequent must be a disease
            if len(consequents) == 1 and consequents[0].startswith(disease_prefix):
                disease_name = consequents[0].replace(disease_prefix, "")
                antecedents = list(row["antecedents"])
                # Antecedents should all be symptoms (not diseases)
                if all(not a.startswith(disease_prefix) for a in antecedents):
                    disease_rule_rows.append({
                        "antecedents": antecedents,
                        "consequent": disease_name,
                        "support": round(float(row["support"]), 4),
                        "confidence": round(float(row["confidence"]), 4),
                        "lift": round(float(row["lift"]), 3),
                        "leverage": round(float(row.get("leverage", 0.0)), 4),
                        "conviction": round(float(row.get("conviction", 1.0)), 3) if not np.isinf(row.get("conviction", 1.0)) else 999.0,
                    })

        # Sort by confidence and lift descending
        disease_rule_rows.sort(key=lambda r: (r["confidence"], r["lift"]), reverse=True)
        self.disease_rules = disease_rule_rows
        return self.disease_rules

    def find_matching_rules(
        self,
        query_symptoms: Dict[str, Any],
        min_lift: float = 1.0,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Find mined association rules satisfied by the query symptoms."""
        # Find positive symptoms in query
        active_symptoms = set([
            k for k, v in query_symptoms.items()
            if str(v) == "1"
        ])

        matched_rules = []
        for r in self.disease_rules:
            antecedent_set = set(r["antecedents"])
            # If all antecedents of the rule are present in the user's symptoms
            if antecedent_set.issubset(active_symptoms) and r["lift"] >= min_lift:
                matched_rules.append(r)
                if len(matched_rules) >= limit:
                    break

        return matched_rules
