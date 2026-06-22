import cmath

from cnrs.cli import main, parse_expr
from cnrs.symbolic import (
    BranchState,
    Integral,
    Log,
    Sqrt,
    Var,
    diff,
    exp,
    integrate,
    log,
    pow_branch,
    sqrt,
)

TOL = 3e-4


def assert_close(a, b, tol=TOL):
    assert abs(complex(a) - complex(b)) < tol


def test_branch_state_dataclass_and_helpers():
    state = BranchState(log_branch=1, sqrt_branch=2, pow_branch=3, winding=4)
    assert state.log_branch == 1
    assert state.sqrt_branch == 2
    assert state.pow_branch == 3
    assert state.winding == 4
    assert state.for_log(5).log_branch == 5
    assert state.for_sqrt(-1).sqrt_branch == -1
    assert state.for_pow(7).pow_branch == 7
    assert "winding=4" in str(state)


def test_log_branch_string_repr_and_state():
    z = Var("z")
    state = BranchState(log_branch=2)
    expr = log(z, branch=2, branch_state=state)
    assert isinstance(expr, Log)
    assert str(expr) == "log_2(z)"
    assert "branch=2" in repr(expr)
    assert expr.branch_state.log_branch == 2


def test_log_branch_eval_changes_value():
    z = Var("z")
    val0 = log(z, branch=0).eval({"z": -1}, L=20)
    val1 = log(z, branch=1).eval({"z": -1}, L=20)
    assert_close(val0, 1j * cmath.pi)
    assert_close(val1, 3j * cmath.pi)
    assert abs(complex(val1) - complex(val0)) > 5.0


def test_sqrt_branch_eval_switches_sign():
    z = Var("z")
    root0 = sqrt(z, branch=0).eval({"z": -1}, L=20)
    root1 = sqrt(z, branch=1).eval({"z": -1}, L=20)
    assert_close(root0, 1j)
    assert_close(root1, -1j)


def test_pow_branch_eval_and_string():
    z = Var("z")
    expr = pow_branch(z, 0.5, branch=1)
    assert "branch=1" in str(expr)
    assert_close(expr.eval({"z": -1}, L=20), -1j)


def test_branch_survives_substitution():
    z = Var("z")
    expr = log(z, branch=3).substitute({"z": z + 1})
    assert isinstance(expr, Log)
    assert expr.branch == 3
    assert "log_3" in str(expr)


def test_branch_survives_diff_origin_expression_and_derivative_is_local():
    z = Var("z")
    expr = log(z, branch=4)
    dexpr = diff(expr, z).simplify()
    assert expr.branch == 4
    assert_close(dexpr.eval({"z": 2.0}, L=20), 0.5)


def test_branch_survives_integrate_power_reciprocal():
    z = Var("z")
    anti = integrate(pow_branch(z, -1, branch=2), z).simplify()
    assert isinstance(anti, Log)
    assert anti.branch == 2


def test_exp_log_not_simplified_unsafely():
    z = Var("z")
    expr = exp(log(z, branch=1)).simplify()
    assert "exp" in str(expr)
    assert "log_1" in str(expr)


def test_sqrt_square_not_simplified_unsafely():
    z = Var("z")
    expr = sqrt(z * z).simplify()
    assert isinstance(expr, Sqrt)
    assert "sqrt" in str(expr)


def test_integral_substitution_does_not_drop_branch():
    z = Var("z")
    y = Var("y")
    integral = Integral(log(z, branch=2), z).substitute({"z": y})
    # Bound variable z is protected; branch tag in integrand is still present.
    assert "log_2" in str(integral)


def test_parser_accepts_branch_keywords():
    expr = parse_expr("log(z, branch=2)")
    assert isinstance(expr, Log)
    assert expr.branch == 2
    root = parse_expr("sqrt(z, branch=1)")
    assert isinstance(root, Sqrt)
    assert root.branch == 1


def test_parser_accepts_pow_branch():
    expr = parse_expr("pow_branch(z, 0.5, branch=1)")
    assert "branch=1" in str(expr)
    assert_close(expr.eval({"z": -1}, L=20), -1j)


def test_cli_eval_log_branch(capsys):
    assert main(["eval", "log(z, branch=2)", "--at", "z=-1"]) == 0
    out = capsys.readouterr().out
    assert "log_2" in out
    assert "value:" in out


def test_cli_eval_sqrt_branch(capsys):
    assert main(["eval", "sqrt(z, branch=1)", "--at", "z=-1"]) == 0
    out = capsys.readouterr().out
    assert "sqrt_1" in out
    assert "value:" in out
