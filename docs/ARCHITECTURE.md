# CNRS Scientific Toolkit Architecture — v0.6.0

v0.6.0 is an architecture-consolidation release.  It keeps the established
flat module API for compatibility, but adds explicit package façades that show
which parts of the toolkit are intended to be CNRS-native and which parts are
bridges, validation tools, or scientific workflows.

## Native spine

```text
cnrs.core      CNRS-A base, digits, value, arithmetic, branch-state façade
cnrs.h         CNRS-H coefficient calculus, jets, composition, chain rule,
               domain diagnostics, and Taylor-model metadata
```

The native spine is the preferred conceptual API.  In this structure,
`CnrsH`, `CnrsHJet`, and the direct CNRS-H chain-rule implementation are not
presented as wrappers around ordinary autodiff.  Differentiation is coefficient
shift, integration is reverse coefficient shift, and composition is finite EGF
composition.

## Supporting layers

```text
cnrs.symbolic.py     human-readable expression layer and symbolic/CNRS-H bridge
cnrs.validation      reference autodiff, reference complex comparisons, and
                     cross-check helpers
cnrs.workflows       scientific examples and applied model interfaces
```

These layers are useful, but they are not the core CNRS claim.  For example,
`cnrs.validation.autodiff` is kept as a reference method to test native CNRS-H
calculus, not as the primary CNRS chain-rule implementation.

## Compatibility policy

Earlier imports remain valid:

```python
from cnrs.cnrs_h_jet import CnrsHJet
from cnrs.autodiff import CnrsDual
```

The v0.6.0 preferred native imports are:

```python
from cnrs.core import CVal, BranchState
from cnrs.h import CnrsH, CnrsHJet, verify_jet_chain_rule
from cnrs.validation import CnrsDual
```

This release does not claim a full global analytic-continuation theorem.  It
organizes the toolkit so future branch/path, rigorous remainder, and formal
claim layers can be added without mixing them with validation scaffolds.

## v0.6.2 path/winding extension

The CNRS-H native layer now includes path/winding scaffolding. Branch-state metadata can be updated by supplied continuation paths and recorded on local jets. This extends static branch bookkeeping toward path-aware complex representation while remaining finite and local.

## v0.7.0 continuation rebuild extension

The CNRS-H path layer now feeds a symbolic branch-continuation rebuild layer. When symbolic source expressions are available, branch events can change local coefficients, placing branch metadata and finite coefficient calculus closer together in the native CNRS-H spine.


## Scientific state layer (v0.7.0)

The scientific state layer sits above `cnrs.h` and below application workflows.
It does not replace CNRS-H calculus; it packages a native CNRS-H jet with the
metadata needed for scientific use: scale unit, branch state, path history,
local domain, source expression, and observation policy.

## v0.7.1 native-status classification

The package now includes a lightweight status registry:

```python
from cnrs.native_status import get_component, native_components, status_table
```

The registry makes the architecture explicit:

```text
CNRS-native core:      cnrs.core, cnrs.h, cnrs.science.state
Bridge/access layers:  cnrs.symbolic, cnrs.cnrs_h_bridge
Validation layers:     cnrs.validation, CnrsDual/autodiff, reference complex checks
Scaffolds:             domain diagnostics, Taylor-model metadata, symbolic continuation rebuilds
Applications:          observation maps and scientific workflows
Compatibility:         legacy flat cnrs.cnrs_* modules
```

The design rule for future releases is: use CNRS-native representations when
available, and keep external methods in bridge, validation, or scaffold roles.
