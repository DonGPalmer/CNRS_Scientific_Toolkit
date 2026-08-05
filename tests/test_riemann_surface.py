import cmath

import pytest

from cnrs.riemann_surface import (
    BranchGenerator,
    PathWord,
    RiemannSurface,
    RiemannSurfaceError,
    SheetPermutation,
    SurfaceAtlas,
    SurfaceChart,
    SurfacePoint,
    cyclic_root_surface,
    surface_from_monodromy,
)


def test_permutation_composition_and_inverse():
    sheets = (0, 1, 2)
    a = SheetPermutation.cycle(sheets, (0, 1, 2))
    assert a.apply(0) == 1
    assert a.power(3).cycle_notation() == "()"
    assert a.inverse().apply(0) == 2
    assert a.compose(a.inverse()).cycle_notation() == "()"


def test_path_word_free_reduction_and_winding_vector():
    word = PathWord(["a", "b", ("b", -1), ("a", -1), "c"])
    assert str(word) == "c"
    assert word.winding_vector(["a", "b", "c"]) == {"a": 0, "b": 0, "c": 1}


def test_square_root_surface_one_loop_changes_sheet_two_returns():
    surface = cyclic_root_surface(2)
    start = SurfacePoint(1 + 0j, 0)
    one = surface.lift(start, PathWord(["a"]))
    two = surface.lift(start, PathWord(["a", "a"]))
    assert one.end.sheet == 1
    assert two.end.sheet == 0
    assert not one.closed_on_surface
    assert two.closed_on_surface
    assert abs(surface.evaluate(one.end) + 1) < 1e-12


def test_cubic_root_surface_has_three_sheet_cycle():
    surface = cyclic_root_surface(3)
    start = SurfacePoint(1 + 0j, 0)
    assert surface.lift(start, PathWord(["a"])).end.sheet == 1
    assert surface.lift(start, PathWord(["a", "a"])).end.sheet == 2
    assert surface.lift(start, PathWord(["a", "a", "a"])).end.sheet == 0
    assert surface.connected


def test_noncommuting_monodromy_preserves_path_order():
    sheets = (0, 1, 2)
    # a=(0 1), b=(1 2); ab and ba have equal winding vectors but differ.
    a = SheetPermutation.cycle(sheets, (0, 1))
    b = SheetPermutation.cycle(sheets, (1, 2))
    surface = RiemannSurface(
        "S3 example",
        sheets,
        [BranchGenerator("a", 0, a), BranchGenerator("b", 1, b)],
    )
    ab = PathWord(["a", "b"])
    ba = PathWord(["b", "a"])
    assert ab.winding_vector(["a", "b"]) == ba.winding_vector(["a", "b"])
    assert surface.monodromy(ab).mapping != surface.monodromy(ba).mapping
    assert surface.lift(SurfacePoint(2, 0), ab).end.sheet != surface.lift(SurfacePoint(2, 0), ba).end.sheet


def test_inverse_word_returns_to_original_sheet():
    surface = cyclic_root_surface(5)
    word = PathWord(["a", "a", "a"])
    round_trip = word * word.inverse()
    result = surface.lift(SurfacePoint(1, 2), round_trip)
    assert result.end.sheet == 2
    assert result.monodromy.cycle_notation() == "()"


def test_surface_atlas_overlap_validation():
    sheets = (0, 1)
    c1 = SurfaceChart("c1", lambda z: abs(z) < 2, lambda z, s: ((-1) ** s) * cmath.sqrt(z), sheets)
    c2 = SurfaceChart("c2", lambda z: abs(z - 1) < 2, lambda z, s: ((-1) ** s) * cmath.sqrt(z), sheets)
    atlas = SurfaceAtlas([c1, c2])
    point = SurfacePoint(1, 1)
    assert atlas.validate_overlap(point, "c1", "c2")
    assert atlas.overlap_error(point, "c1", "c2") == 0


def test_surface_from_monodromy_convenience_constructor():
    sheets = ("u", "v")
    surface = surface_from_monodromy(
        "two-sheet",
        sheets,
        {"zero": (0, {"u": "v", "v": "u"})},
    )
    result = surface.lift(SurfacePoint(2, "u"), PathWord(["zero"]))
    assert result.end.sheet == "v"


def test_rejects_invalid_permutation():
    with pytest.raises(RiemannSurfaceError):
        SheetPermutation({0: 0, 1: 0})
