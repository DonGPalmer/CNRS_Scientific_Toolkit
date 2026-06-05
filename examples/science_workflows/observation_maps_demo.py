from pathlib import Path
import sys
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
from cnrs.science.observation import observation_table

r = np.linspace(1, 20, 400)
f = 1 + 0.05*np.exp(-r/5)
theta = np.pi/2 + 0.4/r
psi = f*np.exp(1j*theta)

maps = observation_table(psi, coord=r)
for name, values in maps.items():
    print(name, values[:3])
