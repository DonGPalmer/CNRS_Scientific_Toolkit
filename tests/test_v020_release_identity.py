"""Candidate release identity check; no publication is implied."""
from importlib.metadata import version
from pathlib import Path
import cnrs

def test_v020_candidate_package_identity():
    assert cnrs.__version__ == "0.20.0"
    assert version("cnrs") == "0.20.0"
    assert Path(cnrs.__file__).is_file()

def test_experimental_modules_remain_qualified():
    from cnrs.cnrs_h_finite_exact import RA, HurwitzJet
    from cnrs.cnrs_h_limits import BoundedFiniteOps
    from cnrs.cnrs_h_toolkit_interop import ToolkitDigitOps
    assert BoundedFiniteOps().decode("1") == RA(1)
    assert HurwitzJet.from_coefficients(1).coefficient(0) == RA(1)
    assert not hasattr(cnrs, "BoundedFiniteOps")
    assert not hasattr(cnrs, "ToolkitDigitOps")
