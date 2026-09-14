# CNRS Scientific Toolkit v0.15.0 finite-convolution API contract

Status: FROZEN FOR IMPLEMENTATION

## Public carrier

```python
@dataclass(frozen=True)
class CNRSFiniteSequence:
    coefficients: tuple[GaussianInteger, ...]
    offset: int = 0

    @property
    def support(self) -> tuple[int, int] | None: ...
    def coefficient(self, exponent: int) -> GaussianInteger: ...
    def evaluate(self, base: GaussianInteger) -> GaussianInteger: ...
    def trimmed(self) -> "CNRSFiniteSequence": ...
```

Construction trims leading and trailing zero coefficients. The zero sequence has `coefficients == ()`, `offset == 0`, and `support is None`.

## Exact convolution

```python
def convolve_exact(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    max_products: int | None = None,
) -> CNRSFiniteSequence: ...
```

The coefficient at exponent `k` is exactly
(sum_{i+j=k} a_i b_j). If the required scalar products exceed a valid limit, the function raises `ConvolutionLimitError` before presenting a completed result.

## Bounded/chunked execution

```python
def iter_convolution(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    chunk_products: int = 1024,
    max_products: int | None = None,
) -> Iterator[ConvolutionProgress]: ...
```

Progress records are deterministic and replayable. Terminal status is one of `COMPLETE` or `LIMIT_REACHED`. Only a `COMPLETE` record may carry the authoritative result.

## Multiplication and witnesses

```python
def multiply_with_witness(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    normalize: bool = True,
    max_products: int | None = None,
) -> MultiplicationResult: ...

def verify_convolution_witness(
    witness: ConvolutionWitness,
) -> WitnessValidation: ...
```

`MultiplicationResult` contains the raw convolution, optional canonical normalized form, status, operation count, and witness. The witness schema has an explicit version; canonical JSON serialization is stable and contains input/output digests, support bounds, operation count, normalization disposition, and terminal status. Validation must reject altered, truncated, non-canonical, or inconsistent witnesses.

## Exceptions and limits

- Boolean values are not accepted as integer limits.
- Limits must be non-negative integers or `None`.
- Invalid coefficient types fail before execution.
- `max_products=0` succeeds only when no scalar products are required.
- Resource exhaustion and malformed input are distinguishable.
- No API silently falls back to approximate arithmetic.

## Compatibility

No existing v0.14.1 public signature is removed or changed. New types are exported from their owning modules; top-level re-export is permitted only after acceptance tests freeze the import path.
