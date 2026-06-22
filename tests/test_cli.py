from cnrs.cli import main, parse_expr, parse_env


def test_cli_version(capsys):
    assert main(["version"]) == 0
    out = capsys.readouterr().out
    assert "0.8.0" in out


def test_cli_convert_to_cnrs(capsys):
    assert main(["convert", "1+2j", "--to", "cnrs"]) == 0
    out = capsys.readouterr().out
    assert "CNRS" in out


def test_cli_convert_from_cnrs(capsys):
    assert main(["convert", "1", "--from", "cnrs"]) == 0
    out = capsys.readouterr().out
    assert "CNRS 1" in out
    assert "(1+0j)" in out


def test_cli_diff_symbolic(capsys):
    assert main(["diff", "sin(exp(s/L))", "--var", "s"]) == 0
    out = capsys.readouterr().out
    assert "diff:" in out
    assert "cos" in out
    assert "exp" in out


def test_cli_diff_at_point(capsys):
    assert main(["diff", "exp(k*s)", "--var", "s", "--at", "s=2,k=0.5"]) == 0
    out = capsys.readouterr().out
    assert "at s=2,k=0.5" in out
    assert "value" not in out.lower()


def test_cli_integrate_symbolic(capsys):
    assert main(["integrate", "A*exp(k*s)", "--var", "s"]) == 0
    out = capsys.readouterr().out
    assert "integral:" in out
    assert "exp" in out
    assert "k" in out


def test_cli_eval(capsys):
    assert main(["eval", "sin(exp(s/L))", "--at", "s=1.2,L=5"]) == 0
    out = capsys.readouterr().out
    assert "expr:" in out
    assert "value:" in out


def test_cli_demo(capsys):
    assert main(["demo"]) == 0
    out = capsys.readouterr().out
    assert "CNRS CLI demo" in out
    assert "symbolic derivative" in out
    assert "scale-law integral" in out


def test_parse_expression_rejects_unsafe_call():
    try:
        parse_expr("__import__('os').system('echo bad')")
    except ValueError as exc:
        assert "unsupported function" in str(exc) or "only simple" in str(exc)
    else:
        raise AssertionError("unsafe expression was accepted")


def test_parse_env_complex_i():
    env = parse_env("z=1+2i")
    assert complex(env["z"]) == complex(1, 2)


def test_cli_examples_lists_entry_points(capsys):
    assert main(["examples"]) == 0
    out = capsys.readouterr().out
    assert "CNRS example entry points" in out
    assert "symbolic-diff" in out
    assert "symbolic-integrate" in out


def test_cli_missing_variable_error_is_friendly(capsys):
    try:
        main(["eval", "s + L", "--at", "s=1"])
    except SystemExit as exc:
        assert exc.code == 2
    err = capsys.readouterr().err
    assert "no value supplied for variable" in err
    assert "Traceback" not in err
