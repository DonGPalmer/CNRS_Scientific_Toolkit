"""Native CNRS-A arithmetic façade."""
from ..cnrs_add import add_cnrs
from ..cnrs_mul import mul_cnrs
from ..cnrs_div import div_cnrs, div_by_base, div_by_base_power
from ..cnrs_ops import cnrs_add, cnrs_sub, cnrs_mul, cnrs_neg, cnrs_eq
__all__ = [
    "add_cnrs", "mul_cnrs", "div_cnrs", "div_by_base", "div_by_base_power",
    "cnrs_add", "cnrs_sub", "cnrs_mul", "cnrs_neg", "cnrs_eq",
]
