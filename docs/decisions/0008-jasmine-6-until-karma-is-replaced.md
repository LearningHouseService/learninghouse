# 8. The UI test stack stays on Jasmine 6 until Karma is replaced

- **Status:** accepted, interim - to be superseded when the test runner changes
- **Date:** 2026-09-01

## Context

`jasmine-core` 7.0.2 cannot run this project's specs. Dependabot proposed the bump (#593); every
spec failed to load with

```
Uncaught TypeError: Cannot assign to read only property 'describe' of object '[object Object]'
    at patchJasmine (node_modules/zone.js/fesm2015/zone-testing.js:53)
```

`zone.js` integrates with Jasmine by overwriting the environment's methods in place -
`jasmine.getEnv().describe = …`, and the same for `it`, `beforeEach` and the rest. Jasmine 7 ends
its `Env` constructor with `Object.freeze(this)` and freezes `Env` and `Env.prototype` alongside;
6.3.0 freezes none of them. Writing to a frozen object throws in a strict-mode bundle, so the patch
dies before a single spec runs.

This is deliberate on Jasmine's side, not an accident to wait out.
[jasmine/jasmine#2084](https://github.com/jasmine/jasmine/issues/2084) announced that 6.x is the
last version compatible with `karma-jasmine` and that 7.0 removes the APIs kept for it, because
Karma has been deprecated since April 2023. Nothing is coming from the other direction either:
`zone.js` is at 0.16.2, which is the newest release published, and Angular's own builder prints
`The "@angular-devkit/build-angular:karma" builder is deprecated` on every run.

## Decision

- **`jasmine-core` stays on 6.x**, and `.github/dependabot.yml` ignores its major updates so the
  proposal does not come back with every patch release of 7.
- **The bump is closed rather than left open.** A pull request that cannot go green is
  indistinguishable at a glance from one nobody has got to yet, which is the same reasoning as
  [0004](0004-dependabot-groups-for-framework-majors.md).
- **The ignore entry is temporary and has an owner.** Issue #596 tracks moving `ui/` to Angular's
  supported unit-test setup, and removing this entry is one of its acceptance criteria.

Rejected alternative: patch around it locally, for instance by re-defining the frozen methods before
`zone.js` loads. That is maintaining a fork of somebody else's integration layer, for a runner both
upstreams have declared finished.

## Consequence

The UI test dependencies are frozen where they are, and the freeze is visible in the configuration
rather than in a series of closed pull requests nobody remembers. `karma-jasmine` and the rest of the
Karma packages stay on their current versions for the same reason.

What this costs is real: the UI suite runs on a stack that receives no further compatibility work,
so the next thing to break there breaks with no upstream fix available. That is the argument for
doing #596 before something forces it.
