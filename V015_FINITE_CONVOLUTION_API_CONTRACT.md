# CNRS Scientific Toolkit v0.15.0 finite-convolution API contract

Status: SECOND HOLD REPAIRED; INDEPENDENT RE-AUDIT REQUIRED

## Scalars and canonical rational representative

```python
GaussianInteger: TypeAlias = tuple[int, int]
GaussianLike: TypeAlias = int | GaussianInteger

@dataclass(frozen=True)
class GaussianRational:
    numerator: GaussianInteger
    denominator: GaussianInteger

    def __init__(self, numerator: GaussianLike, denominator: GaussianLike = 1): ...
```

Stored Gaussian components require `type(x) is int`. A public non-Boolean exact `int` coerces to `(x,0)`; a valid pair is preserved. Boolean, float, complex, list, malformed pair, and non-exact component types raise `TypeError`. A zero denominator raises `ZeroDivisionError`.

Reduction uses exact Gaussian gcd. From reduced `p,q`, form the four associates `u*q` for `u in ((1,0),(-1,0),(0,1),(0,-1))`. Keep associates `w=(r,s)` satisfying `r>0 or (r==0 and s>=0)`; choose the minimum key `(abs(s),r,s)` in ascending tuple order. Multiply the numerator by the same unit. This uniquely fixes the representative and matches the baseline `unit_normalize` rule. Zero is exactly `((0,0),(1,0))`.

## Finite carrier

```python
@dataclass(frozen=True, init=False)
class CNRSFiniteSequence:
    coefficients: tuple[GaussianInteger, ...]
    offset: int

    def __init__(self, coefficients: Iterable[GaussianLike], offset: int = 0): ...
    @property
    def support(self) -> tuple[int, int] | None: ...
    def coefficient(self, exponent: int) -> GaussianInteger: ...
    def evaluate(self, base: GaussianLike) -> GaussianRational: ...
    def trimmed(self) -> "CNRSFiniteSequence": ...
```

`offset` requires `type(offset) is int`. Construction coerces all coefficients, trims zeros from both boundaries, and increments offset once for each low-boundary zero removed. Zero is `()`, offset `0`, support `None`. Otherwise support is `(offset,offset+len(coefficients)-1)`. Exact evaluation computes `sum(a_k*b**k)`; base zero with negative support raises `ZeroDivisionError`.

## Public convolution signatures

```python
def convolve_exact(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    max_products: int | None = None,
) -> CNRSFiniteSequence: ...

def iter_convolution(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    chunk_products: int = 1024,
    max_products: int | None = None,
) -> Iterator[ConvolutionProgress]: ...

def multiply_with_witness(
    left: CNRSFiniteSequence,
    right: CNRSFiniteSequence,
    *,
    normalize: bool = True,
    max_products: int | None = None,
    max_carry_steps: int | None = None,
) -> MultiplicationResult: ...
```

Inputs require `CNRSFiniteSequence` exactly or a subclass; other types raise `TypeError`. `normalize` requires `type(normalize) is bool`.

For canonical stored lengths `m,n`, required products are `m*n`, including internal-zero positions. Traversal is `i=0..m-1` outer and `j=0..n-1` inner. Before trimming, output offset is exactly `left.offset + right.offset`; constructor trimming may increase the canonical stored offset.

`max_products` requires `None` or a nonnegative exact int; Boolean/non-int raises `TypeError`, negative raises `ValueError`. `convolve_exact` raises `ConvolutionLimitError` before arithmetic if required exceeds the limit.

## Progress and result types

```python
class ConvolutionStatus(str, Enum):
    IN_PROGRESS = "in_progress"
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
class NormalizationLimitError(RuntimeError): ...
```

`chunk_products` requires a positive exact int. Iterator records after each full chunk strictly before termination use `IN_PROGRESS`, `result=None`, and the last traversed pair. Exactly one terminal follows. A complete terminal alone carries the result. A limited terminal performs exactly `max_products` products, has `LIMIT_REACHED`, no result, and the last processed pair or `None`. Zero work yields one complete terminal with canonical zero and `last_pair=None`. Completion on a chunk boundary does not emit a preceding duplicate progress record.

`multiply_with_witness` validates `max_carry_steps` using the normalization limit rules on every call, including when `normalize=False`; after validation it is unused when normalization is disabled. A valid insufficient product limit returns `LIMIT_REACHED` with every result/witness field null. Complete product mode exposes raw convolution; normalized is non-null exactly when `normalize=True`; witness is non-null after successful requested processing. If `normalize=True` and post-input carry draining exceeds `max_carry_steps`, `NormalizationLimitError` propagates and no `MultiplicationResult`, normalized value, or witness is returned or created. Normalization exhaustion is never encoded as `LIMIT_REACHED`. Invalid arguments retain the specified exceptions.

## Exact normalization signature and accounting

```python
def normalize_gaussian_laurent(
    value: CNRSFiniteSequence,
    *,
    max_carry_steps: int | None = None,
) -> CNRSFiniteSequence: ...
```

`value` must be a `CNRSFiniteSequence` instance (subclasses accepted); otherwise raise `TypeError`. `max_carry_steps` must be `None` or a nonnegative exact `int`; Boolean or any non-integer raises `TypeError`, and a negative integer raises `ValueError`.

The exact base-`(-2,1)` recurrence processes input positions from `value.offset` upward. At each position, let the total input-plus-carry be `t=(x,y)`. Select exactly `d=(x+2*y) % 5`, where Python integer modulo gives the unique `d in {0,1,2,3,4}`. Emit `(d,0)` and compute `carry_next=(t-(d,0))/(-2,1)` by exact Gaussian division. Every returned coefficient must therefore belong to `{(0,0),(1,0),(2,0),(3,0),(4,0)}`. Internal zero digits are retained; boundary zeros are removed by the canonical constructor, increasing offset for each removed low-boundary zero.

`max_carry_steps` counts only recurrence iterations after the last stored input coefficient. If carry is already zero, zero steps are required. Before each post-input iteration, if the completed drain count equals the limit while carry is nonzero, raise `NormalizationLimitError` and expose no partial canonical result. Input-position processing does not consume this limit. Exact value and exponent placement before trimming are preserved; canonical trimming may increase output offset. The vector `CNRSFiniteSequence(((5,0),),0)` normalizes to coefficients `((1,0),(3,0),(1,0))` at offset `1`.

## Complete witness schema

```python
@dataclass(frozen=True)
class ConvolutionWitness:
    schema: str
    status: str
    algorithm: str
    traversal: str
    left: CNRSFiniteSequence
    right: CNRSFiniteSequence
    raw: CNRSFiniteSequence
    normalized: CNRSFiniteSequence | None
    normalization_requested: bool
    products_required: int
    left_sha256: str
    right_sha256: str
    raw_sha256: str
    normalized_sha256: str | None

@dataclass(frozen=True)
class WitnessValidation:
    valid: bool
    errors: tuple[str, ...]

def serialize_convolution_witness(witness: ConvolutionWitness) -> bytes: ...
def deserialize_convolution_witness(data: bytes) -> ConvolutionWitness: ...
def verify_convolution_witness(
    witness: ConvolutionWitness | bytes,
) -> WitnessValidation: ...
```

The top-level JSON object has exactly these keys and value types:

```json
{
  "algorithm": "schoolbook-gaussian-exact-v1",
  "left": {"coefficients": [[1, 0]], "offset": 0},
  "left_sha256": "64 lowercase hex characters",
  "normalization_requested": true,
  "normalized": {"coefficients": [[1, 0]], "offset": 0},
  "normalized_sha256": "64 lowercase hex characters",
  "products_required": 1,
  "raw": {"coefficients": [[1, 0]], "offset": 0},
  "raw_sha256": "64 lowercase hex characters",
  "right": {"coefficients": [[1, 0]], "offset": 0},
  "right_sha256": "64 lowercase hex characters",
  "schema": "cnrs-convolution-witness-v1",
  "status": "complete",
  "traversal": "left-major-right-minor-v1"
}
```

The displayed unit sequences are canonical examples; every actual sequence object must satisfy the same zero/trimming rules. `normalized` and `normalized_sha256` are both null exactly when `normalization_requested=false`; otherwise both are non-null. No other field is nullable. Status is only `"complete"`.

A sequence object has exactly keys `coefficients` and `offset`; coefficients are arrays of two JSON integers, with Boolean forbidden. Canonical bytes are UTF-8 of `json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)`, without BOM or trailing newline. Each digest hashes the corresponding canonical sequence-object bytes.

Serialization accepts only a structurally and arithmetically self-consistent complete witness; otherwise it raises `ValueError`. Deserialization accepts `type(data) is bytes` only, rejects invalid UTF-8, duplicate keys, missing/unknown keys, noncanonical bytes, invalid/null mismatches, bad identifiers and digests, and returns the dataclass. Verification accepts only `ConvolutionWitness` or exact `bytes`; other types raise `TypeError`. It independently recomputes convolution without importing production convolution, recomputes normalization when requested, and returns all detected consistency errors.

## Resource claim

Product and carry-drain limits do not bound coefficient bit length, Python-integer work, output allocation, elapsed time, or total memory. Only “product-count bounded” and “post-input carry-drain-count bounded” are permitted.
