# 4. Dependabot groups the Angular ecosystem, and does not own framework majors

- **Status:** accepted
- **Date:** 2026-08-29

## Context

Dependabot ran daily against three ecosystems - GitHub Actions, `pip` for `core/`, and `npm` for
`ui/` - proposing one pull request per package. Two separate things kept the queue from draining.

**The Python ecosystem type was wrong.** After the build moved to uv
([0001](0001-uv-for-the-python-build.md)), the `pip` ecosystem kept bumping version strings in
`pyproject.toml` without updating `uv.lock`. CI's `uv sync --locked` then correctly rejected every
one of those pull requests. None of them could ever go green.

**Angular's packages do not resolve independently.** `@angular/*`, `@angular-devkit/*` and
`zone.js` only satisfy each other's peer ranges within one major, so a lone bump of any of them
fails `npm ci` with `ERESOLVE`. Dependabot proposed exactly that, per package, repeatedly.

Framework majors were a third problem wearing the same clothes. Angular 21 → 22 dragged
`typescript` to `~6.0.3`, because `@angular-devkit/build-angular@22` declares
`peer typescript@">=6.0 <6.1"`. `ngx-translate` 17 → 18 dropped the NgModule API outright, so
`TranslateModule` had to become `provideTranslateService()` plus the standalone `TranslatePipe`
across `AppModule`, `SharedModule` and 22 specs. No version bump produces those edits.

Two backlogs accumulated - fourteen open branches, then thirteen more a fortnight later. The queue
refills whenever it is left alone.

## Decision

- **The Python ecosystem is `uv`, not `pip`.** It understands `uv.lock` and updates it alongside
  `pyproject.toml`, so its pull requests can pass `uv sync --locked`.
- **The npm ecosystem gets an `angular` group** covering `@angular/*`, `@angular-devkit/*` and
  `zone.js`, so the framework arrives as one installable pull request instead of a set that each
  fail on their own.
- **A framework major is not Dependabot's job.** Its pull requests for Angular 21 → 22, TypeScript
  6, and `ngx-translate` 18 were closed - not merged, not left open - in favour of branches that
  ran `ng update` and rewrote the call sites by hand. Grouping makes such a bump *installable*; it
  does not make it *correct*.

## Consequence

`typescript` is now bounded from above by whatever Angular's build tooling accepts. TypeScript
7.0.2 exists and Dependabot will keep proposing it. It cannot land before Angular supports it, and
each such pull request has to be closed rather than merged or ignored.

Closing a Dependabot pull request rather than leaving it open is the deliberate half of this. An
open pull request that can never go green is indistinguishable at a glance from one nobody has got
to yet, and the queue is only useful as a signal while every entry in it is actionable.

The grouping is per-ecosystem configuration in `.github/dependabot.yml`, with the reasoning written
next to it. The next framework whose packages only resolve against each other's major gets its own
group there; nothing about this is Angular-specific except the patterns.
