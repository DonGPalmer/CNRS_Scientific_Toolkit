"""Finite-sheet global Riemann-surface scaffolding for CNRS.

The module models a branched cover by a finite set of sheets together with
monodromy permutations assigned to oriented branch-locus generators.  It is a
computational covering-space/analytic-continuation layer, not an automatic
algebraic-curve normalization package.

Core ideas
----------
* ``SheetPermutation`` acts on explicit sheet labels.
* ``PathWord`` preserves the ordered homotopy-generator word.  This is more
  informative than an abelian winding vector when monodromy is noncommutative.
* ``RiemannSurface`` stores branch loci and generator monodromies.
* ``SurfacePoint`` is a lifted endpoint: projected coordinate plus sheet.
* ``SurfaceAtlas`` stores local chart evaluators and transition validation.
* ``lift_path_word`` transports a lifted point globally through the finite
  cover and returns a complete audit trail.

The current implementation assumes isolated finite branch loci and user-supplied
monodromy.  It does not infer branch points or permutations from a polynomial,
construct Puiseux series automatically, or certify paths near singularities.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, Mapping, Sequence


class RiemannSurfaceError(ValueError):
    """Raised for invalid surface, path-word, chart, or transport data."""


Sheet = Hashable


@dataclass(frozen=True)
class SheetPermutation:
    """A bijection of a finite sheet set.

    Composition uses function order: ``p.compose(q)`` means ``p ∘ q`` and
    therefore applies ``q`` first and then ``p``.
    """

    mapping: tuple[tuple[Sheet, Sheet], ...]

    def __init__(self, mapping: Mapping[Sheet, Sheet] | Iterable[tuple[Sheet, Sheet]]) -> None:
        items = tuple(dict(mapping).items()) if isinstance(mapping, Mapping) else tuple(mapping)
        src = tuple(a for a, _ in items)
        dst = tuple(b for _, b in items)
        if not items:
            raise RiemannSurfaceError("a sheet permutation cannot be empty")
        if len(set(src)) != len(src):
            raise RiemannSurfaceError("permutation sources must be unique")
        if set(src) != set(dst):
            raise RiemannSurfaceError("permutation must map the sheet set bijectively to itself")
        object.__setattr__(self, "mapping", items)

    @classmethod
    def identity(cls, sheets: Iterable[Sheet]) -> "SheetPermutation":
        labels = tuple(sheets)
        if not labels:
            raise RiemannSurfaceError("sheet set cannot be empty")
        return cls({s: s for s in labels})

    @classmethod
    def cycle(cls, sheets: Iterable[Sheet], cycle: Sequence[Sheet]) -> "SheetPermutation":
        labels = tuple(sheets)
        cyc = tuple(cycle)
        if len(cyc) < 2:
            raise RiemannSurfaceError("a nontrivial cycle requires at least two sheets")
        if len(set(cyc)) != len(cyc) or not set(cyc).issubset(set(labels)):
            raise RiemannSurfaceError("cycle must contain distinct members of the sheet set")
        out = {s: s for s in labels}
        for a, b in zip(cyc, cyc[1:] + cyc[:1]):
            out[a] = b
        return cls(out)

    @property
    def sheets(self) -> tuple[Sheet, ...]:
        return tuple(a for a, _ in self.mapping)

    def as_dict(self) -> dict[Sheet, Sheet]:
        return dict(self.mapping)

    def apply(self, sheet: Sheet) -> Sheet:
        try:
            return self.as_dict()[sheet]
        except KeyError as exc:
            raise RiemannSurfaceError(f"unknown sheet {sheet!r}") from exc

    def inverse(self) -> "SheetPermutation":
        return SheetPermutation({b: a for a, b in self.mapping})

    def compose(self, other: "SheetPermutation") -> "SheetPermutation":
        if set(self.sheets) != set(other.sheets):
            raise RiemannSurfaceError("cannot compose permutations on different sheet sets")
        return SheetPermutation({s: self.apply(other.apply(s)) for s in other.sheets})

    def power(self, exponent: int) -> "SheetPermutation":
        n = int(exponent)
        if n == 0:
            return SheetPermutation.identity(self.sheets)
        base = self if n > 0 else self.inverse()
        result = SheetPermutation.identity(self.sheets)
        for _ in range(abs(n)):
            result = base.compose(result)
        return result

    def cycle_notation(self) -> str:
        mapping = self.as_dict()
        seen: set[Sheet] = set()
        cycles: list[str] = []
        for start in self.sheets:
            if start in seen:
                continue
            cur = start
            cyc: list[Sheet] = []
            while cur not in seen:
                seen.add(cur)
                cyc.append(cur)
                cur = mapping[cur]
            if len(cyc) > 1:
                cycles.append("(" + " ".join(map(str, cyc)) + ")")
        return "".join(cycles) or "()"


@dataclass(frozen=True)
class BranchGenerator:
    """One oriented loop generator around an isolated branch locus."""

    name: str
    locus: complex
    positive: SheetPermutation
    label: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise RiemannSurfaceError("generator name must be nonempty")

    def permutation(self, orientation: int = 1) -> SheetPermutation:
        if orientation not in {-1, 1}:
            raise RiemannSurfaceError("generator orientation must be +1 or -1")
        return self.positive if orientation == 1 else self.positive.inverse()


@dataclass(frozen=True)
class PathLetter:
    generator: str
    orientation: int = 1

    def __post_init__(self) -> None:
        if not self.generator.strip():
            raise RiemannSurfaceError("path generator name must be nonempty")
        if self.orientation not in {-1, 1}:
            raise RiemannSurfaceError("path-letter orientation must be +1 or -1")

    def inverse(self) -> "PathLetter":
        return PathLetter(self.generator, -self.orientation)

    def __str__(self) -> str:
        return self.generator if self.orientation == 1 else f"{self.generator}^-1"


@dataclass(frozen=True)
class PathWord:
    """Reduced ordered word in branch-locus loop generators."""

    letters: tuple[PathLetter, ...] = ()

    def __init__(self, letters: Iterable[PathLetter | tuple[str, int] | str] = ()) -> None:
        parsed: list[PathLetter] = []
        for item in letters:
            if isinstance(item, PathLetter):
                letter = item
            elif isinstance(item, str):
                letter = PathLetter(item, 1)
            else:
                name, orientation = item
                letter = PathLetter(str(name), int(orientation))
            if parsed and parsed[-1].generator == letter.generator and parsed[-1].orientation == -letter.orientation:
                parsed.pop()
            else:
                parsed.append(letter)
        object.__setattr__(self, "letters", tuple(parsed))

    @classmethod
    def parse(cls, text: str) -> "PathWord":
        letters: list[PathLetter] = []
        for token in text.split():
            if token.endswith("^-1"):
                letters.append(PathLetter(token[:-3], -1))
            else:
                letters.append(PathLetter(token, 1))
        return cls(letters)

    def __mul__(self, other: "PathWord") -> "PathWord":
        return PathWord(self.letters + other.letters)

    def inverse(self) -> "PathWord":
        return PathWord(letter.inverse() for letter in reversed(self.letters))

    def winding_vector(self, generator_names: Iterable[str] | None = None) -> dict[str, int]:
        names = list(generator_names or [])
        out = {name: 0 for name in names}
        for letter in self.letters:
            out[letter.generator] = out.get(letter.generator, 0) + letter.orientation
        return out

    def __str__(self) -> str:
        return " ".join(map(str, self.letters)) or "1"


@dataclass(frozen=True)
class SurfacePoint:
    """A point on the lifted finite-sheet surface."""

    z: complex
    sheet: Sheet
    chart: str | None = None


@dataclass(frozen=True)
class TransportStep:
    index: int
    letter: PathLetter
    before_sheet: Sheet
    after_sheet: Sheet
    permutation: SheetPermutation


@dataclass(frozen=True)
class LiftedTransport:
    start: SurfacePoint
    end: SurfacePoint
    word: PathWord
    monodromy: SheetPermutation
    steps: tuple[TransportStep, ...]

    @property
    def closed_on_surface(self) -> bool:
        return self.start.z == self.end.z and self.start.sheet == self.end.sheet


@dataclass(frozen=True)
class SurfaceChart:
    """A local evaluator for one or more sheets over a projected domain.

    ``contains`` determines whether the projected point lies in the chart.
    ``evaluate`` returns the analytic branch value on a requested sheet.
    """

    name: str
    contains: Callable[[complex], bool]
    evaluate: Callable[[complex, Sheet], complex]
    sheets: tuple[Sheet, ...]
    center: complex | None = None
    radius: float | None = None

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise RiemannSurfaceError("chart name must be nonempty")
        if not self.sheets:
            raise RiemannSurfaceError("chart must expose at least one sheet")
        if self.radius is not None and self.radius <= 0:
            raise RiemannSurfaceError("chart radius must be positive")

    def value(self, point: SurfacePoint) -> complex:
        if point.sheet not in self.sheets:
            raise RiemannSurfaceError(f"chart {self.name!r} does not contain sheet {point.sheet!r}")
        if not self.contains(point.z):
            raise RiemannSurfaceError(f"projected point {point.z!r} lies outside chart {self.name!r}")
        return complex(self.evaluate(point.z, point.sheet))


@dataclass(frozen=True)
class SurfaceAtlas:
    charts: tuple[SurfaceChart, ...]

    def __init__(self, charts: Iterable[SurfaceChart]) -> None:
        data = tuple(charts)
        names = [chart.name for chart in data]
        if len(set(names)) != len(names):
            raise RiemannSurfaceError("chart names must be unique")
        object.__setattr__(self, "charts", data)

    def by_name(self) -> dict[str, SurfaceChart]:
        return {chart.name: chart for chart in self.charts}

    def charts_for(self, point: SurfacePoint) -> tuple[SurfaceChart, ...]:
        return tuple(c for c in self.charts if point.sheet in c.sheets and c.contains(point.z))

    def evaluate(self, point: SurfacePoint, chart: str | None = None) -> complex:
        if chart is not None:
            try:
                return self.by_name()[chart].value(point)
            except KeyError as exc:
                raise RiemannSurfaceError(f"unknown chart {chart!r}") from exc
        choices = self.charts_for(point)
        if not choices:
            raise RiemannSurfaceError("no atlas chart contains the lifted point")
        return choices[0].value(point)

    def overlap_error(self, point: SurfacePoint, chart_a: str, chart_b: str) -> float:
        charts = self.by_name()
        try:
            va = charts[chart_a].value(point)
            vb = charts[chart_b].value(point)
        except KeyError as exc:
            raise RiemannSurfaceError(f"unknown chart {exc.args[0]!r}") from exc
        return abs(va - vb)

    def validate_overlap(self, point: SurfacePoint, chart_a: str, chart_b: str, *, tolerance: float = 1e-10) -> bool:
        return self.overlap_error(point, chart_a, chart_b) <= tolerance


@dataclass(frozen=True)
class RiemannSurface:
    """A finite branched cover specified by monodromy generators."""

    name: str
    sheets: tuple[Sheet, ...]
    generators: tuple[BranchGenerator, ...]
    atlas: SurfaceAtlas | None = None
    basepoint: complex | None = None

    def __init__(
        self,
        name: str,
        sheets: Iterable[Sheet],
        generators: Iterable[BranchGenerator],
        *,
        atlas: SurfaceAtlas | None = None,
        basepoint: complex | None = None,
    ) -> None:
        labels = tuple(sheets)
        if not labels or len(set(labels)) != len(labels):
            raise RiemannSurfaceError("surface sheets must be a nonempty unique set")
        gens = tuple(generators)
        names = [g.name for g in gens]
        if len(set(names)) != len(names):
            raise RiemannSurfaceError("branch-generator names must be unique")
        for gen in gens:
            if set(gen.positive.sheets) != set(labels):
                raise RiemannSurfaceError(f"generator {gen.name!r} acts on the wrong sheet set")
        if atlas is not None:
            for chart in atlas.charts:
                if not set(chart.sheets).issubset(set(labels)):
                    raise RiemannSurfaceError(f"chart {chart.name!r} contains unknown sheets")
        object.__setattr__(self, "name", str(name))
        object.__setattr__(self, "sheets", labels)
        object.__setattr__(self, "generators", gens)
        object.__setattr__(self, "atlas", atlas)
        object.__setattr__(self, "basepoint", None if basepoint is None else complex(basepoint))

    def generator_map(self) -> dict[str, BranchGenerator]:
        return {g.name: g for g in self.generators}

    def monodromy(self, word: PathWord) -> SheetPermutation:
        result = SheetPermutation.identity(self.sheets)
        generators = self.generator_map()
        for letter in word.letters:
            try:
                p = generators[letter.generator].permutation(letter.orientation)
            except KeyError as exc:
                raise RiemannSurfaceError(f"unknown path generator {letter.generator!r}") from exc
            result = p.compose(result)
        return result

    def lift(self, start: SurfacePoint, word: PathWord, *, endpoint: complex | None = None) -> LiftedTransport:
        if start.sheet not in self.sheets:
            raise RiemannSurfaceError(f"unknown start sheet {start.sheet!r}")
        generators = self.generator_map()
        sheet = start.sheet
        steps: list[TransportStep] = []
        aggregate = SheetPermutation.identity(self.sheets)
        for index, letter in enumerate(word.letters):
            try:
                permutation = generators[letter.generator].permutation(letter.orientation)
            except KeyError as exc:
                raise RiemannSurfaceError(f"unknown path generator {letter.generator!r}") from exc
            new_sheet = permutation.apply(sheet)
            steps.append(TransportStep(index, letter, sheet, new_sheet, permutation))
            sheet = new_sheet
            aggregate = permutation.compose(aggregate)
        end = SurfacePoint(start.z if endpoint is None else complex(endpoint), sheet, start.chart)
        return LiftedTransport(start, end, word, aggregate, tuple(steps))

    def orbit(self, sheet: Sheet) -> frozenset[Sheet]:
        if sheet not in self.sheets:
            raise RiemannSurfaceError(f"unknown sheet {sheet!r}")
        reached = {sheet}
        frontier = [sheet]
        perms = [g.positive for g in self.generators] + [g.positive.inverse() for g in self.generators]
        while frontier:
            current = frontier.pop()
            for p in perms:
                nxt = p.apply(current)
                if nxt not in reached:
                    reached.add(nxt)
                    frontier.append(nxt)
        return frozenset(reached)

    @property
    def connected(self) -> bool:
        return len(self.orbit(self.sheets[0])) == len(self.sheets)

    def evaluate(self, point: SurfacePoint, chart: str | None = None) -> complex:
        if self.atlas is None:
            raise RiemannSurfaceError("surface has no atlas evaluator")
        return self.atlas.evaluate(point, chart)


def cyclic_root_surface(
    degree: int,
    *,
    locus: complex = 0,
    name: str | None = None,
    evaluator: Callable[[complex, int], complex] | None = None,
) -> RiemannSurface:
    """Construct the finite monodromy model for ``w**degree = z-locus``.

    The default atlas evaluator uses the principal argument and multiplies by
    the degree-th root of unity associated with the explicit sheet label.
    """

    import cmath

    n = int(degree)
    if n < 2:
        raise RiemannSurfaceError("root degree must be at least 2")
    sheets = tuple(range(n))
    generator = BranchGenerator("a", complex(locus), SheetPermutation.cycle(sheets, sheets))

    if evaluator is None:
        def evaluator(z: complex, sheet: int) -> complex:
            local = complex(z) - complex(locus)
            if local == 0:
                return 0j
            root = cmath.exp(cmath.log(local) / n)
            return root * cmath.exp(2j * cmath.pi * int(sheet) / n)

    chart = SurfaceChart(
        "principal-cut",
        contains=lambda z: complex(z) != complex(locus),
        evaluate=evaluator,
        sheets=sheets,
    )
    return RiemannSurface(name or f"{n}-root surface", sheets, [generator], atlas=SurfaceAtlas([chart]))


def surface_from_monodromy(
    name: str,
    sheets: Iterable[Sheet],
    branch_data: Mapping[str, tuple[complex, Mapping[Sheet, Sheet] | SheetPermutation]],
    *,
    atlas: SurfaceAtlas | None = None,
    basepoint: complex | None = None,
) -> RiemannSurface:
    """Convenience constructor from named loci and permutation mappings."""

    generators = []
    for generator_name, (locus, permutation) in branch_data.items():
        p = permutation if isinstance(permutation, SheetPermutation) else SheetPermutation(permutation)
        generators.append(BranchGenerator(generator_name, complex(locus), p))
    return RiemannSurface(name, sheets, generators, atlas=atlas, basepoint=basepoint)
