# CNRS Scientific Toolkit v0.15.0 finite-convolution API contract

Status: HOLD REPAIRED; INDEPENDENT RE-AUDIT REQUIRED

## Canonical scalar types

```python
GaussianInteger: TypeAlias = tuple[int, int]
GaussianLike: TypeAlias = int | GaussianInteger

@dataclass(frozen=True)
class GaussianRational:
    numerator: GaussianInteger
    denominator: GaussianInteger
```

A stored Gaussian integer is exactly a two-tuple whose components have `type(x) is int`. Public constructors accept `GaussianLike`: a value with `type(x) is int` becomes `(x, 0)`; a valid pair is preserved; Boolean values, lists, floats, complex values, subclasses with non-exact component types, and malformed pairs raise `TypeError`. Zero is `(0,0)`.

`GaussianRational` rejects a zero denominator and is reduced and unit-normalized using exact Gaussian gcd rules. Zero is `((0,0),(1,0))`. Equality is mathematical equality after canonical reduction.

## Finite carrier and Laurent evaluation

```python
@dataclass(frozen=True, init=False)
class CNRSFiniteSequence:
    coefficients: tuple[GaussianInteger, ...]
    offset: int = 0

    def __init__(self, coefficients: Iterable[GaussianLike], offset: int = 0): ...
    @property
    def support(self) -> tuple[int, int] | None: ...
    def coefficient(self, exponent: int) -> GaussianInteger: ...
    def evaluate(self, base: GaussianLike) -> GaussianRational: ...
    def trimmed(self) -> "CNRSFiniteSequence": ...
```

`offset` requires `type(offset) is int`. Construction coerces then trims zero coefficients at both ends, increasing the offset for each leading stored zero. Zero canonicalizes to empty coefficients and offset zero. For nonzero storage, support is `(offset, offset+len(coefficients)-1)`.

Evaluation computes (sum_k a_k b^k) exactly. Base zero with any negative exponent raises `ZeroDivisionError`. Negative powers are represented through the canonical `GaussianRational` denominator; evaluation never rounds.

## Product count and traversal

For canonical stored lengths `m` and `n`, `required_products = m*n`. Every stored position pair counts, including internal zero coefficients. Zero input therefore requires zero products. Traversal is deterministic row-major order: `i=0..m-1` outer, `j=0..n-1` inner, accumulating at stored output index `i+j`.

## Status, progress, result, and exceptions

```python
class ConvolutionStatus(str, Enum):
    COMPLETE = "complete"
    LIMIT_REACHED = "limit_reached"

@dataclass(frozen=True)
class ConvolutionProgress:
    status: ConvolutionStatus
    products_completed: int
    products_required: int
    last_pair: tuple[int, int] | None
    result: CNRSFiniteSequence | None

@dataclass(frozen=True)
class MultiplicationResult:
    status: ConvolutionStatus
    products_completed: int
    products_required: int
    raw_convolution: CNRSFiniteSequence | None
    normalized: CNRSFiniteSequence | None
    witness: ConvolutionWitness | None

class ConvolutionLimitError(RuntimeError): ...
```

Limits require a nonnegative exact `int` or `None`; Boolean and non-integer values raise `TypeError`, negatives raise `ValueError`. `chunk_products` requires a positive exact integer.

`convolve_exact` precomputes the required count. If it exceeds `max_products`, it raises `ConvolutionLimitError` before multiplication. Otherwise it returns the complete trimmed sequence.

`iter_convolution` emits a progress record after each full chunk and then exactly one terminal record. If the limit is below the required count, it performs exactly `max_products` products and terminates with `LIMIT_REACHED`; that terminal has `result=None`. A complete terminal has the sole authoritative result. When zero products are required, it emits one `COMPLETE` terminal with canonical zero. No duplicate terminal is emitted when a chunk boundary equals completion.

`multiply_with_witness` never raises `ConvolutionLimitError` for an otherwise valid limit. It returns `LIMIT_REACHED` with all three result/witness fields `None`, or `COMPLETE` with raw convolution, optional normalized result, and a witness. Invalid arguments still raise their specified type/value exceptions.

## Exact normalization

```python
def normalize_gaussian_laurent(
    value: CNRSFiniteSequence,
    *,
    max_carry_steps: int | None = None,
) -> CNRSFiniteSequence: ...
```

This new function implements exact Gaussian carry recurrence in base `(-2,1)`, preserves value and Laurent offset, and returns coefficients `(d,0)` with `d in {0,1,2,3,4}`. It does not call the legacy floating-point/string normalizer. `max_carry_steps` uses the same exact-integer validation; exhaustion raises `NormalizationLimitError` and returns no partial canonical result.

## Witness schema and canonical bytes

Schema identifier: `cnrs-convolution-witness-v1`.

A complete witness contains: schema; status; canonical left/right/raw/normalized sequence objects; `normalization_requested`; `products_required`; traversal identifier `left-major-right-minor-v1`; algorithm identifier `schoolbook-gaussian-exact-v1`; and SHA-256 digests of the canonical byte encodings of left, right, raw, and normalized values (normalized digest is null when normalization was not requested).

A sequence JSON object is exactly `{"coefficients":[[re,im],...],"offset":n}`. Canonical JSON bytes are UTF-8 of `json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False, allow_nan=False)` with no BOM and no trailing newline. Digests are lowercase hexadecimal SHA-256 of those bytes.

No witness is produced for `LIMIT_REACHED`. Deserialization rejects unknown/missing keys, unknown schema/status/algorithm/traversal, noncanonical scalar encodings, digest case/length errors, and any byte-noncanonical reserialization.

`cnrs.validation.convolution_oracle.verify_convolution_witness` parses strictly, recomputes convolution with an independently coded nested loop that does not import `cnrs.convolution`, recomputes exact normalization when requested, and compares every decisive field and digest.

## Resource claim

`max_products` and `chunk_products` are product-count controls only. They do not bound coefficient bit length, Python-integer allocation, result size, carry steps, elapsed time, or total memory. Documentation must use “product-count bounded” unless additional explicit limits are later frozen.
