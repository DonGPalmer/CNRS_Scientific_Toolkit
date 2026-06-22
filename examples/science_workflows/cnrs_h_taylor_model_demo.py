"""CNRS-H Taylor-model-style remainder metadata demo."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from cnrs.symbolic import Var, exp
from cnrs.cnrs_h_taylor_model import taylor_model_from_symbolic, verify_taylor_model_chain_rule


s = Var("s")
x = Var("x")

# A local scale-law model around a biological reference scale.
model = taylor_model_from_symbolic(exp(0.08 * s), s, center=-12, order=8, sample_point=-11.5)
value, remainder = model.enclosure(-11.5)

print("CNRS-H Taylor model demo")
print("center:", model.center)
print("order:", model.order)
print("value at -11.5:", value)
print("remainder indicator:", remainder)
print("domain valid at -11.5:", model.valid_for(-11.5))

outer = taylor_model_from_symbolic(exp(x), x, center=1, order=8)
inner = taylor_model_from_symbolic(1 + s * s, s, center=0, order=8)
comparison = verify_taylor_model_chain_rule(outer, inner, order=7)
print("chain rule passed:", comparison.passed)
print("max coefficient error:", comparison.max_error)
