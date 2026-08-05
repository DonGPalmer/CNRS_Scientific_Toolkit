"""Finite global Riemann-surface demonstration."""
from cnrs.riemann_surface import (
    BranchGenerator, PathWord, RiemannSurface, SheetPermutation, SurfacePoint,
    cyclic_root_surface,
)


def main() -> None:
    root = cyclic_root_surface(3)
    start = SurfacePoint(1, 0)
    print("Cubic-root surface")
    for word in (PathWord([]), PathWord(["a"]), PathWord(["a", "a"]), PathWord(["a", "a", "a"])):
        result = root.lift(start, word)
        print(f"  word={word!s:8} sheet={result.end.sheet} value={root.evaluate(result.end)}")

    sheets = (0, 1, 2)
    a = SheetPermutation.cycle(sheets, (0, 1))
    b = SheetPermutation.cycle(sheets, (1, 2))
    surface = RiemannSurface("S3 example", sheets, [BranchGenerator("a", 0, a), BranchGenerator("b", 1, b)])
    print("\nNoncommuting monodromy")
    for word in (PathWord(["a", "b"]), PathWord(["b", "a"])):
        result = surface.lift(SurfacePoint(2, 0), word)
        print(f"  word={word}, winding={word.winding_vector(['a','b'])}, sheet={result.end.sheet}, monodromy={result.monodromy.cycle_notation()}")


if __name__ == "__main__":
    main()
