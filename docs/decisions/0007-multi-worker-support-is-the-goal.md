# 7. Multi-worker support is the goal; one worker is an interim guard

- **Status:** accepted, interim - to be superseded when shared storage for this state lands
- **Date:** 2026-08-29

## Context

`workers` is a real setting with a real purpose. Running several uvicorn workers is how this
service is meant to use more than one core, and taking that away permanently is not the intention
of this decision.

What makes it unusable today is process-local state. Uvicorn's workers are separate processes, and
two pieces of the service assume they are the only one:

- **`AuthServiceInternal.refresh_tokens`** is a plain dictionary on a per-process object. A refresh
  token issued by one worker is absent from every other one's dictionary, so `verify_jwt` rejects
  it.
- **The security database is read once per process.** `AuthServiceInternal` loads `security.json`
  in its constructor and is cached for the life of the process, so a password change or a new API
  key made through one worker is invisible to the others until they restart.

The failure this produces is the bad kind. Nothing errors at startup, most requests work, and a
share of session refreshes fail seemingly at random - the share depending on how the operating
system happened to distribute connections. It reads as flakiness, not as a misconfiguration, and a
warning in the documentation only helps someone who already suspects the setting.

That is what
[issue #306](https://github.com/LearningHouseService/learninghouse/issues/306) reports from the
outside - "JWT refresh not working reliably", a refresh that succeeds and then fails moments later,
logging the user out. It was answered with a plan to synchronise state through Redis (issue #373,
closed); the storage that arrives instead is the SQLite database that replaces today's JSON and
CSV files.

The third piece is already fixed: `jwt_secret` persists in `secrets.yaml`, so workers no longer
each invent their own signing secret
([0002](0002-yaml-configuration-with-a-one-shot-migration.md)).

## Decision

**Until that shared storage exists, `workers` above `1` is refused when the settings are loaded**,
with a message that says why and that says it is temporary:

```
workers must be 1 for now: refresh tokens and the security database are held per process,
so a session issued by one worker is rejected by all the others. Support for several
workers comes back once both move into shared storage.
```

This is a guard, not the target architecture. It is written down as a decision because refusing a
previously accepted setting is a visible behaviour change that needs a reason attached - not
because one worker is where this service should stay.

Rejected alternative: build the shared storage now. Refresh tokens and the security database belong
in the SQLite database that is replacing the current mix of JSON files, CSV files and pickles, and
adding a second storage mechanism for them just before that - to be replaced immediately afterwards
- is how a project ends up with four of them. Undoing exactly that is what the persistence work is
for.

Rejected alternative: keep the warning in the documentation and let the setting through. It has
been there, and it does not reach anyone who has not already worked out what is wrong. A
configuration that cannot work should fail where it is applied, not three weeks later through a
support question about random logouts.

## Consequence

An installation that today runs with more than one worker fails to start after this change, instead
of silently logging its users out at intervals. That is the intended trade, and it is temporary.

The setting stays in `configuration.yaml`, and the number stays meaningful. Lifting the guard is
part of the persistence work that moves both pieces of state into the database; "a session issued
by one worker is accepted by every other one, and a password change or new API key made through one
is effective in all of them without a restart" is what that work has to demonstrate. When it lands,
this decision is superseded by the one that records it, not edited.

Two things have to be true before the guard comes off, and both are more than storing a dictionary:
refresh tokens have to be readable and writable by every worker, and the security database has to
stop being a snapshot taken at process start. Issue #306 stays open until then.
