# 3. Shared dependencies are pinned exactly, to pvlearn's values

- **Status:** accepted
- **Date:** 2026-08-29

## Context

learninghouse will depend on [pvlearn](https://github.com/LearningHouseService/pvlearn), the PV
forecast library extracted from `solaredge2mqtt`, in a later phase.

pvlearn pins its own dependencies **exactly**, not as ranges. Once it appears in this project's
dependency list, pip and uv will refuse any different pin of a package both sides declare. In
practice that means learninghouse inherits pvlearn's pins for `numpy`, `pandas`, `scipy`,
`scikit-learn`, `pydantic` and `joblib`.

At the start of the dependency phase the two sides did not agree:

| Package | learninghouse | pvlearn |
|---|---|---|
| `numpy` | 2.4.4 | 2.5.1 |
| `pandas` | 3.0.3 | 3.0.5 |
| `scipy` | *not declared* | 1.18.0 |
| `scikit-learn` | 1.8.0 | 1.9.0 |
| `pydantic` | 2.13.4 | 2.13.4 ✓ |
| `joblib` | 1.5.3 | 1.5.3 ✓ |

## Decision

Align the shared pins now, while adding pvlearn is still a future one-line change rather than a
resolution fight.

- **Exact pins, not ranges**, matching pvlearn and `solaredge2mqtt`. Updates arrive as individual
  Dependabot pull requests that run the full test suite, rather than silently on whatever day a
  transitive resolve changes.
- **`scipy` and `joblib` are declared explicitly** even though `scikit-learn` already pulls both in
  transitively. `joblib` is imported directly (`models/brain.py` calls `joblib.dump`/`load`), and
  pinning `scipy` here rather than leaving it to whatever `scikit-learn`'s own range resolves to is
  what "matches pvlearn exactly" actually requires. A transitive resolve is not a pin.
- **Runtime dependencies are pinned; build-system requirements stay on lower bounds.** They shape
  how the wheel is built, not how the installed package behaves.

## Consequence

The `scikit-learn` bump from 1.8.0 to 1.9.0 is the one with consequences on this side: existing
trained brains were produced by 1.8.0. It is load-bearing on pvlearn's side too - its frozen
forecast baseline is only reproducible against exactly 1.9.0.

A brain therefore has to be *rejected* rather than loaded best-effort when the library versions it
was trained with no longer match. `Brain.actual_versions` / `BrainNotActual` cover the
scikit-learn version, not only the service version, and are pinned by tests. A model that keeps
loading and quietly mispredicts is a worse failure than one that refuses to load.

**Dependabot has no idea this constraint exists.** It will keep proposing a bump of a shared
package on one side without the other. Whoever merges one has to check pvlearn's `pyproject.toml`
in the same breath - this has already happened twice, when `numpy` moved to 2.5.2 and `scipy` to
1.18.1 and pvlearn moved with them.

A real single-environment install of both packages together only becomes possible once pvlearn is
actually a dependency here. Until then the alignment is verified by diffing the two pin lists.
