"""CNRS branch-state objects.

BranchState is part of the CNRS-native representation layer.  In v0.6.0 it is
implemented by the branch-aware symbolic layer and re-exported here so branch
state has a stable native import path.
"""
from ..symbolic import BranchState, DEFAULT_BRANCH_STATE
__all__ = ["BranchState", "DEFAULT_BRANCH_STATE"]
