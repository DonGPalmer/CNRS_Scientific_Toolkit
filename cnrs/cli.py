"""
cnrs.cli
========

A small command-line interface for the CNRS Scientific Toolkit.

The CLI is intentionally modest.  It exposes the most useful inspection and
symbolic-calculus workflows without trying to become a full computer-algebra
system or graphical front end.

Examples
--------
    cnrs version
    cnrs convert "1+2j" --to cnrs
    cnrs convert "104" --from cnrs
    cnrs eval "sin(exp(s/L))" --at s=1.2,L=5
    cnrs eval "log(z, branch=2)" --at z=-1
    cnrs diff "sin(exp(s/L))" --var s
    cnrs diff "sin(exp(s/L))" --var s --at s=1.2,L=5
    cnrs integrate "A*exp(k*s)" --var s
    cnrs examples
    cnrs demo
"""

from __future__ import annotations

import argparse
import ast
import math
import re
import sys
from typing import Any, Mapping

from . import __version__
from .cnrs_repr import gaussian_to_cnrs_str, cnrs_to_gaussian, normalize_cnrs
from .cnrs_complex import CnrsComplex, DEFAULT_L
from . import symbolic as sym


# ---------------------------------------------------------------------------
# Small safe symbolic parser
# ---------------------------------------------------------------------------

_ALLOWED_FUNCS = {
    "exp": sym.exp,
    "log": sym.log,
    "sin": sym.sin,
    "cos": sym.cos,
    "tan": sym.tan,
    "sqrt": sym.sqrt,
    "pow_branch": sym.pow_branch,
}

_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "i": 1j,
    "j": 1j,
}

_EXAMPLES = [
    ("quickstart", "examples/quickstart_cnrs.py", "basic CNRS arithmetic and conversion"),
    ("demo", "examples/demo.py", "general package demonstration"),
    ("scale-integration", "examples/scale_integration.py", "CNRS-H scale integration demonstration"),
    ("chain-rule", "examples/science_workflows/chain_rule_scale_law.py", "first-order chain-rule autodiff for a scale law"),
    ("symbolic-diff", "examples/science_workflows/symbolic_chain_rule_demo.py", "minimal symbolic differentiation and autodiff cross-check"),
    ("symbolic-integrate", "examples/science_workflows/symbolic_integration_demo.py", "conservative rule-based symbolic integration"),
    ("branch-symbolic", "examples/science_workflows/branch_aware_symbolic_demo.py", "explicit branch-aware symbolic log/sqrt/power workflows"),
    ("symbolic-to-h", "examples/science_workflows/symbolic_to_cnrs_h_demo.py", "symbolic calculus to CNRS-H coefficient bridge"),
    ("rd-scale-exit", "examples/science_workflows/cnrs_rd_scale_exit_demo.py", "reaction-diffusion scale-exit workflow"),
    ("phase-branch", "examples/science_workflows/phase_branch_tracking.py", "phase/branch-tracking workflow"),
]

_ALLOWED_NAME = re.compile(r"^[A-Za-z_]\w*$")


def _normalize_expr_text(text: str) -> str:
    """Accept mathematical ``i`` notation where Python expects ``j``."""
    # 2i -> 2j, 2.5i -> 2.5j, and standalone i -> j via constants.
    text = re.sub(r"(?<=\d)i\b", "j", text)
    text = re.sub(r"(?<=\))i\b", "*j", text)
    return text


def parse_expr(text: str) -> sym.Expr:
    """Parse a small expression language into ``cnrs.symbolic`` expressions.

    Supported syntax is Python-like arithmetic: ``+``, ``-``, ``*``, ``/``,
    ``**``, parentheses, variables, numeric literals, and the functions
    ``exp``, ``log``, ``sin``, ``cos``, ``tan``, and ``sqrt``.
    """
    tree = ast.parse(_normalize_expr_text(text), mode="eval")
    return _build_expr(tree.body)


def _build_expr(node: ast.AST) -> sym.Expr:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, complex)):
            return sym.Const(node.value)
        raise ValueError(f"unsupported literal: {node.value!r}")

    if isinstance(node, ast.Name):
        if node.id in _CONSTANTS:
            return sym.Const(_CONSTANTS[node.id])
        if not _ALLOWED_NAME.match(node.id):
            raise ValueError(f"invalid variable name: {node.id!r}")
        return sym.Var(node.id)

    if isinstance(node, ast.UnaryOp):
        val = _build_expr(node.operand)
        if isinstance(node.op, ast.USub):
            return -val
        if isinstance(node.op, ast.UAdd):
            return val
        raise ValueError("unsupported unary operator")

    if isinstance(node, ast.BinOp):
        left = _build_expr(node.left)
        right = _build_expr(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left ** right
        raise ValueError("unsupported binary operator")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("only simple function calls are supported")
        name = node.func.id
        if name not in _ALLOWED_FUNCS:
            raise ValueError(f"unsupported function: {name}")
        kwargs = {kw.arg: _literal_keyword_value(kw.value) for kw in node.keywords}
        if name in {"log", "sqrt"}:
            if len(node.args) != 1:
                raise ValueError(f"{name} expects exactly one positional argument")
            arg = _build_expr(node.args[0])
            branch = int(kwargs.pop("branch", 0))
            if kwargs:
                raise ValueError(f"unsupported keyword(s) for {name}: {sorted(kwargs)}")
            return _ALLOWED_FUNCS[name](arg, branch=branch)
        if name == "pow_branch":
            if len(node.args) != 2:
                raise ValueError("pow_branch expects exactly two positional arguments")
            base = _build_expr(node.args[0])
            exponent = _build_expr(node.args[1])
            branch = int(kwargs.pop("branch", 0))
            if kwargs:
                raise ValueError(f"unsupported keyword(s) for {name}: {sorted(kwargs)}")
            return sym.pow_branch(base, exponent, branch=branch)
        if len(node.args) != 1:
            raise ValueError(f"{name} expects exactly one positional argument")
        arg = _build_expr(node.args[0])
        if kwargs:
            raise ValueError(f"unsupported keyword(s) for {name}: {sorted(kwargs)}")
        return _ALLOWED_FUNCS[name](arg)

    raise ValueError(f"unsupported expression syntax: {ast.dump(node)}")


def _literal_keyword_value(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    raise ValueError("only literal keyword values are supported")


# ---------------------------------------------------------------------------
# Environment/value parsing
# ---------------------------------------------------------------------------


def parse_scalar(text: str, *, L: int = DEFAULT_L) -> CnrsComplex:
    """Parse a scalar into ``CnrsComplex``; accepts Python j or math i."""
    t = text.strip().replace("i", "j")
    try:
        return CnrsComplex(complex(t), L=L)
    except Exception as exc:  # noqa: BLE001 - CLI should report a friendly error.
        raise argparse.ArgumentTypeError(f"could not parse scalar {text!r}") from exc


def parse_env(text: str | None, *, L: int = DEFAULT_L) -> dict[str, CnrsComplex]:
    """Parse assignments such as ``s=1.2,L=5,z=1+2i``."""
    env: dict[str, CnrsComplex] = {}
    if not text:
        return env
    for part in text.split(","):
        item = part.strip()
        if not item:
            continue
        if "=" not in item:
            raise argparse.ArgumentTypeError(f"expected NAME=VALUE in --at, got {item!r}")
        name, value = item.split("=", 1)
        name = name.strip()
        if not _ALLOWED_NAME.match(name):
            raise argparse.ArgumentTypeError(f"invalid variable name in --at: {name!r}")
        env[name] = parse_scalar(value.strip(), L=L)
    return env


def _display_value(value: Any) -> str:
    if isinstance(value, CnrsComplex):
        return f"{value}  ≈ {complex(value)}"
    return str(value)


def _format_cli_error(exc: BaseException) -> str:
    """Convert common expression/evaluation errors to short CLI messages."""
    if isinstance(exc, KeyError):
        return str(exc).strip("'")
    return str(exc)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


def cmd_version(args: argparse.Namespace) -> int:
    print(f"CNRS Scientific Toolkit {__version__}")
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    if args.from_cnrs:
        z = cnrs_to_gaussian(args.value)
        print(f"CNRS {normalize_cnrs(args.value)} = {z}")
        return 0

    z = complex(args.value.strip().replace("i", "j"))
    if abs(z.real - round(z.real)) > 1e-12 or abs(z.imag - round(z.imag)) > 1e-12:
        raise SystemExit("convert --to cnrs currently requires a Gaussian integer value")
    s = gaussian_to_cnrs_str(z)
    print(f"{z} = CNRS {s}")
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    expr = parse_expr(args.expr).simplify()
    env = parse_env(args.at, L=args.L)
    value = expr.eval(env, L=args.L)
    print(f"expr: {expr}")
    print(f"value: {_display_value(value)}")
    return 0


def cmd_diff(args: argparse.Namespace) -> int:
    expr = parse_expr(args.expr).simplify()
    dexpr = sym.diff(expr, args.var).simplify()
    print(f"expr: d/d{args.var} {expr}")
    print(f"diff: {dexpr}")
    if args.at:
        env = parse_env(args.at, L=args.L)
        value = dexpr.eval(env, L=args.L)
        print(f"at {args.at}: {_display_value(value)}")
    return 0


def cmd_integrate(args: argparse.Namespace) -> int:
    expr = parse_expr(args.expr).simplify()
    integral = sym.integrate(expr, args.var).simplify()
    print(f"expr: ∫ {expr} d{args.var}")
    print(f"integral: {integral}")
    if args.at:
        env = parse_env(args.at, L=args.L)
        try:
            value = integral.eval(env, L=args.L)
        except NotImplementedError as exc:
            print(f"at {args.at}: unevaluated ({exc})")
        else:
            print(f"at {args.at}: {_display_value(value)}")
    return 0


def cmd_examples(args: argparse.Namespace) -> int:
    """List packaged examples that are useful entry points."""
    print("CNRS example entry points")
    for name, path, desc in _EXAMPLES:
        print(f"  {name:18s} {path:62s} {desc}")
    print()
    print("Run an example from the repository root, for example:")
    print("  python examples/science_workflows/symbolic_chain_rule_demo.py")
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    s = sym.Var("s")
    L = sym.Var("L")
    A = sym.Var("A")
    k = sym.Var("k")

    expr = sym.sin(sym.exp(s / L))
    d_expr = sym.diff(expr, s).simplify()
    scale_law = A * sym.exp(k * s)
    int_law = sym.integrate(scale_law, s).simplify()

    env = {"s": CnrsComplex(1.2, L=args.L), "L": CnrsComplex(5.0, L=args.L),
           "A": CnrsComplex(2.0, L=args.L), "k": CnrsComplex(0.3, L=args.L)}

    print("CNRS CLI demo")
    print(f"chain-rule expr: {expr}")
    print(f"symbolic derivative: {d_expr}")
    print(f"derivative at s=1.2,L=5: {_display_value(d_expr.eval(env, L=args.L))}")
    print(f"scale-law integral: ∫ {scale_law} ds = {int_law}")
    print(f"integral at A=2,k=0.3,s=1.2: {_display_value(int_law.eval(env, L=args.L))}")
    return 0


# ---------------------------------------------------------------------------
# Parser / entry point
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cnrs",
        description="Command-line interface for the CNRS Scientific Toolkit.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  cnrs version\n"
            "  cnrs convert '1+2j' --to cnrs\n"
            "  cnrs eval 'sin(exp(s/L))' --at s=1.2,L=5\n"
            "  cnrs diff 'sin(exp(s/L))' --var s --at s=1.2,L=5\n"
            "  cnrs integrate 'A*exp(k*s)' --var s\n"
            "  cnrs examples"
        ),
    )
    parser.add_argument("--L", type=int, default=DEFAULT_L, help="CNRS mantissa length for numeric evaluation")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("version", help="show package version")
    p.set_defaults(func=cmd_version)

    p = sub.add_parser("convert", help="convert between Gaussian integers and CNRS-A digit strings")
    p.add_argument("value", help="value to convert, e.g. '1+2j' or CNRS digit string '104'")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--to", choices=["cnrs"], help="convert Gaussian integer to CNRS-A digit string")
    mode.add_argument("--from", dest="from_cnrs", choices=["cnrs"], help="convert CNRS-A digit string to Gaussian value")
    p.set_defaults(func=cmd_convert)

    p = sub.add_parser("eval", help="evaluate a symbolic expression")
    p.add_argument("expr", help="expression, e.g. 'sin(exp(s/L))'")
    p.add_argument("--at", help="comma-separated assignments, e.g. 's=1.2,L=5'")
    p.set_defaults(func=cmd_eval)

    p = sub.add_parser("diff", help="symbolically differentiate an expression")
    p.add_argument("expr", help="expression, e.g. 'sin(exp(s/L))'")
    p.add_argument("--var", default="s", help="variable of differentiation")
    p.add_argument("--at", help="optionally evaluate derivative at assignments")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("integrate", help="conservatively symbolically integrate an expression")
    p.add_argument("expr", help="expression, e.g. 'A*exp(k*s)'")
    p.add_argument("--var", default="s", help="variable of integration")
    p.add_argument("--at", help="optionally evaluate antiderivative at assignments")
    p.set_defaults(func=cmd_integrate)

    p = sub.add_parser("examples", help="list packaged example scripts")
    p.set_defaults(func=cmd_examples)

    p = sub.add_parser("demo", help="run a small symbolic calculus demonstration")
    p.set_defaults(func=cmd_demo)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (ValueError, TypeError, KeyError, NotImplementedError, argparse.ArgumentTypeError) as exc:
        parser.error(_format_cli_error(exc))
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
