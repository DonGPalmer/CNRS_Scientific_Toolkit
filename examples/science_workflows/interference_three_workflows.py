from pathlib import Path
import sys
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from cnrs.science.three_workflows import compare_interference

if __name__ == "__main__":
    result = compare_interference(n=1000, L=14)
    print(result.name)
    for k, v in result.metrics.items():
        print(f"{k}: {v}")
    print(result.interpretation)
