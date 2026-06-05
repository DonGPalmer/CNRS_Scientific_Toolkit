from pathlib import Path
import sys
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
from cnrs.science.scale_law import fit_egf_scale_law

rho = np.linspace(-2, 2, 100)
y = 0.8*np.exp(-0.7*rho) + 0.35*np.exp(0.9*rho)
fit = fit_egf_scale_law(rho, y, degree=10, name="two_exponential_fit")
dfit = fit.derivative()

err = np.linalg.norm(fit(rho).real - y) / np.linalg.norm(y)
print("fit relative L2 error:", err)
print("log derivative samples:", dfit(rho[:5]) / fit(rho[:5]))
