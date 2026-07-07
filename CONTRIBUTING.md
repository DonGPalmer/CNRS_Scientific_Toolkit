# Contributing

Thank you for considering a contribution to the CNRS Scientific Toolkit.

This repository is an **open research-code package**. Contributions are welcome when they improve reproducibility, clarify the implementation, add well-scoped examples, or test existing claims. The project is not presented as a finished theory or production numerical library.
Contributions should preserve the distinction between mathematical claims,
implemented algorithms, and exploratory workflows.

## Development setup

From the repository root:

```bash
pip install -e .
pip install pytest numpy scipy
python -m pytest -q
```

Optional dependencies used by a small number of helpers include `pandas`.

## What to contribute

Good contributions include:

- Bug fixes with regression tests.
- Documentation clarifications.
- Additional tests for existing modules.
- Small examples that demonstrate a specific workflow.
- Reproducibility scripts linked to papers or technical notes.
- Independent checks of formulas or algorithms.

Please avoid large conceptual rewrites unless they are discussed first. New scientific modules should be clearly marked as research demonstrations unless they are independently validated.

## Claim-status discipline

When adding or changing functionality, update the relevant status files when appropriate:

- `docs/CLAIM_STATUS.md` — what is tested, practical, open, or conjectural.
- `docs/TEST_STATUS.md` — current automated-test status.
- `docs/EXAMPLE_SMOKE_STATUS.md` — runnable example status.

Use cautious wording. The existence of code does not establish the associated scientific hypothesis.

## Tests

Every new module should have tests where practical. Every new example should at least run as a smoke test.

Before submitting changes, run:

```bash
python -m pytest -q
python examples/quickstart_cnrs.py
```

If an example requires optional dependencies, document them in the example header.

## Examples

Examples should be placed under `examples/` or a subfolder such as `examples/science_workflows/`.

Each example should state whether it is:

- a quickstart demonstration,
- a benchmark,
- a paper-linked reproducibility example,
- or an exploratory research example.

## Code style

The codebase currently favors readable, dependency-light Python over heavy framework abstractions. Keep public APIs small, documented, and tested.

## Versioning

Public releases should update:

- `pyproject.toml`
- `cnrs/__init__.py`, if the visible package description changes
- `RELEASE_NOTES.md`
- `SOURCE_INDEX.txt`
- relevant files in `docs/`

Generated files such as `__pycache__/` and `.pytest_cache/` should not be committed.
