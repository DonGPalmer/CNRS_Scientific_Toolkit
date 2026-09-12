# v0.14.0 streaming division API contract

Status: FROZEN FOR IMPLEMENTATION  
Public modules: cnrs.streaming_division and cnrs.witnesses

## Accepted input

GaussianInt means either an int or a two-integer tuple (real, imaginary). Bool is rejected. The denominator defaults to 1 and must be nonzero. Inputs are normalized to a reduced exact Gaussian fraction.

## Public names

~~~python
GaussianInt = int | tuple[int, int]

class DivisionStreamStatus(Enum):
    TERMINATING = "terminating"
    EVENTUALLY_PERIODIC = "eventually_periodic"
    LIMIT_REACHED = "limit_reached"

def stream_division(
    numerator: GaussianInt,
    denominator: GaussianInt = 1,
) -> CnrsDivisionStream: ...

@dataclass(frozen=True)
class CnrsDivisionStream:
    numerator: tuple[int, int]
    denominator: tuple[int, int]
    power_offset: int

    def __iter__(self) -> Iterator[int]: ...
    def digit(self, index: int) -> int: ...
    def take(self, count: int) -> tuple[int, ...]: ...
    def resolve(self, max_steps: int = 100_000) -> DivisionResolution: ...

@dataclass(frozen=True)
class DivisionResolution:
    status: DivisionStreamStatus
    numerator: tuple[int, int]
    denominator: tuple[int, int]
    power_offset: int
    prefix_digits: tuple[int, ...]
    period_digits: tuple[int, ...]
    steps: int
    witness: CycleWitness | None

    @property
    def terminates(self) -> bool: ...
    @property
    def resolved(self) -> bool: ...
    @property
    def preperiod_length(self) -> int: ...
    @property
    def period_length(self) -> int: ...
    def exact_value_fractions(self) -> tuple[Fraction, Fraction]: ...
    def to_dict(self) -> dict[str, object]: ...
    def to_witness(self) -> DivisionWitness: ...
~~~

The exported constants are:

~~~python
DIVISION_WITNESS_SCHEMA = "cnrs-division-witness-v1"
DIVISION_ALGORITHM = "cnrs-gaussian-rational-stream-v1"
~~~

The witness module exports frozen dataclasses CycleWitness and DivisionWitness, plus:

~~~python
def division_witness(
    numerator: GaussianInt,
    denominator: GaussianInt = 1,
    *,
    max_steps: int = 100_000,
) -> DivisionWitness: ...

def validate_division_witness(
    witness: DivisionWitness | Mapping[str, object],
) -> DivisionWitness: ...
~~~

## Behavioral contract

- Iteration is lazy and replayable.
- digit(0) is the first emitted digit; negative index raises ValueError.
- take(0) returns (); negative count raises ValueError.
- resolve requires max_steps > 0.
- TERMINATING has an empty period and a zero terminal state.
- EVENTUALLY_PERIODIC has a nonempty primitive period and an exact repeated-state cycle witness.
- LIMIT_REACHED has no mathematical witness, has resolved == False, and preserves only the digits observed within the bound.
- to_witness on LIMIT_REACHED raises DivisionSearchLimitError.
- exact_value_fractions is available only for resolved results and equals the normalized input quotient exactly.
- to_dict and witness dictionaries are deterministic and JSON-safe; Gaussian integers are encoded as two-element integer arrays.

## Witness minimum fields

DivisionWitness contains schema, algorithm, base [-2, 1], normalized numerator, normalized denominator, power_offset, status, prefix_digits, period_digits, steps, cycle, and exact_value. exact_value records real and imaginary rational components as reduced [numerator, denominator] pairs. CycleWitness records first_state_index, repeated_state_index, and repeated_state.

Validation recomputes the recurrence and exact value. It does not trust supplied digits, offsets, cycle positions, or fractions.

## Errors

| Condition | Required result |
| --- | --- |
| Zero denominator | ZeroDivisionError |
| Bool, float, complex, malformed tuple, or noninteger component | TypeError |
| Negative digit index or take count | ValueError |
| max_steps <= 0 | ValueError |
| Unresolved division_witness request | DivisionSearchLimitError |
| Malformed or mathematically invalid witness | WitnessValidationError |

Exception messages must identify the rejected parameter or failed invariant; exact prose is not frozen.

## Canonical parity

For every resolved input:

~~~python
canonical = CanonicalPeriodicExpansion.from_gaussian_fraction(p, q)
resolution.power_offset == canonical.power_offset
resolution.prefix_digits == canonical.prefix
resolution.period_digits == canonical.period
resolution.exact_value_fractions() == canonical.exact_value_fractions()
~~~

Equivalent input representations must produce identical normalized witness dictionaries.
