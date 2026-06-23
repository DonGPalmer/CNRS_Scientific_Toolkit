"""v0.9.0 CNRS preservation workflow demo."""
import numpy as np
from cnrs.cnrs_h_native import CnrsHNative, compose_native
from cnrs.science.workflow import build_preservation_report

# exp(2s), represented through native CNRS-H coefficient composition.
f = CnrsHNative.from_gaussian_list([1] * 10)
g = CnrsHNative.from_gaussian_list([0, 2])
h = compose_native(f, g, 8)

points = np.linspace(0, 0.5, 16)
report = build_preservation_report(h, points, name="native_exp_2s")

print(report.summary())
