"""Unit tests for Rough Set Theory mathematical properties and axioms.

Verifies Pawlak (1982) and Skowron (1992) formal Rough Set axioms.
"""

import pytest
import numpy as np
import pandas as pd

from app.rst.decision_table import DecisionTable
from app.rst.indiscernibility import IndiscernibilityRelation
from app.rst.approximations import RoughApproximations
from app.rst.dependency import DependencyDegree
from app.rst.discernibility import DiscernibilityMatrix
from app.rst.reduct import ReductGenerator
from app.rst.incomplete import BaselineQueryToleranceStrategy


@pytest.fixture
def synthetic_decision_table() -> DecisionTable:
    """Create a minimal synthetic decision table with known properties.

    Attributes:
    a1, a2, a3: condition attributes
    d: decision attribute {X, Y}
    """
    data = {
        "a1": [1, 1, 0, 0, 1, 0],
        "a2": [1, 1, 1, 0, 0, 1],
        "a3": [0, 0, 1, 1, 0, 1],
        "prognosis": ["Flu", "Flu", "Cold", "Cold", "Allergy", "Cold"],
        "Unnamed: 133": [None] * 6,  # Test column stripping
    }
    df = pd.DataFrame(data)
    return DecisionTable(df, decision_col="prognosis", drop_columns=["Unnamed: 133"])


def test_decision_table_initialization(synthetic_decision_table):
    dt = synthetic_decision_table
    assert dt.universe_size == 6
    assert dt.num_condition_attributes == 3
    assert dt.num_decision_classes == 3  # Flu, Cold, Allergy
    assert "Unnamed: 133" not in dt.condition_attributes
    assert dt.condition_attributes == ["a1", "a2", "a3"]


def test_indiscernibility_equivalence_relation(synthetic_decision_table):
    dt = synthetic_decision_table
    ind = IndiscernibilityRelation(dt)

    # Reflexivity: object is indiscernible from itself
    for i in range(dt.universe_size):
        assert ind.are_indiscernible(i, i, ["a1", "a2", "a3"]) is True

    # Equivalence classes partition: objects 0 and 1 have identical [1, 1, 0]
    classes, inv = ind.compute_equivalence_classes(["a1", "a2", "a3"])
    # Objects 0 and 1 must be in the same equivalence class
    assert inv[0] == inv[1]
    # Sum of class sizes must equal total universe
    total_objects = sum(len(c) for c in classes)
    assert total_objects == dt.universe_size


def test_lower_and_upper_approximations_axioms(synthetic_decision_table):
    dt = synthetic_decision_table
    approx = RoughApproximations(dt)

    # Flu target objects are 0 and 1
    flu_indices = np.where(dt.decisions_raw == "Flu")[0]
    res = approx.compute_approximations_for_set(flu_indices)

    lower = set(res["lower_approximation"].tolist())
    upper = set(res["upper_approximation"].tolist())
    target = set(flu_indices.tolist())

    # Pawlak Axiom: B_*(X) ⊆ X ⊆ B^*(X)
    assert lower.issubset(target)
    assert target.issubset(upper)

    # Boundary definition: BN_B(X) = B^*(X) \ B_*(X)
    boundary = set(res["boundary_region"].tolist())
    assert boundary == upper.difference(lower)


def test_dependency_monotonicity(synthetic_decision_table):
    dt = synthetic_decision_table
    dep = DependencyDegree(dt)

    # γ_∅(d) = 0.0
    gamma_empty = dep.compute_gamma(attribute_names=[])
    assert gamma_empty == 0.0

    # Monotonicity: γ_{a1}(d) <= γ_{a1, a2}(d) <= γ_{a1, a2, a3}(d)
    gamma_1 = dep.compute_gamma(attribute_names=["a1"])
    gamma_12 = dep.compute_gamma(attribute_names=["a1", "a2"])
    gamma_all = dep.compute_gamma(attribute_names=["a1", "a2", "a3"])

    assert 0.0 <= gamma_1 <= 1.0
    assert gamma_1 <= gamma_12 + 1e-9
    assert gamma_12 <= gamma_all + 1e-9


def test_incomplete_tolerance_never_treats_unknown_as_zero():
    """Verify that '?' (unknown) is strictly ignored and NOT treated as 0."""
    strat = BaselineQueryToleranceStrategy()

    # Reference objects with 3 symptoms: [s1, s2, s3]
    # Obj 0: [1, 1, 1]
    # Obj 1: [1, 0, 1]
    # Obj 2: [0, 0, 0]
    ref_X = np.array([
        [1, 1, 1],
        [1, 0, 1],
        [0, 0, 0],
    ], dtype=np.int8)
    attrs = ["s1", "s2", "s3"]

    # Query: s1=1, s2="?", s3=1
    # If ? were treated as 0, query would match only Obj 1.
    # But because ? is ignored, it matches BOTH Obj 0 and Obj 1!
    query = {"s1": 1, "s2": "?", "s3": 1}
    res = strat.evaluate_query_compatibility(query, ref_X, attrs)

    compatible = res["compatible_indices"].tolist()
    assert 0 in compatible, "Obj 0 must match because known s1=1 and s3=1 match!"
    assert 1 in compatible, "Obj 1 must match because known s1=1 and s3=1 match!"
    assert 2 not in compatible, "Obj 2 must not match because s1=0 and s3=0 differ from query!"
    assert res["is_exact_match"] is True
    assert res["known_attributes_count"] == 2
    assert res["unknown_attributes_count"] == 1
